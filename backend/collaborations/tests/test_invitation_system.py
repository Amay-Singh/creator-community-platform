"""
Tests for P5-003 Collaboration Invitation System
"""
import uuid
from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.core.cache import cache
from accounts.models import CreatorProfile
from ..invitation_system import NewCollaborationInvite, InviteTemplate, InviteManager
from ..models import Project

User = get_user_model()


class CollaborationInviteModelTestCase(TestCase):
    """Test cases for CollaborationInvite model"""
    
    def setUp(self):
        """Set up test data"""
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@test.com',
            password='testpass123'
        )
        self.recipient = User.objects.create_user(
            username='recipient', 
            email='recipient@test.com',
            password='testpass123'
        )
        
        # Create profiles
        CreatorProfile.objects.create(
            user=self.sender,
            display_name='Sender Profile',
            bio='Test sender bio',
            category='music'
        )
        CreatorProfile.objects.create(
            user=self.recipient,
            display_name='Recipient Profile', 
            bio='Test recipient bio',
            category='video'
        )
    
    def test_create_invite(self):
        """Test creating a collaboration invite"""
        invite = NewCollaborationInvite.objects.create(
            from_user=self.sender,
            to_user=self.recipient,
            project_title='Test Project',
            project_brief='Test project description',
            scope_of_work='Design and development',
            compensation_type='fixed',
            compensation_amount=1000.00,
            nda_required=True
        )
        
        self.assertEqual(invite.from_user, self.sender)
        self.assertEqual(invite.to_user, self.recipient)
        self.assertEqual(invite.status, 'pending')
        self.assertTrue(invite.can_respond())
        self.assertFalse(invite.is_expired())
        self.assertIsNotNone(invite.expires_at)
    
    def test_invite_validation(self):
        """Test invite validation rules"""
        # Test self-invite validation
        with self.assertRaises(ValidationError):
            invite = NewCollaborationInvite(
                from_user=self.sender,
                to_user=self.sender,
                project_title='Test',
                project_brief='Test',
                scope_of_work='Test'
            )
            invite.clean()
        
        # Test date validation
        with self.assertRaises(ValidationError):
            invite = NewCollaborationInvite(
                from_user=self.sender,
                to_user=self.recipient,
                project_title='Test',
                project_brief='Test',
                scope_of_work='Test',
                start_date=date.today() + timedelta(days=10),
                end_date=date.today() + timedelta(days=5)
            )
            invite.clean()
        
        # Test compensation validation
        with self.assertRaises(ValidationError):
            invite = NewCollaborationInvite(
                from_user=self.sender,
                to_user=self.recipient,
                project_title='Test',
                project_brief='Test',
                scope_of_work='Test',
                compensation_type='fixed'
                # Missing compensation_amount
            )
            invite.clean()
    
    def test_accept_invite(self):
        """Test accepting an invite"""
        invite = NewCollaborationInvite.objects.create(
            from_user=self.sender,
            to_user=self.recipient,
            project_title='Test Project',
            project_brief='Test description',
            scope_of_work='Test scope'
        )
        
        project = invite.accept('Thanks for the opportunity!')
        
        self.assertEqual(invite.status, 'accepted')
        self.assertEqual(invite.response_message, 'Thanks for the opportunity!')
        self.assertIsNotNone(invite.responded_at)
        self.assertIsInstance(project, Project)
        self.assertEqual(project.title, 'Test Project')
        self.assertIn(self.sender, project.collaborators.all())
        self.assertIn(self.recipient, project.collaborators.all())
    
    def test_decline_invite(self):
        """Test declining an invite"""
        invite = NewCollaborationInvite.objects.create(
            from_user=self.sender,
            to_user=self.recipient,
            project_title='Test Project',
            project_brief='Test description',
            scope_of_work='Test scope'
        )
        
        invite.decline('Not interested at this time')
        
        self.assertEqual(invite.status, 'declined')
        self.assertEqual(invite.response_message, 'Not interested at this time')
        self.assertIsNotNone(invite.responded_at)
    
    def test_counter_offer(self):
        """Test making a counter offer"""
        invite = NewCollaborationInvite.objects.create(
            from_user=self.sender,
            to_user=self.recipient,
            project_title='Test Project',
            project_brief='Test description',
            scope_of_work='Test scope',
            compensation_type='fixed',
            compensation_amount=1000.00
        )
        
        counter_details = {
            'compensation_amount': '1500.00',
            'estimated_hours': 60
        }
        
        invite.counter_offer(counter_details, 'I would like to propose changes')
        
        self.assertEqual(invite.status, 'countered')
        self.assertEqual(invite.counter_offer_details, counter_details)
        self.assertEqual(invite.response_message, 'I would like to propose changes')
    
    def test_cancel_invite(self):
        """Test cancelling an invite"""
        invite = NewCollaborationInvite.objects.create(
            from_user=self.sender,
            to_user=self.recipient,
            project_title='Test Project',
            project_brief='Test description',
            scope_of_work='Test scope'
        )
        
        invite.cancel()
        
        self.assertEqual(invite.status, 'cancelled')
    
    def test_expired_invite(self):
        """Test expired invite behavior"""
        invite = NewCollaborationInvite.objects.create(
            from_user=self.sender,
            to_user=self.recipient,
            project_title='Test Project',
            project_brief='Test description',
            scope_of_work='Test scope',
            expires_at=timezone.now() - timedelta(hours=1)  # Already expired
        )
        
        self.assertTrue(invite.is_expired())
        self.assertFalse(invite.can_respond())
        
        # Should not be able to accept expired invite
        with self.assertRaises(ValidationError):
            invite.accept()


