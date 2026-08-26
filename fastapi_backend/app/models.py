from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    Text,
    DateTime,
    Boolean
)

from sqlalchemy.orm import relationship

from .database import Base


# =========================================================
# USER MODEL
# =========================================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )

    password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(20),
        default="customer",
        nullable=False
    )

    # -----------------------------------------------------
    # RELATIONSHIPS
    # -----------------------------------------------------

    carts = relationship(
        "Cart",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    orders = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# =========================================================
# PRODUCT MODEL
# =========================================================

class Product(Base):

    __tablename__ = "products"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    category = Column(
        String(100),
        nullable=False
    )

    price = Column(
        Float,
        nullable=False
    )

    stock = Column(
        Integer,
        nullable=False,
        default=0
    )

    images = Column(
        Text,
        nullable=True
    )

    # Optional popularity field
    popularity = Column(
        Integer,
        nullable=False,
        default=0
    )

    # -----------------------------------------------------
    # RELATIONSHIPS
    # -----------------------------------------------------

    carts = relationship(
        "Cart",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    order_items = relationship(
        "OrderItem",
        back_populates="product"
    )


# =========================================================
# CART MODEL
# =========================================================

class Cart(Base):

    __tablename__ = "cart"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    quantity = Column(
        Integer,
        default=1,
        nullable=False
    )

    # -----------------------------------------------------
    # RELATIONSHIPS
    # -----------------------------------------------------

    user = relationship(
        "User",
        back_populates="carts"
    )

    product = relationship(
        "Product",
        back_populates="carts"
    )


# =========================================================
# ORDER MODEL
# =========================================================

class Order(Base):

    __tablename__ = "orders"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    total_amount = Column(
        Float,
        nullable=False
    )

    # -----------------------------------------------------
    # PAYMENT STATUS
    #
    # Pending
    # Paid
    # Failed
    # Cancelled
    # -----------------------------------------------------

    payment_status = Column(
        String(30),
        default="Pending",
        nullable=False
    )

    # -----------------------------------------------------
    # ORDER STATUS
    #
    # Pending
    # Confirmed
    # Processing
    # Shipped
    # Delivered
    # Cancelled
    # -----------------------------------------------------

    order_status = Column(
        String(30),
        default="Pending",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # -----------------------------------------------------
    # RELATIONSHIPS
    # -----------------------------------------------------

    user = relationship(
        "User",
        back_populates="orders"
    )

    payments = relationship(
        "Payment",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    # IMPORTANT:
    # One Order can contain many OrderItems.

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )


# =========================================================
# ORDER ITEM MODEL
# =========================================================
#
# This table stores the actual products purchased
# inside every order.
#
# Example:
#
# Order #81
#
# Laptop      quantity = 2    price = 65000
# Mouse       quantity = 1    price = 1500
# Keyboard    quantity = 1    price = 3000
#
# This allows us to calculate:
#
# - Top-selling products
# - Total quantity sold
# - Product sales
# - Product revenue
# - Sales analytics
# - Detailed reports
#
# =========================================================

class OrderItem(Base):

    __tablename__ = "order_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # -----------------------------------------------------
    # ORDER REFERENCE
    # -----------------------------------------------------

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False,
        index=True
    )

    # -----------------------------------------------------
    # PRODUCT REFERENCE
    # -----------------------------------------------------

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )

    # -----------------------------------------------------
    # QUANTITY PURCHASED
    # -----------------------------------------------------

    quantity = Column(
        Integer,
        nullable=False,
        default=1
    )

    # -----------------------------------------------------
    # PRICE AT TIME OF PURCHASE
    # -----------------------------------------------------
    #
    # Do NOT depend on Product.price here.
    #
    # If the product price changes later,
    # old order records should still contain
    # the original purchase price.
    #
    # -----------------------------------------------------

    price = Column(
        Float,
        nullable=False
    )

    # -----------------------------------------------------
    # RELATIONSHIPS
    # -----------------------------------------------------

    order = relationship(
        "Order",
        back_populates="items"
    )

    product = relationship(
        "Product",
        back_populates="order_items"
    )


# =========================================================
# PAYMENT MODEL
# =========================================================

class Payment(Base):

    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False,
        index=True
    )

    amount = Column(
        Float,
        nullable=False
    )

    # -----------------------------------------------------
    # PAYMENT METHOD
    #
    # stripe
    # cod
    # upi
    # card
    # -----------------------------------------------------

    payment_method = Column(
        String(50),
        default="stripe",
        nullable=False
    )

    # -----------------------------------------------------
    # TRANSACTION ID
    # -----------------------------------------------------

    transaction_id = Column(
        String(255),
        nullable=True,
        index=True
    )

    # -----------------------------------------------------
    # PAYMENT STATUS
    #
    # pending
    # paid
    # failed
    # cancelled
    # -----------------------------------------------------

    status = Column(
        String(30),
        default="pending",
        nullable=False
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # -----------------------------------------------------
    # RELATIONSHIP
    # -----------------------------------------------------

    order = relationship(
        "Order",
        back_populates="payments"
    )


# =========================================================
# NOTIFICATION MODEL
# =========================================================

class Notification(Base):

    __tablename__ = "notifications"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    type = Column(
        String(50),
        nullable=False
    )

    message = Column(
        String(255),
        nullable=False
    )

    read_status = Column(
        Boolean,
        default=False,
        nullable=False
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # -----------------------------------------------------
    # RELATIONSHIP
    # -----------------------------------------------------

    user = relationship(
        "User",
        back_populates="notifications"
    )