"""
Video Collaboration Views
P9-003: Advanced Video Collaboration Tools
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q, Count
from datetime import timedelta
import logging

from .models import (
    VideoRoom, RoomParticipant, VideoRecording, ScreenShare, 
    Whiteboard, VideoMessage, ConnectionLog
)
from .webrtc_service import webrtc_service
from analytics.services import AnalyticsCollector

User = get_user_model()
logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_video_room(request):
    """Create a new video room"""
    try:
        data = request.data
        
        room = VideoRoom.objects.create(
            name=data.get('name', 'Video Collaboration'),
            description=data.get('description', ''),
            room_type=data.get('room_type', 'collaboration'),
            max_participants=data.get('max_participants', 10),
            is_recording_enabled=data.get('is_recording_enabled', True),
            is_screen_sharing_enabled=data.get('is_screen_sharing_enabled', True),
            is_chat_enabled=data.get('is_chat_enabled', True),
            is_whiteboard_enabled=data.get('is_whiteboard_enabled', True),
            require_approval=data.get('require_approval', False),
            host=request.user,
            scheduled_start=data.get('scheduled_start'),
            scheduled_end=data.get('scheduled_end')
        )
        
        # Generate room token
        room.room_token = webrtc_service.generate_room_token(str(room.id))
        room.save()
        
        # Create host participant
        RoomParticipant.objects.create(
            room=room,
            user=request.user,
            role='host',
            status='invited',
            can_share_screen=True,
            can_record=True,
            can_mute_others=True,
            can_manage_participants=True
        )
        
        # Add invited participants
        invited_users = data.get('invited_users', [])
        for user_id in invited_users:
            try:
                user = User.objects.get(id=user_id)
                RoomParticipant.objects.create(
                    room=room,
                    user=user,
                    role='participant',
                    status='invited'
                )
            except User.DoesNotExist:
                continue
        
        # Track analytics
        AnalyticsCollector.track_event(
            'video_room_created',
            user=request.user,
            event_data={
                'room_id': str(room.id),
                'room_type': room.room_type,
                'max_participants': room.max_participants,
                'invited_count': len(invited_users)
            }
        )
        
        return Response({
            'room_id': str(room.id),
            'name': room.name,
            'room_token': room.room_token,
            'ice_servers': webrtc_service.get_ice_servers(),
            'websocket_url': f'/ws/video/{room.id}/',
            'created_at': room.created_at
        })
        
    except Exception as e:
        logger.error(f"Error creating video room: {e}")
        return Response({
            'error': 'Failed to create video room',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_video_room(request, room_id):
    """Get video room details"""
    try:
        room = VideoRoom.objects.get(id=room_id)
        
        # Check if user has access
        participant = RoomParticipant.objects.filter(
            room=room, user=request.user
        ).first()
        
        if not participant and room.host != request.user:
            return Response({
                'error': 'Access denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get participants
        participants = RoomParticipant.objects.filter(room=room).select_related('user')
        participants_data = [
            {
                'user_id': p.user.id,
                'username': p.user.username,
                'role': p.role,
                'status': p.status,
                'joined_at': p.joined_at,
                'can_share_screen': p.can_share_screen,
                'can_record': p.can_record
            }
            for p in participants
        ]
        
        # Get active screen shares
        active_screen_shares = ScreenShare.objects.filter(
            room=room, status='active'
        ).select_related('presenter')
        
        screen_shares_data = [
            {
                'presenter_id': ss.presenter.id,
                'presenter_username': ss.presenter.username,
                'screen_type': ss.screen_type,
                'resolution': ss.resolution,
                'started_at': ss.started_at
            }
            for ss in active_screen_shares
        ]
        
        # Get whiteboard if exists
        whiteboard_data = None
        try:
            whiteboard = room.whiteboard
            whiteboard_data = {
                'id': str(whiteboard.id),
                'canvas_data': whiteboard.canvas_data,
                'canvas_width': whiteboard.canvas_width,
                'canvas_height': whiteboard.canvas_height,
                'is_locked': whiteboard.is_locked,
                'last_edited_by': whiteboard.last_edited_by.username if whiteboard.last_edited_by else None
            }
        except:
            pass
        
        return Response({
            'room_id': str(room.id),
            'name': room.name,
            'description': room.description,
            'room_type': room.room_type,
            'status': room.status,
            'host_id': room.host.id,
            'host_username': room.host.username,
            'max_participants': room.max_participants,
            'is_recording_enabled': room.is_recording_enabled,
            'is_screen_sharing_enabled': room.is_screen_sharing_enabled,
            'is_chat_enabled': room.is_chat_enabled,
            'is_whiteboard_enabled': room.is_whiteboard_enabled,
            'scheduled_start': room.scheduled_start,
            'scheduled_end': room.scheduled_end,
            'actual_start': room.actual_start,
            'actual_end': room.actual_end,
            'participants': participants_data,
            'active_screen_shares': screen_shares_data,
            'whiteboard': whiteboard_data,
            'room_token': room.room_token,
            'websocket_url': f'/ws/video/{room.id}/',
            'ice_servers': webrtc_service.get_ice_servers()
        })
        
    except VideoRoom.DoesNotExist:
        return Response({
            'error': 'Video room not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error getting video room: {e}")
        return Response({
            'error': 'Failed to get video room',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_video_room(request, room_id):
    """Join a video room"""
    try:
        room = VideoRoom.objects.get(id=room_id)
        
        # Check if room is active or can be joined
        if room.status == 'ended':
            return Response({
                'error': 'Room has ended'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create participant
        participant, created = RoomParticipant.objects.get_or_create(
            room=room,
            user=request.user,
            defaults={
                'role': 'participant',
                'status': 'joined',
                'joined_at': timezone.now()
            }
        )
        
        if not created:
            participant.status = 'joined'
            participant.joined_at = timezone.now()
            participant.save()
        
        # Update room status to active if first join
        if room.status == 'scheduled':
            room.status = 'active'
            room.actual_start = timezone.now()
            room.save()
        
        # Track analytics
        AnalyticsCollector.track_event(
            'video_room_joined',
            user=request.user,
            event_data={
                'room_id': str(room.id),
                'room_type': room.room_type,
                'participant_created': created
            }
        )
        
        return Response({
            'message': 'Successfully joined room',
            'participant_id': participant.id,
            'role': participant.role,
            'permissions': {
                'can_share_screen': participant.can_share_screen,
                'can_record': participant.can_record,
                'can_mute_others': participant.can_mute_others,
                'can_manage_participants': participant.can_manage_participants
            }
        })
        
    except VideoRoom.DoesNotExist:
        return Response({
            'error': 'Video room not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error joining video room: {e}")
        return Response({
            'error': 'Failed to join video room',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def leave_video_room(request, room_id):
    """Leave a video room"""
    try:
        room = VideoRoom.objects.get(id=room_id)
        
        participant = RoomParticipant.objects.filter(
            room=room, user=request.user
        ).first()
        
        if participant:
            participant.status = 'left'
            participant.left_at = timezone.now()
            participant.save()
        
        # Track analytics
        AnalyticsCollector.track_event(
            'video_room_left',
            user=request.user,
            event_data={
                'room_id': str(room.id),
                'duration_minutes': participant.left_at - participant.joined_at if participant and participant.joined_at else 0
            }
        )
        
        return Response({
            'message': 'Successfully left room'
        })
        
    except VideoRoom.DoesNotExist:
        return Response({
            'error': 'Video room not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error leaving video room: {e}")
        return Response({
            'error': 'Failed to leave video room',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_user_rooms(request):
    """List user's video rooms"""
    try:
        # Get rooms where user is host or participant
        hosted_rooms = VideoRoom.objects.filter(host=request.user)
        participated_rooms = VideoRoom.objects.filter(
            participants=request.user
        ).exclude(host=request.user)
        
        def serialize_room(room):
            return {
                'room_id': str(room.id),
                'name': room.name,
                'room_type': room.room_type,
                'status': room.status,
                'scheduled_start': room.scheduled_start,
                'scheduled_end': room.scheduled_end,
                'participant_count': room.participants.count(),
                'is_host': room.host == request.user,
                'created_at': room.created_at
            }
        
        return Response({
            'hosted_rooms': [serialize_room(room) for room in hosted_rooms],
            'participated_rooms': [serialize_room(room) for room in participated_rooms]
        })
        
    except Exception as e:
        logger.error(f"Error listing user rooms: {e}")
        return Response({
            'error': 'Failed to list rooms',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_room_recordings(request, room_id):
    """Get recordings for a room"""
    try:
        room = VideoRoom.objects.get(id=room_id)
        
        # Check access
        participant = RoomParticipant.objects.filter(
            room=room, user=request.user
        ).first()
        
        if not participant and room.host != request.user:
            return Response({
                'error': 'Access denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        recordings = VideoRecording.objects.filter(room=room)
        
        recordings_data = [
            {
                'recording_id': str(rec.id),
                'title': rec.title,
                'status': rec.status,
                'quality': rec.quality,
                'duration_seconds': rec.duration_seconds,
                'duration_formatted': rec.duration_formatted,
                'file_size_mb': rec.file_size_mb,
                'video_file_url': rec.video_file_url,
                'thumbnail_url': rec.thumbnail_url,
                'started_at': rec.started_at,
                'ended_at': rec.ended_at,
                'created_by': rec.created_by.username,
                'is_public': rec.is_public
            }
            for rec in recordings
        ]
        
        return Response({
            'recordings': recordings_data,
            'total_count': len(recordings_data)
        })
        
    except VideoRoom.DoesNotExist:
        return Response({
            'error': 'Video room not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error getting room recordings: {e}")
        return Response({
            'error': 'Failed to get recordings',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_room_messages(request, room_id):
    """Get chat messages for a room"""
    try:
        room = VideoRoom.objects.get(id=room_id)
        
        # Check access
        participant = RoomParticipant.objects.filter(
            room=room, user=request.user
        ).first()
        
        if not participant and room.host != request.user:
            return Response({
                'error': 'Access denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        messages = VideoMessage.objects.filter(
            room=room
        ).select_related('sender').order_by('timestamp')
        
        messages_data = [
            {
                'message_id': msg.id,
                'sender_id': msg.sender.id,
                'sender_username': msg.sender.username,
                'message_type': msg.message_type,
                'content': msg.content,
                'file_url': msg.file_url,
                'file_name': msg.file_name,
                'timestamp': msg.timestamp,
                'reactions': msg.reactions
            }
            for msg in messages
        ]
        
        return Response({
            'messages': messages_data,
            'total_count': len(messages_data)
        })
        
    except VideoRoom.DoesNotExist:
        return Response({
            'error': 'Video room not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error getting room messages: {e}")
        return Response({
            'error': 'Failed to get messages',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_room_settings(request, room_id):
    """Update room settings"""
    try:
        room = VideoRoom.objects.get(id=room_id)
        
        # Only host can update settings
        if room.host != request.user:
            return Response({
                'error': 'Only room host can update settings'
            }, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data
        
        # Update allowed fields
        if 'name' in data:
            room.name = data['name']
        if 'description' in data:
            room.description = data['description']
        if 'max_participants' in data:
            room.max_participants = data['max_participants']
        if 'is_recording_enabled' in data:
            room.is_recording_enabled = data['is_recording_enabled']
        if 'is_screen_sharing_enabled' in data:
            room.is_screen_sharing_enabled = data['is_screen_sharing_enabled']
        if 'is_chat_enabled' in data:
            room.is_chat_enabled = data['is_chat_enabled']
        if 'is_whiteboard_enabled' in data:
            room.is_whiteboard_enabled = data['is_whiteboard_enabled']
        
        room.save()
        
        return Response({
            'message': 'Room settings updated successfully',
            'room_id': str(room.id)
        })
        
    except VideoRoom.DoesNotExist:
        return Response({
            'error': 'Video room not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error updating room settings: {e}")
        return Response({
            'error': 'Failed to update room settings',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_video_analytics(request):
    """Get video collaboration analytics"""
    try:
        # Get user's video collaboration stats
        hosted_rooms_count = VideoRoom.objects.filter(host=request.user).count()
        participated_rooms_count = VideoRoom.objects.filter(
            participants=request.user
        ).exclude(host=request.user).count()
        
        # Get recent activity
        recent_rooms = VideoRoom.objects.filter(
            Q(host=request.user) | Q(participants=request.user)
        ).distinct().order_by('-created_at')[:10]
        
        # Calculate total session time
        total_session_minutes = 0
        for room in recent_rooms:
            if room.actual_start and room.actual_end:
                duration = (room.actual_end - room.actual_start).total_seconds() / 60
                total_session_minutes += duration
        
        # Get recordings count
        recordings_count = VideoRecording.objects.filter(
            room__in=recent_rooms
        ).count()
        
        return Response({
            'hosted_rooms_count': hosted_rooms_count,
            'participated_rooms_count': participated_rooms_count,
            'total_session_minutes': int(total_session_minutes),
            'recordings_count': recordings_count,
            'recent_rooms': [
                {
                    'room_id': str(room.id),
                    'name': room.name,
                    'room_type': room.room_type,
                    'status': room.status,
                    'duration_minutes': room.duration_minutes,
                    'participant_count': room.participants.count(),
                    'created_at': room.created_at
                }
                for room in recent_rooms
            ]
        })
        
    except Exception as e:
        logger.error(f"Error getting video analytics: {e}")
        return Response({
            'error': 'Failed to get video analytics',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def video_health_check(request):
    """Health check for video collaboration service"""
    try:
        # Check database connectivity
        rooms_count = VideoRoom.objects.count()
        
        # Check WebRTC service
        ice_servers = webrtc_service.get_ice_servers()
        
        return Response({
            'status': 'healthy',
            'database_connected': True,
            'total_rooms': rooms_count,
            'ice_servers_count': len(ice_servers),
            'webrtc_service': 'operational',
            'timestamp': timezone.now()
        })
        
    except Exception as e:
        logger.error(f"Video health check failed: {e}")
        return Response({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