class InviteTemplateTestCase(TestCase):
    """Test cases for InviteTemplate model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.target_user = User.objects.create_user(
            username='target',
            email='target@test.com', 
            password='testpass123'
        )
        
        # Create profiles
        CreatorProfile.objects.create(
            user=self.user,
            display_name='Test User',
            bio='Test bio',
            category='music'
        )
        CreatorProfile.objects.create(
            user=self.target_user,
            display_name='Target User',
            bio='Target bio',
            category='video'
        )
    
    def test_create_template(self):
        """Test creating an invite template"""
        template = InviteTemplate.objects.create(
            creator=self.user,
            name='Music Collaboration Template',
            description='Template for music collaborations',
            project_title_template='Music Project: {genre}',
            project_brief_template='Looking for collaboration on {genre} project',
            scope_of_work_template='Recording, mixing, and mastering',
            scope_template='Recording, mixing, and mastering',
            default_compensation_type='revenue_share',
            default_duration_days=60
        )
        
        self.assertEqual(template.creator, self.user)
        self.assertEqual(template.usage_count, 0)
        self.assertEqual(template.default_duration_days, 60)
    
    def test_use_template(self):
        """Test using a template to create an invite"""
        template = InviteTemplate.objects.create(
            creator=self.user,
            name='Test Template',
            description='Test template description',
            project_title_template='Test Project',
            project_brief_template='Test brief',
            scope_of_work_template='Test scope',
            scope_template='Test scope',
            default_compensation_type='fixed'
        )
        
        invite = template.use_template(
            to_user=self.target_user,
            compensation_amount=500.00,
            start_date=date.today()
        )
        
        self.assertEqual(invite.from_user, self.user)
        self.assertEqual(invite.to_user, self.target_user)
        self.assertEqual(invite.project_title, 'Test Project')
        self.assertEqual(invite.compensation_type, 'fixed')
        self.assertEqual(invite.compensation_amount, 500.00)
        
        # Check template usage count increased
        template.refresh_from_db()
        self.assertEqual(template.usage_count, 1)


class InviteManagerTestCase(TestCase):
    """Test cases for InviteManager business logic"""
    
    def setUp(self):
        """Set up test data"""
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@test.com',
            password='testpass123'
        )
        self.recipient = User.objects.create_user(
            username='recipient',
            email='recipient@test.com',
            password='testpass123'
        )
        
        # Create profiles
        CreatorProfile.objects.create(
            user=self.sender,
            display_name='Sender',
            bio='Sender bio',
            category='music'
        )
        CreatorProfile.objects.create(
            user=self.recipient,
            display_name='Recipient',
            bio='Recipient bio', 
            category='video'
        )
        
        # Clear cache
        cache.clear()
    
    def test_send_invite(self):
        """Test sending an invite through manager"""
        invite = InviteManager.send_invite(
            from_user=self.sender,
            to_user=self.recipient,
            project_title='Test Project',
            project_brief='Test description',
            scope_of_work='Test scope',
            compensation_type='hourly',
            compensation_amount=50.00
        )
        
        self.assertIsInstance(invite, NewCollaborationInvite)
        self.assertEqual(invite.from_user, self.sender)
        self.assertEqual(invite.to_user, self.recipient)
        self.assertEqual(invite.status, 'pending')
    
    def test_get_user_invites_sent(self):
        """Test getting sent invites with caching"""
        # Create test invites
        invite1 = NewCollaborationInvite.objects.create(
            from_user=self.sender,
            to_user=self.recipient,
            project_title='Project 1',
            project_brief='Brief 1',
            scope_of_work='Scope 1'
        )
        invite2 = NewCollaborationInvite.objects.create(
            from_user=self.sender,
            to_user=self.recipient,
            project_title='Project 2',
            project_brief='Brief 2',
            scope_of_work='Scope 2',
            status='accepted'
        )
        
        # Test getting all sent invites
        sent_invites = InviteManager.get_user_invites_sent(self.sender)
        self.assertEqual(len(sent_invites), 2)
        
        # Test filtering by status
        pending_invites = InviteManager.get_user_invites_sent(self.sender, 'pending')
        self.assertEqual(len(pending_invites), 1)
        self.assertEqual(pending_invites[0].id, invite1.id)
    
    def test_get_user_invites_received(self):
        """Test getting received invites with caching"""
        # Create test invites
        invite1 = NewCollaborationInvite.objects.create(
            from_user=self.sender,
            to_user=self.recipient,
            project_title='Project 1',
            project_brief='Brief 1',
            scope_of_work='Scope 1'
        )
        
        # Test getting received invites
        received_invites = InviteManager.get_user_invites_received(self.recipient)
        self.assertEqual(len(received_invites), 1)
        self.assertEqual(received_invites[0].id, invite1.id)
    
    def test_get_invite_stats(self):
        """Test getting invite statistics"""
        # Create test invites
        NewCollaborationInvite.objects.create(
            from_user=self.sender,
            to_user=self.recipient,
            project_title='Project 1',
            project_brief='Brief 1',
            scope_of_work='Scope 1'
        )
        NewCollaborationInvite.objects.create(
            from_user=self.sender,
            to_user=self.recipient,
            project_title='Project 2',
            project_brief='Brief 2',
            scope_of_work='Scope 2',
            status='accepted'
        )
        
        stats = InviteManager.get_invite_stats(self.sender)
        
        self.assertEqual(stats['sent_total'], 2)
        self.assertEqual(stats['sent_pending'], 1)
        self.assertEqual(stats['sent_accepted'], 1)
        self.assertEqual(stats['acceptance_rate'], 50.0)
        self.assertEqual(stats['response_rate'], 50.0)
    
    def test_expire_old_invites(self):
        """Test expiring old invites"""
        # Create an expired invite
        expired_invite = NewCollaborationInvite.objects.create(
            from_user=self.sender,
            to_user=self.recipient,
            project_title='Expired Project',
            project_brief='Expired brief',
            scope_of_work='Expired scope',
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        # Create a current invite
        current_invite = NewCollaborationInvite.objects.create(
            from_user=self.sender,
            to_user=self.recipient,
            project_title='Current Project',
            project_brief='Current brief',
            scope_of_work='Current scope'
        )
        
        # Expire old invites
        count = InviteManager.expire_old_invites()
        
        self.assertEqual(count, 1)
        
        # Check statuses
        expired_invite.refresh_from_db()
        current_invite.refresh_from_db()
        
        self.assertEqual(expired_invite.status, 'expired')
        self.assertEqual(current_invite.status, 'pending')


class InvitationAPITestCase(APITestCase):
    """Test cases for Invitation API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@test.com',
            password='testpass123'
        )
        self.recipient = User.objects.create_user(
            username='recipient',
            email='recipient@test.com',
            password='testpass123'
        )
        
        # Create profiles
        CreatorProfile.objects.create(
            user=self.sender,
            display_name='Sender',
            bio='Sender bio',
            category='music'
        )
        CreatorProfile.objects.create(
            user=self.recipient,
            display_name='Recipient',
            bio='Recipient bio',
            category='video'
        )
    
    def test_send_invite_api(self):
        """Test sending invite via API"""
        self.client.force_authenticate(user=self.sender)
        url = '/api/collaborations/invites/send/'
        data = {
            'to_user_id': str(self.recipient.id),
            'project_title': 'API Test Project',
            'project_brief': 'Test project via API',
            'scope_of_work': 'Development and testing',
            'compensation_type': 'fixed',
            'compensation_amount': '1000.00',
            'nda_required': True,
            'message': 'Looking forward to working together!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['project_title'], 'API Test Project')
        self.assertEqual(response.data['status'], 'pending')
    
    def test_list_sent_invites_api(self):
        """Test listing sent invites via API"""
        self.client.force_authenticate(user=self.sender)
        
        # Create test invite
        NewCollaborationInvite.objects.create(
            from_user=self.sender,
            to_user=self.recipient,
            project_title='Test Project',
            project_brief='Test brief',
            scope_of_work='Test scope'
        )
        
        url = '/api/collaborations/invites/sent/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('invites', response.data)
        self.assertIn('pagination', response.data)
        self.assertEqual(len(response.data['invites']), 1)
    
    def test_list_received_invites_api(self):
        """Test listing received invites via API"""
        self.client.force_authenticate(user=self.recipient)
        
        # Create test invite
        NewCollaborationInvite.objects.create(
            from_user=self.sender,
            to_user=self.recipient,
            project_title='Test Project',
            project_brief='Test brief',
            scope_of_work='Test scope'
        )
        
        url = '/api/collaborations/invites/received/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('invites', response.data)
        self.assertEqual(len(response.data['invites']), 1)
    
    def test_accept_invite_api(self):
        """Test accepting invite via API"""
        self.client.force_authenticate(user=self.recipient)
        
        # Create test invite
        self.invite = NewCollaborationInvite.objects.create(
            from_user=self.sender,
            to_user=self.recipient,
            project_title='Test Project',
            project_brief='Test brief',
            scope_of_work='Test scope'
        )
        
        url = f'/api/collaborations/invites/{self.invite.id}/accept/'
        data = {'response_message': 'Excited to work together!'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('invite', response.data)
        self.assertIn('project', response.data)
        self.assertEqual(response.data['invite']['status'], 'accepted')
    
    def test_decline_invite_api(self):
        """Test declining invite via API"""
        self.client.force_authenticate(user=self.recipient)
        
        # Create test invite
        self.invite = NewCollaborationInvite.objects.create(
            from_user=self.sender,
            to_user=self.recipient,
            project_title='Test Project',
            project_brief='Test brief',
            scope_of_work='Test scope'
        )
        
        url = f'/api/collaborations/invites/{self.invite.id}/decline/'
        data = {'response_message': 'Not available at this time'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['invite']['status'], 'declined')
    
    def test_get_invite_stats_api(self):
        """Test getting invite stats via API"""
        self.client.force_authenticate(user=self.sender)
        
        # Create test invites
        NewCollaborationInvite.objects.create(
            from_user=self.sender,
            to_user=self.recipient,
            project_title='Project 1',
            project_brief='Brief 1',
            scope_of_work='Scope 1'
        )
        
        url = reverse('collaborations:get_invite_stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('sent_total', response.data)
        self.assertIn('acceptance_rate', response.data)
    
    def test_invite_health_api(self):
        """Test invite health check API"""
        self.client.force_authenticate(user=self.sender)
        url = '/api/collaborations/invites/health/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], 'healthy')
        self.assertIn('total_invites', response.data)
        self.assertIn('cache_working', response.data)
    
    def test_authentication_required(self):
        """Test that authentication is required for protected endpoints"""
        url = reverse('collaborations:send_invite')
        data = {
            'to_user_id': str(self.recipient.id),
            'project_title': 'Test',
            'project_brief': 'Test',
            'scope_of_work': 'Test'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_permission_denied_for_wrong_user(self):
        """Test permission denied for operations on other users' invites"""
        # Create invite from sender to recipient
        invite = NewCollaborationInvite.objects.create(
            from_user=self.sender,
            to_user=self.recipient,
            project_title='Test Project',
            project_brief='Test brief',
            scope_of_work='Test scope'
        )
        
        # Try to accept as sender (should fail)
        self.client.force_authenticate(user=self.sender)
        url = f'/api/collaborations/invites/{invite.id}/accept/'
        
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
