import os

import requests
from requests import RequestException
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Customer, Role
from .serializers import CustomerSerializer, RoleSerializer


CART_SERVICE_URLS = [
	os.getenv("CART_SERVICE_URL", "http://localhost:8003"),
	os.getenv("CART_SERVICE_FALLBACK_URL", "http://cart-service:8000"),
]
REQUEST_TIMEOUT_SECONDS = 5


def _ensure_default_roles() -> None:
	Role.objects.get_or_create(name=Role.CUSTOMER)
	Role.objects.get_or_create(name=Role.STAFF)


def _create_cart_for_customer(customer_id: int) -> tuple[bool, str]:
	payload = {"customer_id": customer_id}
	last_error = "cart-service is unavailable"

	for base_url in dict.fromkeys(CART_SERVICE_URLS):
		cart_url = f"{base_url.rstrip('/')}/carts/"
		try:
			response = requests.post(
				cart_url,
				json=payload,
				timeout=REQUEST_TIMEOUT_SECONDS,
			)
			if response.status_code in (200, 201):
				return True, ""
			last_error = f"{cart_url} returned {response.status_code}"
		except RequestException:
			continue

	return False, last_error


class RoleList(APIView):
	def get(self, request):
		_ensure_default_roles()
		roles = Role.objects.all().order_by("id")
		serializer = RoleSerializer(roles, many=True)
		return Response(serializer.data)


class CustomerListCreate(APIView):
	def get(self, request):
		_ensure_default_roles()
		customers = Customer.objects.select_related("role").all().order_by("id")
		serializer = CustomerSerializer(customers, many=True)
		return Response(serializer.data)

	def post(self, request):
		_ensure_default_roles()
		payload = request.data.copy()
		if not payload.get("role"):
			payload["role"] = Role.CUSTOMER

		serializer = CustomerSerializer(data=payload)
		if not serializer.is_valid():
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		customer = serializer.save()
		cart_created, error_message = _create_cart_for_customer(customer.id)

		if not cart_created:
			customer.delete()
			return Response(
				{
					"error": "Could not auto-create cart for this customer.",
					"details": error_message,
				},
				status=status.HTTP_502_BAD_GATEWAY,
			)

		return Response(CustomerSerializer(customer).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
	def post(self, request):
		email = request.data.get("email")
		password = request.data.get("password")

		if not email or not password:
			return Response(
				{"error": "email and password are required"},
				status=status.HTTP_400_BAD_REQUEST,
			)

		customer = (
			Customer.objects.select_related("role")
			.filter(email=email, password=password)
			.first()
		)

		if not customer:
			return Response(
				{"error": "Invalid credentials"},
				status=status.HTTP_401_UNAUTHORIZED,
			)

		return Response(
			{
				"id": customer.id,
				"name": customer.name,
				"email": customer.email,
				"role": customer.role.name,
			}
		)
