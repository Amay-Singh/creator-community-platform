"""
Performance monitoring middleware for Creator Community Platform
"""
import time
import logging
from django.db import connection
from django.utils.deprecation import MiddlewareMixin
from .cache import track_performance_metric

logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to track API response times and database query performance
    """
    
    def process_request(self, request):
        request.start_time = time.time()
        request.queries_before = len(connection.queries)
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            # Calculate response time
            response_time = time.time() - request.start_time
            
            # Calculate database queries
            queries_count = len(connection.queries) - getattr(request, 'queries_before', 0)
            
            # Track metrics
            track_performance_metric('api_response_times', response_time)
            
            # Log slow requests
            if response_time > 1.0:  # Log requests taking more than 1 second
                logger.warning(
                    f"Slow request: {request.method} {request.path} "
                    f"took {response_time:.2f}s with {queries_count} queries"
                )
            
            # Add performance headers
            response['X-Response-Time'] = f"{response_time:.3f}s"
            response['X-DB-Queries'] = str(queries_count)
            
            # Track database performance
            if queries_count > 0:
                total_query_time = sum(float(q['time']) for q in connection.queries[-queries_count:])
                track_performance_metric('db_query_times', total_query_time)
                response['X-DB-Time'] = f"{total_query_time:.3f}s"
        
        return response


class CacheHitRateMiddleware(MiddlewareMixin):
    """
    Middleware to track cache hit rates
    """
    
    def process_response(self, request, response):
        # Check if response came from cache
        if hasattr(response, '_cache_hit'):
            track_performance_metric('cache_hit_rates', 1 if response._cache_hit else 0)
        
        return response


class ActiveUsersMiddleware(MiddlewareMixin):
    """
    Middleware to track active users
    """
    
    def process_request(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Track active user
            track_performance_metric('active_users', request.user.id)
    
    def process_response(self, request, response):
        return response
