"""
Personality Quiz and Matching Models for Creator Community Platform
Implements REQ-6: Personality-driven collaboration matching
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import CreatorProfile
import uuid
import json

class PersonalityQuiz(models.Model):
    """
    Personality quiz questions and structure
    """
    QUIZ_TYPES = [
        ('big_five', 'Big Five Personality'),
        ('creative_style', 'Creative Style Assessment'),
        ('collaboration_preference', 'Collaboration Preference'),
        ('work_style', 'Work Style Assessment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=500)
    quiz_type = models.CharField(max_length=30, choices=QUIZ_TYPES)
    questions = models.JSONField(default=list)  # List of question objects
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'personality_quizzes'
        verbose_name = 'Personality Quiz'
        verbose_name_plural = 'Personality Quizzes'
    
    def __str__(self):
        return f"{self.title} ({self.quiz_type})"

class PersonalityResponse(models.Model):
    """
    User responses to personality quizzes
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='personality_responses')
    quiz = models.ForeignKey(PersonalityQuiz, on_delete=models.CASCADE, related_name='responses')
    answers = models.JSONField(default=dict)  # Question ID -> Answer mapping
    completion_time_seconds = models.IntegerField(null=True, blank=True)
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'personality_responses'
        unique_together = ['profile', 'quiz']
        verbose_name = 'Personality Response'
        verbose_name_plural = 'Personality Responses'
    
    def __str__(self):
        return f"{self.profile.display_name} - {self.quiz.title}"

class PersonalityProfile(models.Model):
    """
    Computed personality profile based on quiz responses
    """
    PERSONALITY_DIMENSIONS = [
        ('openness', 'Openness to Experience'),
        ('conscientiousness', 'Conscientiousness'),
        ('extraversion', 'Extraversion'),
        ('agreeableness', 'Agreeableness'),
        ('neuroticism', 'Neuroticism'),
        ('creativity', 'Creativity Index'),
        ('collaboration_style', 'Collaboration Style'),
        ('communication_preference', 'Communication Preference'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.OneToOneField(CreatorProfile, on_delete=models.CASCADE, related_name='personality_profile')
    
    # Big Five Personality Traits (0-100 scale)
    openness = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        default=50.0,
        help_text="Openness to experience and new ideas"
    )
    conscientiousness = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        default=50.0,
        help_text="Organization and dependability"
    )
    extraversion = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        default=50.0,
        help_text="Social energy and assertiveness"
    )
    agreeableness = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        default=50.0,
        help_text="Cooperation and trust"
    )
    neuroticism = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        default=50.0,
        help_text="Emotional stability"
    )
    
    # Creative-specific traits
    creativity_index = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        default=50.0,
        help_text="Overall creativity and innovation score"
    )
    risk_tolerance = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        default=50.0,
        help_text="Willingness to take creative risks"
    )
    
    # Collaboration preferences
    collaboration_style = models.CharField(
        max_length=20,
        choices=[
            ('leader', 'Natural Leader'),
            ('collaborator', 'Equal Collaborator'),
            ('supporter', 'Supportive Partner'),
            ('independent', 'Independent Worker'),
        ],
        default='collaborator'
    )
    
    communication_preference = models.CharField(
        max_length=20,
        choices=[
            ('direct', 'Direct Communication'),
            ('diplomatic', 'Diplomatic Approach'),
            ('casual', 'Casual Style'),
            ('formal', 'Formal Style'),
        ],
        default='casual'
    )
    
    # Work style preferences
    work_pace = models.CharField(
        max_length=15,
        choices=[
            ('fast', 'Fast-paced'),
            ('moderate', 'Moderate pace'),
            ('deliberate', 'Deliberate/Slow'),
        ],
        default='moderate'
    )
    
    feedback_style = models.CharField(
        max_length=15,
        choices=[
            ('frequent', 'Frequent feedback'),
            ('milestone', 'Milestone-based'),
            ('minimal', 'Minimal feedback'),
        ],
        default='milestone'
    )
    
    # AI-computed compatibility factors
    compatibility_vector = models.JSONField(
        default=dict,
        help_text="AI-computed vector for matching compatibility"
    )
    
    # Metadata
    last_updated = models.DateTimeField(auto_now=True)
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.0,
        help_text="AI confidence in personality assessment"
    )
    
    class Meta:
        db_table = 'personality_profiles'
        verbose_name = 'Personality Profile'
        verbose_name_plural = 'Personality Profiles'
    
    def __str__(self):
        return f"{self.profile.display_name} - Personality Profile"
    
    def get_compatibility_score(self, other_profile):
        """
        Calculate compatibility score with another personality profile
        Returns score between 0.0 and 1.0
        """
        if not isinstance(other_profile, PersonalityProfile):
            return 0.0
        
        # Weight factors for different traits
        weights = {
            'openness': 0.15,
            'conscientiousness': 0.10,
            'extraversion': 0.15,
            'agreeableness': 0.20,
            'neuroticism': 0.10,
            'creativity_index': 0.20,
            'risk_tolerance': 0.10,
        }
        
        total_score = 0.0
        for trait, weight in weights.items():
            self_value = getattr(self, trait, 50.0)
            other_value = getattr(other_profile, trait, 50.0)
            
            # Calculate similarity (closer values = higher compatibility)
            difference = abs(self_value - other_value)
            similarity = max(0, 100 - difference) / 100
            
            # Special handling for certain traits
            if trait == 'agreeableness':
                # Higher agreeableness in both is better
                bonus = min(self_value, other_value) / 100 * 0.2
                similarity += bonus
            elif trait == 'neuroticism':
                # Lower neuroticism is generally better for collaboration
                penalty = max(self_value, other_value) / 100 * 0.1
                similarity -= penalty
            
            total_score += similarity * weight
        
        # Bonus for complementary collaboration styles
        style_compatibility = self._get_style_compatibility(other_profile)
        total_score += style_compatibility * 0.1
        
        return min(1.0, max(0.0, total_score))
    
    def _get_style_compatibility(self, other_profile):
        """Calculate compatibility bonus for collaboration styles"""
        style_matrix = {
            ('leader', 'supporter'): 0.9,
            ('leader', 'collaborator'): 0.7,
            ('collaborator', 'collaborator'): 0.8,
            ('collaborator', 'supporter'): 0.8,
            ('supporter', 'leader'): 0.9,
            ('independent', 'independent'): 0.3,
        }
        
        key = (self.collaboration_style, other_profile.collaboration_style)
        reverse_key = (other_profile.collaboration_style, self.collaboration_style)
        
        return style_matrix.get(key, style_matrix.get(reverse_key, 0.5))

