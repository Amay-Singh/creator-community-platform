"""
Django settings for creator_platform project.
"""
from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv
import sys

# Load appropriate .env file based on environment
if 'runserver' in sys.argv or 'shell' in sys.argv:
    # Development
    load_dotenv()
else:
    # Production/CI - try production env first, fallback to default
    load_dotenv('.env.production')
    load_dotenv()  # Fallback to .env if .env.production doesn't exist

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration
# --- Paths
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Security / Debug
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-dev-key-change-in-production")
DEBUG = os.environ.get("DEBUG", "False").lower() in ("1", "true", "yes")

# Hosts / CSRF
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0,creator-platform-backend-vfuz.onrender.com").split(",") if h.strip()]
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "https://creator-platform-backend-vfuz.onrender.com,http://localhost:8000,http://localhost:8001,http://localhost:8002,http://localhost:8003,http://127.0.0.1:8000").split(",") if o.strip()]

# --- Apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "channels",
    "accounts",
    "ai_services",
    "chat",
    "collaborations",
    "notifications",
    "analytics",
    "security",
    "integrations",
    "video_collaboration",
    "enterprise",
    "globalization",  # Re-enabled for Phase 10
    "subscriptions",  # Re-enabled - table name conflicts resolved
    "axes",  # Re-enabled with proper authentication backend
    "debug_toolbar",
]

# --- Middleware
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    # Temporarily disable problematic middleware
    # "ai_services.middleware.AIServiceRateLimitMiddleware",
    # "ai_services.middleware.AIServiceMonitoringMiddleware", 
    # "ai_services.middleware.SecurityHeadersMiddleware",
    # "security.middleware.DDoSProtectionMiddleware",
    # "security.middleware.RateLimitMiddleware",
    # "security.middleware.SecurityHeadersMiddleware",
    # "security.middleware.RequestLoggingMiddleware",
    # WhiteNoise to serve collected static files in UAT/PROD
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",  # Enable debug toolbar
    # "utils.middleware.PerformanceMonitoringMiddleware",
    # "utils.middleware.CacheHitRateMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "axes.middleware.AxesMiddleware",  # Re-enabled with proper authentication backend
    # "utils.middleware.ActiveUsersMiddleware",  # Temporarily disabled
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "creator_platform.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "creator_platform.wsgi.application"

# --- Database: Postgres via DATABASE_URL, otherwise SQLite fallback
DEFAULT_SQLITE = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
DATABASES = {
    "default": dj_database_url.config(
        default=DEFAULT_SQLITE,
        conn_max_age=0,     # good with pgBouncer; OK for SQLite too
        ssl_require=False,  # Only enable for PostgreSQL
    )
}

# Only apply SSL settings for PostgreSQL connections
if DATABASES["default"]["ENGINE"].endswith("postgresql") and os.environ.get("DATABASE_URL"):
    DATABASES["default"]["ssl_require"] = True
    DATABASES["default"].setdefault("OPTIONS", {})["sslmode"] = "require"

# --- Optional Supabase config (only if used by your code)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")

# --- Cache (Redis Cloud Configuration with SSL)
import ssl
import certifi

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# Redis Cloud SSL configuration (handle missing Redis gracefully)
try:
    if REDIS_URL and REDIS_URL.startswith('rediss://'):
        REDIS_CONNECTION_KWARGS = {
            "ssl_cert_reqs": ssl.CERT_REQUIRED,
            "ssl_ca_certs": certifi.where(),
            "ssl_check_hostname": False,
            "health_check_interval": 30,
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
            "retry_on_timeout": True,
        }
    else:
        REDIS_CONNECTION_KWARGS = {
            "retry_on_timeout": True,
        }
except Exception:
    # Fallback if Redis configuration fails
    REDIS_CONNECTION_KWARGS = {
        "retry_on_timeout": True,
    }

# Fallback cache configuration for Render deployment
if os.environ.get("REDIS_URL"):
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "CONNECTION_POOL_KWARGS": REDIS_CONNECTION_KWARGS,
            },
            "KEY_PREFIX": "creator_platform",
            "TIMEOUT": 300,  # 5 minutes default
        }
    }
    # Use Redis for sessions as well
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"
else:
    # Fallback to database cache for deployment without Redis
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "cache_table",
        }
    }
    # Use database sessions as fallback
    SESSION_ENGINE = "django.contrib.sessions.backends.db"

# --- DRF
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
}

# --- CORS
# Set to True in UAT only if needed; otherwise prefer explicit allowed origins.
CORS_ALLOW_ALL_ORIGINS = os.environ.get("CORS_ALLOW_ALL_ORIGINS", "False").lower() in ("1", "true", "yes")
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3003",
    "http://127.0.0.1:3003",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# --- i18n
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Static / Media
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
# Requires 'whitenoise' in requirements.txt
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# --- File uploads
FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  # 100MB

# --- External keys (env-driven)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# --- Celery / Redis
CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# --- Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# --- Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "creator_platform.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Custom User Model
AUTH_USER_MODEL = "accounts.CustomUser"

