"""
API Tests for Real-time Messaging System
Tests P5-004: Chat API endpoints and functionality
"""
import json
import tempfile
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test.utils import override_settings
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import CreatorProfile
from chat.models import ChatRoom, ChatMessage, MessageReadStatus

User = get_user_model()


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
})
class ChatAPITestCase(TestCase):
    """Test cases for Chat API endpoints"""
    
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
        
        # Set up API clients
        self.client1 = APIClient()
        self.client1.force_authenticate(user=self.user1)
        
        self.client2 = APIClient()
        self.client2.force_authenticate(user=self.user2)
    
    def test_list_chat_rooms(self):
        """Test listing chat rooms for authenticated user"""
        url = reverse('chat:room_list')
        response = self.client1.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(self.room.id))
        self.assertEqual(response.data[0]['room_type'], 'direct')
    
    def test_create_chat_room(self):
        """Test creating a new chat room"""
        url = reverse('chat:room_list')
        data = {
            'room_type': 'group',
            'name': 'Test Group Chat'
        }
        
        response = self.client1.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Group Chat')
        self.assertEqual(response.data['room_type'], 'group')
        
        # Verify room was created in database
        room = ChatRoom.objects.get(id=response.data['id'])
        self.assertEqual(room.created_by, self.profile1)
        self.assertTrue(room.participants.filter(id=self.profile1.id).exists())
    
    def test_get_room_detail(self):
        """Test getting detailed room information"""
        url = reverse('chat:room_detail', kwargs={'room_id': self.room.id})
        response = self.client1.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.room.id))
        self.assertEqual(len(response.data['participants']), 2)
    
    def test_get_room_detail_unauthorized(self):
        """Test getting room detail without access"""
        # Create user not in room
        user3 = User.objects.create_user(
            username='testuser3',
            email='test3@example.com',
            password='testpass123'
        )
        profile3 = CreatorProfile.objects.create(
            user=user3,
            display_name='Test User 3'
        )
        
        client3 = APIClient()
        client3.force_authenticate(user=user3)
        
        url = reverse('chat:room_detail', kwargs={'room_id': self.room.id})
        response = client3.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_list_messages(self):
        """Test listing messages in a room"""
        # Create test messages
        message1 = ChatMessage.objects.create(
            room=self.room,
            sender=self.profile1,
            content='First message'
        )
        message2 = ChatMessage.objects.create(
            room=self.room,
            sender=self.profile2,
            content='Second message'
        )
        
        url = reverse('chat:room_messages', kwargs={'room_id': self.room.id})
        response = self.client1.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Messages should be ordered by created_at descending
        self.assertEqual(response.data['results'][0]['content'], 'Second message')
        self.assertEqual(response.data['results'][1]['content'], 'First message')
    
    def test_send_message(self):
        """Test sending a message via API"""
        url = reverse('chat:room_messages', kwargs={'room_id': self.room.id})
        data = {
            'content': 'Hello from API!',
            'message_type': 'text'
        }
        
        response = self.client1.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Hello from API!')
        self.assertEqual(response.data['sender']['id'], str(self.profile1.id))
        
        # Verify message was saved
        message = ChatMessage.objects.get(id=response.data['id'])
        self.assertEqual(message.content, 'Hello from API!')
        self.assertEqual(message.sender, self.profile1)
        
        # Verify room timestamp was updated
        self.room.refresh_from_db()
        self.assertIsNotNone(self.room.last_message_at)
    
    def test_send_message_unauthorized(self):
        """Test sending message to room without access"""
        user3 = User.objects.create_user(
            username='testuser3',
            email='test3@example.com',
            password='testpass123'
        )
        profile3 = CreatorProfile.objects.create(
            user=user3,
            display_name='Test User 3'
        )
        
        client3 = APIClient()
        client3.force_authenticate(user=user3)
        
        url = reverse('chat:room_messages', kwargs={'room_id': self.room.id})
        data = {
            'content': 'Unauthorized message',
            'message_type': 'text'
        }
        
        response = client3.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_mark_messages_read(self):
        """Test marking messages as read"""
        # Create unread messages
        message1 = ChatMessage.objects.create(
            room=self.room,
            sender=self.profile2,
            content='Unread message 1'
        )
        message2 = ChatMessage.objects.create(
            room=self.room,
            sender=self.profile2,
            content='Unread message 2'
        )
        
        url = reverse('chat:mark_messages_read', kwargs={'room_id': self.room.id})
        response = self.client1.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['marked_read'], 2)
        
        # Verify read statuses were created
        self.assertTrue(
            MessageReadStatus.objects.filter(
                message=message1,
                reader=self.profile1
            ).exists()
        )
        self.assertTrue(
            MessageReadStatus.objects.filter(
                message=message2,
                reader=self.profile1
            ).exists()
        )
    
    def test_get_user_presence(self):
        """Test getting user presence information"""
        # Set presence in cache
        cache.set(f"presence_{self.user1.id}", {
            'is_online': True,
            'last_seen': '2025-08-20T08:00:00Z',
            'room_id': str(self.room.id)
        })
        cache.set(f"presence_{self.user2.id}", {
            'is_online': False,
            'last_seen': '2025-08-20T07:30:00Z',
            'room_id': None
        })
        
        url = reverse('chat:user_presence')
        response = self.client1.get(url, {
            'user_ids': [str(self.user1.id), str(self.user2.id)]
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data[str(self.user1.id)]['is_online'])
        self.assertFalse(response.data[str(self.user2.id)]['is_online'])
    
    def test_get_typing_status(self):
        """Test getting typing indicators for a room"""
        # Set typing status in cache
        cache.set(f"typing_{self.room.id}_{self.user2.id}", True, timeout=10)
        
        url = reverse('chat:typing_status', kwargs={'room_id': self.room.id})
        response = self.client1.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['typing_users']), 1)
        self.assertEqual(response.data['typing_users'][0]['user_id'], str(self.user2.id))
    
    def test_file_upload(self):
        """Test file upload functionality"""
        # Create a test file
        test_file = SimpleUploadedFile(
            "test.txt",
            b"This is a test file content",
            content_type="text/plain"
        )
        
        url = reverse('chat:upload_file', kwargs={'room_id': self.room.id})
        response = self.client1.post(url, {'file': test_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message_type'], 'file')
        self.assertEqual(response.data['file_name'], 'test.txt')
        self.assertIn('Shared file: test.txt', response.data['content'])
        
        # Verify file message was created
        message = ChatMessage.objects.get(id=response.data['id'])
        self.assertEqual(message.message_type, 'file')
        self.assertEqual(message.file_name, 'test.txt')
        self.assertTrue(message.file_size > 0)
    
    def test_file_upload_no_file(self):
        """Test file upload without providing file"""
        url = reverse('chat:upload_file', kwargs={'room_id': self.room.id})
        response = self.client1.post(url, {})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('No file provided', response.data['error'])
    
    def test_file_upload_size_limit(self):
        """Test file upload size limit enforcement"""
        # Create a file larger than 10MB (simulated)
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        large_file = SimpleUploadedFile(
            "large_file.txt",
            large_content,
            content_type="text/plain"
        )
        
        url = reverse('chat:upload_file', kwargs={'room_id': self.room.id})
        response = self.client1.post(url, {'file': large_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('File size exceeds 10MB limit', response.data['error'])
    
    def test_pagination(self):
        """Test message pagination"""
        # Create many messages
        for i in range(75):
            ChatMessage.objects.create(
                room=self.room,
                sender=self.profile1,
                content=f'Message {i}'
            )
        
        url = reverse('chat:room_messages', kwargs={'room_id': self.room.id})
        response = self.client1.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('next'))  # Should have next page
        self.assertEqual(len(response.data['results']), 50)  # Default page size
        
        # Test custom page size
        response = self.client1.get(url, {'page_size': 25})
        self.assertEqual(len(response.data['results']), 25)
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated requests are rejected"""
        client = APIClient()  # No authentication
        
        url = reverse('chat:room_list')
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        url = reverse('chat:room_messages', kwargs={'room_id': self.room.id})
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ChatRoomModelTestCase(TestCase):
    """Test cases for ChatRoom model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.profile1 = CreatorProfile.objects.create(
            user=self.user1,
            display_name='Test User 1'
        )
    
    def test_room_string_representation(self):
        """Test ChatRoom string representation"""
        # Test direct message room
        room = ChatRoom.objects.create(
            room_type='direct',
            created_by=self.profile1
        )
        
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        profile2 = CreatorProfile.objects.create(
            user=user2,
            display_name='Test User 2'
        )
        
        room.participants.add(self.profile1, profile2)
        
        str_repr = str(room)
        self.assertIn('DM:', str_repr)
        self.assertIn('Test User 1', str_repr)
        self.assertIn('Test User 2', str_repr)
        
        # Test group room
        group_room = ChatRoom.objects.create(
            room_type='group',
            name='Test Group',
            created_by=self.profile1
        )
        
        self.assertEqual(str(group_room), 'Test Group')


class ChatMessageModelTestCase(TestCase):
    """Test cases for ChatMessage model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.profile1 = CreatorProfile.objects.create(
            user=self.user1,
            display_name='Test User 1'
        )
        self.room = ChatRoom.objects.create(
            room_type='direct',
            created_by=self.profile1
        )
    
    def test_message_string_representation(self):
        """Test ChatMessage string representation"""
        message = ChatMessage.objects.create(
            room=self.room,
            sender=self.profile1,
            content='This is a test message that is longer than fifty characters to test truncation'
        )
        
        str_repr = str(message)
        self.assertIn('Test User 1:', str_repr)
        self.assertTrue(len(str_repr) <= 100)  # Should be truncated
        self.assertIn('This is a test message that is longer than fifty', str_repr)
    
    def test_message_ordering(self):
        """Test message ordering by created_at"""
        message1 = ChatMessage.objects.create(
            room=self.room,
            sender=self.profile1,
            content='First message'
        )
        message2 = ChatMessage.objects.create(
            room=self.room,
            sender=self.profile1,
            content='Second message'
        )
        
        messages = list(ChatMessage.objects.all())
        self.assertEqual(messages[0], message1)  # Should be ordered by created_at
        self.assertEqual(messages[1], message2)
