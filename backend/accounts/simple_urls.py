"""
Simplified URLs for demo
"""
from django.urls import path, include
from django.http import JsonResponse
from .simple_views import RegisterView, LoginView, ProfileView, dashboard_view

def auth_health(request):
    """Auth service health check"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'authentication',
        'endpoints': {
            'register': '/api/auth/register/',
            'login': '/api/auth/login/',
            'profile': '/api/auth/profile/'
        }
    })

def profile_health(request):
    """Profile service health check"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'profiles',
        'endpoints': {
            'profiles': '/api/accounts/profiles/',
            'dashboard': '/api/accounts/dashboard/'
        }
    })

urlpatterns = [
    path('health/', auth_health, name='auth_health'),
    path('profile/health/', profile_health, name='profile_health'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profiles/', ProfileView.as_view(), name='profiles_list'),  # For /api/accounts/profiles/
    path('dashboard/', dashboard_view, name='dashboard'),
    path('subscription/', include('accounts.subscription_urls')),
]
