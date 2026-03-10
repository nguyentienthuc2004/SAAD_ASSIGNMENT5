import uuid

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Shipment
from .serializers import ShipmentSerializer


class ShipmentCreate(APIView):
	def get(self, request):
		order_id = request.query_params.get("order_id")
		shipments = Shipment.objects.all().order_by("-id")

		if order_id:
			shipments = shipments.filter(order_id=order_id)

		return Response(ShipmentSerializer(shipments, many=True).data)

	def post(self, request):
		required_fields = ["order_id", "customer_id", "method"]
		missing_fields = [field for field in required_fields if not request.data.get(field)]

		if missing_fields:
			return Response(
				{"error": f"Missing fields: {', '.join(missing_fields)}"},
				status=status.HTTP_400_BAD_REQUEST,
			)

		payload = request.data.copy()
		payload["status"] = Shipment.STATUS_CREATED
		payload["tracking_number"] = f"SHIP-{uuid.uuid4().hex[:10].upper()}"
		payload["shipped_at"] = timezone.now()

		serializer = ShipmentSerializer(data=payload)
		if not serializer.is_valid():
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)
