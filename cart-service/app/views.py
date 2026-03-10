import os
from decimal import Decimal

import requests
from requests import RequestException
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem
from .serializers import CartItemSerializer, CartSerializer


BOOK_SERVICE_URLS = [
	os.getenv("BOOK_SERVICE_URL", "http://localhost:8002"),
	os.getenv("BOOK_SERVICE_FALLBACK_URL", "http://book-service:8000"),
]
ORDER_SERVICE_URLS = [
	os.getenv("ORDER_SERVICE_URL", "http://localhost:8004"),
	os.getenv("ORDER_SERVICE_FALLBACK_URL", "http://order-service:8000"),
]
REQUEST_TIMEOUT_SECONDS = 5


def _json_or_fallback(response):
	try:
		return response.json()
	except ValueError:
		return {"raw": response.text}


def _fetch_book(book_id: int):
	for base_url in dict.fromkeys(BOOK_SERVICE_URLS):
		try:
			response = requests.get(
				f"{base_url.rstrip('/')}/books/{book_id}/",
				timeout=REQUEST_TIMEOUT_SECONDS,
			)
			if response.status_code == 200:
				return response.json()
		except RequestException:
			continue
	return None


def _to_decimal(value) -> Decimal:
	return Decimal(str(value or "0"))


def _build_cart_response(cart: Cart):
	items_payload = []
	total_amount = Decimal("0.00")

	for item in cart.items.all().order_by("id"):
		book = _fetch_book(item.book_id)
		price = _to_decimal(book.get("price")) if book else Decimal("0")
		promotion_percent = _to_decimal(book.get("promotion_percent")) if book else Decimal("0")
		discounted_price = price * (Decimal("100") - promotion_percent) / Decimal("100")
		line_total = discounted_price * item.quantity
		total_amount += line_total

		items_payload.append(
			{
				"id": item.id,
				"book_id": item.book_id,
				"title": book.get("title") if book else "Unknown book",
				"quantity": item.quantity,
				"price": str(price.quantize(Decimal("0.01"))),
				"promotion_percent": str(promotion_percent.quantize(Decimal("0.01"))),
				"discounted_price": str(discounted_price.quantize(Decimal("0.01"))),
				"line_total": str(line_total.quantize(Decimal("0.01"))),
			}
		)

	return {
		"cart_id": cart.id,
		"customer_id": cart.customer_id,
		"items": items_payload,
		"total_amount": str(total_amount.quantize(Decimal("0.01"))),
	}


class CartCreate(APIView):
	def post(self, request):
		customer_id = request.data.get("customer_id")
		if not customer_id:
			return Response(
				{"error": "customer_id is required"},
				status=status.HTTP_400_BAD_REQUEST,
			)

		try:
			customer_id = int(customer_id)
		except (TypeError, ValueError):
			return Response(
				{"error": "customer_id must be an integer"},
				status=status.HTTP_400_BAD_REQUEST,
			)

		cart, _ = Cart.objects.get_or_create(customer_id=customer_id)
		return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)


class AddCartItem(APIView):
	def post(self, request):
		customer_id = request.data.get("customer_id")
		book_id = request.data.get("book_id")
		quantity = request.data.get("quantity", 1)

		if not customer_id or not book_id:
			return Response(
				{"error": "customer_id and book_id are required"},
				status=status.HTTP_400_BAD_REQUEST,
			)

		try:
			customer_id = int(customer_id)
			book_id = int(book_id)
		except (TypeError, ValueError):
			return Response(
				{"error": "customer_id and book_id must be integers"},
				status=status.HTTP_400_BAD_REQUEST,
			)

		try:
			quantity = int(quantity)
		except (TypeError, ValueError):
			return Response(
				{"error": "quantity must be an integer"},
				status=status.HTTP_400_BAD_REQUEST,
			)

		if quantity < 1:
			return Response(
				{"error": "quantity must be >= 1"},
				status=status.HTTP_400_BAD_REQUEST,
			)

		book = _fetch_book(book_id)
		if not book:
			return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

		cart, _ = Cart.objects.get_or_create(customer_id=customer_id)
		item = CartItem.objects.filter(cart=cart, book_id=book_id).first()
		created = False

		if item:
			item.quantity += quantity
			item.save(update_fields=["quantity"])
		else:
			item = CartItem.objects.create(cart=cart, book_id=book_id, quantity=quantity)
			created = True

		payload = {
			"item": CartItemSerializer(item).data,
			"book": {
				"id": book.get("id"),
				"title": book.get("title"),
				"price": book.get("price"),
				"promotion_percent": book.get("promotion_percent"),
			},
		}
		return Response(
			payload,
			status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
		)


class ViewCart(APIView):
	def get(self, request, customer_id):
		cart = Cart.objects.filter(customer_id=customer_id).first()
		if not cart:
			return Response(
				{
					"cart_id": None,
					"customer_id": customer_id,
					"items": [],
					"total_amount": "0.00",
				}
			)

		return Response(_build_cart_response(cart))


class UpdateCartItem(APIView):
	def patch(self, request, item_id):
		item = CartItem.objects.filter(id=item_id).first()
		if not item:
			return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

		quantity = request.data.get("quantity")
		if quantity is None:
			return Response(
				{"error": "quantity is required"},
				status=status.HTTP_400_BAD_REQUEST,
			)

		try:
			quantity = int(quantity)
		except (TypeError, ValueError):
			return Response(
				{"error": "quantity must be an integer"},
				status=status.HTTP_400_BAD_REQUEST,
			)

		if quantity <= 0:
			item.delete()
			return Response({"message": "Item removed from cart"})

		item.quantity = quantity
		item.save(update_fields=["quantity"])
		return Response(CartItemSerializer(item).data)

	def put(self, request, item_id):
		return self.patch(request, item_id)


class OrderCreate(APIView):
	def post(self, request, customer_id):
		payload = request.data.copy()
		payload["customer_id"] = customer_id
		last_error = "order-service is unavailable"

		for base_url in dict.fromkeys(ORDER_SERVICE_URLS):
			order_url = f"{base_url.rstrip('/')}/orders/{customer_id}/"
			try:
				response = requests.post(
					order_url,
					json=payload,
					timeout=REQUEST_TIMEOUT_SECONDS,
				)
				return Response(_json_or_fallback(response), status=response.status_code)
			except RequestException as exc:
				last_error = str(exc)

		return Response(
			{
				"error": "Could not create order",
				"details": last_error,
			},
			status=status.HTTP_502_BAD_GATEWAY,
		)
