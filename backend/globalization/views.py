"""
Globalization Views - Phase 10: Platform Maturity & Global Scale
API endpoints for internationalization and localization
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Q, Count, Sum
from datetime import timedelta
import logging

from .models import (
    Language, Currency, Region, Translation, TranslationKey,
    UserLocalization, LocalizedContent, ExchangeRate, LocalizationAnalytics
)
from .serializers import (
    LanguageSerializer, CurrencySerializer, RegionSerializer,
    TranslationSerializer, UserLocalizationSerializer,
    LocalizedContentSerializer, ExchangeRateSerializer
)
from .services import (
    get_translation_service, get_currency_service, get_localization_service, get_analytics_service
)

logger = logging.getLogger(__name__)


class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for supported languages
    """
    queryset = Language.objects.filter(is_active=True)
    serializer_class = LanguageSerializer
    permission_classes = [AllowAny]
    
    def list(self, request):
        """List all active languages"""
        languages = self.get_queryset()
        serializer = self.get_serializer(languages, many=True)
        
        # Track language usage
        if request.user.is_authenticated:
            user_lang = get_localization_service().get_user_localization(request.user).language.code
            get_analytics_service().track_language_usage(request.user, user_lang)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get most popular languages based on usage"""
        cache_key = "popular_languages"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return Response(cached_result)
        
        # Get usage stats from last 30 days
        try:
            stats = get_analytics_service().get_language_usage_stats(30)
            popular_languages = []
            
            # If no analytics data, return top languages by default
            if not stats:
                # Return default popular languages
                default_popular = ['en', 'es', 'fr', 'de', 'zh', 'ja', 'pt', 'it', 'ru', 'ar']
                for code in default_popular:
                    try:
                        language = Language.objects.get(code=code)
                        popular_languages.append({
                            'code': language.code,
                            'name': language.name,
                            'native_name': language.native_name,
                            'users': 0,
                            'page_views': 0
                        })
                    except Language.DoesNotExist:
                        continue
            else:
                for stat in stats[:10]:  # Top 10
                    try:
                        language = Language.objects.get(code=stat['language__code'])
                        popular_languages.append({
                            'code': language.code,
                            'name': language.name,
                            'native_name': language.native_name,
                            'users': stat['total_users'],
                            'page_views': stat['total_page_views']
                        })
                    except Language.DoesNotExist:
                        continue
        except Exception as e:
            # Fallback to default popular languages
            default_popular = ['en', 'es', 'fr', 'de', 'zh']
            popular_languages = []
            for code in default_popular:
                try:
                    language = Language.objects.get(code=code)
                    popular_languages.append({
                        'code': language.code,
                        'name': language.name,
                        'native_name': language.native_name,
                        'users': 0,
                        'page_views': 0
                    })
                except Language.DoesNotExist:
                    continue
        
        cache.set(cache_key, popular_languages, 3600)  # Cache for 1 hour
        return Response(popular_languages)


class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for supported currencies
    """
    queryset = Currency.objects.filter(is_active=True)
    serializer_class = CurrencySerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def rates(self, request):
        """Get current exchange rates"""
        base_currency = request.query_params.get('base', 'USD')
        target_currencies = request.query_params.get('targets', '').split(',')
        
        if not target_currencies or target_currencies == ['']:
            target_currencies = ['EUR', 'GBP', 'JPY', 'CAD', 'AUD']
        
        rates = {}
        for target in target_currencies:
            if target and target != base_currency:
                rate = get_currency_service().get_exchange_rate(base_currency, target)
                if rate:
                    rates[target] = str(rate)
        
        return Response({
            'base': base_currency,
            'rates': rates,
            'timestamp': timezone.now().isoformat()
        })
    
    @action(detail=False, methods=['post'])
    def convert(self, request):
        """Convert amount between currencies"""
        amount = request.data.get('amount')
        from_currency = request.data.get('from')
        to_currency = request.data.get('to')
        
        if not all([amount, from_currency, to_currency]):
            return Response(
                {'error': 'Amount, from, and to currencies are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from decimal import Decimal
            amount_decimal = Decimal(str(amount))
            converted = get_currency_service().convert_amount(amount_decimal, from_currency, to_currency)
            
            if converted is not None:
                return Response({
                    'original_amount': amount,
                    'from_currency': from_currency,
                    'to_currency': to_currency,
                    'converted_amount': str(converted),
                    'timestamp': timezone.now().isoformat()
                })
            else:
                return Response(
                    {'error': 'Conversion not available for these currencies'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except ValueError:
            return Response(
                {'error': 'Invalid amount format'},
                status=status.HTTP_400_BAD_REQUEST
            )


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for geographic regions
    """
    queryset = Region.objects.filter(is_active=True)
    serializer_class = RegionSerializer
    permission_classes = [AllowAny]


class TranslationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for translations
    """
    queryset = Translation.objects.filter(is_approved=True)
    serializer_class = TranslationSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        language = self.request.query_params.get('language')
        context = self.request.query_params.get('context')
        
        if language:
            queryset = queryset.filter(language__code=language)
        if context:
            queryset = queryset.filter(key__context=context)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def bulk(self, request):
        """Get multiple translations at once"""
        keys = request.query_params.get('keys', '').split(',')
        language = request.query_params.get('language', 'en')
        
        if not keys or keys == ['']:
            return Response(
                {'error': 'Keys parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        translations = get_translation_service().get_translations_bulk(keys, language)
        
        # Track translation request
        get_analytics_service().track_translation_request(language)
        
        return Response(translations)
    
    @action(detail=False, methods=['post'])
    def auto_translate(self, request):
        """Auto-translate text using external service"""
        text = request.data.get('text')
        target_language = request.data.get('target_language')
        source_language = request.data.get('source_language', 'en')
        
        if not all([text, target_language]):
            return Response(
                {'error': 'Text and target_language are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        translated_text = get_translation_service().auto_translate_text(
            text, target_language, source_language
        )
        
        if translated_text:
            # Track auto-translation
            get_analytics_service().track_translation_request(target_language, is_auto_translation=True)
            
            return Response({
                'original_text': text,
                'translated_text': translated_text,
                'source_language': source_language,
                'target_language': target_language,
                'is_auto_translated': True
            })
        else:
            return Response(
                {'error': 'Translation service unavailable'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class UserLocalizationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user localization preferences
    """
    serializer_class = UserLocalizationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserLocalization.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get or create user localization"""
        return get_localization_service().get_user_localization(self.request.user)
    
    def list(self, request):
        """Get current user's localization preferences"""
        localization = self.get_object()
        serializer = self.get_serializer(localization)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """Update user's localization preferences"""
        localization = self.get_object()
        serializer = self.get_serializer(localization, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def detect_locale(self, request):
        """Detect user's locale from browser/IP and update preferences"""
        # This would integrate with IP geolocation service
        # For now, return current settings
        localization = self.get_object()
        serializer = self.get_serializer(localization)
        
        return Response({
            'detected': False,  # Would be True if detection was successful
            'current_settings': serializer.data,
            'suggestions': {
                'language': 'en',
                'currency': 'USD',
                'region': 'NA'
            }
        })


class LocalizedContentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for localized content
    """
    queryset = LocalizedContent.objects.all()
    serializer_class = LocalizedContentSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        content_type = self.request.query_params.get('content_type')
        content_id = self.request.query_params.get('content_id')
        language = self.request.query_params.get('language')
        
        if content_type:
            queryset = queryset.filter(content_type=content_type)
        if content_id:
            queryset = queryset.filter(content_id=content_id)
        if language:
            queryset = queryset.filter(language__code=language)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def get_content(self, request):
        """Get localized content with fallback"""
        content_type = request.query_params.get('content_type')
        content_id = request.query_params.get('content_id')
        language = request.query_params.get('language', 'en')
        
        if not all([content_type, content_id]):
            return Response(
                {'error': 'content_type and content_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        content = get_localization_service().get_localized_content(
            content_type, content_id, language
        )
        
        if content:
            serializer = self.get_serializer(content)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Content not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
@permission_classes([AllowAny])
def localization_health(request):
    """
    Health check endpoint for localization services
    """
    health_data = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'services': {}
    }
    
    try:
        # Check translation service
        test_translation = get_translation_service().get_translation('test', 'en', 'test')
        health_data['services']['translation'] = {
            'status': 'healthy',
            'test_result': test_translation == 'test'
        }
    except Exception as e:
        health_data['services']['translation'] = {
            'status': 'error',
            'error': str(e)
        }
        health_data['status'] = 'degraded'
    
    try:
        # Check currency service
        test_rate = get_currency_service().get_exchange_rate('USD', 'EUR')
        health_data['services']['currency'] = {
            'status': 'healthy',
            'test_result': test_rate is not None
        }
    except Exception as e:
        health_data['services']['currency'] = {
            'status': 'error',
            'error': str(e)
        }
        health_data['status'] = 'degraded'
    
    # Check database connectivity
    try:
        language_count = Language.objects.count()
        health_data['services']['database'] = {
            'status': 'healthy',
            'languages_count': language_count
        }
    except Exception as e:
        health_data['services']['database'] = {
            'status': 'error',
            'error': str(e)
        }
        health_data['status'] = 'critical'
    
    status_code = status.HTTP_200_OK
    if health_data['status'] == 'degraded':
        status_code = status.HTTP_200_OK  # Still operational
    elif health_data['status'] == 'critical':
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return Response(health_data, status=status_code)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def localization_analytics(request):
    """
    Get localization analytics and usage statistics
    """
    days = int(request.query_params.get('days', 30))
    
    # Language usage stats
    language_stats = get_analytics_service().get_language_usage_stats(days)
    
    # Currency usage stats
    start_date = timezone.now().date() - timedelta(days=days)
    currency_stats = UserLocalization.objects.filter(
        updated_at__date__gte=start_date
    ).values('currency__code', 'currency__name').annotate(
        user_count=Count('user')
    ).order_by('-user_count')
    
    # Translation request stats
    translation_stats = LocalizationAnalytics.objects.filter(
        date__gte=start_date
    ).aggregate(
        total_requests=Sum('translation_requests'),
        auto_translations=Sum('auto_translations'),
        human_translations=Sum('human_translations')
    )
    
    return Response({
        'period_days': days,
        'language_usage': language_stats,
        'currency_usage': list(currency_stats),
        'translation_stats': translation_stats,
        'timestamp': timezone.now().isoformat()
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_exchange_rates(request):
    """
    Manually trigger exchange rate updates (admin only)
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        get_currency_service().update_exchange_rates()
        return Response({
            'status': 'success',
            'message': 'Exchange rates updated successfully',
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Exchange rate update failed: {str(e)}")
        return Response(
            {'error': 'Failed to update exchange rates', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
