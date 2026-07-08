from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .serializers import RegisterSerializer, UserSerializer

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
