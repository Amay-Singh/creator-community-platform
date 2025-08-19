"""
Ad Showcase Views
Implements REQ-17: Relevant ad showcase for creators
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404

from .ad_showcase_service import ad_showcase_service
from .models import CreatorProfile

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_relevant_ads(request):
    """Get relevant ads for the authenticated creator"""
    
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    context = request.query_params.get('context', 'general')
    result = ad_showcase_service.get_relevant_ads(profile, context)
    
    if result['success']:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def track_ad_interaction(request):
    """Track ad interaction (view, click, dismiss)"""
    
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    ad_id = request.data.get('ad_id')
    interaction_type = request.data.get('interaction_type')
    
    if not ad_id or not interaction_type:
        return Response({
            'error': 'ad_id and interaction_type are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if interaction_type not in ['view', 'click', 'dismiss']:
        return Response({
            'error': 'interaction_type must be view, click, or dismiss'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    result = ad_showcase_service.track_ad_interaction(profile, ad_id, interaction_type)
    
    if result['success']:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_ad_insights(request):
    """Get ad performance insights for the creator"""
    
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    result = ad_showcase_service.get_ad_performance_insights(profile)
    
    if result['success']:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_contextual_ads(request, context):
    """Get ads for specific context (profile, portfolio, collaboration, etc.)"""
    
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    valid_contexts = ['profile', 'portfolio', 'collaboration', 'chat', 'general']
    if context not in valid_contexts:
        return Response({
            'error': f'Invalid context. Must be one of: {", ".join(valid_contexts)}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    result = ad_showcase_service.get_relevant_ads(profile, context)
    
    if result['success']:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
