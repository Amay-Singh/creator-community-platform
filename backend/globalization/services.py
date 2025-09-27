"""
Globalization Services - Phase 10: Platform Maturity & Global Scale
Translation, localization, and currency conversion services
"""
import logging
import requests
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from datetime import date, datetime, timedelta
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import (
    Language, Currency, Region, Translation, TranslationKey,
    UserLocalization, LocalizedContent, ExchangeRate, LocalizationAnalytics
)

User = get_user_model()
logger = logging.getLogger(__name__)


class TranslationService:
    """
    Service for managing translations and localization
    """
    
    def __init__(self):
        self.cache_timeout = 3600  # 1 hour
        self._supported_languages = None
    
    @property
    def supported_languages(self):
        """Lazy load supported languages to avoid database queries during Django startup"""
        if self._supported_languages is None:
            try:
                self._supported_languages = list(Language.objects.filter(is_active=True).values_list('code', flat=True))
            except Exception:
                # Fallback during migrations or when tables don't exist yet
                self._supported_languages = ['en', 'es', 'fr', 'de', 'zh', 'ja', 'ko', 'pt', 'it', 'ru']
        return self._supported_languages
    
    def get_translation(self, key: str, language_code: str, default: str = None) -> str:
        """
        Get translation for a specific key and language
        """
        cache_key = f"translation_{key}_{language_code}"
        cached_translation = cache.get(cache_key)
        
        if cached_translation:
            return cached_translation
        
        try:
            translation_key = TranslationKey.objects.get(key=key)
            translation = Translation.objects.get(
                key=translation_key,
                language_id=language_code,
                is_approved=True
            )
            
            result = translation.value
            cache.set(cache_key, result, self.cache_timeout)
            return result
            
        except (TranslationKey.DoesNotExist, Translation.DoesNotExist):
            logger.warning(f"Translation not found: {key} ({language_code})")
            return default or key
    
    def get_translations_bulk(self, keys: List[str], language_code: str) -> Dict[str, str]:
        """
        Get multiple translations at once for better performance
        """
        translations = {}
        missing_keys = []
        
        # Check cache first
        for key in keys:
            cache_key = f"translation_{key}_{language_code}"
            cached_value = cache.get(cache_key)
            if cached_value:
                translations[key] = cached_value
            else:
                missing_keys.append(key)
        
        # Fetch missing translations from database
        if missing_keys:
            db_translations = Translation.objects.select_related('key', 'language').filter(
                key__key__in=missing_keys,
                language_id=language_code,
                is_approved=True
            )
            
            for translation in db_translations:
                key = translation.key.key
                value = translation.value
                translations[key] = value
                
                # Cache the result
                cache_key = f"translation_{key}_{language_code}"
                cache.set(cache_key, value, self.cache_timeout)
        
        # Fill in missing translations with keys
        for key in keys:
            if key not in translations:
                translations[key] = key
        
        return translations
    
    
    def auto_translate_text(self, text: str, target_language: str, source_language: str = 'en') -> Optional[str]:
        """
        Auto-translate text using external translation service
        """
        if not text or source_language == target_language:
            return text
        
        cache_key = f"auto_translate_{hash(text)}_{source_language}_{target_language}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        try:
            # Use Google Translate API (placeholder - implement with actual API)
            translated_text = self._call_translation_api(text, source_language, target_language)
            
            if translated_text:
                cache.set(cache_key, translated_text, self.cache_timeout * 24)  # Cache for 24 hours
                return translated_text
                
        except Exception as e:
            logger.error(f"Auto-translation failed: {str(e)}")
        
        return None
    
    def _call_translation_api(self, text: str, source: str, target: str) -> Optional[str]:
        """
        Call external translation API (Google Translate, DeepL, etc.)
        """
        # Placeholder implementation - integrate with actual translation service
        # This would use Google Translate API, DeepL API, or similar service
        
        api_key = getattr(settings, 'GOOGLE_TRANSLATE_API_KEY', None)
        if not api_key:
            logger.warning("Translation API key not configured - using fallback")
            # Fallback: return a simple mock translation for demo purposes
            return f"[{target}] {text}"
        
        try:
            # Mock implementation - replace with actual API call
            url = "https://translation.googleapis.com/language/translate/v2"
            params = {
                'key': api_key,
                'q': text,
                'source': source,
                'target': target,
                'format': 'text'
            }
            
            response = requests.post(url, data=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if 'data' in result and 'translations' in result['data']:
                return result['data']['translations'][0]['translatedText']
                
        except Exception as e:
            logger.error(f"Translation API call failed: {str(e)}")
        
        return None
    
    def create_localized_content(self, content_type: str, content_id: str, 
                               title: str, content: str, language_code: str,
                               auto_translate_to: List[str] = None) -> LocalizedContent:
        """
        Create localized content and optionally auto-translate to other languages
        """
        # Create the main localized content
        localized_content = LocalizedContent.objects.create(
            content_type=content_type,
            content_id=content_id,
            language_id=language_code,
            title=title,
            content=content,
            is_machine_translated=False,
            is_human_reviewed=True
        )
        
        # Auto-translate to other languages if requested
        if auto_translate_to:
            for target_lang in auto_translate_to:
                if target_lang != language_code:
                    translated_title = self.auto_translate_text(title, target_lang, language_code)
                    translated_content = self.auto_translate_text(content, target_lang, language_code)
                    
                    if translated_title and translated_content:
                        LocalizedContent.objects.create(
                            content_type=content_type,
                            content_id=content_id,
                            language_id=target_lang,
                            title=translated_title,
                            content=translated_content,
                            is_machine_translated=True,
                            is_human_reviewed=False
                        )
        
        return localized_content
    
    def get_user_language(self, user: User) -> str:
        """
        Get user's preferred language
        """
        try:
            user_localization = UserLocalization.objects.get(user=user)
            return user_localization.language.code
        except UserLocalization.DoesNotExist:
            return 'en'  # Default to English


class CurrencyService:
    """
    Service for currency conversion and multi-currency support
    """
    
    def __init__(self):
        self.cache_timeout = 3600  # 1 hour
        self.base_currency = 'USD'
    
    def get_exchange_rate(self, from_currency: str, to_currency: str, date_requested: date = None) -> Optional[Decimal]:
        """
        Get exchange rate between two currencies
        """
        if from_currency == to_currency:
            return Decimal('1.0')
        
        if date_requested is None:
            date_requested = timezone.now().date()
        
        cache_key = f"exchange_rate_{from_currency}_{to_currency}_{date_requested}"
        cached_rate = cache.get(cache_key)
        
        if cached_rate:
            return Decimal(str(cached_rate))
        
        try:
            # Try to get exact date first
            exchange_rate = ExchangeRate.objects.get(
                from_currency_id=from_currency,
                to_currency_id=to_currency,
                date=date_requested
            )
            
            rate = exchange_rate.rate
            cache.set(cache_key, str(rate), self.cache_timeout)
            return rate
            
        except ExchangeRate.DoesNotExist:
            # Try to get the most recent rate
            try:
                exchange_rate = ExchangeRate.objects.filter(
                    from_currency_id=from_currency,
                    to_currency_id=to_currency,
                    date__lte=date_requested
                ).order_by('-date').first()
                
                if exchange_rate:
                    rate = exchange_rate.rate
                    cache.set(cache_key, str(rate), self.cache_timeout // 2)  # Shorter cache for older rates
                    return rate
                    
            except ExchangeRate.DoesNotExist:
                pass
        
        # If no rate found, try to fetch from external API
        rate = self._fetch_exchange_rate_from_api(from_currency, to_currency)
        if rate:
            # Store the fetched rate
            ExchangeRate.objects.create(
                from_currency_id=from_currency,
                to_currency_id=to_currency,
                rate=rate,
                date=date_requested,
                source='api'
            )
            cache.set(cache_key, str(rate), self.cache_timeout)
            return rate
        
        logger.warning(f"Exchange rate not found: {from_currency} -> {to_currency}")
        return None
    
    def convert_amount(self, amount: Decimal, from_currency: str, to_currency: str) -> Optional[Decimal]:
        """
        Convert amount from one currency to another
        """
        if from_currency == to_currency:
            return amount
        
        exchange_rate = self.get_exchange_rate(from_currency, to_currency)
        if exchange_rate:
            return amount * exchange_rate
        
        return None
    
    def _fetch_exchange_rate_from_api(self, from_currency: str, to_currency: str) -> Optional[Decimal]:
        """
        Fetch exchange rate from external API
        """
        api_key = getattr(settings, 'EXCHANGE_RATE_API_KEY', None)
        if not api_key:
            logger.warning("Exchange rate API key not configured - using fallback rates")
            # Fallback: return mock exchange rates for demo purposes
            mock_rates = {
                ('USD', 'EUR'): Decimal('0.85'),
                ('USD', 'GBP'): Decimal('0.75'),
                ('USD', 'JPY'): Decimal('110.0'),
                ('USD', 'CAD'): Decimal('1.25'),
                ('USD', 'AUD'): Decimal('1.35'),
                ('EUR', 'USD'): Decimal('1.18'),
                ('GBP', 'USD'): Decimal('1.33'),
                ('JPY', 'USD'): Decimal('0.009'),
                ('CAD', 'USD'): Decimal('0.80'),
                ('AUD', 'USD'): Decimal('0.74'),
            }
            
            rate = mock_rates.get((from_currency, to_currency))
            if rate:
                return rate
            
            # Try reverse rate
            reverse_rate = mock_rates.get((to_currency, from_currency))
            if reverse_rate:
                return Decimal('1.0') / reverse_rate
                
            return None
        
        try:
            # Using exchangerate-api.com as example
            url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency}/{to_currency}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('result') == 'success':
                return Decimal(str(data['conversion_rate']))
                
        except Exception as e:
            logger.error(f"Exchange rate API call failed: {str(e)}")
        
        return None
    
    def update_exchange_rates(self):
        """
        Update exchange rates from external API
        """
        currencies = Currency.objects.filter(is_active=True)
        today = timezone.now().date()
        
        for from_currency in currencies:
            for to_currency in currencies:
                if from_currency.code != to_currency.code:
                    # Check if we already have today's rate
                    if not ExchangeRate.objects.filter(
                        from_currency=from_currency,
                        to_currency=to_currency,
                        date=today
                    ).exists():
                        rate = self._fetch_exchange_rate_from_api(from_currency.code, to_currency.code)
                        if rate:
                            ExchangeRate.objects.create(
                                from_currency=from_currency,
                                to_currency=to_currency,
                                rate=rate,
                                date=today,
                                source='api'
                            )


class LocalizationService:
    """
    Service for user localization preferences and regional settings
    """
    
    def __init__(self):
        self.translation_service = TranslationService()
        self.currency_service = CurrencyService()
    
    def get_user_localization(self, user: User) -> UserLocalization:
        """
        Get or create user localization preferences
        """
        localization, created = UserLocalization.objects.get_or_create(
            user=user,
            defaults={
                'language_id': 'en',
                'currency_id': 'USD',
                'timezone': 'UTC'
            }
        )
        
        if created:
            # Set defaults based on user's detected location or preferences
            self._set_default_localization(localization)
        
        return localization
    
    def update_user_localization(self, user: User, **kwargs) -> UserLocalization:
        """
        Update user localization preferences
        """
        localization = self.get_user_localization(user)
        
        for key, value in kwargs.items():
            if hasattr(localization, key):
                setattr(localization, key, value)
        
        localization.save()
        
        # Clear user-specific caches
        self._clear_user_caches(user)
        
        return localization
    
    def _set_default_localization(self, localization: UserLocalization):
        """
        Set default localization based on user's region or other factors
        """
        # This could be enhanced with IP geolocation or other detection methods
        # For now, keep defaults
        pass
    
    def _clear_user_caches(self, user: User):
        """
        Clear user-specific localization caches
        """
        user_id = user.id
        cache_patterns = [
            f"user_translations_{user_id}_*",
            f"user_currency_{user_id}_*",
            f"user_localization_{user_id}"
        ]
        
        for pattern in cache_patterns:
            cache.delete_pattern(pattern)
    
    def format_currency(self, amount: Decimal, currency_code: str, user: User = None) -> str:
        """
        Format currency amount according to user's locale
        """
        try:
            currency = Currency.objects.get(code=currency_code)
            
            # Convert to user's preferred currency if different
            if user:
                user_localization = self.get_user_localization(user)
                if user_localization.currency.code != currency_code:
                    converted_amount = self.currency_service.convert_amount(
                        amount, currency_code, user_localization.currency.code
                    )
                    if converted_amount:
                        amount = converted_amount
                        currency = user_localization.currency
            
            # Format according to currency's decimal places
            formatted_amount = f"{amount:.{currency.decimal_places}f}"
            
            return f"{currency.symbol}{formatted_amount}"
            
        except Currency.DoesNotExist:
            return f"{amount:.2f}"
    
    def get_localized_content(self, content_type: str, content_id: str, 
                            language_code: str = 'en') -> Optional[LocalizedContent]:
        """
        Get localized content for specific type and language
        """
        try:
            return LocalizedContent.objects.get(
                content_type=content_type,
                content_id=content_id,
                language_id=language_code
            )
        except LocalizedContent.DoesNotExist:
            # Try to get English version as fallback
            if language_code != 'en':
                try:
                    return LocalizedContent.objects.get(
                        content_type=content_type,
                        content_id=content_id,
                        language_id='en'
                    )
                except LocalizedContent.DoesNotExist:
                    pass
        
        return None


class LocalizationAnalyticsService:
    """
    Service for tracking localization usage and effectiveness
    """
    
    def track_language_usage(self, user: User, language_code: str, page_views: int = 1):
        """
        Track language usage for analytics
        """
        today = timezone.now().date()
        
        # Get user's region if available
        try:
            user_localization = UserLocalization.objects.get(user=user)
            region = user_localization.region
        except UserLocalization.DoesNotExist:
            region = None
        
        # Update or create analytics record
        analytics, created = LocalizationAnalytics.objects.get_or_create(
            date=today,
            language_id=language_code,
            region=region,
            defaults={
                'active_users': 0,
                'page_views': 0,
                'translation_requests': 0
            }
        )
        
        if created:
            analytics.active_users = 1
        else:
            # Check if this user was already counted today
            cache_key = f"user_counted_{user.id}_{today}_{language_code}"
            if not cache.get(cache_key):
                analytics.active_users += 1
                cache.set(cache_key, True, 86400)  # 24 hours
        
        analytics.page_views += page_views
        analytics.save()
    
    def track_translation_request(self, language_code: str, is_auto_translation: bool = False):
        """
        Track translation requests for analytics
        """
        today = timezone.now().date()
        
        analytics, created = LocalizationAnalytics.objects.get_or_create(
            date=today,
            language_id=language_code,
            defaults={
                'active_users': 0,
                'page_views': 0,
                'translation_requests': 0,
                'auto_translations': 0,
                'human_translations': 0
            }
        )
        
        analytics.translation_requests += 1
        
        if is_auto_translation:
            analytics.auto_translations += 1
        else:
            analytics.human_translations += 1
        
        analytics.save()
    
    def get_language_usage_stats(self, days: int = 30) -> Dict:
        """
        Get language usage statistics for the specified period
        """
        start_date = timezone.now().date() - timedelta(days=days)
        
        stats = LocalizationAnalytics.objects.filter(
            date__gte=start_date
        ).values('language__code', 'language__name').annotate(
            total_users=models.Sum('active_users'),
            total_page_views=models.Sum('page_views'),
            total_translations=models.Sum('translation_requests')
        ).order_by('-total_users')
        
        return list(stats)
    
    def track_language_usage(self, user, language_code: str):
        """
        Track language usage for analytics
        """
        # For now, just pass - in production this would update analytics
        pass
    
    def track_translation_request(self, language_code: str, is_auto_translation: bool = False):
        """
        Track translation requests for analytics
        """
        # For now, just pass - in production this would update analytics
        pass


# Service instances (lazy-loaded to avoid database access during startup)
_translation_service = None
_currency_service = None
_localization_service = None
_analytics_service = None

def get_translation_service():
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService()
    return _translation_service

def get_currency_service():
    global _currency_service
    if _currency_service is None:
        _currency_service = CurrencyService()
    return _currency_service

def get_localization_service():
    global _localization_service
    if _localization_service is None:
        _localization_service = LocalizationService()
    return _localization_service

def get_analytics_service():
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = LocalizationAnalyticsService()
    return _analytics_service

# Backward compatibility
translation_service = get_translation_service
currency_service = get_currency_service
localization_service = get_localization_service
analytics_service = get_analytics_service
