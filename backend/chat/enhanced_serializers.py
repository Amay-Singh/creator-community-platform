"""
Enhanced Chat Serializers
Implements REQ-9, REQ-10, REQ-11: Chat functionality, meeting invites, real-time translation
"""
from rest_framework import serializers
from .enhanced_models import ChatRoom, Message, MeetingInvite, MeetingParticipant, TranslationRequest
from accounts.models import CreatorProfile

class ChatRoomSerializer(serializers.ModelSerializer):
    """Chat room serializer with participant details"""
    participants = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'room_type', 'participants', 'created_by', 
            'is_active', 'created_at', 'updated_at', 'last_message', 'unread_count'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_participants(self, obj):
        return [
            {
                'id': str(p.id),
                'display_name': p.display_name,
                'avatar_url': p.avatar.url if p.avatar else None,
                'is_online': hasattr(p.user, 'last_login') and p.user.last_login
            }
            for p in obj.participants.all()
        ]
    
    def get_last_message(self, obj):
        last_message = obj.messages.first()
        if last_message:
            return {
                'id': str(last_message.id),
                'sender': last_message.sender.display_name,
                'content': last_message.content[:100],
                'message_type': last_message.message_type,
                'created_at': last_message.created_at
            }
        return None
    
    def get_unread_count(self, obj):
        # This would require a read status tracking system
        return 0

class MessageSerializer(serializers.ModelSerializer):
    """Message serializer with translation support"""
    sender_name = serializers.CharField(source='sender.display_name', read_only=True)
    sender_avatar = serializers.SerializerMethodField()
    translations = serializers.JSONField(read_only=True)
    reply_to_content = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'room', 'sender', 'sender_name', 'sender_avatar', 'message_type',
            'content', 'file_attachment', 'original_language', 'translations',
            'is_translated', 'is_edited', 'edited_at', 'reply_to', 'reply_to_content',
            'created_at'
        ]
        read_only_fields = ['id', 'sender', 'original_language', 'is_translated', 'created_at']
    
    def get_sender_avatar(self, obj):
        return obj.sender.avatar.url if obj.sender.avatar else None
    
    def get_reply_to_content(self, obj):
        if obj.reply_to:
            return {
                'id': str(obj.reply_to.id),
                'sender': obj.reply_to.sender.display_name,
                'content': obj.reply_to.content[:50] + '...' if len(obj.reply_to.content) > 50 else obj.reply_to.content
            }
        return None

class MessageCreateSerializer(serializers.ModelSerializer):
    """Create message serializer"""
    
    class Meta:
        model = Message
        fields = ['content', 'message_type', 'file_attachment', 'reply_to']
    
    def validate_content(self, value):
        if not value and not self.initial_data.get('file_attachment'):
            raise serializers.ValidationError("Message content or file attachment required")
        return value

class MeetingInviteSerializer(serializers.ModelSerializer):
    """Meeting invite serializer with participant details"""
    organizer_name = serializers.CharField(source='organizer.display_name', read_only=True)
    participants_details = serializers.SerializerMethodField()
    my_response_status = serializers.SerializerMethodField()
    
    class Meta:
        model = MeetingInvite
        fields = [
            'id', 'organizer', 'organizer_name', 'participants_details', 'chat_room',
            'title', 'description', 'meeting_type', 'scheduled_at', 'duration_minutes',
            'location', 'meeting_url', 'meeting_id', 'meeting_password',
            'my_response_status', 'created_at'
        ]
        read_only_fields = ['id', 'organizer', 'created_at']
    
    def get_participants_details(self, obj):
        participants = MeetingParticipant.objects.filter(meeting=obj).select_related('participant')
        return [
            {
                'id': str(p.participant.id),
                'display_name': p.participant.display_name,
                'status': p.status,
                'responded_at': p.responded_at
            }
            for p in participants
        ]
    
    def get_my_response_status(self, obj):
        request = self.context.get('request')
        if request and hasattr(request.user, 'profile'):
            try:
                participant = MeetingParticipant.objects.get(
                    meeting=obj,
                    participant=request.user.profile
                )
                return participant.status
            except MeetingParticipant.DoesNotExist:
                pass
        return None

class MeetingInviteCreateSerializer(serializers.ModelSerializer):
    """Create meeting invite serializer"""
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = MeetingInvite
        fields = [
            'title', 'description', 'meeting_type', 'scheduled_at', 'duration_minutes',
            'location', 'meeting_url', 'meeting_id', 'meeting_password',
            'participant_ids', 'chat_room'
        ]
    
    def validate_scheduled_at(self, value):
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError("Meeting must be scheduled for future time")
        return value

class TranslationRequestSerializer(serializers.ModelSerializer):
    """Translation request serializer"""
    requester_name = serializers.CharField(source='requester.display_name', read_only=True)
    message_content = serializers.CharField(source='message.content', read_only=True)
    target_language_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TranslationRequest
        fields = [
            'id', 'message', 'requester', 'requester_name', 'message_content',
            'target_language', 'target_language_name', 'translated_content',
            'confidence_score', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_target_language_name(self, obj):
        from .translation_service import translation_service
        return translation_service.SUPPORTED_LANGUAGES.get(obj.target_language, obj.target_language)

class ChatRoomCreateSerializer(serializers.ModelSerializer):
    """Create chat room serializer"""
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = ChatRoom
        fields = ['name', 'room_type', 'participant_ids']
    
    def validate_room_type(self, value):
        if value not in ['individual', 'group', 'collaboration']:
            raise serializers.ValidationError("Invalid room type")
        return value
