import logging
from typing import Dict, List, Optional, Any
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Notification, MatchNotification, NotificationSubscription

User = get_user_model()
logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


class NotificationService:
    """
    Service class for handling real-time notifications
    """
    
    @staticmethod
    def send_notification(user_id: int, notification_type: str, title: str, 
                         message: str, payload: Dict = None, 
                         send_realtime: bool = True) -> Notification:
        """
        Send notification to user with optional real-time delivery
        """
        try:
            user = User.objects.get(id=user_id)
            
            # Create notification record
            notification = Notification.objects.create(
                user=user,
                type=notification_type,
                payload=payload or {}
            )
            
            # Send real-time notification if requested
            if send_realtime:
                NotificationService.send_realtime_notification(
                    user_id=user_id,
                    notification_data={
                        'id': str(notification.id),
                        'type': notification_type,
                        'title': title,
                        'message': message,
                        'payload': payload or {},
                        'created_at': notification.created_at.isoformat(),
                        'is_read': False
                    }
                )
            
            logger.info(f"Notification sent to user {user_id}: {notification_type}")
            return notification
            
        except User.DoesNotExist:
            logger.error(f"User {user_id} not found for notification")
            return None
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            return None
    
    @staticmethod
    def send_realtime_notification(user_id: int, notification_data: Dict):
        """
        Send real-time notification via WebSocket
        """
        try:
            group_name = f"user_{user_id}_notifications"
            
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'notification_message',
                    'notification': notification_data
                }
            )
            
            logger.debug(f"Real-time notification sent to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error sending real-time notification: {str(e)}")
    
    @staticmethod
    def send_system_message(user_id: int, message: str, level: str = 'info'):
        """
        Send system message to user via WebSocket
        """
        try:
            group_name = f"user_{user_id}_notifications"
            
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'system_message',
                    'message': message,
                    'level': level
                }
            )
            
        except Exception as e:
            logger.error(f"Error sending system message: {str(e)}")
    
    @staticmethod
    def get_user_notifications(user_id: int, limit: int = 20, 
                              unread_only: bool = False) -> List[Dict]:
        """
        Get user notifications with optional filtering
        """
        try:
            queryset = Notification.objects.filter(user_id=user_id)
            
            if unread_only:
                queryset = queryset.filter(read_at__isnull=True)
            
            notifications = queryset[:limit]
            
            return [
                {
                    'id': str(n.id),
                    'type': n.type,
                    'payload': n.payload,
                    'is_read': n.is_read,
                    'created_at': n.created_at.isoformat(),
                    'read_at': n.read_at.isoformat() if n.read_at else None
                }
                for n in notifications
            ]
            
        except Exception as e:
            logger.error(f"Error getting user notifications: {str(e)}")
            return []
    
    @staticmethod
    def mark_notification_read(notification_id: str, user_id: int) -> bool:
        """
        Mark notification as read
        """
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user_id=user_id
            )
            notification.mark_as_read()
            return True
            
        except Notification.DoesNotExist:
            logger.error(f"Notification {notification_id} not found for user {user_id}")
            return False
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            return False


