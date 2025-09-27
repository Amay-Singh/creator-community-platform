"""
Social Media Integrations for Creator Community Platform
P9-002: Social Media & External API Integrations
"""
import requests
import json
import logging
from typing import Dict, Any, List, Optional
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import base64
import hashlib
import hmac
from urllib.parse import urlencode, parse_qs
from analytics.services import AnalyticsCollector

User = get_user_model()
logger = logging.getLogger(__name__)


class LinkedInIntegration:
    """LinkedIn API integration for profile import and networking"""
    
    def __init__(self):
        self.client_id = getattr(settings, 'LINKEDIN_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'LINKEDIN_CLIENT_SECRET', '')
        self.redirect_uri = getattr(settings, 'LINKEDIN_REDIRECT_URI', '')
        self.base_url = 'https://api.linkedin.com/v2'
        
    def get_authorization_url(self, state: str = None) -> str:
        """Generate LinkedIn OAuth authorization URL"""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'r_liteprofile r_emailaddress w_member_social',
            'state': state or 'linkedin_auth'
        }
        
        return f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        try:
            token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
            
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': self.redirect_uri,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Cache token for user
            cache_key = f"linkedin_token:{code[:10]}"
            cache.set(cache_key, token_data, token_data.get('expires_in', 3600))
            
            return {
                'success': True,
                'access_token': token_data.get('access_token'),
                'expires_in': token_data.get('expires_in'),
                'token_type': token_data.get('token_type')
            }
            
        except Exception as e:
            logger.error(f"LinkedIn token exchange failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """Get LinkedIn user profile data"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Get basic profile
            profile_url = f"{self.base_url}/people/~"
            profile_response = requests.get(profile_url, headers=headers)
            profile_response.raise_for_status()
            profile_data = profile_response.json()
            
            # Get email
            email_url = f"{self.base_url}/emailAddress?q=members&projection=(elements*(handle~))"
            email_response = requests.get(email_url, headers=headers)
            email_response.raise_for_status()
            email_data = email_response.json()
            
            # Extract email
            email = None
            if email_data.get('elements'):
                email = email_data['elements'][0]['handle~']['emailAddress']
            
            return {
                'success': True,
                'profile': {
                    'id': profile_data.get('id'),
                    'first_name': profile_data.get('localizedFirstName'),
                    'last_name': profile_data.get('localizedLastName'),
                    'email': email,
                    'headline': profile_data.get('localizedHeadline'),
                    'industry': profile_data.get('industryName'),
                    'location': profile_data.get('locationName'),
                    'profile_picture': profile_data.get('profilePicture', {}).get('displayImage')
                }
            }
            
        except Exception as e:
            logger.error(f"LinkedIn profile fetch failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def import_profile_to_creator(self, user: User, linkedin_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Import LinkedIn profile data to creator profile"""
        try:
            from ai_services.models import CreatorProfile
            
            profile, created = CreatorProfile.objects.get_or_create(user=user)
            
            # Update profile with LinkedIn data
            if linkedin_profile.get('headline'):
                profile.bio = linkedin_profile['headline']
            
            if linkedin_profile.get('location'):
                profile.location = linkedin_profile['location']
            
            # Extract skills from headline/industry
            skills = []
            if linkedin_profile.get('industry'):
                skills.append(linkedin_profile['industry'])
            
            if linkedin_profile.get('headline'):
                # Simple skill extraction from headline
                headline_lower = linkedin_profile['headline'].lower()
                skill_keywords = [
                    'python', 'javascript', 'react', 'django', 'design', 'marketing',
                    'data science', 'machine learning', 'photography', 'writing',
                    'video editing', 'graphic design', 'web development'
                ]
                
                for keyword in skill_keywords:
                    if keyword in headline_lower:
                        skills.append(keyword.title())
            
            if skills:
                existing_skills = profile.skills if hasattr(profile, 'skills') and profile.skills else []
                if isinstance(existing_skills, str):
                    existing_skills = existing_skills.split(',') if existing_skills else []
                
                combined_skills = list(set(existing_skills + skills))
                profile.skills = combined_skills
            
            profile.save()
            
            # Track analytics
            AnalyticsCollector.track_event(
                'linkedin_profile_imported',
                user=user,
                event_data={
                    'skills_imported': len(skills),
                    'profile_created': created
                }
            )
            
            return {
                'success': True,
                'profile_updated': True,
                'skills_imported': skills,
                'profile_created': created
            }
            
        except Exception as e:
            logger.error(f"LinkedIn profile import failed: {e}")
            return {'success': False, 'error': str(e)}


class GitHubIntegration:
    """GitHub API integration for developer portfolios"""
    
    def __init__(self):
        self.client_id = getattr(settings, 'GITHUB_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'GITHUB_CLIENT_SECRET', '')
        self.base_url = 'https://api.github.com'
        
    def get_authorization_url(self, state: str = None) -> str:
        """Generate GitHub OAuth authorization URL"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': getattr(settings, 'GITHUB_REDIRECT_URI', ''),
            'scope': 'user:email,public_repo',
            'state': state or 'github_auth'
        }
        
        return f"https://github.com/login/oauth/authorize?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        try:
            token_url = 'https://github.com/login/oauth/access_token'
            
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code
            }
            
            headers = {'Accept': 'application/json'}
            response = requests.post(token_url, data=data, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            
            return {
                'success': True,
                'access_token': token_data.get('access_token'),
                'token_type': token_data.get('token_type'),
                'scope': token_data.get('scope')
            }
            
        except Exception as e:
            logger.error(f"GitHub token exchange failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """Get GitHub user profile and repositories"""
        try:
            headers = {'Authorization': f'token {access_token}'}
            
            # Get user profile
            user_url = f"{self.base_url}/user"
            user_response = requests.get(user_url, headers=headers)
            user_response.raise_for_status()
            user_data = user_response.json()
            
            # Get repositories
            repos_url = f"{self.base_url}/user/repos?sort=updated&per_page=10"
            repos_response = requests.get(repos_url, headers=headers)
            repos_response.raise_for_status()
            repos_data = repos_response.json()
            
            # Get languages used
            languages = set()
            for repo in repos_data[:5]:  # Check top 5 repos
                if repo.get('languages_url'):
                    lang_response = requests.get(repo['languages_url'], headers=headers)
                    if lang_response.status_code == 200:
                        repo_languages = lang_response.json()
                        languages.update(repo_languages.keys())
            
            return {
                'success': True,
                'profile': {
                    'username': user_data.get('login'),
                    'name': user_data.get('name'),
                    'bio': user_data.get('bio'),
                    'location': user_data.get('location'),
                    'email': user_data.get('email'),
                    'public_repos': user_data.get('public_repos'),
                    'followers': user_data.get('followers'),
                    'following': user_data.get('following'),
                    'avatar_url': user_data.get('avatar_url'),
                    'html_url': user_data.get('html_url')
                },
                'repositories': [
                    {
                        'name': repo.get('name'),
                        'description': repo.get('description'),
                        'language': repo.get('language'),
                        'stars': repo.get('stargazers_count'),
                        'forks': repo.get('forks_count'),
                        'url': repo.get('html_url'),
                        'updated_at': repo.get('updated_at')
                    }
                    for repo in repos_data
                ],
                'languages': list(languages)
            }
            
        except Exception as e:
            logger.error(f"GitHub profile fetch failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def import_github_portfolio(self, user: User, github_data: Dict[str, Any]) -> Dict[str, Any]:
        """Import GitHub data to creator profile"""
        try:
            from ai_services.models import CreatorProfile
            
            profile, created = CreatorProfile.objects.get_or_create(user=user)
            github_profile = github_data.get('profile', {})
            
            # Update bio if not set
            if github_profile.get('bio') and not profile.bio:
                profile.bio = github_profile['bio']
            
            # Update location if not set
            if github_profile.get('location') and not profile.location:
                profile.location = github_profile['location']
            
            # Add programming languages as skills
            languages = github_data.get('languages', [])
            existing_skills = profile.skills if hasattr(profile, 'skills') and profile.skills else []
            if isinstance(existing_skills, str):
                existing_skills = existing_skills.split(',') if existing_skills else []
            
            # Add development-related skills
            dev_skills = ['Software Development', 'Version Control', 'Open Source']
            combined_skills = list(set(existing_skills + languages + dev_skills))
            profile.skills = combined_skills
            
            # Store GitHub portfolio data
            portfolio_data = {
                'github_username': github_profile.get('username'),
                'github_url': github_profile.get('html_url'),
                'public_repos': github_profile.get('public_repos'),
                'github_followers': github_profile.get('followers'),
                'top_repositories': github_data.get('repositories', [])[:5],
                'programming_languages': languages
            }
            
            # Store in profile metadata or separate field
            if hasattr(profile, 'portfolio_data'):
                existing_portfolio = profile.portfolio_data or {}
                existing_portfolio.update(portfolio_data)
                profile.portfolio_data = existing_portfolio
            
            profile.save()
            
            # Track analytics
            AnalyticsCollector.track_event(
                'github_portfolio_imported',
                user=user,
                event_data={
                    'repositories_count': len(github_data.get('repositories', [])),
                    'languages_count': len(languages),
                    'profile_created': created
                }
            )
            
            return {
                'success': True,
                'profile_updated': True,
                'repositories_imported': len(github_data.get('repositories', [])),
                'languages_imported': languages,
                'profile_created': created
            }
            
        except Exception as e:
            logger.error(f"GitHub portfolio import failed: {e}")
            return {'success': False, 'error': str(e)}


class TwitterIntegration:
    """Twitter/X API integration for social presence"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'TWITTER_API_KEY', '')
        self.api_secret = getattr(settings, 'TWITTER_API_SECRET', '')
        self.bearer_token = getattr(settings, 'TWITTER_BEARER_TOKEN', '')
        self.base_url = 'https://api.twitter.com/2'
        
    def get_user_profile(self, username: str) -> Dict[str, Any]:
        """Get Twitter user profile (public data only)"""
        try:
            headers = {'Authorization': f'Bearer {self.bearer_token}'}
            
            url = f"{self.base_url}/users/by/username/{username}"
            params = {
                'user.fields': 'description,location,public_metrics,profile_image_url,verified'
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            user_data = data.get('data', {})
            
            return {
                'success': True,
                'profile': {
                    'id': user_data.get('id'),
                    'username': user_data.get('username'),
                    'name': user_data.get('name'),
                    'description': user_data.get('description'),
                    'location': user_data.get('location'),
                    'verified': user_data.get('verified'),
                    'profile_image_url': user_data.get('profile_image_url'),
                    'followers_count': user_data.get('public_metrics', {}).get('followers_count'),
                    'following_count': user_data.get('public_metrics', {}).get('following_count'),
                    'tweet_count': user_data.get('public_metrics', {}).get('tweet_count')
                }
            }
            
        except Exception as e:
            logger.error(f"Twitter profile fetch failed: {e}")
            return {'success': False, 'error': str(e)}


class GoogleCalendarIntegration:
    """Google Calendar integration for scheduling"""
    
    def __init__(self):
        self.client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', '')
        self.redirect_uri = getattr(settings, 'GOOGLE_REDIRECT_URI', '')
        
    def get_authorization_url(self, state: str = None) -> str:
        """Generate Google OAuth authorization URL"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'https://www.googleapis.com/auth/calendar.readonly',
            'response_type': 'code',
            'access_type': 'offline',
            'state': state or 'google_calendar_auth'
        }
        
        return f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        try:
            token_url = 'https://oauth2.googleapis.com/token'
            
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            return {
                'success': True,
                'access_token': token_data.get('access_token'),
                'refresh_token': token_data.get('refresh_token'),
                'expires_in': token_data.get('expires_in'),
                'token_type': token_data.get('token_type')
            }
            
        except Exception as e:
            logger.error(f"Google Calendar token exchange failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_availability(self, access_token: str, time_min: str, time_max: str) -> Dict[str, Any]:
        """Get user's calendar availability"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            
            url = 'https://www.googleapis.com/calendar/v3/calendars/primary/events'
            params = {
                'timeMin': time_min,
                'timeMax': time_max,
                'singleEvents': True,
                'orderBy': 'startTime'
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            events_data = response.json()
            events = events_data.get('items', [])
            
            # Process events to determine availability
            busy_times = []
            for event in events:
                start = event.get('start', {})
                end = event.get('end', {})
                
                if start.get('dateTime') and end.get('dateTime'):
                    busy_times.append({
                        'start': start['dateTime'],
                        'end': end['dateTime'],
                        'summary': event.get('summary', 'Busy')
                    })
            
            return {
                'success': True,
                'busy_times': busy_times,
                'total_events': len(events)
            }
            
        except Exception as e:
            logger.error(f"Google Calendar availability fetch failed: {e}")
            return {'success': False, 'error': str(e)}


class StripeIntegration:
    """Stripe payment processing integration"""
    
    def __init__(self):
        import stripe
        self.stripe = stripe
        self.stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
        self.publishable_key = getattr(settings, 'STRIPE_PUBLISHABLE_KEY', '')
        
    def create_customer(self, user: User, email: str = None) -> Dict[str, Any]:
        """Create Stripe customer"""
        try:
            customer = self.stripe.Customer.create(
                email=email or user.email,
                name=f"{user.first_name} {user.last_name}".strip(),
                metadata={'user_id': user.id}
            )
            
            return {
                'success': True,
                'customer_id': customer.id,
                'customer': customer
            }
            
        except Exception as e:
            logger.error(f"Stripe customer creation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_payment_intent(self, amount: int, currency: str = 'usd', 
                            customer_id: str = None, metadata: Dict = None) -> Dict[str, Any]:
        """Create payment intent"""
        try:
            intent = self.stripe.PaymentIntent.create(
                amount=amount,  # Amount in cents
                currency=currency,
                customer=customer_id,
                metadata=metadata or {},
                automatic_payment_methods={'enabled': True}
            )
            
            return {
                'success': True,
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            }
            
        except Exception as e:
            logger.error(f"Stripe payment intent creation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_subscription(self, customer_id: str, price_id: str, 
                          metadata: Dict = None) -> Dict[str, Any]:
        """Create subscription"""
        try:
            subscription = self.stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': price_id}],
                metadata=metadata or {},
                expand=['latest_invoice.payment_intent']
            )
            
            return {
                'success': True,
                'subscription_id': subscription.id,
                'status': subscription.status,
                'client_secret': subscription.latest_invoice.payment_intent.client_secret
            }
            
        except Exception as e:
            logger.error(f"Stripe subscription creation failed: {e}")
            return {'success': False, 'error': str(e)}


# Global instances
linkedin_integration = LinkedInIntegration()
github_integration = GitHubIntegration()
twitter_integration = TwitterIntegration()
google_calendar_integration = GoogleCalendarIntegration()
stripe_integration = StripeIntegration()
