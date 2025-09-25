"""
URL patterns for subscription and payment system
"""
from django.urls import path
from django.http import JsonResponse
from .subscription_views import (
    SubscriptionPlansView, UserSubscriptionView, CreateSubscriptionView,
    PremiumAddonsView, PurchaseAddonView, cancel_subscription,
    usage_limits, payment_history, validate_promo_code,
    subscription_analytics, increment_feature_usage
)

def subscription_health(request):
    """Subscription service health check"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'subscriptions',
        'endpoints': {
            'plans': '/api/subscriptions/plans/',
            'current': '/api/subscriptions/current/',
            'create': '/api/subscriptions/create/'
        }
    })

app_name = 'subscription'

urlpatterns = [
    # Health endpoint
    path('health/', subscription_health, name='subscription_health'),
    
    # Subscription plans and management
    path('plans/', SubscriptionPlansView.as_view(), name='plans'),
    path('current/', UserSubscriptionView.as_view(), name='current'),
    path('create/', CreateSubscriptionView.as_view(), name='create'),
    path('cancel/', cancel_subscription, name='cancel'),
    path('analytics/', subscription_analytics, name='analytics'),
    
    # Premium add-ons
    path('addons/', PremiumAddonsView.as_view(), name='addons'),
    path('addons/purchase/', PurchaseAddonView.as_view(), name='purchase_addon'),
    
    # Usage and payments
    path('usage-limits/', usage_limits, name='usage_limits'),
    path('payment-history/', payment_history, name='payment_history'),
    path('usage/increment/', increment_feature_usage, name='increment_usage'),
    
    # Promo codes
    path('promo-code/validate/', validate_promo_code, name='validate_promo_code'),
]