class MatchNotificationService:
    """
    Specialized service for AI matching notifications
    """
    
    @staticmethod
    def send_match_notification(recipient_id: int, sender_id: Optional[int],
                               notification_type: str, match_id: str,
                               title: str, message: str, 
                               metadata: Dict = None) -> MatchNotification:
        """
        Send match-specific notification
        """
        try:
            recipient = User.objects.get(id=recipient_id)
            sender = User.objects.get(id=sender_id) if sender_id else None
            
            # Create match notification
            match_notification = MatchNotification.objects.create(
                recipient=recipient,
                sender=sender,
                notification_type=notification_type,
                match_id=match_id,
                title=title,
                message=message,
                metadata=metadata or {}
            )
            
            # Check user preferences
            subscription = NotificationSubscription.objects.filter(
                user=recipient
            ).first()
            
            if subscription and subscription.get_preference(f'match_{notification_type}', True):
                # Send real-time notification
                MatchNotificationService.send_realtime_match_update(
                    recipient_id=recipient_id,
                    match_data={
                        'id': str(match_notification.id),
                        'type': notification_type,
                        'match_id': match_id,
                        'title': title,
                        'message': message,
                        'sender': sender.username if sender else 'System',
                        'metadata': metadata or {},
                        'created_at': match_notification.created_at.isoformat()
                    }
                )
            
            # Mark as delivered
            match_notification.mark_as_delivered()
            
            logger.info(f"Match notification sent: {notification_type} to user {recipient_id}")
            return match_notification
            
        except User.DoesNotExist:
            logger.error(f"User not found for match notification")
            return None
        except Exception as e:
            logger.error(f"Error sending match notification: {str(e)}")
            return None
    
    @staticmethod
    def send_realtime_match_update(recipient_id: int, match_data: Dict):
        """
        Send real-time match update via WebSocket
        """
        try:
            # Send to general notifications channel
            notification_group = f"user_{recipient_id}_notifications"
            async_to_sync(channel_layer.group_send)(
                notification_group,
                {
                    'type': 'notification_message',
                    'notification': {
                        'type': 'match_notification',
                        'data': match_data
                    }
                }
            )
            
            # Send to matching-specific channel
            matching_group = f"user_{recipient_id}_matching"
            async_to_sync(channel_layer.group_send)(
                matching_group,
                {
                    'type': 'new_match_found' if match_data['type'] == 'new_match' else 'match_status_changed',
                    'match': match_data
                }
            )
            
        except Exception as e:
            logger.error(f"Error sending real-time match update: {str(e)}")
    
    @staticmethod
    def notify_new_match(requester_id: int, matched_creator_id: int, 
                        match_id: str, compatibility_score: float):
        """
        Send notification for new AI match
        """
        try:
            matched_creator = User.objects.get(id=matched_creator_id)
            
            title = "New Match Found!"
            message = f"You have a new match with {matched_creator.username} (Compatibility: {compatibility_score:.1%})"
            
            return MatchNotificationService.send_match_notification(
                recipient_id=requester_id,
                sender_id=matched_creator_id,
                notification_type='new_match',
                match_id=match_id,
                title=title,
                message=message,
                metadata={
                    'compatibility_score': compatibility_score,
                    'matched_creator_name': matched_creator.username
                }
            )
            
        except Exception as e:
            logger.error(f"Error sending new match notification: {str(e)}")
            return None
    
    @staticmethod
    def notify_match_status_change(user_id: int, match_id: str, 
                                  old_status: str, new_status: str):
        """
        Send notification for match status change
        """
        status_messages = {
            'accepted': 'Your match has been accepted!',
            'declined': 'Your match was declined',
            'expired': 'Your match has expired',
            'viewed': 'Your match has been viewed'
        }
        
        title = f"Match Status Update"
        message = status_messages.get(new_status, f"Match status changed to {new_status}")
        
        return MatchNotificationService.send_match_notification(
            recipient_id=user_id,
            sender_id=None,
            notification_type='match_status_changed',
            match_id=match_id,
            title=title,
            message=message,
            metadata={
                'old_status': old_status,
                'new_status': new_status
            }
        )
    
    @staticmethod
    def notify_feedback_received(user_id: int, match_id: str, 
                                feedback_rating: int, feedback_text: str = None):
        """
        Send notification for match feedback
        """
        title = "Feedback Received"
        message = f"You received feedback on your match (Rating: {feedback_rating}/5)"
        
        if feedback_text:
            message += f": {feedback_text[:100]}..."
        
        return MatchNotificationService.send_match_notification(
            recipient_id=user_id,
            sender_id=None,
            notification_type='feedback_received',
            match_id=match_id,
            title=title,
            message=message,
            metadata={
                'rating': feedback_rating,
                'feedback_text': feedback_text
            }
        )


class NotificationPreferencesService:
    """
    Service for managing user notification preferences
    """
    
    @staticmethod
    def get_or_create_subscription(user_id: int) -> NotificationSubscription:
        """
        Get or create notification subscription for user
        """
        try:
            user = User.objects.get(id=user_id)
            subscription, created = NotificationSubscription.objects.get_or_create(
                user=user,
                defaults={
                    'is_active': True,
                    'preferences': NotificationSubscription().default_preferences
                }
            )
            
            if created:
                logger.info(f"Created notification subscription for user {user_id}")
            
            return subscription
            
        except User.DoesNotExist:
            logger.error(f"User {user_id} not found")
            return None
    
    @staticmethod
    def update_preferences(user_id: int, preferences: Dict) -> bool:
        """
        Update user notification preferences
        """
        try:
            subscription = NotificationPreferencesService.get_or_create_subscription(user_id)
            if subscription:
                subscription.preferences.update(preferences)
                subscription.save()
                
                # Send real-time update
                NotificationService.send_system_message(
                    user_id=user_id,
                    message="Notification preferences updated",
                    level='success'
                )
                
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error updating notification preferences: {str(e)}")
            return False
    
    @staticmethod
    def get_preferences(user_id: int) -> Dict:
        """
        Get user notification preferences
        """
        try:
            subscription = NotificationPreferencesService.get_or_create_subscription(user_id)
            return subscription.preferences if subscription else {}
            
        except Exception as e:
            logger.error(f"Error getting notification preferences: {str(e)}")
            return {}
