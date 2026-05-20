from django.urls import path
from .views import DriverListView, DriverDetailView, nearby_drivers, update_location, update_status

urlpatterns = [
    path('', DriverListView.as_view(), name='driver-list'),
    path('nearby', nearby_drivers, name='driver-nearby'),
    path('location', update_location, name='driver-location'),
    path('status', update_status, name='driver-status'),
    path('<str:pk>', DriverDetailView.as_view(), name='driver-detail'),
]
