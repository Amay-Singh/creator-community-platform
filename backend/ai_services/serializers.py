"""
AI Services serializers for API responses
"""
from rest_framework import serializers
from .models import (
    ContentValidation, AIContentGeneration, ContentGenerationRequest,
    GeneratedContent, ContentTemplate, ContentCategory, UserUsageTracking
)


class ContentValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentValidation
        fields = ['id', 'portfolio_item', 'is_valid', 'confidence_score', 'validation_data', 'status', 'validated_at']


class AIContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIContentGeneration
        fields = ['id', 'generation_type', 'prompt', 'generated_content', 'quality_score', 'created_at']


# P5-006 AI Content Generation Assistant Serializers

class ContentGenerationRequestSerializer(serializers.ModelSerializer):
    """Serializer for content generation requests"""
    user_display_name = serializers.CharField(source='user.display_name', read_only=True)
    
    class Meta:
        model = ContentGenerationRequest
        fields = [
            'id', 'user', 'user_display_name', 'content_type', 'platform',
            'prompt', 'topic', 'target_audience', 'tone', 'word_count',
            'duration_minutes', 'temperature', 'max_tokens', 'custom_parameters',
            'status', 'tokens_used', 'cost_estimate', 'created_at', 'updated_at',
            'completed_at'
        ]
        read_only_fields = ['id', 'user', 'tokens_used', 'cost_estimate', 'status', 'completed_at']


class ContentGenerationRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating content generation requests"""
    
    class Meta:
        model = ContentGenerationRequest
        fields = [
            'content_type', 'platform', 'prompt', 'topic', 'target_audience',
            'tone', 'word_count', 'duration_minutes', 'temperature', 'max_tokens',
            'custom_parameters'
        ]
    
    def validate_prompt(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Prompt must be at least 10 characters long.")
        return value
    
    def validate_temperature(self, value):
        if not 0.0 <= value <= 2.0:
            raise serializers.ValidationError("Temperature must be between 0.0 and 2.0.")
        return value
    
    def validate_max_tokens(self, value):
        if not 50 <= value <= 4000:
            raise serializers.ValidationError("Max tokens must be between 50 and 4000.")
        return value


class GeneratedContentSerializer(serializers.ModelSerializer):
    """Serializer for generated content"""
    request_details = serializers.SerializerMethodField()
    
    class Meta:
        model = GeneratedContent
        fields = [
            'id', 'request', 'request_details', 'content', 'title', 'metadata',
            'version', 'parent_version', 'quality_score', 'user_rating',
            'user_feedback', 'is_published', 'is_favorite', 'view_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'quality_score', 'view_count']
    
    def get_request_details(self, obj):
        return {
            'content_type': obj.request.content_type,
            'platform': obj.request.platform,
            'topic': obj.request.topic
        }


class GeneratedContentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating generated content"""
    
    class Meta:
        model = GeneratedContent
        fields = ['request', 'content', 'title', 'metadata']
    
    def validate_content(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Content must be at least 10 characters long.")
        return value


class ContentTemplateSerializer(serializers.ModelSerializer):
    """Serializer for content templates"""
    creator_name = serializers.CharField(source='creator.display_name', read_only=True)
    
    class Meta:
        model = ContentTemplate
        fields = [
            'id', 'creator', 'creator_name', 'name', 'description', 'template_type',
            'content_type', 'prompt_template', 'default_parameters', 'example_output',
            'is_public', 'is_featured', 'usage_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'creator', 'usage_count', 'is_featured']


class ContentTemplateCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating content templates"""
    
    class Meta:
        model = ContentTemplate
        fields = [
            'name', 'description', 'template_type', 'content_type',
            'prompt_template', 'default_parameters', 'example_output', 'is_public'
        ]
    
    def validate_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Template name must be at least 3 characters long.")
        return value
    
    def validate_prompt_template(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Prompt template must be at least 10 characters long.")
        return value


class ContentCategorySerializer(serializers.ModelSerializer):
    """Serializer for content categories"""
    subcategories = serializers.SerializerMethodField()
    
    class Meta:
        model = ContentCategory
        fields = [
            'id', 'name', 'description', 'parent', 'color', 'icon',
            'created_at', 'is_active', 'subcategories'
        ]
        read_only_fields = ['id']
    
    def get_subcategories(self, obj):
        if obj.subcategories.exists():
            return ContentCategorySerializer(obj.subcategories.filter(is_active=True), many=True).data
        return []


class UserUsageTrackingSerializer(serializers.ModelSerializer):
    """Serializer for user usage tracking"""
    user_name = serializers.CharField(source='user.display_name', read_only=True)
    
    class Meta:
        model = UserUsageTracking
        fields = [
            'id', 'user', 'user_name', 'usage_type', 'tokens_consumed',
            'cost_incurred', 'daily_count', 'monthly_count', 'date', 'created_at'
        ]
        read_only_fields = ['id', 'user']


class ContentGenerationStatsSerializer(serializers.Serializer):
    """Serializer for content generation statistics"""
    total_requests = serializers.IntegerField()
    completed_requests = serializers.IntegerField()
    failed_requests = serializers.IntegerField()
    total_tokens_used = serializers.IntegerField()
    total_cost = serializers.DecimalField(max_digits=8, decimal_places=4)
    average_quality_score = serializers.FloatField()
    most_used_content_type = serializers.CharField()
    most_used_platform = serializers.CharField()


class ContentGenerationBatchSerializer(serializers.Serializer):
    """Serializer for batch content generation"""
    requests = ContentGenerationRequestCreateSerializer(many=True)
    
    def validate_requests(self, value):
        if len(value) > 10:
            raise serializers.ValidationError("Maximum 10 requests allowed per batch.")
        if len(value) == 0:
            raise serializers.ValidationError("At least one request is required.")
        return value
