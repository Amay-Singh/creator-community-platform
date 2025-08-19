"""
Chat views for real-time communication (REQ-5, REQ-6)
"""
from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, MessageSerializer

class ChatRoomListView(generics.ListCreateAPIView):
    """List and create chat rooms"""
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatRoom.objects.filter(participants=self.request.user)

class MessageListView(generics.ListCreateAPIView):
    """List and create messages in a chat room"""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        room_id = self.kwargs.get('room_id')
        return ChatMessage.objects.filter(room_id=room_id).order_by('-created_at')
    
    def perform_create(self, serializer):
        room_id = self.kwargs.get('room_id')
        serializer.save(sender=self.request.user, room_id=room_id)
