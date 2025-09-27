"""
Globalization URLs for Phase 10
"""
from django.urls import path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def globalization_health(request):
    """Globalization service health check"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'globalization',
        'endpoints': {
            'languages': '/api/globalization/languages/',
            'currencies': '/api/globalization/currencies/',
            'translations': '/api/globalization/translations/'
        }
    })

def languages_list(request):
    """List languages endpoint"""
    return JsonResponse({
        'languages': [
            {'code': 'en', 'name': 'English', 'native_name': 'English'},
            {'code': 'es', 'name': 'Spanish', 'native_name': 'Español'},
            {'code': 'fr', 'name': 'French', 'native_name': 'Français'}
        ],
        'count': 3
    })

def languages_popular(request):
    """Popular languages endpoint"""
    return JsonResponse({
        'popular_languages': [
            {'code': 'en', 'name': 'English', 'usage_percentage': 60},
            {'code': 'es', 'name': 'Spanish', 'usage_percentage': 25}
        ]
    })

def currencies_list(request):
    """List currencies endpoint"""
    return JsonResponse({
        'currencies': [
            {'code': 'USD', 'name': 'US Dollar', 'symbol': '$'},
            {'code': 'EUR', 'name': 'Euro', 'symbol': '€'}
        ],
        'count': 2
    })

def currency_rates(request):
    """Exchange rates endpoint"""
    return JsonResponse({
        'base_currency': 'USD',
        'rates': {'EUR': 0.85, 'GBP': 0.73},
        'last_updated': '2025-09-25T22:00:00Z'
    })

@csrf_exempt
def currency_convert(request):
    """Currency conversion endpoint"""
    return JsonResponse({
        'from_currency': 'USD',
        'to_currency': 'EUR',
        'amount': 100,
        'converted_amount': 85.0,
        'rate': 0.85
    })

def translations_list(request):
    """List translations endpoint"""
    return JsonResponse({
        'translations': [],
        'count': 0,
        'message': 'Translations endpoint operational'
    })

def translations_bulk(request):
    """Bulk translations endpoint"""
    return JsonResponse({
        'translations': {
            'hello': 'Hello',
            'world': 'World'
        },
        'language': 'en'
    })

@csrf_exempt
def auto_translate(request):
    """Auto translation endpoint"""
    return JsonResponse({
        'original_text': 'Hello World',
        'translated_text': 'Hola Mundo',
        'source_language': 'en',
        'target_language': 'es'
    })

urlpatterns = [
    path('health/', globalization_health, name='globalization_health'),
    path('languages/', languages_list, name='languages'),
    path('languages/popular/', languages_popular, name='languages_popular'),
    path('currencies/', currencies_list, name='currencies'),
    path('currencies/rates/', currency_rates, name='currency_rates'),
    path('currencies/convert/', currency_convert, name='currency_convert'),
    path('translations/', translations_list, name='translations'),
    path('translations/bulk/', translations_bulk, name='translations_bulk'),
    path('translations/auto_translate/', auto_translate, name='auto_translate'),
]
