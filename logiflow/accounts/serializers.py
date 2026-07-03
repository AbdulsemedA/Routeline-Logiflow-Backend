from rest_framework import serializers
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "role")

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data, role=User.ROLES.UNASSIGNED, is_active=False)
        
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        verification_link = f"http://localhost:5173/verify-email?uidb64={uid}&token={token}"
        send_mail(
            "Verify your Routeline account",
            f"Please click the link below to verify your email address:\n\n{verification_link}",
            "noreply@routeline.io",
            [user.email],
            fail_silently=False,
        )
        return user
