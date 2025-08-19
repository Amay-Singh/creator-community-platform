"""
Enhanced Chat Views with Real-time Features
Implements REQ-9, REQ-10, REQ-11: Chat functionality, meeting invites, real-time translation
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q, Prefetch
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

from .enhanced_models import ChatRoom, Message, MeetingInvite, MeetingParticipant, TranslationRequest
from .translation_service import translation_service
from .enhanced_serializers import (
    ChatRoomSerializer, MessageSerializer, MeetingInviteSerializer,
    MessageCreateSerializer, MeetingInviteCreateSerializer, TranslationRequestSerializer
)
from accounts.models import CreatorProfile

class ChatRoomListView(generics.ListCreateAPIView):
    """List and create chat rooms (REQ-9)"""
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        profile = getattr(self.request.user, 'profile', None)
        if not profile:
            return ChatRoom.objects.none()
        
        return ChatRoom.objects.filter(
            participants=profile,
            is_active=True
        ).prefetch_related('participants', 'messages').order_by('-updated_at')
    
    def perform_create(self, serializer):
        profile = getattr(self.request.user, 'profile', None)
        if not profile:
            raise ValidationError("Profile not found")
        
        room = serializer.save(created_by=profile)
        room.participants.add(profile)
        
        # Add other participants if specified
        participant_ids = self.request.data.get('participant_ids', [])
        if participant_ids:
            participants = CreatorProfile.objects.filter(id__in=participant_ids)
            room.participants.add(*participants)

class ChatRoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Chat room detail view with message history"""
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        profile = getattr(self.request.user, 'profile', None)
        if not profile:
            return ChatRoom.objects.none()
        
        return ChatRoom.objects.filter(participants=profile)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Get recent messages
        messages = instance.messages.select_related('sender').order_by('-created_at')[:50]
        message_serializer = MessageSerializer(messages, many=True)
        
        data = serializer.data
        data['recent_messages'] = message_serializer.data
        
        return Response(data)

