"""
Test suite for Kanban board functionality
P5-005: Project Management Tools - Kanban Testing
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import CreatorProfile
from collaborations.models import Project, ProjectMembership, Task

User = get_user_model()


class KanbanBoardTestCase(APITestCase):
    """Test cases for Kanban board functionality"""
    
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
            title='Kanban Test Project',
            description='Test project for Kanban',
            owner=self.profile
        )
        
        ProjectMembership.objects.create(
            project=self.project,
            member=self.profile,
            role='owner',
            can_manage_tasks=True
        )
        
        # Create tasks in different columns
        self.todo_task = Task.objects.create(
            project=self.project,
            title='Todo Task',
            status='todo',
            board_order=0,
            created_by=self.profile
        )
        
        self.progress_task = Task.objects.create(
            project=self.project,
            title='In Progress Task',
            status='in_progress',
            board_order=0,
            created_by=self.profile
        )
        
        self.review_task = Task.objects.create(
            project=self.project,
            title='Review Task',
            status='review',
            board_order=0,
            created_by=self.profile
        )
        
        self.done_task = Task.objects.create(
            project=self.project,
            title='Done Task',
            status='done',
            board_order=0,
            created_by=self.profile
        )
    
    def test_kanban_board_structure(self):
        """Test Kanban board returns proper structure"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(f'/api/collaborations/api/projects/{self.project.id}/kanban/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check all columns exist
        self.assertIn('todo', response.data)
        self.assertIn('in_progress', response.data)
        self.assertIn('review', response.data)
        self.assertIn('done', response.data)
        
        # Check tasks are in correct columns
        self.assertEqual(len(response.data['todo']), 1)
        self.assertEqual(len(response.data['in_progress']), 1)
        self.assertEqual(len(response.data['review']), 1)
        self.assertEqual(len(response.data['done']), 1)
        
        # Verify task details
        todo_tasks = response.data['todo']
        self.assertEqual(todo_tasks[0]['title'], 'Todo Task')
        self.assertEqual(todo_tasks[0]['status'], 'todo')
    
    def test_task_move_between_columns(self):
        """Test moving tasks between Kanban columns"""
        self.client.force_authenticate(user=self.user)
        
        # Move todo task to in_progress
        data = {
            'status': 'in_progress',
            'board_order': 1
        }
        
        response = self.client.post(f'/api/collaborations/api/tasks/{self.todo_task.id}/move/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify task moved
        self.todo_task.refresh_from_db()
        self.assertEqual(self.todo_task.status, 'in_progress')
        self.assertEqual(self.todo_task.board_order, 1)
        
        # Check Kanban board reflects change
        response = self.client.get(f'/api/collaborations/api/projects/{self.project.id}/kanban/')
        self.assertEqual(len(response.data['todo']), 0)
        self.assertEqual(len(response.data['in_progress']), 2)
    
    def test_task_ordering_within_column(self):
        """Test task ordering within same column"""
        self.client.force_authenticate(user=self.user)
        
        # Create another todo task
        task2 = Task.objects.create(
            project=self.project,
            title='Todo Task 2',
            status='todo',
            board_order=1,
            created_by=self.profile
        )
        
        # Move first task to position 2
        data = {
            'status': 'todo',
            'board_order': 2
        }
        
        response = self.client.post(f'/api/collaborations/api/tasks/{self.todo_task.id}/move/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check ordering
        response = self.client.get(f'/api/collaborations/api/projects/{self.project.id}/kanban/')
        todo_tasks = response.data['todo']
        self.assertEqual(len(todo_tasks), 2)
        
        # Tasks should be ordered by board_order
        self.assertEqual(todo_tasks[0]['title'], 'Todo Task 2')
        self.assertEqual(todo_tasks[1]['title'], 'Todo Task')
    
    def test_task_completion_updates_progress(self):
        """Test that completing tasks updates project progress"""
        self.client.force_authenticate(user=self.user)
        
        # Initially 1 of 4 tasks done (25%)
        self.project.update_progress()
        self.assertEqual(self.project.progress_percentage, 25)
        
        # Move todo task to done
        data = {
            'status': 'done',
            'board_order': 0
        }
        
        response = self.client.post(f'/api/collaborations/api/tasks/{self.todo_task.id}/move/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Progress should update to 50% (2 of 4 tasks done)
        self.project.refresh_from_db()
        self.assertEqual(self.project.progress_percentage, 50)
    
    def test_task_dependencies(self):
        """Test task dependencies functionality"""
        # Create dependent task
        dependent_task = Task.objects.create(
            project=self.project,
            title='Dependent Task',
            status='todo',
            created_by=self.profile
        )
        
        # Add dependency
        dependent_task.depends_on.add(self.todo_task)
        
        self.assertEqual(dependent_task.depends_on.count(), 1)
        self.assertEqual(self.todo_task.blocking_tasks.count(), 1)
    
    def test_kanban_board_filtering(self):
        """Test Kanban board with task filtering"""
        self.client.force_authenticate(user=self.user)
        
        # Create tasks with different priorities
        high_priority_task = Task.objects.create(
            project=self.project,
            title='High Priority Task',
            status='todo',
            priority='high',
            created_by=self.profile
        )
        
        low_priority_task = Task.objects.create(
            project=self.project,
            title='Low Priority Task',
            status='todo',
            priority='low',
            created_by=self.profile
        )
        
        # Get Kanban board
        response = self.client.get(f'/api/collaborations/api/projects/{self.project.id}/kanban/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should include all tasks regardless of priority
        self.assertEqual(len(response.data['todo']), 3)  # Original + 2 new
    
    def test_task_assignment_in_kanban(self):
        """Test task assignment functionality"""
        self.client.force_authenticate(user=self.user)
        
        # Assign task to user
        data = {'assignee_id': str(self.profile.id)}
        
        response = self.client.post(f'/api/collaborations/api/tasks/{self.todo_task.id}/assign/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify assignment
        self.todo_task.refresh_from_db()
        self.assertEqual(self.todo_task.assignee, self.profile)
        
        # Check Kanban board shows assignee
        response = self.client.get(f'/api/collaborations/api/projects/{self.project.id}/kanban/')
        todo_tasks = response.data['todo']
        assigned_task = next(task for task in todo_tasks if task['id'] == str(self.todo_task.id))
        self.assertEqual(assigned_task['assignee']['display_name'], 'Test Creator')
    
    def test_kanban_permissions(self):
        """Test Kanban board access permissions"""
        # Create another user without project access
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        self.client.force_authenticate(user=other_user)
        
        # Should not be able to access Kanban board
        response = self.client.get(f'/api/collaborations/api/projects/{self.project.id}/kanban/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_bulk_task_operations(self):
        """Test bulk operations on tasks"""
        self.client.force_authenticate(user=self.user)
        
        # Create multiple tasks
        tasks = []
        for i in range(3):
            task = Task.objects.create(
                project=self.project,
                title=f'Bulk Task {i}',
                status='todo',
                board_order=i,
                created_by=self.profile
            )
            tasks.append(task)
        
        # Move all tasks to in_progress (simulate bulk operation)
        for task in tasks:
            data = {
                'status': 'in_progress',
                'board_order': task.board_order
            }
            response = self.client.post(f'/api/collaborations/api/tasks/{task.id}/move/', data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify all tasks moved
        response = self.client.get(f'/api/collaborations/api/projects/{self.project.id}/kanban/')
        self.assertEqual(len(response.data['in_progress']), 4)  # 1 original + 3 moved
    
    def test_kanban_real_time_updates(self):
        """Test Kanban board reflects real-time updates"""
        self.client.force_authenticate(user=self.user)
        
        # Get initial state
        response = self.client.get(f'/api/collaborations/api/projects/{self.project.id}/kanban/')
        initial_todo_count = len(response.data['todo'])
        
        # Create new task
        data = {
            'project': str(self.project.id),
            'title': 'Real-time Task',
            'status': 'todo',
            'description': 'Test real-time updates'
        }
        
        response = self.client.post('/api/collaborations/api/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Get updated state
        response = self.client.get(f'/api/collaborations/api/projects/{self.project.id}/kanban/')
        updated_todo_count = len(response.data['todo'])
        
        # Should have one more task in todo column
        self.assertEqual(updated_todo_count, initial_todo_count + 1)
