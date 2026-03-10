import os

import requests
from django.contrib import messages
from django.shortcuts import redirect, render
from requests import RequestException


CUSTOMER_SERVICE_URLS = [
	os.getenv("CUSTOMER_SERVICE_URL", "http://localhost:8001"),
	os.getenv("CUSTOMER_SERVICE_FALLBACK_URL", "http://customer-service:8000"),
]
BOOK_SERVICE_URLS = [
	os.getenv("BOOK_SERVICE_URL", "http://localhost:8002"),
	os.getenv("BOOK_SERVICE_FALLBACK_URL", "http://book-service:8000"),
]
CART_SERVICE_URLS = [
	os.getenv("CART_SERVICE_URL", "http://localhost:8003"),
	os.getenv("CART_SERVICE_FALLBACK_URL", "http://cart-service:8000"),
]
ORDER_SERVICE_URLS = [
	os.getenv("ORDER_SERVICE_URL", "http://localhost:8004"),
	os.getenv("ORDER_SERVICE_FALLBACK_URL", "http://order-service:8000"),
]
COMMENT_RATE_SERVICE_URLS = [
	os.getenv("COMMENT_RATE_SERVICE_URL", "http://localhost:8007"),
	os.getenv("COMMENT_RATE_SERVICE_FALLBACK_URL", "http://comment-rate-service:8000"),
]
REQUEST_TIMEOUT_SECONDS = 6


def _json_or_fallback(response):
	try:
		return response.json()
	except ValueError:
		return {"raw": response.text}


def _service_call(method, urls, path, payload=None, headers=None):
	last_error = "service unavailable"

	for base_url in dict.fromkeys(urls):
		url = f"{base_url.rstrip('/')}{path}"
		try:
			response = requests.request(
				method,
				url,
				json=payload,
				headers=headers,
				timeout=REQUEST_TIMEOUT_SECONDS,
			)
			return response.status_code, _json_or_fallback(response), ""
		except RequestException as exc:
			last_error = str(exc)

	return 0, {}, last_error


def _session_user(request):
	return {
		"id": request.session.get("customer_id"),
		"name": request.session.get("customer_name"),
		"role": request.session.get("role"),
	}


def home(request):
	return render(request, "home.html", {"session_user": _session_user(request)})


def login_view(request):
	if request.method != "POST":
		return redirect("home")

	payload = {
		"email": request.POST.get("email"),
		"password": request.POST.get("password"),
	}
	status_code, data, error = _service_call(
		"POST",
		CUSTOMER_SERVICE_URLS,
		"/customers/login/",
		payload,
	)

	if status_code == 200:
		request.session["customer_id"] = data.get("id")
		request.session["customer_name"] = data.get("name")
		request.session["role"] = data.get("role")
		messages.success(request, f"Xin chao {data.get('name')}!")
		return redirect("list_books")

	messages.error(request, data.get("error") or error or "Dang nhap that bai")
	return redirect("home")


def logout_view(request):
	request.session.flush()
	messages.info(request, "Da dang xuat")
	return redirect("home")


def register_customer(request):
	if request.method != "POST":
		return redirect("home")

	payload = {
		"name": request.POST.get("name"),
		"email": request.POST.get("email"),
		"password": request.POST.get("password"),
		"role": request.POST.get("role", "customer"),
	}
	status_code, data, error = _service_call(
		"POST",
		CUSTOMER_SERVICE_URLS,
		"/customers/",
		payload,
	)

	if status_code == 201:
		messages.success(
			request,
			"Dang ky thanh cong. Cart da duoc tao tu dong cho tai khoan nay.",
		)
	else:
		details = data.get("error") or data or error
		messages.error(request, f"Dang ky that bai: {details}")

	return redirect("home")


def list_books(request):
	status_code, data, error = _service_call("GET", BOOK_SERVICE_URLS, "/books/")
	books = data if status_code == 200 and isinstance(data, list) else []

	if status_code != 200:
		messages.error(request, f"Khong lay duoc danh sach sach: {error or data}")

	session_user = _session_user(request)
	return render(
		request,
		"books.html",
		{
			"books": books,
			"session_user": session_user,
			"is_staff": session_user.get("role") == "staff",
		},
	)


def manage_books(request):
	session_user = _session_user(request)
	if session_user.get("role") != "staff":
		messages.error(request, "Chi staff moi duoc quan ly sach")
		return redirect("list_books")

	if request.method == "POST":
		action = request.POST.get("action")
		staff_headers = {"X-User-Role": (session_user.get("role") or "")}

		if action == "create":
			payload = {
				"title": request.POST.get("title"),
				"author": request.POST.get("author"),
				"price": request.POST.get("price"),
				"stock": request.POST.get("stock"),
				"promotion_percent": request.POST.get("promotion_percent", 0),
			}
			status_code, data, error = _service_call(
				"POST",
				BOOK_SERVICE_URLS,
				"/books/",
				payload,
				headers=staff_headers,
			)
			if status_code == 201:
				messages.success(request, "Da them sach moi")
			else:
				messages.error(request, f"Them sach that bai: {data or error}")

		if action == "update":
			book_id = request.POST.get("book_id")
			payload = {
				"title": request.POST.get("title"),
				"author": request.POST.get("author"),
				"price": request.POST.get("price"),
				"stock": request.POST.get("stock"),
				"promotion_percent": request.POST.get("promotion_percent"),
			}
			payload = {key: value for key, value in payload.items() if value not in (None, "")}

			status_code, data, error = _service_call(
				"PATCH",
				BOOK_SERVICE_URLS,
				f"/books/{book_id}/",
				payload,
				headers=staff_headers,
			)
			if status_code == 200:
				messages.success(request, f"Da cap nhat sach #{book_id}")
			else:
				messages.error(request, f"Cap nhat that bai: {data or error}")

		return redirect("manage_books")

	status_code, data, error = _service_call("GET", BOOK_SERVICE_URLS, "/books/")
	books = data if status_code == 200 and isinstance(data, list) else []

	if status_code != 200:
		messages.error(request, f"Khong tai duoc du lieu sach: {error or data}")

	return render(
		request,
		"manage_books.html",
		{
			"books": books,
			"session_user": session_user,
		},
	)


