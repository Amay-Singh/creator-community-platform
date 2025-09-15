"""
AI Services serializers for API responses
"""
from rest_framework import serializers
from .models import (
    ContentValidation, AIContentGeneration, ProfileFeedback,
    ContentGenerationRequest, GeneratedContent, ContentTemplate, ContentCategory, UserUsageTracking,
    CreatorEmbedding, MatchResult, MatchFeedback, MatchHistory
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
    user_display_name = serializers.CharField(source='user.display_name', read_only=True)
    
    class Meta:
        model = UserUsageTracking
        fields = [
            'id', 'user', 'user_display_name', 'usage_type', 'daily_count', 
            'monthly_count', 'total_cost', 'date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# ============================================================================
# P5-001: AI-Powered Creator Matching Serializers
# ============================================================================

class CreatorEmbeddingSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='creator.display_name', read_only=True)
    needs_update = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = CreatorEmbedding
        fields = [
            'id', 'creator', 'creator_name', 'embedding_version', 
            'needs_update', 'created_at', 'updated_at', 'last_profile_update'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MatchResultSerializer(serializers.ModelSerializer):
    requester_name = serializers.CharField(source='requester.display_name', read_only=True)
    matched_creator_name = serializers.CharField(source='matched_creator.display_name', read_only=True)
    matched_creator_bio = serializers.CharField(source='matched_creator.bio', read_only=True)
    matched_creator_location = serializers.CharField(source='matched_creator.location', read_only=True)
    matched_creator_avatar = serializers.SerializerMethodField()
    feedback_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MatchResult
        fields = [
            'id', 'requester', 'requester_name', 'matched_creator', 'matched_creator_name',
            'matched_creator_bio', 'matched_creator_location', 'matched_creator_avatar',
            'similarity_score', 'compatibility_score', 'match_reasons', 'shared_skills',
            'complementary_skills', 'match_type', 'status', 'viewed_at', 'expires_at',
            'feedback_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'similarity_score', 'compatibility_score', 'match_reasons',
            'shared_skills', 'complementary_skills', 'created_at', 'updated_at'
        ]
    
    def get_matched_creator_avatar(self, obj):
        """Get matched creator's avatar URL"""
        if hasattr(obj.matched_creator, 'avatar') and obj.matched_creator.avatar:
            return obj.matched_creator.avatar.url
        return None
    
    def get_feedback_count(self, obj):
        """Get count of feedback for this match"""
        return obj.feedback.count()


class MatchResultCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating match results (used internally)"""
    
    class Meta:
        model = MatchResult
        fields = [
            'requester', 'matched_creator', 'similarity_score', 'compatibility_score',
            'match_reasons', 'shared_skills', 'complementary_skills', 'match_type',
            'match_filters', 'expires_at'
        ]


class MatchFeedbackSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.display_name', read_only=True)
    match_info = serializers.SerializerMethodField()
    
    class Meta:
        model = MatchFeedback
        fields = [
            'id', 'match_result', 'user', 'user_name', 'rating', 'feedback_type',
            'comment', 'contacted_match', 'collaboration_started', 'would_recommend',
            'match_info', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
    def get_match_info(self, obj):
        """Get basic info about the match"""
        return {
            'matched_creator': obj.match_result.matched_creator.display_name,
            'compatibility_score': obj.match_result.compatibility_score,
            'match_date': obj.match_result.created_at
        }
    
    def validate_rating(self, value):
        """Validate rating is within acceptable range"""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value


class MatchHistorySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.display_name', read_only=True)
    
    class Meta:
        model = MatchHistory
        fields = [
            'id', 'user', 'user_name', 'request_type', 'filters_used', 'results_count',
            'processing_time_ms', 'embedding_version', 'top_similarity_score',
            'average_compatibility', 'matches_viewed', 'matches_contacted', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MatchRequestSerializer(serializers.Serializer):
    """Serializer for match request parameters"""
    limit = serializers.IntegerField(default=10, min_value=1, max_value=50)
    location = serializers.CharField(required=False, allow_blank=True)
    skills = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        allow_empty=True
    )
    experience_level = serializers.CharField(required=False, allow_blank=True)
    match_type = serializers.CharField(default='general')
    exclude_previous = serializers.BooleanField(default=True)
    
    def validate_limit(self, value):
        """Validate limit is reasonable"""
        if value > 50:
            raise serializers.ValidationError("Maximum limit is 50 matches")
        return value


class BatchMatchRequestSerializer(serializers.Serializer):
    """Serializer for batch matching requests"""
    creator_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=100
    )
    limit_per_creator = serializers.IntegerField(default=5, min_value=1, max_value=20)
    filters = MatchRequestSerializer(required=False)
    
    def validate_creator_ids(self, value):
        """Validate creator IDs exist"""
        from accounts.models import CreatorProfile
        existing_ids = set(CreatorProfile.objects.filter(id__in=value).values_list('id', flat=True))
        invalid_ids = set(value) - existing_ids
        
        if invalid_ids:
            raise serializers.ValidationError(f"Invalid creator IDs: {list(invalid_ids)}")
        
        return value


class MatchStatisticsSerializer(serializers.Serializer):
    """Serializer for match statistics"""
    total_matches = serializers.IntegerField()
    matches_viewed = serializers.IntegerField()
    matches_contacted = serializers.IntegerField()
    average_compatibility = serializers.FloatField()
    feedback_given = serializers.IntegerField()
    average_feedback = serializers.FloatField()
    recent_matches = serializers.IntegerField()
    
    # Additional computed fields
    view_rate = serializers.SerializerMethodField()
    contact_rate = serializers.SerializerMethodField()
    
    def get_view_rate(self, obj):
        """Calculate view rate percentage"""
        if obj['total_matches'] > 0:
            return round((obj['matches_viewed'] / obj['total_matches']) * 100, 1)
        return 0.0
    
    def get_contact_rate(self, obj):
        """Calculate contact rate percentage"""
        if obj['matches_viewed'] > 0:
            return round((obj['matches_contacted'] / obj['matches_viewed']) * 100, 1)
        return 0.0


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
