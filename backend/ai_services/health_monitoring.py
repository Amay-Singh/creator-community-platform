"""
AI Services Health Monitoring and Performance Metrics
Phase 5 Guardian Compliance - Monitoring & Observability
"""
import time
import psutil
import logging
from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import CreatorProfile, MatchResult, ContentGenerationRequest
from .matching_service import AIMatchingService
import json
from datetime import datetime, timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)


class AIServiceHealthMonitor:
    """
    Comprehensive health monitoring for AI services
    """
    
    def __init__(self):
        self.matching_service = AIMatchingService()
        
    def get_system_health(self) -> dict:
        """Get overall system health status"""
        health_data = {
            'timestamp': timezone.now().isoformat(),
            'status': 'healthy',
            'services': {},
            'performance': {},
            'errors': []
        }
        
        try:
            # Check database connectivity
            health_data['services']['database'] = self._check_database_health()
            
            # Check cache connectivity
            health_data['services']['cache'] = self._check_cache_health()
            
            # Check AI services
            health_data['services']['ai_matching'] = self._check_ai_matching_health()
            health_data['services']['content_generation'] = self._check_content_generation_health()
            
            # Get performance metrics
            health_data['performance'] = self._get_performance_metrics()
            
            # Determine overall status
            service_statuses = [service['status'] for service in health_data['services'].values()]
            if 'critical' in service_statuses:
                health_data['status'] = 'critical'
            elif 'warning' in service_statuses:
                health_data['status'] = 'warning'
            else:
                health_data['status'] = 'healthy'
                
        except Exception as e:
            logger.error(f"Error checking system health: {str(e)}")
            health_data['status'] = 'critical'
            health_data['errors'].append(str(e))
            
        return health_data
    
    def _check_database_health(self) -> dict:
        """Check database connectivity and performance"""
        try:
            start_time = time.time()
            
            # Test basic connectivity
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            # Test AI services tables
            profile_count = CreatorProfile.objects.count()
            match_count = MatchingResult.objects.count()
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            return {
                'status': 'healthy' if response_time < 100 else 'warning',
                'response_time_ms': round(response_time, 2),
                'profile_count': profile_count,
                'match_count': match_count,
                'connection_status': 'connected'
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                'status': 'critical',
                'error': str(e),
                'connection_status': 'failed'
            }
    
    def _check_cache_health(self) -> dict:
        """Check Redis cache connectivity and performance"""
        try:
            start_time = time.time()
            
            # Test cache operations
            test_key = 'health_check_test'
            test_value = 'test_value'
            
            cache.set(test_key, test_value, 30)
            retrieved_value = cache.get(test_key)
            cache.delete(test_key)
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            return {
                'status': 'healthy' if response_time < 50 else 'warning',
                'response_time_ms': round(response_time, 2),
                'operation_success': retrieved_value == test_value,
                'connection_status': 'connected'
            }
            
        except Exception as e:
            logger.error(f"Cache health check failed: {str(e)}")
            return {
                'status': 'critical',
                'error': str(e),
                'connection_status': 'failed'
            }
    
    def _check_ai_matching_health(self) -> dict:
        """Check AI matching service health"""
        try:
            start_time = time.time()
            
            # Check if we have profiles to match
            active_profiles = CreatorProfile.objects.filter(is_available=True).count()
            
            # Check recent matching activity
            recent_matches = MatchingResult.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).count()
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            status = 'healthy'
            if active_profiles < 10:
                status = 'warning'
            if response_time > 200:
                status = 'warning'
                
            return {
                'status': status,
                'response_time_ms': round(response_time, 2),
                'active_profiles': active_profiles,
                'recent_matches_24h': recent_matches,
                'service_status': 'operational'
            }
            
        except Exception as e:
            logger.error(f"AI matching health check failed: {str(e)}")
            return {
                'status': 'critical',
                'error': str(e),
                'service_status': 'failed'
            }
    
    def _check_content_generation_health(self) -> dict:
        """Check content generation service health"""
        try:
            start_time = time.time()
            
            # Check pending requests
            pending_requests = ContentGenerationRequest.objects.filter(
                status='processing'
            ).count()
            
            # Check recent successful generations
            recent_success = ContentGenerationRequest.objects.filter(
                status='completed',
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).count()
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            status = 'healthy'
            if pending_requests > 50:
                status = 'warning'
            if response_time > 200:
                status = 'warning'
                
            return {
                'status': status,
                'response_time_ms': round(response_time, 2),
                'pending_requests': pending_requests,
                'recent_success_24h': recent_success,
                'service_status': 'operational'
            }
            
        except Exception as e:
            logger.error(f"Content generation health check failed: {str(e)}")
            return {
                'status': 'critical',
                'error': str(e),
                'service_status': 'failed'
            }
    
    def _get_performance_metrics(self) -> dict:
        """Get system performance metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Database connection pool info
            db_connections = len(connection.queries) if hasattr(connection, 'queries') else 0
            
            return {
                'cpu_usage_percent': cpu_percent,
                'memory_usage_percent': memory.percent,
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'disk_usage_percent': disk.percent,
                'disk_free_gb': round(disk.free / (1024**3), 2),
                'database_connections': db_connections,
                'cache_hit_rate': self._get_cache_hit_rate()
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
            return {'error': str(e)}
    
    def _get_cache_hit_rate(self) -> float:
        """Calculate cache hit rate (simplified)"""
        try:
            # This is a simplified implementation
            # In production, you'd track hits/misses more accurately
            cache_stats = cache.get('cache_stats', {'hits': 0, 'misses': 0})
            total = cache_stats['hits'] + cache_stats['misses']
            
            if total == 0:
                return 0.0
                
            return round((cache_stats['hits'] / total) * 100, 2)
            
        except Exception:
            return 0.0


# Health check endpoints
health_monitor = AIServiceHealthMonitor()


@api_view(['GET'])
@permission_classes([])  # Public endpoint for monitoring
def health_check(request):
    """
    Public health check endpoint for load balancers and monitoring
    """
    try:
        health_data = health_monitor.get_system_health()
        
        # Return appropriate HTTP status based on health
        if health_data['status'] == 'critical':
            return Response(health_data, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        elif health_data['status'] == 'warning':
            return Response(health_data, status=status.HTTP_200_OK)
        else:
            return Response(health_data, status=status.HTTP_200_OK)
            
    except Exception as e:
        logger.error(f"Health check endpoint error: {str(e)}")
        return Response(
            {
                'status': 'critical',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detailed_health_check(request):
    """
    Detailed health check for authenticated users (admin/monitoring)
    """
    try:
        health_data = health_monitor.get_system_health()
        
        # Add additional detailed metrics for authenticated users
        health_data['detailed_metrics'] = {
            'recent_errors': get_recent_errors(),
            'performance_trends': get_performance_trends(),
            'service_uptime': get_service_uptime()
        }
        
        return Response(health_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Detailed health check error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def get_recent_errors() -> list:
    """Get recent error logs (last 24 hours)"""
    try:
        # This would integrate with your logging system
        # For now, return mock data
        return [
            {
                'timestamp': (timezone.now() - timedelta(hours=2)).isoformat(),
                'level': 'WARNING',
                'message': 'Slow AI request detected: /api/ai/match/suggestions took 6.234s',
                'service': 'ai_matching'
            }
        ]
    except Exception:
        return []


def get_performance_trends() -> dict:
    """Get performance trends over time"""
    try:
        # This would integrate with your metrics collection system
        # For now, return mock data
        return {
            'avg_response_time_ms': 245,
            'trend_direction': 'stable',
            'peak_cpu_usage': 67.5,
            'peak_memory_usage': 78.2
        }
    except Exception:
        return {}


def get_service_uptime() -> dict:
    """Get service uptime information"""
    try:
        # This would track actual service start times
        # For now, return mock data
        return {
            'ai_matching_uptime_hours': 168.5,
            'content_generation_uptime_hours': 165.2,
            'database_uptime_hours': 720.0
        }
    except Exception:
        return {}


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_service_cache(request):
    """
    Clear AI service caches (admin endpoint)
    """
    try:
        # Clear specific cache patterns
        cache_patterns = [
            'user_recommendations_*',
            'project_recommendations_*',
            'ai_matching_*',
            'content_generation_*'
        ]
        
        cleared_count = 0
        for pattern in cache_patterns:
            try:
                cache.delete_pattern(pattern)
                cleared_count += 1
            except Exception as e:
                logger.warning(f"Failed to clear cache pattern {pattern}: {str(e)}")
        
        return Response({
            'status': 'success',
            'cleared_patterns': cleared_count,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Cache clear error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
