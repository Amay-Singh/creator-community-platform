from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
import time
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class AIServiceRateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting middleware specifically for AI service endpoints.
    Implements different limits for different endpoint types.
    """
    
    # Rate limits per endpoint pattern (requests per minute)
    RATE_LIMITS = {
        '/api/ai/match/': 10,  # AI matching - expensive operations
        '/api/ai/content/': 5,  # Content generation - very expensive
        '/api/ai/recommend/': 15,  # Recommendations - moderate cost
        '/api/collaborations/': 30,  # Collaboration endpoints
        'default': 60  # Default rate limit
    }
    
    def process_request(self, request):
        # Skip rate limiting for non-AI endpoints
        if not self._is_ai_endpoint(request.path):
            return None
            
        # Get user identifier
        user_id = self._get_user_identifier(request)
        
        # Check rate limit
        if self._is_rate_limited(request.path, user_id):
            logger.warning(f"Rate limit exceeded for user {user_id} on {request.path}")
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.',
                'retry_after': 60
            }, status=429)
            
        return None
    
    def _is_ai_endpoint(self, path: str) -> bool:
        """Check if the path is an AI service endpoint"""
        ai_patterns = ['/api/ai/', '/api/collaborations/']
        return any(pattern in path for pattern in ai_patterns)
    
    def _get_user_identifier(self, request) -> str:
        """Get unique identifier for rate limiting"""
        if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
            return f"user_{request.user.id}"
        else:
            # Use IP address for anonymous users
            ip = self._get_client_ip(request)
            return f"ip_{ip}"
    
    def _get_client_ip(self, request) -> str:
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _is_rate_limited(self, path: str, user_id: str) -> bool:
        """Check if user has exceeded rate limit for this endpoint"""
        # Determine rate limit for this endpoint
        limit = self._get_rate_limit(path)
        
        # Create cache key
        cache_key = f"rate_limit_{user_id}_{self._get_endpoint_pattern(path)}"
        
        # Get current request count
        current_count = cache.get(cache_key, 0)
        
        if current_count >= limit:
            return True
        
        # Increment counter
        cache.set(cache_key, current_count + 1, 60)  # 60 seconds TTL
        return False
    
    def _get_rate_limit(self, path: str) -> int:
        """Get rate limit for specific endpoint"""
        for pattern, limit in self.RATE_LIMITS.items():
            if pattern != 'default' and pattern in path:
                return limit
        return self.RATE_LIMITS['default']
    
    def _get_endpoint_pattern(self, path: str) -> str:
        """Get endpoint pattern for cache key"""
        for pattern in self.RATE_LIMITS.keys():
            if pattern != 'default' and pattern in path:
                return pattern.replace('/', '_').strip('_')
        return 'default'

class AIServiceMonitoringMiddleware(MiddlewareMixin):
    """
    Monitoring middleware for AI service performance and errors.
    """
    
    def process_request(self, request):
        if self._is_ai_endpoint(request.path):
            request._ai_start_time = time.time()
            logger.info(f"AI Request started: {request.method} {request.path}")
        return None
    
    def process_response(self, request, response):
        if hasattr(request, '_ai_start_time'):
            duration = time.time() - request._ai_start_time
            
            # Log performance metrics
            logger.info(f"AI Request completed: {request.method} {request.path} "
                       f"- Status: {response.status_code} - Duration: {duration:.3f}s")
            
            # Log slow requests
            if duration > 5.0:  # 5 second threshold
                logger.warning(f"Slow AI request detected: {request.path} took {duration:.3f}s")
            
            # Add performance headers
            response['X-AI-Processing-Time'] = f"{duration:.3f}"
            
        return response
    
    def process_exception(self, request, exception):
        if hasattr(request, '_ai_start_time'):
            duration = time.time() - request._ai_start_time
            logger.error(f"AI Request failed: {request.method} {request.path} "
                        f"- Error: {str(exception)} - Duration: {duration:.3f}s")
        return None
    
    def _is_ai_endpoint(self, path: str) -> bool:
        """Check if the path is an AI service endpoint"""
        ai_patterns = ['/api/ai/', '/api/collaborations/']
        return any(pattern in path for pattern in ai_patterns)

class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers for AI service endpoints.
    """
    
    def process_response(self, request, response):
        if self._is_ai_endpoint(request.path):
            # Add security headers
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['X-XSS-Protection'] = '1; mode=block'
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Add AI-specific headers
            response['X-AI-Service'] = 'creator-platform-ai'
            response['X-Rate-Limit-Remaining'] = '10'  # Will be updated by rate limiting
            
        return response
    
    def _is_ai_endpoint(self, path: str) -> bool:
        """Check if the path is an AI service endpoint"""
        ai_patterns = ['/api/ai/', '/api/collaborations/']
        return any(pattern in path for pattern in ai_patterns)
