"""
Advanced security middleware for Creator Community Platform
"""
import time
import hashlib
import logging
from django.http import HttpResponse
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.contrib.auth import get_user_model
from analytics.services import AnalyticsCollector

User = get_user_model()
logger = logging.getLogger(__name__)


class RateLimitMiddleware(MiddlewareMixin):
    """
    Advanced rate limiting middleware with different limits for different endpoints
    """
    
    # Rate limit configurations (requests per minute)
    RATE_LIMITS = {
        '/api/auth/login': 5,           # Login attempts
        '/api/auth/register': 3,        # Registration attempts
        '/api/auth/password-reset': 2,  # Password reset requests
        '/api/collaborations/invites/send': 10,  # Collaboration invites
        '/api/ai/matches': 30,          # AI matching requests
        '/api/notifications': 60,       # Notification requests
        'default': 100                  # Default for other endpoints
    }
    
    def process_request(self, request):
        # Skip rate limiting for certain conditions
        if self._should_skip_rate_limiting(request):
            return None
        
        # Get client identifier
        client_id = self._get_client_identifier(request)
        
        # Get rate limit for this endpoint
        rate_limit = self._get_rate_limit(request.path)
        
        # Check rate limit
        if self._is_rate_limited(client_id, request.path, rate_limit):
            # Log rate limit violation
            logger.warning(
                f"Rate limit exceeded: {client_id} on {request.path} "
                f"(limit: {rate_limit}/min)"
            )
            
            # Track security event
            AnalyticsCollector.track_event(
                'rate_limit_exceeded',
                user=getattr(request, 'user', None),
                event_data={
                    'client_id': client_id,
                    'path': request.path,
                    'limit': rate_limit
                },
                request=request
            )
            
            return HttpResponse(
                'Rate limit exceeded. Please try again later.',
                status=429,
                content_type='text/plain'
            )
        
        return None
    
    def _should_skip_rate_limiting(self, request):
        """Check if rate limiting should be skipped"""
        # Skip for admin users
        if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_staff:
            return True
        
        # Skip for health checks
        if request.path in ['/api/healthz', '/health/', '/status/']:
            return True
        
        # Skip for static files
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return True
        
        return False
    
    def _get_client_identifier(self, request):
        """Get unique identifier for the client"""
        # Use user ID if authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            return f"user_{request.user.id}"
        
        # Use IP address for anonymous users
        ip = self._get_client_ip(request)
        return f"ip_{ip}"
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _get_rate_limit(self, path):
        """Get rate limit for specific path"""
        for pattern, limit in self.RATE_LIMITS.items():
            if pattern != 'default' and path.startswith(pattern):
                return limit
        return self.RATE_LIMITS['default']
    
    def _is_rate_limited(self, client_id, path, rate_limit):
        """Check if client has exceeded rate limit"""
        cache_key = f"rate_limit:{client_id}:{path}"
        
        # Get current request count
        current_count = cache.get(cache_key, 0)
        
        if current_count >= rate_limit:
            return True
        
        # Increment counter
        cache.set(cache_key, current_count + 1, 60)  # 1 minute window
        return False


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses
    """
    
    def process_response(self, request, response):
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = (
            'geolocation=(self), '
            'microphone=(), '
            'camera=(), '
            'payment=(self), '
            'usb=(), '
            'magnetometer=(), '
            'accelerometer=()'
        )
        
        # HSTS (only for HTTPS)
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


class DDoSProtectionMiddleware(MiddlewareMixin):
    """
    Advanced DDoS protection middleware
    """
    
    # Thresholds for DDoS detection
    SUSPICIOUS_REQUEST_THRESHOLD = 200  # requests per minute
    BLOCK_DURATION = 300  # 5 minutes
    
    def process_request(self, request):
        client_ip = self._get_client_ip(request)
        
        # Check if IP is already blocked
        if self._is_ip_blocked(client_ip):
            logger.warning(f"Blocked request from {client_ip} (DDoS protection)")
            return HttpResponse(
                'Access temporarily restricted.',
                status=429,
                content_type='text/plain'
            )
        
        # Track request frequency
        if self._is_suspicious_activity(client_ip):
            self._block_ip(client_ip)
            logger.warning(f"Blocking {client_ip} for suspicious activity")
            
            # Track security event
            AnalyticsCollector.track_event(
                'ddos_protection_triggered',
                event_data={
                    'client_ip': client_ip,
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'path': request.path
                },
                request=request
            )
            
            return HttpResponse(
                'Access temporarily restricted due to suspicious activity.',
                status=429,
                content_type='text/plain'
            )
        
        return None
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _is_ip_blocked(self, ip):
        """Check if IP is currently blocked"""
        cache_key = f"blocked_ip:{ip}"
        return cache.get(cache_key, False)
    
    def _is_suspicious_activity(self, ip):
        """Check if IP shows suspicious activity patterns"""
        cache_key = f"request_count:{ip}"
        
        # Get current request count
        current_count = cache.get(cache_key, 0)
        
        # Increment counter
        cache.set(cache_key, current_count + 1, 60)  # 1 minute window
        
        return current_count >= self.SUSPICIOUS_REQUEST_THRESHOLD
    
    def _block_ip(self, ip):
        """Block IP address temporarily"""
        cache_key = f"blocked_ip:{ip}"
        cache.set(cache_key, True, self.BLOCK_DURATION)


class APIKeyAuthMiddleware(MiddlewareMixin):
    """
    API key authentication middleware for external integrations
    """
    
    API_KEY_HEADER = 'HTTP_X_API_KEY'
    API_ENDPOINTS = ['/api/webhooks/', '/api/external/']
    
    def process_request(self, request):
        # Check if this is an API endpoint that requires API key
        if not any(request.path.startswith(endpoint) for endpoint in self.API_ENDPOINTS):
            return None
        
        # Get API key from header
        api_key = request.META.get(self.API_KEY_HEADER)
        
        if not api_key:
            return HttpResponse(
                'API key required',
                status=401,
                content_type='text/plain'
            )
        
        # Validate API key
        if not self._validate_api_key(api_key):
            logger.warning(f"Invalid API key attempt: {api_key[:8]}...")
            
            # Track security event
            AnalyticsCollector.track_event(
                'invalid_api_key',
                event_data={
                    'api_key_prefix': api_key[:8] if api_key else None,
                    'path': request.path,
                    'ip': request.META.get('REMOTE_ADDR')
                },
                request=request
            )
            
            return HttpResponse(
                'Invalid API key',
                status=403,
                content_type='text/plain'
            )
        
        return None
    
    def _validate_api_key(self, api_key):
        """Validate API key against stored keys"""
        # In production, this would check against a database or secure storage
        valid_keys = getattr(settings, 'VALID_API_KEYS', [])
        return api_key in valid_keys


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Log security-relevant requests for monitoring
    """
    
    SENSITIVE_ENDPOINTS = [
        '/api/auth/',
        '/api/admin/',
        '/api/users/',
        '/api/collaborations/invites/'
    ]
    
    def process_request(self, request):
        # Log sensitive endpoint access
        if any(request.path.startswith(endpoint) for endpoint in self.SENSITIVE_ENDPOINTS):
            logger.info(
                f"Sensitive endpoint access: {request.method} {request.path} "
                f"from {request.META.get('REMOTE_ADDR')} "
                f"User: {getattr(request.user, 'username', 'anonymous') if hasattr(request, 'user') else 'unknown'}"
            )
        
        return None
    
    def process_response(self, request, response):
        # Log failed authentication attempts
        if (request.path.startswith('/api/auth/') and 
            response.status_code in [401, 403]):
            
            logger.warning(
                f"Authentication failure: {request.method} {request.path} "
                f"from {request.META.get('REMOTE_ADDR')} "
                f"Status: {response.status_code}"
            )
            
            # Track security event
            AnalyticsCollector.track_event(
                'authentication_failure',
                event_data={
                    'path': request.path,
                    'status_code': response.status_code,
                    'ip': request.META.get('REMOTE_ADDR'),
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')
                },
                request=request
            )
        
        return response
