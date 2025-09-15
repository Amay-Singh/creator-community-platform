"""
Chat views for real-time communication (REQ-5, REQ-6)
"""
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.cache import cache
from .models import ChatRoom, ChatMessage, MessageReadStatus
from .serializers import ChatRoomSerializer, ChatMessageSerializer, MessageSerializer
from notifications.utils import create_notification, create_activity
from accounts.models import CreatorProfile

User = get_user_model()

class MessagePagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class ChatRoomListView(generics.ListCreateAPIView):
    """List and create chat rooms"""
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        profile = get_object_or_404(CreatorProfile, user=self.request.user)
        return ChatRoom.objects.filter(participants=profile, is_active=True).order_by('-last_message_at')
    
    def perform_create(self, serializer):
        profile = get_object_or_404(CreatorProfile, user=self.request.user)
        room = serializer.save(created_by=profile)
        room.participants.add(profile)

class MessageListView(generics.ListCreateAPIView):
    """List and create messages in a chat room"""
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MessagePagination
    
    def get_queryset(self):
        room_id = self.kwargs.get('room_id')
        profile = get_object_or_404(CreatorProfile, user=self.request.user)
        
        # Verify user has access to this room
        room = get_object_or_404(ChatRoom, id=room_id, participants=profile)
        
        return ChatMessage.objects.filter(
            room=room, 
            is_deleted=False
        ).select_related('sender').order_by('-created_at')
    
    def perform_create(self, serializer):
        room_id = self.kwargs.get('room_id')
        profile = get_object_or_404(CreatorProfile, user=self.request.user)
        room = get_object_or_404(ChatRoom, id=room_id, participants=profile)
        
        message = serializer.save(sender=profile, room=room)
        
        # Update room's last message timestamp
        room.last_message_at = message.created_at
        room.save(update_fields=['last_message_at'])
        
        # Create notifications for other participants
        recipients = room.participants.exclude(id=profile.id)
        
        for recipient in recipients:
            # Create notification
            create_notification(
                user=recipient.user,
                notification_type='message_received',
                payload={
                    'sender_name': profile.display_name,
                    'sender_id': str(profile.id),
                    'room_id': str(room_id),
                    'message_preview': message.content[:100] + ('...' if len(message.content) > 100 else '')
                }
            )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def room_detail(request, room_id):
    """Get detailed information about a chat room"""
    profile = get_object_or_404(CreatorProfile, user=request.user)
    room = get_object_or_404(ChatRoom, id=room_id, participants=profile)
    
    serializer = ChatRoomSerializer(room)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_messages_read(request, room_id):
    """Mark messages as read in a chat room"""
    profile = get_object_or_404(CreatorProfile, user=request.user)
    room = get_object_or_404(ChatRoom, id=room_id, participants=profile)
    
    # Get unread messages
    unread_messages = ChatMessage.objects.filter(
        room=room,
        is_deleted=False
    ).exclude(
        read_status__reader=profile
    )
    
    # Mark as read
    read_statuses = []
    for message in unread_messages:
        read_status, created = MessageReadStatus.objects.get_or_create(
            message=message,
            reader=profile
        )
        if created:
            read_statuses.append(read_status)
    
    return Response({
        'marked_read': len(read_statuses),
        'total_unread': unread_messages.count()
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_presence(request):
    """Get presence status for users"""
    user_ids = request.GET.getlist('user_ids')
    presence_data = {}
    
    for user_id in user_ids:
        cache_key = f"presence_{user_id}"
        presence = cache.get(cache_key, {
            'is_online': False,
            'last_seen': None,
            'room_id': None
        })
        presence_data[user_id] = presence
    
    return Response(presence_data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def typing_status(request, room_id):
    """Get typing indicators for a room"""
    profile = get_object_or_404(CreatorProfile, user=request.user)
    room = get_object_or_404(ChatRoom, id=room_id, participants=profile)
    
    typing_users = []
    for participant in room.participants.all():
        if participant.id != profile.id:  # Exclude current user
            cache_key = f"typing_{room_id}_{participant.user.id}"
            if cache.get(cache_key):
                typing_users.append({
                    'user_id': str(participant.user.id),
                    'username': participant.user.username,
                    'display_name': participant.display_name
                })
    
    return Response({'typing_users': typing_users})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_file(request, room_id):
    """Upload a file to a chat room"""
    profile = get_object_or_404(CreatorProfile, user=request.user)
    room = get_object_or_404(ChatRoom, id=room_id, participants=profile)
    
    file = request.FILES.get('file')
    if not file:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    # File size validation (10MB limit)
    if file.size > 10 * 1024 * 1024:
        return Response({'error': 'File size exceeds 10MB limit'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create message with file
    message = ChatMessage.objects.create(
        room=room,
        sender=profile,
        content=f"Shared file: {file.name}",
        message_type='file',
        file=file,
        file_name=file.name,
        file_size=file.size
    )
    
    # Update room timestamp
    room.last_message_at = message.created_at
    room.save(update_fields=['last_message_at'])
    
    serializer = ChatMessageSerializer(message)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
