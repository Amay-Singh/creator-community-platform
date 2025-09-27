import json
import logging
from typing import Dict, Optional
from pywebpush import webpush, WebPushException
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import NotificationSubscription

User = get_user_model()
logger = logging.getLogger(__name__)


class PushNotificationService:
    """
    Service for sending Web Push notifications
    """
    
    def __init__(self):
        self.vapid_private_key = getattr(settings, 'VAPID_PRIVATE_KEY', None)
        self.vapid_public_key = getattr(settings, 'VAPID_PUBLIC_KEY', None)
        self.vapid_claims = {
            "sub": getattr(settings, 'VAPID_SUBJECT', "mailto:admin@creatorplatform.com")
        }
    
    def send_push_notification(self, user_id: int, title: str, message: str, 
                              data: Dict = None, actions: list = None) -> bool:
        """
        Send push notification to user
        """
        try:
            # Get user's push subscription
            subscription = NotificationSubscription.objects.filter(
                user_id=user_id,
                push_subscription__isnull=False,
                is_active=True
            ).first()
            
            if not subscription or not subscription.push_subscription:
                logger.warning(f"No push subscription found for user {user_id}")
                return False
            
            # Check if user has push notifications enabled
            if not subscription.get_preference('push_notifications', True):
                logger.info(f"Push notifications disabled for user {user_id}")
                return False
            
            # Prepare notification payload
            payload = {
                "title": title,
                "body": message,
                "icon": "/static/icons/notification-icon.png",
                "badge": "/static/icons/badge-icon.png",
                "data": data or {},
                "actions": actions or [],
                "requireInteraction": True,
                "tag": f"notification-{user_id}",
                "timestamp": int(timezone.now().timestamp() * 1000)
            }
            
            # Send push notification
            response = webpush(
                subscription_info=subscription.push_subscription,
                data=json.dumps(payload),
                vapid_private_key=self.vapid_private_key,
                vapid_claims=self.vapid_claims
            )
            
            logger.info(f"Push notification sent to user {user_id}: {response.status_code}")
            return response.status_code == 201
            
        except WebPushException as e:
            logger.error(f"WebPush error for user {user_id}: {e}")
            
            # Handle subscription errors
            if e.response and e.response.status_code in [410, 413, 429]:
                # Subscription is no longer valid
                self._handle_invalid_subscription(user_id)
            
            return False
        except Exception as e:
            logger.error(f"Error sending push notification to user {user_id}: {str(e)}")
            return False
    
    def send_match_notification_push(self, user_id: int, match_data: Dict) -> bool:
        """
        Send push notification for new match
        """
        title = "New Match Found! 🎯"
        message = f"You have a new match with {match_data.get('matched_creator_name', 'someone')} ({match_data.get('compatibility_score', 0):.0%} compatibility)"
        
        actions = [
            {
                "action": "view_match",
                "title": "View Match",
                "icon": "/static/icons/view-icon.png"
            },
            {
                "action": "dismiss",
                "title": "Dismiss",
                "icon": "/static/icons/dismiss-icon.png"
            }
        ]
        
        data = {
            "type": "new_match",
            "match_id": match_data.get('match_id'),
            "url": f"/matching?highlight={match_data.get('match_id')}"
        }
        
        return self.send_push_notification(user_id, title, message, data, actions)
    
    def send_collaboration_invite_push(self, user_id: int, invite_data: Dict) -> bool:
        """
        Send push notification for collaboration invite
        """
        title = "Collaboration Invite 🤝"
        message = f"{invite_data.get('sender_name', 'Someone')} sent you a collaboration invite"
        
        actions = [
            {
                "action": "view_invite",
                "title": "View Invite",
                "icon": "/static/icons/view-icon.png"
            }
        ]
        
        data = {
            "type": "collaboration_invite",
            "invite_id": invite_data.get('invite_id'),
            "url": f"/collaborations/invites/{invite_data.get('invite_id')}"
        }
        
        return self.send_push_notification(user_id, title, message, data, actions)
    
    def send_match_accepted_push(self, user_id: int, match_data: Dict) -> bool:
        """
        Send push notification for match acceptance
        """
        title = "Match Accepted! ✅"
        message = f"{match_data.get('requester_name', 'Someone')} accepted your match!"
        
        actions = [
            {
                "action": "start_collaboration",
                "title": "Start Collaboration",
                "icon": "/static/icons/collaborate-icon.png"
            }
        ]
        
        data = {
            "type": "match_accepted",
            "match_id": match_data.get('match_id'),
            "url": f"/collaborations/new?match={match_data.get('match_id')}"
        }
        
        return self.send_push_notification(user_id, title, message, data, actions)
    
    def subscribe_user(self, user_id: int, subscription_data: Dict) -> bool:
        """
        Subscribe user to push notifications
        """
        try:
            subscription, created = NotificationSubscription.objects.get_or_create(
                user_id=user_id,
                defaults={'is_active': True}
            )
            
            subscription.push_subscription = subscription_data
            subscription.save()
            
            logger.info(f"Push subscription {'created' if created else 'updated'} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error subscribing user {user_id} to push notifications: {str(e)}")
            return False
    
    def unsubscribe_user(self, user_id: int) -> bool:
        """
        Unsubscribe user from push notifications
        """
        try:
            subscription = NotificationSubscription.objects.filter(user_id=user_id).first()
            if subscription:
                subscription.push_subscription = None
                subscription.save()
                
            logger.info(f"Push subscription removed for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error unsubscribing user {user_id} from push notifications: {str(e)}")
            return False
    
    def _handle_invalid_subscription(self, user_id: int):
        """
        Handle invalid push subscription
        """
        try:
            subscription = NotificationSubscription.objects.filter(user_id=user_id).first()
            if subscription:
                subscription.push_subscription = None
                subscription.save()
                logger.info(f"Removed invalid push subscription for user {user_id}")
        except Exception as e:
            logger.error(f"Error handling invalid subscription for user {user_id}: {str(e)}")
    
    def get_vapid_public_key(self) -> Optional[str]:
        """
        Get VAPID public key for client-side subscription
        """
        return self.vapid_public_key
    
    def test_push_notification(self, user_id: int) -> bool:
        """
        Send test push notification
        """
        return self.send_push_notification(
            user_id=user_id,
            title="Test Notification",
            message="This is a test push notification from Creator Community Platform",
            data={"type": "test", "timestamp": timezone.now().isoformat()}
        )


# Singleton instance
push_service = PushNotificationService()

# Import timezone after class definition to avoid circular imports
from django.utils import timezone
