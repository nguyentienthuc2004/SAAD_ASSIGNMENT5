from django.db import models


class Shipment(models.Model):
	STATUS_CREATED = "created"
	STATUS_SHIPPING = "shipping"
	STATUS_DELIVERED = "delivered"

	order_id = models.IntegerField()
	customer_id = models.IntegerField()
	method = models.CharField(max_length=50)
	address = models.CharField(max_length=500, blank=True)
	status = models.CharField(max_length=30, default=STATUS_CREATED)
	tracking_number = models.CharField(max_length=100, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)
	shipped_at = models.DateTimeField(null=True, blank=True)

	def __str__(self) -> str:
		return f"Shipment #{self.id} for order {self.order_id}"
