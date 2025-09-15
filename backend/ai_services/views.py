"""
AI Services views for content validation and generation
Enhanced for P5-006: AI Content Generation Assistant
"""
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
import json

from .models import (
    ContentValidation, AIContentGeneration, ProfileFeedback,
    ContentGenerationRequest, GeneratedContent, ContentTemplate, ContentCategory, UserUsageTracking,
    CreatorEmbedding, MatchResult, MatchFeedback, MatchHistory
)
from .serializers import (
    ContentValidationSerializer, AIContentSerializer,
    ContentGenerationRequestSerializer, GeneratedContentSerializer, ContentTemplateSerializer, 
    ContentCategorySerializer, UserUsageTrackingSerializer, ContentGenerationBatchSerializer,
    ContentGenerationStatsSerializer, CreatorEmbeddingSerializer, MatchResultSerializer,
    MatchFeedbackSerializer, MatchHistorySerializer, MatchRequestSerializer, BatchMatchRequestSerializer,
    MatchStatisticsSerializer
)
from .content_generation_service import content_generation_service
from .matching_service import matching_service


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
def usage_tracking(request):
    """Get user's usage tracking data"""
    from datetime import timedelta
    user_profile = request.user.creatorprofile
    
    # Get recent usage data
    recent_usage = UserUsageTracking.objects.filter(
        user=user_profile,
        date__gte=timezone.now().date() - timedelta(days=30)
    ).order_by('-date')
    
    serializer = UserUsageTrackingSerializer(recent_usage, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def content_generation_stats(request):
    """Get content generation statistics for the current user"""
    try:
        user_profile = request.user.creatorprofile
        stats = content_generation_service.get_user_statistics(user_profile)
        serializer = ContentGenerationStatsSerializer(stats)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {'error': f'Failed to get statistics: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def batch_content_generation(request):
    """Generate multiple content pieces in batch"""
    try:
        user_profile = request.user.creatorprofile
        
        # Validate request data
        serializer = ContentGenerationBatchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
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
        
    except Exception as e:
        return Response(
            {'error': f'Batch generation failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ai_services_health(request):
    """Health check for AI services"""
    return Response({
        'status': 'healthy',
        'services': {
            'content_generation': True,
            'ai_matching': True,
            'database': True
        },
        'timestamp': timezone.now()
    })


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


# ============================================================================
# P5-001: AI-Powered Creator Matching Views
# ============================================================================

class CreatorEmbeddingViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for creator embeddings (read-only)"""
    serializer_class = CreatorEmbeddingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter to current user's embedding"""
        try:
            user_profile = self.request.user.creatorprofile
            return CreatorEmbedding.objects.filter(creator=user_profile)
        except AttributeError:
            return CreatorEmbedding.objects.none()
    
    @action(detail=False, methods=['post'])
    def update_embedding(self, request):
        """Update current user's embedding"""
        try:
            user_profile = request.user.creatorprofile
        except AttributeError:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            force_update = request.data.get('force_update', False)
            success = matching_service.update_creator_embedding(user_profile, force_update)
            
            if success:
                embedding = CreatorEmbedding.objects.get(creator=user_profile)
                serializer = self.get_serializer(embedding)
                return Response({
                    'success': True,
                    'message': 'Embedding updated successfully',
                    'embedding': serializer.data
                })
            else:
                return Response(
                    {'error': 'Failed to update embedding'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            return Response(
                {'error': f'Error updating embedding: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MatchResultViewSet(viewsets.ModelViewSet):
    """ViewSet for match results"""
    serializer_class = MatchResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter to current user's matches"""
        try:
            user_profile = self.request.user.creatorprofile
            return MatchResult.objects.filter(requester=user_profile)
        except AttributeError:
            return MatchResult.objects.none()
    
    @action(detail=False, methods=['post'])
    def find_matches(self, request):
        """Find matches for the current user"""
        try:
            user_profile = request.user.creatorprofile
        except AttributeError:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Validate request data
            serializer = MatchRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = serializer.validated_data
            limit = validated_data.get('limit', 10)
            filters = {
                'location': validated_data.get('location'),
                'skills': validated_data.get('skills'),
                'experience_level': validated_data.get('experience_level')
            }
            
            # Remove None values from filters
            filters = {k: v for k, v in filters.items() if v}
            
            # Find matches
            matches = matching_service.find_matches(user_profile, limit, filters)
            
            # Serialize results
            match_serializer = MatchResultSerializer(matches, many=True)
            
            return Response({
                'matches': match_serializer.data,
                'count': len(matches),
                'filters_applied': filters
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error finding matches: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def mark_viewed(self, request, pk=None):
        """Mark a match as viewed"""
        try:
            match = self.get_object()
            match.status = 'viewed'
            match.viewed_at = timezone.now()
            match.save()
            
            serializer = self.get_serializer(match)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Error marking match as viewed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def mark_contacted(self, request, pk=None):
        """Mark a match as contacted"""
        try:
            match = self.get_object()
            match.status = 'contacted'
            match.save()
            
            serializer = self.get_serializer(match)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Error marking match as contacted: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        """Decline a match"""
        try:
            match = self.get_object()
            match.status = 'declined'
            match.save()
            
            serializer = self.get_serializer(match)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Error declining match: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MatchFeedbackViewSet(viewsets.ModelViewSet):
    """ViewSet for match feedback"""
    serializer_class = MatchFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter to current user's feedback"""
        try:
            user_profile = self.request.user.creatorprofile
            return MatchFeedback.objects.filter(user=user_profile).select_related(
                'match_result__matched_creator'
            )
        except AttributeError:
            return MatchFeedback.objects.none()
    
    def perform_create(self, serializer):
        """Set the user when creating feedback"""
        try:
            user_profile = self.request.user.creatorprofile
            serializer.save(user=user_profile)
        except AttributeError:
            raise serializers.ValidationError({'error': 'User profile not found'})


class MatchHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for match history (read-only)"""
    serializer_class = MatchHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter to current user's history"""
        user_profile = self.request.user.creatorprofile
        return MatchHistory.objects.filter(user=user_profile)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_match(request):
    """Batch matching for multiple creators"""
    try:
        # Validate request data
        serializer = BatchMatchRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        creator_ids = validated_data['creator_ids']
        limit_per_creator = validated_data.get('limit_per_creator', 5)
        filters = validated_data.get('filters', {})
        
        # Get creators
        from accounts.models import CreatorProfile
        creators = CreatorProfile.objects.filter(id__in=creator_ids)
        
        results = {}
        
        for creator in creators:
            try:
                matches = matching_service.find_matches(creator, limit_per_creator, filters)
                match_serializer = MatchResultSerializer(matches, many=True)
                results[str(creator.id)] = {
                    'creator_name': creator.display_name,
                    'matches': match_serializer.data,
                    'count': len(matches)
                }
            except Exception as e:
                results[str(creator.id)] = {
                    'creator_name': creator.display_name,
                    'error': str(e),
                    'matches': [],
                    'count': 0
                }
        
        return Response({
            'results': results,
            'total_creators': len(creators),
            'successful_matches': len([r for r in results.values() if 'error' not in r])
        })
        
    except Exception as e:
        return Response(
            {'error': f'Error in batch matching: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def match_statistics(request):
    """Get matching statistics for the current user"""
    try:
        user_profile = request.user.creatorprofile
    except AttributeError:
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        stats = matching_service.get_match_statistics(user_profile)
        serializer = MatchStatisticsSerializer(stats)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {'error': f'Failed to get match statistics: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
