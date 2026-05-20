from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("logiflow.accounts.urls")),
    path("drivers/", include("logiflow.drivers.urls")),
    path("deliveries/", include("logiflow.deliveries.urls")),
    path("analytics/", include("logiflow.analytics.urls")),
]
