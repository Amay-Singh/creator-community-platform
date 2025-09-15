"""
Advanced Search Engine for Creator Community Platform
Implements P5-002: Advanced search with filters and talent map
"""
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q, Count, Avg
from accounts.models import CreatorProfile
import json
import math
import re

logger = logging.getLogger(__name__)

@dataclass
class SearchRequest:
    """Search request parameters"""
    query: str = ""
    category: Optional[str] = None
    experience_level: Optional[str] = None
    location: Optional[str] = None
    radius_km: Optional[float] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    skills: Optional[List[str]] = None
    min_rating: Optional[float] = None
    availability: Optional[str] = None
    page: int = 1
    page_size: int = 20
    sort_by: str = "relevance"  # relevance, distance, rating, recent

@dataclass
class SearchResult:
    """Search result item"""
    profile_id: str
    user_id: str
    display_name: str
    category: str
    experience_level: str
    location: str
    bio: str
    relevance_score: float
    distance_km: Optional[float] = None
    rating: Optional[float] = None
    portfolio_count: int = 0
    skills: List[str] = None
    social_links: Dict[str, str] = None

@dataclass
class SearchResponse:
    """Search response with results and metadata"""
    results: List[SearchResult]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    aggregations: Dict[str, Any]
    query_time_ms: int

