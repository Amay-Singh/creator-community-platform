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
