import logging
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Notification, MatchNotification, NotificationSubscription
from .services import NotificationService, MatchNotificationService
from .push_service import push_service
from .analytics import NotificationAnalytics, NotificationMonitor
from utils.cache import CacheManager, cache_result, CACHE_TIMEOUT_SHORT
import json

logger = logging.getLogger(__name__)


class NotificationPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notifications_list(request):
    """
    GET /api/notifications
    Query params: page, status (unread|all)
    """
    try:
        user = request.user
        status_filter = request.query_params.get('status', 'all')
        page_num = request.query_params.get('page', 1)
        
        # Try to get from cache first
        cached_data = CacheManager.get_notifications(user.id, page_num)
        if cached_data and status_filter == 'all':
            logger.info(f"notif_list_cache_hit user_id={user.id} page={page_num}")
            return Response(cached_data)
        
        queryset = Notification.objects.filter(user=user).select_related('user').order_by('-created_at')
        
        if status_filter == 'unread':
            queryset = queryset.filter(read_at__isnull=True)
        
        paginator = NotificationPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = NotificationSerializer(page, many=True)
            response_data = paginator.get_paginated_response(serializer.data).data
            
            # Cache the response for 'all' status filter
            if status_filter == 'all':
                CacheManager.set_notifications(user.id, response_data, page_num, CACHE_TIMEOUT_SHORT)
            
            logger.info(f"notif_list_viewed user_id={user.id} status={status_filter} count={len(page)}")
            return Response(response_data)
        
        serializer = NotificationSerializer(queryset, many=True)
        logger.info(f"notif_list_viewed user_id={user.id} status={status_filter} count={queryset.count()}")
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"notifications_list_error user_id={request.user.id} error={str(e)}")
        return Response(
            {'error': 'Failed to fetch notifications'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notifications_read(request):
    """
    POST /api/notifications/mark-read
    Body: {"ids": [...]} or {"all": true}
    """
    try:
        user = request.user
        serializer = MarkNotificationsReadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        now = timezone.now()
        
        if data.get('all'):
            # Mark all unread notifications as read
            updated_count = Notification.objects.filter(
                user=user, 
                read_at__isnull=True
            ).update(read_at=now)
            
            # Invalidate notification cache
            CacheManager.invalidate_user_notifications(user.id)
            
            logger.info(f"notif_read user_id={user.id} action=mark_all count={updated_count}")
            return Response({
                'success': True, 
                'marked_read': updated_count,
                'message': f'Marked {updated_count} notifications as read'
            })
        
        elif data.get('ids'):
            # Mark specific notifications as read
            notification_ids = data['ids']
            updated_count = Notification.objects.filter(
                user=user,
                id__in=notification_ids,
                read_at__isnull=True
            ).update(read_at=now)
            
            # Invalidate notification cache
            CacheManager.invalidate_user_notifications(user.id)
            
            logger.info(f"notif_read user_id={user.id} action=mark_specific ids={notification_ids} count={updated_count}")
            return Response({
                'success': True,
                'marked_read': updated_count,
                'message': f'Marked {updated_count} notifications as read'
            })
        
        return Response(
            {'error': 'Invalid request data'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    except Exception as e:
        logger.error(f"mark_notifications_read_error user_id={request.user.id} error={str(e)}")
        return Response(
            {'error': 'Failed to mark notifications as read'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_feed(request):
    """
    GET /api/feed
    Query params: page
    """
    try:
        user = request.user
        
        # Get activities where user is involved (as user or mentioned)
        queryset = ActivityFeed.objects.filter(
            Q(user=user) | Q(actor=user)
        ).distinct()
        
        paginator = NotificationPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = ActivityFeedSerializer(page, many=True)
            logger.info(f"feed_viewed user_id={user.id} count={len(page)}")
            return paginator.get_paginated_response(serializer.data)
        
        serializer = ActivityFeedSerializer(queryset, many=True)
        logger.info(f"feed_viewed user_id={user.id} count={queryset.count()}")
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"activity_feed_error user_id={request.user.id} error={str(e)}")
        return Response(
            {'error': 'Failed to fetch activity feed'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_count(request):
    """
    GET /api/notifications/unread-count
    Returns count of unread notifications for current user
    """
    try:
        user = request.user
        count = Notification.objects.filter(user=user, read_at__isnull=True).count()
        
        return Response({'unread_count': count})
        
    except Exception as e:
        logger.error(f"unread_count_error user_id={request.user.id} error={str(e)}")
        return Response(
            {'error': 'Failed to get unread count'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Real-time notification API endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def match_notifications(request):
    """
    GET /api/notifications/matches
    Get match-specific notifications
    """
    try:
        user = request.user
        queryset = MatchNotification.objects.filter(recipient=user)
        
        # Filter by read status if specified
        status_filter = request.query_params.get('status', 'all')
        if status_filter == 'unread':
            queryset = queryset.filter(is_read=False)
        
        paginator = NotificationPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            notifications = []
            for notification in page:
                notifications.append({
                    'id': str(notification.id),
                    'type': notification.notification_type,
                    'match_id': str(notification.match_id),
                    'title': notification.title,
                    'message': notification.message,
                    'metadata': notification.metadata,
                    'is_read': notification.is_read,
                    'created_at': notification.created_at.isoformat(),
                    'sender': notification.sender.username if notification.sender else None
                })
            
            return paginator.get_paginated_response(notifications)
        
        return Response([])
        
    except Exception as e:
        logger.error(f"match_notifications_error user_id={request.user.id} error={str(e)}")
        return Response(
            {'error': 'Failed to fetch match notifications'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_match_notification_read(request, notification_id):
    """
    POST /api/notifications/matches/{notification_id}/read
    Mark specific match notification as read
    """
    try:
        user = request.user
        notification = MatchNotification.objects.get(
            id=notification_id,
            recipient=user
        )
        
        notification.mark_as_read()
        
        return Response({
            'success': True,
            'message': 'Notification marked as read'
        })
        
    except MatchNotification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"mark_match_notification_read_error user_id={request.user.id} error={str(e)}")
        return Response(
            {'error': 'Failed to mark notification as read'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def notification_preferences(request):
    """
    GET/PUT /api/notifications/preferences
    Get or update user notification preferences
    """
    try:
        user = request.user
        
        if request.method == 'GET':
            preferences = NotificationPreferencesService.get_preferences(user.id)
            return Response({'preferences': preferences})
        
        elif request.method == 'PUT':
            preferences = request.data.get('preferences', {})
            success = NotificationPreferencesService.update_preferences(user.id, preferences)
            
            if success:
                return Response({
                    'success': True,
                    'message': 'Preferences updated successfully'
                })
            else:
                return Response(
                    {'error': 'Failed to update preferences'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
    except Exception as e:
        logger.error(f"notification_preferences_error user_id={request.user.id} error={str(e)}")
        return Response(
            {'error': 'Failed to handle notification preferences'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_notification(request):
    """
    POST /api/notifications/test
    Send test notification for development/testing
    """
    try:
        user = request.user
        notification_type = request.data.get('type', 'system_announcement')
        title = request.data.get('title', 'Test Notification')
        message = request.data.get('message', 'This is a test notification')
        
        notification = NotificationService.send_notification(
            user_id=user.id,
            notification_type=notification_type,
            title=title,
            message=message,
            payload={'test': True}
        )
        
        if notification:
            return Response({
                'success': True,
                'notification_id': str(notification.id),
                'message': 'Test notification sent'
            })
        else:
            return Response(
                {'error': 'Failed to send test notification'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"test_notification_error user_id={request.user.id} error={str(e)}")
        return Response(
            {'error': 'Failed to send test notification'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def websocket_status(request):
    """
    GET /api/notifications/websocket-status
    Get WebSocket connection status for user
    """
    try:
        user = request.user
        subscription = NotificationSubscription.objects.filter(user=user).first()
        
        if subscription:
            return Response({
                'connected': subscription.websocket_connected,
                'connection_count': subscription.connection_count,
                'last_connected': subscription.last_connected_at.isoformat() if subscription.last_connected_at else None,
                'preferences': subscription.preferences
            })
        else:
            return Response({
                'connected': False,
                'connection_count': 0,
                'last_connected': None,
                'preferences': {}
            })
            
    except Exception as e:
        logger.error(f"websocket_status_error user_id={request.user.id} error={str(e)}")
        return Response(
            {'error': 'Failed to get WebSocket status'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Push notification endpoints
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe_push(request):
    """
    POST /api/notifications/push/subscribe
    Subscribe user to push notifications
    """
    try:
        from .push_service import push_service
        
        subscription_data = request.data.get('subscription')
        if not subscription_data:
            return Response(
                {'error': 'Subscription data required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = push_service.subscribe_user(request.user.id, subscription_data)
        
        if success:
            return Response({
                'success': True,
                'message': 'Successfully subscribed to push notifications'
            })
        else:
            return Response(
                {'error': 'Failed to subscribe to push notifications'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"subscribe_push_error user_id={request.user.id} error={str(e)}")
        return Response(
            {'error': 'Failed to subscribe to push notifications'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unsubscribe_push(request):
    """
    POST /api/notifications/push/unsubscribe
    Unsubscribe user from push notifications
    """
    try:
        from .push_service import push_service
        
        success = push_service.unsubscribe_user(request.user.id)
        
        if success:
            return Response({
                'success': True,
                'message': 'Successfully unsubscribed from push notifications'
            })
        else:
            return Response(
                {'error': 'Failed to unsubscribe from push notifications'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"unsubscribe_push_error user_id={request.user.id} error={str(e)}")
        return Response(
            {'error': 'Failed to unsubscribe from push notifications'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vapid_public_key(request):
    """
    GET /api/notifications/push/vapid-key
    Get VAPID public key for push subscription
    """
    try:
        from .push_service import push_service
        
        public_key = push_service.get_vapid_public_key()
        
        if public_key:
            return Response({'public_key': public_key})
        else:
            return Response(
                {'error': 'VAPID public key not configured'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"vapid_public_key_error user_id={request.user.id} error={str(e)}")
        return Response(
            {'error': 'Failed to get VAPID public key'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_push_notification(request):
    """
    POST /api/notifications/push/test
    Send test push notification
    """
    try:
        from .push_service import push_service
        
        success = push_service.test_push_notification(request.user.id)
        
        if success:
            return Response({
                'success': True,
                'message': 'Test push notification sent'
            })
        else:
            return Response(
                {'error': 'Failed to send test push notification'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"test_push_notification_error user_id={request.user.id} error={str(e)}")
        return Response(
            {'error': 'Failed to send test push notification'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_dashboard(request):
    """
    GET /api/notifications/analytics/dashboard
    Get comprehensive notification analytics dashboard data
    """
    try:
        dashboard_data = NotificationAnalytics.generate_dashboard_data()
        return Response(dashboard_data)
    except Exception as e:
        logger.error(f"Error generating analytics dashboard: {str(e)}")
        return Response({'error': 'Failed to generate analytics dashboard'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_delivery_stats(request):
    """
    GET /api/notifications/analytics/delivery
    Get notification delivery statistics
    Query params: days (default: 7)
    """
    try:
        days = int(request.query_params.get('days', 7))
        stats = NotificationAnalytics.get_delivery_stats(days)
        return Response(stats)
    except Exception as e:
        logger.error(f"Error getting delivery stats: {str(e)}")
        return Response({'error': 'Failed to get delivery statistics'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_user_engagement(request):
    """
    GET /api/notifications/analytics/engagement
    Get user engagement metrics
    Query params: days (default: 30)
    """
    try:
        days = int(request.query_params.get('days', 30))
        metrics = NotificationAnalytics.get_user_engagement_metrics(days)
        return Response(metrics)
    except Exception as e:
        logger.error(f"Error getting engagement metrics: {str(e)}")
        return Response({'error': 'Failed to get engagement metrics'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_match_notifications(request):
    """
    GET /api/notifications/analytics/matches
    Get match notification analytics
    Query params: days (default: 7)
    """
    try:
        days = int(request.query_params.get('days', 7))
        analytics = NotificationAnalytics.get_match_notification_analytics(days)
        return Response(analytics)
    except Exception as e:
        logger.error(f"Error getting match analytics: {str(e)}")
        return Response({'error': 'Failed to get match analytics'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_real_time_metrics(request):
    """
    GET /api/notifications/analytics/realtime
    Get real-time system metrics
    """
    try:
        metrics = NotificationAnalytics.get_real_time_metrics()
        return Response(metrics)
    except Exception as e:
        logger.error(f"Error getting real-time metrics: {str(e)}")
        return Response({'error': 'Failed to get real-time metrics'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_performance(request):
    """
    GET /api/notifications/analytics/performance
    Get system performance metrics
    Query params: days (default: 7)
    """
    try:
        days = int(request.query_params.get('days', 7))
        metrics = NotificationAnalytics.get_performance_metrics(days)
        return Response(metrics)
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        return Response({'error': 'Failed to get performance metrics'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_user_history(request):
    """
    GET /api/notifications/analytics/user-history
    Get notification history for current user
    Query params: days (default: 30)
    """
    try:
        days = int(request.query_params.get('days', 30))
        history = NotificationAnalytics.get_user_notification_history(
            request.user.id, days
        )
        return Response(history)
    except Exception as e:
        logger.error(f"Error getting user history: {str(e)}")
        return Response({'error': 'Failed to get user notification history'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])  # Health endpoints should be public
def simple_health(request):
    """Simple health check"""
    return Response({
        'status': 'healthy',
        'service': 'notifications',
        'timestamp': timezone.now()
    })

@api_view(['GET'])
@permission_classes([AllowAny])  # Health endpoints should be public
def system_health(request):
    """
    GET /api/notifications/health
    Get system health status
    """
    try:
        health = NotificationMonitor.check_system_health()
        return Response(health)
    except Exception as e:
        logger.error(f"Error checking system health: {str(e)}")
        return Response({'error': 'Failed to check system health'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_alerts(request):
    """
    GET /api/notifications/alerts
    Get system alert conditions
    """
    try:
        alerts = NotificationMonitor.get_alert_conditions()
        return Response({'alerts': alerts})
    except Exception as e:
        logger.error(f"Error getting system alerts: {str(e)}")
        return Response({'error': 'Failed to get system alerts'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)
