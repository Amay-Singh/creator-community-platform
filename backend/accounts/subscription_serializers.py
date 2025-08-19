"""
Subscription and Payment Serializers
Implements REQ-22-25: Revenue features - subscriptions, premium add-ons, payment processing
"""
from rest_framework import serializers
from .subscription_models import (
    SubscriptionPlan, UserSubscription, PremiumAddon, UserAddon,
    PaymentHistory, UsageLimit, PromoCode
)

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for subscription plans"""
    yearly_savings = serializers.SerializerMethodField()
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'plan_type', 'description', 'price_monthly', 'price_yearly',
            'max_portfolio_items', 'max_collaborations', 'ai_generations_per_month',
            'storage_gb', 'priority_support', 'advanced_analytics', 'custom_branding',
            'api_access', 'yearly_savings'
        ]
    
    def get_yearly_savings(self, obj):
        if obj.price_yearly > 0:
            return float(obj.price_monthly * 12 - obj.price_yearly)
        return 0

class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for user subscriptions"""
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    plan_type = serializers.CharField(source='plan.plan_type', read_only=True)
    days_remaining = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = UserSubscription
        fields = [
            'id', 'plan_name', 'plan_type', 'status', 'billing_cycle',
            'started_at', 'current_period_start', 'current_period_end',
            'days_remaining', 'is_active', 'portfolio_items_used',
            'collaborations_used', 'ai_generations_used', 'storage_used_gb'
        ]
        read_only_fields = ['id', 'started_at']

class CreateSubscriptionSerializer(serializers.Serializer):
    """Serializer for creating subscriptions"""
    plan_id = serializers.UUIDField()
    billing_cycle = serializers.ChoiceField(choices=['monthly', 'yearly'])
    promo_code = serializers.CharField(max_length=50, required=False)

class PremiumAddonSerializer(serializers.ModelSerializer):
    """Serializer for premium add-ons"""
    
    class Meta:
        model = PremiumAddon
        fields = [
            'id', 'name', 'addon_type', 'description', 'price',
            'storage_gb', 'ai_credits', 'collaboration_slots', 'duration_days'
        ]

class UserAddonSerializer(serializers.ModelSerializer):
    """Serializer for user add-ons"""
    addon_name = serializers.CharField(source='addon.name', read_only=True)
    addon_type = serializers.CharField(source='addon.addon_type', read_only=True)
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = UserAddon
        fields = [
            'id', 'addon_name', 'addon_type', 'status', 'purchased_at',
            'expires_at', 'is_active', 'storage_used_gb', 'ai_credits_used',
            'collaborations_used'
        ]

class PurchaseAddonSerializer(serializers.Serializer):
    """Serializer for purchasing add-ons"""
    addon_id = serializers.UUIDField()

class PaymentHistorySerializer(serializers.ModelSerializer):
    """Serializer for payment history"""
    
    class Meta:
        model = PaymentHistory
        fields = [
            'id', 'payment_type', 'status', 'amount', 'currency',
            'description', 'created_at', 'completed_at'
        ]

class UsageLimitSerializer(serializers.ModelSerializer):
    """Serializer for usage limits"""
    usage_percentage = serializers.ReadOnlyField()
    is_exceeded = serializers.ReadOnlyField()
    
    class Meta:
        model = UsageLimit
        fields = [
            'id', 'feature_type', 'limit_value', 'current_usage',
            'usage_percentage', 'is_exceeded', 'reset_period',
            'last_reset', 'next_reset'
        ]

class PromoCodeValidationSerializer(serializers.Serializer):
    """Serializer for promo code validation"""
    code = serializers.CharField(max_length=50)

class SubscriptionAnalyticsSerializer(serializers.Serializer):
    """Serializer for subscription analytics"""
    subscription_overview = serializers.DictField()
    usage_overview = serializers.DictField()
    feature_utilization = serializers.DictField()
    payment_summary = serializers.DictField()
    recommendations = serializers.ListField()
