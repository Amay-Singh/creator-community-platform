"""
Subscription URL patterns
"""
from django.urls import path
from . import views

urlpatterns = [
    # Subscription plans
    path('plans/', views.SubscriptionPlansView.as_view(), name='subscription-plans'),
    
    # User subscription management
    path('me/', views.UserSubscriptionView.as_view(), name='user-subscription'),
    path('create/', views.create_subscription, name='create-subscription'),
    path('cancel/', views.cancel_subscription, name='cancel-subscription'),
    path('usage/', views.subscription_usage, name='subscription-usage'),
    
    # One-time purchases
    path('purchase-ai-portfolio/', views.purchase_ai_portfolio, name='purchase-ai-portfolio'),
    
    # Advertisement system
    path('ads/', views.RelevantAdsView.as_view(), name='relevant-ads'),
    path('ads/track/', views.track_ad_interaction, name='track-ad-interaction'),
]
