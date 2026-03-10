from django.db.models import Avg
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Book, Rating
from .serializers import BookSerializer, RatingSerializer


class BookListCreate(APIView):
	def get(self, request):
		books = Book.objects.all().order_by("id")
		serializer = BookSerializer(books, many=True)
		return Response(serializer.data)

	def post(self, request):
		serializer = BookSerializer(data=request.data)
		if not serializer.is_valid():
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)


class BookDetail(APIView):
	def _get_book(self, pk: int):
		return Book.objects.filter(pk=pk).first()

	def get(self, request, pk):
		book = self._get_book(pk)
		if not book:
			return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

		return Response(BookSerializer(book).data)

	def patch(self, request, pk):
		book = self._get_book(pk)
		if not book:
			return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

		serializer = BookSerializer(book, data=request.data, partial=True)
		if not serializer.is_valid():
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		serializer.save()
		return Response(serializer.data)

	def put(self, request, pk):
		return self.patch(request, pk)

	def delete(self, request, pk):
		book = self._get_book(pk)
		if not book:
			return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

		book.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)


class RatingCreate(APIView):
	def get(self, request, book_id):
		if not Book.objects.filter(id=book_id).exists():
			return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

		ratings = Rating.objects.filter(book_id=book_id).order_by("-created_at")
		serializer = RatingSerializer(ratings, many=True)
		average_score = ratings.aggregate(avg=Avg("score"))["avg"]

		return Response(
			{
				"book_id": book_id,
				"average_score": round(average_score, 2) if average_score else None,
				"count": ratings.count(),
				"ratings": serializer.data,
			}
		)

	def post(self, request, book_id):
		if not Book.objects.filter(id=book_id).exists():
			return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

		payload = request.data.copy()
		payload["book"] = book_id
		customer_id = payload.get("customer_id")

		if not customer_id:
			return Response(
				{"error": "customer_id is required"},
				status=status.HTTP_400_BAD_REQUEST,
			)

		existing_rating = Rating.objects.filter(
			book_id=book_id,
			customer_id=customer_id,
		).first()

		if existing_rating:
			serializer = RatingSerializer(existing_rating, data=payload, partial=True)
		else:
			serializer = RatingSerializer(data=payload)

		if not serializer.is_valid():
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)
