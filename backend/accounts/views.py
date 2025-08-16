"""
Views for User Registration and Profile Management
Implements REQ-1, REQ-3, REQ-18, REQ-19: Registration, validation, browsing
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser, CreatorProfile, PortfolioItem
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, 
    CreatorProfileSerializer, PortfolioItemSerializer,
    PublicProfileSerializer, ProfileFeedbackSerializer
)
from ai_services.content_validator import ContentValidator

class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint (REQ-18)"""
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Send verification email (REQ-3)
        try:
            send_mail(
                'Verify Your Creator Account',
                f'Your verification code is: {user.verification_code}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            # Log error but don't fail registration
            pass
        
        return Response({
            'message': 'Registration successful. Please check your email for verification code.',
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_account(request):
    """Account verification endpoint (REQ-3)"""
    email = request.data.get('email')
    code = request.data.get('verification_code')
    
    try:
        user = CustomUser.objects.get(email=email, verification_code=code)
        user.is_verified = True
        user.verification_code = None
        user.save()
        
        # Create authentication token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'Account verified successfully',
            'token': token.key,
            'user_id': user.id
        })
    except CustomUser.DoesNotExist:
        return Response({
            'error': 'Invalid verification code'
        }, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(generics.GenericAPIView):
    """User login endpoint"""
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.id,
            'has_profile': hasattr(user, 'profile')
        })

class CreatorProfileView(generics.RetrieveUpdateAPIView):
    """Creator profile management (REQ-1, REQ-4)"""
    serializer_class = CreatorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = CreatorProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        profile = serializer.save()
        # Trigger AI validation for profile updates
        ContentValidator.validate_profile(profile)

class ProfileBrowsingView(generics.ListAPIView):
    """Profile browsing with filters (REQ-19)"""
    serializer_class = PublicProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = CreatorProfile.objects.filter(is_validated=True).exclude(user=self.request.user)
        
        # Apply filters (REQ-19)
        category = self.request.query_params.get('category')
        location = self.request.query_params.get('location')
        experience = self.request.query_params.get('experience')
        search = self.request.query_params.get('search')
        
        if category:
            queryset = queryset.filter(category=category)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if experience:
            queryset = queryset.filter(experience_level=experience)
        if search:
            queryset = queryset.filter(
                Q(display_name__icontains=search) |
                Q(bio__icontains=search) |
                Q(subcategory__icontains=search)
            )
        
        return queryset.order_by('-health_score', '-last_active')

class PortfolioUploadView(generics.CreateAPIView):
    """Portfolio item upload (REQ-1)"""
    serializer_class = PortfolioItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        profile = self.request.user.profile
        portfolio_item = serializer.save(profile=profile)
        
        # Trigger AI validation (REQ-2)
        ContentValidator.validate_portfolio_item(portfolio_item)
        
        # Update profile health score
        profile.calculate_health_score()

class ProfileDetailView(generics.RetrieveAPIView):
    """Public profile detail view"""
    serializer_class = PublicProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        return CreatorProfile.objects.filter(is_validated=True)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile_stats(request):
    """Get profile statistics dashboard"""
    profile = request.user.profile
    
    stats = {
        'health_score': profile.health_score,
        'portfolio_items': profile.portfolio_items.count(),
        'connections': profile.connections_made.count(),
        'collaborations': profile.collaborations_initiated.count(),
        'feedback_received': profile.feedback_received.count(),
        'last_active': profile.last_active
    }
    
    return Response(stats)
