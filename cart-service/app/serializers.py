from rest_framework import serializers

from .models import Cart, CartItem


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"


class CartItemSerializer(serializers.ModelSerializer):
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("quantity must be >= 1")
        return value

    class Meta:
        model = CartItem
        fields = "__all__"
