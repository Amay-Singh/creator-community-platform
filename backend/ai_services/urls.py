"""
URL patterns for ai_services app
"""
from django.urls import path
from . import views
from .recommendation_api import (
    AIMatchingAPIView, explain_match, record_match_feedback,
    get_matching_stats, update_matching_preferences, 
    get_matching_preferences, matching_health_check
)

app_name = 'ai_services'

urlpatterns = [
    # AI Content Validation
    path('validate/', views.validate_content, name='validate_content'),
    path('validation/<uuid:validation_id>/', views.get_validation_result, name='get_validation_result'),
    
    # AI Content Generation
    path('generate/', views.generate_content, name='generate_content'),
    path('generation/<uuid:generation_id>/', views.get_generation_result, name='get_generation_result'),
    
    # Profile Feedback
    path('feedback/', views.submit_feedback, name='submit_feedback'),
    path('feedback/<uuid:profile_id>/', views.get_profile_feedback, name='get_profile_feedback'),
    
    # AI Matching & Recommendations
    path('match/suggestions/', AIMatchingAPIView.as_view(), name='ai_match_suggestions'),
    path('match/explain/<str:candidate_id>/', explain_match, name='explain_match'),
    path('match/feedback/', record_match_feedback, name='match_feedback'),
    path('match/stats/', get_matching_stats, name='matching_stats'),
    path('match/preferences/', update_matching_preferences, name='update_preferences'),
    path('match/preferences/', get_matching_preferences, name='get_preferences'),
    path('match/health/', matching_health_check, name='matching_health'),
    # Legacy endpoints
    path('legacy/generate/', views.AIContentGenerationView.as_view(), name='legacy_ai_content_generation'),
]
