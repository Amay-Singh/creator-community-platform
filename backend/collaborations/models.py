"""
Collaboration Models for Creator Community Platform
Implements REQ-8, REQ-9, REQ-10: Collaboration invites, matching, and communication
"""
from django.db import models
from accounts.models import CreatorProfile
import uuid

class CollaborationInvite(models.Model):
    """
    Collaboration invites between creators (REQ-8)
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='invites_sent')
    recipient = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='invites_received')
    
    # Collaboration details
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    collaboration_type = models.CharField(max_length=50)  # e.g., 'music_video', 'art_collab'
    
    # AI matching explanation (REQ-6)
    match_explanation = models.TextField(max_length=500, blank=True)
    match_score = models.FloatField(default=0.0)
    
    # Status and metadata
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'collaboration_invites'
        unique_together = ['sender', 'recipient', 'title']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['recipient', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.sender.display_name} to {self.recipient.display_name}"

class Collaboration(models.Model):
    """
    Active collaborations between creators
    """
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invite = models.OneToOneField(CollaborationInvite, on_delete=models.CASCADE, related_name='collaboration')
    participants = models.ManyToManyField(CreatorProfile, related_name='collaborations')
    
    # Project details
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=2000)
    goals = models.TextField(max_length=1000, blank=True)
    
    # Status and timeline
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='planning')
    start_date = models.DateTimeField(auto_now_add=True)
    target_completion = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'collaborations'
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.status})"

class CollaborationFile(models.Model):
    """
    File sharing for collaborations (REQ-12)
    """
    collaboration = models.ForeignKey(Collaboration, on_delete=models.CASCADE, related_name='files')
    uploader = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE)
    
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='collaboration_files/%Y/%m/')
    file_type = models.CharField(max_length=50)
    file_size = models.PositiveIntegerField()
    
    description = models.TextField(max_length=500, blank=True)
    version = models.PositiveSmallIntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'collaboration_files'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.collaboration.title}"

class CollaborationTask(models.Model):
    """
    Task management for collaborations (REQ-12)
    """
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'Under Review'),
        ('completed', 'Completed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    collaboration = models.ForeignKey(Collaboration, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='assigned_tasks')
    created_by = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='created_tasks')
    
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'collaboration_tasks'
        indexes = [
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['collaboration', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.assigned_to.display_name}"

class AICollaborationSuggestion(models.Model):
    """
    AI-generated collaboration suggestions (REQ-6, REQ-7)
    """
    SUGGESTION_TYPES = [
        ('portfolio_match', 'Portfolio Match'),
        ('skill_complement', 'Skill Complement'),
        ('style_similarity', 'Style Similarity'),
        ('location_based', 'Location Based'),
    ]
    
    profile = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='ai_suggestions')
    suggested_profile = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='suggested_for')
    
    suggestion_type = models.CharField(max_length=20, choices=SUGGESTION_TYPES)
    match_score = models.FloatField()
    explanation = models.TextField(max_length=500)
    
    # Suggested collaboration details
    suggested_project_type = models.CharField(max_length=100)
    suggested_title = models.CharField(max_length=200)
    suggested_description = models.TextField(max_length=1000)
    
    # Interaction tracking
    is_viewed = models.BooleanField(default=False)
    is_acted_upon = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'ai_collaboration_suggestions'
        unique_together = ['profile', 'suggested_profile']
        indexes = [
            models.Index(fields=['profile', 'match_score']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Suggest {self.suggested_profile.display_name} to {self.profile.display_name}"
