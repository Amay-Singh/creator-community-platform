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


# P5-006 AI Content Generation Assistant Models

class ContentGenerationRequest(models.Model):
    """
    AI content generation requests with prompt and parameters
    """
    CONTENT_TYPES = [
        ('social_media_post', 'Social Media Post'),
        ('video_script', 'Video Script'),
        ('blog_post', 'Blog Post'),
        ('marketing_copy', 'Marketing Copy'),
        ('creative_writing', 'Creative Writing'),
        ('product_description', 'Product Description'),
        ('email_campaign', 'Email Campaign'),
        ('press_release', 'Press Release'),
    ]
    
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
        ('youtube', 'YouTube'),
        ('twitter', 'Twitter'),
        ('linkedin', 'LinkedIn'),
        ('facebook', 'Facebook'),
        ('general', 'General'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='content_requests')
    content_type = models.CharField(max_length=30, choices=CONTENT_TYPES)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='general')
    
    # Content parameters
    prompt = models.TextField(max_length=2000)
    topic = models.CharField(max_length=200)
    target_audience = models.CharField(max_length=200, blank=True)
    tone = models.CharField(max_length=50, blank=True)
    word_count = models.PositiveIntegerField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    # AI parameters
    temperature = models.FloatField(default=0.7)
    max_tokens = models.PositiveIntegerField(default=1000)
    custom_parameters = models.JSONField(default=dict, blank=True)
    
    # Status and results
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tokens_used = models.PositiveIntegerField(default=0)
    cost_estimate = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'content_generation_requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['content_type', 'platform']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.display_name} - {self.content_type} - {self.status}"


class GeneratedContent(models.Model):
    """
    AI-generated content with versioning and feedback
    """
    QUALITY_RATINGS = [
        (1, 'Poor'),
        (2, 'Fair'),
        (3, 'Good'),
        (4, 'Very Good'),
        (5, 'Excellent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(ContentGenerationRequest, on_delete=models.CASCADE, related_name='generated_content')
    
    # Content data
    content = models.TextField()
    title = models.CharField(max_length=200, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Versioning
    version = models.PositiveIntegerField(default=1)
    parent_version = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_versions')
    
    # Quality and feedback
    quality_score = models.FloatField(default=0.0)
    user_rating = models.IntegerField(choices=QUALITY_RATINGS, null=True, blank=True)
    user_feedback = models.TextField(max_length=1000, blank=True)
    
    # Usage tracking
    is_published = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'generated_content'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['request', 'version']),
            models.Index(fields=['user_rating', 'quality_score']),
            models.Index(fields=['is_published', 'is_favorite']),
        ]
    
    def __str__(self):
        return f"{self.request.content_type} v{self.version} - {self.title[:50]}"


class ContentTemplate(models.Model):
    """
    Reusable content generation templates
    """
    TEMPLATE_TYPES = [
        ('prompt', 'Prompt Template'),
        ('structure', 'Content Structure'),
        ('style', 'Style Guide'),
        ('format', 'Format Template'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='content_templates')
    
    # Template details
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=500, blank=True)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    content_type = models.CharField(max_length=30, choices=ContentGenerationRequest.CONTENT_TYPES)
    
    # Template content
    prompt_template = models.TextField()
    default_parameters = models.JSONField(default=dict, blank=True)
    example_output = models.TextField(blank=True)
    
    # Sharing and usage
    is_public = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    usage_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'content_templates'
        ordering = ['-usage_count', '-created_at']
        indexes = [
            models.Index(fields=['creator', 'template_type']),
            models.Index(fields=['content_type', 'is_public']),
            models.Index(fields=['is_featured', 'usage_count']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.content_type}"


class ContentCategory(models.Model):
    """
    Content categorization for organization
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=300, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    
    # Display settings
    color = models.CharField(max_length=7, default='#007bff')  # Hex color
    icon = models.CharField(max_length=50, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'content_categories'
        verbose_name_plural = 'Content Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class UserUsageTracking(models.Model):
    """
    Track user AI content generation usage for rate limiting
    """
    USAGE_TYPES = [
        ('content_generation', 'Content Generation'),
        ('template_usage', 'Template Usage'),
        ('api_call', 'API Call'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='usage_tracking')
    usage_type = models.CharField(max_length=30, choices=USAGE_TYPES)
    
    # Usage metrics
    tokens_consumed = models.PositiveIntegerField(default=0)
    cost_incurred = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    
    # Rate limiting
    daily_count = models.PositiveIntegerField(default=0)
    monthly_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_usage_tracking'
        unique_together = ['user', 'usage_type', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['usage_type', 'date']),
        ]
    
    def __str__(self):
        return f"{self.user.display_name} - {self.usage_type} - {self.date}"


# ============================================================================
# P5-001: AI-Powered Creator Matching Models
# ============================================================================

class CreatorEmbedding(models.Model):
    """
    Store vector embeddings for creator profiles to enable AI-powered matching
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator = models.OneToOneField(CreatorProfile, on_delete=models.CASCADE, related_name='embedding')
    
    # Vector embedding data
    embedding_vector = models.JSONField(help_text="Vector representation of creator profile")
    embedding_version = models.CharField(max_length=50, default='v1.0')
    
    # Source data for embedding generation
    skills_hash = models.CharField(max_length=64, help_text="Hash of skills data used")
    bio_hash = models.CharField(max_length=64, help_text="Hash of bio data used")
    interests_hash = models.CharField(max_length=64, help_text="Hash of interests data used")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_profile_update = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'creator_embeddings'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['creator']),
            models.Index(fields=['embedding_version']),
            models.Index(fields=['updated_at']),
        ]
    
    def __str__(self):
        return f"Embedding for {self.creator.display_name}"
    
    @property
    def needs_update(self):
        """Check if embedding needs to be regenerated"""
        if not self.last_profile_update:
            return True
        return self.creator.updated_at > self.last_profile_update


