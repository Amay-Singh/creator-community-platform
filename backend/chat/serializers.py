"""
Chat serializers for API responses
"""
from rest_framework import serializers
from .models import ChatRoom, ChatMessage, MeetingInvite
from accounts.serializers import CreatorProfileSerializer

class ChatRoomSerializer(serializers.ModelSerializer):
    participants = CreatorProfileSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'room_type', 'name', 'participants', 'is_active', 'created_at', 'last_message_at']

class MessageSerializer(serializers.ModelSerializer):
    sender = CreatorProfileSerializer(read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'content', 'message_type', 'sender', 'file', 'created_at', 'is_edited']

class MeetingInviteSerializer(serializers.ModelSerializer):
    organizer = CreatorProfileSerializer(read_only=True)
    
    class Meta:
        model = MeetingInvite
        fields = ['id', 'title', 'description', 'meeting_type', 'scheduled_at', 'duration_minutes', 'status', 'organizer']
