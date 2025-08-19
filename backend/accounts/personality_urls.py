"""
URL patterns for Personality Quiz and Matching API endpoints
"""
from django.urls import path
from . import personality_views

urlpatterns = [
    # Personality Quizzes
    path('personality/quizzes/', personality_views.PersonalityQuizListView.as_view(), name='personality-quiz-list'),
    path('personality/quizzes/<uuid:pk>/', personality_views.PersonalityQuizDetailView.as_view(), name='personality-quiz-detail'),
    path('personality/submit-quiz/', personality_views.submit_quiz_response, name='submit-quiz-response'),
    
    # Personality Profile
    path('personality/profile/', personality_views.PersonalityProfileView.as_view(), name='personality-profile'),
    path('personality/insights/', personality_views.personality_insights, name='personality-insights'),
    
    # Collaboration Matching
    path('matches/', personality_views.CollaborationMatchListView.as_view(), name='collaboration-match-list'),
    path('matches/generate/', personality_views.generate_new_matches, name='generate-matches'),
    path('matches/action/', personality_views.match_action, name='match-action'),
    path('matches/statistics/', personality_views.match_statistics, name='match-statistics'),
]
