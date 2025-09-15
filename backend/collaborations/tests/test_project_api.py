"""
Test suite for Project Management API endpoints
P5-005: Project Management Tools Testing
"""
import json
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import CreatorProfile
from collaborations.models import Project, ProjectMembership, Task, ProjectFile, ProjectMilestone

User = get_user_model()


class ProjectAPITestCase(APITestCase):
    """Test cases for Project API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2', 
            email='test2@example.com',
            password='testpass123'
        )
        
        # Create creator profiles
        self.profile1 = CreatorProfile.objects.create(
            user=self.user1,
            display_name='Test Creator 1',
            bio='Test bio 1'
        )
        self.profile2 = CreatorProfile.objects.create(
            user=self.user2,
            display_name='Test Creator 2',
            bio='Test bio 2'
        )
        
        # Create test project
        self.project = Project.objects.create(
            title='Test Project',
            description='Test project description',
            owner=self.profile1,
            priority='high',
            estimated_hours=40,
            budget=Decimal('1000.00')
        )
        
        # Create project membership
        self.membership = ProjectMembership.objects.create(
            project=self.project,
            member=self.profile1,
            role='owner',
            can_edit_project=True,
            can_manage_tasks=True,
            can_upload_files=True,
            can_invite_members=True
        )
    
    def test_create_project(self):
        """Test project creation"""
        self.client.force_authenticate(user=self.user1)
        
        data = {
            'title': 'New Test Project',
            'description': 'New project description',
            'priority': 'medium',
            'estimated_hours': 20,
            'budget': '500.00',
            'is_public': False
        }
        
        response = self.client.post('/api/collaborations/api/projects/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        project = Project.objects.get(title='New Test Project')
        self.assertEqual(project.owner, self.profile1)
        self.assertEqual(project.priority, 'medium')
        
        # Check owner membership was created
        membership = ProjectMembership.objects.get(project=project, member=self.profile1)
        self.assertEqual(membership.role, 'owner')
        self.assertTrue(membership.can_edit_project)
    
    def test_list_projects(self):
        """Test listing user's projects"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get('/api/collaborations/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Project')
    
    def test_get_project_detail(self):
        """Test getting project details"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(f'/api/collaborations/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Project')
        self.assertEqual(response.data['owner']['display_name'], 'Test Creator 1')
    
    def test_update_project(self):
        """Test updating project"""
        self.client.force_authenticate(user=self.user1)
        
        data = {
            'title': 'Updated Test Project',
            'description': 'Updated description',
            'status': 'active'
        }
        
        response = self.client.patch(f'/api/collaborations/api/projects/{self.project.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, 'Updated Test Project')
        self.assertEqual(self.project.status, 'active')
    
    def test_kanban_board_view(self):
        """Test Kanban board data retrieval"""
        self.client.force_authenticate(user=self.user1)
        
        # Create test tasks
        Task.objects.create(
            project=self.project,
            title='Todo Task',
            status='todo',
            created_by=self.profile1
        )
        Task.objects.create(
            project=self.project,
            title='In Progress Task',
            status='in_progress',
            created_by=self.profile1
        )
        
        response = self.client.get(f'/api/collaborations/api/projects/{self.project.id}/kanban/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertIn('todo', response.data)
        self.assertIn('in_progress', response.data)
        self.assertIn('review', response.data)
        self.assertIn('done', response.data)
        
        self.assertEqual(len(response.data['todo']), 1)
        self.assertEqual(len(response.data['in_progress']), 1)
    
    def test_add_project_member(self):
        """Test adding member to project"""
        self.client.force_authenticate(user=self.user1)
        
        data = {
            'member_id': str(self.profile2.id),
            'role': 'member'
        }
        
        response = self.client.post(f'/api/collaborations/api/projects/{self.project.id}/add_member/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        membership = ProjectMembership.objects.get(project=self.project, member=self.profile2)
        self.assertEqual(membership.role, 'member')
    
    def test_unauthorized_project_access(self):
        """Test unauthorized access to project"""
        self.client.force_authenticate(user=self.user2)
        
        response = self.client.get(f'/api/collaborations/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_project_progress_calculation(self):
        """Test project progress calculation"""
        # Create tasks
        Task.objects.create(
            project=self.project,
            title='Task 1',
            status='done',
            created_by=self.profile1
        )
        Task.objects.create(
            project=self.project,
            title='Task 2',
            status='todo',
            created_by=self.profile1
        )
        
        self.project.update_progress()
        self.assertEqual(self.project.progress_percentage, 50)


class TaskAPITestCase(APITestCase):
    """Test cases for Task API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = CreatorProfile.objects.create(
            user=self.user,
            display_name='Test Creator',
            bio='Test bio'
        )
        
        self.project = Project.objects.create(
            title='Test Project',
            description='Test description',
            owner=self.profile
        )
        
        ProjectMembership.objects.create(
            project=self.project,
            member=self.profile,
            role='owner',
            can_manage_tasks=True
        )
        
        self.task = Task.objects.create(
            project=self.project,
            title='Test Task',
            description='Test task description',
            status='todo',
            created_by=self.profile
        )
    
    def test_create_task(self):
        """Test task creation"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'project': str(self.project.id),
            'title': 'New Task',
            'description': 'New task description',
            'priority': 'high',
            'assignee_id': str(self.profile.id)
        }
        
        response = self.client.post('/api/collaborations/api/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        task = Task.objects.get(title='New Task')
        self.assertEqual(task.project, self.project)
        self.assertEqual(task.assignee, self.profile)
        self.assertEqual(task.created_by, self.profile)
    
    def test_move_task(self):
        """Test moving task in Kanban board"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'status': 'in_progress',
            'board_order': 1
        }
        
        response = self.client.post(f'/api/collaborations/api/tasks/{self.task.id}/move/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'in_progress')
        self.assertEqual(self.task.board_order, 1)
    
    def test_assign_task(self):
        """Test task assignment"""
        self.client.force_authenticate(user=self.user)
        
        data = {'assignee_id': str(self.profile.id)}
        
        response = self.client.post(f'/api/collaborations/api/tasks/{self.task.id}/assign/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.task.refresh_from_db()
        self.assertEqual(self.task.assignee, self.profile)
    
    def test_task_completion_tracking(self):
        """Test task completion timestamp"""
        self.task.status = 'done'
        self.task.save()
        
        self.assertIsNotNone(self.task.completed_at)
        
        # Test project progress update
        self.project.refresh_from_db()
        self.assertEqual(self.project.progress_percentage, 100)


class ProjectFileAPITestCase(APITestCase):
    """Test cases for Project File API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = CreatorProfile.objects.create(
            user=self.user,
            display_name='Test Creator',
            bio='Test bio'
        )
        
        self.project = Project.objects.create(
            title='Test Project',
            description='Test description',
            owner=self.profile,
            allow_file_sharing=True
        )
        
        ProjectMembership.objects.create(
            project=self.project,
            member=self.profile,
            role='owner',
            can_upload_files=True
        )
    
    def test_file_upload_permissions(self):
        """Test file upload permissions"""
        self.client.force_authenticate(user=self.user)
        
        # Test with file sharing enabled
        response = self.client.get('/api/collaborations/api/project-files/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test project with file sharing disabled
        self.project.allow_file_sharing = False
        self.project.save()
        
        # Should still allow access for existing files
        response = self.client.get('/api/collaborations/api/project-files/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProjectMilestoneAPITestCase(APITestCase):
    """Test cases for Project Milestone API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = CreatorProfile.objects.create(
            user=self.user,
            display_name='Test Creator',
            bio='Test bio'
        )
        
        self.project = Project.objects.create(
            title='Test Project',
            description='Test description',
            owner=self.profile
        )
        
        ProjectMembership.objects.create(
            project=self.project,
            member=self.profile,
            role='owner'
        )
    
    def test_create_milestone(self):
        """Test milestone creation"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'project': str(self.project.id),
            'title': 'Project Kickoff',
            'description': 'Initial project milestone',
            'due_date': '2024-12-31T23:59:59Z',
            'completion_percentage': 0
        }
        
        response = self.client.post('/api/collaborations/api/milestones/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        milestone = ProjectMilestone.objects.get(title='Project Kickoff')
        self.assertEqual(milestone.project, self.project)
        self.assertEqual(milestone.created_by, self.profile)
    
    def test_milestone_status_tracking(self):
        """Test milestone status updates"""
        milestone = ProjectMilestone.objects.create(
            project=self.project,
            title='Test Milestone',
            due_date='2024-12-31T23:59:59Z',
            created_by=self.profile
        )
        
        self.client.force_authenticate(user=self.user)
        
        data = {
            'status': 'completed',
            'completion_percentage': 100
        }
        
        response = self.client.patch(f'/api/collaborations/api/milestones/{milestone.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        milestone.refresh_from_db()
        self.assertEqual(milestone.status, 'completed')
        self.assertEqual(milestone.completion_percentage, 100)
