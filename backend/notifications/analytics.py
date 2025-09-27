"""
Notification Analytics Service

Provides analytics and monitoring for the notification system including:
- Delivery tracking and success rates
- User engagement metrics
- Performance monitoring
- Real-time dashboard data
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.db.models import Count, Q, Avg, F
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache
from .models import Notification, MatchNotification, NotificationSubscription

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationAnalytics:
    """Analytics service for notification system"""
    
    CACHE_TIMEOUT = 300  # 5 minutes
    
    @classmethod
    def get_delivery_stats(cls, days: int = 7) -> Dict[str, Any]:
        """Get notification delivery statistics"""
        cache_key = f"notification_delivery_stats_{days}"
        stats = cache.get(cache_key)
        
        if stats is None:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # Total notifications sent
            total_sent = Notification.objects.filter(
                created_at__gte=start_date
            ).count()
            
            # Read notifications
            total_read = Notification.objects.filter(
                created_at__gte=start_date,
                read_at__isnull=False
            ).count()
            
            # Notifications by type
            by_type = list(Notification.objects.filter(
                created_at__gte=start_date
            ).values('type').annotate(
                count=Count('id'),
                read_count=Count('id', filter=Q(read_at__isnull=False))
            ).order_by('-count'))
            
            # Calculate read rates
            for item in by_type:
                item['read_rate'] = (
                    item['read_count'] / item['count'] * 100 
                    if item['count'] > 0 else 0
                )
            
            # Daily breakdown
            daily_stats = list(Notification.objects.filter(
                created_at__gte=start_date
            ).extra(
                select={'day': "DATE(created_at)"}
            ).values('day').annotate(
                sent=Count('id'),
                read=Count('id', filter=Q(read_at__isnull=False))
            ).order_by('day'))
            
            stats = {
                'period': f'{days} days',
                'total_sent': total_sent,
                'total_read': total_read,
                'read_rate': total_read / total_sent * 100 if total_sent > 0 else 0,
                'by_type': by_type,
                'daily_stats': daily_stats
            }
            
            cache.set(cache_key, stats, cls.CACHE_TIMEOUT)
        
        return stats
    
    @classmethod
    def get_user_engagement_metrics(cls, days: int = 30) -> Dict[str, Any]:
        """Get user engagement metrics"""
        cache_key = f"user_engagement_metrics_{days}"
        metrics = cache.get(cache_key)
        
        if metrics is None:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # Active users (users who received notifications)
            active_users = User.objects.filter(
                notifications__created_at__gte=start_date
            ).distinct().count()
            
            # Engaged users (users who read notifications)
            engaged_users = User.objects.filter(
                notifications__created_at__gte=start_date,
                notifications__read_at__isnull=False
            ).distinct().count()
            
            # Average notifications per user
            avg_notifications = Notification.objects.filter(
                created_at__gte=start_date
            ).values('user').annotate(
                count=Count('id')
            ).aggregate(
                avg_count=Avg('count')
            )['avg_count'] or 0
            
            # Users with push subscriptions
            push_subscribers = NotificationSubscription.objects.filter(
                push_subscription__isnull=False
            ).exclude(push_subscription={}).count()
            
            # Top engaged users
            top_users = list(User.objects.filter(
                notifications__created_at__gte=start_date
            ).annotate(
                notification_count=Count('notifications'),
                read_count=Count('notifications', filter=Q(notifications__read_at__isnull=False))
            ).filter(notification_count__gt=0).annotate(
                engagement_rate=F('read_count') * 100.0 / F('notification_count')
            ).order_by('-engagement_rate')[:10].values(
                'id', 'username', 'notification_count', 'read_count', 'engagement_rate'
            ))
            
            metrics = {
                'period': f'{days} days',
                'active_users': active_users,
                'engaged_users': engaged_users,
                'engagement_rate': engaged_users / active_users * 100 if active_users > 0 else 0,
                'avg_notifications_per_user': round(avg_notifications, 2),
                'push_subscribers': push_subscribers,
                'top_engaged_users': top_users
            }
            
            cache.set(cache_key, metrics, cls.CACHE_TIMEOUT)
        
        return metrics
    
    @classmethod
    def get_match_notification_analytics(cls, days: int = 7) -> Dict[str, Any]:
        """Get analytics specific to match notifications"""
        cache_key = f"match_notification_analytics_{days}"
        analytics = cache.get(cache_key)
        
        if analytics is None:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # Match notifications by type
            match_stats = list(MatchNotification.objects.filter(
                created_at__gte=start_date
            ).values('notification_type').annotate(
                count=Count('id'),
                read_count=Count('id', filter=Q(read_at__isnull=False))
            ).order_by('-count'))
            
            # Calculate read rates
            for stat in match_stats:
                stat['read_rate'] = (
                    stat['read_count'] / stat['count'] * 100 
                    if stat['count'] > 0 else 0
                )
            
            # Average compatibility scores for new matches (placeholder)
            # Note: Compatibility scores are stored in metadata, would need custom aggregation
            avg_compatibility = 0.0
            
            # Match notification response times (time to read)
            response_times = list(MatchNotification.objects.filter(
                created_at__gte=start_date,
                read_at__isnull=False
            ).annotate(
                response_time=F('read_at') - F('created_at')
            ).values('notification_type').annotate(
                avg_response_seconds=Avg('response_time')
            ))
            
            analytics = {
                'period': f'{days} days',
                'match_stats': match_stats,
                'avg_compatibility_score': round(avg_compatibility, 3),
                'response_times': response_times
            }
            
            cache.set(cache_key, analytics, cls.CACHE_TIMEOUT)
        
        return analytics
    
    @classmethod
    def get_real_time_metrics(cls) -> Dict[str, Any]:
        """Get real-time system metrics"""
        cache_key = "real_time_metrics"
        metrics = cache.get(cache_key)
        
        if metrics is None:
            now = timezone.now()
            last_hour = now - timedelta(hours=1)
            last_24h = now - timedelta(hours=24)
            
            # Notifications in last hour
            last_hour_count = Notification.objects.filter(
                created_at__gte=last_hour
            ).count()
            
            # Notifications in last 24 hours
            last_24h_count = Notification.objects.filter(
                created_at__gte=last_24h
            ).count()
            
            # Unread notifications count
            unread_count = Notification.objects.filter(
                read_at__isnull=True
            ).count()
            
            # Active WebSocket connections (from subscriptions)
            active_connections = NotificationSubscription.objects.filter(
                websocket_connected=True
            ).count()
            
            # Recent notification types
            recent_types = list(Notification.objects.filter(
                created_at__gte=last_hour
            ).values('type').annotate(
                count=Count('id')
            ).order_by('-count')[:5])
            
            metrics = {
                'timestamp': now.isoformat(),
                'last_hour_notifications': last_hour_count,
                'last_24h_notifications': last_24h_count,
                'total_unread': unread_count,
                'active_connections': active_connections,
                'recent_notification_types': recent_types,
                'system_health': 'healthy' if last_hour_count < 1000 else 'high_load'
            }
            
            cache.set(cache_key, metrics, 60)  # Cache for 1 minute
        
        return metrics
    
    @classmethod
    def get_performance_metrics(cls, days: int = 7) -> Dict[str, Any]:
        """Get system performance metrics"""
        cache_key = f"performance_metrics_{days}"
        metrics = cache.get(cache_key)
        
        if metrics is None:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # Notification creation rate
            total_notifications = Notification.objects.filter(
                created_at__gte=start_date
            ).count()
            
            creation_rate = total_notifications / (days * 24)  # per hour
            
            # Peak hours analysis
            hourly_distribution = list(Notification.objects.filter(
                created_at__gte=start_date
            ).extra(
                select={'hour': "strftime('%%H', created_at)"}
            ).values('hour').annotate(
                count=Count('id')
            ).order_by('hour'))
            
            # Error rate (failed notifications)
            # Note: This would require additional error tracking in the future
            error_rate = 0  # Placeholder
            
            # Average processing time (placeholder for future implementation)
            avg_processing_time = 0.05  # 50ms placeholder
            
            metrics = {
                'period': f'{days} days',
                'total_notifications': total_notifications,
                'creation_rate_per_hour': round(creation_rate, 2),
                'hourly_distribution': hourly_distribution,
                'error_rate': error_rate,
                'avg_processing_time_ms': avg_processing_time * 1000
            }
            
            cache.set(cache_key, metrics, cls.CACHE_TIMEOUT)
        
        return metrics
    
    @classmethod
    def generate_dashboard_data(cls) -> Dict[str, Any]:
        """Generate comprehensive dashboard data"""
        return {
            'real_time': cls.get_real_time_metrics(),
            'delivery_stats': cls.get_delivery_stats(days=7),
            'user_engagement': cls.get_user_engagement_metrics(days=30),
            'match_analytics': cls.get_match_notification_analytics(days=7),
            'performance': cls.get_performance_metrics(days=7),
            'generated_at': timezone.now().isoformat()
        }
    
    @classmethod
    def track_notification_event(cls, event_type: str, notification_id: str, 
                                user_id: int, metadata: Dict = None):
        """Track notification events for analytics"""
        # This is a placeholder for future event tracking implementation
        # Could integrate with analytics services like Google Analytics, Mixpanel, etc.
        
        event_data = {
            'event_type': event_type,  # 'sent', 'delivered', 'read', 'clicked'
            'notification_id': notification_id,
            'user_id': user_id,
            'timestamp': timezone.now().isoformat(),
            'metadata': metadata or {}
        }
        
        logger.info(f"Notification event tracked: {event_data}")
        
        # Future: Send to analytics service
        # analytics_service.track_event(event_data)
    
    @classmethod
    def get_user_notification_history(cls, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get notification history for a specific user"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # User's notifications
        notifications = Notification.objects.filter(
            user_id=user_id,
            created_at__gte=start_date
        ).values('type', 'created_at', 'is_read', 'read_at')
        
        # User's match notifications
        match_notifications = MatchNotification.objects.filter(
            recipient_id=user_id,
            created_at__gte=start_date
        ).values('notification_type', 'created_at', 'is_read', 'read_at', 'compatibility_score')
        
        # User's subscription status
        subscription = NotificationSubscription.objects.filter(
            user_id=user_id
        ).first()
        
        # Calculate user engagement
        total_received = len(notifications)
        total_read = len([n for n in notifications if n['is_read']])
        
        return {
            'user_id': user_id,
            'period': f'{days} days',
            'total_received': total_received,
            'total_read': total_read,
            'read_rate': total_read / total_received * 100 if total_received > 0 else 0,
            'notifications': list(notifications),
            'match_notifications': list(match_notifications),
            'subscription_status': {
                'has_push': bool(subscription and subscription.push_subscription),
                'is_connected': bool(subscription and subscription.is_connected),
                'preferences': subscription.preferences if subscription else {}
            }
        }


class NotificationMonitor:
    """Real-time monitoring for notification system health"""
    
    @classmethod
    def check_system_health(cls) -> Dict[str, Any]:
        """Check overall system health"""
        now = timezone.now()
        last_hour = now - timedelta(hours=1)
        
        # Check notification creation rate
        recent_notifications = Notification.objects.filter(
            created_at__gte=last_hour
        ).count()
        
        # Check for stuck notifications (unread for > 24 hours)
        stuck_notifications = Notification.objects.filter(
            created_at__lt=now - timedelta(hours=24),
            read_at__isnull=True
        ).count()
        
        # Check WebSocket connections
        active_connections = NotificationSubscription.objects.filter(
            websocket_connected=True
        ).count()
        
        # Determine health status
        health_status = "healthy"
        issues = []
        
        if recent_notifications > 500:  # High load threshold
            health_status = "warning"
            issues.append("High notification volume detected")
        
        if stuck_notifications > 100:
            health_status = "warning"
            issues.append(f"{stuck_notifications} notifications unread for >24h")
        
        if active_connections == 0:
            health_status = "warning"
            issues.append("No active WebSocket connections")
        
        return {
            'status': health_status,
            'timestamp': now.isoformat(),
            'metrics': {
                'recent_notifications': recent_notifications,
                'stuck_notifications': stuck_notifications,
                'active_connections': active_connections
            },
            'issues': issues
        }
    
    @classmethod
    def get_alert_conditions(cls) -> List[Dict[str, Any]]:
        """Check for alert conditions"""
        alerts = []
        now = timezone.now()
        
        # High error rate alert (placeholder)
        # In a real implementation, this would check error logs
        
        # High unread notification count
        unread_count = Notification.objects.filter(read_at__isnull=True).count()
        if unread_count > 1000:
            alerts.append({
                'type': 'high_unread_count',
                'severity': 'warning',
                'message': f'High unread notification count: {unread_count}',
                'timestamp': now.isoformat()
            })
        
        # No recent notifications (system might be down)
        last_hour = now - timedelta(hours=1)
        recent_count = Notification.objects.filter(
            created_at__gte=last_hour
        ).count()
        
        if recent_count == 0:
            alerts.append({
                'type': 'no_recent_notifications',
                'severity': 'critical',
                'message': 'No notifications created in the last hour',
                'timestamp': now.isoformat()
            })
        
        return alerts
