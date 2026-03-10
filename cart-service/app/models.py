from django.db import models


class Cart(models.Model):
  customer_id = models.IntegerField(unique=True)
  created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
  cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
  book_id = models.IntegerField()
  quantity = models.IntegerField()
  added_at = models.DateTimeField(auto_now_add=True)

