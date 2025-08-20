"""
Collaboration serializers for API responses
Includes P5-003 Collaboration Invitation System serializers
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()
from .models import Collaboration, CollaborationInvite as OldCollaborationInvite
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
