"""
Chat Models for Creator Community Platform
Implements REQ-9, REQ-11, REQ-20: Individual/group chat with translation
"""
from django.db import models
from accounts.models import CreatorProfile
from collaborations.models import Collaboration
import uuid

class ChatRoom(models.Model):
    """
    Chat rooms for direct and group conversations (REQ-9)
    """
    ROOM_TYPES = [
        ('direct', 'Direct Message'),
        ('group', 'Group Chat'),
        ('collaboration', 'Collaboration Chat'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_type = models.CharField(max_length=15, choices=ROOM_TYPES)
    name = models.CharField(max_length=100, blank=True)  # For group chats
    
    participants = models.ManyToManyField(CreatorProfile, related_name='chat_rooms')
    collaboration = models.ForeignKey(Collaboration, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_rooms')
    
    # Room settings
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(CreatorProfile, on_delete=models.SET_NULL, null=True, related_name='created_rooms')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'chat_rooms'
        indexes = [
            models.Index(fields=['room_type', 'is_active']),
            models.Index(fields=['last_message_at']),
        ]
    
    def __str__(self):
        if self.room_type == 'direct':
            participants = list(self.participants.all()[:2])
            return f"DM: {participants[0].display_name} & {participants[1].display_name}"
        return self.name or f"{self.room_type.title()} Chat"

class ChatMessage(models.Model):
    """
    Individual chat messages with translation support (REQ-11)
    """
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='sent_messages')
    
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    content = models.TextField(max_length=2000)
    
    # File attachments
    file = models.FileField(upload_to='chat_files/%Y/%m/', null=True, blank=True)
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveIntegerField(default=0)
    
    # Translation support (REQ-11)
    original_language = models.CharField(max_length=10, default='en')
    translations = models.JSONField(default=dict, blank=True)  # {language_code: translated_text}
    
    # Message status
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['room', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.sender.display_name}: {self.content[:50]}..."

class MessageReadStatus(models.Model):
    """
    Track message read status for participants
    """
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='read_status')
    reader = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='message_reads')
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'message_read_status'
        unique_together = ['message', 'reader']
        indexes = [
            models.Index(fields=['reader', 'read_at']),
        ]

class MeetingInvite(models.Model):
    """
    Meeting invites for video calls (REQ-10)
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    MEETING_TYPES = [
        ('video_call', 'Video Call'),
        ('audio_call', 'Audio Call'),
        ('screen_share', 'Screen Share'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='meeting_invites')
    organizer = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='organized_meetings')
    
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, blank=True)
    meeting_type = models.CharField(max_length=15, choices=MEETING_TYPES, default='video_call')
    
    # Meeting details
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    meeting_url = models.URLField(blank=True)  # Zoom/Teams URL
    meeting_id = models.CharField(max_length=100, blank=True)
    passcode = models.CharField(max_length=50, blank=True)
    
    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'meeting_invites'
        indexes = [
            models.Index(fields=['scheduled_at', 'status']),
            models.Index(fields=['organizer', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.scheduled_at}"

class MeetingResponse(models.Model):
    """
    Responses to meeting invites
    """
    RESPONSE_CHOICES = [
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('tentative', 'Tentative'),
    ]
    
    meeting = models.ForeignKey(MeetingInvite, on_delete=models.CASCADE, related_name='responses')
    participant = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='meeting_responses')
    response = models.CharField(max_length=10, choices=RESPONSE_CHOICES)
    notes = models.TextField(max_length=500, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'meeting_responses'
        unique_together = ['meeting', 'participant']
