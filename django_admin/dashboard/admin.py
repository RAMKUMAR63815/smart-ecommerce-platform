from django.contrib import admin

from .models import (
    Users,
    Products,
    Cart,
    Orders,
)


# =========================================================
# USERS ADMIN
# =========================================================

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


# =========================================================
# PRODUCTS ADMIN
# =========================================================

@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "category",
        "price",
        "stock",
        "popularity",
    )

    search_fields = (
        "name",
        "description",
        "category",
    )

    list_filter = (
        "category",
        "stock",
    )

    ordering = (
        "-id",
    )


# =========================================================
# CART ADMIN
# =========================================================

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

    list_filter = (
        "product",
    )


# =========================================================
# ORDERS ADMIN
# =========================================================

@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user_id",
        "total_amount",
        "payment_status",
        "order_status",
        "created_at",
    )

    search_fields = (
        "payment_status",
        "order_status",
    )

    list_filter = (
        "payment_status",
        "order_status",
    )

    ordering = (
        "-id",
    )