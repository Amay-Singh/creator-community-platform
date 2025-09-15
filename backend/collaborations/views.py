"""
Collaboration views for project management (REQ-7, REQ-8)
P5-005: Project Management Tools API Views
"""
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction, models
from django.utils import timezone
from accounts.models import CreatorProfile

from .models import (
    Collaboration, CollaborationInvite, Project, ProjectMembership, 
    Task, TaskComment, ProjectFile, ProjectMilestone
)
from .serializers import (
    CollaborationSerializer, CollaborationInviteSerializer,
    ProjectSerializer, ProjectCreateSerializer, TaskSerializer, 
    TaskCommentSerializer, ProjectFileSerializer, ProjectMilestoneSerializer,
    KanbanBoardSerializer, TaskMoveSerializer, ProjectMembershipSerializer
)

class CollaborationListView(generics.ListCreateAPIView):
    """List and create collaborations"""
    serializer_class = CollaborationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Collaboration.objects.filter(participants=self.request.user.profile)

class CollaborationInviteView(generics.ListCreateAPIView):
    """Handle collaboration invites"""
    serializer_class = CollaborationInviteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CollaborationInvite.objects.filter(recipient=self.request.user.profile)


# P5-005 Project Management Views

class ProjectViewSet(viewsets.ModelViewSet):
    """Project management ViewSet with Kanban support"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProjectCreateSerializer
        return ProjectSerializer
    
    def get_queryset(self):
        user_profile = self.request.user.creatorprofile
        return Project.objects.filter(
            models.Q(owner=user_profile) | 
            models.Q(collaborators=user_profile)
        ).distinct()
    
    def perform_create(self, serializer):
        user_profile = self.request.user.creatorprofile
        project = serializer.save(owner=user_profile)
        
        # Create owner membership
        ProjectMembership.objects.create(
            project=project,
            member=user_profile,
            role='owner',
            can_edit_project=True,
            can_manage_tasks=True,
            can_upload_files=True,
            can_invite_members=True
        )
    
    @action(detail=True, methods=['get'])
    def kanban(self, request, pk=None):
        """Get Kanban board data for project"""
        project = self.get_object()
        
        tasks = {
            'todo': project.tasks.filter(status='todo').order_by('board_order'),
            'in_progress': project.tasks.filter(status='in_progress').order_by('board_order'),
            'review': project.tasks.filter(status='review').order_by('board_order'),
            'done': project.tasks.filter(status='done').order_by('board_order')
        }
        
        serializer = KanbanBoardSerializer(tasks)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add member to project"""
        project = self.get_object()
        
        # Check permissions
        membership = get_object_or_404(
            ProjectMembership, 
            project=project, 
            member=request.user.creatorprofile
        )
        if not membership.can_invite_members:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        member_id = request.data.get('member_id')
        role = request.data.get('role', 'member')
        
        try:
            member = CreatorProfile.objects.get(id=member_id)
            membership, created = ProjectMembership.objects.get_or_create(
                project=project,
                member=member,
                defaults={'role': role}
            )
            
            if not created:
                return Response(
                    {'error': 'Member already in project'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = ProjectMembershipSerializer(membership)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except CreatorProfile.DoesNotExist:
            return Response(
                {'error': 'Member not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class TaskViewSet(viewsets.ModelViewSet):
    """Task management ViewSet for Kanban boards"""
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user_profile = self.request.user.creatorprofile
        return Task.objects.filter(
            project__in=Project.objects.filter(
                models.Q(owner=user_profile) | 
                models.Q(collaborators=user_profile)
            )
        ).select_related('project', 'assignee', 'created_by')
    
    def perform_create(self, serializer):
        user_profile = self.request.user.creatorprofile
        assignee_id = serializer.validated_data.pop('assignee_id', None)
        
        task = serializer.save(created_by=user_profile)
        
        if assignee_id:
            try:
                assignee = CreatorProfile.objects.get(id=assignee_id)
                task.assignee = assignee
                task.save()
            except CreatorProfile.DoesNotExist:
                pass
    
    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        """Move task in Kanban board"""
        task = self.get_object()
        serializer = TaskMoveSerializer(data=request.data)
        
        if serializer.is_valid():
            with transaction.atomic():
                # Update task status and order
                task.status = serializer.validated_data['status']
                task.board_order = serializer.validated_data['board_order']
                task.save()
                
                # Reorder other tasks in the same column
                other_tasks = Task.objects.filter(
                    project=task.project,
                    status=task.status
                ).exclude(id=task.id).order_by('board_order')
                
                for i, other_task in enumerate(other_tasks):
                    if i >= task.board_order:
                        other_task.board_order = i + 1
                        other_task.save()
            
            return Response(TaskSerializer(task).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign task to user"""
        task = self.get_object()
        assignee_id = request.data.get('assignee_id')
        
        if assignee_id:
            try:
                assignee = CreatorProfile.objects.get(id=assignee_id)
                task.assignee = assignee
                task.save()
                return Response(TaskSerializer(task).data)
            except CreatorProfile.DoesNotExist:
                return Response(
                    {'error': 'Assignee not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            task.assignee = None
            task.save()
            return Response(TaskSerializer(task).data)


class TaskCommentViewSet(viewsets.ModelViewSet):
    """Task comments for collaboration"""
    serializer_class = TaskCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user_profile = self.request.user.creatorprofile
        return TaskComment.objects.filter(
            task__project__in=Project.objects.filter(
                models.Q(owner=user_profile) | 
                models.Q(collaborators=user_profile)
            )
        ).select_related('task', 'author')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user.creatorprofile)


class ProjectFileViewSet(viewsets.ModelViewSet):
    """Project file sharing and storage"""
    serializer_class = ProjectFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user_profile = self.request.user.creatorprofile
        return ProjectFile.objects.filter(
            project__in=Project.objects.filter(
                models.Q(owner=user_profile) | 
                models.Q(collaborators=user_profile)
            )
        ).select_related('project', 'uploaded_by')
    
    def perform_create(self, serializer):
        # Get file details
        uploaded_file = self.request.FILES.get('file')
        if uploaded_file:
            # Determine file type
            file_type = 'other'
            mime_type = getattr(uploaded_file, 'content_type', 'application/octet-stream')
            
            if mime_type.startswith('image/'):
                file_type = 'image'
            elif mime_type.startswith('video/'):
                file_type = 'video'
            elif mime_type.startswith('audio/'):
                file_type = 'audio'
            elif mime_type in ['application/pdf', 'application/msword', 'text/']:
                file_type = 'document'
            elif mime_type in ['application/zip', 'application/x-rar']:
                file_type = 'archive'
            
            serializer.save(
                uploaded_by=self.request.user.creatorprofile,
                file_size=uploaded_file.size,
                mime_type=mime_type,
                file_type=file_type
            )
    
    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        """Track file downloads"""
        project_file = self.get_object()
        project_file.download_count += 1
        project_file.save()
        
        return Response({
            'download_url': project_file.file.url,
            'download_count': project_file.download_count
        })


class ProjectMilestoneViewSet(viewsets.ModelViewSet):
    """Project milestone tracking"""
    serializer_class = ProjectMilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user_profile = self.request.user.creatorprofile
        return ProjectMilestone.objects.filter(
            project__in=Project.objects.filter(
                models.Q(owner=user_profile) | 
                models.Q(collaborators=user_profile)
            )
        ).select_related('project', 'created_by')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.creatorprofile)
