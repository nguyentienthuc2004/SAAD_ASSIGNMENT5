from django.db import models


class Order(models.Model):
	STATUS_CREATED = "created"
	STATUS_PROCESSING = "processing"
	STATUS_COMPLETED = "completed"
	STATUS_FAILED = "failed"

	STATUS_CHOICES = [
		(STATUS_CREATED, "Created"),
		(STATUS_PROCESSING, "Processing"),
		(STATUS_COMPLETED, "Completed"),
		(STATUS_FAILED, "Failed"),
	]

	customer_id = models.IntegerField()
	total_amount = models.DecimalField(max_digits=10, decimal_places=2)
	payment_method = models.CharField(max_length=50)
	shipping_method = models.CharField(max_length=50)
	shipping_address = models.CharField(max_length=500, blank=True)
	status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_CREATED)
	payment_status = models.CharField(max_length=30, default="pending")
	shipping_status = models.CharField(max_length=30, default="pending")
	payment_id = models.IntegerField(null=True, blank=True)
	shipping_id = models.IntegerField(null=True, blank=True)
	items = models.JSONField(default=list, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self) -> str:
		return f"Order #{self.id} - customer {self.customer_id}"
