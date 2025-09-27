"""
WebSocket consumers for real-time analytics
"""
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import AnalyticsEvent, PlatformMetric
from .services import AnalyticsReporter
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class AnalyticsConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time analytics updates
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        try:
            # Check if user is admin
            user = self.scope.get('user')
            if not user or not user.is_authenticated or not user.is_staff:
                await self.close()
                return
            
            # Join analytics group
            self.group_name = 'analytics_updates'
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # Send initial data
            await self.send_analytics_update()
            
            logger.info(f"Analytics WebSocket connected for admin user {user.id}")
            
        except Exception as e:
            logger.error(f"Error connecting analytics WebSocket: {e}")
            await self.close()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        try:
            if hasattr(self, 'group_name'):
                await self.channel_layer.group_discard(
                    self.group_name,
                    self.channel_name
                )
            logger.info(f"Analytics WebSocket disconnected with code {close_code}")
        except Exception as e:
            logger.error(f"Error disconnecting analytics WebSocket: {e}")
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'get_update':
                await self.send_analytics_update()
            elif message_type == 'get_events':
                await self.send_recent_events()
            elif message_type == 'get_metrics':
                days = data.get('days', 30)
                await self.send_metrics_data(days)
                
        except Exception as e:
            logger.error(f"Error handling analytics WebSocket message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to process request'
            }))
    
    async def send_analytics_update(self):
        """Send current analytics data"""
        try:
            # Get platform overview
            platform_data = await database_sync_to_async(
                AnalyticsReporter.get_platform_overview
            )(7)  # Last 7 days
            
            # Get recent events
            recent_events = await self.get_recent_events()
            
            # Get real-time stats
            realtime_stats = await self.get_realtime_stats()
            
            await self.send(text_data=json.dumps({
                'type': 'analytics_update',
                'data': {
                    'platform_overview': platform_data,
                    'recent_events': recent_events,
                    'realtime_stats': realtime_stats,
                    'timestamp': timezone.now().isoformat()
                }
            }))
            
        except Exception as e:
            logger.error(f"Error sending analytics update: {e}")
    
    async def send_recent_events(self):
        """Send recent analytics events"""
        try:
            events = await self.get_recent_events(limit=20)
            
            await self.send(text_data=json.dumps({
                'type': 'recent_events',
                'data': events
            }))
            
        except Exception as e:
            logger.error(f"Error sending recent events: {e}")
    
    async def send_metrics_data(self, days=30):
        """Send metrics data for specified time range"""
        try:
            platform_data = await database_sync_to_async(
                AnalyticsReporter.get_platform_overview
            )(days)
            
            matching_data = await database_sync_to_async(
                AnalyticsReporter.get_matching_performance
            )(days)
            
            notification_data = await database_sync_to_async(
                AnalyticsReporter.get_notification_performance
            )(days)
            
            await self.send(text_data=json.dumps({
                'type': 'metrics_data',
                'data': {
                    'platform_overview': platform_data,
                    'matching_performance': matching_data,
                    'notification_performance': notification_data,
                    'days': days
                }
            }))
            
        except Exception as e:
            logger.error(f"Error sending metrics data: {e}")
    
    @database_sync_to_async
    def get_recent_events(self, limit=10):
        """Get recent analytics events"""
        try:
            events = AnalyticsEvent.objects.select_related('user').order_by('-timestamp')[:limit]
            return [
                {
                    'id': event.id,
                    'event_type': event.event_type,
                    'username': event.user.username if event.user else None,
                    'timestamp': event.timestamp.isoformat(),
                    'event_data': event.event_data
                }
                for event in events
            ]
        except Exception as e:
            logger.error(f"Error getting recent events: {e}")
            return []
    
    @database_sync_to_async
    def get_realtime_stats(self):
        """Get real-time statistics"""
        try:
            today = timezone.now().date()
            
            # Get today's events count
            events_today = AnalyticsEvent.objects.filter(timestamp__date=today).count()
            
            # Get active users in last hour
            one_hour_ago = timezone.now() - timezone.timedelta(hours=1)
            active_users_hour = AnalyticsEvent.objects.filter(
                timestamp__gte=one_hour_ago,
                user__isnull=False
            ).values('user').distinct().count()
            
            # Get latest platform metrics
            latest_metrics = PlatformMetric.objects.order_by('-date').first()
            
            return {
                'events_today': events_today,
                'active_users_hour': active_users_hour,
                'avg_response_time': latest_metrics.avg_api_response_time if latest_metrics else 0,
                'error_rate': latest_metrics.error_rate if latest_metrics else 0,
                'last_updated': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting realtime stats: {e}")
            return {}
    
    # Group message handlers
    async def analytics_event(self, event):
        """Handle analytics event broadcast"""
        await self.send(text_data=json.dumps({
            'type': 'new_event',
            'data': event['data']
        }))
    
    async def metrics_update(self, event):
        """Handle metrics update broadcast"""
        await self.send(text_data=json.dumps({
            'type': 'metrics_update',
            'data': event['data']
        }))


class LiveMetricsConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for live metrics display
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        try:
            # Check if user is admin
            user = self.scope.get('user')
            if not user or not user.is_authenticated or not user.is_staff:
                await self.close()
                return
            
            # Join live metrics group
            self.group_name = 'live_metrics'
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # Start sending periodic updates
            asyncio.create_task(self.send_periodic_updates())
            
            logger.info(f"Live metrics WebSocket connected for admin user {user.id}")
            
        except Exception as e:
            logger.error(f"Error connecting live metrics WebSocket: {e}")
            await self.close()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        try:
            if hasattr(self, 'group_name'):
                await self.channel_layer.group_discard(
                    self.group_name,
                    self.channel_name
                )
            logger.info(f"Live metrics WebSocket disconnected with code {close_code}")
        except Exception as e:
            logger.error(f"Error disconnecting live metrics WebSocket: {e}")
    
    async def send_periodic_updates(self):
        """Send periodic metric updates"""
        try:
            while True:
                # Send live metrics every 30 seconds
                await asyncio.sleep(30)
                
                realtime_stats = await self.get_realtime_stats()
                
                await self.send(text_data=json.dumps({
                    'type': 'live_update',
                    'data': realtime_stats
                }))
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in periodic updates: {e}")
    
    @database_sync_to_async
    def get_realtime_stats(self):
        """Get real-time statistics"""
        try:
            now = timezone.now()
            today = now.date()
            
            # Get current metrics
            events_today = AnalyticsEvent.objects.filter(timestamp__date=today).count()
            
            # Active users in different time windows
            active_users_5min = AnalyticsEvent.objects.filter(
                timestamp__gte=now - timezone.timedelta(minutes=5),
                user__isnull=False
            ).values('user').distinct().count()
            
            active_users_hour = AnalyticsEvent.objects.filter(
                timestamp__gte=now - timezone.timedelta(hours=1),
                user__isnull=False
            ).values('user').distinct().count()
            
            # Recent API requests
            api_requests_5min = AnalyticsEvent.objects.filter(
                timestamp__gte=now - timezone.timedelta(minutes=5),
                event_type='api_request'
            ).count()
            
            # Error rate in last hour
            errors_hour = AnalyticsEvent.objects.filter(
                timestamp__gte=now - timezone.timedelta(hours=1),
                event_type='error_occurred'
            ).count()
            
            total_requests_hour = AnalyticsEvent.objects.filter(
                timestamp__gte=now - timezone.timedelta(hours=1),
                event_type='api_request'
            ).count()
            
            error_rate = (errors_hour / total_requests_hour * 100) if total_requests_hour > 0 else 0
            
            return {
                'events_today': events_today,
                'active_users_5min': active_users_5min,
                'active_users_hour': active_users_hour,
                'api_requests_5min': api_requests_5min,
                'error_rate_hour': round(error_rate, 2),
                'timestamp': now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting realtime stats: {e}")
            return {}
    
    # Group message handlers
    async def live_metric(self, event):
        """Handle live metric broadcast"""
        await self.send(text_data=json.dumps({
            'type': 'metric_update',
            'data': event['data']
        }))
