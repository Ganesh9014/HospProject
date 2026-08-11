from django.urls import path
from hospApp.mobile_api_views import (
    mobile_login,
    mobile_logout,
    mobile_dashboard,
    mobile_reports_collection,
)

urlpatterns = [
    # Authentication
    path("auth/login/",  mobile_login,   name="mobile_login"),
    path("auth/logout/", mobile_logout,  name="mobile_logout"),

    # Dashboard
    path("dashboard/",   mobile_dashboard, name="mobile_dashboard"),

    # Reports
    path("reports/collection/", mobile_reports_collection, name="mobile_reports_collection"),
]
