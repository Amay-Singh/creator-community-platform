from rest_framework import serializers
from .models import Notification, ActivityFeed


class NotificationSerializer(serializers.ModelSerializer):
    is_read = serializers.ReadOnlyField()
    
    class Meta:
        model = Notification
        fields = ['id', 'type', 'payload', 'is_read', 'read_at', 'created_at']
        read_only_fields = ['id', 'created_at']


class ActivityFeedSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.username', read_only=True)
    actor_avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = ActivityFeed
        fields = ['id', 'actor_name', 'actor_avatar', 'action_type', 'target_type', 'target_id', 'metadata', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_actor_avatar(self, obj):
        if obj.actor and hasattr(obj.actor, 'profile'):
            return obj.actor.profile.avatar_url if obj.actor.profile.avatar_url else None
        return None


class MarkNotificationsReadSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text="List of notification IDs to mark as read"
    )
    all = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Mark all notifications as read"
    )
    
    def validate(self, data):
        if not data.get('ids') and not data.get('all'):
            raise serializers.ValidationError("Either 'ids' or 'all' must be provided")
        return data
