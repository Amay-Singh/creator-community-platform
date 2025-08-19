"""
Subscription and Payment Views
Implements REQ-21, REQ-22, REQ-23, REQ-24: Payment journeys and revenue features
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import stripe
import logging

from .models import SubscriptionPlan, UserSubscription, Advertisement, PaymentTransaction
from .serializers import (
    SubscriptionPlanSerializer, UserSubscriptionSerializer,
    AdvertisementSerializer, PaymentTransactionSerializer
)
from accounts.models import CreatorProfile

logger = logging.getLogger(__name__)
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

class SubscriptionPlansView(generics.ListAPIView):
    """List available subscription plans (REQ-22)"""
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserSubscriptionView(generics.RetrieveUpdateAPIView):
    """Get and update user subscription"""
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        subscription, created = UserSubscription.objects.get_or_create(
            profile=self.request.user.profile,
            defaults={
                'plan': SubscriptionPlan.objects.get(plan_type='free'),
                'current_period_start': timezone.now(),
                'current_period_end': timezone.now() + timedelta(days=30),
                'next_billing_date': timezone.now() + timedelta(days=30),
            }
        )
        return subscription

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_subscription(request):
    """Create new subscription with Stripe (REQ-21)"""
    try:
        plan_id = request.data.get('plan_id')
        billing_cycle = request.data.get('billing_cycle', 'monthly')
        payment_method_id = request.data.get('payment_method_id')
        
        plan = SubscriptionPlan.objects.get(id=plan_id)
        profile = request.user.profile
        
        # Create Stripe customer if doesn't exist
        if not hasattr(profile, 'stripe_customer_id'):
            customer = stripe.Customer.create(
                email=profile.user.email,
                name=profile.display_name,
                metadata={'profile_id': str(profile.id)}
            )
            profile.stripe_customer_id = customer.id
            profile.save()
        
        # Calculate price based on billing cycle
        price = plan.price_yearly if billing_cycle == 'yearly' else plan.price_monthly
        
        # Create Stripe subscription
        stripe_subscription = stripe.Subscription.create(
            customer=profile.stripe_customer_id,
            items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': plan.name,
                    },
                    'unit_amount': int(price * 100),  # Convert to cents
                    'recurring': {
                        'interval': 'year' if billing_cycle == 'yearly' else 'month',
                    },
                },
            }],
            default_payment_method=payment_method_id,
            expand=['latest_invoice.payment_intent'],
        )
        
        # Create or update user subscription
        subscription, created = UserSubscription.objects.get_or_create(
            profile=profile,
            defaults={
                'plan': plan,
                'billing_cycle': billing_cycle,
                'stripe_subscription_id': stripe_subscription.id,
                'current_period_start': timezone.now(),
                'current_period_end': timezone.now() + timedelta(days=365 if billing_cycle == 'yearly' else 30),
                'next_billing_date': timezone.now() + timedelta(days=365 if billing_cycle == 'yearly' else 30),
            }
        )
        
        if not created:
            subscription.plan = plan
            subscription.billing_cycle = billing_cycle
            subscription.stripe_subscription_id = stripe_subscription.id
            subscription.status = 'active'
            subscription.save()
        
        # Create payment transaction record
        PaymentTransaction.objects.create(
            profile=profile,
            transaction_type='subscription',
            status='completed',
            amount=price,
            stripe_payment_intent_id=stripe_subscription.latest_invoice.payment_intent.id,
            description=f'{plan.name} subscription ({billing_cycle})',
        )
        
        return Response({
            'success': True,
            'subscription_id': subscription.id,
            'client_secret': stripe_subscription.latest_invoice.payment_intent.client_secret
        })
        
    except Exception as e:
        logger.error(f"Subscription creation failed: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_subscription(request):
    """Cancel user subscription"""
    try:
        subscription = UserSubscription.objects.get(profile=request.user.profile)
        
        if subscription.stripe_subscription_id:
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )
        
        subscription.status = 'cancelled'
        subscription.save()
        
        return Response({'success': True, 'message': 'Subscription cancelled'})
        
    except UserSubscription.DoesNotExist:
        return Response({'error': 'No active subscription found'}, status=404)
    except Exception as e:
        logger.error(f"Subscription cancellation failed: {e}")
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def purchase_ai_portfolio(request):
    """Purchase AI portfolio generator (REQ-25)"""
    try:
        profile = request.user.profile
        payment_method_id = request.data.get('payment_method_id')
        
        # Check if user has access through subscription
        if hasattr(profile, 'subscription') and profile.subscription.is_feature_available('ai_portfolio_generator'):
            return Response({'error': 'Feature already available in your subscription'}, status=400)
        
        # Create one-time payment
        payment_intent = stripe.PaymentIntent.create(
            amount=2999,  # $29.99
            currency='usd',
            customer=getattr(profile, 'stripe_customer_id', None),
            payment_method=payment_method_id,
            confirmation_method='manual',
            confirm=True,
            description='AI Portfolio Generator',
            metadata={'profile_id': str(profile.id)}
        )
        
        # Create payment transaction
        transaction = PaymentTransaction.objects.create(
            profile=profile,
            transaction_type='portfolio_generator',
            status='completed' if payment_intent.status == 'succeeded' else 'pending',
            amount=29.99,
            stripe_payment_intent_id=payment_intent.id,
            description='AI Portfolio Generator purchase',
        )
        
        return Response({
            'success': True,
            'transaction_id': transaction.id,
            'client_secret': payment_intent.client_secret
        })
        
    except Exception as e:
        logger.error(f"AI portfolio purchase failed: {e}")
        return Response({'error': str(e)}, status=400)

class RelevantAdsView(generics.ListAPIView):
    """Get relevant ads for user (REQ-17, REQ-24)"""
    serializer_class = AdvertisementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        profile = self.request.user.profile
        now = timezone.now()
        
        # Get ads relevant to user's category and experience
        queryset = Advertisement.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        )
        
        # Filter by targeting criteria
        if profile.category:
            queryset = queryset.filter(
                models.Q(target_categories__contains=[profile.category]) |
                models.Q(target_categories=[])  # No targeting = show to all
            )
        
        if profile.experience_level:
            queryset = queryset.filter(
                models.Q(target_experience_levels__contains=[profile.experience_level]) |
                models.Q(target_experience_levels=[])
            )
        
        if profile.location:
            queryset = queryset.filter(
                models.Q(target_locations__contains=[profile.location]) |
                models.Q(target_locations=[])
            )
        
        return queryset.order_by('?')[:5]  # Random selection of 5 ads

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def track_ad_interaction(request):
    """Track ad impressions and clicks"""
    try:
        ad_id = request.data.get('ad_id')
        action = request.data.get('action')  # 'impression' or 'click'
        page_context = request.data.get('page_context', 'unknown')
        
        ad = Advertisement.objects.get(id=ad_id)
        profile = request.user.profile
        
        if action == 'impression':
            # Track impression
            from .models import AdImpression
            AdImpression.objects.create(
                ad=ad,
                profile=profile,
                page_context=page_context,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            # Update ad stats
            ad.impressions += 1
            ad.save()
            
        elif action == 'click':
            # Track click
            impression = AdImpression.objects.filter(
                ad=ad,
                profile=profile,
                was_clicked=False
            ).first()
            
            if impression:
                impression.was_clicked = True
                impression.click_time = timezone.now()
                impression.save()
                
                # Update ad stats
                ad.clicks += 1
                ad.save()
        
        return Response({'success': True})
        
    except Exception as e:
        logger.error(f"Ad tracking failed: {e}")
        return Response({'error': str(e)}, status=400)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def subscription_usage(request):
    """Get current subscription usage stats"""
    try:
        profile = request.user.profile
        subscription = getattr(profile, 'subscription', None)
        
        if not subscription:
            return Response({'error': 'No subscription found'}, status=404)
        
        # Calculate current usage
        from collaborations.models import CollaborationInvite
        from ai_services.models import AICollaborationSuggestion
        
        current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        usage_stats = {
            'plan_name': subscription.plan.name,
            'status': subscription.status,
            'current_period_end': subscription.current_period_end,
            'usage': {
                'profile_views': subscription.profile_views_used,
                'profile_views_limit': subscription.plan.profile_views_limit,
                'invites_sent': CollaborationInvite.objects.filter(
                    sender=profile,
                    created_at__gte=current_month_start
                ).count(),
                'invites_limit': subscription.plan.collaboration_invites_limit,
                'ai_suggestions_used': subscription.ai_suggestions_used,
                'ai_suggestions_limit': subscription.plan.ai_suggestions_limit,
                'portfolio_items': profile.portfolio_items.count(),
                'portfolio_items_limit': subscription.plan.portfolio_items_limit,
            },
            'features': {
                'send_invites_only': subscription.plan.can_send_invites_only,
                'visibility_controls': subscription.plan.has_visibility_controls,
                'auto_translation': subscription.plan.has_auto_translation,
                'ai_portfolio_generator': subscription.plan.has_ai_portfolio_generator,
                'priority_support': subscription.plan.has_priority_support,
                'analytics': subscription.plan.has_analytics,
            }
        }
        
        return Response(usage_stats)
        
    except Exception as e:
        logger.error(f"Usage stats failed: {e}")
        return Response({'error': str(e)}, status=400)
