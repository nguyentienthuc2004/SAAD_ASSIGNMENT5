"""
URL configuration for api_gateway project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from app import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("books/", views.list_books, name="list_books"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("customers/register/", views.register_customer, name="register_customer"),
    path("books/manage/", views.manage_books, name="manage_books"),
    path("books/<int:book_id>/rate/", views.rate_book, name="rate_book"),
    path("cart/add/", views.add_to_cart, name="add_to_cart"),
    path("cart/<int:customer_id>/", views.view_cart, name="view_cart"),
    path("cart/items/<int:item_id>/update/", views.update_cart_item, name="update_cart_item"),
    path("order/<int:customer_id>/", views.create_order, name="create_order"),
]
