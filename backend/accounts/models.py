"""
User Account Models for Creator Community Platform
Implements REQ-1, REQ-3, REQ-4: User profiles with authentication and health metrics
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
import uuid

class CustomUser(AbstractUser):
    """Extended user model with creator-specific fields"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class CreatorProfile(models.Model):
    """
    Creator profile model implementing REQ-1: Valid profiles with portfolios
    REQ-4: Profile health metrics
    """
    ARTIST_CATEGORIES = [
        ('visual_arts', 'Visual Arts'),
        ('performing_arts', 'Performing Arts'),
        ('literary_arts', 'Literary Arts'),
        ('design', 'Design'),
        ('digital_arts', 'Digital Arts'),
        ('crafts', 'Crafts'),
        ('media_arts', 'Media Arts'),
        ('culinary_arts', 'Culinary Arts'),
        ('architecture', 'Architecture'),
        ('other', 'Other'),
    ]
    
    EXPERIENCE_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('professional', 'Professional'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=100)
    bio = models.TextField(max_length=500, blank=True)
    category = models.CharField(max_length=20, choices=ARTIST_CATEGORIES)
    subcategory = models.CharField(max_length=100, blank=True)
    experience_level = models.CharField(max_length=15, choices=EXPERIENCE_LEVELS)
    location = models.CharField(max_length=100, blank=True)
    
    # External platform links (REQ-1)
    instagram_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    spotify_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    
    # Profile validation (REQ-2, REQ-3)
    is_validated = models.BooleanField(default=False)
    validation_score = models.FloatField(default=0.0)
    
    # Profile health metrics (REQ-4)
    health_score = models.FloatField(default=0.0)
    activity_score = models.FloatField(default=0.0)
    connection_score = models.FloatField(default=0.0)
    feedback_score = models.FloatField(default=0.0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'creator_profiles'
        verbose_name = 'Creator Profile'
        verbose_name_plural = 'Creator Profiles'
        indexes = [
            models.Index(fields=['category', 'experience_level']),
            models.Index(fields=['location']),
            models.Index(fields=['health_score']),
        ]
    
    def __str__(self):
        return f"{self.display_name} ({self.category})"
    
    def calculate_health_score(self):
        """Calculate profile health score based on completeness and activity"""
        completeness = 0
        if self.bio: completeness += 20
        if self.location: completeness += 15
        if self.instagram_url or self.youtube_url or self.spotify_url or self.website_url: completeness += 25
        if self.portfolio_items.exists(): completeness += 40
        
        self.health_score = (completeness + self.activity_score + self.connection_score + self.feedback_score) / 4
        self.save(update_fields=['health_score'])
        return self.health_score

class PortfolioItem(models.Model):
    """
    Portfolio items for creator profiles (REQ-1)
    Supports multimedia content with AI validation
    """
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
    ]
    
    profile = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='portfolio_items')
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, blank=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    file = models.FileField(upload_to='portfolio/%Y/%m/')
    thumbnail = models.ImageField(upload_to='thumbnails/%Y/%m/', blank=True, null=True)
    
    # AI validation fields (REQ-2)
    is_validated = models.BooleanField(default=False)
    validation_score = models.FloatField(default=0.0)
    is_original = models.BooleanField(default=True)
    
    # Metadata
    file_size = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'portfolio_items'
        verbose_name = 'Portfolio Item'
        verbose_name_plural = 'Portfolio Items'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.profile.display_name})"

class ProfileFeedback(models.Model):
    """
    Profile feedback system (REQ-16)
    """
    FEEDBACK_TYPES = [
        ('positive', 'Positive'),
        ('constructive', 'Constructive'),
        ('report', 'Report'),
    ]
    
    profile = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='feedback_received')
    reviewer = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='feedback_given')
    feedback_type = models.CharField(max_length=15, choices=FEEDBACK_TYPES)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(max_length=500, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'profile_feedback'
        unique_together = ['profile', 'reviewer']
        verbose_name = 'Profile Feedback'
        verbose_name_plural = 'Profile Feedback'
    
    def __str__(self):
        return f"Feedback for {self.profile.display_name} by {self.reviewer.display_name}"
