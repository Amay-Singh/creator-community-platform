"""
Enhanced AI Services Views
Implements REQ-13, REQ-15: AI content generation and portfolio generator
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404

from .models import AIContentGeneration
from .content_generation_service import content_generation_service
from .enhanced_serializers import (
    AIContentGenerationSerializer, ContentGenerationRequestSerializer,
    PortfolioGenerationSerializer
)
from accounts.models import CreatorProfile

class AIContentGenerationView(generics.CreateAPIView):
    """Generate AI content (REQ-13)"""
    serializer_class = ContentGenerationRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        generation_type = serializer.validated_data['generation_type']
        prompt = serializer.validated_data['prompt']
        parameters = serializer.validated_data.get('parameters', {})
        
        # Route to appropriate generation method
        if generation_type == 'music':
            result = content_generation_service.generate_music_concept(profile, prompt, parameters)
        elif generation_type == 'artwork':
            result = content_generation_service.generate_artwork_concept(profile, prompt, parameters)
        elif generation_type == 'story':
            result = content_generation_service.generate_story_concept(profile, prompt, parameters)
        else:
            return Response({'error': 'Unsupported generation type'}, status=status.HTTP_400_BAD_REQUEST)
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PortfolioGenerationView(generics.CreateAPIView):
    """Generate portfolio content (REQ-15)"""
    serializer_class = PortfolioGenerationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        content_type = serializer.validated_data['content_type']
        result = content_generation_service.generate_portfolio_content(profile, content_type)
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AIContentGenerationListView(generics.ListAPIView):
    """List user's AI content generations"""
    serializer_class = AIContentGenerationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        profile = getattr(self.request.user, 'profile', None)
        if not profile:
            return AIContentGeneration.objects.none()
        
        generation_type = self.request.query_params.get('type')
        queryset = profile.ai_generations.all()
        
        if generation_type:
            queryset = queryset.filter(generation_type=generation_type)
        
        return queryset.order_by('-created_at')

class AIContentGenerationDetailView(generics.RetrieveDestroyAPIView):
    """View and delete specific AI generation"""
    serializer_class = AIContentGenerationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        profile = getattr(self.request.user, 'profile', None)
        if not profile:
            return AIContentGeneration.objects.none()
        
        return profile.ai_generations.all()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def regenerate_content(request, generation_id):
    """Regenerate content based on previous generation"""
    
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    result = content_generation_service.regenerate_content(generation_id, profile)
    
    if result['success']:
        return Response(result, status=status.HTTP_201_CREATED)
    else:
        return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def generation_history(request):
    """Get user's content generation history"""
    
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    generation_type = request.query_params.get('type')
    history = content_generation_service.get_generation_history(profile, generation_type)
    
    return Response({
        'history': history,
        'total_count': len(history)
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def batch_portfolio_generation(request):
    """Generate multiple portfolio content types at once"""
    
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    content_types = request.data.get('content_types', ['bio', 'project_descriptions', 'social_captions'])
    results = {}
    
    for content_type in content_types:
        result = content_generation_service.generate_portfolio_content(profile, content_type)
        results[content_type] = result
    
    successful_generations = sum(1 for r in results.values() if r['success'])
    
    return Response({
        'results': results,
        'successful_generations': successful_generations,
        'total_requested': len(content_types)
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def content_generation_stats(request):
    """Get user's content generation statistics"""
    
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    generations = profile.ai_generations.all()
    
    stats = {
        'total_generations': generations.count(),
        'by_type': {},
        'average_quality_score': 0.0,
        'recent_activity': []
    }
    
    # Count by type
    for gen_type, _ in AIContentGeneration.GENERATION_TYPES:
        count = generations.filter(generation_type=gen_type).count()
        if count > 0:
            stats['by_type'][gen_type] = count
    
    # Average quality score
    if generations.exists():
        avg_score = generations.aggregate(
            avg_score=models.Avg('quality_score')
        )['avg_score']
        stats['average_quality_score'] = round(avg_score or 0.0, 2)
    
    # Recent activity (last 10 generations)
    recent = generations.order_by('-created_at')[:10]
    stats['recent_activity'] = [
        {
            'id': str(gen.id),
            'type': gen.generation_type,
            'quality_score': gen.quality_score,
            'created_at': gen.created_at
        }
        for gen in recent
    ]
    
    return Response(stats)
