"""
Simplified URLs for demo
"""
from django.urls import path, include
from .simple_views import RegisterView, LoginView, ProfileView, dashboard_view

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('subscription/', include('accounts.subscription_urls')),
]
