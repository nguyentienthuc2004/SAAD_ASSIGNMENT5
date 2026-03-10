from rest_framework import serializers

from .models import Customer, Role


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name"]


class CustomerSerializer(serializers.ModelSerializer):
    role = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Role.objects.all(),
        required=False,
    )

    class Meta:
        model = Customer
        fields = ["id", "name", "email", "password", "role"]
        extra_kwargs = {
            "password": {"write_only": True},
        }