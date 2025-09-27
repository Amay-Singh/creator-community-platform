"""
URL patterns for integrations app
P9-002: Social Media & External API Integrations
"""
from django.urls import path
from . import views

app_name = 'integrations'

urlpatterns = [
    # LinkedIn Integration
    path('linkedin/auth-url/', views.linkedin_auth_url, name='linkedin_auth_url'),
    path('linkedin/callback/', views.linkedin_callback, name='linkedin_callback'),
    
    # GitHub Integration
    path('github/auth-url/', views.github_auth_url, name='github_auth_url'),
    path('github/callback/', views.github_callback, name='github_callback'),
    
    # Twitter Integration
    path('twitter/profile/', views.twitter_profile_lookup, name='twitter_profile_lookup'),
    
    # Google Calendar Integration
    path('google-calendar/auth-url/', views.google_calendar_auth_url, name='google_calendar_auth_url'),
    path('google-calendar/callback/', views.google_calendar_callback, name='google_calendar_callback'),
    
    # Stripe Integration
    path('stripe/create-customer/', views.create_stripe_customer, name='create_stripe_customer'),
    path('stripe/create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    
    # Integration Status
    path('status/', views.integration_status, name='integration_status'),
]
