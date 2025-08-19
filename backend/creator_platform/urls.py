"""
Creator Platform URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def api_status(request):
    return JsonResponse({
        'status': 'online',
        'message': 'Creator Platform API is running',
        'endpoints': {
            'auth': '/api/auth/',
            'admin': '/admin/'
        }
    })

urlpatterns = [
    path('', api_status, name='api_status'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.simple_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
