"""
Analytics serializers
"""
from rest_framework import serializers
from .models import (
    UserEngagementMetric, PlatformMetric, MatchingAnalytics,
    NotificationAnalytics, RealtimeAnalytics, AnalyticsEvent
)


class UserEngagementMetricSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserEngagementMetric
        fields = [
            'id', 'username', 'date', 'sessions_count', 'total_session_duration',
            'avg_session_duration', 'pages_viewed', 'actions_performed',
            'notifications_clicked', 'matches_viewed', 'collaborations_initiated',
            'messages_sent', 'created_at', 'updated_at'
        ]


class PlatformMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformMetric
        fields = [
            'id', 'date', 'total_users', 'active_users_daily', 'active_users_weekly',
            'active_users_monthly', 'new_registrations', 'total_sessions',
            'avg_session_duration', 'total_page_views', 'total_matches_generated',
            'successful_matches', 'collaboration_invites_sent',
            'collaboration_invites_accepted', 'messages_exchanged',
            'avg_api_response_time', 'error_rate', 'cache_hit_rate',
            'created_at', 'updated_at'
        ]


class MatchingAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchingAnalytics
        fields = [
            'id', 'date', 'total_match_requests', 'successful_matches',
            'match_acceptance_rate', 'avg_match_score', 'avg_matching_time',
            'cache_hit_rate', 'user_feedback_positive', 'user_feedback_negative',
            'matches_leading_to_collaboration', 'created_at', 'updated_at'
        ]


class NotificationAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationAnalytics
        fields = [
            'id', 'date', 'total_notifications_sent', 'push_notifications_sent',
            'email_notifications_sent', 'notifications_opened', 'notifications_clicked',
            'open_rate', 'click_rate', 'avg_delivery_time', 'delivery_failure_rate',
            'users_opted_out', 'users_opted_in', 'created_at', 'updated_at'
        ]


class RealtimeAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealtimeAnalytics
        fields = [
            'id', 'date', 'total_realtime_sessions', 'avg_session_duration',
            'concurrent_users_peak', 'total_messages_sent', 'avg_messages_per_session',
            'translation_requests', 'avg_message_latency', 'connection_success_rate',
            'websocket_errors', 'created_at', 'updated_at'
        ]


class AnalyticsEventSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AnalyticsEvent
        fields = [
            'id', 'username', 'event_type', 'event_data', 'ip_address',
            'user_agent', 'session_id', 'response_time', 'timestamp'
        ]


class AnalyticsDashboardSerializer(serializers.Serializer):
    """Serializer for dashboard overview data"""
    platform_overview = serializers.DictField()
    matching_performance = serializers.DictField()
    notification_performance = serializers.DictField()
    recent_events = AnalyticsEventSerializer(many=True)


class DateRangeSerializer(serializers.Serializer):
    """Serializer for date range queries"""
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    
    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Start date must be before end date")
        return data
