"""
AI Services views for content validation and generation
"""
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import ContentValidation, AIContentGeneration
from .serializers import ContentValidationSerializer, AIContentSerializer

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def validate_content(request):
    """Validate content using AI"""
    serializer = ContentValidationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_content(request):
    """Generate AI content"""
    serializer = AIContentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ContentValidationView(generics.CreateAPIView):
    """Validate content using AI"""
    serializer_class = ContentValidationSerializer
    permission_classes = [permissions.IsAuthenticated]

class AIContentGenerationView(generics.CreateAPIView):
    """Generate AI content"""
    serializer_class = AIContentSerializer
    permission_classes = [permissions.IsAuthenticated]
