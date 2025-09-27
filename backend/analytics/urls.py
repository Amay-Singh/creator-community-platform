"""
Analytics URL configuration
"""
from django.urls import path
from . import views
from analytics_service import analytics_health_endpoint

app_name = 'analytics'

urlpatterns = [
    # Dashboard and overview
    path('dashboard/', views.analytics_dashboard, name='dashboard'),
    path('health/', analytics_health_endpoint, name='analytics_health_endpoint'),
    
    # Metrics endpoints
    path('platform-metrics/', views.platform_metrics, name='platform_metrics'),
    path('user-engagement/', views.user_engagement, name='user_engagement'),
    path('matching/', views.matching_analytics, name='matching_analytics'),
    path('notifications/', views.notification_analytics, name='notification_analytics'),
    path('realtime/', views.realtime_analytics, name='realtime_analytics'),
    
    # Events and collection
    path('events/', views.analytics_events, name='analytics_events'),
    path('collect/', views.collect_metrics, name='collect_metrics'),
]
