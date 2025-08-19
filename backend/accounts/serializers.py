"""
Serializers for User Registration and Profile Management
Implements REQ-1, REQ-3, REQ-5, REQ-7, REQ-16, REQ-18: User registration, authentication, search, and feedback
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, CreatorProfile, PortfolioItem, ProfileFeedback
from .authentication import ApprovalCode
from ai_services.models import ProfileFeedback as AIProfileFeedback
import random
import string

class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer with validation"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(**validated_data)
        # Generate verification code (REQ-3)
        user.verification_code = ''.join(random.choices(string.digits, k=6))
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    """User login serializer"""
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_verified:
                raise serializers.ValidationError('Account not verified')
            attrs['user'] = user
        return attrs

class PortfolioItemSerializer(serializers.ModelSerializer):
    """Portfolio item serializer with file validation"""
    
    class Meta:
        model = PortfolioItem
        fields = ['id', 'title', 'description', 'media_type', 'file', 'thumbnail', 
                 'is_validated', 'validation_score', 'created_at']
        read_only_fields = ['id', 'is_validated', 'validation_score', 'created_at']
    
    def validate_file(self, value):
        """Validate file size and type"""
        if value.size > 104857600:  # 100MB
            raise serializers.ValidationError("File size cannot exceed 100MB")
        return value

class CreatorProfileSerializer(serializers.ModelSerializer):
    """Creator profile serializer with portfolio items"""
    portfolio_items = PortfolioItemSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = CreatorProfile
        fields = ['id', 'user_email', 'display_name', 'bio', 'category', 'subcategory',
                 'experience_level', 'location', 'instagram_url', 'youtube_url', 
                 'spotify_url', 'website_url', 'is_validated', 'health_score',
                 'portfolio_items', 'created_at', 'last_active']
        read_only_fields = ['id', 'is_validated', 'health_score', 'created_at', 'last_active']
    
    def validate_display_name(self, value):
        """Ensure display name is appropriate"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Display name must be at least 2 characters")
        return value.strip()
    
    def create(self, validated_data):
        profile = super().create(validated_data)
        profile.calculate_health_score()
        return profile
    
    def update(self, instance, validated_data):
        profile = super().update(instance, validated_data)
        profile.calculate_health_score()
        return profile

class ProfileFeedbackSerializer(serializers.ModelSerializer):
    """Profile feedback serializer"""
    reviewer_name = serializers.CharField(source='reviewer.display_name', read_only=True)
    
    class Meta:
        model = ProfileFeedback
        fields = ['id', 'feedback_type', 'rating', 'comment', 'reviewer_name', 'created_at']
        read_only_fields = ['id', 'reviewer_name', 'created_at']

class ApprovalCodeSerializer(serializers.ModelSerializer):
    """Approval code serializer for profile authentication (REQ-3)"""
    
    class Meta:
        model = ApprovalCode
        fields = ['id', 'code', 'code_type', 'status', 'expires_at', 'created_at']
        read_only_fields = ['id', 'code', 'status', 'expires_at', 'created_at']

class ApprovalCodeRequestSerializer(serializers.Serializer):
    """Request approval code serializer"""
    code_type = serializers.ChoiceField(choices=ApprovalCode.CODE_TYPES)

class ApprovalCodeVerificationSerializer(serializers.Serializer):
    """Verify approval code serializer"""
    code = serializers.CharField(max_length=8)
    code_type = serializers.ChoiceField(choices=ApprovalCode.CODE_TYPES)

class ProfileSearchSerializer(serializers.Serializer):
    """Advanced profile search serializer (REQ-5)"""
    query = serializers.CharField(required=False, allow_blank=True)
    categories = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    location = serializers.CharField(required=False, allow_blank=True)
    experience_levels = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    media_types = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    min_portfolio_items = serializers.IntegerField(required=False, min_value=0)
    ai_validated_only = serializers.BooleanField(required=False, default=False)
    availability = serializers.BooleanField(required=False, default=False)
    sort_by = serializers.ChoiceField(
        choices=['relevance', 'newest', 'experience', 'portfolio_count', 'rating'],
        required=False,
        default='relevance'
    )
    page = serializers.IntegerField(required=False, default=1, min_value=1)
    page_size = serializers.IntegerField(required=False, default=20, min_value=1, max_value=50)

class AIRecommendationSerializer(serializers.Serializer):
    """AI recommendation request serializer (REQ-7)"""
    recommendation_type = serializers.ChoiceField(
        choices=['collaboration', 'inspiration', 'networking'],
        default='collaboration'
    )
    limit = serializers.IntegerField(required=False, default=10, min_value=1, max_value=20)

class ProfileFeedbackCreateSerializer(serializers.ModelSerializer):
    """Create profile feedback serializer (REQ-16)"""
    
    class Meta:
        model = AIProfileFeedback
        fields = ['feedback_type', 'rating', 'comment', 'is_anonymous']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

class ProfileHealthMetricsSerializer(serializers.Serializer):
    """Profile health metrics serializer (REQ-4)"""
    health_score = serializers.FloatField(read_only=True)
    completeness_score = serializers.FloatField(read_only=True)
    activity_score = serializers.FloatField(read_only=True)
    feedback_score = serializers.FloatField(read_only=True)
    validation_score = serializers.FloatField(read_only=True)
    recommendations = serializers.ListField(
        child=serializers.CharField(),
        read_only=True
    )

class SearchResultSerializer(serializers.Serializer):
    """Search result serializer with AI enhancements"""
    id = serializers.UUIDField(read_only=True)
    display_name = serializers.CharField(read_only=True)
    category = serializers.CharField(read_only=True)
    experience_level = serializers.CharField(read_only=True)
    location = serializers.CharField(read_only=True)
    bio = serializers.CharField(read_only=True)
    avatar_url = serializers.URLField(read_only=True, allow_null=True)
    portfolio_count = serializers.IntegerField(read_only=True)
    is_validated = serializers.BooleanField(read_only=True)
    compatibility_score = serializers.FloatField(read_only=True, required=False)
    recommendation_reason = serializers.CharField(read_only=True, required=False)
    feedback = serializers.DictField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

class AIRecommendationResultSerializer(serializers.Serializer):
    """AI recommendation result serializer"""
    profile = SearchResultSerializer(read_only=True)
    score = serializers.FloatField(read_only=True)
    reason = serializers.CharField(read_only=True)
    ai_explanation = serializers.CharField(read_only=True)

class PublicProfileSerializer(serializers.ModelSerializer):
    """Public profile view for browsing (no sensitive data)"""
    portfolio_items = PortfolioItemSerializer(many=True, read_only=True)
    feedback_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = CreatorProfile
        fields = ['id', 'display_name', 'bio', 'category', 'subcategory',
                 'experience_level', 'location', 'instagram_url', 'youtube_url',
                 'spotify_url', 'website_url', 'health_score', 'portfolio_items',
                 'feedback_summary']
    
    def get_feedback_summary(self, obj):
        """Get feedback summary for public view"""
        from django.db.models import Avg, Count
        
        feedback_stats = obj.feedback_received.aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('rating')
        )
        
        return {
            'average_rating': feedback_stats['avg_rating'],
            'total_reviews': feedback_stats['total_reviews']
        }
