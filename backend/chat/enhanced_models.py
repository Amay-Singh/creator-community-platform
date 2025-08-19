"""
Enhanced Chat Models with Real-time Translation and Meeting Features
Implements REQ-9, REQ-10, REQ-11: Chat functionality, meeting invites, real-time translation
"""
from django.db import models
from accounts.models import CreatorProfile
import uuid

class ChatRoom(models.Model):
    """
    Chat room for individual and group conversations (REQ-9)
    """
    ROOM_TYPES = [
        ('individual', 'Individual Chat'),
        ('group', 'Group Chat'),
        ('collaboration', 'Collaboration Chat'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True)
    room_type = models.CharField(max_length=15, choices=ROOM_TYPES, default='individual')
    participants = models.ManyToManyField(CreatorProfile, related_name='chat_rooms')
    created_by = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='created_rooms')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_rooms'
        ordering = ['-updated_at']
    
    def __str__(self):
        if self.name:
            return self.name
        participants = list(self.participants.all()[:3])
        names = [p.display_name for p in participants]
        if len(participants) > 2:
            return f"{', '.join(names[:2])} and {len(participants)-2} others"
        return ', '.join(names)

class Message(models.Model):
    """
    Enhanced message model with translation support (REQ-11)
    """
    MESSAGE_TYPES = [
        ('text', 'Text Message'),
        ('image', 'Image'),
        ('file', 'File'),
        ('audio', 'Audio'),
        ('meeting_invite', 'Meeting Invite'),
        ('collaboration_request', 'Collaboration Request'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='sent_messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    content = models.TextField()
    file_attachment = models.FileField(upload_to='chat_files/', null=True, blank=True)
    
    # Translation fields (REQ-11)
    original_language = models.CharField(max_length=10, default='en')
    translations = models.JSONField(default=dict, blank=True)
    is_translated = models.BooleanField(default=False)
    
    # Message metadata
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['room', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.sender.display_name}: {self.content[:50]}..."

class MeetingInvite(models.Model):
    """
    Meeting invite system (REQ-10)
    """
    MEETING_TYPES = [
        ('video_call', 'Video Call'),
        ('audio_call', 'Audio Call'),
        ('in_person', 'In-Person Meeting'),
        ('collaboration_session', 'Collaboration Session'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organizer = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='organized_meetings')
    participants = models.ManyToManyField(CreatorProfile, through='MeetingParticipant', related_name='meeting_invites')
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='meeting_invites', null=True, blank=True)
    
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, blank=True)
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPES)
    
    scheduled_at = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    location = models.CharField(max_length=500, blank=True)  # URL for virtual meetings or address for in-person
    
    # Meeting platform details
    meeting_url = models.URLField(blank=True)
    meeting_id = models.CharField(max_length=100, blank=True)
    meeting_password = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'meeting_invites'
        ordering = ['scheduled_at']
        indexes = [
            models.Index(fields=['organizer', 'scheduled_at']),
            models.Index(fields=['scheduled_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.scheduled_at.strftime('%Y-%m-%d %H:%M')}"

class MeetingParticipant(models.Model):
    """
    Meeting participant with response status
    """
    meeting = models.ForeignKey(MeetingInvite, on_delete=models.CASCADE)
    participant = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=MeetingInvite.STATUS_CHOICES, default='pending')
    responded_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(max_length=500, blank=True)
    
    class Meta:
        db_table = 'meeting_participants'
        unique_together = ['meeting', 'participant']
    
    def __str__(self):
        return f"{self.participant.display_name} - {self.meeting.title} ({self.status})"

class TranslationRequest(models.Model):
    """
    Translation request tracking (REQ-11)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='translation_requests')
    requester = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='translation_requests')
    target_language = models.CharField(max_length=10)
    translated_content = models.TextField()
    confidence_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'translation_requests'
        unique_together = ['message', 'target_language']
    
    def __str__(self):
        return f"Translation to {self.target_language} for message {self.message.id}"

class ChatRoomSettings(models.Model):
    """
    Chat room settings and preferences
    """
    room = models.OneToOneField(ChatRoom, on_delete=models.CASCADE, related_name='settings')
    auto_translate = models.BooleanField(default=False)
    default_language = models.CharField(max_length=10, default='en')
    allow_file_sharing = models.BooleanField(default=True)
    allow_meeting_invites = models.BooleanField(default=True)
    message_retention_days = models.IntegerField(default=365)
    
    class Meta:
        db_table = 'chat_room_settings'
    
    def __str__(self):
        return f"Settings for {self.room}"
