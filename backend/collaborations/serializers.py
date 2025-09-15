"""
Collaboration serializers for API responses
Includes P5-003 Collaboration Invitation System serializers
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()
from .models import (
    Collaboration, CollaborationInvite as OldCollaborationInvite,
    Project, ProjectMembership, Task, TaskComment, ProjectFile, ProjectMilestone
)
from .invitation_system import NewCollaborationInvite, InviteTemplate
from accounts.serializers import CreatorProfileSerializer

class CollaborationSerializer(serializers.ModelSerializer):
    participants = CreatorProfileSerializer(many=True, read_only=True)
    creator = CreatorProfileSerializer(read_only=True)
    
    class Meta:
        model = Collaboration
        fields = ['id', 'title', 'description', 'collaboration_type', 'status', 'creator', 'participants', 'created_at']

class OldCollaborationInviteSerializer(serializers.ModelSerializer):
    sender = CreatorProfileSerializer(read_only=True)
    recipient = CreatorProfileSerializer(read_only=True)
    
    class Meta:
        model = OldCollaborationInvite
        fields = ['id', 'title', 'description', 'sender', 'recipient', 'status', 'match_score', 'created_at']


# P5-003 New Collaboration Invitation System Serializers

class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for invite serialization"""
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'display_name']
    
    def get_display_name(self, obj):
        try:
            return obj.creatorprofile.display_name
        except:
            return obj.username


class CollaborationInviteSerializer(serializers.ModelSerializer):
    """Serializer for collaboration invites"""
    from_user = UserBasicSerializer(read_only=True)
    to_user = UserBasicSerializer(read_only=True)
    is_expired = serializers.SerializerMethodField()
    can_respond = serializers.SerializerMethodField()
    
    class Meta:
        model = NewCollaborationInvite
        fields = [
            'id', 'from_user', 'to_user', 'project_title', 'project_brief', 
            'scope_of_work', 'start_date', 'end_date', 'estimated_hours',
            'compensation_type', 'compensation_amount', 'compensation_currency',
            'compensation_details', 'nda_required', 'status', 'message',
            'created_at', 'updated_at', 'expires_at', 'responded_at',
            'response_message', 'counter_offer_details', 'is_expired', 'can_respond'
        ]
        read_only_fields = [
            'id', 'from_user', 'to_user', 'status', 'created_at', 'updated_at',
            'expires_at', 'responded_at', 'response_message', 'counter_offer_details'
        ]
    
    def get_is_expired(self, obj):
        return obj.is_expired()
    
    def get_can_respond(self, obj):
        return obj.can_respond()


class SendInviteSerializer(serializers.Serializer):
    """Serializer for sending collaboration invites"""
    to_user_id = serializers.UUIDField()
    project_title = serializers.CharField(max_length=200)
    project_brief = serializers.CharField()
    scope_of_work = serializers.CharField()
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    estimated_hours = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    compensation_type = serializers.ChoiceField(
        choices=NewCollaborationInvite.COMPENSATION_TYPE_CHOICES,
        default='none'
    )
    compensation_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True
    )
    compensation_currency = serializers.CharField(max_length=3, default='USD')
    compensation_details = serializers.CharField(required=False, allow_blank=True)
    nda_required = serializers.BooleanField(default=False)
    message = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        # Validate date range
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError("Start date cannot be after end date")
        
        # Validate compensation
        if data.get('compensation_type') != 'none' and not data.get('compensation_amount'):
            raise serializers.ValidationError(
                "Compensation amount required when compensation type is specified"
            )
        
        return data


class RespondInviteSerializer(serializers.Serializer):
    """Serializer for responding to invites"""
    response_message = serializers.CharField(required=False, allow_blank=True)


