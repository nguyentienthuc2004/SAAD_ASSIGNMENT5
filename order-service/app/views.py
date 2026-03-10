import os
from decimal import Decimal

import requests
from requests import RequestException
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from .serializers import OrderSerializer


CART_SERVICE_URLS = [
	os.getenv("CART_SERVICE_URL", "http://localhost:8003"),
	os.getenv("CART_SERVICE_FALLBACK_URL", "http://cart-service:8000"),
]
PAY_SERVICE_URLS = [
	os.getenv("PAY_SERVICE_URL", "http://localhost:8005"),
	os.getenv("PAY_SERVICE_FALLBACK_URL", "http://pay-service:8000"),
]
SHIP_SERVICE_URLS = [
	os.getenv("SHIP_SERVICE_URL", "http://localhost:8006"),
	os.getenv("SHIP_SERVICE_FALLBACK_URL", "http://ship-service:8000"),
]
REQUEST_TIMEOUT_SECONDS = 5


def _json_or_fallback(response):
	try:
		return response.json()
	except ValueError:
		return {"raw": response.text}


def _call_service(method, urls, path, payload=None):
	last_error = "service unavailable"

	for base_url in dict.fromkeys(urls):
		service_url = f"{base_url.rstrip('/')}{path}"
		try:
			response = requests.request(
				method,
				service_url,
				json=payload,
				timeout=REQUEST_TIMEOUT_SECONDS,
			)
			return response.status_code, _json_or_fallback(response), ""
		except RequestException as exc:
			last_error = str(exc)

	return 0, {}, last_error


def _to_decimal(value) -> Decimal:
	return Decimal(str(value or "0"))


class OrderCreate(APIView):
	def post(self, request, customer_id):
		payment_method = request.data.get("payment_method")
		shipping_method = request.data.get("shipping_method")
		shipping_address = request.data.get("shipping_address", "")

		if not payment_method or not shipping_method:
			return Response(
				{"error": "payment_method and shipping_method are required"},
				status=status.HTTP_400_BAD_REQUEST,
			)

		cart_status, cart_data, cart_error = _call_service(
			"GET",
			CART_SERVICE_URLS,
			f"/carts/{customer_id}/",
		)

		if cart_status != 200:
			return Response(
				{
					"error": "Could not read customer cart",
					"details": cart_error or cart_data,
				},
				status=status.HTTP_502_BAD_GATEWAY,
			)

		items = cart_data.get("items", [])
		if not items:
			return Response(
				{"error": "Cart is empty"},
				status=status.HTTP_400_BAD_REQUEST,
			)

		total_amount = _to_decimal(cart_data.get("total_amount"))
		if total_amount <= 0:
			total_amount = sum(_to_decimal(item.get("line_total")) for item in items)

		order = Order.objects.create(
			customer_id=customer_id,
			total_amount=total_amount,
			payment_method=payment_method,
			shipping_method=shipping_method,
			shipping_address=shipping_address,
			status=Order.STATUS_PROCESSING,
			items=items,
		)

		payment_status, payment_data, payment_error = _call_service(
			"POST",
			PAY_SERVICE_URLS,
			"/payments/",
			{
				"order_id": order.id,
				"customer_id": customer_id,
				"amount": str(total_amount),
				"method": payment_method,
			},
		)

		if payment_status not in (200, 201):
			order.status = Order.STATUS_FAILED
			order.payment_status = "failed"
			order.save(update_fields=["status", "payment_status"])
			return Response(
				{
					"error": "Payment failed",
					"details": payment_error or payment_data,
					"order": OrderSerializer(order).data,
				},
				status=status.HTTP_502_BAD_GATEWAY,
			)

		shipping_status, shipping_data, shipping_error = _call_service(
			"POST",
			SHIP_SERVICE_URLS,
			"/shipments/",
			{
				"order_id": order.id,
				"customer_id": customer_id,
				"method": shipping_method,
				"address": shipping_address,
			},
		)

		if shipping_status not in (200, 201):
			order.status = Order.STATUS_FAILED
			order.payment_status = payment_data.get("status", "success")
			order.shipping_status = "failed"
			order.payment_id = payment_data.get("id")
			order.save(
				update_fields=["status", "payment_status", "shipping_status", "payment_id"]
			)
			return Response(
				{
					"error": "Shipping creation failed",
					"details": shipping_error or shipping_data,
					"order": OrderSerializer(order).data,
					"payment": payment_data,
				},
				status=status.HTTP_502_BAD_GATEWAY,
			)

		order.status = Order.STATUS_COMPLETED
		order.payment_status = payment_data.get("status", "success")
		order.shipping_status = shipping_data.get("status", "created")
		order.payment_id = payment_data.get("id")
		order.shipping_id = shipping_data.get("id")
		order.save(
			update_fields=[
				"status",
				"payment_status",
				"shipping_status",
				"payment_id",
				"shipping_id",
			]
		)

		return Response(
			{
				"order": OrderSerializer(order).data,
				"payment": payment_data,
				"shipping": shipping_data,
			},
			status=status.HTTP_201_CREATED,
		)


class OrderDetail(APIView):
	def get(self, request, order_id):
		order = Order.objects.filter(id=order_id).first()
		if not order:
			return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

		return Response(OrderSerializer(order).data)
