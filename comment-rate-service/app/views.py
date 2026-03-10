import os

import requests
from requests import RequestException
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


BOOK_SERVICE_URLS = [
	os.getenv("BOOK_SERVICE_URL", "http://localhost:8002"),
	os.getenv("BOOK_SERVICE_FALLBACK_URL", "http://book-service:8000"),
]
REQUEST_TIMEOUT_SECONDS = 5


def _json_or_fallback(response):
	try:
		return response.json()
	except ValueError:
		return {"raw": response.text}


class BookRatingProxy(APIView):
	def _forward(self, method: str, book_id: int, payload=None):
		last_error = "book-service is unavailable"

		for base_url in dict.fromkeys(BOOK_SERVICE_URLS):
			url = f"{base_url.rstrip('/')}/books/{book_id}/ratings/"
			try:
				response = requests.request(
					method,
					url,
					json=payload,
					timeout=REQUEST_TIMEOUT_SECONDS,
				)
				return Response(_json_or_fallback(response), status=response.status_code)
			except RequestException as exc:
				last_error = str(exc)

		return Response(
			{"error": "Could not contact book-service", "details": last_error},
			status=status.HTTP_502_BAD_GATEWAY,
		)

	def get(self, request, book_id):
		return self._forward("GET", book_id)

	def post(self, request, book_id):
		return self._forward("POST", book_id, payload=request.data)