class InviteTemplateSerializer(serializers.ModelSerializer):
    """Serializer for invite templates"""
    
    class Meta:
        model = InviteTemplate
        fields = [
            'id', 'name', 'project_title_template', 'project_brief_template',
            'scope_template', 'message_template', 'default_compensation_type',
            'default_nda_required', 'default_duration_days', 'created_at',
            'updated_at', 'usage_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'usage_count']


class InviteStatsSerializer(serializers.Serializer):
    """Serializer for invite statistics"""
    sent_total = serializers.IntegerField()
    sent_pending = serializers.IntegerField()
    sent_accepted = serializers.IntegerField()
    sent_declined = serializers.IntegerField()
    received_total = serializers.IntegerField()
    received_pending = serializers.IntegerField()
    received_accepted = serializers.IntegerField()
    received_declined = serializers.IntegerField()
    acceptance_rate = serializers.FloatField()
    response_rate = serializers.FloatField()


# P5-005 Project Management Serializers

class ProjectMembershipSerializer(serializers.ModelSerializer):
    """Serializer for project membership"""
    member = CreatorProfileSerializer(read_only=True)
    
    class Meta:
        model = ProjectMembership
        fields = [
            'id', 'member', 'role', 'can_edit_project', 'can_manage_tasks',
            'can_upload_files', 'can_invite_members', 'joined_at'
        ]


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for projects"""
    owner = CreatorProfileSerializer(read_only=True)
    memberships = ProjectMembershipSerializer(many=True, read_only=True)
    total_tasks = serializers.ReadOnlyField()
    completed_tasks = serializers.ReadOnlyField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'owner', 'status', 'priority',
            'progress_percentage', 'start_date', 'end_date', 'estimated_hours',
            'actual_hours', 'budget', 'is_public', 'allow_file_sharing',
            'enable_time_tracking', 'created_at', 'updated_at', 'last_activity_at',
            'memberships', 'total_tasks', 'completed_tasks'
        ]
        read_only_fields = ['id', 'owner', 'progress_percentage', 'actual_hours', 'last_activity_at']


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Kanban tasks"""
    assignee = CreatorProfileSerializer(read_only=True)
    created_by = CreatorProfileSerializer(read_only=True)
    assignee_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'project', 'title', 'description', 'status', 'priority',
            'assignee', 'assignee_id', 'created_by', 'due_date', 'estimated_hours',
            'actual_hours', 'board_order', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_by', 'completed_at']
    
    def validate_assignee_id(self, value):
        if value:
            from accounts.models import CreatorProfile
            try:
                CreatorProfile.objects.get(id=value)
            except CreatorProfile.DoesNotExist:
                raise serializers.ValidationError("Invalid assignee ID")
        return value


class TaskCommentSerializer(serializers.ModelSerializer):
    """Serializer for task comments"""
    author = CreatorProfileSerializer(read_only=True)
    
    class Meta:
        model = TaskComment
        fields = ['id', 'task', 'author', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author']


class ProjectFileSerializer(serializers.ModelSerializer):
    """Serializer for project files"""
    uploaded_by = CreatorProfileSerializer(read_only=True)
    file_size_mb = serializers.ReadOnlyField()
    
    class Meta:
        model = ProjectFile
        fields = [
            'id', 'project', 'task', 'name', 'description', 'file', 'file_type',
            'file_size', 'file_size_mb', 'mime_type', 'version', 'uploaded_by',
            'is_public', 'download_count', 'virus_scan_status', 'created_at'
        ]
        read_only_fields = [
            'id', 'file_size', 'mime_type', 'uploaded_by', 'download_count',
            'virus_scan_status', 'version'
        ]


class ProjectMilestoneSerializer(serializers.ModelSerializer):
    """Serializer for project milestones"""
    created_by = CreatorProfileSerializer(read_only=True)
    
    class Meta:
        model = ProjectMilestone
        fields = [
            'id', 'project', 'title', 'description', 'status', 'due_date',
            'completion_percentage', 'created_by', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_by', 'completed_at']


class KanbanBoardSerializer(serializers.Serializer):
    """Serializer for Kanban board data"""
    todo = TaskSerializer(many=True, read_only=True)
    in_progress = TaskSerializer(many=True, read_only=True)
    review = TaskSerializer(many=True, read_only=True)
    done = TaskSerializer(many=True, read_only=True)


class TaskMoveSerializer(serializers.Serializer):
    """Serializer for moving tasks in Kanban board"""
    status = serializers.ChoiceField(choices=Task.STATUS_CHOICES)
    board_order = serializers.IntegerField(min_value=0)


class ProjectCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating projects"""
    
    class Meta:
        model = Project
        fields = [
            'title', 'description', 'priority', 'start_date', 'end_date',
            'estimated_hours', 'budget', 'is_public', 'allow_file_sharing',
            'enable_time_tracking'
        ]
