"""
Video Collaboration Models
P9-003: Advanced Video Collaboration Tools
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class VideoRoom(models.Model):
    """Video conference room model"""
    
    ROOM_TYPES = [
        ('collaboration', 'Collaboration Session'),
        ('interview', 'Interview'),
        ('presentation', 'Presentation'),
        ('brainstorming', 'Brainstorming'),
        ('review', 'Review Session'),
    ]
    
    ROOM_STATUS = [
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='collaboration')
    status = models.CharField(max_length=20, choices=ROOM_STATUS, default='scheduled')
    
    # Room settings
    max_participants = models.IntegerField(default=10)
    is_recording_enabled = models.BooleanField(default=True)
    is_screen_sharing_enabled = models.BooleanField(default=True)
    is_chat_enabled = models.BooleanField(default=True)
    is_whiteboard_enabled = models.BooleanField(default=True)
    require_approval = models.BooleanField(default=False)
    
    # Ownership and access
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_rooms')
    participants = models.ManyToManyField(User, through='RoomParticipant', related_name='joined_rooms')
    
    # Scheduling
    scheduled_start = models.DateTimeField(null=True, blank=True)
    scheduled_end = models.DateTimeField(null=True, blank=True)
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # WebRTC signaling server info
    signaling_server = models.CharField(max_length=200, blank=True)
    room_token = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'video_rooms'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.room_type})"
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def duration_minutes(self):
        if self.actual_start and self.actual_end:
            return int((self.actual_end - self.actual_start).total_seconds() / 60)
        return 0


class RoomParticipant(models.Model):
    """Participant in a video room"""
    
    PARTICIPANT_ROLES = [
        ('host', 'Host'),
        ('co_host', 'Co-Host'),
        ('participant', 'Participant'),
        ('observer', 'Observer'),
    ]
    
    PARTICIPANT_STATUS = [
        ('invited', 'Invited'),
        ('joined', 'Joined'),
        ('left', 'Left'),
        ('kicked', 'Kicked'),
    ]
    
    room = models.ForeignKey(VideoRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=PARTICIPANT_ROLES, default='participant')
    status = models.CharField(max_length=20, choices=PARTICIPANT_STATUS, default='invited')
    
    # Permissions
    can_share_screen = models.BooleanField(default=True)
    can_record = models.BooleanField(default=False)
    can_mute_others = models.BooleanField(default=False)
    can_manage_participants = models.BooleanField(default=False)
    
    # Session info
    joined_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)
    connection_quality = models.CharField(max_length=20, blank=True)  # good, fair, poor
    
    # WebRTC peer info
    peer_id = models.CharField(max_length=100, blank=True)
    ice_servers = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'room_participants'
        unique_together = ['room', 'user']
    
    def __str__(self):
        return f"{self.user.username} in {self.room.name} ({self.role})"


class VideoRecording(models.Model):
    """Video recording of a session"""
    
    RECORDING_STATUS = [
        ('recording', 'Recording'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    RECORDING_QUALITY = [
        ('720p', '720p HD'),
        ('1080p', '1080p Full HD'),
        ('480p', '480p SD'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(VideoRoom, on_delete=models.CASCADE, related_name='recordings')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Recording details
    status = models.CharField(max_length=20, choices=RECORDING_STATUS, default='recording')
    quality = models.CharField(max_length=10, choices=RECORDING_QUALITY, default='720p')
    duration_seconds = models.IntegerField(default=0)
    file_size_mb = models.FloatField(default=0)
    
    # File storage
    video_file_url = models.URLField(blank=True)
    audio_file_url = models.URLField(blank=True)
    transcript_file_url = models.URLField(blank=True)
    thumbnail_url = models.URLField(blank=True)
    
    # Access control
    is_public = models.BooleanField(default=False)
    allowed_viewers = models.ManyToManyField(User, blank=True, related_name='accessible_recordings')
    
    # Metadata
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_recordings')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Processing info
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    processing_error = models.TextField(blank=True)
    
    class Meta:
        db_table = 'video_recordings'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Recording: {self.title}"
    
    @property
    def duration_formatted(self):
        """Return duration in HH:MM:SS format"""
        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        seconds = self.duration_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class ScreenShare(models.Model):
    """Screen sharing session within a video room"""
    
    SHARE_STATUS = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('ended', 'Ended'),
    ]
    
    room = models.ForeignKey(VideoRoom, on_delete=models.CASCADE, related_name='screen_shares')
    presenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='screen_shares')
    title = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=SHARE_STATUS, default='active')
    
    # Screen share details
    screen_type = models.CharField(max_length=50, blank=True)  # desktop, window, tab
    resolution = models.CharField(max_length=20, blank=True)  # 1920x1080
    frame_rate = models.IntegerField(default=30)
    
    # Session timing
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Recording of screen share
    is_recorded = models.BooleanField(default=False)
    recording_url = models.URLField(blank=True)
    
    class Meta:
        db_table = 'screen_shares'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Screen share by {self.presenter.username} in {self.room.name}"


class Whiteboard(models.Model):
    """Collaborative whiteboard for video sessions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.OneToOneField(VideoRoom, on_delete=models.CASCADE, related_name='whiteboard')
    title = models.CharField(max_length=200, default='Collaboration Whiteboard')
    
    # Whiteboard data (stored as JSON)
    canvas_data = models.JSONField(default=dict, blank=True)
    canvas_width = models.IntegerField(default=1920)
    canvas_height = models.IntegerField(default=1080)
    
    # Access control
    is_locked = models.BooleanField(default=False)
    allowed_editors = models.ManyToManyField(User, blank=True, related_name='editable_whiteboards')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Export options
    export_url = models.URLField(blank=True)
    export_format = models.CharField(max_length=10, blank=True)  # png, pdf, svg
    
    class Meta:
        db_table = 'whiteboards'
    
    def __str__(self):
        return f"Whiteboard for {self.room.name}"


class VideoMessage(models.Model):
    """Chat messages during video sessions"""
    
    MESSAGE_TYPES = [
        ('text', 'Text Message'),
        ('file', 'File Share'),
        ('link', 'Link Share'),
        ('system', 'System Message'),
    ]
    
    room = models.ForeignKey(VideoRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    
    # Message content
    content = models.TextField()
    file_url = models.URLField(blank=True)
    file_name = models.CharField(max_length=200, blank=True)
    file_size = models.IntegerField(default=0)
    
    # Message metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='private_video_messages')
    
    # Message reactions
    reactions = models.JSONField(default=dict, blank=True)  # {emoji: [user_ids]}
    
    class Meta:
        db_table = 'video_messages'
        ordering = ['timestamp']
    
    def __str__(self):
        return f"Message from {self.sender.username} in {self.room.name}"


class ConnectionLog(models.Model):
    """Log of connection events for debugging and analytics"""
    
    EVENT_TYPES = [
        ('join', 'User Joined'),
        ('leave', 'User Left'),
        ('connection_failed', 'Connection Failed'),
        ('reconnect', 'Reconnection'),
        ('quality_change', 'Quality Change'),
        ('error', 'Error'),
    ]
    
    room = models.ForeignKey(VideoRoom, on_delete=models.CASCADE, related_name='connection_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_connection_logs')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    
    # Event details
    details = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    connection_quality = models.CharField(max_length=20, blank=True)
    
    # Network info
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    bandwidth_kbps = models.IntegerField(null=True, blank=True)
    latency_ms = models.IntegerField(null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'video_connection_logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.event_type} - {self.user.username} in {self.room.name}"
