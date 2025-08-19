"""
AI Services Models for Creator Community Platform
Implements REQ-2, REQ-13, REQ-15: AI content validation and generation
"""
from django.db import models
from accounts.models import CreatorProfile, PortfolioItem
import uuid

class ContentValidation(models.Model):
    """
    AI content validation results for portfolio items (REQ-2)
    """
    VALIDATION_STATUS = [
        ('valid', 'Valid'),
        ('invalid', 'Invalid'),
        ('flagged', 'Flagged for Review'),
        ('pending', 'Pending Review'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio_item = models.OneToOneField(PortfolioItem, on_delete=models.CASCADE, related_name='validation', null=True, blank=True)
    is_valid = models.BooleanField(default=True)
    confidence_score = models.FloatField(default=0.0)
    validation_data = models.JSONField(default=dict)
    issues = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=VALIDATION_STATUS, default='pending')
    validated_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'content_validations'
        ordering = ['-validated_at']
        indexes = [
            models.Index(fields=['is_valid', 'confidence_score']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Validation for {self.portfolio_item.title} - {self.status}"

class AIContentGeneration(models.Model):
    """
    AI-generated content requests and results (REQ-13, REQ-15)
    """
    GENERATION_TYPES = [
        ('music', 'Music Generation'),
        ('lyrics', 'Lyrics Generation'),
        ('artwork', 'Artwork Generation'),
        ('story', 'Story Generation'),
        ('concept', 'Concept Development'),
        ('bio', 'Profile Bio'),
        ('description', 'Project Description'),
        ('caption', 'Social Media Caption'),
        ('script', 'Video Script'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='ai_generations')
    generation_type = models.CharField(max_length=20, choices=GENERATION_TYPES)
    prompt = models.TextField(max_length=2000)
    parameters = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result_data = models.JSONField(default=dict, blank=True)
    generated_content = models.TextField(blank=True)
    quality_score = models.FloatField(default=0.0)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'ai_content_generations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['profile', 'generation_type']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.profile.display_name} - {self.generation_type} - {self.status}"

class ProfileFeedback(models.Model):
    """
    Profile feedback system (REQ-16)
    """
    FEEDBACK_TYPES = [
        ('collaboration', 'Collaboration Feedback'),
        ('portfolio', 'Portfolio Feedback'),
        ('communication', 'Communication Feedback'),
        ('professionalism', 'Professionalism'),
    ]
    
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reviewer = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='ai_feedback_given')
    reviewee = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='ai_feedback_received')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(max_length=1000, blank=True)
    is_anonymous = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_profile_feedback'
        unique_together = ['reviewer', 'reviewee', 'feedback_type']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['reviewee', 'rating']),
            models.Index(fields=['feedback_type']),
        ]
    
    def __str__(self):
        return f"Feedback for {self.reviewee.display_name} - {self.rating} stars"
