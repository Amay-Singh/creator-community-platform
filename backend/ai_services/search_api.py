"""
Advanced Search API Views for Creator Community Platform
Implements P5-002: Advanced search with filters and talent map
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .search_engine import AdvancedSearchEngine, SearchRequest
import logging

logger = logging.getLogger(__name__)

# Initialize search engine
search_engine = AdvancedSearchEngine()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def advanced_search(request):
    """
    Advanced search with filters and geospatial support
    
    POST /api/ai/search/advanced/
    {
        "query": "music producer",
        "category": "performing_arts",
        "experience_level": "intermediate",
        "location": "New York",
        "radius_km": 50,
        "lat": 40.7128,
        "lng": -74.0060,
        "skills": ["music_production", "mixing"],
        "min_rating": 4.0,
        "page": 1,
        "page_size": 20,
        "sort_by": "relevance"
    }
    """
    try:
        data = request.data
        
        # Create search request
        search_request = SearchRequest(
            query=data.get('query', ''),
            category=data.get('category'),
            experience_level=data.get('experience_level'),
            location=data.get('location'),
            radius_km=data.get('radius_km'),
            lat=data.get('lat'),
            lng=data.get('lng'),
            skills=data.get('skills', []),
            min_rating=data.get('min_rating'),
            availability=data.get('availability'),
            page=data.get('page', 1),
            page_size=min(data.get('page_size', 20), 100),  # Max 100 per page
            sort_by=data.get('sort_by', 'relevance')
        )
        
        # Perform search
        search_response = search_engine.search(search_request)
        
        # Convert to API response format
        response_data = {
            'results': [
                {
                    'profile_id': result.profile_id,
                    'user_id': result.user_id,
                    'display_name': result.display_name,
                    'category': result.category,
                    'experience_level': result.experience_level,
                    'location': result.location,
                    'bio': result.bio,
                    'relevance_score': result.relevance_score,
                    'distance_km': result.distance_km,
                    'rating': result.rating,
                    'portfolio_count': result.portfolio_count,
                    'skills': result.skills or [],
                    'social_links': result.social_links or {}
                }
                for result in search_response.results
            ],
            'pagination': {
                'total_count': search_response.total_count,
                'page': search_response.page,
                'page_size': search_response.page_size,
                'total_pages': search_response.total_pages
            },
            'aggregations': search_response.aggregations,
            'query_time_ms': search_response.query_time_ms
        }
        
        logger.info(f"Advanced search completed: {search_response.total_count} results in {search_response.query_time_ms}ms")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in advanced search: {str(e)}")
        return Response(
            {'error': 'Search failed', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def talent_map(request):
    """
    Get talent map data for visualization
    
    GET /api/ai/search/talent-map/?north=41.0&south=40.0&east=-73.0&west=-74.0&zoom=10
    """
    try:
        # Get bounds from query parameters
        bounds = {
            'north': float(request.GET.get('north', 41.0)),
            'south': float(request.GET.get('south', 40.0)),
            'east': float(request.GET.get('east', -73.0)),
            'west': float(request.GET.get('west', -74.0))
        }
        
        zoom_level = int(request.GET.get('zoom', 10))
        
        # Get talent map data
        map_data = search_engine.get_talent_map_data(bounds, zoom_level)
        
        # Format clusters for API response
        formatted_clusters = []
        for cluster in map_data.get('clusters', []):
            formatted_clusters.append({
                'id': cluster['id'],
                'lat': cluster['lat'],
                'lng': cluster['lng'],
                'size': cluster['size'],
                'profiles': [
                    {
                        'id': str(profile.id),
                        'display_name': profile.display_name,
                        'category': profile.category,
                        'experience_level': profile.experience_level
                    }
                    for profile in cluster.get('profiles', [])
                ]
            })
        
        response_data = {
            'clusters': formatted_clusters,
            'heatmap': map_data.get('heatmap', []),
            'category_stats': map_data.get('category_stats', {}),
            'total_profiles': map_data.get('total_profiles', 0),
            'bounds': bounds,
            'zoom_level': zoom_level
        }
        
        logger.info(f"Talent map data generated: {len(formatted_clusters)} clusters")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error generating talent map: {str(e)}")
        return Response(
            {'error': 'Talent map generation failed', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_suggestions(request):
    """
    Get search suggestions for autocomplete
    
    GET /api/ai/search/suggestions/?q=music&limit=10
    """
    try:
        query = request.GET.get('q', '').strip()
        limit = min(int(request.GET.get('limit', 10)), 20)  # Max 20 suggestions
        
        if len(query) < 2:
            return Response({'suggestions': []}, status=status.HTTP_200_OK)
        
        suggestions = search_engine.get_search_suggestions(query, limit)
        
        response_data = {
            'suggestions': suggestions,
            'query': query
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting search suggestions: {str(e)}")
        return Response(
            {'error': 'Search suggestions failed', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_filters(request):
    """
    Get available search filters and their options
    
    GET /api/ai/search/filters/
    """
    try:
        from accounts.models import CreatorProfile
        
        # Get available categories
        categories = CreatorProfile.objects.values_list(
            'category', flat=True
        ).distinct().exclude(category__isnull=True)
        
        # Get available experience levels
        experience_levels = CreatorProfile.objects.values_list(
            'experience_level', flat=True
        ).distinct().exclude(experience_level__isnull=True)
        
        # Get popular locations
        locations = CreatorProfile.objects.exclude(
            location__isnull=True
        ).exclude(
            location=""
        ).values_list('location', flat=True).distinct()[:50]
        
        response_data = {
            'categories': [
                {'value': cat, 'label': cat.replace('_', ' ').title()}
                for cat in categories if cat
            ],
            'experience_levels': [
                {'value': level, 'label': level.replace('_', ' ').title()}
                for level in experience_levels if level
            ],
            'locations': [
                {'value': loc, 'label': loc}
                for loc in locations if loc
            ],
            'sort_options': [
                {'value': 'relevance', 'label': 'Relevance'},
                {'value': 'recent', 'label': 'Most Recent'},
                {'value': 'rating', 'label': 'Highest Rated'},
                {'value': 'distance', 'label': 'Nearest'}
            ]
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting search filters: {str(e)}")
        return Response(
            {'error': 'Search filters failed', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def search_health(request):
    """
    Health check for search service
    
    GET /api/ai/search/health/
    """
    try:
        from accounts.models import CreatorProfile
        
        # Basic health checks
        total_profiles = CreatorProfile.objects.count()
        
        # Test cache
        cache_key = "search_health_test"
        cache.set(cache_key, "ok", 60)
        cache_test = cache.get(cache_key) == "ok"
        
        health_data = {
            'status': 'healthy',
            'total_profiles': total_profiles,
            'cache_working': cache_test,
            'search_engine': 'operational',
            'timestamp': '2025-08-20T07:47:00Z'
        }
        
        return Response(health_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Search health check failed: {str(e)}")
        return Response(
            {'status': 'unhealthy', 'error': str(e)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
