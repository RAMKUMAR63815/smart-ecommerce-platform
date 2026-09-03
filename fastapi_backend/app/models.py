from datetime import datetime
from sqlalchemy import DECIMAL

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

    return_requests = relationship(
        "ReturnRequest",
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
    # Refunded
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
    # Returned
    # Rejected
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
    # DELIVERY DATE
    # -----------------------------------------------------

    delivered_at = Column(
        DateTime,
        nullable=True
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

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    return_requests = relationship(
        "ReturnRequest",
        back_populates="order",
        cascade="all, delete-orphan"
    )


# =========================================================
# ORDER ITEM MODEL
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
    # PAYMENT AMOUNT
    # -----------------------------------------------------

    amount = Column(DECIMAL(12, 2), nullable=False)

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
    # PAYMENT TRANSACTION ID
    #
    # For Stripe this can contain:
    # PaymentIntent ID / Charge ID
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
    # refunded
    # -----------------------------------------------------

    status = Column(
        String(30),
        default="pending",
        nullable=False
    )

    # -----------------------------------------------------
    # REFUND ID
    #
    # Stores Stripe Refund ID
    # Example:
    # re_123456789
    # -----------------------------------------------------

    refund_id = Column(
        String(255),
        nullable=True,
        index=True
    )

    # -----------------------------------------------------
    # REFUND AMOUNT
    # -----------------------------------------------------

    refund_amount = Column(DECIMAL(12, 2), nullable=True)

    # -----------------------------------------------------
    # REFUND COMPLETED TIME
    # -----------------------------------------------------

    refunded_at = Column(
        DateTime,
        nullable=True
    )

    # -----------------------------------------------------
    # PAYMENT CREATED TIME
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # NOTIFICATION TYPE
    #
    # payment
    # order
    # return
    # refund
    # -----------------------------------------------------

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


# =========================================================
# RETURN REQUEST MODEL
# =========================================================

class ReturnRequest(Base):

    __tablename__ = "return_requests"

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
    # USER REFERENCE
    # -----------------------------------------------------

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # -----------------------------------------------------
    # RETURN REASON
    # -----------------------------------------------------

    reason = Column(
        String(255),
        nullable=False
    )

    # -----------------------------------------------------
    # ADDITIONAL COMMENT
    # -----------------------------------------------------

    comment = Column(
        Text,
        nullable=True
    )

    # -----------------------------------------------------
    # RETURN STATUS
    #
    # pending
    # approved
    # rejected
    # refunded
    # -----------------------------------------------------

    status = Column(
        String(30),
        default="pending",
        nullable=False
    )

    # -----------------------------------------------------
    # RETURN REQUEST CREATED TIME
    # -----------------------------------------------------

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # -----------------------------------------------------
    # RELATIONSHIPS
    # -----------------------------------------------------

    order = relationship(
        "Order",
        back_populates="return_requests"
    )

    user = relationship(
        "User",
        back_populates="return_requests"
    )