class MatchResult(models.Model):
    """
    Store AI-generated matches between creators
    """
    MATCH_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('viewed', 'Viewed'),
        ('interested', 'Interested'),
        ('contacted', 'Contacted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requester = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='match_requests')
    matched_creator = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='received_matches')
    
    # Matching scores and metadata
    similarity_score = models.FloatField(help_text="Cosine similarity score (0-1)")
    compatibility_score = models.FloatField(help_text="Overall compatibility score (0-100)")
    
    # Match reasoning and explanation
    match_reasons = models.JSONField(default=list, help_text="List of reasons for the match")
    shared_skills = models.JSONField(default=list, help_text="Skills in common")
    complementary_skills = models.JSONField(default=list, help_text="Complementary skills")
    
    # Match context
    match_type = models.CharField(max_length=50, default='general', help_text="Type of match (collaboration, mentorship, etc.)")
    match_filters = models.JSONField(default=dict, help_text="Filters used for matching")
    
    # Status and interaction
    status = models.CharField(max_length=20, choices=MATCH_STATUS_CHOICES, default='pending')
    viewed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'match_results'
        ordering = ['-compatibility_score', '-created_at']
        unique_together = ['requester', 'matched_creator', 'created_at']
        indexes = [
            models.Index(fields=['requester', 'status']),
            models.Index(fields=['matched_creator', 'status']),
            models.Index(fields=['similarity_score']),
            models.Index(fields=['compatibility_score']),
            models.Index(fields=['created_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Match: {self.requester.display_name} → {self.matched_creator.display_name} ({self.compatibility_score}%)"


class MatchFeedback(models.Model):
    """
    User feedback on match quality for algorithm improvement
    """
    FEEDBACK_CHOICES = [
        (1, 'Very Poor'),
        (2, 'Poor'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    
    FEEDBACK_TYPES = [
        ('quality', 'Match Quality'),
        ('relevance', 'Relevance'),
        ('accuracy', 'Accuracy'),
        ('usefulness', 'Usefulness'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match_result = models.ForeignKey(MatchResult, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE)
    
    # Feedback data
    rating = models.PositiveSmallIntegerField(choices=FEEDBACK_CHOICES)
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES, default='quality')
    comment = models.TextField(blank=True, help_text="Optional feedback comment")
    
    # Interaction outcome
    contacted_match = models.BooleanField(default=False)
    collaboration_started = models.BooleanField(default=False)
    would_recommend = models.BooleanField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'match_feedback'
        ordering = ['-created_at']
        unique_together = ['match_result', 'user', 'feedback_type']
        indexes = [
            models.Index(fields=['match_result']),
            models.Index(fields=['user']),
            models.Index(fields=['rating']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Feedback: {self.match_result} - {self.rating}/5"


class MatchHistory(models.Model):
    """
    Track matching requests and history for analytics
    """
    REQUEST_TYPES = [
        ('find_matches', 'Find Matches'),
        ('batch_match', 'Batch Match'),
        ('similar_creators', 'Similar Creators'),
        ('collaboration_match', 'Collaboration Match'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='match_history')
    
    # Request details
    request_type = models.CharField(max_length=30, choices=REQUEST_TYPES)
    filters_used = models.JSONField(default=dict, help_text="Filters applied to the search")
    results_count = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    processing_time_ms = models.PositiveIntegerField(help_text="Processing time in milliseconds")
    embedding_version = models.CharField(max_length=50, default='v1.0')
    
    # Results summary
    top_similarity_score = models.FloatField(null=True, blank=True)
    average_compatibility = models.FloatField(null=True, blank=True)
    matches_viewed = models.PositiveIntegerField(default=0)
    matches_contacted = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'match_history'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['request_type']),
            models.Index(fields=['processing_time_ms']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Match History: {self.user.display_name} - {self.request_type} ({self.results_count} results)"