class AdvancedSearchEngine:
    """
    Advanced search engine with filtering, geospatial search, and talent mapping
    Uses Elasticsearch-like functionality with Django ORM fallback
    """
    
    def __init__(self):
        self.cache_timeout = getattr(settings, 'SEARCH_CACHE_TIMEOUT', 300)  # 5 minutes
        self.max_results = getattr(settings, 'SEARCH_MAX_RESULTS', 1000)
        
    def search(self, request: SearchRequest) -> SearchResponse:
        """
        Perform advanced search with filters and geospatial support
        """
        try:
            import time
            start_time = time.time()
            
            # Generate cache key
            cache_key = self._generate_cache_key(request)
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f"Returning cached search results for key: {cache_key}")
                return cached_result
            
            # Build queryset with filters
            queryset = self._build_queryset(request)
            
            # Apply text search
            if request.query:
                queryset = self._apply_text_search(queryset, request.query)
            
            # Apply geospatial filtering
            if request.lat and request.lng and request.radius_km:
                queryset = self._apply_geospatial_filter(queryset, request)
            
            # Get total count before pagination
            total_count = queryset.count()
            
            # Apply sorting
            queryset = self._apply_sorting(queryset, request)
            
            # Apply pagination
            start_idx = (request.page - 1) * request.page_size
            end_idx = start_idx + request.page_size
            paginated_queryset = queryset[start_idx:end_idx]
            
            # Convert to search results
            results = []
            for profile in paginated_queryset:
                result = self._profile_to_search_result(profile, request)
                results.append(result)
            
            # Generate aggregations
            aggregations = self._generate_aggregations(queryset)
            
            # Create response
            total_pages = math.ceil(total_count / request.page_size)
            query_time_ms = int((time.time() - start_time) * 1000)
            
            response = SearchResponse(
                results=results,
                total_count=total_count,
                page=request.page,
                page_size=request.page_size,
                total_pages=total_pages,
                aggregations=aggregations,
                query_time_ms=query_time_ms
            )
            
            # Cache the result
            cache.set(cache_key, response, self.cache_timeout)
            
            logger.info(f"Search completed: {total_count} results in {query_time_ms}ms")
            return response
            
        except Exception as e:
            logger.error(f"Error performing search: {str(e)}")
            return SearchResponse(
                results=[],
                total_count=0,
                page=request.page,
                page_size=request.page_size,
                total_pages=0,
                aggregations={},
                query_time_ms=0
            )
    
    def get_talent_map_data(
        self, 
        bounds: Dict[str, float], 
        zoom_level: int = 10
    ) -> Dict[str, Any]:
        """
        Get talent map data for visualization
        bounds: {"north": lat, "south": lat, "east": lng, "west": lng}
        """
        try:
            # Determine clustering level based on zoom
            cluster_size = self._get_cluster_size(zoom_level)
            
            # Get profiles within bounds (placeholder - no lat/lng in current model)
            profiles = CreatorProfile.objects.all()[:100]  # Limit for demo
            
            # Generate mock clusters for demonstration
            clusters = self._generate_mock_clusters(profiles, bounds)
            
            # Generate heatmap data
            heatmap_data = self._generate_heatmap_data(profiles)
            
            # Category distribution
            category_stats = self._get_category_distribution(profiles)
            
            return {
                "clusters": clusters,
                "heatmap": heatmap_data,
                "category_stats": category_stats,
                "total_profiles": len(profiles),
                "bounds": bounds,
                "zoom_level": zoom_level
            }
            
        except Exception as e:
            logger.error(f"Error generating talent map data: {str(e)}")
            return {
                "clusters": [],
                "heatmap": [],
                "category_stats": {},
                "total_profiles": 0,
                "bounds": bounds,
                "zoom_level": zoom_level
            }
    
    def get_search_suggestions(self, partial_query: str, limit: int = 10) -> List[str]:
        """Get search suggestions for autocomplete"""
        try:
            cache_key = f"search_suggestions:{partial_query}:{limit}"
            cached_suggestions = cache.get(cache_key)
            if cached_suggestions:
                return cached_suggestions
            
            suggestions = []
            
            # Category suggestions
            categories = CreatorProfile.objects.filter(
                category__icontains=partial_query
            ).values_list('category', flat=True).distinct()[:limit//2]
            suggestions.extend(categories)
            
            # Location suggestions
            locations = CreatorProfile.objects.filter(
                location__icontains=partial_query
            ).values_list('location', flat=True).distinct()[:limit//2]
            suggestions.extend(locations)
            
            # Cache suggestions
            cache.set(cache_key, suggestions, 3600)  # 1 hour
            
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"Error getting search suggestions: {str(e)}")
            return []
    
    def _generate_cache_key(self, request: SearchRequest) -> str:
        """Generate cache key for search request"""
        key_data = {
            'query': request.query,
            'category': request.category,
            'experience_level': request.experience_level,
            'location': request.location,
            'radius_km': request.radius_km,
            'lat': request.lat,
            'lng': request.lng,
            'skills': request.skills,
            'min_rating': request.min_rating,
            'page': request.page,
            'page_size': request.page_size,
            'sort_by': request.sort_by
        }
        import hashlib
        key_string = json.dumps(key_data, sort_keys=True)
        return f"search:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    def _build_queryset(self, request: SearchRequest):
        """Build base queryset with filters"""
        queryset = CreatorProfile.objects.select_related('user').all()
        
        # Category filter
        if request.category:
            queryset = queryset.filter(category=request.category)
        
        # Experience level filter
        if request.experience_level:
            queryset = queryset.filter(experience_level=request.experience_level)
        
        # Location filter
        if request.location:
            queryset = queryset.filter(location__icontains=request.location)
        
        # Rating filter (placeholder - no rating field in current model)
        if request.min_rating:
            # queryset = queryset.filter(rating__gte=request.min_rating)
            pass
        
        return queryset
    
    def _apply_text_search(self, queryset, query: str):
        """Apply text search across multiple fields"""
        # Split query into terms
        terms = re.findall(r'\w+', query.lower())
        
        # Build Q objects for each term
        q_objects = Q()
        for term in terms:
            q_objects |= (
                Q(display_name__icontains=term) |
                Q(bio__icontains=term) |
                Q(category__icontains=term) |
                Q(subcategory__icontains=term) |
                Q(location__icontains=term)
            )
        
        return queryset.filter(q_objects)
    
    def _apply_geospatial_filter(self, queryset, request: SearchRequest):
        """Apply geospatial filtering (placeholder - no coordinates in current model)"""
        # In a real implementation, this would use PostGIS or similar
        # For now, return the queryset unchanged
        logger.info(f"Geospatial filter requested: lat={request.lat}, lng={request.lng}, radius={request.radius_km}km")
        return queryset
    
    def _apply_sorting(self, queryset, request: SearchRequest):
        """Apply sorting to queryset"""
        if request.sort_by == "recent":
            return queryset.order_by('-created_at')
        elif request.sort_by == "rating":
            # Placeholder - no rating field
            return queryset.order_by('-health_score')
        elif request.sort_by == "distance":
            # Placeholder - no distance calculation
            return queryset.order_by('id')
        else:  # relevance
            return queryset.order_by('-validation_score', '-health_score')
    
    def _profile_to_search_result(self, profile: CreatorProfile, request: SearchRequest) -> SearchResult:
        """Convert CreatorProfile to SearchResult"""
        # Calculate relevance score
        relevance_score = self._calculate_relevance_score(profile, request)
        
        # Calculate distance (placeholder)
        distance_km = None
        if request.lat and request.lng:
            distance_km = self._calculate_distance_placeholder(profile, request.lat, request.lng)
        
        # Get social links
        social_links = {}
        if profile.instagram_url:
            social_links['instagram'] = profile.instagram_url
        if profile.youtube_url:
            social_links['youtube'] = profile.youtube_url
        if profile.spotify_url:
            social_links['spotify'] = profile.spotify_url
        if profile.website_url:
            social_links['website'] = profile.website_url
        
        return SearchResult(
            profile_id=str(profile.id),
            user_id=str(profile.user.id),
            display_name=profile.display_name,
            category=profile.category,
            experience_level=profile.experience_level,
            location=profile.location or "",
            bio=profile.bio or "",
            relevance_score=relevance_score,
            distance_km=distance_km,
            rating=profile.health_score,  # Use health_score as proxy for rating
            portfolio_count=0,  # Placeholder
            skills=[],  # Placeholder
            social_links=social_links
        )
    
    def _calculate_relevance_score(self, profile: CreatorProfile, request: SearchRequest) -> float:
        """Calculate relevance score for search result"""
        score = 0.0
        
        # Base score from profile completeness
        score += profile.validation_score * 0.3
        score += profile.health_score * 0.2
        
        # Query matching bonus
        if request.query:
            query_lower = request.query.lower()
            if query_lower in (profile.display_name or "").lower():
                score += 0.3
            if query_lower in (profile.bio or "").lower():
                score += 0.2
            if query_lower in (profile.category or "").lower():
                score += 0.1
        
        # Category match bonus
        if request.category and profile.category == request.category:
            score += 0.2
        
        # Experience level match bonus
        if request.experience_level and profile.experience_level == request.experience_level:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_distance_placeholder(self, profile: CreatorProfile, lat: float, lng: float) -> float:
        """Placeholder distance calculation"""
        # Return random distance for demo purposes
        import random
        return random.uniform(1.0, 50.0)
    
    def _generate_aggregations(self, queryset) -> Dict[str, Any]:
        """Generate search result aggregations"""
        try:
            # Category aggregation
            category_agg = queryset.values('category').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # Experience level aggregation
            experience_agg = queryset.values('experience_level').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # Location aggregation (top cities)
            location_agg = queryset.exclude(
                location__isnull=True
            ).exclude(
                location=""
            ).values('location').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
            
            return {
                "categories": list(category_agg),
                "experience_levels": list(experience_agg),
                "locations": list(location_agg),
                "total_profiles": queryset.count()
            }
            
        except Exception as e:
            logger.error(f"Error generating aggregations: {str(e)}")
            return {}
    
    def _get_cluster_size(self, zoom_level: int) -> float:
        """Determine cluster size based on zoom level"""
        # Higher zoom = smaller clusters
        if zoom_level >= 15:
            return 0.01  # ~1km
        elif zoom_level >= 12:
            return 0.05  # ~5km
        elif zoom_level >= 10:
            return 0.1   # ~10km
        else:
            return 0.5   # ~50km
    
    def _generate_mock_clusters(self, profiles, bounds: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate mock clusters for demonstration"""
        clusters = []
        
        # Create some sample clusters within bounds
        import random
        num_clusters = min(len(profiles) // 5, 20)
        
        for i in range(num_clusters):
            # Random position within bounds
            lat = random.uniform(bounds.get('south', 40.0), bounds.get('north', 41.0))
            lng = random.uniform(bounds.get('west', -74.5), bounds.get('east', -73.5))
            
            # Random cluster size
            size = random.randint(1, 10)
            
            clusters.append({
                "id": f"cluster_{i}",
                "lat": lat,
                "lng": lng,
                "size": size,
                "profiles": profiles[i*5:(i+1)*5] if i*5 < len(profiles) else []
            })
        
        return clusters
    
    def _generate_heatmap_data(self, profiles) -> List[Dict[str, Any]]:
        """Generate heatmap data for talent density"""
        heatmap = []
        
        # Generate sample heatmap points
        import random
        for i in range(50):
            heatmap.append({
                "lat": random.uniform(40.0, 41.0),
                "lng": random.uniform(-74.5, -73.5),
                "intensity": random.uniform(0.1, 1.0)
            })
        
        return heatmap
    
    def _get_category_distribution(self, profiles) -> Dict[str, int]:
        """Get category distribution for profiles"""
        distribution = {}
        for profile in profiles:
            category = profile.category or "other"
            distribution[category] = distribution.get(category, 0) + 1
        
        return distribution
