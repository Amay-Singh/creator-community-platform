"""
WebSocket consumers for real-time messaging
Implements P5-004: Real-time messaging with typing indicators and presence
"""
import json
import logging
from datetime import datetime, timedelta
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from .models import ChatRoom, ChatMessage, MessageReadStatus
from .serializers import ChatMessageSerializer

User = get_user_model()
logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time chat functionality
    Handles message sending, typing indicators, and presence
    """
    
    async def connect(self):
        """Accept WebSocket connection and join room group"""
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope["user"]
        
        # Reject anonymous users
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Verify user has access to this room
        if not await self.user_has_room_access():
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Update user presence
        await self.update_user_presence(True)
        
        # Notify room about user joining
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_presence',
                'user_id': str(self.user.id),
                'username': self.user.username,
                'is_online': True,
                'timestamp': timezone.now().isoformat()
            }
        )
        
        logger.info(f"User {self.user.username} connected to room {self.room_id}")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'room_group_name'):
            # Update user presence
            await self.update_user_presence(False)
            
            # Notify room about user leaving
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_presence',
                    'user_id': str(self.user.id),
                    'username': self.user.username,
                    'is_online': False,
                    'timestamp': timezone.now().isoformat()
                }
            )
            
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        
        logger.info(f"User {self.user.username} disconnected from room {self.room_id}")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'typing_indicator':
                await self.handle_typing_indicator(data)
            elif message_type == 'read_receipt':
                await self.handle_read_receipt(data)
            else:
                await self.send_error('Unknown message type')
                
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON format')
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self.send_error('Message processing failed')
    
    async def handle_chat_message(self, data):
        """Process and broadcast chat messages"""
        content = data.get('content', '').strip()
        message_type = data.get('message_type', 'text')
        
        if not content and message_type == 'text':
            await self.send_error('Message content cannot be empty')
            return
        
        # Rate limiting check
        if not await self.check_rate_limit():
            await self.send_error('Rate limit exceeded')
            return
        
        # Create message in database
        message = await self.create_message(content, message_type)
        if not message:
            await self.send_error('Failed to create message')
            return
        
        # Serialize message for broadcast
        message_data = await self.serialize_message(message)
        
        # Broadcast to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_data,
                'sender_id': str(self.user.id),
                'timestamp': timezone.now().isoformat()
            }
        )
        
        # Update room's last message timestamp
        await self.update_room_last_message()
    
    async def handle_typing_indicator(self, data):
        """Handle typing indicator events"""
        is_typing = data.get('is_typing', False)
        
        # Cache typing status
        cache_key = f"typing_{self.room_id}_{self.user.id}"
        if is_typing:
            cache.set(cache_key, True, timeout=10)  # 10 second timeout
        else:
            cache.delete(cache_key)
        
        # Broadcast typing indicator to room (except sender)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': str(self.user.id),
                'username': self.user.username,
                'is_typing': is_typing,
                'timestamp': timezone.now().isoformat()
            }
        )
    
    async def handle_read_receipt(self, data):
        """Handle message read receipts"""
        message_id = data.get('message_id')
        if not message_id:
            return
        
        # Mark message as read
        await self.mark_message_read(message_id)
        
        # Broadcast read receipt
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'read_receipt',
                'message_id': message_id,
                'reader_id': str(self.user.id),
                'timestamp': timezone.now().isoformat()
            }
        )
    
    # WebSocket event handlers
    async def chat_message(self, event):
        """Send chat message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp']
        }))
    
    async def typing_indicator(self, event):
        """Send typing indicator to WebSocket (except to sender)"""
        if event['user_id'] != str(self.user.id):
            await self.send(text_data=json.dumps({
                'type': 'typing_indicator',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing'],
                'timestamp': event['timestamp']
            }))
    
    async def user_presence(self, event):
        """Send user presence update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user_presence',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_online': event['is_online'],
            'timestamp': event['timestamp']
        }))
    
    async def read_receipt(self, event):
        """Send read receipt to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'message_id': event['message_id'],
            'reader_id': event['reader_id'],
            'timestamp': event['timestamp']
        }))
    
    async def send_error(self, error_message):
        """Send error message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': error_message,
            'timestamp': timezone.now().isoformat()
        }))
    
    # Database operations
    @database_sync_to_async
    def user_has_room_access(self):
        """Check if user has access to the chat room"""
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            profile = getattr(self.user, 'profile', None)
            if not profile:
                return False
            return room.participants.filter(id=profile.id).exists()
        except ChatRoom.DoesNotExist:
            return False
    
    @database_sync_to_async
    def create_message(self, content, message_type):
        """Create a new chat message"""
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            profile = self.user.profile
            
            message = ChatMessage.objects.create(
                room=room,
                sender=profile,
                content=content,
                message_type=message_type,
                original_language='en'  # Default, will be detected later
            )
            return message
        except Exception as e:
            logger.error(f"Error creating message: {e}")
            return None
    
    @database_sync_to_async
    def serialize_message(self, message):
        """Serialize message for WebSocket transmission"""
        serializer = ChatMessageSerializer(message)
        return serializer.data
    
    @database_sync_to_async
    def mark_message_read(self, message_id):
        """Mark a message as read by the current user"""
        try:
            message = ChatMessage.objects.get(id=message_id)
            profile = self.user.profile
            
            MessageReadStatus.objects.get_or_create(
                message=message,
                reader=profile,
                defaults={'read_at': timezone.now()}
            )
        except Exception as e:
            logger.error(f"Error marking message as read: {e}")
    
    @database_sync_to_async
    def update_room_last_message(self):
        """Update room's last message timestamp"""
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            room.last_message_at = timezone.now()
            room.save(update_fields=['last_message_at'])
        except Exception as e:
            logger.error(f"Error updating room timestamp: {e}")
    
    async def update_user_presence(self, is_online):
        """Update user presence in cache"""
        cache_key = f"presence_{self.user.id}"
        if is_online:
            cache.set(cache_key, {
                'is_online': True,
                'last_seen': timezone.now().isoformat(),
                'room_id': self.room_id
            }, timeout=300)  # 5 minute timeout
        else:
            cache.set(cache_key, {
                'is_online': False,
                'last_seen': timezone.now().isoformat(),
                'room_id': None
            }, timeout=86400)  # 24 hour timeout for last_seen
    
    async def check_rate_limit(self):
        """Check if user is within rate limits for sending messages"""
        cache_key = f"rate_limit_{self.user.id}"
        current_count = cache.get(cache_key, 0)
        
        if current_count >= 30:  # 30 messages per minute
            return False
        
        cache.set(cache_key, current_count + 1, timeout=60)
        return True


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications
    """
    
    async def connect(self):
        """Accept WebSocket connection for notifications"""
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        self.user_group_name = f'notifications_{self.user.id}'
        
        # Join user notification group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"User {self.user.username} connected to notifications")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
        
        logger.info(f"User {self.user.username} disconnected from notifications")
    
    async def notification_message(self, event):
        """Send notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification'],
            'timestamp': event['timestamp']
        }))
