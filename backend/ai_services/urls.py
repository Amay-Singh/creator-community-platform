"""
URL patterns for ai_services app
Enhanced for P5-006: AI Content Generation Assistant
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'ai_services'

# Create router for ViewSets
router = DefaultRouter()

# P5-006: AI Content Generation Assistant
router.register(r'content-requests', views.ContentGenerationRequestViewSet, basename='content-requests')
router.register(r'generated-content', views.GeneratedContentViewSet, basename='generated-content')
router.register(r'templates', views.ContentTemplateViewSet, basename='templates')
router.register(r'categories', views.ContentCategoryViewSet, basename='categories')

# P5-001: AI-Powered Creator Matching
router.register(r'embeddings', views.CreatorEmbeddingViewSet, basename='embeddings')
router.register(r'matches', views.MatchResultViewSet, basename='matches')
router.register(r'match-feedback', views.MatchFeedbackViewSet, basename='match-feedback')
router.register(r'match-history', views.MatchHistoryViewSet, basename='match-history')

urlpatterns = [
    # Legacy endpoints
    path('validate/', views.validate_content, name='validate_content'),
    path('generate/', views.generate_content, name='generate_content'),
    
    # ViewSet routes
    path('', include(router.urls)),
    
    # P5-006: AI Content Generation endpoints
    path('stats/', views.content_generation_stats, name='content_generation_stats'),
    path('usage/', views.usage_tracking, name='usage_tracking'),
    path('batch/', views.batch_content_generation, name='batch_content_generation'),
    
    # P5-001: AI Matching endpoints
    path('matching/batch/', views.batch_match, name='batch_match'),
    path('matching/stats/', views.match_statistics, name='match_statistics'),
    
    # Health check
    path('health/', views.ai_services_health, name='ai_services_health'),
]
