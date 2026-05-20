from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import RegisterView, MeView, update_role

urlpatterns = [
    path("login", TokenObtainPairView.as_view(), name="login"),
    path("register", RegisterView.as_view(), name="register"),
    path("me", MeView.as_view(), name="me"),
    path("role", update_role, name="update-role"),
]
