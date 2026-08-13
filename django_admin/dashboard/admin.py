from django.contrib import admin

from .models import Users, Products, Cart, Orders


# =========================
# USERS ADMIN
# =========================

@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "email",
        "role",
    )

    search_fields = (
        "name",
        "email",
    )

    list_filter = (
        "role",
    )


# =========================
# PRODUCTS ADMIN
# =========================

@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "price",
        "stock",
    )

    search_fields = (
        "name",
        "description",
    )

    list_filter = (
        "stock",
    )


# =========================
# CART ADMIN
# =========================

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "product",
        "quantity",
    )

    search_fields = (
        "user__email",
        "product__name",
    )


# =========================
# ORDERS ADMIN
# =========================

@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user_id",
        "total_amount",
        "status",
    )

    search_fields = (
        "status",
    )

    list_filter = (
        "status",
    )