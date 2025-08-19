"""
Enhanced Views for Creator Community Platform
Implements REQ-3, REQ-4, REQ-5, REQ-7, REQ-16: Authentication, search, recommendations, feedback
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random
import string

from .models import CustomUser, CreatorProfile, PortfolioItem, ProfileFeedback
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, CreatorProfileSerializer,
    PortfolioItemSerializer, ApprovalCodeSerializer, ApprovalCodeRequestSerializer,
    ApprovalCodeVerificationSerializer, ProfileSearchSerializer, AIRecommendationSerializer,
    ProfileFeedbackCreateSerializer, ProfileHealthMetricsSerializer, SearchResultSerializer,
    AIRecommendationResultSerializer, PublicProfileSerializer
)
from .authentication import ProfileAuthenticationService
from .search_service import ProfileSearchService
from ai_services.models import ProfileFeedback as AIProfileFeedback
from rest_framework.exceptions import ValidationError
from notifications.utils import create_notification, create_activity

class RegisterView(generics.CreateAPIView):
    """User registration view (REQ-18)"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class VerifyAccountView(generics.GenericAPIView):
    """Account verification view"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('verification_code')
        
        try:
            user = CustomUser.objects.get(email=email)
            
            if user.verification_code == code:
                user.is_verified = True
                user.verification_code = None
                user.save()
                
                token, created = Token.objects.get_or_create(user=user)
                
                return Response({
                    'token': token.key,
                    'user_id': user.id,
                    'message': 'Account verified successfully'
                })
            else:
                return Response({'error': 'Invalid verification code'}, status=400)
                
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

class LoginView(generics.GenericAPIView):
    """User login view"""
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

class LogoutView(generics.GenericAPIView):
    """User logout view"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            request.user.auth_token.delete()
        except:
            pass
        return Response({'message': 'Logged out successfully'})

class CreatorProfileView(generics.RetrieveUpdateAPIView):
    """Creator profile management view"""
    serializer_class = CreatorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = CreatorProfile.objects.get_or_create(user=self.request.user)
        return profile

# Profile Authentication Views (REQ-3)
class RequestApprovalCodeView(generics.GenericAPIView):
    """Request approval code for profile authentication"""
    serializer_class = ApprovalCodeRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        code_type = serializer.validated_data['code_type']
        approval_code = profile_auth_service.generate_approval_code(profile, code_type)
        
        return Response({
            'message': 'Approval code sent successfully',
            'code_id': approval_code.id,
            'expires_at': approval_code.expires_at
        }, status=status.HTTP_201_CREATED)

class VerifyApprovalCodeView(generics.GenericAPIView):
    """Verify approval code for profile authentication"""
    serializer_class = ApprovalCodeVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        code = serializer.validated_data['code']
        code_type = serializer.validated_data['code_type']
        
        result = profile_auth_service.verify_approval_code(code, profile, code_type)
        
        if result['is_valid']:
            return Response({
                'message': result['message'],
                'verification_successful': True
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': result['message'],
                'verification_successful': False
            }, status=status.HTTP_400_BAD_REQUEST)

