"""
Analytics models for Creator Community Platform
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()


class UserEngagementMetric(models.Model):
    """Track user engagement metrics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='engagement_metrics')
    date = models.DateField(default=timezone.now)
    
    # Session metrics
    sessions_count = models.IntegerField(default=0)
    total_session_duration = models.DurationField(default=timezone.timedelta)
    avg_session_duration = models.DurationField(default=timezone.timedelta)
    
    # Activity metrics
    pages_viewed = models.IntegerField(default=0)
    actions_performed = models.IntegerField(default=0)
    notifications_clicked = models.IntegerField(default=0)
    
    # Feature usage
    matches_viewed = models.IntegerField(default=0)
    collaborations_initiated = models.IntegerField(default=0)
    messages_sent = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date']
        indexes = [
            models.Index(fields=['date', 'user']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Engagement for {self.user.username} on {self.date}"


class PlatformMetric(models.Model):
    """Track platform-wide metrics"""
    date = models.DateField(default=timezone.now)
    
    # User metrics
    total_users = models.IntegerField(default=0)
    active_users_daily = models.IntegerField(default=0)
    active_users_weekly = models.IntegerField(default=0)
    active_users_monthly = models.IntegerField(default=0)
    new_registrations = models.IntegerField(default=0)
    
    # Engagement metrics
    total_sessions = models.IntegerField(default=0)
    avg_session_duration = models.DurationField(default=timezone.timedelta)
    total_page_views = models.IntegerField(default=0)
    
    # Feature usage
    total_matches_generated = models.IntegerField(default=0)
    successful_matches = models.IntegerField(default=0)
    collaboration_invites_sent = models.IntegerField(default=0)
    collaboration_invites_accepted = models.IntegerField(default=0)
    messages_exchanged = models.IntegerField(default=0)
    
    # Performance metrics
    avg_api_response_time = models.FloatField(default=0.0)  # in seconds
    error_rate = models.FloatField(default=0.0)  # percentage
    cache_hit_rate = models.FloatField(default=0.0)  # percentage
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Platform metrics for {self.date}"


class MatchingAnalytics(models.Model):
    """Track AI matching performance"""
    date = models.DateField(default=timezone.now)
    
    # Matching metrics
    total_match_requests = models.IntegerField(default=0)
    successful_matches = models.IntegerField(default=0)
    match_acceptance_rate = models.FloatField(default=0.0)  # percentage
    avg_match_score = models.FloatField(default=0.0)
    
    # Performance metrics
    avg_matching_time = models.FloatField(default=0.0)  # in seconds
    cache_hit_rate = models.FloatField(default=0.0)  # percentage
    
    # Quality metrics
    user_feedback_positive = models.IntegerField(default=0)
    user_feedback_negative = models.IntegerField(default=0)
    matches_leading_to_collaboration = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['match_acceptance_rate']),
        ]
    
    def __str__(self):
        return f"Matching analytics for {self.date}"


class NotificationAnalytics(models.Model):
    """Track notification performance"""
    date = models.DateField(default=timezone.now)
    
    # Delivery metrics
    total_notifications_sent = models.IntegerField(default=0)
    push_notifications_sent = models.IntegerField(default=0)
    email_notifications_sent = models.IntegerField(default=0)
    
    # Engagement metrics
    notifications_opened = models.IntegerField(default=0)
    notifications_clicked = models.IntegerField(default=0)
    open_rate = models.FloatField(default=0.0)  # percentage
    click_rate = models.FloatField(default=0.0)  # percentage
    
    # Performance metrics
    avg_delivery_time = models.FloatField(default=0.0)  # in seconds
    delivery_failure_rate = models.FloatField(default=0.0)  # percentage
    
    # User preferences
    users_opted_out = models.IntegerField(default=0)
    users_opted_in = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['open_rate', 'click_rate']),
        ]
    
    def __str__(self):
        return f"Notification analytics for {self.date}"


class RealtimeAnalytics(models.Model):
    """Track real-time collaboration metrics"""
    date = models.DateField(default=timezone.now)
    
    # Real-time session metrics
    total_realtime_sessions = models.IntegerField(default=0)
    avg_session_duration = models.DurationField(default=timezone.timedelta)
    concurrent_users_peak = models.IntegerField(default=0)
    
    # Message metrics
    total_messages_sent = models.IntegerField(default=0)
    avg_messages_per_session = models.FloatField(default=0.0)
    translation_requests = models.IntegerField(default=0)
    
    # Performance metrics
    avg_message_latency = models.FloatField(default=0.0)  # in milliseconds
    connection_success_rate = models.FloatField(default=0.0)  # percentage
    websocket_errors = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['concurrent_users_peak']),
        ]
    
    def __str__(self):
        return f"Real-time analytics for {self.date}"


class AnalyticsEvent(models.Model):
    """Store individual analytics events for detailed tracking"""
    EVENT_TYPES = [
        ('user_login', 'User Login'),
        ('user_logout', 'User Logout'),
        ('page_view', 'Page View'),
        ('match_request', 'Match Request'),
        ('match_acceptance', 'Match Acceptance'),
        ('collaboration_invite', 'Collaboration Invite'),
        ('message_sent', 'Message Sent'),
        ('notification_sent', 'Notification Sent'),
        ('notification_opened', 'Notification Opened'),
        ('api_request', 'API Request'),
        ('error_occurred', 'Error Occurred'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    event_data = models.JSONField(default=dict)
    
    # Request context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=255, blank=True)
    
    # Performance data
    response_time = models.FloatField(null=True, blank=True)  # in seconds
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.event_type} at {self.timestamp}"
