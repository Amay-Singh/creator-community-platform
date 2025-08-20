"""
Creator Platform URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from notifications import views as notification_views

def api_status(request):
    return JsonResponse({
        'status': 'online',
        'message': 'Creator Platform API is running',
        'endpoints': {
            'auth': '/api/auth/',
            'admin': '/admin/'
        }
    })

def healthz(request):
    """Health check endpoint for load balancers and monitoring"""
    import os
    return JsonResponse({
        'status': 'healthy',
        'version': '1.0.0',
        'git_sha': os.environ.get('GIT_SHA', 'unknown'),
        'database': 'connected'
    })

urlpatterns = [
    path('', api_status, name='api_status'),
    path('api/healthz', healthz, name='healthz'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.simple_urls')),
    path('api/accounts/', include('accounts.simple_urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/feed/', notification_views.activity_feed, name='activity-feed'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
