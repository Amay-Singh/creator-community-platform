"""
AI Services views for content validation and generation
Enhanced for P5-006: AI Content Generation Assistant
"""
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta

from .models import (
    ContentValidation, AIContentGeneration, ContentGenerationRequest,
    GeneratedContent, ContentTemplate, ContentCategory, UserUsageTracking
)
from .serializers import (
    ContentValidationSerializer, AIContentSerializer,
    ContentGenerationRequestSerializer, ContentGenerationRequestCreateSerializer,
    GeneratedContentSerializer, GeneratedContentCreateSerializer,
    ContentTemplateSerializer, ContentTemplateCreateSerializer,
    ContentCategorySerializer, UserUsageTrackingSerializer,
    ContentGenerationStatsSerializer, ContentGenerationBatchSerializer
)
from .content_generation_service import content_generation_service


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


# P5-006 AI Content Generation Assistant ViewSets

class ContentGenerationRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for content generation requests"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ContentGenerationRequestCreateSerializer
        return ContentGenerationRequestSerializer
    
    def get_queryset(self):
        user_profile = getattr(self.request.user, 'creatorprofile', None)
        if not user_profile:
            return ContentGenerationRequest.objects.none()
        queryset = ContentGenerationRequest.objects.filter(user=user_profile)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by content type
        content_type = self.request.query_params.get('content_type')
        if content_type:
            queryset = queryset.filter(content_type=content_type)
        
        # Filter by platform
        platform = self.request.query_params.get('platform')
        if platform:
            queryset = queryset.filter(platform=platform)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        user_profile = self.request.user.creatorprofile
        
        # Check rate limits
        usage_stats = content_generation_service.get_user_usage_stats(user_profile)
        if usage_stats['daily_requests'] >= 50:  # Daily limit
            return Response(
                {'error': 'Daily request limit exceeded'}, 
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Create request
        request_data = serializer.validated_data
        request_obj = content_generation_service.create_content_request(user_profile, request_data)
        
        # Process request asynchronously (for now, process synchronously)
        try:
            generated_content = content_generation_service.process_content_request(request_obj)
            return Response({
                'request': ContentGenerationRequestSerializer(request_obj).data,
                'generated_content': GeneratedContentSerializer(generated_content).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': f'Content generation failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate content for a request"""
        request_obj = self.get_object()
        user_profile = request.user.creatorprofile
        
        if request_obj.user != user_profile:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            generated_content = content_generation_service.process_content_request(request_obj)
            return Response(GeneratedContentSerializer(generated_content).data)
        except Exception as e:
            return Response(
                {'error': f'Regeneration failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def create_template(self, request, pk=None):
        """Create a template from this request"""
        request_obj = self.get_object()
        user_profile = request.user.creatorprofile
        
        if request_obj.user != user_profile:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        name = request.data.get('name')
        description = request.data.get('description', '')
        
        if not name:
            return Response({'error': 'Template name is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        template = content_generation_service.create_template_from_request(request_obj, name, description)
        return Response(ContentTemplateSerializer(template).data, status=status.HTTP_201_CREATED)


class GeneratedContentViewSet(viewsets.ModelViewSet):
    """ViewSet for generated content"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return GeneratedContentCreateSerializer
        return GeneratedContentSerializer
    
    def get_queryset(self):
        user_profile = self.request.user.creatorprofile
        queryset = GeneratedContent.objects.filter(request__user=user_profile)
        
        # Filter by rating
        rating = self.request.query_params.get('rating')
        if rating:
            queryset = queryset.filter(user_rating=rating)
        
        # Filter by favorites
        favorites_only = self.request.query_params.get('favorites')
        if favorites_only == 'true':
            queryset = queryset.filter(is_favorite=True)
        
        # Filter by published
        published_only = self.request.query_params.get('published')
        if published_only == 'true':
            queryset = queryset.filter(is_published=True)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Rate generated content"""
        content = self.get_object()
        user_profile = request.user.creatorprofile
        
        if content.request.user != user_profile:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        rating = request.data.get('rating')
        feedback = request.data.get('feedback', '')
        
        if not rating or rating not in [1, 2, 3, 4, 5]:
            return Response({'error': 'Valid rating (1-5) is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        content.user_rating = rating
        content.user_feedback = feedback
        content.save()
        
        return Response(GeneratedContentSerializer(content).data)
    
    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """Toggle favorite status"""
        content = self.get_object()
        user_profile = request.user.creatorprofile
        
        if content.request.user != user_profile:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        content.is_favorite = not content.is_favorite
        content.save()
        
        return Response({'is_favorite': content.is_favorite})
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Mark content as published"""
        content = self.get_object()
        user_profile = request.user.creatorprofile
        
        if content.request.user != user_profile:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        content.is_published = True
        content.save()
        
        return Response({'is_published': content.is_published})


class ContentTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for content templates"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ContentTemplateCreateSerializer
        return ContentTemplateSerializer
    
    def get_queryset(self):
        user_profile = self.request.user.creatorprofile
        queryset = ContentTemplate.objects.filter(
            Q(creator=user_profile) | Q(is_public=True)
        )
        
        # Filter by content type
        content_type = self.request.query_params.get('content_type')
        if content_type:
            queryset = queryset.filter(content_type=content_type)
        
        # Filter by template type
        template_type = self.request.query_params.get('template_type')
        if template_type:
            queryset = queryset.filter(template_type=template_type)
        
        # Show featured first, then by usage
        return queryset.order_by('-is_featured', '-usage_count', '-created_at')
    
    def perform_create(self, serializer):
        user_profile = self.request.user.creatorprofile
        serializer.save(creator=user_profile)
    
    @action(detail=True, methods=['post'])
    def use_template(self, request, pk=None):
        """Use template to create a new content request"""
        template = self.get_object()
        user_profile = request.user.creatorprofile
        
        custom_params = request.data.get('parameters', {})
        
        try:
            request_obj = content_generation_service.use_template(template, user_profile, custom_params)
            generated_content = content_generation_service.process_content_request(request_obj)
            
            return Response({
                'request': ContentGenerationRequestSerializer(request_obj).data,
                'generated_content': GeneratedContentSerializer(generated_content).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': f'Template usage failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured templates"""
        templates = ContentTemplate.objects.filter(is_featured=True, is_public=True)
        serializer = ContentTemplateSerializer(templates, many=True)
        return Response(serializer.data)


class ContentCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for content categories"""
    serializer_class = ContentCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ContentCategory.objects.filter(is_active=True).order_by('name')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def content_generation_stats(request):
    """Get content generation statistics for the user"""
    user_profile = request.user.creatorprofile
    
    # Get request statistics
    requests = ContentGenerationRequest.objects.filter(user=user_profile)
    total_requests = requests.count()
    completed_requests = requests.filter(status='completed').count()
    failed_requests = requests.filter(status='failed').count()
    
    # Get usage statistics
    total_tokens_used = requests.aggregate(Sum('tokens_used'))['tokens_used__sum'] or 0
    total_cost = requests.aggregate(Sum('cost_estimate'))['cost_estimate__sum'] or 0
    
    # Get quality statistics
    generated_content = GeneratedContent.objects.filter(request__user=user_profile)
    avg_quality = generated_content.aggregate(Avg('quality_score'))['quality_score__avg'] or 0
    
    # Get most used content type and platform
    content_type_stats = requests.values('content_type').annotate(count=Count('content_type')).order_by('-count').first()
    platform_stats = requests.values('platform').annotate(count=Count('platform')).order_by('-count').first()
    
    stats_data = {
        'total_requests': total_requests,
        'completed_requests': completed_requests,
        'failed_requests': failed_requests,
        'total_tokens_used': total_tokens_used,
        'total_cost': total_cost,
        'average_quality_score': round(avg_quality, 2),
        'most_used_content_type': content_type_stats['content_type'] if content_type_stats else '',
        'most_used_platform': platform_stats['platform'] if platform_stats else ''
    }
    
    serializer = ContentGenerationStatsSerializer(stats_data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def usage_tracking(request):
    """Get user's usage tracking data"""
    user_profile = request.user.creatorprofile
    
    # Get recent usage data
    recent_usage = UserUsageTracking.objects.filter(
        user=user_profile,
        date__gte=timezone.now().date() - timedelta(days=30)
    ).order_by('-date')
    
    serializer = UserUsageTrackingSerializer(recent_usage, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def batch_generate(request):
    """Generate multiple content pieces in batch"""
    user_profile = request.user.creatorprofile
    
    serializer = ContentGenerationBatchSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Check rate limits
    usage_stats = content_generation_service.get_user_usage_stats(user_profile)
    batch_size = len(serializer.validated_data['requests'])
    
    if usage_stats['daily_requests'] + batch_size > 50:
        return Response(
            {'error': 'Batch would exceed daily request limit'}, 
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    results = []
    
    for request_data in serializer.validated_data['requests']:
        try:
            request_obj = content_generation_service.create_content_request(user_profile, request_data)
            generated_content = content_generation_service.process_content_request(request_obj)
            
            results.append({
                'success': True,
                'request': ContentGenerationRequestSerializer(request_obj).data,
                'generated_content': GeneratedContentSerializer(generated_content).data
            })
        except Exception as e:
            results.append({
                'success': False,
                'error': str(e),
                'request_data': request_data
            })
    
    return Response({'results': results}, status=status.HTTP_201_CREATED)
