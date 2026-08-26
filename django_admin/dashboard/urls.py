from django.contrib import admin
from django.urls import path

from dashboard.views import (
    dashboard,
    analytics,
    reports,
    detailed_reports,
    export_orders_csv,
)

urlpatterns = [

    # Django Admin
    path(
        "admin/",
        admin.site.urls
    ),

    # Dashboard
    path(
        "",
        dashboard,
        name="dashboard"
    ),

    # Analytics
    path(
        "analytics/",
        analytics,
        name="analytics"
    ),

    # Reports
    path(
        "reports/",
        reports,
        name="reports"
    ),

    # Detailed Reports
    path(
        "detailed-reports/",
        detailed_reports,
        name="detailed_reports"
    ),

    # CSV Export
    path(
        "export/orders/csv/",
        export_orders_csv,
        name="export_orders_csv"
    ),
]