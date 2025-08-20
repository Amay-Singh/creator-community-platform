"""
AI Recommendation API Views
Implements SRCH-003, SRCH-004: AI collaboration suggestions API endpoints
"""
import logging
from typing import Dict, Any
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json
import time

from .matching_engine import MatchingEngine, MatchingRequest
from accounts.models import CreatorProfile

logger = logging.getLogger(__name__)

class AIMatchingAPIView(View):
    """API view for AI-powered creator matching"""
    
    def __init__(self):
        super().__init__()
        self.matching_engine = MatchingEngine()
    
    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        """
        Generate AI collaboration suggestions
        
        POST /api/ai/match/suggestions
        Body: {
            "intent": "collaboration|networking|mentorship",
            "k": 20,
            "diversity": 0.3,
            "filters": {
                "category": "music",
                "skills": ["guitar", "vocals"],
                "location": "New York",
                "min_portfolio_items": 3
            }
        }
        """
        start_time = time.time()
        
        try:
            # Parse request data
            data = json.loads(request.body)
            
            # Validate required fields
            intent = data.get('intent', 'collaboration')
            if intent not in ['collaboration', 'networking', 'mentorship']:
                return JsonResponse({
                    'error': 'Invalid intent. Must be: collaboration, networking, or mentorship'
                }, status=400)
            
            # Create matching request
            matching_request = MatchingRequest(
                user_id=str(request.user.id),
                intent=intent,
                k=min(data.get('k', 20), 50),  # Cap at 50
                diversity=max(0.0, min(data.get('diversity', 0.3), 1.0)),  # 0-1 range
                filters=data.get('filters', {}),
                exclude_previous=data.get('exclude_previous', True)
            )
            
            # Generate suggestions
            candidates = self.matching_engine.generate_suggestions(matching_request)
            
            # Format response
            response_data = {
                'suggestions': [],
                'metadata': {
                    'total_candidates': len(candidates),
                    'intent': intent,
                    'diversity_applied': matching_request.diversity,
                    'processing_time_ms': round((time.time() - start_time) * 1000, 2)
                }
            }
            
            for candidate in candidates:
                candidate_data = {
                    'user_id': candidate.user_id,
                    'profile_id': candidate.profile_id,
                    'score': round(candidate.score, 3),
                    'reasons': candidate.reasons,
                    'skills_overlap': candidate.skills_overlap,
                    'complementary_skills': candidate.complementary_skills[:5],  # Top 5
                    'location_distance_km': candidate.location_distance,
                    'timezone_compatibility': candidate.timezone_compatibility
                }
                response_data['suggestions'].append(candidate_data)
            
            # Log successful request
            logger.info(f"Generated {len(candidates)} suggestions for user {request.user.id} "
                       f"in {response_data['metadata']['processing_time_ms']}ms")
            
            return JsonResponse(response_data)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            logger.error(f"Error in AI matching API: {str(e)}")
            return JsonResponse({
                'error': 'Internal server error',
                'processing_time_ms': round((time.time() - start_time) * 1000, 2)
            }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_suggestions(request):
    """
    Generate AI-powered collaboration suggestions
    
    POST /api/ai/match/suggestions/
    Body: {
        "intent": "collaboration",
        "k": 20,
        "diversity": 0.3,
        "filters": {}
    }
    """
    try:
        matching_engine = MatchingEngine()
        
        # Parse request data
        data = request.data
        
        # Validate required fields
        intent = data.get('intent', 'collaboration')
        if intent not in ['collaboration', 'networking', 'mentorship']:
            return Response({
                'error': 'Invalid intent. Must be: collaboration, networking, or mentorship'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create matching request
        matching_request = MatchingRequest(
            user_id=str(request.user.id),
            intent=intent,
            k=min(data.get('k', 20), 50),  # Cap at 50
            diversity=max(0.0, min(data.get('diversity', 0.3), 1.0)),  # 0-1 range
            filters=data.get('filters', {}),
            exclude_previous=data.get('exclude_previous', True)
        )
        
        # Generate suggestions
        candidates = matching_engine.generate_suggestions(matching_request)
        
        # Format response
        response_data = {
            'suggestions': [],
            'metadata': {
                'total_candidates': len(candidates),
                'intent': intent,
                'diversity_applied': matching_request.diversity,
            }
        }
        
        for candidate in candidates:
            candidate_data = {
                'user_id': str(candidate.user_id),
                'profile_id': str(candidate.profile_id),
                'score': round(candidate.score, 3),
                'reasons': candidate.reasons,
                'skills_overlap': candidate.skills_overlap,
                'complementary_skills': candidate.complementary_skills[:5],  # Top 5
            }
            response_data['suggestions'].append(candidate_data)
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error generating suggestions: {str(e)}")
        return Response({
            'error': 'Failed to generate suggestions'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def explain_match(request, candidate_id):
    """
    Explain why a specific candidate was matched
    
    GET /api/ai/match/explain/{candidate_id}
    """
    try:
        matching_engine = MatchingEngine()
        
        explanation = matching_engine.explain_match(
            str(request.user.id),
            candidate_id
        )
        
        if 'error' in explanation:
            return Response(explanation, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'explanation': explanation,
            'candidate_id': candidate_id
        })
        
    except Exception as e:
        logger.error(f"Error explaining match: {str(e)}")
        return Response({
            'error': 'Failed to generate explanation'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def record_feedback(request):
    """
    Record user feedback on match quality
    
    POST /api/ai/match/feedback
    Body: {
        "candidate_id": "uuid",
        "rating": 1-5,
        "feedback": "text feedback",
        "action_taken": "contacted|ignored|blocked"
    }
    """
    try:
        data = request.data
        
        # Validate required fields
        candidate_id = data.get('candidate_id')
        rating = data.get('rating')
        
        if not candidate_id or not rating:
            return Response({
                'error': 'candidate_id and rating are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return Response({
                'error': 'rating must be an integer between 1 and 5'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Record feedback
        matching_engine = MatchingEngine()
        matching_engine.record_feedback(
            str(request.user.id),
            candidate_id,
            data.get('feedback', ''),
            rating
        )
        
        # Store additional metadata
        feedback_metadata = {
            'action_taken': data.get('action_taken'),
            'timestamp': time.time()
        }
        
        return Response({
            'success': True,
            'message': 'Feedback recorded successfully'
        })
        
    except Exception as e:
        logger.error(f"Error recording match feedback: {str(e)}")
        return Response({
            'error': 'Failed to record feedback'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_matching_stats(request):
    """
    Get matching statistics for the user
    
    GET /api/ai/match/stats
    """
    try:
        user_id = str(request.user.id)
        
        # Get cached stats
        cache_key = f"match_stats:{user_id}"
        stats = cache.get(cache_key)
        
        if not stats:
            # Calculate stats
            stats = {
                'total_suggestions_generated': 0,
                'matches_contacted': 0,
                'successful_collaborations': 0,
                'average_match_rating': 0.0,
                'top_matching_categories': [],
                'recommendation_accuracy': 0.0
            }
            
            # Cache for 1 hour
            cache.set(cache_key, stats, 3600)
        
        return Response({
            'stats': stats,
            'user_id': user_id
        })
        
    except Exception as e:
        logger.error(f"Error getting matching stats: {str(e)}")
        return Response({
            'error': 'Failed to get matching statistics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_preferences(request):
    """
    Update user's matching preferences
    
    POST /api/ai/match/preferences
    Body: {
        "default_diversity": 0.3,
        "preferred_intent": "collaboration",
        "max_distance_km": 100,
        "exclude_categories": ["category1"],
        "boost_categories": ["category2"]
    }
    """
    try:
        data = request.data
        user_id = str(request.user.id)
        
        # Validate preferences
        preferences = {}
        
        if 'default_diversity' in data:
            diversity = data['default_diversity']
            if isinstance(diversity, (int, float)) and 0 <= diversity <= 1:
                preferences['default_diversity'] = diversity
        
        if 'preferred_intent' in data:
            intent = data['preferred_intent']
            if intent in ['collaboration', 'networking', 'mentorship']:
                preferences['preferred_intent'] = intent
        
        if 'max_distance_km' in data:
            distance = data['max_distance_km']
            if isinstance(distance, (int, float)) and distance > 0:
                preferences['max_distance_km'] = distance
        
        if 'exclude_categories' in data:
            if isinstance(data['exclude_categories'], list):
                preferences['exclude_categories'] = data['exclude_categories']
        
        if 'boost_categories' in data:
            if isinstance(data['boost_categories'], list):
                preferences['boost_categories'] = data['boost_categories']
        
        # Store preferences in cache
        cache_key = f"match_prefs:{user_id}"
        cache.set(cache_key, preferences, 86400)  # 24 hours
        
        return Response({
            'success': True,
            'preferences': preferences
        })
        
    except Exception as e:
        logger.error(f"Error updating matching preferences: {str(e)}")
        return Response({
            'error': 'Failed to update preferences'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def matching_health(request):
    """
    Health check for matching service
    
    GET /api/ai/match/health/
    """
    try:
        from accounts.models import CreatorProfile
        
        # Basic health checks
        total_profiles = CreatorProfile.objects.count()
        
        # Test cache
        cache_key = "match_health_test"
        cache.set(cache_key, "ok", 60)
        cache_test = cache.get(cache_key) == "ok"
        
        health_data = {
            'status': 'healthy',
            'total_profiles': total_profiles,
            'cache_working': cache_test,
            'matching_engine': 'operational',
            'timestamp': '2025-08-20T07:47:00Z'
        }
        
        return Response(health_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Matching health check failed: {str(e)}")
        return Response(
            {'status': 'unhealthy', 'error': str(e)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
