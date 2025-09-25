import json
import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Notification, MatchNotification, NotificationSubscription
from .services import NotificationService, MatchNotificationService
from .consumers import NotificationConsumer
from .push_service import push_service
from ai_services.models import MatchResult, MatchFeedback, CreatorEmbedding

User = get_user_model()


class NotificationServiceTests(TestCase):
    """Test notification services"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @patch('notifications.services.channel_layer')
    def test_send_notification(self, mock_channel_layer):
        """Test sending notification"""
        notification = NotificationService.send_notification(
            user_id=self.user.id,
            notification_type='match_found',
            title='Test Notification',
            message='Test message',
            payload={'test': 'data'}
        )
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.type, 'match_found')
        
        # Check that real-time notification was sent
        mock_channel_layer.group_send.assert_called_once()
    
    def test_get_user_notifications(self):
        """Test getting user notifications"""
        # Create test notifications
        for i in range(5):
            Notification.objects.create(
                user=self.user,
                type='match_found',
                payload={'index': i}
            )
        
        notifications = NotificationService.get_user_notifications(self.user.id, limit=3)
        
        self.assertEqual(len(notifications), 3)
        self.assertEqual(notifications[0]['payload']['index'], 4)  # Most recent first
    
    def test_mark_notification_read(self):
        """Test marking notification as read"""
        notification = Notification.objects.create(
            user=self.user,
            type='match_found'
        )
        
        success = NotificationService.mark_notification_read(
            str(notification.id),
            self.user.id
        )
        
        self.assertTrue(success)
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)


class MatchNotificationServiceTests(TestCase):
    """Test match notification services"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
    
    @patch('notifications.services.channel_layer')
    def test_notify_new_match(self, mock_channel_layer):
        """Test new match notification"""
        notification = MatchNotificationService.notify_new_match(
            requester_id=self.user1.id,
            matched_creator_id=self.user2.id,
            match_id='test-match-id',
            compatibility_score=0.85
        )
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.recipient, self.user1)
        self.assertEqual(notification.notification_type, 'new_match')
        self.assertIn('85%', notification.message)
    
    @patch('notifications.services.channel_layer')
    def test_notify_match_status_change(self, mock_channel_layer):
        """Test match status change notification"""
        notification = MatchNotificationService.notify_match_status_change(
            user_id=self.user1.id,
            match_id='test-match-id',
            old_status='pending',
            new_status='accepted'
        )
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.notification_type, 'match_status_changed')
        self.assertIn('accepted', notification.message)


class NotificationAPITests(APITestCase):
    """Test notification API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_match_notifications(self):
        """Test getting match notifications via API"""
        # Create test match notifications
        for i in range(3):
            MatchNotification.objects.create(
                recipient=self.user,
                notification_type='new_match',
                match_id=f'match-{i}',
                title=f'Match {i}',
                message=f'Test match notification {i}'
            )
        
        response = self.client.get('/api/notifications/matches/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_notification_preferences(self):
        """Test notification preferences API"""
        # Test GET preferences
        response = self.client.get('/api/notifications/preferences/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test PUT preferences
        new_preferences = {
            'match_found': False,
            'sound_enabled': True
        }
        response = self.client.put('/api/notifications/preferences/', {
            'preferences': new_preferences
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify preferences were saved
        subscription = NotificationSubscription.objects.get(user=self.user)
        self.assertFalse(subscription.get_preference('match_found'))
        self.assertTrue(subscription.get_preference('sound_enabled'))


class WebSocketConsumerTests(TransactionTestCase):
    """Test WebSocket consumers"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @pytest.mark.asyncio
    async def test_notification_consumer_connect(self):
        """Test WebSocket connection"""
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            "/ws/notifications/"
        )
        communicator.scope["user"] = self.user
        
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        
        # Should receive connection confirmation
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'connection_established')
        
        await communicator.disconnect()
    
    @pytest.mark.asyncio
    async def test_notification_consumer_ping_pong(self):
        """Test ping/pong functionality"""
        communicator = WebsocketCommunicator(
            NotificationConsumer.as_asgi(),
            "/ws/notifications/"
        )
        communicator.scope["user"] = self.user
        
        await communicator.connect()
        await communicator.receive_json_from()  # Connection message
        
        # Send ping
        await communicator.send_json_to({'type': 'ping'})
        
        # Should receive pong
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'pong')
        
        await communicator.disconnect()


