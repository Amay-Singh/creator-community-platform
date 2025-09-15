"""
Collaboration Invitation System for Creator Community Platform
Implements P5-003: COLL-001 Collaboration Invites
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from accounts.models import CreatorProfile
import uuid
import logging

logger = logging.getLogger(__name__)


class NewCollaborationInvite(models.Model):
    """
    Collaboration invitation model with project brief, scope, and compensation
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('countered', 'Countered'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    COMPENSATION_TYPE_CHOICES = [
        ('none', 'No Compensation'),
        ('fixed', 'Fixed Amount'),
        ('hourly', 'Hourly Rate'),
        ('revenue_share', 'Revenue Share'),
        ('equity', 'Equity'),
        ('barter', 'Barter/Trade'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_invites')
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_invites')
    
    # Project details
    project_title = models.CharField(max_length=200)
    project_brief = models.TextField(help_text="Detailed description of the collaboration")
    scope_of_work = models.TextField(help_text="Specific tasks and deliverables")
    
    # Timeline
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    estimated_hours = models.PositiveIntegerField(null=True, blank=True)
    
    # Compensation
    compensation_type = models.CharField(max_length=20, choices=COMPENSATION_TYPE_CHOICES, default='none')
    compensation_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    compensation_currency = models.CharField(max_length=3, default='USD')
    compensation_details = models.TextField(blank=True, help_text="Additional compensation details")
    
    # Legal and privacy
    nda_required = models.BooleanField(default=False)
    nda_document = models.FileField(upload_to='ndas/', null=True, blank=True)
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, help_text="Personal message with the invite")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    # Response details
    response_message = models.TextField(blank=True)
    counter_offer_details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'new_collaboration_invites'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['from_user', 'status']),
            models.Index(fields=['to_user', 'status']),
            models.Index(fields=['status', 'expires_at']),
        ]
    
    def __str__(self):
        return f"Invite from {self.from_user.username} to {self.to_user.username}: {self.project_title}"
    
    def clean(self):
        """Validate invite data"""
        if self.from_user == self.to_user:
            raise ValidationError("Cannot send invite to yourself")
        
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("Start date cannot be after end date")
        
        if self.compensation_type != 'none' and not self.compensation_amount:
            raise ValidationError("Compensation amount required when compensation type is specified")
    
    def save(self, *args, **kwargs):
        """Set expiration date if not provided"""
        if not self.expires_at and self.status == 'pending':
            # Default expiration: 7 days from creation
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        
        self.clean()
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if invite has expired"""
        return self.expires_at and timezone.now() > self.expires_at
    
    def can_respond(self):
        """Check if invite can still be responded to"""
        return self.status == 'pending' and not self.is_expired()
    
    def accept(self, response_message=""):
        """Accept the collaboration invite"""
        if not self.can_respond():
            raise ValidationError("Cannot accept expired or already responded invite")
        
        self.status = 'accepted'
        self.response_message = response_message
        self.responded_at = timezone.now()
        self.save()
        
        # Create collaboration project
        project = self._create_collaboration_project()
        
        # Clear cache
        self._clear_invite_cache()
        
        logger.info(f"Invite {self.id} accepted by {self.to_user.username}")
        return project
    
    def decline(self, response_message=""):
        """Decline the collaboration invite"""
        if not self.can_respond():
            raise ValidationError("Cannot decline expired or already responded invite")
        
        self.status = 'declined'
        self.response_message = response_message
        self.responded_at = timezone.now()
        self.save()
        
        self._clear_invite_cache()
        logger.info(f"Invite {self.id} declined by {self.to_user.username}")
    
    def counter_offer(self, counter_details, response_message=""):
        """Make a counter offer"""
        if not self.can_respond():
            raise ValidationError("Cannot counter expired or already responded invite")
        
        self.status = 'countered'
        self.response_message = response_message
        self.counter_offer_details = counter_details
        self.responded_at = timezone.now()
        self.save()
        
        self._clear_invite_cache()
        logger.info(f"Invite {self.id} countered by {self.to_user.username}")
    
    def cancel(self):
        """Cancel the invite (only by sender)"""
        if self.status not in ['pending', 'countered']:
            raise ValidationError("Can only cancel pending or countered invites")
        
        self.status = 'cancelled'
        self.save()
        
        self._clear_invite_cache()
        logger.info(f"Invite {self.id} cancelled by {self.from_user.username}")
    
    def _create_collaboration_project(self):
        """Create a collaboration project when invite is accepted"""
        from .models import Project  # Avoid circular import
        
        project = Project.objects.create(
            title=self.project_title,
            description=self.project_brief,
            owner=self.from_user,
            status='active',
            start_date=self.start_date,
            end_date=self.end_date,
            estimated_hours=self.estimated_hours,
        )
        
        # Add both users as collaborators
        project.collaborators.add(self.from_user, self.to_user)
        
        return project
    
    def _clear_invite_cache(self):
        """Clear relevant cache entries"""
        cache_keys = [
            f"user_invites_sent:{self.from_user.id}",
            f"user_invites_received:{self.to_user.id}",
            f"invite_stats:{self.from_user.id}",
            f"invite_stats:{self.to_user.id}",
        ]
        cache.delete_many(cache_keys)


class InviteTemplate(models.Model):
    """
    Reusable templates for collaboration invites
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invite_templates')
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    project_title_template = models.CharField(max_length=200)
    project_brief_template = models.TextField()
    scope_of_work_template = models.TextField()
    scope_template = models.TextField()
    message_template = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    # Default settings
    default_compensation_type = models.CharField(max_length=20, choices=NewCollaborationInvite.COMPENSATION_TYPE_CHOICES, default='none')
    default_nda_required = models.BooleanField(default=False)
    default_duration_days = models.PositiveIntegerField(default=30)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    usage_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'invite_templates'
        ordering = ['-usage_count', '-updated_at']
    
    def __str__(self):
        return f"{self.creator.username}'s template: {self.name}"
    
    def use_template(self, to_user, **overrides):
        """Create an invite using this template"""
        invite_data = {
            'from_user': self.creator,
            'to_user': to_user,
            'project_title': self.project_title_template,
            'project_brief': self.project_brief_template,
            'scope_of_work': self.scope_template,
            'message': self.message_template,
            'compensation_type': self.default_compensation_type,
            'nda_required': self.default_nda_required,
        }
        
        # Apply overrides
        invite_data.update(overrides)
        
        # Create invite
        invite = NewCollaborationInvite.objects.create(**invite_data)
        
        # Update usage count
        self.usage_count += 1
        self.save(update_fields=['usage_count'])
        
        return invite


