import logging
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import Notification, ActivityFeed
from .serializers import NotificationSerializer, ActivityFeedSerializer, MarkNotificationsReadSerializer

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
        
        queryset = Notification.objects.filter(user=user)
        
        if status_filter == 'unread':
            queryset = queryset.filter(read_at__isnull=True)
        
        paginator = NotificationPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = NotificationSerializer(page, many=True)
            logger.info(f"notif_list_viewed user_id={user.id} status={status_filter} count={len(page)}")
            return paginator.get_paginated_response(serializer.data)
        
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
