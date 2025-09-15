"""
URL patterns for ai_services app
Enhanced for P5-006: AI Content Generation Assistant
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import recommendation_api
from . import search_api

app_name = 'ai_services'

# P5-006 AI Content Generation Assistant Router
router = DefaultRouter()
router.register(r'content-requests', views.ContentGenerationRequestViewSet, basename='content-requests')
router.register(r'generated-content', views.GeneratedContentViewSet, basename='generated-content')
router.register(r'templates', views.ContentTemplateViewSet, basename='templates')
router.register(r'categories', views.ContentCategoryViewSet, basename='categories')

urlpatterns = [
    # AI Content Validation
    path('validate/', views.validate_content, name='validate_content'),
    
    # AI Content Generation
    path('generate/', views.generate_content, name='generate_content'),
    
    # P5-006 AI Content Generation Assistant API
    path('content/', include(router.urls)),
    path('content/stats/', views.content_generation_stats, name='content_stats'),
    path('content/usage/', views.usage_tracking, name='usage_tracking'),
    path('content/batch/', views.batch_generate, name='batch_generate'),
    
    # AI Matching and Recommendations
    path('match/suggestions/', recommendation_api.generate_suggestions, name='match_suggestions'),
    path('match/explain/<str:candidate_id>/', recommendation_api.explain_match, name='explain_match'),
    path('match/feedback/', recommendation_api.record_feedback, name='match_feedback'),
    path('match/stats/', recommendation_api.get_matching_stats, name='match_stats'),
    path('match/preferences/', recommendation_api.user_preferences, name='match_preferences'),
    path('match/health/', recommendation_api.matching_health, name='match_health'),
    
    # Advanced Search and Talent Map
    path('search/advanced/', search_api.advanced_search, name='advanced_search'),
    path('search/talent-map/', search_api.talent_map, name='talent_map'),
    path('search/suggestions/', search_api.search_suggestions, name='search_suggestions'),
    path('search/filters/', search_api.search_filters, name='search_filters'),
    path('search/health/', search_api.search_health, name='search_health'),
    
    # Legacy endpoints
    path('legacy/generate/', views.AIContentGenerationView.as_view(), name='legacy_ai_content_generation'),
]
