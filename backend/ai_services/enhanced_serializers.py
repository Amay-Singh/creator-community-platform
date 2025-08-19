"""
Enhanced AI Services Serializers
Implements REQ-13, REQ-15: AI content generation and portfolio generator
"""
from rest_framework import serializers
from .models import AIContentGeneration

class ContentGenerationRequestSerializer(serializers.Serializer):
    """Serializer for content generation requests"""
    generation_type = serializers.ChoiceField(
        choices=['music', 'artwork', 'story'],
        help_text="Type of content to generate"
    )
    prompt = serializers.CharField(
        max_length=1000,
        help_text="Description of what you want to create"
    )
    parameters = serializers.JSONField(
        required=False,
        default=dict,
        help_text="Additional parameters for generation"
    )

class PortfolioGenerationSerializer(serializers.Serializer):
    """Serializer for portfolio content generation"""
    content_type = serializers.ChoiceField(
        choices=['bio', 'project_descriptions', 'social_captions'],
        help_text="Type of portfolio content to generate"
    )

class AIContentGenerationSerializer(serializers.ModelSerializer):
    """Serializer for AI content generation results"""
    profile_name = serializers.CharField(source='profile.display_name', read_only=True)
    generation_type_display = serializers.CharField(source='get_generation_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    content_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = AIContentGeneration
        fields = [
            'id', 'profile_name', 'generation_type', 'generation_type_display',
            'prompt', 'parameters', 'status', 'status_display',
            'generated_content', 'content_preview', 'quality_score',
            'error_message', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_content_preview(self, obj):
        """Return truncated content for list views"""
        if obj.generated_content:
            return obj.generated_content[:200] + '...' if len(obj.generated_content) > 200 else obj.generated_content
        return None

class ContentGenerationStatsSerializer(serializers.Serializer):
    """Serializer for content generation statistics"""
    total_generations = serializers.IntegerField()
    by_type = serializers.DictField()
    average_quality_score = serializers.FloatField()
    recent_activity = serializers.ListField()

class GenerationHistorySerializer(serializers.Serializer):
    """Serializer for generation history"""
    id = serializers.UUIDField()
    generation_type = serializers.CharField()
    prompt = serializers.CharField()
    quality_score = serializers.FloatField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    preview = serializers.CharField()