class CollaborationMatch(models.Model):
    """
    AI-generated collaboration matches between creators
    """
    MATCH_STATUS = [
        ('pending', 'Pending Review'),
        ('viewed', 'Viewed'),
        ('liked', 'Liked'),
        ('passed', 'Passed'),
        ('matched', 'Mutual Match'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile_a = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='matches_as_a')
    profile_b = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='matches_as_b')
    
    # Matching scores
    compatibility_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Overall compatibility score"
    )
    personality_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Personality-based compatibility"
    )
    skill_complementarity_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="How well skills complement each other"
    )
    
    # Match metadata
    match_reason = models.TextField(
        max_length=500,
        help_text="AI-generated explanation for the match"
    )
    suggested_collaboration_types = models.JSONField(
        default=list,
        help_text="List of suggested collaboration types"
    )
    
    # Status tracking
    status_a = models.CharField(max_length=10, choices=MATCH_STATUS, default='pending')
    status_b = models.CharField(max_length=10, choices=MATCH_STATUS, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    viewed_at_a = models.DateTimeField(null=True, blank=True)
    viewed_at_b = models.DateTimeField(null=True, blank=True)
    matched_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'collaboration_matches'
        unique_together = ['profile_a', 'profile_b']
        indexes = [
            models.Index(fields=['profile_a', 'status_a']),
            models.Index(fields=['profile_b', 'status_b']),
            models.Index(fields=['compatibility_score']),
            models.Index(fields=['created_at']),
        ]
        verbose_name = 'Collaboration Match'
        verbose_name_plural = 'Collaboration Matches'
    
    def __str__(self):
        return f"Match: {self.profile_a.display_name} ↔ {self.profile_b.display_name} ({self.compatibility_score:.2f})"
    
    @property
    def is_mutual_match(self):
        """Check if both profiles have liked each other"""
        return self.status_a == 'liked' and self.status_b == 'liked'
    
    def update_match_status(self):
        """Update match status if mutual like occurs"""
        if self.is_mutual_match and self.status_a != 'matched':
            self.status_a = 'matched'
            self.status_b = 'matched'
            self.matched_at = models.timezone.now()
            self.save()
            return True
        return False
