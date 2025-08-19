"""
AI Services views for content validation and generation
"""
from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import ContentValidation, AIContentGeneration
from .serializers import ContentValidationSerializer, AIContentSerializer

class ContentValidationView(generics.CreateAPIView):
    """Validate content using AI"""
    serializer_class = ContentValidationSerializer
    permission_classes = [permissions.IsAuthenticated]

class AIContentGenerationView(generics.CreateAPIView):
    """Generate AI content"""
    serializer_class = AIContentSerializer
    permission_classes = [permissions.IsAuthenticated]
