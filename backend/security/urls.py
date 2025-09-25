"""
Security URL configuration
"""
from django.urls import path
from .two_factor import (
    setup_2fa, enable_2fa, disable_2fa, 
    verify_2fa, get_2fa_status
)

app_name = 'security'

urlpatterns = [
    # Two-Factor Authentication
    path('2fa/setup/', setup_2fa, name='setup_2fa'),
    path('2fa/enable/', enable_2fa, name='enable_2fa'),
    path('2fa/disable/', disable_2fa, name='disable_2fa'),
    path('2fa/verify/', verify_2fa, name='verify_2fa'),
    path('2fa/status/', get_2fa_status, name='get_2fa_status'),
]
