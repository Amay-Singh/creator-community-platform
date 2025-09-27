"""
Integration views for external services
P9-002: Social Media & External API Integrations
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.conf import settings
import logging

from .social_media import (
    linkedin_integration, github_integration, twitter_integration,
    google_calendar_integration, stripe_integration
)
from analytics.services import AnalyticsCollector

User = get_user_model()
logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def linkedin_auth_url(request):
    """Get LinkedIn OAuth authorization URL"""
    try:
        state = f"linkedin_{request.user.id}"
        auth_url = linkedin_integration.get_authorization_url(state)
        
        return Response({
            'auth_url': auth_url,
            'state': state
        })
        
    except Exception as e:
        logger.error(f"LinkedIn auth URL generation failed: {e}")
        return Response({
            'error': 'Failed to generate LinkedIn auth URL'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def linkedin_callback(request):
    """Handle LinkedIn OAuth callback"""
    try:
        code = request.data.get('code')
        state = request.data.get('state')
        
        if not code:
            return Response({
                'error': 'Authorization code is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Exchange code for token
        token_result = linkedin_integration.exchange_code_for_token(code)
        
        if not token_result.get('success'):
            return Response({
                'error': 'Failed to exchange code for token',
                'details': token_result.get('error')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user profile
        access_token = token_result['access_token']
        profile_result = linkedin_integration.get_user_profile(access_token)
        
        if not profile_result.get('success'):
            return Response({
                'error': 'Failed to fetch LinkedIn profile',
                'details': profile_result.get('error')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Import profile to creator profile
        import_result = linkedin_integration.import_profile_to_creator(
            request.user, 
            profile_result['profile']
        )
        
        return Response({
            'message': 'LinkedIn profile imported successfully',
            'profile_data': profile_result['profile'],
            'import_result': import_result
        })
        
    except Exception as e:
        logger.error(f"LinkedIn callback failed: {e}")
        return Response({
            'error': 'LinkedIn integration failed',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def github_auth_url(request):
    """Get GitHub OAuth authorization URL"""
    try:
        state = f"github_{request.user.id}"
        auth_url = github_integration.get_authorization_url(state)
        
        return Response({
            'auth_url': auth_url,
            'state': state
        })
        
    except Exception as e:
        logger.error(f"GitHub auth URL generation failed: {e}")
        return Response({
            'error': 'Failed to generate GitHub auth URL'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def github_callback(request):
    """Handle GitHub OAuth callback"""
    try:
        code = request.data.get('code')
        
        if not code:
            return Response({
                'error': 'Authorization code is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Exchange code for token
        token_result = github_integration.exchange_code_for_token(code)
        
        if not token_result.get('success'):
            return Response({
                'error': 'Failed to exchange code for token',
                'details': token_result.get('error')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user profile and repositories
        access_token = token_result['access_token']
        profile_result = github_integration.get_user_profile(access_token)
        
        if not profile_result.get('success'):
            return Response({
                'error': 'Failed to fetch GitHub profile',
                'details': profile_result.get('error')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Import portfolio to creator profile
        import_result = github_integration.import_github_portfolio(
            request.user, 
            profile_result
        )
        
        return Response({
            'message': 'GitHub portfolio imported successfully',
            'profile_data': profile_result['profile'],
            'repositories': profile_result['repositories'],
            'languages': profile_result['languages'],
            'import_result': import_result
        })
        
    except Exception as e:
        logger.error(f"GitHub callback failed: {e}")
        return Response({
            'error': 'GitHub integration failed',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def twitter_profile_lookup(request):
    """Look up Twitter profile by username"""
    try:
        username = request.data.get('username')
        
        if not username:
            return Response({
                'error': 'Twitter username is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Remove @ if present
        username = username.lstrip('@')
        
        profile_result = twitter_integration.get_user_profile(username)
        
        if not profile_result.get('success'):
            return Response({
                'error': 'Failed to fetch Twitter profile',
                'details': profile_result.get('error')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Track analytics
        AnalyticsCollector.track_event(
            'twitter_profile_lookup',
            user=request.user,
            event_data={'username': username}
        )
        
        return Response({
            'message': 'Twitter profile fetched successfully',
            'profile': profile_result['profile']
        })
        
    except Exception as e:
        logger.error(f"Twitter profile lookup failed: {e}")
        return Response({
            'error': 'Twitter profile lookup failed',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def google_calendar_auth_url(request):
    """Get Google Calendar OAuth authorization URL"""
    try:
        state = f"google_calendar_{request.user.id}"
        auth_url = google_calendar_integration.get_authorization_url(state)
        
        return Response({
            'auth_url': auth_url,
            'state': state
        })
        
    except Exception as e:
        logger.error(f"Google Calendar auth URL generation failed: {e}")
        return Response({
            'error': 'Failed to generate Google Calendar auth URL'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def google_calendar_callback(request):
    """Handle Google Calendar OAuth callback"""
    try:
        code = request.data.get('code')
        
        if not code:
            return Response({
                'error': 'Authorization code is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Exchange code for token
        token_result = google_calendar_integration.exchange_code_for_token(code)
        
        if not token_result.get('success'):
            return Response({
                'error': 'Failed to exchange code for token',
                'details': token_result.get('error')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Store tokens securely (in production, encrypt these)
        # For now, we'll just return success
        
        return Response({
            'message': 'Google Calendar connected successfully',
            'has_refresh_token': bool(token_result.get('refresh_token'))
        })
        
    except Exception as e:
        logger.error(f"Google Calendar callback failed: {e}")
        return Response({
            'error': 'Google Calendar integration failed',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_stripe_customer(request):
    """Create Stripe customer for user"""
    try:
        email = request.data.get('email', request.user.email)
        
        result = stripe_integration.create_customer(request.user, email)
        
        if not result.get('success'):
            return Response({
                'error': 'Failed to create Stripe customer',
                'details': result.get('error')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Store customer ID (in production, store securely)
        # For now, we'll just return the customer ID
        
        return Response({
            'message': 'Stripe customer created successfully',
            'customer_id': result['customer_id']
        })
        
    except Exception as e:
        logger.error(f"Stripe customer creation failed: {e}")
        return Response({
            'error': 'Stripe customer creation failed',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_intent(request):
    """Create Stripe payment intent"""
    try:
        amount = request.data.get('amount')  # in cents
        currency = request.data.get('currency', 'usd')
        customer_id = request.data.get('customer_id')
        metadata = request.data.get('metadata', {})
        
        if not amount:
            return Response({
                'error': 'Amount is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = stripe_integration.create_payment_intent(
            amount=amount,
            currency=currency,
            customer_id=customer_id,
            metadata=metadata
        )
        
        if not result.get('success'):
            return Response({
                'error': 'Failed to create payment intent',
                'details': result.get('error')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'client_secret': result['client_secret'],
            'payment_intent_id': result['payment_intent_id']
        })
        
    except Exception as e:
        logger.error(f"Payment intent creation failed: {e}")
        return Response({
            'error': 'Payment intent creation failed',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def integration_status(request):
    """Get integration status for user"""
    try:
        # Check which integrations are configured
        integrations_status = {
            'linkedin': {
                'configured': bool(getattr(settings, 'LINKEDIN_CLIENT_ID', '')),
                'connected': False  # Would check user's stored tokens
            },
            'github': {
                'configured': bool(getattr(settings, 'GITHUB_CLIENT_ID', '')),
                'connected': False  # Would check user's stored tokens
            },
            'twitter': {
                'configured': bool(getattr(settings, 'TWITTER_BEARER_TOKEN', '')),
                'connected': False  # Would check user's stored tokens
            },
            'google_calendar': {
                'configured': bool(getattr(settings, 'GOOGLE_CLIENT_ID', '')),
                'connected': False  # Would check user's stored tokens
            },
            'stripe': {
                'configured': bool(getattr(settings, 'STRIPE_SECRET_KEY', '')),
                'connected': False  # Would check user's customer ID
            }
        }
        
        return Response({
            'integrations': integrations_status,
            'user_id': request.user.id
        })
        
    except Exception as e:
        logger.error(f"Integration status check failed: {e}")
        return Response({
            'error': 'Failed to check integration status',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