class InviteManager:
    """
    Business logic for managing collaboration invites
    """
    
    @staticmethod
    def send_invite(from_user, to_user, **invite_data):
        """Send a collaboration invite with validation"""
        # Check if users can collaborate
        if not InviteManager._can_send_invite(from_user, to_user):
            raise ValidationError("Cannot send invite to this user.")
            
        # Check rate limiting
        rate_limit_key = f"invite_rate_limit:{from_user.id}"
        recent_invites = cache.get(rate_limit_key, 0)
        if recent_invites >= 10:  # Max 10 invites per hour
            raise ValidationError("Rate limit exceeded. Please wait before sending more invites.")
        
        # Create invite
        invite = NewCollaborationInvite.objects.create(
            from_user=from_user,
            to_user=to_user,
            **invite_data
        )
        
        # Send notification
        InviteManager._send_notification(invite)
        
        # Update cache
        InviteManager._update_invite_cache(from_user, to_user)
        
        logger.info(f"Collaboration invite sent from {from_user.username} to {to_user.username}")
        return invite
    
    @staticmethod
    def get_user_invites_sent(user, status=None):
        """Get invites sent by user with caching"""
        cache_key = f"user_invites_sent:{user.id}:{status or 'all'}"
        invites = cache.get(cache_key)
        
        if invites is None:
            invites = NewCollaborationInvite.objects.filter(from_user=user)
            if status:
                invites = invites.filter(status=status)
            
            invites = list(invites.select_related('to_user', 'to_user__profile'))
            cache.set(cache_key, invites, 300)  # 5 minutes
        
        return invites
    
    @staticmethod
    def get_user_invites_received(user, status=None):
        """Get invites received by user with caching"""
        cache_key = f"user_invites_received:{user.id}:{status or 'all'}"
        invites = cache.get(cache_key)
        
        if invites is None:
            queryset = NewCollaborationInvite.objects.filter(to_user=user)
            if status:
                queryset = queryset.filter(status=status)
            
            invites = list(queryset.select_related('from_user', 'from_user__profile'))
            cache.set(cache_key, invites, 300)  # 5 minutes
        
        return invites
    
    @staticmethod
    def get_invite_stats(user):
        """Get invite statistics for user"""
        cache_key = f"invite_stats:{user.id}"
        stats = cache.get(cache_key)
        
        if stats is None:
            sent_invites = NewCollaborationInvite.objects.filter(from_user=user)
            received_invites = NewCollaborationInvite.objects.filter(to_user=user)
            
            stats = {
                'sent_total': sent_invites.count(),
                'sent_pending': sent_invites.filter(status='pending').count(),
                'sent_accepted': sent_invites.filter(status='accepted').count(),
                'sent_declined': sent_invites.filter(status='declined').count(),
                'received_total': received_invites.count(),
                'received_pending': received_invites.filter(status='pending').count(),
                'received_accepted': received_invites.filter(status='accepted').count(),
                'received_declined': received_invites.filter(status='declined').count(),
                'acceptance_rate': 0.0,
                'response_rate': 0.0,
            }
            
            # Calculate rates
            if stats['sent_total'] > 0:
                stats['acceptance_rate'] = (stats['sent_accepted'] / stats['sent_total']) * 100
                responded = stats['sent_accepted'] + stats['sent_declined']
                stats['response_rate'] = (responded / stats['sent_total']) * 100
            
            cache.set(cache_key, stats, 600)  # 10 minutes
        
        return stats
    
    @staticmethod
    def expire_old_invites():
        """Expire old pending invites (called by periodic task)"""
        expired_invites = NewCollaborationInvite.objects.filter(
            status='pending',
            expires_at__lt=timezone.now()
        )
        
        count = expired_invites.update(status='expired')
        logger.info(f"Expired {count} old collaboration invites")
        
        return count
    
    @staticmethod
    def _can_send_invite(from_user, to_user):
        """Check if from_user can send invite to to_user"""
        if from_user == to_user:
            return False
        
        # Check if both users have profiles
        try:
            from_profile = getattr(from_user, 'profile', None)
            to_profile = getattr(to_user, 'profile', None)
            if not from_profile or not to_profile:
                # Allow invites even without profiles for testing
                pass
        except:
            pass
        
        # Check for existing pending invites
        existing = NewCollaborationInvite.objects.filter(
            from_user=from_user,
            to_user=to_user,
            status='pending'
        ).exists()
        
        return not existing
    
    @staticmethod
    def _check_rate_limit(user):
        """Check if user has exceeded invite sending rate limit"""
        cache_key = f"invite_rate_limit:{user.id}"
        count = cache.get(cache_key, 0)
        
        # Allow 10 invites per hour for regular users
        # TODO: Increase limit for premium users
        limit = 10
        
        if count >= limit:
            return False
        
        # Increment counter
        cache.set(cache_key, count + 1, 3600)  # 1 hour
        return True
    
    @staticmethod
    def _send_notification(invite):
        """Send notification about new invite"""
        from notifications.utils import create_notification
        
        create_notification(
            user=invite.to_user,
            notification_type='collaboration_invite',
            payload={
                'title': f"New collaboration invite from {invite.from_user.username}",
                'message': f"{invite.from_user.username} invited you to collaborate on '{invite.project_title}'",
                'action_url': f"/invites/{invite.id}/",
                'invite_id': str(invite.id),
                'from_user_id': str(invite.from_user.id),
                'project_title': invite.project_title
            }
        )
    
    @staticmethod
    def _update_invite_cache(from_user, to_user):
        """Update relevant cache entries"""
        cache_keys = [
            f"user_invites_sent:{from_user.id}",
            f"user_invites_received:{to_user.id}",
            f"invite_stats:{from_user.id}",
            f"invite_stats:{to_user.id}",
        ]
        cache.delete_many(cache_keys)
