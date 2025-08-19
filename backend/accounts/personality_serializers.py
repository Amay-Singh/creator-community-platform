"""
Serializers for Personality Quiz and Matching API endpoints
"""
from rest_framework import serializers
from .personality_models import PersonalityQuiz, PersonalityResponse, PersonalityProfile, CollaborationMatch
from .models import CreatorProfile

class PersonalityQuizSerializer(serializers.ModelSerializer):
    """Serializer for personality quizzes"""
    
    class Meta:
        model = PersonalityQuiz
        fields = [
            'id', 'title', 'description', 'quiz_type', 'questions', 
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class PersonalityResponseSerializer(serializers.ModelSerializer):
    """Serializer for quiz responses"""
    
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    quiz_type = serializers.CharField(source='quiz.quiz_type', read_only=True)
    
    class Meta:
        model = PersonalityResponse
        fields = [
            'id', 'quiz', 'quiz_title', 'quiz_type', 'answers', 
            'completion_time_seconds', 'completed_at'
        ]
        read_only_fields = ['id', 'profile', 'completed_at']

class PersonalityProfileSerializer(serializers.ModelSerializer):
    """Serializer for personality profiles"""
    
    profile_name = serializers.CharField(source='profile.display_name', read_only=True)
    profile_category = serializers.CharField(source='profile.get_category_display', read_only=True)
    
    class Meta:
        model = PersonalityProfile
        fields = [
            'id', 'profile_name', 'profile_category',
            'openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism',
            'creativity_index', 'risk_tolerance',
            'collaboration_style', 'communication_preference', 'work_pace', 'feedback_style',
            'last_updated', 'confidence_score'
        ]
        read_only_fields = ['id', 'profile_name', 'profile_category', 'last_updated']

class CollaborationMatchSerializer(serializers.ModelSerializer):
    """Serializer for collaboration matches"""
    
    profile_a_data = serializers.SerializerMethodField()
    profile_b_data = serializers.SerializerMethodField()
    is_mutual_match = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = CollaborationMatch
        fields = [
            'id', 'profile_a_data', 'profile_b_data',
            'compatibility_score', 'personality_score', 'skill_complementarity_score',
            'match_reason', 'suggested_collaboration_types',
            'status_a', 'status_b', 'is_mutual_match',
            'created_at', 'viewed_at_a', 'viewed_at_b', 'matched_at'
        ]
        read_only_fields = [
            'id', 'profile_a_data', 'profile_b_data', 'compatibility_score',
            'personality_score', 'skill_complementarity_score', 'match_reason',
            'suggested_collaboration_types', 'is_mutual_match',
            'created_at', 'viewed_at_a', 'viewed_at_b', 'matched_at'
        ]
    
    def get_profile_a_data(self, obj):
        """Get profile A summary data"""
        return self._get_profile_summary(obj.profile_a)
    
    def get_profile_b_data(self, obj):
        """Get profile B summary data"""
        return self._get_profile_summary(obj.profile_b)
    
    def _get_profile_summary(self, profile):
        """Get summary data for a profile"""
        return {
            'id': str(profile.id),
            'display_name': profile.display_name,
            'category': profile.get_category_display(),
            'experience_level': profile.get_experience_level_display(),
            'location': profile.location,
            'bio': profile.bio[:100] + '...' if len(profile.bio) > 100 else profile.bio,
            'portfolio_count': profile.portfolio_items.count(),
            'avatar_url': profile.avatar.url if profile.avatar else None,
        }

class QuizSubmissionSerializer(serializers.Serializer):
    """Serializer for quiz submission"""
    
    quiz_id = serializers.UUIDField()
    answers = serializers.DictField()
    completion_time_seconds = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_quiz_id(self, value):
        """Validate quiz exists and is active"""
        try:
            quiz = PersonalityQuiz.objects.get(id=value, is_active=True)
            return value
        except PersonalityQuiz.DoesNotExist:
            raise serializers.ValidationError("Quiz not found or inactive")
    
    def validate_answers(self, value):
        """Validate answers format"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Answers must be a dictionary")
        
        if not value:
            raise serializers.ValidationError("Answers cannot be empty")
        
        return value

class MatchActionSerializer(serializers.Serializer):
    """Serializer for match actions (like/pass)"""
    
    ACTION_CHOICES = [
        ('like', 'Like'),
        ('pass', 'Pass'),
    ]
    
    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    match_id = serializers.UUIDField()
    
    def validate_match_id(self, value):
        """Validate match exists"""
        try:
            CollaborationMatch.objects.get(id=value)
            return value
        except CollaborationMatch.DoesNotExist:
            raise serializers.ValidationError("Match not found")

class PersonalityInsightsSerializer(serializers.Serializer):
    """Serializer for personality insights and recommendations"""
    
    personality_summary = serializers.CharField()
    strengths = serializers.ListField(child=serializers.CharField())
    collaboration_tips = serializers.ListField(child=serializers.CharField())
    recommended_partners = serializers.ListField(child=serializers.CharField())
    growth_areas = serializers.ListField(child=serializers.CharField())
    
class MatchingPreferencesSerializer(serializers.Serializer):
    """Serializer for user matching preferences"""
    
    preferred_categories = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    preferred_experience_levels = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    preferred_collaboration_types = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    location_preference = serializers.CharField(required=False, allow_blank=True)
    min_compatibility_score = serializers.FloatField(
        min_value=0.0,
        max_value=1.0,
        default=0.3
    )
    max_matches_per_day = serializers.IntegerField(
        min_value=1,
        max_value=50,
        default=10
    )
