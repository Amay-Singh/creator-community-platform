"""
Analytics API views
"""
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from datetime import timedelta
from .models import (
    UserEngagementMetric, PlatformMetric, MatchingAnalytics,
    NotificationAnalytics, RealtimeAnalytics, AnalyticsEvent
)
from .serializers import (
    UserEngagementMetricSerializer, PlatformMetricSerializer,
    MatchingAnalyticsSerializer, NotificationAnalyticsSerializer,
    RealtimeAnalyticsSerializer, AnalyticsEventSerializer,
    AnalyticsDashboardSerializer, DateRangeSerializer
)
from .services import AnalyticsCollector, AnalyticsReporter
from utils.cache import cache_result, CACHE_TIMEOUT_MEDIUM
import logging

logger = logging.getLogger(__name__)


class AnalyticsPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
@cache_result(timeout=CACHE_TIMEOUT_MEDIUM, key_prefix='analytics_dashboard')
def analytics_dashboard(request):
    """
    GET /api/analytics/dashboard
    Get comprehensive analytics dashboard data
    """
    try:
        days = int(request.query_params.get('days', 30))
        
        # Get overview data
        platform_overview = AnalyticsReporter.get_platform_overview(days)
        matching_performance = AnalyticsReporter.get_matching_performance(days)
        notification_performance = AnalyticsReporter.get_notification_performance(days)
        
        # Get recent events
        recent_events = AnalyticsEvent.objects.select_related('user').order_by('-timestamp')[:20]
        
        dashboard_data = {
            'platform_overview': platform_overview or {},
            'matching_performance': matching_performance or {},
            'notification_performance': notification_performance or {},
            'recent_events': recent_events
        }
        
        serializer = AnalyticsDashboardSerializer(dashboard_data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"analytics_dashboard_error: {e}")
        return Response(
            {'error': 'Failed to fetch dashboard data'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def platform_metrics(request):
    """
    GET /api/analytics/platform-metrics
    Get platform metrics with optional date filtering
    """
    try:
        # Parse date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = PlatformMetric.objects.all().order_by('-date')
        
        if start_date and end_date:
            date_serializer = DateRangeSerializer(data={
                'start_date': start_date,
                'end_date': end_date
            })
            if date_serializer.is_valid():
                queryset = queryset.filter(
                    date__gte=date_serializer.validated_data['start_date'],
                    date__lte=date_serializer.validated_data['end_date']
                )
            else:
                return Response(date_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        paginator = AnalyticsPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = PlatformMetricSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = PlatformMetricSerializer(queryset, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"platform_metrics_error: {e}")
        return Response(
            {'error': 'Failed to fetch platform metrics'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def user_engagement(request):
    """
    GET /api/analytics/user-engagement
    Get user engagement metrics
    """
    try:
        # Parse date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = UserEngagementMetric.objects.select_related('user').order_by('-date')
        
        if start_date and end_date:
            date_serializer = DateRangeSerializer(data={
                'start_date': start_date,
                'end_date': end_date
            })
            if date_serializer.is_valid():
                queryset = queryset.filter(
                    date__gte=date_serializer.validated_data['start_date'],
                    date__lte=date_serializer.validated_data['end_date']
                )
            else:
                return Response(date_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        paginator = AnalyticsPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = UserEngagementMetricSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = UserEngagementMetricSerializer(queryset, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"user_engagement_error: {e}")
        return Response(
            {'error': 'Failed to fetch user engagement metrics'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def matching_analytics(request):
    """
    GET /api/analytics/matching
    Get AI matching analytics
    """
    try:
        # Parse date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = MatchingAnalytics.objects.all().order_by('-date')
        
        if start_date and end_date:
            date_serializer = DateRangeSerializer(data={
                'start_date': start_date,
                'end_date': end_date
            })
            if date_serializer.is_valid():
                queryset = queryset.filter(
                    date__gte=date_serializer.validated_data['start_date'],
                    date__lte=date_serializer.validated_data['end_date']
                )
            else:
                return Response(date_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        paginator = AnalyticsPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = MatchingAnalyticsSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = MatchingAnalyticsSerializer(queryset, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"matching_analytics_error: {e}")
        return Response(
            {'error': 'Failed to fetch matching analytics'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def notification_analytics(request):
    """
    GET /api/analytics/notifications
    Get notification analytics
    """
    try:
        # Parse date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = NotificationAnalytics.objects.all().order_by('-date')
        
        if start_date and end_date:
            date_serializer = DateRangeSerializer(data={
                'start_date': start_date,
                'end_date': end_date
            })
            if date_serializer.is_valid():
                queryset = queryset.filter(
                    date__gte=date_serializer.validated_data['start_date'],
                    date__lte=date_serializer.validated_data['end_date']
                )
            else:
                return Response(date_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        paginator = AnalyticsPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = NotificationAnalyticsSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = NotificationAnalyticsSerializer(queryset, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"notification_analytics_error: {e}")
        return Response(
            {'error': 'Failed to fetch notification analytics'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def realtime_analytics(request):
    """
    GET /api/analytics/realtime
    Get real-time collaboration analytics
    """
    try:
        # Parse date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = RealtimeAnalytics.objects.all().order_by('-date')
        
        if start_date and end_date:
            date_serializer = DateRangeSerializer(data={
                'start_date': start_date,
                'end_date': end_date
            })
            if date_serializer.is_valid():
                queryset = queryset.filter(
                    date__gte=date_serializer.validated_data['start_date'],
                    date__lte=date_serializer.validated_data['end_date']
                )
            else:
                return Response(date_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        paginator = AnalyticsPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = RealtimeAnalyticsSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = RealtimeAnalyticsSerializer(queryset, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"realtime_analytics_error: {e}")
        return Response(
            {'error': 'Failed to fetch real-time analytics'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def analytics_events(request):
    """
    GET /api/analytics/events
    Get analytics events with filtering
    """
    try:
        event_type = request.query_params.get('event_type')
        user_id = request.query_params.get('user_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = AnalyticsEvent.objects.select_related('user').order_by('-timestamp')
        
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        if start_date and end_date:
            date_serializer = DateRangeSerializer(data={
                'start_date': start_date,
                'end_date': end_date
            })
            if date_serializer.is_valid():
                queryset = queryset.filter(
                    timestamp__date__gte=date_serializer.validated_data['start_date'],
                    timestamp__date__lte=date_serializer.validated_data['end_date']
                )
            else:
                return Response(date_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        paginator = AnalyticsPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = AnalyticsEventSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = AnalyticsEventSerializer(queryset, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"analytics_events_error: {e}")
        return Response(
            {'error': 'Failed to fetch analytics events'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def collect_metrics(request):
    """
    POST /api/analytics/collect
    Manually trigger metrics collection
    """
    try:
        date_str = request.data.get('date')
        if date_str:
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date = timezone.now().date()
        
        AnalyticsCollector.collect_all_daily_metrics(date)
        
        return Response({
            'success': True,
            'message': f'Metrics collected for {date}'
        })
        
    except Exception as e:
        logger.error(f"collect_metrics_error: {e}")
        return Response(
            {'error': 'Failed to collect metrics'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Health endpoints should be public
def simple_analytics_health(request):
    """Simple analytics health check"""
    return Response({
        'status': 'healthy',
        'service': 'analytics',
        'timestamp': timezone.now()
    })

@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Health endpoints should be public
def analytics_health(request):
    """
    GET /api/analytics/health
    Health check for analytics system
    """
    try:
        # Check if we have recent data
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        platform_metrics_count = PlatformMetric.objects.filter(date__gte=yesterday).count()
        events_count = AnalyticsEvent.objects.filter(timestamp__date=today).count()
        
        health_status = {
            'status': 'healthy',
            'platform_metrics_recent': platform_metrics_count > 0,
            'events_today': events_count,
            'last_collection': PlatformMetric.objects.order_by('-created_at').first().created_at if PlatformMetric.objects.exists() else None,
            'timestamp': timezone.now()
        }
        
        return Response(health_status)
        
    except Exception as e:
        logger.error(f"analytics_health_error: {e}")
        return Response(
            {'status': 'unhealthy', 'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
