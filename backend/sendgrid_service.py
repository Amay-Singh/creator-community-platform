"""
SendGrid Email Service Integration
Production-ready email service using SendGrid API (Free Tier: 100 emails/day)
"""
import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

class SendGridService:
    """SendGrid Email Service"""
    
    def __init__(self):
        self.api_key = os.environ.get('SENDGRID_API_KEY', '')
        self.from_email = os.environ.get('SENDGRID_FROM_EMAIL', 'noreply@creator-platform.com')
        self.client = None
        
        if self.api_key:
            self.client = SendGridAPIClient(api_key=self.api_key)
    
    def is_configured(self):
        """Check if SendGrid is properly configured"""
        return bool(self.api_key and self.client)
    
    def send_email(self, to_email, subject, html_content, plain_content=None):
        """Send email using SendGrid"""
        if not self.is_configured():
            logger.warning("SendGrid not configured, email not sent")
            return {
                'success': False,
                'error': 'SendGrid not configured',
                'message_id': None
            }
        
        try:
            # Create email message
            message = Mail(
                from_email=Email(self.from_email),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            if plain_content:
                message.content = [
                    Content("text/plain", plain_content),
                    Content("text/html", html_content)
                ]
            
            # Send email
            response = self.client.send(message)
            
            return {
                'success': True,
                'status_code': response.status_code,
                'message_id': response.headers.get('X-Message-Id', 'unknown'),
                'timestamp': timezone.now()
            }
            
        except Exception as e:
            logger.error(f"SendGrid email error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message_id': None,
                'timestamp': timezone.now()
            }
    
    def send_collaboration_invite(self, to_email, inviter_name, project_name, invite_link):
        """Send collaboration invitation email"""
        subject = f"Collaboration Invitation from {inviter_name}"
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">You're Invited to Collaborate!</h2>
            
            <p>Hi there!</p>
            
            <p><strong>{inviter_name}</strong> has invited you to collaborate on the project:</p>
            <h3 style="color: #007bff;">{project_name}</h3>
            
            <p>Join this exciting collaboration and bring your creative skills to the project!</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{invite_link}" 
                   style="background-color: #007bff; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    Accept Invitation
                </a>
            </div>
            
            <p style="color: #666; font-size: 14px;">
                If the button doesn't work, copy and paste this link into your browser:<br>
                <a href="{invite_link}">{invite_link}</a>
            </p>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
            <p style="color: #999; font-size: 12px;">
                This invitation was sent by Creator Community Platform.<br>
                If you didn't expect this invitation, you can safely ignore this email.
            </p>
        </div>
        """
        
        plain_content = f"""
        You're Invited to Collaborate!
        
        {inviter_name} has invited you to collaborate on: {project_name}
        
        Accept the invitation by visiting: {invite_link}
        
        ---
        Creator Community Platform
        """
        
        return self.send_email(to_email, subject, html_content, plain_content)
    
    def send_notification_email(self, to_email, notification_type, content):
        """Send notification email"""
        subject_map = {
            'match_found': 'New Creator Match Found!',
            'message_received': 'New Message Received',
            'project_update': 'Project Update',
            'system_notification': 'Platform Notification'
        }
        
        subject = subject_map.get(notification_type, 'Creator Platform Notification')
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">{subject}</h2>
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px;">
                {content}
            </div>
            <p style="color: #666; font-size: 14px; margin-top: 20px;">
                Visit your <a href="https://creator-platform.com/dashboard">dashboard</a> 
                to see more details.
            </p>
        </div>
        """
        
        return self.send_email(to_email, subject, html_content)
    
    def health_check(self):
        """Check SendGrid service health"""
        if not self.is_configured():
            return {
                'status': 'unhealthy',
                'error': 'API key not configured',
                'configured': False
            }
        
        try:
            # Test API connection (this doesn't send an email)
            # SendGrid doesn't have a ping endpoint, so we check if client is initialized
            return {
                'status': 'healthy',
                'configured': True,
                'from_email': self.from_email,
                'daily_limit': 100,
                'service': 'sendgrid_free_tier',
                'timestamp': timezone.now()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'configured': True,
                'timestamp': timezone.now()
            }

# Global instance
sendgrid_service = SendGridService()
