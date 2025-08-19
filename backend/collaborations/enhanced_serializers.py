"""
Enhanced Collaboration Serializers
Implements REQ-8: Collaboration invites with match explanations
"""
from rest_framework import serializers
from .models import CollaborationInvite
from accounts.models import CreatorProfile

class CollaborationInviteCreateSerializer(serializers.Serializer):
    """Create collaboration invite serializer"""
    recipient_id = serializers.UUIDField()
    message = serializers.CharField(max_length=500, required=False, allow_blank=True)
    project_type = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    def validate_recipient_id(self, value):
        try:
            recipient = CreatorProfile.objects.get(id=value)
            return value
        except CreatorProfile.DoesNotExist:
            raise serializers.ValidationError("Recipient profile not found")

class CollaborationInviteSerializer(serializers.ModelSerializer):
    """Collaboration invite serializer with full details"""
    sender_name = serializers.CharField(source='sender.display_name', read_only=True)
    sender_category = serializers.CharField(source='sender.get_category_display', read_only=True)
    sender_avatar = serializers.SerializerMethodField()
    recipient_name = serializers.CharField(source='recipient.display_name', read_only=True)
    recipient_category = serializers.CharField(source='recipient.get_category_display', read_only=True)
    recipient_avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = CollaborationInvite
        fields = [
            'id', 'sender', 'recipient', 'sender_name', 'sender_category', 'sender_avatar',
            'recipient_name', 'recipient_category', 'recipient_avatar', 'message', 
            'project_type', 'status', 'match_explanation', 'compatibility_score',
            'created_at', 'responded_at'
        ]
        read_only_fields = ['id', 'sender', 'recipient', 'match_explanation', 'compatibility_score', 'created_at']
    
    def get_sender_avatar(self, obj):
        return obj.sender.avatar.url if obj.sender.avatar else None
    
    def get_recipient_avatar(self, obj):
        return obj.recipient.avatar.url if obj.recipient.avatar else None

class CollaborationSuggestionSerializer(serializers.Serializer):
    """Collaboration suggestion serializer"""
    profile = serializers.DictField()
    compatibility_score = serializers.FloatField()
    suggestion_reason = serializers.CharField()
