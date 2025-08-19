"""
Subscription and Monetization Models
Implements REQ-22, REQ-23, REQ-24, REQ-25: Revenue features
"""
from django.db import models
from accounts.models import CreatorProfile
from decimal import Decimal
import uuid
from datetime import datetime, timedelta

class SubscriptionPlan(models.Model):
    """Subscription plans for the platform (REQ-22, REQ-23)"""
    PLAN_TYPES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('pro', 'Pro'),
    ]
    
    name = models.CharField(max_length=50)
    plan_type = models.CharField(max_length=10, choices=PLAN_TYPES, unique=True)
    price_monthly = models.DecimalField(max_digits=8, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Features
    profile_views_limit = models.IntegerField(default=10)  # Free: 10, Basic: 100, Premium: unlimited
    collaboration_invites_limit = models.IntegerField(default=3)  # Free: 3, Basic: 20, Premium: unlimited
    ai_suggestions_limit = models.IntegerField(default=5)  # Free: 5, Basic: 50, Premium: unlimited
    portfolio_items_limit = models.IntegerField(default=5)  # Free: 5, Basic: 25, Premium: unlimited
    
    # Premium features
    can_send_invites_only = models.BooleanField(default=False)  # REQ-23
    has_visibility_controls = models.BooleanField(default=False)  # REQ-23
    has_auto_translation = models.BooleanField(default=False)  # REQ-23
    has_ai_portfolio_generator = models.BooleanField(default=False)  # REQ-25
    has_priority_support = models.BooleanField(default=False)
    has_analytics = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'subscription_plans'
        ordering = ['price_monthly']
    
    def __str__(self):
        return f"{self.name} - ${self.price_monthly}/month"

class UserSubscription(models.Model):
    """User subscription records (REQ-22)"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('pending', 'Pending'),
    ]
    
    BILLING_CYCLES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.OneToOneField(CreatorProfile, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CYCLES, default='monthly')
    
    # Billing details
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    next_billing_date = models.DateTimeField()
    
    # Payment tracking
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    last_payment_date = models.DateTimeField(null=True, blank=True)
    last_payment_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Usage tracking
    profile_views_used = models.IntegerField(default=0)
    invites_sent_count = models.IntegerField(default=0)
    ai_suggestions_used = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_subscriptions'
        indexes = [
            models.Index(fields=['status', 'next_billing_date']),
        ]
    
    def __str__(self):
        return f"{self.profile.display_name} - {self.plan.name}"
    
    def is_feature_available(self, feature: str) -> bool:
        """Check if a feature is available for current subscription"""
        if self.status != 'active':
            return False
        
        feature_map = {
            'send_invites_only': self.plan.can_send_invites_only,
            'visibility_controls': self.plan.has_visibility_controls,
            'auto_translation': self.plan.has_auto_translation,
            'ai_portfolio_generator': self.plan.has_ai_portfolio_generator,
            'priority_support': self.plan.has_priority_support,
            'analytics': self.plan.has_analytics,
        }
        
        return feature_map.get(feature, False)
    
    def can_use_feature(self, feature: str, current_usage: int = 0) -> bool:
        """Check if user can use a limited feature"""
        if self.status != 'active':
            return False
        
        limits = {
            'profile_views': self.plan.profile_views_limit,
            'collaboration_invites': self.plan.collaboration_invites_limit,
            'ai_suggestions': self.plan.ai_suggestions_limit,
            'portfolio_items': self.plan.portfolio_items_limit,
        }
        
        limit = limits.get(feature, 0)
        if limit == -1:  # Unlimited
            return True
        
        return current_usage < limit

class Advertisement(models.Model):
    """Advertisement system (REQ-24)"""
    AD_TYPES = [
        ('banner', 'Banner'),
        ('sidebar', 'Sidebar'),
        ('interstitial', 'Interstitial'),
        ('native', 'Native'),
    ]
    
    AD_CATEGORIES = [
        ('courses', 'Online Courses'),
        ('equipment', 'Equipment & Tools'),
        ('software', 'Software & Apps'),
        ('services', 'Creative Services'),
        ('events', 'Events & Workshops'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=500)
    ad_type = models.CharField(max_length=15, choices=AD_TYPES)
    category = models.CharField(max_length=15, choices=AD_CATEGORIES)
    
    # Targeting
    target_categories = models.JSONField(default=list)  # Artist categories to target
    target_experience_levels = models.JSONField(default=list)
    target_locations = models.JSONField(default=list)
    
    # Ad content
    image_url = models.URLField()
    click_url = models.URLField()
    call_to_action = models.CharField(max_length=50, default='Learn More')
    
    # Campaign details
    advertiser_name = models.CharField(max_length=100)
    budget_daily = models.DecimalField(max_digits=8, decimal_places=2)
    cost_per_click = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Status and scheduling
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Performance tracking
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    conversions = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'advertisements'
        indexes = [
            models.Index(fields=['is_active', 'start_date', 'end_date']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.advertiser_name})"
    
    @property
    def click_through_rate(self):
        if self.impressions == 0:
            return 0
        return (self.clicks / self.impressions) * 100

class AdImpression(models.Model):
    """Track ad impressions and clicks"""
    ad = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name='impression_records')
    profile = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='ad_impressions')
    
    was_clicked = models.BooleanField(default=False)
    impression_time = models.DateTimeField(auto_now_add=True)
    click_time = models.DateTimeField(null=True, blank=True)
    
    # Context
    page_context = models.CharField(max_length=50)  # 'browse', 'profile', 'chat', etc.
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'ad_impressions'
        unique_together = ['ad', 'profile', 'impression_time']

class PaymentTransaction(models.Model):
    """Payment transaction records"""
    TRANSACTION_TYPES = [
        ('subscription', 'Subscription Payment'),
        ('portfolio_generator', 'AI Portfolio Generator'),
        ('premium_feature', 'Premium Feature'),
        ('refund', 'Refund'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='transactions')
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Payment processor details
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_charge_id = models.CharField(max_length=100, blank=True, null=True)
    
    description = models.CharField(max_length=200)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payment_transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.profile.display_name} - {self.transaction_type} - ${self.amount}"
