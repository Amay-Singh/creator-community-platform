import logging
from django.utils import timezone
from .models import Notification, ActivityFeed

logger = logging.getLogger(__name__)


def create_notification(user, notification_type, payload=None):
    """
    Create a notification for a user
    
    Args:
        user: User instance
        notification_type: String from Notification.NOTIFICATION_TYPES
        payload: Dict with notification data
    
    Returns:
        Notification instance or None if failed
    """
    try:
        if payload is None:
            payload = {}
            
        notification = Notification.objects.create(
            user=user,
            type=notification_type,
            payload=payload
        )
        
        logger.info(f"notif_created user_id={user.id} type={notification_type} notif_id={notification.id}")
        return notification
        
    except Exception as e:
        logger.error(f"notif_create_error user_id={user.id} type={notification_type} error={str(e)}")
        return None


def create_activity(user, actor, action_type, target_type=None, target_id=None, metadata=None):
    """
    Create an activity feed entry
    
    Args:
        user: User who will see this in their feed
        actor: User who performed the action (can be same as user)
        action_type: String from ActivityFeed.ACTIVITY_TYPES
        target_type: Optional string describing what was acted upon
        target_id: Optional UUID of the target object
        metadata: Optional dict with additional data
    
    Returns:
        ActivityFeed instance or None if failed
    """
    try:
        if metadata is None:
            metadata = {}
            
        activity = ActivityFeed.objects.create(
            user=user,
            actor=actor,
            action_type=action_type,
            target_type=target_type,
            target_id=target_id,
            metadata=metadata
        )
        
        logger.info(f"activity_created user_id={user.id} actor_id={actor.id if actor else None} type={action_type}")
        return activity
        
    except Exception as e:
        logger.error(f"activity_create_error user_id={user.id} type={action_type} error={str(e)}")
        return None


def get_unread_count(user):
    """Get count of unread notifications for user"""
    try:
        count = Notification.objects.filter(user=user, read_at__isnull=True).count()
        return count
    except Exception as e:
        logger.error(f"unread_count_error user_id={user.id} error={str(e)}")
        return 0


def mark_all_read(user):
    """Mark all notifications as read for user"""
    try:
        updated_count = Notification.objects.filter(
            user=user, 
            read_at__isnull=True
        ).update(read_at=timezone.now())
        
        logger.info(f"notif_read user_id={user.id} action=mark_all count={updated_count}")
        return updated_count
        
    except Exception as e:
        logger.error(f"mark_all_read_error user_id={user.id} error={str(e)}")
        return 0
