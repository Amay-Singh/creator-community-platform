"""
Subscription and Payment Views
Implements REQ-22-25: Revenue features - subscriptions, premium add-ons, payment processing
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404

from .subscription_service import subscription_service
from .subscription_serializers import (
    SubscriptionPlanSerializer, UserSubscriptionSerializer,
    PremiumAddonSerializer, PaymentHistorySerializer,
    CreateSubscriptionSerializer, PurchaseAddonSerializer,
    PromoCodeValidationSerializer
)

class SubscriptionPlansView(generics.ListAPIView):
    """List all available subscription plans"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
        plans = subscription_service.get_available_plans()
        return Response({'plans': plans}, status=status.HTTP_200_OK)

class UserSubscriptionView(generics.RetrieveAPIView):
    """Get user's current subscription details"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        result = subscription_service.get_user_subscription(request.user)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreateSubscriptionView(generics.CreateAPIView):
    """Create a new subscription"""
    serializer_class = CreateSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        plan_id = serializer.validated_data['plan_id']
        billing_cycle = serializer.validated_data['billing_cycle']
        promo_code = serializer.validated_data.get('promo_code')
        
        result = subscription_service.create_subscription(
            request.user, plan_id, billing_cycle, promo_code
        )
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_subscription(request):
    """Cancel user's subscription"""
    
    reason = request.data.get('reason', '')
    result = subscription_service.cancel_subscription(request.user, reason)
    
    if result['success']:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

class PremiumAddonsView(generics.ListAPIView):
    """List all available premium add-ons"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        addons = subscription_service.get_available_addons()
        return Response({'addons': addons}, status=status.HTTP_200_OK)

class PurchaseAddonView(generics.CreateAPIView):
    """Purchase a premium add-on"""
    serializer_class = PurchaseAddonSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        addon_id = serializer.validated_data['addon_id']
        result = subscription_service.purchase_addon(request.user, addon_id)
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def usage_limits(request):
    """Get user's usage limits for all features"""
    
    feature_types = ['portfolio_items', 'collaborations', 'ai_generations', 'storage']
    usage_data = {}
    
    for feature_type in feature_types:
        result = subscription_service.check_usage_limits(request.user, feature_type)
        if result['success']:
            usage_data[feature_type] = {
                'limit': result['limit'],
                'current_usage': result['current_usage'],
                'is_exceeded': result['is_exceeded'],
                'usage_percentage': result['usage_percentage'],
                'next_reset': result['next_reset']
            }
    
    return Response({'usage_limits': usage_data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def payment_history(request):
    """Get user's payment history"""
    
    payments = subscription_service.get_payment_history(request.user)
    return Response({'payments': payments}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def validate_promo_code(request):
    """Validate a promo code"""
    
    code = request.data.get('code')
    if not code:
        return Response({'error': 'Promo code is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    result = subscription_service.validate_promo_code(code, request.user)
    
    if result['success']:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def subscription_analytics(request):
    """Get subscription analytics for the user"""
    
    subscription_result = subscription_service.get_user_subscription(request.user)
    payments = subscription_service.get_payment_history(request.user)
    
    if not subscription_result['success']:
        return Response({'error': 'No subscription found'}, status=status.HTTP_404_NOT_FOUND)
    
    subscription = subscription_result['subscription']
    
    analytics = {
        'subscription_overview': {
            'plan_name': subscription['plan']['name'],
            'plan_type': subscription['plan']['plan_type'],
            'status': subscription['status'],
            'days_remaining': subscription['days_remaining'],
            'billing_cycle': subscription['billing_cycle']
        },
        'usage_overview': subscription['usage'],
        'feature_utilization': {
            'portfolio_items': {
                'used': subscription['usage']['portfolio_items_used'],
                'limit': subscription['plan']['features']['max_portfolio_items'],
                'percentage': (subscription['usage']['portfolio_items_used'] / max(1, subscription['plan']['features']['max_portfolio_items'])) * 100
            },
            'collaborations': {
                'used': subscription['usage']['collaborations_used'],
                'limit': subscription['plan']['features']['max_collaborations'],
                'percentage': (subscription['usage']['collaborations_used'] / max(1, subscription['plan']['features']['max_collaborations'])) * 100
            },
            'ai_generations': {
                'used': subscription['usage']['ai_generations_used'],
                'limit': subscription['plan']['features']['ai_generations_per_month'],
                'percentage': (subscription['usage']['ai_generations_used'] / max(1, subscription['plan']['features']['ai_generations_per_month'])) * 100
            }
        },
        'payment_summary': {
            'total_payments': len(payments),
            'total_spent': sum(p['amount'] for p in payments if p['status'] == 'completed'),
            'recent_payments': payments[:5]
        },
        'recommendations': []
    }
    
    # Add recommendations based on usage
    if analytics['feature_utilization']['portfolio_items']['percentage'] > 80:
        analytics['recommendations'].append({
            'type': 'upgrade',
            'message': 'You\'re approaching your portfolio item limit. Consider upgrading for more storage.',
            'action': 'upgrade_plan'
        })
    
    if analytics['feature_utilization']['ai_generations']['percentage'] > 90:
        analytics['recommendations'].append({
            'type': 'addon',
            'message': 'You\'ve used most of your AI generation credits. Consider purchasing additional credits.',
            'action': 'buy_ai_credits'
        })
    
    return Response(analytics, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def increment_feature_usage(request):
    """Increment usage for a specific feature (internal API)"""
    
    feature_type = request.data.get('feature_type')
    amount = request.data.get('amount', 1)
    
    if not feature_type:
        return Response({'error': 'feature_type is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    valid_features = ['portfolio_items', 'collaborations', 'ai_generations', 'storage']
    if feature_type not in valid_features:
        return Response({'error': 'Invalid feature_type'}, status=status.HTTP_400_BAD_REQUEST)
    
    result = subscription_service.increment_usage(request.user, feature_type, amount)
    
    if result['success']:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
