import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from ai_services.models import MatchResult, MatchFeedback
from .services import MatchNotificationService, NotificationService

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=MatchResult)
def handle_match_result_created(sender, instance, created, **kwargs):
    """
    Handle new AI match creation
    """
    if created:
        try:
            # Send notification to the requester about new match
            MatchNotificationService.notify_new_match(
                requester_id=instance.requester.id,
                matched_creator_id=instance.matched_creator.id,
                match_id=str(instance.id),
                compatibility_score=instance.compatibility_score
            )
            
            logger.info(f"New match notification sent for match {instance.id}")
            
        except Exception as e:
            logger.error(f"Error sending new match notification: {str(e)}")


@receiver(pre_save, sender=MatchResult)
def handle_match_status_change(sender, instance, **kwargs):
    """
    Handle match status changes
    """
    if instance.pk:  # Only for existing instances
        try:
            # Get the old instance to compare status
            old_instance = MatchResult.objects.get(pk=instance.pk)
            
            # Check if status changed
            if old_instance.status != instance.status:
                # Send notification to requester about status change
                MatchNotificationService.notify_match_status_change(
                    user_id=instance.requester.id,
                    match_id=str(instance.id),
                    old_status=old_instance.status,
                    new_status=instance.status
                )
                
                # If match was accepted, also notify the matched creator
                if instance.status == 'accepted':
                    NotificationService.send_notification(
                        user_id=instance.matched_creator.id,
                        notification_type='match_accepted',
                        title='Match Accepted',
                        message=f'{instance.requester.username} accepted your match!',
                        payload={
                            'match_id': str(instance.id),
                            'requester_name': instance.requester.username,
                            'compatibility_score': instance.compatibility_score
                        }
                    )
                
                logger.info(f"Match status change notification sent for match {instance.id}")
                
        except MatchResult.DoesNotExist:
            # This shouldn't happen, but handle gracefully
            logger.warning(f"Could not find old match instance {instance.pk}")
        except Exception as e:
            logger.error(f"Error handling match status change: {str(e)}")


@receiver(post_save, sender=MatchFeedback)
def handle_match_feedback_created(sender, instance, created, **kwargs):
    """
    Handle new match feedback
    """
    if created:
        try:
            # Get the match result to find who should be notified
            match_result = instance.match_result
            
            # Determine who should receive the feedback notification
            # If feedback is from requester, notify matched_creator and vice versa
            if instance.reviewer == match_result.requester:
                recipient_id = match_result.matched_creator.id
                reviewer_name = match_result.requester.username
            else:
                recipient_id = match_result.requester.id
                reviewer_name = match_result.matched_creator.username
            
            # Send feedback notification
            MatchNotificationService.notify_feedback_received(
                user_id=recipient_id,
                match_id=str(match_result.id),
                feedback_rating=instance.rating,
                feedback_text=instance.feedback_text
            )
            
            # Also send general notification
            NotificationService.send_notification(
                user_id=recipient_id,
                notification_type='match_feedback_received',
                title='New Feedback Received',
                message=f'{reviewer_name} left feedback on your match (Rating: {instance.rating}/5)',
                payload={
                    'match_id': str(match_result.id),
                    'reviewer_name': reviewer_name,
                    'rating': instance.rating,
                    'feedback_text': instance.feedback_text,
                    'feedback_id': str(instance.id)
                }
            )
            
            logger.info(f"Feedback notification sent for match {match_result.id}")
            
        except Exception as e:
            logger.error(f"Error sending feedback notification: {str(e)}")


@receiver(post_save, sender=User)
def handle_user_created(sender, instance, created, **kwargs):
    """
    Create notification subscription for new users
    """
    if created:
        try:
            from .services import NotificationPreferencesService
            NotificationPreferencesService.get_or_create_subscription(instance.id)
            logger.info(f"Created notification subscription for new user {instance.id}")
            
        except Exception as e:
            logger.error(f"Error creating notification subscription for user {instance.id}: {str(e)}")


# Custom signal for match expiration (would be triggered by a background task)
def handle_match_expiration(match_id: str, user_id: int):
    """
    Handle match expiration notification
    Custom function to be called by background tasks
    """
    try:
        MatchNotificationService.notify_match_status_change(
            user_id=user_id,
            match_id=match_id,
            old_status='pending',
            new_status='expired'
        )
        
        NotificationService.send_notification(
            user_id=user_id,
            notification_type='match_expired',
            title='Match Expired',
            message='One of your matches has expired due to inactivity',
            payload={
                'match_id': match_id,
                'expiration_reason': 'timeout'
            }
        )
        
        logger.info(f"Match expiration notification sent for match {match_id}")
        
    except Exception as e:
        logger.error(f"Error sending match expiration notification: {str(e)}")


# Custom signal for collaboration invites (integrating with existing collaboration system)
def handle_collaboration_invite_notification(invite_id: str, recipient_id: int, sender_id: int):
    """
    Handle collaboration invite notifications
    """
    try:
        sender = User.objects.get(id=sender_id)
        
        NotificationService.send_notification(
            user_id=recipient_id,
            notification_type='collaboration_invite',
            title='New Collaboration Invite',
            message=f'{sender.username} sent you a collaboration invite',
            payload={
                'invite_id': invite_id,
                'sender_name': sender.username,
                'sender_id': sender_id
            }
        )
        
        logger.info(f"Collaboration invite notification sent to user {recipient_id}")
        
    except Exception as e:
        logger.error(f"Error sending collaboration invite notification: {str(e)}")
