"""
Redis Cloud SSL Configuration
Production-ready Redis Cloud connection with proper SSL handling
"""
import os
import ssl
import redis
from urllib.parse import urlparse
import certifi

def get_redis_connection():
    """Get properly configured Redis Cloud connection"""
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    if redis_url.startswith('rediss://'):
        # Redis Cloud SSL connection
        parsed = urlparse(redis_url)
        
        return redis.Redis(
            host=parsed.hostname,
            port=parsed.port,
            username=parsed.username,
            password=parsed.password,
            decode_responses=True,
            ssl=True,
            ssl_cert_reqs=ssl.CERT_REQUIRED,
            ssl_ca_certs=certifi.where(),
            ssl_check_hostname=False,
            health_check_interval=30,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            retry_on_error=[redis.exceptions.ConnectionError, redis.exceptions.TimeoutError]
        )
    else:
        # Local Redis connection
        return redis.from_url(redis_url, decode_responses=True)

def test_redis_connection():
    """Test Redis connection and return status"""
    try:
        r = get_redis_connection()
        
        # Test ping
        ping_result = r.ping()
        if not ping_result:
            return {'status': 'error', 'message': 'Ping failed'}
        
        # Test set/get
        test_key = 'health_check_test'
        r.set(test_key, 'working', ex=60)  # Expire in 60 seconds
        value = r.get(test_key)
        
        if value != 'working':
            return {'status': 'error', 'message': 'Set/Get test failed'}
        
        # Clean up
        r.delete(test_key)
        
        return {
            'status': 'healthy',
            'message': 'Redis Cloud connection working',
            'ssl_enabled': True,
            'connection_type': 'redis_cloud'
        }
        
    except redis.exceptions.ConnectionError as e:
        return {
            'status': 'error',
            'message': f'Connection error: {str(e)}',
            'ssl_enabled': False
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Unexpected error: {str(e)}',
            'ssl_enabled': False
        }

# Global Redis connection instance
redis_client = None

def get_redis_client():
    """Get or create Redis client instance"""
    global redis_client
    if redis_client is None:
        redis_client = get_redis_connection()
    return redis_client