# --- Authentication Backends (Fixed for Django Axes)
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default Django backend
    'axes.backends.AxesBackend',  # Proper Axes backend that works with DRF
]

# --- Django Channels Configuration
ASGI_APPLICATION = "creator_platform.asgi.application"

# --- Redis Configuration for Channels
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get("REDIS_URL", "redis://localhost:6379")],
        },
    },
}

# --- Cache Configuration (Production-ready)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "cache_table",
    } if not DEBUG else {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# --- Performance Monitoring & Error Tracking
# Sentry Configuration
SENTRY_DSN = os.environ.get("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(
                transaction_style='url',
                middleware_spans=True,
                signals_spans=True,
            ),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,  # Capture 10% of transactions for performance monitoring
        send_default_pii=False,  # Don't send personally identifiable information
        environment=os.environ.get("ENVIRONMENT", "development"),
        release=os.environ.get("GIT_SHA", "unknown"),
    )

# Debug Toolbar Configuration (only in DEBUG mode)
if DEBUG:
    INTERNAL_IPS = [
        "127.0.0.1",
        "localhost",
    ]

# --- Performance Settings
# Database connection pooling and optimization
DATABASES['default']['CONN_MAX_AGE'] = 60  # Keep connections alive for 60 seconds
# Note: Connection pooling is handled by Django's CONN_MAX_AGE setting
# MAX_CONNS is not a valid PostgreSQL connection parameter

# Cache timeout settings
CACHE_TTL = 60 * 15  # 15 minutes default cache timeout

# Session configuration for production reliability
SESSION_ENGINE = "django.contrib.sessions.backends.db"  # Use database sessions for production
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_SECURE = not DEBUG  # Secure cookies in production
SESSION_COOKIE_HTTPONLY = True  # Prevent XSS attacks

# --- Security Configuration
# Django Axes (brute force protection)
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # 1 hour
AXES_LOCKOUT_CALLABLE = 'axes.lockout.database_lockout'
AXES_RESET_ON_SUCCESS = True
AXES_ENABLE_ADMIN = True

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_CONNECT_SRC = ("'self'", "wss:", "ws:")
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_BASE_URI = ("'self'",)
CSP_FORM_ACTION = ("'self'",)

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookie security
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Additional security settings
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

# API Keys for external services (set via environment variables)
VALID_API_KEYS = os.environ.get("VALID_API_KEYS", "").split(",")

# Two-Factor Authentication settings
TOTP_ISSUER_NAME = "Creator Community Platform"
BACKUP_CODE_LENGTH = 8
BACKUP_CODE_COUNT = 10

# --- External Integrations Configuration (Phase 9)
# LinkedIn Integration
LINKEDIN_CLIENT_ID = os.environ.get("LINKEDIN_CLIENT_ID", "")
LINKEDIN_CLIENT_SECRET = os.environ.get("LINKEDIN_CLIENT_SECRET", "")
LINKEDIN_REDIRECT_URI = os.environ.get("LINKEDIN_REDIRECT_URI", "")

# GitHub Integration
GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET", "")
GITHUB_REDIRECT_URI = os.environ.get("GITHUB_REDIRECT_URI", "")

# Twitter/X Integration
TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET", "")
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN", "")

# Google Calendar Integration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "")

# Stripe Payment Integration
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

# OpenAI API (for advanced content generation)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# --- Logging Configuration for Error Visibility
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.StreamHandler',  # Use StreamHandler for stdout
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'ai_services': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'collaborations': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Force all errors to stdout for Render visibility
import sys
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s %(asctime)s %(name)s %(message)s',
    stream=sys.stdout
)

# --- Django Axes Configuration (Security)
# Proper configuration to prevent production issues
AXES_FAILURE_LIMIT = 5  # Allow 5 failed attempts before blocking
AXES_COOLOFF_TIME = 1  # Block for 1 hour after limit reached
AXES_LOCKOUT_CALLABLE = None  # Use default lockout behavior
AXES_ENABLE_ADMIN = True  # Enable admin interface for Axes
AXES_VERBOSE = True  # Enable verbose logging for debugging
AXES_RESET_ON_SUCCESS = True  # Reset failed attempts on successful login
AXES_LOCKOUT_PARAMETERS = ['ip_address', 'username']  # Lock by IP and username
AXES_IPWARE_PROXY_COUNT = 1  # Handle proxy headers (important for Render)
AXES_IPWARE_META_PRECEDENCE_ORDER = [
    'HTTP_X_FORWARDED_FOR',  # Render proxy header
    'HTTP_X_REAL_IP',
    'REMOTE_ADDR',
]
# Use database handler for production reliability (no Redis dependency)
AXES_CACHE = None  # Disable cache to avoid Redis dependency
AXES_HANDLER = 'axes.handlers.database.AxesDatabaseHandler'  # Use database handler

# --- Debug Toolbar Configuration
if DEBUG:
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]
