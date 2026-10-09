from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .serializers import UserProfileSerializer, UserRegistrationSerializer

User = get_user_model()

class RegisterAPIView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class =  UserRegistrationSerializer

class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user