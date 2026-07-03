from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSerializer, RegisterSerializer

class VerifyEmailView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        uidb64 = request.data.get("uidb64")
        token = request.data.get("token")
        
        if not uidb64 or not token:
            return Response({"error": "Missing parameters"}, status=400)
            
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
            
        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            
            refresh = RefreshToken.for_user(user)
            
            return Response({
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            })
        
        return Response({"error": "Invalid or expired token"}, status=400)

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

@api_view(["PATCH"])
@permission_classes([permissions.IsAuthenticated])
def update_role(request):
    role = request.data.get("role")
    if role not in ("admin", "driver", "customer"):
        return Response({"error": "Invalid role"}, status=400)
    request.user.role = role
    request.user.save()
    return Response(UserSerializer(request.user).data)
