"""
Subscription and Payment Service
Implements REQ-22-25: Revenue features - subscriptions, premium add-ons, payment processing
"""
# import stripe  # Commented out for development - not needed for basic functionality
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from typing import Dict, List, Optional
from decimal import Decimal

from .subscription_models import (
    SubscriptionPlan, UserSubscription, PremiumAddon, UserAddon,
    PaymentHistory, UsageLimit, PromoCode, PromoCodeUsage
)
from .models import CreatorProfile
from django.contrib.auth import get_user_model

User = get_user_model()

class SubscriptionService:
    """
    Service for managing subscriptions, payments, and premium features
    """
    
    def __init__(self):
        # Initialize Stripe (mock for development)
        # stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', 'sk_test_mock')
        pass
    
    def get_available_plans(self) -> List[Dict]:
        """Get all available subscription plans"""
        
        plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price_monthly')
        
        return [
            {
                'id': str(plan.id),
                'name': plan.name,
                'plan_type': plan.plan_type,
                'description': plan.description,
                'price_monthly': float(plan.price_monthly),
                'price_yearly': float(plan.price_yearly),
                'features': {
                    'max_portfolio_items': plan.max_portfolio_items,
                    'max_collaborations': plan.max_collaborations,
                    'ai_generations_per_month': plan.ai_generations_per_month,
                    'storage_gb': plan.storage_gb,
                    'priority_support': plan.priority_support,
                    'advanced_analytics': plan.advanced_analytics,
                    'custom_branding': plan.custom_branding,
                    'api_access': plan.api_access
                },
                'yearly_savings': float(plan.price_monthly * 12 - plan.price_yearly) if plan.price_yearly > 0 else 0
            }
            for plan in plans
        ]
    
    def get_user_subscription(self, user: User) -> Dict:
        """Get user's current subscription details"""
        
        try:
            subscription = UserSubscription.objects.get(user=user)
            
            return {
                'success': True,
                'subscription': {
                    'id': str(subscription.id),
                    'plan': {
                        'name': subscription.plan.name,
                        'plan_type': subscription.plan.plan_type,
                        'features': {
                            'max_portfolio_items': subscription.plan.max_portfolio_items,
                            'max_collaborations': subscription.plan.max_collaborations,
                            'ai_generations_per_month': subscription.plan.ai_generations_per_month,
                            'storage_gb': subscription.plan.storage_gb,
                            'priority_support': subscription.plan.priority_support,
                            'advanced_analytics': subscription.plan.advanced_analytics,
                            'custom_branding': subscription.plan.custom_branding,
                            'api_access': subscription.plan.api_access
                        }
                    },
                    'status': subscription.status,
                    'billing_cycle': subscription.billing_cycle,
                    'current_period_start': subscription.current_period_start,
                    'current_period_end': subscription.current_period_end,
                    'days_remaining': subscription.days_remaining,
                    'is_active': subscription.is_active,
                    'usage': {
                        'portfolio_items_used': subscription.portfolio_items_used,
                        'collaborations_used': subscription.collaborations_used,
                        'ai_generations_used': subscription.ai_generations_used,
                        'storage_used_gb': subscription.storage_used_gb
                    }
                }
            }
        
        except UserSubscription.DoesNotExist:
            # Create free subscription
            free_plan = SubscriptionPlan.objects.get(plan_type='free')
            subscription = self._create_free_subscription(user, free_plan)
            
            return {
                'success': True,
                'subscription': {
                    'id': str(subscription.id),
                    'plan': {
                        'name': subscription.plan.name,
                        'plan_type': subscription.plan.plan_type,
                        'features': {
                            'max_portfolio_items': subscription.plan.max_portfolio_items,
                            'max_collaborations': subscription.plan.max_collaborations,
                            'ai_generations_per_month': subscription.plan.ai_generations_per_month,
                            'storage_gb': subscription.plan.storage_gb,
                            'priority_support': subscription.plan.priority_support,
                            'advanced_analytics': subscription.plan.advanced_analytics,
                            'custom_branding': subscription.plan.custom_branding,
                            'api_access': subscription.plan.api_access
                        }
                    },
                    'status': subscription.status,
                    'billing_cycle': subscription.billing_cycle,
                    'current_period_start': subscription.current_period_start,
                    'current_period_end': subscription.current_period_end,
                    'days_remaining': subscription.days_remaining,
                    'is_active': subscription.is_active,
                    'usage': {
                        'portfolio_items_used': subscription.portfolio_items_used,
                        'collaborations_used': subscription.collaborations_used,
                        'ai_generations_used': subscription.ai_generations_used,
                        'storage_used_gb': subscription.storage_used_gb
                    }
                }
            }
    
    def create_subscription(self, user: User, plan_id: str, billing_cycle: str, promo_code: str = None) -> Dict:
        """Create a new subscription for user"""
        
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
            
            # Check if user already has active subscription
            existing_subscription = UserSubscription.objects.filter(user=user, status='active').first()
            if existing_subscription:
                return {
                    'success': False,
                    'error': 'User already has an active subscription'
                }
            
            # Calculate price based on billing cycle
            if billing_cycle == 'yearly':
                amount = plan.price_yearly
            else:
                amount = plan.price_monthly
            
            # Apply promo code if provided
            discount_applied = Decimal('0.00')
            if promo_code:
                promo_result = self._apply_promo_code(user, promo_code, amount)
                if promo_result['success']:
                    amount = promo_result['final_amount']
                    discount_applied = promo_result['discount_applied']
            
            # Create Stripe payment intent (mock)
            payment_intent = self._create_payment_intent(user, amount)
            
            if payment_intent['success']:
                # Create subscription
                subscription = UserSubscription.objects.create(
                    user=user,
                    plan=plan,
                    status='active',
                    billing_cycle=billing_cycle,
                    current_period_start=timezone.now(),
                    current_period_end=timezone.now() + timedelta(days=365 if billing_cycle == 'yearly' else 30),
                    stripe_subscription_id=payment_intent['subscription_id'],
                    stripe_customer_id=payment_intent['customer_id']
                )
                
                # Create payment record
                payment = PaymentHistory.objects.create(
                    user=user,
                    payment_type='subscription',
                    status='completed',
                    amount=amount,
                    subscription=subscription,
                    stripe_payment_intent_id=payment_intent['payment_intent_id'],
                    description=f"Subscription to {plan.name} ({billing_cycle})",
                    completed_at=timezone.now()
                )
                
                # Initialize usage limits
                self._initialize_usage_limits(user, plan)
                
                return {
                    'success': True,
                    'subscription_id': str(subscription.id),
                    'payment_id': str(payment.id),
                    'amount_charged': float(amount),
                    'discount_applied': float(discount_applied)
                }
            else:
                return {
                    'success': False,
                    'error': payment_intent['error']
                }
        
        except SubscriptionPlan.DoesNotExist:
            return {
                'success': False,
                'error': 'Subscription plan not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to create subscription: {str(e)}'
            }
    
    def cancel_subscription(self, user: User, reason: str = None) -> Dict:
        """Cancel user's subscription"""
        
        try:
            subscription = UserSubscription.objects.get(user=user, status='active')
            
            # Cancel in Stripe (mock)
            stripe_result = self._cancel_stripe_subscription(subscription.stripe_subscription_id)
            
            if stripe_result['success']:
                subscription.status = 'cancelled'
                subscription.cancelled_at = timezone.now()
                subscription.save()
                
                return {
                    'success': True,
                    'message': 'Subscription cancelled successfully',
                    'access_until': subscription.current_period_end
                }
            else:
                return {
                    'success': False,
                    'error': stripe_result['error']
                }
        
        except UserSubscription.DoesNotExist:
            return {
                'success': False,
                'error': 'No active subscription found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to cancel subscription: {str(e)}'
            }
    
    def get_available_addons(self) -> List[Dict]:
        """Get available premium add-ons"""
        
        addons = PremiumAddon.objects.filter(is_active=True)
        
        return [
            {
                'id': str(addon.id),
                'name': addon.name,
                'addon_type': addon.addon_type,
                'description': addon.description,
                'price': float(addon.price),
                'specifications': {
                    'storage_gb': addon.storage_gb,
                    'ai_credits': addon.ai_credits,
                    'collaboration_slots': addon.collaboration_slots,
                    'duration_days': addon.duration_days
                }
            }
            for addon in addons
        ]
    
    def purchase_addon(self, user: User, addon_id: str) -> Dict:
        """Purchase a premium add-on"""
        
        try:
            addon = PremiumAddon.objects.get(id=addon_id, is_active=True)
            
            # Create payment intent
            payment_intent = self._create_payment_intent(user, addon.price)
            
            if payment_intent['success']:
                # Create user addon
                user_addon = UserAddon.objects.create(
                    user=user,
                    addon=addon,
                    status='active',
                    expires_at=timezone.now() + timedelta(days=addon.duration_days),
                    stripe_payment_intent_id=payment_intent['payment_intent_id']
                )
                
                # Create payment record
                payment = PaymentHistory.objects.create(
                    user=user,
                    payment_type='addon',
                    status='completed',
                    amount=addon.price,
                    addon=user_addon,
                    stripe_payment_intent_id=payment_intent['payment_intent_id'],
                    description=f"Purchase of {addon.name}",
                    completed_at=timezone.now()
                )
                
                return {
                    'success': True,
                    'addon_id': str(user_addon.id),
                    'payment_id': str(payment.id),
                    'expires_at': user_addon.expires_at
                }
            else:
                return {
                    'success': False,
                    'error': payment_intent['error']
                }
        
        except PremiumAddon.DoesNotExist:
            return {
                'success': False,
                'error': 'Add-on not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to purchase add-on: {str(e)}'
            }
    
    def check_usage_limits(self, user: User, feature_type: str) -> Dict:
        """Check if user has exceeded usage limits for a feature"""
        
        try:
            usage_limit = UsageLimit.objects.get(user=user, feature_type=feature_type)
            
            return {
                'success': True,
                'limit': usage_limit.limit_value,
                'current_usage': usage_limit.current_usage,
                'is_exceeded': usage_limit.is_exceeded,
                'usage_percentage': usage_limit.usage_percentage,
                'next_reset': usage_limit.next_reset
            }
        
        except UsageLimit.DoesNotExist:
            # Create default usage limit based on subscription
            subscription = UserSubscription.objects.get(user=user)
            limit_value = self._get_feature_limit(subscription.plan, feature_type)
            
            usage_limit = UsageLimit.objects.create(
                user=user,
                feature_type=feature_type,
                limit_value=limit_value,
                next_reset=timezone.now() + timedelta(days=30)
            )
            
            return {
                'success': True,
                'limit': usage_limit.limit_value,
                'current_usage': usage_limit.current_usage,
                'is_exceeded': usage_limit.is_exceeded,
                'usage_percentage': usage_limit.usage_percentage,
                'next_reset': usage_limit.next_reset
            }
    
    def increment_usage(self, user: User, feature_type: str, amount: int = 1) -> Dict:
        """Increment usage for a feature"""
        
        try:
            usage_limit = UsageLimit.objects.get(user=user, feature_type=feature_type)
            usage_limit.current_usage += amount
            usage_limit.save()
            
            return {
                'success': True,
                'new_usage': usage_limit.current_usage,
                'is_exceeded': usage_limit.is_exceeded
            }
        
        except UsageLimit.DoesNotExist:
            return {
                'success': False,
                'error': 'Usage limit not found'
            }
    
    def get_payment_history(self, user: User) -> List[Dict]:
        """Get user's payment history"""
        
        payments = PaymentHistory.objects.filter(user=user).order_by('-created_at')[:20]
        
        return [
            {
                'id': str(payment.id),
                'payment_type': payment.payment_type,
                'status': payment.status,
                'amount': float(payment.amount),
                'currency': payment.currency,
                'description': payment.description,
                'created_at': payment.created_at,
                'completed_at': payment.completed_at
            }
            for payment in payments
        ]
    
    def validate_promo_code(self, code: str, user: User = None) -> Dict:
        """Validate a promo code"""
        
        try:
            promo = PromoCode.objects.get(code=code.upper())
            
            if not promo.is_valid:
                return {
                    'success': False,
                    'error': 'Promo code is expired or invalid'
                }
            
            if user and PromoCodeUsage.objects.filter(promo_code=promo, user=user).exists():
                return {
                    'success': False,
                    'error': 'Promo code already used'
                }
            
            return {
                'success': True,
                'promo_code': {
                    'code': promo.code,
                    'description': promo.description,
                    'discount_type': promo.discount_type,
                    'discount_value': float(promo.discount_value),
                    'valid_until': promo.valid_until
                }
            }
        
        except PromoCode.DoesNotExist:
            return {
                'success': False,
                'error': 'Promo code not found'
            }
    
    def _create_free_subscription(self, user: User, plan: SubscriptionPlan) -> UserSubscription:
        """Create a free subscription for new users"""
        
        subscription = UserSubscription.objects.create(
            user=user,
            plan=plan,
            status='active',
            billing_cycle='monthly',
            current_period_start=timezone.now(),
            current_period_end=timezone.now() + timedelta(days=365)  # Free plan doesn't expire
        )
        
        self._initialize_usage_limits(user, plan)
        return subscription
    
    def _initialize_usage_limits(self, user: User, plan: SubscriptionPlan):
        """Initialize usage limits based on subscription plan"""
        
        limits = [
            ('portfolio_items', plan.max_portfolio_items),
            ('collaborations', plan.max_collaborations),
            ('ai_generations', plan.ai_generations_per_month),
            ('storage', plan.storage_gb),
        ]
        
        for feature_type, limit_value in limits:
            UsageLimit.objects.get_or_create(
                user=user,
                feature_type=feature_type,
                defaults={
                    'limit_value': limit_value,
                    'next_reset': timezone.now() + timedelta(days=30)
                }
            )
    
    def _get_feature_limit(self, plan: SubscriptionPlan, feature_type: str) -> int:
        """Get feature limit for a plan"""
        
        limits = {
            'portfolio_items': plan.max_portfolio_items,
            'collaborations': plan.max_collaborations,
            'ai_generations': plan.ai_generations_per_month,
            'storage': plan.storage_gb,
        }
        
        return limits.get(feature_type, 0)
    
    def _create_payment_intent(self, user: User, amount: Decimal) -> Dict:
        """Create Stripe payment intent (mock implementation)"""
        
        # Mock Stripe payment intent creation
        return {
            'success': True,
            'payment_intent_id': f'pi_mock_{user.id}_{timezone.now().timestamp()}',
            'subscription_id': f'sub_mock_{user.id}_{timezone.now().timestamp()}',
            'customer_id': f'cus_mock_{user.id}',
            'client_secret': f'pi_mock_secret_{user.id}'
        }
    
    def _cancel_stripe_subscription(self, subscription_id: str) -> Dict:
        """Cancel Stripe subscription (mock implementation)"""
        
        # Mock Stripe subscription cancellation
        return {
            'success': True,
            'message': 'Subscription cancelled in Stripe'
        }
    
    def _apply_promo_code(self, user: User, code: str, amount: Decimal) -> Dict:
        """Apply promo code discount"""
        
        validation = self.validate_promo_code(code, user)
        if not validation['success']:
            return validation
        
        promo = PromoCode.objects.get(code=code.upper())
        
        if promo.discount_type == 'percentage':
            discount = amount * (promo.discount_value / 100)
        else:
            discount = promo.discount_value
        
        final_amount = max(Decimal('0.00'), amount - discount)
        
        # Record usage
        PromoCodeUsage.objects.create(
            promo_code=promo,
            user=user,
            discount_applied=discount
        )
        
        promo.current_uses += 1
        promo.save()
        
        return {
            'success': True,
            'discount_applied': discount,
            'final_amount': final_amount
        }

# Service instance
subscription_service = SubscriptionService()
