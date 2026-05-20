from django.urls import path
from .views import DeliveryListView, DeliveryDetailView, update_status

urlpatterns = [
    path('', DeliveryListView.as_view(), name='delivery-list'),
    path('<str:pk>', DeliveryDetailView.as_view(), name='delivery-detail'),
    path('<str:pk>/status', update_status, name='delivery-status'),
]
