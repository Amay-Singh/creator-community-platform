"""
WebSocket Consumer Tests for Real-time Messaging
Tests P5-004: Real-time messaging with typing indicators and presence
"""
import json
import pytest
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from accounts.models import CreatorProfile
from chat.models import ChatRoom, ChatMessage
from chat.consumers import ChatConsumer
from creator_platform.asgi import application

User = get_user_model()


class ChatConsumerTestCase(TransactionTestCase):
    """Test cases for ChatConsumer WebSocket functionality"""
    
    def setUp(self):
        """Set up test data"""
        cache.clear()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2', 
            email='test2@example.com',
            password='testpass123'
        )
        
        # Create profiles
        self.profile1 = CreatorProfile.objects.create(
            user=self.user1,
            display_name='Test User 1',
            bio='Test bio 1'
        )
        self.profile2 = CreatorProfile.objects.create(
            user=self.user2,
            display_name='Test User 2',
            bio='Test bio 2'
        )
        
        # Create chat room
        self.room = ChatRoom.objects.create(
            room_type='direct',
            created_by=self.profile1
        )
        self.room.participants.add(self.profile1, self.profile2)
    
    async def test_websocket_connect_authenticated(self):
        """Test WebSocket connection with authenticated user"""
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{self.room.id}/",
            headers=[(b"authorization", b"Bearer test-token")]
        )
        
        # Mock authentication
        communicator.scope["user"] = self.user1
        
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        
        # Should receive presence notification
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'user_presence')
        self.assertEqual(response['user_id'], str(self.user1.id))
        self.assertTrue(response['is_online'])
        
        await communicator.disconnect()
    
    async def test_websocket_connect_anonymous_rejected(self):
        """Test WebSocket connection rejection for anonymous users"""
        from django.contrib.auth.models import AnonymousUser
        
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{self.room.id}/"
        )
        
        # Mock anonymous user
        communicator.scope["user"] = AnonymousUser()
        
        connected, subprotocol = await communicator.connect()
        self.assertFalse(connected)
    
    async def test_send_chat_message(self):
        """Test sending a chat message via WebSocket"""
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{self.room.id}/"
        )
        communicator.scope["user"] = self.user1
        
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        
        # Skip presence notification
        await communicator.receive_json_from()
        
        # Send chat message
        await communicator.send_json_to({
            'type': 'chat_message',
            'content': 'Hello, World!',
            'message_type': 'text'
        })
        
        # Should receive the message back
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'chat_message')
        self.assertIn('message', response)
        self.assertEqual(response['message']['content'], 'Hello, World!')
        
        # Verify message was saved to database
        message = await database_sync_to_async(ChatMessage.objects.get)(
            room=self.room,
            content='Hello, World!'
        )
        self.assertEqual(message.sender, self.profile1)
        
        await communicator.disconnect()
    
    async def test_typing_indicator(self):
        """Test typing indicator functionality"""
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{self.room.id}/"
        )
        communicator.scope["user"] = self.user1
        
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        
        # Skip presence notification
        await communicator.receive_json_from()
        
        # Send typing indicator
        await communicator.send_json_to({
            'type': 'typing_indicator',
            'is_typing': True
        })
        
        # Check cache for typing status
        cache_key = f"typing_{self.room.id}_{self.user1.id}"
        typing_status = cache.get(cache_key)
        self.assertTrue(typing_status)
        
        await communicator.disconnect()
    
    async def test_read_receipt(self):
        """Test read receipt functionality"""
        # Create a message first
        message = await database_sync_to_async(ChatMessage.objects.create)(
            room=self.room,
            sender=self.profile2,
            content='Test message for read receipt'
        )
        
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{self.room.id}/"
        )
        communicator.scope["user"] = self.user1
        
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        
        # Skip presence notification
        await communicator.receive_json_from()
        
        # Send read receipt
        await communicator.send_json_to({
            'type': 'read_receipt',
            'message_id': str(message.id)
        })
        
        # Should receive read receipt broadcast
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'read_receipt')
        self.assertEqual(response['message_id'], str(message.id))
        self.assertEqual(response['reader_id'], str(self.user1.id))
        
        await communicator.disconnect()
    
    async def test_rate_limiting(self):
        """Test message rate limiting"""
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{self.room.id}/"
        )
        communicator.scope["user"] = self.user1
        
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        
        # Skip presence notification
        await communicator.receive_json_from()
        
        # Send messages rapidly to trigger rate limit
        for i in range(35):  # Exceeds 30 message limit
            await communicator.send_json_to({
                'type': 'chat_message',
                'content': f'Message {i}',
                'message_type': 'text'
            })
        
        # Should receive rate limit error
        error_received = False
        for _ in range(10):  # Check multiple responses
            try:
                response = await communicator.receive_json_from(timeout=1)
                if response.get('type') == 'error' and 'rate limit' in response.get('message', '').lower():
                    error_received = True
                    break
            except:
                break
        
        self.assertTrue(error_received, "Rate limit error should be received")
        
        await communicator.disconnect()
    
    async def test_user_presence_update(self):
        """Test user presence tracking"""
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{self.room.id}/"
        )
        communicator.scope["user"] = self.user1
        
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        
        # Check presence in cache
        cache_key = f"presence_{self.user1.id}"
        presence = cache.get(cache_key)
        self.assertIsNotNone(presence)
        self.assertTrue(presence['is_online'])
        self.assertEqual(presence['room_id'], str(self.room.id))
        
        await communicator.disconnect()
        
        # Check presence after disconnect
        presence = cache.get(cache_key)
        self.assertIsNotNone(presence)
        self.assertFalse(presence['is_online'])
    
    async def test_invalid_json_handling(self):
        """Test handling of invalid JSON messages"""
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{self.room.id}/"
        )
        communicator.scope["user"] = self.user1
        
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        
        # Skip presence notification
        await communicator.receive_json_from()
        
        # Send invalid JSON
        await communicator.send_to(text_data="invalid json")
        
        # Should receive error response
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'error')
        self.assertIn('Invalid JSON', response['message'])
        
        await communicator.disconnect()
    
    async def test_empty_message_rejection(self):
        """Test rejection of empty messages"""
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{self.room.id}/"
        )
        communicator.scope["user"] = self.user1
        
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        
        # Skip presence notification
        await communicator.receive_json_from()
        
        # Send empty message
        await communicator.send_json_to({
            'type': 'chat_message',
            'content': '',
            'message_type': 'text'
        })
        
        # Should receive error response
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'error')
        self.assertIn('cannot be empty', response['message'])
        
        await communicator.disconnect()


