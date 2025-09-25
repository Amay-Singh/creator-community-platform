from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications_list, name='notifications-list'),
    path('mark-read/', views.mark_notifications_read, name='mark-notifications-read'),
    path('unread-count/', views.unread_count, name='unread-count'),
    path('feed/', views.activity_feed, name='activity-feed'),
    
    # Real-time notification endpoints
    path('matches/', views.match_notifications, name='match-notifications'),
    path('matches/<uuid:notification_id>/read/', views.mark_match_notification_read, name='mark-match-notification-read'),
    path('preferences/', views.notification_preferences, name='notification-preferences'),
    path('test/', views.test_notification, name='test-notification'),
    path('websocket-status/', views.websocket_status, name='websocket-status'),
    
    # Push notification endpoints
    path('push/subscribe/', views.subscribe_push, name='subscribe-push'),
    path('push/unsubscribe/', views.unsubscribe_push, name='unsubscribe-push'),
    path('push/vapid-key/', views.vapid_public_key, name='vapid-public-key'),
    path('push/test/', views.test_push_notification, name='test_push_notification'),
    
    # Analytics endpoints
    path('analytics/dashboard/', views.analytics_dashboard, name='analytics_dashboard'),
    path('analytics/delivery/', views.analytics_delivery_stats, name='analytics_delivery_stats'),
    path('analytics/engagement/', views.analytics_user_engagement, name='analytics_user_engagement'),
    path('analytics/matches/', views.analytics_match_notifications, name='analytics_match_notifications'),
    path('analytics/realtime/', views.analytics_real_time_metrics, name='analytics_real_time_metrics'),
    path('analytics/performance/', views.analytics_performance, name='analytics_performance'),
    path('analytics/user-history/', views.analytics_user_history, name='analytics_user_history'),
    
    # System monitoring endpoints
    path('health/', views.system_health, name='system_health'),
    path('alerts/', views.system_alerts, name='system_alerts'),
]
