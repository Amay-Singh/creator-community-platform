"""
Profile Authentication System via Approval Codes
Implements REQ-3: Profile authentication via approval codes
"""
import random
import string
import uuid
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from .models import CreatorProfile, CustomUser

class ApprovalCode(models.Model):
    """
    Approval codes for profile authentication
    """
    CODE_TYPES = [
        ('profile_verification', 'Profile Verification'),
        ('portfolio_approval', 'Portfolio Approval'),
        ('collaboration_verification', 'Collaboration Verification'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('used', 'Used'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE, related_name='approval_codes')
    code = models.CharField(max_length=8, unique=True)
    code_type = models.CharField(max_length=30, choices=CODE_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'approval_codes'
        indexes = [
            models.Index(fields=['code', 'status']),
            models.Index(fields=['profile', 'code_type']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.profile.display_name} - {self.code_type}"
    
    def is_valid(self):
        """Check if code is still valid"""
        return (
            self.status == 'pending' and
            self.expires_at > timezone.now()
        )
    
    def use_code(self):
        """Mark code as used"""
        if self.is_valid():
            self.status = 'used'
            self.used_at = timezone.now()
            self.save()
            return True
        return False

class ProfileAuthenticationService:
    """
    Service for managing profile authentication via approval codes
    """
    
    def __init__(self):
        self.code_length = 6
        self.expiry_hours = 24
    
    def generate_approval_code(self, profile: CreatorProfile, code_type: str) -> ApprovalCode:
        """
        Generate a new approval code for profile authentication
        
        Args:
            profile: CreatorProfile instance
            code_type: Type of approval code
        
        Returns:
            ApprovalCode instance
        """
        # Revoke any existing pending codes of the same type
        ApprovalCode.objects.filter(
            profile=profile,
            code_type=code_type,
            status='pending'
        ).update(status='revoked')
        
        # Generate unique code
        code = self._generate_unique_code()
        
        # Create approval code
        approval_code = ApprovalCode.objects.create(
            profile=profile,
            code=code,
            code_type=code_type,
            expires_at=timezone.now() + timedelta(hours=self.expiry_hours)
        )
        
        # Send notification
        self._send_approval_code_notification(approval_code)
        
        return approval_code
    
    def verify_approval_code(self, code: str, profile: CreatorProfile, code_type: str) -> dict:
        """
        Verify an approval code
        
        Args:
            code: The approval code to verify
            profile: CreatorProfile instance
            code_type: Expected code type
        
        Returns:
            Dict with verification results
        """
        result = {
            'is_valid': False,
            'message': '',
            'code_obj': None
        }
        
        try:
            approval_code = ApprovalCode.objects.get(
                code=code.upper(),
                profile=profile,
                code_type=code_type
            )
            
            if approval_code.status == 'used':
                result['message'] = 'Code has already been used'
            elif approval_code.status == 'expired':
                result['message'] = 'Code has expired'
            elif approval_code.status == 'revoked':
                result['message'] = 'Code has been revoked'
            elif approval_code.expires_at <= timezone.now():
                approval_code.status = 'expired'
                approval_code.save()
                result['message'] = 'Code has expired'
            else:
                # Code is valid
                approval_code.use_code()
                result['is_valid'] = True
                result['message'] = 'Code verified successfully'
                result['code_obj'] = approval_code
                
                # Apply authentication based on code type
                self._apply_authentication(profile, code_type)
        
        except ApprovalCode.DoesNotExist:
            result['message'] = 'Invalid approval code'
        
        return result
    
    def request_profile_verification(self, profile: CreatorProfile) -> ApprovalCode:
        """
        Request profile verification code
        """
        return self.generate_approval_code(profile, 'profile_verification')
    
    def verify_profile(self, code: str, profile: CreatorProfile) -> dict:
        """
        Verify profile using approval code
        """
        return self.verify_approval_code(code, profile, 'profile_verification')
    
    def request_portfolio_approval(self, profile: CreatorProfile) -> ApprovalCode:
        """
        Request portfolio approval code
        """
        return self.generate_approval_code(profile, 'portfolio_approval')
    
    def approve_portfolio(self, code: str, profile: CreatorProfile) -> dict:
        """
        Approve portfolio using approval code
        """
        return self.verify_approval_code(code, profile, 'portfolio_approval')
    
    def get_profile_authentication_status(self, profile: CreatorProfile) -> dict:
        """
        Get comprehensive authentication status for a profile
        """
        status = {
            'is_verified': profile.is_validated,
            'verification_level': self._calculate_verification_level(profile),
            'pending_codes': [],
            'completed_verifications': [],
            'health_score': self._calculate_profile_health_score(profile)
        }
        
        # Get pending codes
        pending_codes = ApprovalCode.objects.filter(
            profile=profile,
            status='pending',
            expires_at__gt=timezone.now()
        )
        
        for code in pending_codes:
            status['pending_codes'].append({
                'code_type': code.code_type,
                'expires_at': code.expires_at,
                'created_at': code.created_at
            })
        
        # Get completed verifications
        used_codes = ApprovalCode.objects.filter(
            profile=profile,
            status='used'
        )
        
        for code in used_codes:
            status['completed_verifications'].append({
                'code_type': code.code_type,
                'verified_at': code.used_at
            })
        
        return status
    
    def _generate_unique_code(self) -> str:
        """Generate a unique approval code"""
        while True:
            code = ''.join(random.choices(
                string.ascii_uppercase + string.digits,
                k=self.code_length
            ))
            
            if not ApprovalCode.objects.filter(code=code).exists():
                return code
    
    def _send_approval_code_notification(self, approval_code: ApprovalCode):
        """Send approval code notification to user"""
        
        try:
            subject = f"Your Creator Platform Approval Code: {approval_code.code}"
            
            message = f"""
            Hello {approval_code.profile.display_name},
            
            Your approval code for {approval_code.get_code_type_display()} is:
            
            {approval_code.code}
            
            This code will expire on {approval_code.expires_at.strftime('%Y-%m-%d at %H:%M UTC')}.
            
            Please enter this code in the Creator Community Platform to complete your verification.
            
            If you didn't request this code, please ignore this email.
            
            Best regards,
            Creator Community Platform Team
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@creatorplatform.com'),
                recipient_list=[approval_code.profile.user.email],
                fail_silently=True
            )
        
        except Exception as e:
            # Log error but don't fail the code generation
            pass
    
    def _apply_authentication(self, profile: CreatorProfile, code_type: str):
        """Apply authentication effects based on code type"""
        
        if code_type == 'profile_verification':
            profile.is_validated = True
            profile.validation_date = timezone.now()
            profile.save()
        
        elif code_type == 'portfolio_approval':
            # Mark portfolio items as approved
            profile.portfolio_items.filter(
                ai_validation_score__isnull=True
            ).update(
                ai_validation_score=0.8,
                is_ai_validated=True
            )
        
        elif code_type == 'collaboration_verification':
            # Update collaboration status
            profile.collaboration_verified = True
            profile.save()
    
    def _calculate_verification_level(self, profile: CreatorProfile) -> str:
        """Calculate profile verification level"""
        
        score = 0
        
        # Basic verification
        if profile.is_validated:
            score += 30
        
        # Portfolio verification
        if profile.portfolio_items.filter(is_ai_validated=True).exists():
            score += 25
        
        # User account verification
        if profile.user.is_verified:
            score += 20
        
        # Feedback score
        avg_feedback = profile.feedback_received.aggregate(
            avg_rating=models.Avg('rating')
        )['avg_rating']
        
        if avg_feedback:
            score += min(25, int(avg_feedback * 5))
        
        if score >= 80:
            return 'verified_premium'
        elif score >= 60:
            return 'verified'
        elif score >= 40:
            return 'partially_verified'
        else:
            return 'unverified'
    
    def _calculate_profile_health_score(self, profile: CreatorProfile) -> float:
        """Calculate profile health score (REQ-4)"""
        
        score = 0.0
        max_score = 100.0
        
        # Profile completeness (30 points)
        completeness_score = 0
        if profile.bio:
            completeness_score += 10
        if profile.avatar:
            completeness_score += 5
        if profile.location:
            completeness_score += 5
        if profile.portfolio_items.count() > 0:
            completeness_score += 10
        
        score += completeness_score
        
        # Activity level (25 points)
        from django.utils import timezone
        from datetime import timedelta
        
        recent_activity = timezone.now() - timedelta(days=30)
        
        # Recent portfolio additions
        recent_portfolio = profile.portfolio_items.filter(
            created_at__gte=recent_activity
        ).count()
        score += min(10, recent_portfolio * 2)
        
        # Recent chat activity
        recent_messages = profile.sent_messages.filter(
            created_at__gte=recent_activity
        ).count()
        score += min(10, recent_messages / 10)
        
        # Recent collaborations
        recent_collabs = profile.invites_sent.filter(
            created_at__gte=recent_activity
        ).count()
        score += min(5, recent_collabs)
        
        # Feedback score (25 points)
        avg_feedback = profile.feedback_received.aggregate(
            avg_rating=models.Avg('rating')
        )['avg_rating']
        
        if avg_feedback:
            score += (avg_feedback / 5.0) * 25
        
        # Validation status (20 points)
        if profile.is_validated:
            score += 20
        
        return min(max_score, score)

# Service instance
profile_auth_service = ProfileAuthenticationService()