def add_to_cart(request):
	if request.method != "POST":
		return redirect("list_books")

	session_user = _session_user(request)
	if not session_user.get("id"):
		messages.error(request, "Ban can dang nhap de them vao gio")
		return redirect("home")

	payload = {
		"customer_id": session_user["id"],
		"book_id": request.POST.get("book_id"),
		"quantity": request.POST.get("quantity", 1),
	}
	status_code, data, error = _service_call(
		"POST",
		CART_SERVICE_URLS,
		"/carts/items/",
		payload,
	)

	if status_code in (200, 201):
		messages.success(request, "Da them sach vao gio")
	else:
		messages.error(request, f"Khong the them vao gio: {data or error}")

	return redirect("list_books")


def view_cart(request, customer_id):
	session_user = _session_user(request)
	if not session_user.get("id"):
		messages.error(request, "Ban can dang nhap")
		return redirect("home")

	if session_user.get("role") != "staff" and session_user.get("id") != customer_id:
		messages.error(request, "Ban khong co quyen xem gio hang nay")
		return redirect("list_books")

	status_code, data, error = _service_call(
		"GET",
		CART_SERVICE_URLS,
		f"/carts/{customer_id}/",
	)

	cart_data = data if status_code == 200 and isinstance(data, dict) else {
		"items": [],
		"total_amount": "0.00",
	}

	if status_code != 200:
		messages.error(request, f"Khong tai duoc gio hang: {error or data}")

	return render(
		request,
		"cart.html",
		{
			"cart": cart_data,
			"session_user": session_user,
			"customer_id": customer_id,
		},
	)


def update_cart_item(request, item_id):
	if request.method != "POST":
		return redirect("list_books")

	session_user = _session_user(request)
	if not session_user.get("id"):
		messages.error(request, "Ban can dang nhap")
		return redirect("home")

	payload = {"quantity": request.POST.get("quantity")}
	status_code, data, error = _service_call(
		"PATCH",
		CART_SERVICE_URLS,
		f"/carts/items/{item_id}/",
		payload,
	)

	if status_code == 200:
		messages.success(request, "Cap nhat gio hang thanh cong")
	else:
		messages.error(request, f"Cap nhat gio hang that bai: {data or error}")

	target_customer_id = request.POST.get("customer_id") or session_user["id"]
	try:
		target_customer_id = int(target_customer_id)
	except (TypeError, ValueError):
		target_customer_id = session_user["id"]
	return redirect("view_cart", customer_id=target_customer_id)


def create_order(request, customer_id):
	if request.method != "POST":
		return redirect("view_cart", customer_id=customer_id)

	session_user = _session_user(request)
	if not session_user.get("id"):
		messages.error(request, "Ban can dang nhap")
		return redirect("home")

	if session_user.get("role") != "staff" and session_user.get("id") != customer_id:
		messages.error(request, "Ban khong co quyen tao don nay")
		return redirect("list_books")

	payload = {
		"payment_method": request.POST.get("payment_method"),
		"shipping_method": request.POST.get("shipping_method"),
		"shipping_address": request.POST.get("shipping_address", ""),
	}
	status_code, data, error = _service_call(
		"POST",
		ORDER_SERVICE_URLS,
		f"/orders/{customer_id}/",
		payload,
	)

	if status_code == 201:
		order = data.get("order", {})
		messages.success(
			request,
			f"Dat hang thanh cong. Ma don: {order.get('id')} - Trang thai: {order.get('status')}",
		)
	else:
		messages.error(request, f"Dat hang that bai: {data or error}")

	return redirect("view_cart", customer_id=customer_id)


def rate_book(request, book_id):
	if request.method != "POST":
		return redirect("list_books")

	session_user = _session_user(request)
	if not session_user.get("id"):
		messages.error(request, "Ban can dang nhap de danh gia")
		return redirect("home")

	payload = {
		"customer_id": session_user["id"],
		"score": request.POST.get("score"),
		"comment": request.POST.get("comment", ""),
	}
	status_code, data, error = _service_call(
		"POST",
		COMMENT_RATE_SERVICE_URLS,
		f"/books/{book_id}/ratings/",
		payload,
	)

	if status_code in (200, 201):
		messages.success(request, "Danh gia cua ban da duoc ghi nhan")
	else:
		messages.error(request, f"Danh gia that bai: {data or error}")

	return redirect("list_books")