class MessageListCreateView(generics.ListCreateAPIView):
    """List and create messages in a chat room"""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        room_id = self.kwargs.get('room_id')
        profile = getattr(self.request.user, 'profile', None)
        
        if not profile:
            return Message.objects.none()
        
        # Verify user is participant in the room
        try:
            room = ChatRoom.objects.get(id=room_id, participants=profile)
            return room.messages.select_related('sender').order_by('-created_at')
        except ChatRoom.DoesNotExist:
            return Message.objects.none()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MessageCreateSerializer
        return MessageSerializer
    
    def perform_create(self, serializer):
        room_id = self.kwargs.get('room_id')
        profile = getattr(self.request.user, 'profile', None)
        
        if not profile:
            raise ValidationError("Profile not found")
        
        try:
            room = ChatRoom.objects.get(id=room_id, participants=profile)
        except ChatRoom.DoesNotExist:
            raise ValidationError("Chat room not found or access denied")
        
        # Detect message language
        content = serializer.validated_data.get('content', '')
        original_language = translation_service.detect_language(content)
        
        message = serializer.save(
            room=room,
            sender=profile,
            original_language=original_language
        )
        
        # Update room timestamp
        room.updated_at = timezone.now()
        room.save()
        
        # Send real-time notification via WebSocket
        self._send_realtime_message(room, message)
    
    def _send_realtime_message(self, room, message):
        """Send real-time message via WebSocket"""
        channel_layer = get_channel_layer()
        if channel_layer:
            room_group_name = f'chat_{room.id}'
            
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'id': str(message.id),
                        'sender': message.sender.display_name,
                        'content': message.content,
                        'message_type': message.message_type,
                        'created_at': message.created_at.isoformat()
                    }
                }
            )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def translate_message(request, message_id):
    """Translate a specific message (REQ-11)"""
    
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    target_language = request.data.get('target_language')
    if not target_language:
        return Response({'error': 'Target language required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        message = Message.objects.get(id=message_id)
        
        # Verify user has access to this message's room
        if not message.room.participants.filter(id=profile.id).exists():
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        
        result = translation_service.translate_message(message, target_language, profile)
        
        if result['success']:
            return Response({
                'translated_content': result['translated_content'],
                'confidence_score': result['confidence_score'],
                'target_language': target_language,
                'cached': result.get('cached', False)
            })
        else:
            return Response({
                'error': result.get('error', 'Translation failed')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Message.DoesNotExist:
        return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def batch_translate_messages(request, room_id):
    """Translate multiple messages in a room (REQ-11)"""
    
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    target_language = request.data.get('target_language')
    message_ids = request.data.get('message_ids', [])
    
    if not target_language:
        return Response({'error': 'Target language required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        room = ChatRoom.objects.get(id=room_id, participants=profile)
        
        if message_ids:
            messages = room.messages.filter(id__in=message_ids)
        else:
            # Translate recent messages if no specific IDs provided
            messages = room.messages.order_by('-created_at')[:20]
        
        result = translation_service.batch_translate_messages(
            list(messages), target_language, profile
        )
        
        return Response(result)
    
    except ChatRoom.DoesNotExist:
        return Response({'error': 'Chat room not found'}, status=status.HTTP_404_NOT_FOUND)

# Meeting Invite Views (REQ-10)
class MeetingInviteListCreateView(generics.ListCreateAPIView):
    """List and create meeting invites"""
    serializer_class = MeetingInviteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        profile = getattr(self.request.user, 'profile', None)
        if not profile:
            return MeetingInvite.objects.none()
        
        # Show meetings where user is organizer or participant
        return MeetingInvite.objects.filter(
            Q(organizer=profile) | Q(participants=profile)
        ).distinct().order_by('scheduled_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MeetingInviteCreateSerializer
        return MeetingInviteSerializer
    
    def perform_create(self, serializer):
        profile = getattr(self.request.user, 'profile', None)
        if not profile:
            raise ValidationError("Profile not found")
        
        meeting = serializer.save(organizer=profile)
        
        # Add participants
        participant_ids = self.request.data.get('participant_ids', [])
        if participant_ids:
            participants = CreatorProfile.objects.filter(id__in=participant_ids)
            for participant in participants:
                MeetingParticipant.objects.create(
                    meeting=meeting,
                    participant=participant,
                    status='pending'
                )
        
        # Send notifications to participants
        self._send_meeting_notifications(meeting)
    
    def _send_meeting_notifications(self, meeting):
        """Send meeting invite notifications"""
        # This would integrate with notification system
        pass

class MeetingInviteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Meeting invite detail view"""
    serializer_class = MeetingInviteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        profile = getattr(self.request.user, 'profile', None)
        if not profile:
            return MeetingInvite.objects.none()
        
        return MeetingInvite.objects.filter(
            Q(organizer=profile) | Q(participants=profile)
        ).distinct()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def respond_to_meeting(request, meeting_id):
    """Respond to meeting invite (accept/decline)"""
    
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    response_status = request.data.get('status')
    if response_status not in ['accepted', 'declined']:
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        participant = MeetingParticipant.objects.get(
            meeting_id=meeting_id,
            participant=profile
        )
        
        participant.status = response_status
        participant.responded_at = timezone.now()
        participant.notes = request.data.get('notes', '')
        participant.save()
        
        return Response({
            'message': f'Meeting invite {response_status}',
            'status': response_status
        })
    
    except MeetingParticipant.DoesNotExist:
        return Response({'error': 'Meeting invite not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_translation_suggestions(request, message_id):
    """Get suggested languages for message translation"""
    
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        message = Message.objects.get(id=message_id)
        
        # Verify access
        if not message.room.participants.filter(id=profile.id).exists():
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        
        suggestions = translation_service.get_translation_suggestions(message, profile)
        
        return Response({
            'suggested_languages': [
                {
                    'code': lang,
                    'name': translation_service.SUPPORTED_LANGUAGES.get(lang, lang)
                }
                for lang in suggestions
            ]
        })
    
    except Message.DoesNotExist:
        return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_participants_to_room(request, room_id):
    """Add participants to existing chat room"""
    
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    participant_ids = request.data.get('participant_ids', [])
    if not participant_ids:
        return Response({'error': 'Participant IDs required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        room = ChatRoom.objects.get(id=room_id, participants=profile)
        
        # Only room creator or existing participants can add new members
        new_participants = CreatorProfile.objects.filter(id__in=participant_ids)
        room.participants.add(*new_participants)
        
        return Response({
            'message': f'Added {len(new_participants)} participants to room',
            'participant_count': room.participants.count()
        })
    
    except ChatRoom.DoesNotExist:
        return Response({'error': 'Chat room not found'}, status=status.HTTP_404_NOT_FOUND)
