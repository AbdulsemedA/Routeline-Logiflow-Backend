from django.urls import path
from .consumers import GlobalConsumer

websocket_urlpatterns = [
    path("ws/stream/", GlobalConsumer.as_asgi()),
]
