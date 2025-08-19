"""
AI Services serializers for API responses
"""
from rest_framework import serializers
from .models import ContentValidation, AIContentGeneration

class ContentValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentValidation
        fields = ['id', 'portfolio_item', 'is_valid', 'confidence_score', 'validation_data', 'status', 'validated_at']

class AIContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIContentGeneration
        fields = ['id', 'generation_type', 'prompt', 'generated_content', 'quality_score', 'created_at']
