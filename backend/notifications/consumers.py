import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from .models import NotificationSubscription

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications
    Handles user authentication, group management, and message routing
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]
        
        if isinstance(self.user, AnonymousUser):
            logger.warning("Anonymous user attempted WebSocket connection")
            await self.close()
            return
            
        # Create user-specific group
        self.group_name = f"user_{self.user.id}_notifications"
        
        # Join user notification group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        # Accept connection
        await self.accept()
        
        # Create or update notification subscription
        await self.create_notification_subscription()
        
        logger.info(f"User {self.user.id} connected to notifications WebSocket")
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to notification service',
            'user_id': self.user.id,
            'timestamp': self.get_current_timestamp()
        }))

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'group_name'):
            # Leave user notification group
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            
            # Update subscription status
            await self.update_subscription_status(False)
            
            logger.info(f"User {self.user.id} disconnected from notifications WebSocket")

    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': self.get_current_timestamp()
                }))
            elif message_type == 'mark_notification_read':
                notification_id = data.get('notification_id')
                await self.mark_notification_read(notification_id)
            elif message_type == 'update_preferences':
                preferences = data.get('preferences', {})
                await self.update_notification_preferences(preferences)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received from WebSocket")
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {str(e)}")

    # Group message handlers
    async def notification_message(self, event):
        """Send notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification'],
            'timestamp': self.get_current_timestamp()
        }))

    async def match_update(self, event):
        """Send match update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'match_update',
            'match_data': event['match_data'],
            'update_type': event['update_type'],
            'timestamp': self.get_current_timestamp()
        }))

    async def system_message(self, event):
        """Send system message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'system_message',
            'message': event['message'],
            'level': event.get('level', 'info'),
            'timestamp': self.get_current_timestamp()
        }))

    # Database operations
    @database_sync_to_async
    def create_notification_subscription(self):
        """Create or update notification subscription for user"""
        subscription, created = NotificationSubscription.objects.get_or_create(
            user=self.user,
            defaults={
                'is_active': True,
                'websocket_connected': True,
                'connection_count': 1
            }
        )
        if not created:
            subscription.websocket_connected = True
            subscription.connection_count += 1
            subscription.save()
        return subscription

    @database_sync_to_async
    def update_subscription_status(self, connected):
        """Update subscription connection status"""
        try:
            subscription = NotificationSubscription.objects.get(user=self.user)
            subscription.websocket_connected = connected
            if not connected:
                subscription.connection_count = max(0, subscription.connection_count - 1)
            subscription.save()
        except NotificationSubscription.DoesNotExist:
            pass

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark notification as read"""
        from .models import Notification
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=self.user
            )
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False

    @database_sync_to_async
    def update_notification_preferences(self, preferences):
        """Update user notification preferences"""
        subscription = NotificationSubscription.objects.get(user=self.user)
        subscription.preferences.update(preferences)
        subscription.save()
        return subscription.preferences

    def get_current_timestamp(self):
        """Get current timestamp in ISO format"""
        from django.utils import timezone
        return timezone.now().isoformat()


class MatchingConsumer(AsyncWebsocketConsumer):
    """
    Specialized consumer for AI matching real-time updates
    """
    
    async def connect(self):
        """Handle connection for matching updates"""
        self.user = self.scope["user"]
        
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
            
        # Join matching-specific group
        self.group_name = f"user_{self.user.id}_matching"
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        
        logger.info(f"User {self.user.id} connected to matching WebSocket")

    async def disconnect(self, close_code):
        """Handle disconnection"""
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle matching-specific messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'request_match_updates':
                # Send current match status
                await self.send_current_matches()
            elif message_type == 'update_match_preferences':
                preferences = data.get('preferences', {})
                await self.update_matching_preferences(preferences)
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON in matching WebSocket")

    async def new_match_found(self, event):
        """Handle new match notification"""
        await self.send(text_data=json.dumps({
            'type': 'new_match',
            'match': event['match'],
            'compatibility_score': event['compatibility_score'],
            'timestamp': self.get_current_timestamp()
        }))

    async def match_status_changed(self, event):
        """Handle match status change"""
        await self.send(text_data=json.dumps({
            'type': 'match_status_update',
            'match_id': event['match_id'],
            'old_status': event['old_status'],
            'new_status': event['new_status'],
            'timestamp': self.get_current_timestamp()
        }))

    @database_sync_to_async
    def send_current_matches(self):
        """Send current user matches"""
        from ai_services.models import MatchResult
        matches = MatchResult.objects.filter(
            requester=self.user,
            status__in=['pending', 'viewed']
        ).select_related('matched_creator')[:10]
        
        match_data = []
        for match in matches:
            match_data.append({
                'id': match.id,
                'matched_creator': match.matched_creator_name,
                'compatibility_score': match.compatibility_score,
                'status': match.status,
                'created_at': match.created_at.isoformat()
            })
        
        return match_data

    def get_current_timestamp(self):
        """Get current timestamp"""
        from django.utils import timezone
        return timezone.now().isoformat()
