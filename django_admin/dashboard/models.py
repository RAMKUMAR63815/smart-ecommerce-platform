from django.db import models


# =========================================================
# USERS
# =========================================================

class Users(models.Model):

    id = models.BigAutoField(
        primary_key=True
    )

    name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    email = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True
    )

    password = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    role = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    class Meta:
        managed = False
        db_table = "users"

    def __str__(self):
        return self.email or str(self.id)


# =========================================================
# PRODUCTS
# =========================================================

class Products(models.Model):

    id = models.BigAutoField(
        primary_key=True
    )

    name = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    description = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )

    category = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    price = models.FloatField(
        blank=True,
        null=True
    )

    stock = models.IntegerField(
        blank=True,
        null=True
    )

    images = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )

    popularity = models.IntegerField(
        default=0
    )

    class Meta:
        managed = False
        db_table = "products"

    def __str__(self):
        return self.name or str(self.id)


# =========================================================
# CART
# =========================================================

class Cart(models.Model):

    id = models.BigAutoField(
        primary_key=True
    )

    user = models.ForeignKey(
        Users,
        models.DO_NOTHING,
        db_column="user_id",
        blank=True,
        null=True
    )

    product = models.ForeignKey(
        Products,
        models.DO_NOTHING,
        db_column="product_id",
        blank=True,
        null=True
    )

    quantity = models.IntegerField(
        blank=True,
        null=True
    )

    class Meta:
        managed = False
        db_table = "cart"

    def __str__(self):
        return f"Cart {self.id}"


# =========================================================
# ORDERS
# =========================================================

class Orders(models.Model):

    id = models.BigAutoField(
        primary_key=True
    )

    user_id = models.IntegerField(
        blank=True,
        null=True
    )

    total_amount = models.FloatField(
        blank=True,
        null=True
    )

    payment_status = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    order_status = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        blank=True,
        null=True
    )

    class Meta:
        managed = False
        db_table = "orders"

    def __str__(self):
        return f"Order {self.id}"