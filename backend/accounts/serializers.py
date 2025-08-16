"""
Serializers for User Registration and Profile Management
Implements REQ-1, REQ-3, REQ-18: User registration with profile validation
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, CreatorProfile, PortfolioItem, ProfileFeedback
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

class PublicProfileSerializer(serializers.ModelSerializer):
    """Public profile view for browsing (no sensitive data)"""
    portfolio_items = PortfolioItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = CreatorProfile
        fields = ['id', 'display_name', 'bio', 'category', 'subcategory',
                 'experience_level', 'location', 'instagram_url', 'youtube_url',
                 'spotify_url', 'website_url', 'health_score', 'portfolio_items']
