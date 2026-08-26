from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum
from .models import Users, Products, Orders

import csv
from collections import defaultdict
from datetime import datetime


# =========================================================
# DASHBOARD
# =========================================================

def dashboard(request):

    total_users = Users.objects.count()
    total_products = Products.objects.count()
    total_orders = Orders.objects.count()

    total_revenue = (
        Orders.objects
        .filter(payment_status__iexact="paid")
        .aggregate(total=Sum("total_amount"))["total"]
        or 0
    )

    return render(
        request,
        "dashboard.html",
        {
            "total_users": total_users,
            "total_products": total_products,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
        }
    )


# =========================================================
# ANALYTICS
# =========================================================

def analytics(request):

    total_orders = Orders.objects.count()
    total_products = Products.objects.count()
    total_users = Users.objects.count()

    # Payment status
    paid_orders = Orders.objects.filter(
        payment_status__iexact="paid"
    ).count()

    pending_payments = Orders.objects.filter(
        payment_status__iexact="pending"
    ).count()

    failed_payments = Orders.objects.filter(
        payment_status__iexact="failed"
    ).count()

    # Order status
    pending_orders = Orders.objects.filter(
        order_status__iexact="pending"
    ).count()

    confirmed_orders = Orders.objects.filter(
        order_status__iexact="confirmed"
    ).count()

    shipped_orders = Orders.objects.filter(
        order_status__iexact="shipped"
    ).count()

    delivered_orders = Orders.objects.filter(
        order_status__iexact="delivered"
    ).count()

    # Total paid revenue
    total_revenue = (
        Orders.objects
        .filter(payment_status__iexact="paid")
        .aggregate(total=Sum("total_amount"))["total"]
        or 0
    )

    # Average order value
    if paid_orders > 0:
        average_order_value = float(total_revenue) / paid_orders
    else:
        average_order_value = 0

    # Total sales
    sales_labels = [
        "Paid",
        "Pending",
        "Failed",
    ]

    sales_values = [
        paid_orders,
        pending_payments,
        failed_payments,
    ]

    # Order status
    order_status_labels = [
        "Pending",
        "Confirmed",
        "Shipped",
        "Delivered",
    ]

    order_status_values = [
        pending_orders,
        confirmed_orders,
        shipped_orders,
        delivered_orders,
    ]

    # Payment status
    payment_status_labels = [
        "Paid",
        "Pending",
        "Failed",
    ]

    payment_status_values = [
        paid_orders,
        pending_payments,
        failed_payments,
    ]

    # Revenue trends
    revenue_data = defaultdict(float)

    paid_orders_queryset = (
        Orders.objects
        .filter(payment_status__iexact="paid")
        .values("created_at", "total_amount")
    )

    for order in paid_orders_queryset:

        created_at = order["created_at"]
        amount = order["total_amount"] or 0

        if created_at:

            try:
                month_name = created_at.strftime("%b %Y")
                revenue_data[month_name] += float(amount)

            except Exception:
                pass

    # Sort revenue months
    sorted_revenue = []

    for month, amount in revenue_data.items():

        try:
            date_value = datetime.strptime(
                month,
                "%b %Y"
            )

            sorted_revenue.append(
                (
                    date_value,
                    month,
                    amount
                )
            )

        except Exception:
            pass

    sorted_revenue.sort(
        key=lambda x: x[0]
    )

    revenue_labels = [
        item[1]
        for item in sorted_revenue
    ]

    revenue_values = [
        round(item[2], 2)
        for item in sorted_revenue
    ]

    # Low stock
    LOW_STOCK_LIMIT = 10

    low_stock_products = (
        Products.objects
        .filter(
            stock__isnull=False,
            stock__lte=LOW_STOCK_LIMIT
        )
        .order_by(
            "stock",
            "name"
        )
    )

    low_stock_labels = []
    low_stock_values = []

    for product in low_stock_products:

        product_name = (
            product.name
            or f"Product {product.id}"
        )

        stock_value = product.stock or 0

        low_stock_labels.append(
            product_name
        )

        low_stock_values.append(
            int(stock_value)
        )

    context = {

        # Summary
        "total_orders": total_orders,
        "total_products": total_products,
        "total_users": total_users,

        # Revenue
        "total_revenue": total_revenue,
        "average_order_value": average_order_value,

        # Payment
        "paid_orders": paid_orders,
        "pending_payments": pending_payments,
        "failed_payments": failed_payments,

        # Sales
        "sales_labels": sales_labels,
        "sales_values": sales_values,

        # Revenue Trends
        "revenue_labels": revenue_labels,
        "revenue_values": revenue_values,

        # Order Status
        "order_status_labels": order_status_labels,
        "order_status_values": order_status_values,

        # Payment Status
        "payment_status_labels": payment_status_labels,
        "payment_status_values": payment_status_values,

        # Low Stock
        "low_stock_labels": low_stock_labels,
        "low_stock_values": low_stock_values,
    }

    return render(
        request,
        "analytics.html",
        context
    )


# =========================================================
# REPORTS
# =========================================================

def reports(request):

    orders = Orders.objects.all().order_by("-id")

    total_orders = Orders.objects.count()
    total_products = Products.objects.count()
    total_users = Users.objects.count()

    total_revenue = (
        Orders.objects
        .filter(payment_status__iexact="paid")
        .aggregate(
            total=Sum("total_amount")
        )["total"]
        or 0
    )

    return render(
        request,
        "reports.html",
        {
            "orders": orders,
            "total_orders": total_orders,
            "total_products": total_products,
            "total_users": total_users,
            "total_revenue": total_revenue,
        }
    )


# =========================================================
# DETAILED REPORTS
# =========================================================

def detailed_reports(request):

    orders = Orders.objects.all().order_by("-id")

    total_orders = Orders.objects.count()
    total_products = Products.objects.count()
    total_users = Users.objects.count()

    total_revenue = (
        Orders.objects
        .filter(payment_status__iexact="paid")
        .aggregate(
            total=Sum("total_amount")
        )["total"]
        or 0
    )

    return render(
        request,
        "detailed_reports.html",
        {
            "orders": orders,
            "total_orders": total_orders,
            "total_products": total_products,
            "total_users": total_users,
            "total_revenue": total_revenue,
        }
    )


# =========================================================
# EXPORT ORDERS CSV
# =========================================================

def export_orders_csv(request):

    response = HttpResponse(
        content_type="text/csv"
    )

    response["Content-Disposition"] = (
        'attachment; filename="orders.csv"'
    )

    writer = csv.writer(response)

    # CSV header
    writer.writerow([
        "Order ID",
        "User ID",
        "Total Amount",
        "Payment Status",
        "Order Status",
        "Created At",
    ])

    # All orders
    orders = Orders.objects.all().order_by("-id")

    # CSV rows
    for order in orders:

        writer.writerow([
            order.id,
            order.user_id,
            order.total_amount,
            order.payment_status,
            order.order_status,
            order.created_at,
        ])

    return response