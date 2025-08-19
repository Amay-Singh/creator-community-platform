"""
URL patterns for ai_services app
"""
from django.urls import path
from . import views
from .enhanced_views import (
    AIContentGenerationView, PortfolioGenerationView,
    AIContentGenerationListView, AIContentGenerationDetailView,
    regenerate_content, generation_history, batch_portfolio_generation,
    content_generation_stats
)

app_name = 'ai_services'

urlpatterns = [
    # Content validation
    path('validate/', views.ContentValidationView.as_view(), name='content_validation'),
    
    # AI Content Generation (REQ-13)
    path('generate/', AIContentGenerationView.as_view(), name='ai_content_generation'),
    path('generations/', AIContentGenerationListView.as_view(), name='generation_list'),
    path('generations/<uuid:pk>/', AIContentGenerationDetailView.as_view(), name='generation_detail'),
    path('generations/<uuid:generation_id>/regenerate/', regenerate_content, name='regenerate_content'),
    path('generation-history/', generation_history, name='generation_history'),
    path('generation-stats/', content_generation_stats, name='generation_stats'),
    
    # Portfolio Generation (REQ-15)
    path('portfolio/generate/', PortfolioGenerationView.as_view(), name='portfolio_generation'),
    path('portfolio/batch-generate/', batch_portfolio_generation, name='batch_portfolio_generation'),
    
    # Legacy endpoints
    path('legacy/generate/', views.AIContentGenerationView.as_view(), name='legacy_ai_content_generation'),
]