class ProfileAuthenticationStatusView(generics.GenericAPIView):
    """Get profile authentication status"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        status_data = profile_auth_service.get_profile_authentication_status(profile)
        return Response(status_data, status=status.HTTP_200_OK)

# Advanced Search Views (REQ-5)
class ProfileSearchView(generics.GenericAPIView):
    """Advanced profile search with filters"""
    serializer_class = ProfileSearchSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        profile = getattr(request.user, 'profile', None)
        search_results = search_service.advanced_search(
            serializer.validated_data, 
            requesting_profile=profile
        )
        
        return Response(search_results, status=status.HTTP_200_OK)

# AI Recommendation Views (REQ-7)
class AIRecommendationsView(generics.GenericAPIView):
    """Get AI-powered profile recommendations"""
    serializer_class = AIRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        recommendation_type = serializer.validated_data['recommendation_type']
        recommendations = search_service.get_ai_recommendations(profile, recommendation_type)
        
        # Serialize recommendations
        serialized_recommendations = []
        for rec in recommendations:
            rec_data = {
                'profile': SearchResultSerializer(rec['profile']).data,
                'score': rec['score'],
                'reason': rec['reason'],
                'ai_explanation': rec.get('ai_explanation', '')
            }
            serialized_recommendations.append(rec_data)
        
        return Response({
            'recommendations': serialized_recommendations,
            'recommendation_type': recommendation_type,
            'total_count': len(serialized_recommendations)
        }, status=status.HTTP_200_OK)

# Profile Health Metrics (REQ-4)
class ProfileHealthMetricsView(generics.GenericAPIView):
    """Get profile health metrics and recommendations"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        health_score = profile_auth_service._calculate_profile_health_score(profile)
        
        # Calculate component scores
        completeness_score = self._calculate_completeness_score(profile)
        activity_score = self._calculate_activity_score(profile)
        feedback_score = self._calculate_feedback_score(profile)
        validation_score = self._calculate_validation_score(profile)
        
        # Generate recommendations
        recommendations = self._generate_health_recommendations(profile, {
            'completeness': completeness_score,
            'activity': activity_score,
            'feedback': feedback_score,
            'validation': validation_score
        })
        
        return Response({
            'health_score': health_score,
            'completeness_score': completeness_score,
            'activity_score': activity_score,
            'feedback_score': feedback_score,
            'validation_score': validation_score,
            'recommendations': recommendations
        }, status=status.HTTP_200_OK)
    
    def _calculate_completeness_score(self, profile):
        """Calculate profile completeness score"""
        score = 0
        max_score = 100
        
        if profile.bio:
            score += 25
        if profile.avatar:
            score += 15
        if profile.location:
            score += 15
        if profile.portfolio_items.count() > 0:
            score += 30
        if any([profile.instagram_url, profile.youtube_url, profile.spotify_url, profile.website_url]):
            score += 15
        
        return min(max_score, score)
    
    def _calculate_activity_score(self, profile):
        """Calculate profile activity score"""
        from datetime import timedelta
        
        recent_activity = timezone.now() - timedelta(days=30)
        score = 0
        max_score = 100
        
        # Recent portfolio additions
        recent_portfolio = profile.portfolio_items.filter(created_at__gte=recent_activity).count()
        score += min(40, recent_portfolio * 10)
        
        # Profile updates
        if profile.updated_at and profile.updated_at >= recent_activity:
            score += 30
        
        # User login activity
        if profile.user.last_login and profile.user.last_login >= recent_activity:
            score += 30
        
        return min(max_score, score)
    
    def _calculate_feedback_score(self, profile):
        """Calculate feedback score"""
        from django.db.models import Avg
        
        avg_feedback = profile.feedback_received.aggregate(avg_rating=Avg('rating'))['avg_rating']
        if avg_feedback:
            return (avg_feedback / 5.0) * 100
        return 0
    
    def _calculate_validation_score(self, profile):
        """Calculate validation score"""
        score = 0
        max_score = 100
        
        if profile.is_validated:
            score += 50
        
        validated_portfolio = profile.portfolio_items.filter(is_ai_validated=True).count()
        total_portfolio = profile.portfolio_items.count()
        
        if total_portfolio > 0:
            validation_ratio = validated_portfolio / total_portfolio
            score += validation_ratio * 50
        
        return min(max_score, score)
    
    def _generate_health_recommendations(self, profile, scores):
        """Generate recommendations to improve profile health"""
        recommendations = []
        
        if scores['completeness'] < 80:
            if not profile.bio:
                recommendations.append("Add a compelling bio to tell your story")
            if not profile.avatar:
                recommendations.append("Upload a profile picture to personalize your profile")
            if profile.portfolio_items.count() < 3:
                recommendations.append("Add more portfolio items to showcase your work")
        
        if scores['activity'] < 60:
            recommendations.append("Stay active by updating your portfolio regularly")
            recommendations.append("Log in frequently to show you're an active creator")
        
        if scores['feedback'] < 70:
            recommendations.append("Engage with other creators to build your reputation")
            recommendations.append("Collaborate with others to receive feedback")
        
        if scores['validation'] < 80:
            if not profile.is_validated:
                recommendations.append("Complete profile verification to increase trust")
            recommendations.append("Validate your portfolio items with AI assistance")
        
        return recommendations

# Profile Feedback Views (REQ-16)
class CreateProfileFeedbackView(generics.CreateAPIView):
    """Create feedback for a profile"""
    serializer_class = ProfileFeedbackCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        reviewee_id = self.kwargs.get('profile_id')
        try:
            reviewee = CreatorProfile.objects.get(id=reviewee_id)
            reviewer = getattr(self.request.user, 'profile', None)
            
            if not reviewer:
                raise ValidationError("Reviewer profile not found")
            
            if reviewer == reviewee:
                raise ValidationError("Cannot review your own profile")
            
            serializer.save(reviewer=reviewer, reviewee=reviewee)
        except CreatorProfile.DoesNotExist:
            raise ValidationError("Profile not found")

class ProfileFeedbackListView(generics.ListAPIView):
    """List feedback for a profile"""
    serializer_class = ProfileFeedbackCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        profile_id = self.kwargs.get('profile_id')
        return AIProfileFeedback.objects.filter(reviewee_id=profile_id).order_by('-created_at')

# Public Profile Browsing
class PublicProfileListView(generics.ListAPIView):
    """Public profile browsing with basic filters"""
    serializer_class = PublicProfileSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = CreatorProfile.objects.filter(is_validated=True, user__is_active=True)
        
        # Apply basic filters
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        return queryset.order_by('-created_at')

class PublicProfileDetailView(generics.RetrieveAPIView):
    """Public profile detail view"""
    serializer_class = PublicProfileSerializer
    permission_classes = [permissions.AllowAny]
    queryset = CreatorProfile.objects.filter(is_validated=True, user__is_active=True)
    
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        
        # Create notification for profile owner when someone views their profile
        if request.user.is_authenticated:
            profile = self.get_object()
            viewer = request.user
            
            # Don't notify if viewing own profile
            if profile.user != viewer:
                create_notification(
                    user=profile.user,
                    notification_type='profile_view',
                    payload={
                        'viewer_name': viewer.get_full_name() or viewer.username,
                        'viewer_id': str(viewer.id),
                        'profile_id': str(profile.id)
                    }
                )
                
                create_activity(
                    user=profile.user,
                    actor=viewer,
                    action_type='profile_viewed',
                    target_type='profile',
                    target_id=str(profile.id),
                    metadata={
                        'viewer_name': viewer.get_full_name() or viewer.username
                    }
                )
        
        return response
