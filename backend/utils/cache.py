"""
Performance caching utilities for Creator Community Platform
"""
from django.core.cache import cache
from django.conf import settings
from functools import wraps
import hashlib
import json
import logging

logger = logging.getLogger(__name__)

# Cache timeout constants
CACHE_TIMEOUT_SHORT = 60 * 5      # 5 minutes
CACHE_TIMEOUT_MEDIUM = 60 * 15    # 15 minutes  
CACHE_TIMEOUT_LONG = 60 * 60      # 1 hour
CACHE_TIMEOUT_VERY_LONG = 60 * 60 * 24  # 24 hours

def make_cache_key(*args, **kwargs):
    """
    Generate a consistent cache key from arguments
    """
    key_data = {
        'args': args,
        'kwargs': sorted(kwargs.items())
    }
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode()).hexdigest()

def cache_result(timeout=CACHE_TIMEOUT_MEDIUM, key_prefix=''):
    """
    Decorator to cache function results
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{make_cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            logger.debug(f"Cache set for {cache_key}")
            return result
        return wrapper
    return decorator

def invalidate_cache_pattern(pattern):
    """
    Invalidate cache keys matching a pattern
    """
    try:
        cache.delete_many(cache.keys(pattern))
        logger.info(f"Invalidated cache pattern: {pattern}")
    except Exception as e:
        logger.error(f"Failed to invalidate cache pattern {pattern}: {e}")

class CacheManager:
    """
    Centralized cache management for common operations
    """
    
    @staticmethod
    def get_user_profile(user_id):
        """Get cached user profile"""
        cache_key = f"user_profile:{user_id}"
        return cache.get(cache_key)
    
    @staticmethod
    def set_user_profile(user_id, profile_data, timeout=CACHE_TIMEOUT_LONG):
        """Cache user profile"""
        cache_key = f"user_profile:{user_id}"
        cache.set(cache_key, profile_data, timeout)
    
    @staticmethod
    def invalidate_user_profile(user_id):
        """Invalidate user profile cache"""
        cache_key = f"user_profile:{user_id}"
        cache.delete(cache_key)
    
    @staticmethod
    def get_notifications(user_id, page=1):
        """Get cached notifications"""
        cache_key = f"notifications:{user_id}:page:{page}"
        return cache.get(cache_key)
    
    @staticmethod
    def set_notifications(user_id, notifications_data, page=1, timeout=CACHE_TIMEOUT_SHORT):
        """Cache notifications"""
        cache_key = f"notifications:{user_id}:page:{page}"
        cache.set(cache_key, notifications_data, timeout)
    
    @staticmethod
    def invalidate_user_notifications(user_id):
        """Invalidate all notification caches for a user"""
        pattern = f"notifications:{user_id}:*"
        invalidate_cache_pattern(pattern)
    
    @staticmethod
    def get_ai_matches(user_id, filters_hash):
        """Get cached AI matches"""
        cache_key = f"ai_matches:{user_id}:{filters_hash}"
        return cache.get(cache_key)
    
    @staticmethod
    def set_ai_matches(user_id, matches_data, filters_hash, timeout=CACHE_TIMEOUT_MEDIUM):
        """Cache AI matches"""
        cache_key = f"ai_matches:{user_id}:{filters_hash}"
        cache.set(cache_key, matches_data, timeout)
    
    @staticmethod
    def get_collaboration_invites(user_id):
        """Get cached collaboration invites"""
        cache_key = f"collaboration_invites:{user_id}"
        return cache.get(cache_key)
    
    @staticmethod
    def set_collaboration_invites(user_id, invites_data, timeout=CACHE_TIMEOUT_SHORT):
        """Cache collaboration invites"""
        cache_key = f"collaboration_invites:{user_id}"
        cache.set(cache_key, invites_data, timeout)
    
    @staticmethod
    def invalidate_user_invites(user_id):
        """Invalidate collaboration invites cache"""
        cache_key = f"collaboration_invites:{user_id}"
        cache.delete(cache_key)

# Performance monitoring cache keys
PERFORMANCE_CACHE_KEYS = {
    'api_response_times': 'perf:api_response_times',
    'db_query_times': 'perf:db_query_times',
    'cache_hit_rates': 'perf:cache_hit_rates',
    'active_users': 'perf:active_users',
}

def track_performance_metric(metric_name, value, timestamp=None):
    """
    Track performance metrics in cache
    """
    import time
    if timestamp is None:
        timestamp = time.time()
    
    cache_key = PERFORMANCE_CACHE_KEYS.get(metric_name)
    if not cache_key:
        return
    
    # Get existing metrics
    metrics = cache.get(cache_key, [])
    
    # Add new metric
    metrics.append({
        'value': value,
        'timestamp': timestamp
    })
    
    # Keep only last 1000 entries
    metrics = metrics[-1000:]
    
    # Store back in cache
    cache.set(cache_key, metrics, CACHE_TIMEOUT_VERY_LONG)
