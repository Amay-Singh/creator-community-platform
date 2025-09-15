"""
Simplified views for demo purposes
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
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

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_view(request):
    """Dashboard data view"""
    user = request.user
    profile, created = CreatorProfile.objects.get_or_create(user=user)
    
    # Mock dashboard data
    dashboard_data = {
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_verified': getattr(user, 'is_verified', True)
        },
        'profile': {
            'display_name': profile.display_name or user.username,
            'bio': profile.bio or '',
            'location': profile.location or '',
            'website_url': profile.website_url or '',
            'avatar_url': getattr(profile, 'avatar', None).url if hasattr(profile, 'avatar') and profile.avatar else None
        },
        'stats': {
            'portfolio_items': 0,
            'collaborations': 0,
            'followers': 0,
            'following': 0,
            'total_views': 0
        },
        'recent_activity': [],
        'notifications_count': 0
    }
    
    return Response(dashboard_data, status=status.HTTP_200_OK)
