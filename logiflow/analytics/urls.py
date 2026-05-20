from django.urls import path
from .views import summary, series

urlpatterns = [
    path("summary", summary, name="analytics-summary"),
    path("series", series, name="analytics-series"),
]
