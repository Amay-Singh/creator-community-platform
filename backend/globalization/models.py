"""
Globalization Models - Phase 10: Platform Maturity & Global Scale
Comprehensive internationalization and localization support
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils import timezone
from decimal import Decimal
import json

User = get_user_model()


class Language(models.Model):
    """
    Supported languages for the platform
    """
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('zh', 'Chinese (Simplified)'),
        ('zh-tw', 'Chinese (Traditional)'),
        ('ja', 'Japanese'),
        ('ko', 'Korean'),
        ('pt', 'Portuguese'),
        ('it', 'Italian'),
        ('ru', 'Russian'),
        ('ar', 'Arabic'),
        ('he', 'Hebrew'),
        ('hi', 'Hindi'),
        ('th', 'Thai'),
    ]
    
    code = models.CharField(max_length=10, primary_key=True, choices=LANGUAGE_CHOICES)
    name = models.CharField(max_length=100)
    native_name = models.CharField(max_length=100)
    is_rtl = models.BooleanField(default=False)  # Right-to-left languages
    is_active = models.BooleanField(default=True)
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    class Meta:
        db_table = 'globalization_language'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Currency(models.Model):
    """
    Supported currencies for multi-currency support
    """
    code = models.CharField(max_length=3, primary_key=True)  # ISO 4217 currency codes
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    decimal_places = models.IntegerField(default=2)
    is_active = models.BooleanField(default=True)
    exchange_rate_to_usd = models.DecimalField(max_digits=10, decimal_places=6, default=1.000000)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'globalization_currency'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Region(models.Model):
    """
    Geographic regions for localization and compliance
    """
    REGION_CHOICES = [
        ('NA', 'North America'),
        ('SA', 'South America'),
        ('EU', 'Europe'),
        ('AS', 'Asia'),
        ('AF', 'Africa'),
        ('OC', 'Oceania'),
        ('ME', 'Middle East'),
    ]
    
    code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)
    region_type = models.CharField(max_length=2, choices=REGION_CHOICES)
    default_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='default_regions')
    default_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='default_regions')
    timezone_offset = models.IntegerField(default=0)  # UTC offset in minutes
    is_active = models.BooleanField(default=True)
    
    # Compliance and regulatory information
    data_residency_required = models.BooleanField(default=False)
    gdpr_applicable = models.BooleanField(default=False)
    ccpa_applicable = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'globalization_region'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class TranslationKey(models.Model):
    """
    Translation keys for internationalization
    """
    CONTEXT_CHOICES = [
        ('ui', 'User Interface'),
        ('email', 'Email Templates'),
        ('notification', 'Notifications'),
        ('error', 'Error Messages'),
        ('help', 'Help Text'),
        ('marketing', 'Marketing Content'),
        ('legal', 'Legal Documents'),
    ]
    
    key = models.CharField(max_length=255, unique=True, validators=[MinLengthValidator(3)])
    context = models.CharField(max_length=20, choices=CONTEXT_CHOICES, default='ui')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'globalization_translation_key'
        ordering = ['key']
    
    def __str__(self):
        return self.key


class Translation(models.Model):
    """
    Translations for different languages
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.ForeignKey(TranslationKey, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='translations')
    value = models.TextField()
    is_approved = models.BooleanField(default=False)
    translator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'globalization_translation'
        unique_together = ['key', 'language']
        ordering = ['key__key', 'language__code']
    
    def __str__(self):
        return f"{self.key.key} ({self.language.code})"


class UserLocalization(models.Model):
    """
    User-specific localization preferences
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='localization')
    language = models.ForeignKey(Language, on_delete=models.CASCADE, default='en')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, default='USD')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    date_format = models.CharField(max_length=20, default='YYYY-MM-DD')
    time_format = models.CharField(max_length=20, default='24h')
    number_format = models.CharField(max_length=20, default='1,234.56')
    
    # Content preferences
    auto_translate = models.BooleanField(default=True)
    show_original_text = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'globalization_user_localization'
    
    def __str__(self):
        return f"{self.user.username} - {self.language.code}"


class LocalizedContent(models.Model):
    """
    Localized content for dynamic content
    """
    CONTENT_TYPES = [
        ('project_description', 'Project Description'),
        ('skill_name', 'Skill Name'),
        ('category_name', 'Category Name'),
        ('notification_template', 'Notification Template'),
        ('email_template', 'Email Template'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_type = models.CharField(max_length=50, choices=CONTENT_TYPES)
    content_id = models.CharField(max_length=100)  # ID of the original content
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    
    # Translation quality
    is_machine_translated = models.BooleanField(default=False)
    is_human_reviewed = models.BooleanField(default=False)
    quality_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'globalization_localized_content'
        unique_together = ['content_type', 'content_id', 'language']
        ordering = ['content_type', 'content_id', 'language__code']
    
    def __str__(self):
        return f"{self.content_type}:{self.content_id} ({self.language.code})"


class ExchangeRate(models.Model):
    """
    Currency exchange rates for multi-currency support
    """
    from_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='exchange_rates_from')
    to_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='exchange_rates_to')
    rate = models.DecimalField(max_digits=10, decimal_places=6)
    date = models.DateField()
    source = models.CharField(max_length=50, default='api')  # Source of exchange rate
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'globalization_exchange_rate'
        unique_together = ['from_currency', 'to_currency', 'date']
        ordering = ['-date', 'from_currency', 'to_currency']
    
    def __str__(self):
        return f"{self.from_currency.code} -> {self.to_currency.code}: {self.rate}"


class LocalizationAnalytics(models.Model):
    """
    Analytics for localization usage and effectiveness
    """
    date = models.DateField()
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True)
    
    # Usage metrics
    active_users = models.IntegerField(default=0)
    page_views = models.IntegerField(default=0)
    translation_requests = models.IntegerField(default=0)
    auto_translations = models.IntegerField(default=0)
    human_translations = models.IntegerField(default=0)
    
    # Quality metrics
    translation_accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    user_satisfaction = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'globalization_localization_analytics'
        unique_together = ['date', 'language', 'region']
        ordering = ['-date', 'language__code']
    
    def __str__(self):
        return f"{self.date} - {self.language.code} ({self.active_users} users)"
