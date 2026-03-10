from django.db import models


class Role(models.Model):
  STAFF = "staff"
  CUSTOMER = "customer"

  ROLE_CHOICES = [
    (STAFF, "Staff"),
    (CUSTOMER, "Customer"),
  ]

  name = models.CharField(max_length=32, unique=True, choices=ROLE_CHOICES)

  def __str__(self) -> str:
    return self.name


class Customer(models.Model):
  name = models.CharField(max_length=255)
  email = models.EmailField(unique=True)
  password = models.CharField(max_length=255)
  role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="customers")

  def __str__(self) -> str:
    return f"{self.email} ({self.role.name})"