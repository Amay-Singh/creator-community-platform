import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Notification, MatchNotification, NotificationSubscription
from .analytics import NotificationAnalytics, NotificationMonitor

User = get_user_model()


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
})
class NotificationAnalyticsTests(TestCase):
    """Test notification analytics functionality"""
    
    def setUp(self):
        cache.clear()  # Clear cache before each test
        
        self.users = []
        for i in range(5):
            user = User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='testpass123'
            )
            self.users.append(user)
    
    def test_get_delivery_stats(self):
        """Test delivery statistics calculation"""
        # Create test notifications
        now = timezone.now()
        
        for i, user in enumerate(self.users):
            for j in range(3):
                notification = Notification.objects.create(
                    user=user,
                    type='match_found',
                    created_at=now - timedelta(hours=i)
                )
                if j % 2 == 0:  # 2/3 read
                    notification.mark_as_read()
        
        stats = NotificationAnalytics.get_delivery_stats(days=7)
        
        self.assertEqual(stats['total_sent'], 15)
        self.assertEqual(stats['total_read'], 10)  # 2/3 of 15
        self.assertAlmostEqual(stats['read_rate'], 66.67, places=1)
        self.assertEqual(len(stats['by_type']), 1)
        self.assertEqual(stats['by_type'][0]['type'], 'match_found')
    
    def test_get_user_engagement_metrics(self):
        """Test user engagement metrics"""
        # Create notifications for users
        now = timezone.now()
        
        for i, user in enumerate(self.users[:3]):  # Only 3 users get notifications
            for j in range(2):
                notification = Notification.objects.create(
                    user=user,
                    type='match_found',
                    created_at=now - timedelta(hours=1)
                )
                if i < 2:  # First 2 users read notifications
                    notification.mark_as_read()
        
        # Create push subscriptions for some users
        for user in self.users[:2]:
            subscription = NotificationSubscription.objects.get(user=user)
            subscription.push_subscription = {'endpoint': 'test', 'keys': {}}
            subscription.save()
        
        metrics = NotificationAnalytics.get_user_engagement_metrics(days=30)
        
        self.assertEqual(metrics['active_users'], 3)
        self.assertEqual(metrics['engaged_users'], 2)
        self.assertAlmostEqual(metrics['engagement_rate'], 66.67, places=1)
        self.assertEqual(metrics['push_subscribers'], 2)
        self.assertEqual(metrics['avg_notifications_per_user'], 2.0)
    
    def test_get_match_notification_analytics(self):
        """Test match notification analytics"""
        now = timezone.now()
        
        # Create match notifications
        for i, user in enumerate(self.users[:3]):
            notification = MatchNotification.objects.create(
                recipient=user,
                notification_type='new_match',
                match_id=f'match-{i}',
                title=f'New Match {i}',
                message=f'You have a new match!',
                compatibility_score=0.8 + (i * 0.05),
                created_at=now - timedelta(hours=i)
            )
            if i < 2:
                notification.mark_as_read()
        
        analytics = NotificationAnalytics.get_match_notification_analytics(days=7)
        
        self.assertEqual(len(analytics['match_stats']), 1)
        self.assertEqual(analytics['match_stats'][0]['notification_type'], 'new_match')
        self.assertEqual(analytics['match_stats'][0]['count'], 3)
        self.assertEqual(analytics['match_stats'][0]['read_count'], 2)
        self.assertAlmostEqual(analytics['avg_compatibility_score'], 0.85, places=2)
    
    def test_get_real_time_metrics(self):
        """Test real-time metrics"""
        now = timezone.now()
        
        # Create recent notifications
        for i in range(3):
            Notification.objects.create(
                user=self.users[0],
                type='match_found',
                created_at=now - timedelta(minutes=30)
            )
        
        # Create older notifications
        for i in range(5):
            Notification.objects.create(
                user=self.users[1],
                type='collaboration_invite',
                created_at=now - timedelta(hours=12)
            )
        
        # Set some users as connected
        for user in self.users[:2]:
            subscription = NotificationSubscription.objects.get(user=user)
            subscription.websocket_connected = True
            subscription.save()
        
        metrics = NotificationAnalytics.get_real_time_metrics()
        
        self.assertEqual(metrics['last_hour_notifications'], 3)
        self.assertEqual(metrics['last_24h_notifications'], 8)
        self.assertEqual(metrics['active_connections'], 2)
        self.assertEqual(metrics['system_health'], 'healthy')
    
    def test_get_performance_metrics(self):
        """Test performance metrics"""
        now = timezone.now()
        
        # Create notifications spread across different hours
        for hour in range(24):
            for i in range(hour % 3 + 1):  # Variable count per hour
                Notification.objects.create(
                    user=self.users[i % len(self.users)],
                    type='match_found',
                    created_at=now - timedelta(hours=hour)
                )
        
        metrics = NotificationAnalytics.get_performance_metrics(days=7)
        
        self.assertGreater(metrics['total_notifications'], 0)
        self.assertGreater(metrics['creation_rate_per_hour'], 0)
        self.assertEqual(len(metrics['hourly_distribution']), 24)
        self.assertEqual(metrics['error_rate'], 0)  # Placeholder
    
    def test_generate_dashboard_data(self):
        """Test dashboard data generation"""
        # Create some test data
        now = timezone.now()
        
        for user in self.users[:2]:
            Notification.objects.create(
                user=user,
                type='match_found',
                created_at=now - timedelta(hours=1)
            )
        
        dashboard = NotificationAnalytics.generate_dashboard_data()
        
        self.assertIn('real_time', dashboard)
        self.assertIn('delivery_stats', dashboard)
        self.assertIn('user_engagement', dashboard)
        self.assertIn('match_analytics', dashboard)
        self.assertIn('performance', dashboard)
        self.assertIn('generated_at', dashboard)
    
    def test_get_user_notification_history(self):
        """Test user notification history"""
        user = self.users[0]
        now = timezone.now()
        
        # Create notifications for user
        for i in range(3):
            Notification.objects.create(
                user=user,
                type='match_found',
                created_at=now - timedelta(hours=i),
                is_read=(i < 2)
            )
        
        # Create match notifications
        for i in range(2):
            MatchNotification.objects.create(
                recipient=user,
                notification_type='new_match',
                match_id=f'match-{i}',
                title=f'Match {i}',
                message='Test match',
                created_at=now - timedelta(hours=i)
            )
        
        history = NotificationAnalytics.get_user_notification_history(user.id, days=30)
        
        self.assertEqual(history['user_id'], user.id)
        self.assertEqual(history['total_received'], 3)
        self.assertEqual(history['total_read'], 2)
        self.assertAlmostEqual(history['read_rate'], 66.67, places=1)
        self.assertEqual(len(history['notifications']), 3)
        self.assertEqual(len(history['match_notifications']), 2)


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
})
class NotificationMonitorTests(TestCase):
    """Test notification monitoring functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_check_system_health_healthy(self):
        """Test system health check when system is healthy"""
        now = timezone.now()
        
        # Create some recent notifications (not too many)
        for i in range(5):
            Notification.objects.create(
                user=self.user,
                type='match_found',
                created_at=now - timedelta(minutes=30)
            )
        
        # Set user as connected
        subscription = NotificationSubscription.objects.get(user=self.user)
        subscription.websocket_connected = True
        subscription.save()
        
        health = NotificationMonitor.check_system_health()
        
        self.assertEqual(health['status'], 'healthy')
        self.assertEqual(len(health['issues']), 0)
        self.assertEqual(health['metrics']['recent_notifications'], 5)
        self.assertEqual(health['metrics']['active_connections'], 1)
    
    def test_check_system_health_warning_high_load(self):
        """Test system health check with high load warning"""
        now = timezone.now()
        
        # Create many recent notifications
        for i in range(600):  # Above threshold
            Notification.objects.create(
                user=self.user,
                type='match_found',
                created_at=now - timedelta(minutes=30)
            )
        
        health = NotificationMonitor.check_system_health()
        
        self.assertEqual(health['status'], 'warning')
        self.assertIn('High notification volume detected', health['issues'])
    
    def test_check_system_health_warning_stuck_notifications(self):
        """Test system health check with stuck notifications"""
        now = timezone.now()
        
        # Create old unread notifications
        for i in range(150):  # Above threshold
            Notification.objects.create(
                user=self.user,
                type='match_found',
                created_at=now - timedelta(hours=30),  # Old
                is_read=False
            )
        
        health = NotificationMonitor.check_system_health()
        
        self.assertEqual(health['status'], 'warning')
        self.assertTrue(any('unread for >24h' in issue for issue in health['issues']))
    
    def test_get_alert_conditions_high_unread(self):
        """Test alert conditions for high unread count"""
        # Create many unread notifications
        for i in range(1200):  # Above threshold
            Notification.objects.create(
                user=self.user,
                type='match_found',
                is_read=False
            )
        
        alerts = NotificationMonitor.get_alert_conditions()
        
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['type'], 'high_unread_count')
        self.assertEqual(alerts[0]['severity'], 'warning')
    
    def test_get_alert_conditions_no_recent_notifications(self):
        """Test alert conditions when no recent notifications"""
        # Don't create any recent notifications
        
        alerts = NotificationMonitor.get_alert_conditions()
        
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['type'], 'no_recent_notifications')
        self.assertEqual(alerts[0]['severity'], 'critical')


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
})
class NotificationAnalyticsAPITests(APITestCase):
    """Test notification analytics API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create some test data
        now = timezone.now()
        for i in range(3):
            notification = Notification.objects.create(
                user=self.user,
                type='match_found',
                created_at=now - timedelta(hours=i)
            )
            if i < 2:
                notification.mark_as_read()
    
    def test_analytics_dashboard_endpoint(self):
        """Test analytics dashboard API endpoint"""
        response = self.client.get('/api/notifications/analytics/dashboard/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('real_time', response.data)
        self.assertIn('delivery_stats', response.data)
        self.assertIn('user_engagement', response.data)
        self.assertIn('match_analytics', response.data)
        self.assertIn('performance', response.data)
    
    def test_analytics_delivery_stats_endpoint(self):
        """Test delivery stats API endpoint"""
        response = self.client.get('/api/notifications/analytics/delivery/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_sent', response.data)
        self.assertIn('total_read', response.data)
        self.assertIn('read_rate', response.data)
    
    def test_analytics_delivery_stats_with_days_param(self):
        """Test delivery stats with days parameter"""
        response = self.client.get('/api/notifications/analytics/delivery/?days=14')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['period'], '14 days')
    
    def test_analytics_user_engagement_endpoint(self):
        """Test user engagement API endpoint"""
        response = self.client.get('/api/notifications/analytics/engagement/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('active_users', response.data)
        self.assertIn('engaged_users', response.data)
        self.assertIn('engagement_rate', response.data)
    
    def test_analytics_real_time_metrics_endpoint(self):
        """Test real-time metrics API endpoint"""
        response = self.client.get('/api/notifications/analytics/realtime/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('last_hour_notifications', response.data)
        self.assertIn('last_24h_notifications', response.data)
        self.assertIn('system_health', response.data)
    
    def test_analytics_user_history_endpoint(self):
        """Test user history API endpoint"""
        response = self.client.get('/api/notifications/analytics/user-history/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_id'], self.user.id)
        self.assertIn('total_received', response.data)
        self.assertIn('notifications', response.data)
    
    def test_system_health_endpoint(self):
        """Test system health API endpoint"""
        response = self.client.get('/api/notifications/health/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('metrics', response.data)
    
    def test_system_alerts_endpoint(self):
        """Test system alerts API endpoint"""
        response = self.client.get('/api/notifications/alerts/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('alerts', response.data)
        self.assertIsInstance(response.data['alerts'], list)
    
    def test_analytics_endpoints_require_authentication(self):
        """Test that analytics endpoints require authentication"""
        self.client.force_authenticate(user=None)
        
        endpoints = [
            '/api/notifications/analytics/dashboard/',
            '/api/notifications/analytics/delivery/',
            '/api/notifications/analytics/engagement/',
            '/api/notifications/analytics/realtime/',
            '/api/notifications/health/',
            '/api/notifications/alerts/',
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
})
class NotificationAnalyticsCacheTests(TestCase):
    """Test caching behavior in analytics"""
    
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_delivery_stats_caching(self):
        """Test that delivery stats are cached"""
        # Create test data
        Notification.objects.create(user=self.user, type='match_found')
        
        # First call should hit database
        with self.assertNumQueries(4):  # Expect some queries
            stats1 = NotificationAnalytics.get_delivery_stats(days=7)
        
        # Second call should use cache
        with self.assertNumQueries(0):  # No queries expected
            stats2 = NotificationAnalytics.get_delivery_stats(days=7)
        
        self.assertEqual(stats1, stats2)
    
    def test_real_time_metrics_caching(self):
        """Test that real-time metrics are cached with shorter timeout"""
        # Create test data
        Notification.objects.create(user=self.user, type='match_found')
        
        # First call should hit database
        metrics1 = NotificationAnalytics.get_real_time_metrics()
        
        # Second call should use cache
        with self.assertNumQueries(0):
            metrics2 = NotificationAnalytics.get_real_time_metrics()
        
        self.assertEqual(metrics1, metrics2)
    
    @patch('notifications.analytics.cache')
    def test_cache_key_uniqueness(self, mock_cache):
        """Test that different parameters create different cache keys"""
        mock_cache.get.return_value = None
        mock_cache.set.return_value = None
        
        NotificationAnalytics.get_delivery_stats(days=7)
        NotificationAnalytics.get_delivery_stats(days=14)
        
        # Should have different cache keys
        call_args = [call[0][0] for call in mock_cache.set.call_args_list]
        self.assertIn('notification_delivery_stats_7', call_args)
        self.assertIn('notification_delivery_stats_14', call_args)
