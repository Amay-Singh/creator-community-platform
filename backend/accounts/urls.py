"""
URL patterns for accounts app
"""
from django.urls import path, include
from . import views
from .ad_showcase_views import (
    get_relevant_ads, track_ad_interaction, get_ad_insights, get_contextual_ads
)

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify/', views.VerifyAccountView.as_view(), name='verify'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.CreatorProfileView.as_view(), name='profile'),
    
    # Profile Authentication (REQ-3)
    path('approval-code/request/', views.RequestApprovalCodeView.as_view(), name='request_approval_code'),
    path('approval-code/verify/', views.VerifyApprovalCodeView.as_view(), name='verify_approval_code'),
    path('authentication-status/', views.ProfileAuthenticationStatusView.as_view(), name='authentication_status'),
    
    # Advanced Search (REQ-5)
    path('search/', views.ProfileSearchView.as_view(), name='profile_search'),
    
    # AI Recommendations (REQ-7)
    path('recommendations/', views.AIRecommendationsView.as_view(), name='ai_recommendations'),
    
    # Profile Health Metrics (REQ-4)
    path('health-metrics/', views.ProfileHealthMetricsView.as_view(), name='health_metrics'),
    
    # Profile feedback
    path('profiles/<uuid:profile_id>/feedback/', views.ProfileFeedbackCreateView.as_view(), name='profile_feedback_create'),
    path('profiles/<uuid:profile_id>/feedback/list/', views.ProfileFeedbackListView.as_view(), name='profile_feedback_list'),
    
    # Public profile browsing
    path('public/profiles/', views.PublicProfileBrowsingView.as_view(), name='public_profile_browsing'),
    
    # Ad showcase (REQ-17)
    path('ads/', get_relevant_ads, name='relevant_ads'),
    path('ads/track/', track_ad_interaction, name='track_ad_interaction'),
    path('ads/insights/', get_ad_insights, name='ad_insights'),
    path('ads/<str:context>/', get_contextual_ads, name='contextual_ads'),
    
    # Subscription and Payment System (REQ-22-25)
    path('subscription/', include('accounts.subscription_urls')),
    
    # Public Profile Browsing
    path('profiles/', views.PublicProfileListView.as_view(), name='public_profiles'),
    path('profiles/<uuid:pk>/', views.PublicProfileDetailView.as_view(), name='public_profile_detail'),
    
    # Include personality URLs
    path('personality/', include('accounts.personality_urls')),
]
