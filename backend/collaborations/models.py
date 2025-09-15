"""
Collaboration Models for Creator Community Platform
Implements REQ-8, REQ-9, REQ-10: Collaboration invites, matching, and communication
Includes P5-003 New Collaboration Invitation System models
"""
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
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
    assigned_to = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='assigned_collaboration_tasks')
    created_by = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='created_collaboration_tasks')
    
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


# P5-003 New Collaboration Invitation System Models

class Project(models.Model):
    """
    Enhanced Project model for collaboration management with Kanban support
    Implements P5-005: Project Management Tools
    """
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    owner = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='owned_projects')
    # collaborators = models.ManyToManyField(CreatorProfile, through='ProjectMembership', related_name='collaborative_projects')
    
    # Project management fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    progress_percentage = models.PositiveIntegerField(default=0)
    
    # Timeline and budget
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    estimated_hours = models.PositiveIntegerField(null=True, blank=True)
    actual_hours = models.PositiveIntegerField(default=0)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Project settings
    is_public = models.BooleanField(default=False)
    allow_file_sharing = models.BooleanField(default=True)
    enable_time_tracking = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'projects'
        ordering = ['-last_activity_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['last_activity_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.status})"
    
    @property
    def total_tasks(self):
        return self.tasks.count()
    
    @property
    def completed_tasks(self):
        return self.tasks.filter(status='done').count()
    
    def update_progress(self):
        """Update project progress based on completed tasks"""
        if self.total_tasks > 0:
            self.progress_percentage = int((self.completed_tasks / self.total_tasks) * 100)
            self.save(update_fields=['progress_percentage'])


class ProjectMembership(models.Model):
    """
    Project membership with roles and permissions
    """
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='memberships')
    member = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='project_memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    
    # Permissions
    can_edit_project = models.BooleanField(default=False)
    can_manage_tasks = models.BooleanField(default=True)
    can_upload_files = models.BooleanField(default=True)
    can_invite_members = models.BooleanField(default=False)
    
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'project_memberships'
        unique_together = ['project', 'member']
        indexes = [
            models.Index(fields=['project', 'role']),
        ]
    
    def __str__(self):
        return f"{self.member.display_name} - {self.project.title} ({self.role})"


class Task(models.Model):
    """
    Kanban task model for project management
    """
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('done', 'Done'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Task management
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    assignee = models.ForeignKey(CreatorProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    created_by = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='created_tasks')
    
    # Timeline and effort
    due_date = models.DateTimeField(null=True, blank=True)
    estimated_hours = models.PositiveIntegerField(null=True, blank=True)
    actual_hours = models.PositiveIntegerField(default=0)
    
    # Kanban board positioning
    board_order = models.PositiveIntegerField(default=0)
    
    # Dependencies
    depends_on = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='blocking_tasks')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'tasks'
        ordering = ['board_order', '-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['assignee', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['board_order']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Update completed_at when task is marked as done
        if self.status == 'done' and not self.completed_at:
            from django.utils import timezone
            self.completed_at = timezone.now()
        elif self.status != 'done':
            self.completed_at = None
        
        super().save(*args, **kwargs)
        
        # Update project progress
        self.project.update_progress()


class TaskComment(models.Model):
    """
    Comments on tasks for collaboration
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='task_comments')
    content = models.TextField(max_length=1000)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'task_comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment on {self.task.title} by {self.author.display_name}"


class ProjectFile(models.Model):
    """
    File sharing and storage for projects
    """
    FILE_TYPE_CHOICES = [
        ('document', 'Document'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('archive', 'Archive'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='files')
    
    # File details
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='project_files/%Y/%m/')
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, default='other')
    file_size = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=100)
    
    # Version control
    version = models.PositiveIntegerField(default=1)
    previous_version = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='newer_versions')
    
    # Access control
    uploaded_by = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='uploaded_files')
    is_public = models.BooleanField(default=False)
    download_count = models.PositiveIntegerField(default=0)
    
    # Security
    virus_scan_status = models.CharField(max_length=20, default='pending')  # pending, clean, infected
    virus_scan_result = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'project_files'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'file_type']),
            models.Index(fields=['uploaded_by', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} (v{self.version})"
    
    @property
    def file_size_mb(self):
        return round(self.file_size / (1024 * 1024), 2)


class ProjectMilestone(models.Model):
    """
    Project milestones for tracking progress
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateTimeField()
    completion_percentage = models.PositiveIntegerField(default=0)
    
    created_by = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='created_milestones')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'project_milestones'
        ordering = ['due_date']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.project.title} - {self.title}"
