from django.urls import path
from . import views

urlpatterns = [
    # AI content generation
    path('generate/', views.GenerateContentView.as_view(), name='generate-content'),
    path('validate/', views.ValidateContentView.as_view(), name='validate-content'),
    
    # AI collaboration matching
    path('collaboration-match/<int:profile_id>/', views.CollaborationMatchView.as_view(), name='collaboration-match'),
    path('suggestions/', views.AICollaborationSuggestionsView.as_view(), name='ai-suggestions'),
]
