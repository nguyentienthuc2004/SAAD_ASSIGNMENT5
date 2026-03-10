from rest_framework import serializers

from .models import Book, Rating


class BookSerializer(serializers.ModelSerializer):
    discounted_price = serializers.SerializerMethodField(read_only=True)

    def get_discounted_price(self, obj):
        discount_multiplier = (100 - obj.promotion_percent) / 100
        return round(obj.price * discount_multiplier, 2)

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("price must be >= 0")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("stock must be >= 0")
        return value

    def validate_promotion_percent(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("promotion_percent must be between 0 and 100")
        return value

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "price",
            "stock",
            "promotion_percent",
            "discounted_price",
        ]


class RatingSerializer(serializers.ModelSerializer):
    def validate_score(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("score must be between 1 and 5")
        return value

    class Meta:
        model = Rating
        fields = "__all__"
