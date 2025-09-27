import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('user_signed_in', 'User Signed In'),
        ('profile_updated', 'Profile Updated'),
        ('message_received', 'Message Received'),
        ('profile_followed', 'Profile Followed'),
        ('collaboration_invite', 'Collaboration Invite'),
        ('system_announcement', 'System Announcement'),
        # AI Matching notification types
        ('match_found', 'New Match Found'),
        ('match_accepted', 'Match Accepted'),
        ('match_declined', 'Match Declined'),
        ('match_feedback_received', 'Match Feedback Received'),
        ('match_expired', 'Match Expired'),
        ('matching_preferences_updated', 'Matching Preferences Updated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    payload = models.JSONField(default=dict)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'notifications'
        indexes = [
            models.Index(fields=['user', 'read_at']),
            models.Index(fields=['user', '-created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.type} - {self.created_at}"
    
    @property
    def is_read(self):
        return self.read_at is not None
    
    def mark_as_read(self):
        if not self.is_read:
            self.read_at = timezone.now()
            self.save(update_fields=['read_at'])


class ActivityFeed(models.Model):
    ACTIVITY_TYPES = [
        ('profile_created', 'Profile Created'),
        ('profile_updated', 'Profile Updated'),
        ('message_sent', 'Message Sent'),
        ('collaboration_joined', 'Collaboration Joined'),
        ('content_generated', 'Content Generated'),
        ('profile_followed', 'Profile Followed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_feed')
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='actor_activities')
    action_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    target_type = models.CharField(max_length=50, null=True, blank=True)
    target_id = models.UUIDField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'activity_feed'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['actor', '-created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        actor_name = self.actor.username if self.actor else 'System'
        return f"{actor_name} - {self.action_type} - {self.created_at}"


class NotificationSubscription(models.Model):
    """
    Model to track user notification preferences and WebSocket connections
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_subscription')
    is_active = models.BooleanField(default=True)
    websocket_connected = models.BooleanField(default=False)
    connection_count = models.PositiveIntegerField(default=0)
    last_connected_at = models.DateTimeField(auto_now=True)
    preferences = models.JSONField(default=dict, help_text="User notification preferences")
    push_subscription = models.JSONField(null=True, blank=True, help_text="Web push subscription data")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_subscriptions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['websocket_connected']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - Active: {self.is_active} - Connected: {self.websocket_connected}"
    
    def get_preference(self, key, default=True):
        """Get specific notification preference"""
        return self.preferences.get(key, default)
    
    def set_preference(self, key, value):
        """Set specific notification preference"""
        self.preferences[key] = value
        self.save(update_fields=['preferences'])
    
    @property
    def default_preferences(self):
        """Default notification preferences for new users"""
        return {
            'match_found': True,
            'match_accepted': True,
            'match_declined': False,
            'match_feedback_received': True,
            'match_expired': True,
            'collaboration_invite': True,
            'message_received': True,
            'profile_followed': True,
            'system_announcement': True,
            'email_notifications': True,
            'push_notifications': True,
            'sound_enabled': True,
        }


class MatchNotification(models.Model):
    """
    Specialized notification model for AI matching events
    """
    MATCH_NOTIFICATION_TYPES = [
        ('new_match', 'New Match Found'),
        ('match_viewed', 'Match Viewed'),
        ('match_accepted', 'Match Accepted'),
        ('match_declined', 'Match Declined'),
        ('feedback_received', 'Feedback Received'),
        ('match_expired', 'Match Expired'),
        ('rematch_suggested', 'Rematch Suggested'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='match_notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_match_notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=30, choices=MATCH_NOTIFICATION_TYPES)
    match_id = models.UUIDField(help_text="ID of the related match")
    title = models.CharField(max_length=200)
    message = models.TextField()
    metadata = models.JSONField(default=dict, help_text="Additional notification data")
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'match_notifications'
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['match_id']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient.username} - {self.notification_type} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def mark_as_delivered(self):
        """Mark notification as delivered"""
        if not self.delivered_at:
            self.delivered_at = timezone.now()
            self.save(update_fields=['delivered_at'])
