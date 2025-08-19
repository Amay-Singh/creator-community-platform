"""
Subscription and Payment Models
Implements REQ-22-25: Revenue features - subscriptions, premium add-ons, payment processing
"""
import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from accounts.models import CreatorProfile

User = get_user_model()

class SubscriptionPlan(models.Model):
    """Subscription plans available on the platform"""
    
    PLAN_TYPES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    description = models.TextField()
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Features
    max_portfolio_items = models.IntegerField(default=10)
    max_collaborations = models.IntegerField(default=5)
    ai_generations_per_month = models.IntegerField(default=10)
    storage_gb = models.IntegerField(default=1)
    priority_support = models.BooleanField(default=False)
    advanced_analytics = models.BooleanField(default=False)
    custom_branding = models.BooleanField(default=False)
    api_access = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscription_plans'
        ordering = ['price_monthly']
    
    def __str__(self):
        return f"{self.name} - ${self.price_monthly}/month"

class UserSubscription(models.Model):
    """User's current subscription"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
        ('trial', 'Trial'),
    ]
    
    BILLING_CYCLES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLES, default='monthly')
    
    # Subscription dates
    started_at = models.DateTimeField(default=timezone.now)
    current_period_start = models.DateTimeField(default=timezone.now)
    current_period_end = models.DateTimeField()
    cancelled_at = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)
    
    # Payment info
    stripe_subscription_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Usage tracking
    portfolio_items_used = models.IntegerField(default=0)
    collaborations_used = models.IntegerField(default=0)
    ai_generations_used = models.IntegerField(default=0)
    storage_used_gb = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_subscriptions'
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"
    
    @property
    def is_active(self):
        return self.status == 'active' and self.current_period_end > timezone.now()
    
    @property
    def days_remaining(self):
        if self.current_period_end > timezone.now():
            return (self.current_period_end - timezone.now()).days
        return 0

class PremiumAddon(models.Model):
    """Premium add-ons available for purchase"""
    
    ADDON_TYPES = [
        ('storage', 'Extra Storage'),
        ('ai_credits', 'AI Generation Credits'),
        ('collaborations', 'Extra Collaborations'),
        ('analytics', 'Advanced Analytics'),
        ('priority_support', 'Priority Support'),
        ('custom_domain', 'Custom Domain'),
        ('white_label', 'White Label Branding'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    addon_type = models.CharField(max_length=30, choices=ADDON_TYPES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Addon specifications
    storage_gb = models.IntegerField(default=0)
    ai_credits = models.IntegerField(default=0)
    collaboration_slots = models.IntegerField(default=0)
    duration_days = models.IntegerField(default=30)  # How long the addon lasts
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'premium_addons'
    
    def __str__(self):
        return f"{self.name} - ${self.price}"

class UserAddon(models.Model):
    """User's purchased add-ons"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addons')
    addon = models.ForeignKey(PremiumAddon, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    purchased_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    
    # Usage tracking
    storage_used_gb = models.FloatField(default=0.0)
    ai_credits_used = models.IntegerField(default=0)
    collaborations_used = models.IntegerField(default=0)
    
    stripe_payment_intent_id = models.CharField(max_length=255, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_addons'
    
    def __str__(self):
        return f"{self.user.email} - {self.addon.name}"
    
    @property
    def is_active(self):
        return self.status == 'active' and self.expires_at > timezone.now()

class PaymentHistory(models.Model):
    """Payment transaction history"""
    
    PAYMENT_TYPES = [
        ('subscription', 'Subscription'),
        ('addon', 'Add-on'),
        ('one_time', 'One-time Payment'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Related objects
    subscription = models.ForeignKey(UserSubscription, on_delete=models.SET_NULL, null=True, blank=True)
    addon = models.ForeignKey(UserAddon, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Payment gateway info
    stripe_payment_intent_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_charge_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Metadata
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payment_history'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - ${self.amount} ({self.status})"

class UsageLimit(models.Model):
    """Track usage limits for different features"""
    
    FEATURE_TYPES = [
        ('portfolio_items', 'Portfolio Items'),
        ('collaborations', 'Collaborations'),
        ('ai_generations', 'AI Generations'),
        ('storage', 'Storage'),
        ('api_calls', 'API Calls'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usage_limits')
    feature_type = models.CharField(max_length=30, choices=FEATURE_TYPES)
    
    limit_value = models.IntegerField()  # The limit
    current_usage = models.IntegerField(default=0)  # Current usage
    
    # Reset period
    reset_period = models.CharField(max_length=20, default='monthly')  # monthly, yearly, never
    last_reset = models.DateTimeField(default=timezone.now)
    next_reset = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'usage_limits'
        unique_together = ['user', 'feature_type']
    
    def __str__(self):
        return f"{self.user.email} - {self.feature_type}: {self.current_usage}/{self.limit_value}"
    
    @property
    def is_exceeded(self):
        return self.current_usage >= self.limit_value
    
    @property
    def usage_percentage(self):
        if self.limit_value == 0:
            return 100
        return (self.current_usage / self.limit_value) * 100

class PromoCode(models.Model):
    """Promotional codes for discounts"""
    
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed_amount', 'Fixed Amount'),
        ('free_trial', 'Free Trial Extension'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Validity
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField()
    
    # Usage limits
    max_uses = models.IntegerField(default=1)
    current_uses = models.IntegerField(default=0)
    
    # Applicable plans
    applicable_plans = models.ManyToManyField(SubscriptionPlan, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'promo_codes'
    
    def __str__(self):
        return f"{self.code} - {self.discount_value}{'%' if self.discount_type == 'percentage' else '$'}"
    
    @property
    def is_valid(self):
        now = timezone.now()
        return (self.is_active and 
                self.valid_from <= now <= self.valid_until and
                self.current_uses < self.max_uses)

class PromoCodeUsage(models.Model):
    """Track promo code usage"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='promo_usages')
    payment = models.ForeignKey(PaymentHistory, on_delete=models.CASCADE, null=True, blank=True)
    
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'promo_code_usage'
        unique_together = ['promo_code', 'user']  # One use per user per code
    
    def __str__(self):
        return f"{self.user.email} used {self.promo_code.code}"
