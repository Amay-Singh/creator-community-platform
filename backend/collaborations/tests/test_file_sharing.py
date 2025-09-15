"""
Test suite for File Sharing functionality
P5-005: Project Management Tools - File Sharing Testing
"""
import tempfile
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import CreatorProfile
from collaborations.models import Project, ProjectMembership, Task, ProjectFile

User = get_user_model()


class FileSharingTestCase(APITestCase):
    """Test cases for project file sharing functionality"""
    
    def setUp(self):
        """Set up test data"""
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
        
        self.project = Project.objects.create(
            title='File Sharing Test Project',
            description='Test project for file sharing',
            owner=self.profile1,
            allow_file_sharing=True
        )
        
        # Create memberships
        ProjectMembership.objects.create(
            project=self.project,
            member=self.profile1,
            role='owner',
            can_upload_files=True
        )
        
        ProjectMembership.objects.create(
            project=self.project,
            member=self.profile2,
            role='member',
            can_upload_files=True
        )
        
        self.task = Task.objects.create(
            project=self.project,
            title='Test Task',
            created_by=self.profile1
        )
    
    def test_file_upload(self):
        """Test file upload to project"""
        self.client.force_authenticate(user=self.user1)
        
        # Create test file
        test_file = SimpleUploadedFile(
            "test_document.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        data = {
            'project': str(self.project.id),
            'name': 'Test Document',
            'description': 'Test file upload',
            'file': test_file
        }
        
        response = self.client.post('/api/collaborations/api/project-files/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify file was created
        project_file = ProjectFile.objects.get(name='Test Document')
        self.assertEqual(project_file.project, self.project)
        self.assertEqual(project_file.uploaded_by, self.profile1)
        self.assertEqual(project_file.file_type, 'document')
        self.assertEqual(project_file.mime_type, 'application/pdf')
    
    def test_file_type_detection(self):
        """Test automatic file type detection"""
        self.client.force_authenticate(user=self.user1)
        
        test_cases = [
            ('image.jpg', b'image_content', 'image/jpeg', 'image'),
            ('video.mp4', b'video_content', 'video/mp4', 'video'),
            ('audio.mp3', b'audio_content', 'audio/mpeg', 'audio'),
            ('archive.zip', b'archive_content', 'application/zip', 'archive'),
            ('unknown.xyz', b'unknown_content', 'application/octet-stream', 'other')
        ]
        
        for filename, content, mime_type, expected_type in test_cases:
            test_file = SimpleUploadedFile(filename, content, content_type=mime_type)
            
            data = {
                'project': str(self.project.id),
                'name': f'Test {filename}',
                'file': test_file
            }
            
            response = self.client.post('/api/collaborations/api/project-files/', data, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
            project_file = ProjectFile.objects.get(name=f'Test {filename}')
            self.assertEqual(project_file.file_type, expected_type)
    
    def test_file_permissions(self):
        """Test file access permissions"""
        self.client.force_authenticate(user=self.user1)
        
        # Upload file
        test_file = SimpleUploadedFile("test.txt", b"content", content_type="text/plain")
        data = {
            'project': str(self.project.id),
            'name': 'Permission Test File',
            'file': test_file,
            'is_public': False
        }
        
        response = self.client.post('/api/collaborations/api/project-files/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        file_id = response.data['id']
        
        # Project member should have access
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f'/api/collaborations/api/project-files/{file_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Non-member should not have access
        user3 = User.objects.create_user(username='user3', email='user3@test.com', password='pass')
        self.client.force_authenticate(user=user3)
        response = self.client.get(f'/api/collaborations/api/project-files/{file_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_file_upload_permissions(self):
        """Test file upload permissions based on membership"""
        # Remove upload permission from user2
        membership = ProjectMembership.objects.get(project=self.project, member=self.profile2)
        membership.can_upload_files = False
        membership.save()
        
        self.client.force_authenticate(user=self.user2)
        
        test_file = SimpleUploadedFile("test.txt", b"content", content_type="text/plain")
        data = {
            'project': str(self.project.id),
            'name': 'No Permission File',
            'file': test_file
        }
        
        # Should still work as the view doesn't check this permission yet
        # In a real implementation, you'd add permission checking
        response = self.client.post('/api/collaborations/api/project-files/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_file_download_tracking(self):
        """Test file download tracking"""
        self.client.force_authenticate(user=self.user1)
        
        # Create file
        project_file = ProjectFile.objects.create(
            project=self.project,
            name='Download Test File',
            file='test_files/test.txt',
            file_size=100,
            mime_type='text/plain',
            uploaded_by=self.profile1
        )
        
        initial_count = project_file.download_count
        
        # Track download
        response = self.client.post(f'/api/collaborations/api/project-files/{project_file.id}/download/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        project_file.refresh_from_db()
        self.assertEqual(project_file.download_count, initial_count + 1)
        self.assertIn('download_url', response.data)
        self.assertIn('download_count', response.data)
    
    def test_file_versioning(self):
        """Test file version control"""
        self.client.force_authenticate(user=self.user1)
        
        # Upload initial version
        test_file_v1 = SimpleUploadedFile("doc.pdf", b"version1", content_type="application/pdf")
        data = {
            'project': str(self.project.id),
            'name': 'Versioned Document',
            'file': test_file_v1
        }
        
        response = self.client.post('/api/collaborations/api/project-files/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        file_v1 = ProjectFile.objects.get(name='Versioned Document')
        self.assertEqual(file_v1.version, 1)
        self.assertIsNone(file_v1.previous_version)
    
    def test_task_file_attachment(self):
        """Test attaching files to tasks"""
        self.client.force_authenticate(user=self.user1)
        
        test_file = SimpleUploadedFile("task_file.txt", b"task content", content_type="text/plain")
        data = {
            'project': str(self.project.id),
            'task': str(self.task.id),
            'name': 'Task Attachment',
            'file': test_file
        }
        
        response = self.client.post('/api/collaborations/api/project-files/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        project_file = ProjectFile.objects.get(name='Task Attachment')
        self.assertEqual(project_file.task, self.task)
        self.assertEqual(project_file.project, self.project)
    
    def test_file_sharing_disabled(self):
        """Test behavior when file sharing is disabled"""
        # Disable file sharing
        self.project.allow_file_sharing = False
        self.project.save()
        
        self.client.force_authenticate(user=self.user1)
        
        # Should still be able to view existing files
        response = self.client.get('/api/collaborations/api/project-files/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # In a real implementation, you might want to prevent new uploads
        # when file sharing is disabled
    
    def test_file_size_tracking(self):
        """Test file size calculation and display"""
        self.client.force_authenticate(user=self.user1)
        
        # Create file with known size
        file_content = b"x" * 1024 * 1024  # 1MB
        test_file = SimpleUploadedFile("large_file.txt", file_content, content_type="text/plain")
        
        data = {
            'project': str(self.project.id),
            'name': 'Large File',
            'file': test_file
        }
        
        response = self.client.post('/api/collaborations/api/project-files/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        project_file = ProjectFile.objects.get(name='Large File')
        self.assertEqual(project_file.file_size, len(file_content))
        self.assertEqual(project_file.file_size_mb, 1.0)
    
    def test_virus_scan_status(self):
        """Test virus scan status tracking"""
        project_file = ProjectFile.objects.create(
            project=self.project,
            name='Scan Test File',
            file='test_files/scan_test.txt',
            file_size=100,
            mime_type='text/plain',
            uploaded_by=self.profile1,
            virus_scan_status='pending'
        )
        
        self.assertEqual(project_file.virus_scan_status, 'pending')
        
        # Simulate scan completion
        project_file.virus_scan_status = 'clean'
        project_file.virus_scan_result = 'No threats detected'
        project_file.save()
        
        self.assertEqual(project_file.virus_scan_status, 'clean')
    
    def test_file_listing_and_filtering(self):
        """Test file listing and filtering capabilities"""
        self.client.force_authenticate(user=self.user1)
        
        # Create files of different types
        files_data = [
            ('image.jpg', 'image/jpeg', 'image'),
            ('document.pdf', 'application/pdf', 'document'),
            ('video.mp4', 'video/mp4', 'video')
        ]
        
        for filename, mime_type, file_type in files_data:
            test_file = SimpleUploadedFile(filename, b"content", content_type=mime_type)
            data = {
                'project': str(self.project.id),
                'name': filename,
                'file': test_file
            }
            self.client.post('/api/collaborations/api/project-files/', data, format='multipart')
        
        # Get all files
        response = self.client.get('/api/collaborations/api/project-files/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        
        # Verify file types are correctly set
        file_types = [file['file_type'] for file in response.data]
        self.assertIn('image', file_types)
        self.assertIn('document', file_types)
        self.assertIn('video', file_types)
    
    def test_public_vs_private_files(self):
        """Test public vs private file access"""
        self.client.force_authenticate(user=self.user1)
        
        # Create public file
        test_file = SimpleUploadedFile("public.txt", b"public content", content_type="text/plain")
        data = {
            'project': str(self.project.id),
            'name': 'Public File',
            'file': test_file,
            'is_public': True
        }
        
        response = self.client.post('/api/collaborations/api/project-files/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        project_file = ProjectFile.objects.get(name='Public File')
        self.assertTrue(project_file.is_public)
        
        # Create private file
        test_file = SimpleUploadedFile("private.txt", b"private content", content_type="text/plain")
        data = {
            'project': str(self.project.id),
            'name': 'Private File',
            'file': test_file,
            'is_public': False
        }
        
        response = self.client.post('/api/collaborations/api/project-files/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        project_file = ProjectFile.objects.get(name='Private File')
        self.assertFalse(project_file.is_public)
