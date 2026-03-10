from django.contrib import admin

from .models import Customer, Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "role")
    list_filter = ("role",)
    search_fields = ("name", "email")