class PushNotificationTests(TestCase):
    """Test push notification service"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Get or update the subscription created by signal
        self.subscription, created = NotificationSubscription.objects.get_or_create(
            user=self.user,
            defaults={
                'push_subscription': {
                    'endpoint': 'https://fcm.googleapis.com/fcm/send/test',
                    'keys': {
                        'p256dh': 'test-p256dh-key',
                        'auth': 'test-auth-key'
                    }
                }
            }
        )
        if not created:
            self.subscription.push_subscription = {
                'endpoint': 'https://fcm.googleapis.com/fcm/send/test',
                'keys': {
                    'p256dh': 'test-p256dh-key',
                    'auth': 'test-auth-key'
                }
            }
            self.subscription.save()
    
    @patch('notifications.push_service.webpush')
    def test_send_push_notification(self, mock_webpush):
        """Test sending push notification"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_webpush.return_value = mock_response
        
        success = push_service.send_push_notification(
            user_id=self.user.id,
            title='Test Push',
            message='Test message'
        )
        
        self.assertTrue(success)
        mock_webpush.assert_called_once()
    
    @patch('notifications.push_service.webpush')
    def test_send_match_notification_push(self, mock_webpush):
        """Test sending match notification push"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_webpush.return_value = mock_response
        
        match_data = {
            'match_id': 'test-match',
            'matched_creator_name': 'John Doe',
            'compatibility_score': 0.85
        }
        
        success = push_service.send_match_notification_push(
            user_id=self.user.id,
            match_data=match_data
        )
        
        self.assertTrue(success)
        mock_webpush.assert_called_once()
    
    def test_subscribe_user(self):
        """Test subscribing user to push notifications"""
        subscription_data = {
            'endpoint': 'https://fcm.googleapis.com/fcm/send/new',
            'keys': {
                'p256dh': 'new-p256dh-key',
                'auth': 'new-auth-key'
            }
        }
        
        success = push_service.subscribe_user(self.user.id, subscription_data)
        
        self.assertTrue(success)
        
        # Verify subscription was updated
        subscription = NotificationSubscription.objects.get(user=self.user)
        self.assertEqual(subscription.push_subscription, subscription_data)


class NotificationSignalTests(TestCase):
    """Test notification signals"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
    
    @patch('notifications.services.channel_layer')
    def test_match_result_created_signal(self, mock_channel_layer):
        """Test signal when match result is created"""
        # Create embeddings first
        embedding1 = CreatorEmbedding.objects.create(
            creator=self.user1,
            embedding_vector=[0.1] * 384,
            skills=['python', 'django'],
            interests=['web development']
        )
        
        embedding2 = CreatorEmbedding.objects.create(
            creator=self.user2,
            embedding_vector=[0.2] * 384,
            skills=['react', 'javascript'],
            interests=['frontend development']
        )
        
        # Create match result - should trigger signal
        match_result = MatchResult.objects.create(
            requester=self.user1,
            matched_creator=self.user2,
            compatibility_score=0.85,
            matching_criteria={'skills': ['python']},
            requester_embedding=embedding1,
            matched_embedding=embedding2
        )
        
        # Check that notification was created
        notifications = MatchNotification.objects.filter(
            recipient=self.user1,
            notification_type='new_match'
        )
        self.assertEqual(notifications.count(), 1)
    
    @patch('notifications.services.channel_layer')
    def test_user_created_signal(self, mock_channel_layer):
        """Test signal when new user is created"""
        new_user = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            password='testpass123'
        )
        
        # Check that notification subscription was created
        subscription = NotificationSubscription.objects.filter(user=new_user)
        self.assertEqual(subscription.count(), 1)


class NotificationPerformanceTests(TestCase):
    """Test notification system performance"""
    
    def setUp(self):
        self.users = []
        for i in range(10):
            user = User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='testpass123'
            )
            self.users.append(user)
    
    def test_bulk_notification_creation(self):
        """Test creating notifications in bulk"""
        import time
        
        start_time = time.time()
        
        notifications = []
        for user in self.users:
            for j in range(10):
                notifications.append(Notification(
                    user=user,
                    type='match_found',
                    payload={'index': j}
                ))
        
        Notification.objects.bulk_create(notifications)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Should create 100 notifications quickly
        self.assertLess(creation_time, 1.0)  # Less than 1 second
        self.assertEqual(Notification.objects.count(), 100)
    
    def test_notification_query_performance(self):
        """Test notification query performance"""
        # Create notifications for users
        for user in self.users:
            for j in range(20):
                Notification.objects.create(
                    user=user,
                    type='match_found',
                    payload={'index': j}
                )
        
        import time
        
        # Test getting notifications for a user
        start_time = time.time()
        
        notifications = list(Notification.objects.filter(
            user=self.users[0]
        ).order_by('-created_at')[:10])
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # Should be fast
        self.assertLess(query_time, 0.1)  # Less than 100ms
        self.assertEqual(len(notifications), 10)


class NotificationIntegrationTests(APITestCase):
    """Integration tests for the complete notification flow"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user1)
    
    @patch('notifications.services.channel_layer')
    @patch('notifications.push_service.webpush')
    def test_complete_match_notification_flow(self, mock_webpush, mock_channel_layer):
        """Test complete notification flow from match creation to delivery"""
        # Setup push notification
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_webpush.return_value = mock_response
        
        NotificationSubscription.objects.create(
            user=self.user1,
            push_subscription={'endpoint': 'test', 'keys': {'p256dh': 'test', 'auth': 'test'}}
        )
        
        # Create embeddings
        embedding1 = CreatorEmbedding.objects.create(
            creator=self.user1,
            embedding_vector=[0.1] * 384,
            skills=['python'],
            interests=['web development']
        )
        
        embedding2 = CreatorEmbedding.objects.create(
            creator=self.user2,
            embedding_vector=[0.2] * 384,
            skills=['react'],
            interests=['frontend']
        )
        
        # Create match result - triggers notifications
        match_result = MatchResult.objects.create(
            requester=self.user1,
            matched_creator=self.user2,
            compatibility_score=0.85,
            matching_criteria={'skills': ['python']},
            requester_embedding=embedding1,
            matched_embedding=embedding2
        )
        
        # Check that notifications were created
        notifications = Notification.objects.filter(user=self.user1)
        self.assertGreater(notifications.count(), 0)
        
        match_notifications = MatchNotification.objects.filter(recipient=self.user1)
        self.assertGreater(match_notifications.count(), 0)
        
        # Check that real-time notification was sent
        mock_channel_layer.group_send.assert_called()
        
        # Test API endpoints
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get('/api/notifications/unread-count/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data['unread_count'], 0)
