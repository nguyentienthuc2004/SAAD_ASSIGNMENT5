from django.db import models


class Book(models.Model):
  title = models.CharField(max_length=255)
  author = models.CharField(max_length=255)
  price = models.DecimalField(max_digits=10, decimal_places=2)
  stock = models.IntegerField()
  promotion_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

  def __str__(self) -> str:
    return f"{self.title} - {self.author}"


class Rating(models.Model):
  book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="ratings")
  customer_id = models.IntegerField()
  score = models.PositiveSmallIntegerField()
  comment = models.TextField(blank=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self) -> str:
    return f"{self.book_id}:{self.customer_id}:{self.score}"
