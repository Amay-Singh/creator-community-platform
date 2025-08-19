"""
Collaboration serializers for API responses
"""
from rest_framework import serializers
from .models import Collaboration, CollaborationInvite
from accounts.serializers import CreatorProfileSerializer

class CollaborationSerializer(serializers.ModelSerializer):
    participants = CreatorProfileSerializer(many=True, read_only=True)
    creator = CreatorProfileSerializer(read_only=True)
    
    class Meta:
        model = Collaboration
        fields = ['id', 'title', 'description', 'collaboration_type', 'status', 'creator', 'participants', 'created_at']

class CollaborationInviteSerializer(serializers.ModelSerializer):
    sender = CreatorProfileSerializer(read_only=True)
    recipient = CreatorProfileSerializer(read_only=True)
    
    class Meta:
        model = CollaborationInvite
        fields = ['id', 'title', 'description', 'sender', 'recipient', 'status', 'match_score', 'created_at']
