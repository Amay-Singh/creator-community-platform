"""
Chat views for real-time communication (REQ-5, REQ-6)
"""
from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, MessageSerializer
from notifications.utils import create_notification, create_activity

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
        message = serializer.save(sender=self.request.user, room_id=room_id)
        
        # Create notifications for other participants
        room = ChatRoom.objects.get(id=room_id)
        recipients = room.participants.exclude(id=self.request.user.id)
        
        for recipient in recipients:
            # Create notification
            create_notification(
                user=recipient,
                notification_type='message_received',
                payload={
                    'sender_name': self.request.user.get_full_name() or self.request.user.username,
                    'sender_id': str(self.request.user.id),
                    'room_id': str(room_id),
                    'message_preview': message.content[:100] + ('...' if len(message.content) > 100 else '')
                }
            )
            
            # Create activity feed entry
            create_activity(
                user=recipient,
                actor=self.request.user,
                action_type='message_sent',
                target_type='chat_room',
                target_id=str(room_id),
                metadata={
                    'message_preview': message.content[:100] + ('...' if len(message.content) > 100 else '')
                }
            )
