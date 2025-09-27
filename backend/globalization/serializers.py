"""
Globalization Serializers - Phase 10: Platform Maturity & Global Scale
Serializers for internationalization and localization
"""
from rest_framework import serializers
from .models import (
    Language, Currency, Region, Translation, TranslationKey,
    UserLocalization, LocalizedContent, ExchangeRate, LocalizationAnalytics
)


class LanguageSerializer(serializers.ModelSerializer):
    """
    Serializer for Language model
    """
    class Meta:
        model = Language
        fields = [
            'code', 'name', 'native_name', 'is_rtl', 
            'completion_percentage'
        ]


class CurrencySerializer(serializers.ModelSerializer):
    """
    Serializer for Currency model
    """
    class Meta:
        model = Currency
        fields = [
            'code', 'name', 'symbol', 'decimal_places',
            'exchange_rate_to_usd', 'last_updated'
        ]


class RegionSerializer(serializers.ModelSerializer):
    """
    Serializer for Region model
    """
    default_language = LanguageSerializer(read_only=True)
    default_currency = CurrencySerializer(read_only=True)
    
    class Meta:
        model = Region
        fields = [
            'code', 'name', 'region_type', 'default_language',
            'default_currency', 'timezone_offset', 'data_residency_required',
            'gdpr_applicable', 'ccpa_applicable'
        ]


class TranslationKeySerializer(serializers.ModelSerializer):
    """
    Serializer for TranslationKey model
    """
    class Meta:
        model = TranslationKey
        fields = ['key', 'context', 'description']


class TranslationSerializer(serializers.ModelSerializer):
    """
    Serializer for Translation model
    """
    key = TranslationKeySerializer(read_only=True)
    language = LanguageSerializer(read_only=True)
    
    class Meta:
        model = Translation
        fields = [
            'id', 'key', 'language', 'value', 'is_approved',
            'created_at', 'updated_at'
        ]


class UserLocalizationSerializer(serializers.ModelSerializer):
    """
    Serializer for UserLocalization model
    """
    language = LanguageSerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    region = RegionSerializer(read_only=True)
    
    # Write-only fields for updates
    language_code = serializers.CharField(write_only=True, required=False)
    currency_code = serializers.CharField(write_only=True, required=False)
    region_code = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = UserLocalization
        fields = [
            'language', 'currency', 'region', 'timezone',
            'date_format', 'time_format', 'number_format',
            'auto_translate', 'show_original_text',
            'language_code', 'currency_code', 'region_code'
        ]
    
    def update(self, instance, validated_data):
        # Handle foreign key updates
        if 'language_code' in validated_data:
            try:
                language = Language.objects.get(code=validated_data.pop('language_code'))
                instance.language = language
            except Language.DoesNotExist:
                raise serializers.ValidationError({'language_code': 'Invalid language code'})
        
        if 'currency_code' in validated_data:
            try:
                currency = Currency.objects.get(code=validated_data.pop('currency_code'))
                instance.currency = currency
            except Currency.DoesNotExist:
                raise serializers.ValidationError({'currency_code': 'Invalid currency code'})
        
        if 'region_code' in validated_data:
            try:
                region = Region.objects.get(code=validated_data.pop('region_code'))
                instance.region = region
            except Region.DoesNotExist:
                raise serializers.ValidationError({'region_code': 'Invalid region code'})
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class LocalizedContentSerializer(serializers.ModelSerializer):
    """
    Serializer for LocalizedContent model
    """
    language = LanguageSerializer(read_only=True)
    
    class Meta:
        model = LocalizedContent
        fields = [
            'id', 'content_type', 'content_id', 'language',
            'title', 'content', 'metadata', 'is_machine_translated',
            'is_human_reviewed', 'quality_score', 'created_at', 'updated_at'
        ]


class ExchangeRateSerializer(serializers.ModelSerializer):
    """
    Serializer for ExchangeRate model
    """
    from_currency = CurrencySerializer(read_only=True)
    to_currency = CurrencySerializer(read_only=True)
    
    class Meta:
        model = ExchangeRate
        fields = [
            'from_currency', 'to_currency', 'rate', 'date', 'source'
        ]


class LocalizationAnalyticsSerializer(serializers.ModelSerializer):
    """
    Serializer for LocalizationAnalytics model
    """
    language = LanguageSerializer(read_only=True)
    region = RegionSerializer(read_only=True)
    
    class Meta:
        model = LocalizationAnalytics
        fields = [
            'date', 'language', 'region', 'active_users', 'page_views',
            'translation_requests', 'auto_translations', 'human_translations',
            'translation_accuracy', 'user_satisfaction'
        ]


class BulkTranslationSerializer(serializers.Serializer):
    """
    Serializer for bulk translation requests
    """
    keys = serializers.ListField(
        child=serializers.CharField(max_length=255),
        min_length=1,
        max_length=100
    )
    language = serializers.CharField(max_length=10, default='en')


class AutoTranslationSerializer(serializers.Serializer):
    """
    Serializer for auto-translation requests
    """
    text = serializers.CharField(max_length=5000)
    target_language = serializers.CharField(max_length=10)
    source_language = serializers.CharField(max_length=10, default='en')


class CurrencyConversionSerializer(serializers.Serializer):
    """
    Serializer for currency conversion requests
    """
    amount = serializers.DecimalField(max_digits=15, decimal_places=6)
    from_currency = serializers.CharField(max_length=3, source='from')
    to_currency = serializers.CharField(max_length=3, source='to')
    
    def validate_from_currency(self, value):
        if not Currency.objects.filter(code=value, is_active=True).exists():
            raise serializers.ValidationError("Invalid or inactive currency code")
        return value
    
    def validate_to_currency(self, value):
        if not Currency.objects.filter(code=value, is_active=True).exists():
            raise serializers.ValidationError("Invalid or inactive currency code")
        return value


class LocaleDetectionSerializer(serializers.Serializer):
    """
    Serializer for locale detection responses
    """
    detected = serializers.BooleanField()
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0, required=False)
    suggestions = serializers.DictField(required=False)
    current_settings = UserLocalizationSerializer(required=False)