@pytest.mark.asyncio
class TestNotificationConsumer:
    """Test cases for NotificationConsumer"""
    
    async def test_notification_consumer_connect(self):
        """Test notification consumer connection"""
        user = await database_sync_to_async(User.objects.create_user)(
            username='notifuser',
            email='notif@example.com',
            password='testpass123'
        )
        
        communicator = WebsocketCommunicator(
            application,
            f"/ws/notifications/{user.id}/"
        )
        communicator.scope["user"] = user
        
        connected, subprotocol = await communicator.connect()
        assert connected
        
        await communicator.disconnect()
    
    async def test_notification_message_broadcast(self):
        """Test notification message broadcasting"""
        user = await database_sync_to_async(User.objects.create_user)(
            username='notifuser2',
            email='notif2@example.com',
            password='testpass123'
        )
        
        communicator = WebsocketCommunicator(
            application,
            f"/ws/notifications/{user.id}/"
        )
        communicator.scope["user"] = user
        
        connected, subprotocol = await communicator.connect()
        assert connected
        
        # Simulate notification broadcast
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        
        await channel_layer.group_send(
            f'notifications_{user.id}',
            {
                'type': 'notification_message',
                'notification': {
                    'id': '123',
                    'type': 'test_notification',
                    'message': 'Test notification'
                },
                'timestamp': '2025-08-20T08:00:00Z'
            }
        )
        
        # Should receive notification
        response = await communicator.receive_json_from()
        assert response['type'] == 'notification'
        assert response['notification']['message'] == 'Test notification'
        
        await communicator.disconnect()
