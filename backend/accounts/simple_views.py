"""
Simplified views for demo purposes
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import CustomUser, CreatorProfile
from .serializers import UserRegistrationSerializer, UserLoginSerializer, CreatorProfileSerializer

class RegisterView(generics.CreateAPIView):
    """User registration view"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.is_verified = True  # Auto-verify for demo
        user.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username
            },
            'token': token.key
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    """User login view"""
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = authenticate(username=email, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username
                },
                'token': token.key
            })
        return Response({'error': 'Invalid credentials'}, status=400)

class ProfileView(generics.RetrieveUpdateAPIView):
    """Creator profile view"""
    serializer_class = CreatorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = CreatorProfile.objects.get_or_create(user=self.request.user)
        return profile
