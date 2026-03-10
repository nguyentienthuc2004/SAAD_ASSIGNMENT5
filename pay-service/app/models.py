from django.db import models


class Payment(models.Model):
	STATUS_PENDING = "pending"
	STATUS_SUCCESS = "success"
	STATUS_FAILED = "failed"

	order_id = models.IntegerField()
	customer_id = models.IntegerField()
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	method = models.CharField(max_length=50)
	status = models.CharField(max_length=30, default=STATUS_PENDING)
	transaction_ref = models.CharField(max_length=100, unique=True)
	paid_at = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self) -> str:
		return f"Payment #{self.id} for order {self.order_id}"
