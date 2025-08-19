"""
Subscription and Payment Serializers
"""
from rest_framework import serializers
from .models import SubscriptionPlan, UserSubscription, Advertisement, PaymentTransaction, AdImpression

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for subscription plans"""
    features = serializers.SerializerMethodField()
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'description', 'plan_type', 'price_monthly', 'price_yearly',
            'profile_views_limit', 'collaboration_invites_limit', 'ai_suggestions_limit',
            'portfolio_items_limit', 'features', 'is_active'
        ]
    
    def get_features(self, obj):
        return {
            'send_invites_only': obj.can_send_invites_only,
            'visibility_controls': obj.has_visibility_controls,
            'auto_translation': obj.has_auto_translation,
            'ai_portfolio_generator': obj.has_ai_portfolio_generator,
            'priority_support': obj.has_priority_support,
            'analytics': obj.has_analytics,
        }

class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for user subscriptions"""
    plan = SubscriptionPlanSerializer(read_only=True)
    plan_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = UserSubscription
        fields = [
            'id', 'plan', 'plan_id', 'billing_cycle', 'status',
            'current_period_start', 'current_period_end', 'next_billing_date',
            'profile_views_used', 'ai_suggestions_used', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'profile_views_used', 'ai_suggestions_used']

class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer for advertisements"""
    
    class Meta:
        model = Advertisement
        fields = [
            'id', 'title', 'description', 'image_url', 'click_url',
            'target_categories', 'target_experience_levels', 'target_locations',
            'impressions', 'clicks', 'ctr', 'start_date', 'end_date'
        ]

class PaymentTransactionSerializer(serializers.ModelSerializer):
    """Serializer for payment transactions"""
    
    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'transaction_type', 'status', 'amount', 'description',
            'stripe_payment_intent_id', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class AdImpressionSerializer(serializers.ModelSerializer):
    """Serializer for ad impressions"""
    ad = AdvertisementSerializer(read_only=True)
    
    class Meta:
        model = AdImpression
        fields = [
            'id', 'ad', 'page_context', 'was_clicked', 'click_time',
            'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
