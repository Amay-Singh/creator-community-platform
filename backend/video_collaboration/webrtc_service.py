"""
WebRTC Service for Video Collaboration
P9-003: Advanced Video Collaboration Tools
"""
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import uuid

from .models import VideoRoom, RoomParticipant, ConnectionLog, VideoMessage
from analytics.services import AnalyticsCollector

User = get_user_model()
logger = logging.getLogger(__name__)


class WebRTCSignalingService:
    """WebRTC signaling service for peer-to-peer connections"""
    
    def __init__(self):
        self.ice_servers = [
            {'urls': 'stun:stun.l.google.com:19302'},
            {'urls': 'stun:stun1.l.google.com:19302'},
            # Add TURN servers for production
            # {
            #     'urls': 'turn:your-turn-server.com:3478',
            #     'username': 'your-username',
            #     'credential': 'your-password'
            # }
        ]
    
    def generate_room_token(self, room_id: str) -> str:
        """Generate secure room token"""
        import hashlib
        import time
        
        timestamp = str(int(time.time()))
        token_data = f"{room_id}:{timestamp}:{settings.SECRET_KEY}"
        return hashlib.sha256(token_data.encode()).hexdigest()[:32]
    
    def validate_room_token(self, room_id: str, token: str) -> bool:
        """Validate room token"""
        # In production, implement proper token validation with expiration
        return len(token) == 32
    
    def get_ice_servers(self) -> List[Dict[str, Any]]:
        """Get ICE servers configuration"""
        return self.ice_servers
    
    async def create_peer_connection_config(self, room_id: str, user_id: int) -> Dict[str, Any]:
        """Create peer connection configuration"""
        return {
            'iceServers': self.get_ice_servers(),
            'iceCandidatePoolSize': 10,
            'bundlePolicy': 'balanced',
            'rtcpMuxPolicy': 'require'
        }


class VideoRoomConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for video room signaling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_id = None
        self.room_group_name = None
        self.user = None
        self.participant = None
        self.webrtc_service = WebRTCSignalingService()
    
    async def connect(self):
        """Handle WebSocket connection"""
        try:
            self.room_id = self.scope['url_route']['kwargs']['room_id']
            self.room_group_name = f'video_room_{self.room_id}'
            self.user = self.scope['user']
            
            if not self.user.is_authenticated:
                await self.close()
                return
            
            # Verify room exists and user has access
            room = await self.get_room(self.room_id)
            if not room:
                await self.close()
                return
            
            # Get or create participant
            self.participant = await self.get_or_create_participant(room, self.user)
            
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # Notify room of new participant
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'participant_joined',
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'participant_id': str(self.participant.id) if self.participant else None
                }
            )
            
            # Log connection
            await self.log_connection_event('join')
            
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            await self.close()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        try:
            if self.room_group_name:
                # Notify room of participant leaving
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'participant_left',
                        'user_id': self.user.id if self.user else None,
                        'username': self.user.username if self.user else None
                    }
                )
                
                # Leave room group
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
            
            # Update participant status
            if self.participant:
                await self.update_participant_status('left')
            
            # Log disconnection
            await self.log_connection_event('leave')
            
        except Exception as e:
            logger.error(f"WebSocket disconnection error: {e}")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'offer':
                await self.handle_webrtc_offer(data)
            elif message_type == 'answer':
                await self.handle_webrtc_answer(data)
            elif message_type == 'ice_candidate':
                await self.handle_ice_candidate(data)
            elif message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'screen_share_start':
                await self.handle_screen_share_start(data)
            elif message_type == 'screen_share_stop':
                await self.handle_screen_share_stop(data)
            elif message_type == 'whiteboard_update':
                await self.handle_whiteboard_update(data)
            elif message_type == 'recording_start':
                await self.handle_recording_start(data)
            elif message_type == 'recording_stop':
                await self.handle_recording_stop(data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
    
    async def handle_webrtc_offer(self, data):
        """Handle WebRTC offer"""
        target_user_id = data.get('target_user_id')
        offer = data.get('offer')
        
        if not target_user_id or not offer:
            return
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'webrtc_offer',
                'from_user_id': self.user.id,
                'target_user_id': target_user_id,
                'offer': offer
            }
        )
    
    async def handle_webrtc_answer(self, data):
        """Handle WebRTC answer"""
        target_user_id = data.get('target_user_id')
        answer = data.get('answer')
        
        if not target_user_id or not answer:
            return
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'webrtc_answer',
                'from_user_id': self.user.id,
                'target_user_id': target_user_id,
                'answer': answer
            }
        )
    
    async def handle_ice_candidate(self, data):
        """Handle ICE candidate"""
        target_user_id = data.get('target_user_id')
        candidate = data.get('candidate')
        
        if not target_user_id or not candidate:
            return
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'ice_candidate',
                'from_user_id': self.user.id,
                'target_user_id': target_user_id,
                'candidate': candidate
            }
        )
    
    async def handle_chat_message(self, data):
        """Handle chat message"""
        content = data.get('content', '').strip()
        if not content:
            return
        
        # Save message to database
        message = await self.save_chat_message(content)
        
        # Broadcast to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message_id': str(message.id) if message else None,
                'user_id': self.user.id,
                'username': self.user.username,
                'content': content,
                'timestamp': timezone.now().isoformat()
            }
        )
    
    async def handle_screen_share_start(self, data):
        """Handle screen share start"""
        screen_type = data.get('screen_type', 'desktop')
        resolution = data.get('resolution', '1920x1080')
        
        # Create screen share record
        await self.create_screen_share(screen_type, resolution)
        
        # Notify room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'screen_share_started',
                'user_id': self.user.id,
                'username': self.user.username,
                'screen_type': screen_type,
                'resolution': resolution
            }
        )
    
    async def handle_screen_share_stop(self, data):
        """Handle screen share stop"""
        # End screen share record
        await self.end_screen_share()
        
        # Notify room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'screen_share_stopped',
                'user_id': self.user.id,
                'username': self.user.username
            }
        )
    
    async def handle_whiteboard_update(self, data):
        """Handle whiteboard update"""
        canvas_data = data.get('canvas_data')
        if not canvas_data:
            return
        
        # Update whiteboard
        await self.update_whiteboard(canvas_data)
        
        # Broadcast to room (except sender)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'whiteboard_updated',
                'user_id': self.user.id,
                'canvas_data': canvas_data,
                'exclude_user': self.user.id
            }
        )
    
    async def handle_recording_start(self, data):
        """Handle recording start"""
        if not await self.can_record():
            return
        
        recording_id = await self.start_recording(data)
        
        # Notify room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'recording_started',
                'recording_id': str(recording_id) if recording_id else None,
                'started_by': self.user.username
            }
        )
    
    async def handle_recording_stop(self, data):
        """Handle recording stop"""
        if not await self.can_record():
            return
        
        await self.stop_recording()
        
        # Notify room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'recording_stopped',
                'stopped_by': self.user.username
            }
        )
    
    # WebSocket message handlers
    async def participant_joined(self, event):
        """Send participant joined message"""
        if event['user_id'] != self.user.id:  # Don't send to self
            await self.send(text_data=json.dumps({
                'type': 'participant_joined',
                'user_id': event['user_id'],
                'username': event['username']
            }))
    
    async def participant_left(self, event):
        """Send participant left message"""
        if event['user_id'] != self.user.id:  # Don't send to self
            await self.send(text_data=json.dumps({
                'type': 'participant_left',
                'user_id': event['user_id'],
                'username': event['username']
            }))
    
    async def webrtc_offer(self, event):
        """Send WebRTC offer to target user"""
        if event['target_user_id'] == self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'webrtc_offer',
                'from_user_id': event['from_user_id'],
                'offer': event['offer']
            }))
    
    async def webrtc_answer(self, event):
        """Send WebRTC answer to target user"""
        if event['target_user_id'] == self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'webrtc_answer',
                'from_user_id': event['from_user_id'],
                'answer': event['answer']
            }))
    
    async def ice_candidate(self, event):
        """Send ICE candidate to target user"""
        if event['target_user_id'] == self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'ice_candidate',
                'from_user_id': event['from_user_id'],
                'candidate': event['candidate']
            }))
    
    async def chat_message(self, event):
        """Send chat message to all participants"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'username': event['username'],
            'content': event['content'],
            'timestamp': event['timestamp']
        }))
    
    async def screen_share_started(self, event):
        """Send screen share started notification"""
        await self.send(text_data=json.dumps({
            'type': 'screen_share_started',
            'user_id': event['user_id'],
            'username': event['username'],
            'screen_type': event['screen_type'],
            'resolution': event['resolution']
        }))
    
    async def screen_share_stopped(self, event):
        """Send screen share stopped notification"""
        await self.send(text_data=json.dumps({
            'type': 'screen_share_stopped',
            'user_id': event['user_id'],
            'username': event['username']
        }))
    
    async def whiteboard_updated(self, event):
        """Send whiteboard update to all participants except sender"""
        if event.get('exclude_user') != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'whiteboard_updated',
                'user_id': event['user_id'],
                'canvas_data': event['canvas_data']
            }))
    
    async def recording_started(self, event):
        """Send recording started notification"""
        await self.send(text_data=json.dumps({
            'type': 'recording_started',
            'recording_id': event['recording_id'],
            'started_by': event['started_by']
        }))
    
    async def recording_stopped(self, event):
        """Send recording stopped notification"""
        await self.send(text_data=json.dumps({
            'type': 'recording_stopped',
            'stopped_by': event['stopped_by']
        }))
    
    # Database operations
    @database_sync_to_async
    def get_room(self, room_id):
        """Get video room"""
        try:
            return VideoRoom.objects.get(id=room_id)
        except VideoRoom.DoesNotExist:
            return None
    
    @database_sync_to_async
    def get_or_create_participant(self, room, user):
        """Get or create room participant"""
        try:
            participant, created = RoomParticipant.objects.get_or_create(
                room=room,
                user=user,
                defaults={
                    'status': 'joined',
                    'joined_at': timezone.now(),
                    'peer_id': str(uuid.uuid4())
                }
            )
            
            if not created and participant.status != 'joined':
                participant.status = 'joined'
                participant.joined_at = timezone.now()
                participant.save()
            
            return participant
            
        except Exception as e:
            logger.error(f"Error creating participant: {e}")
            return None
    
    @database_sync_to_async
    def update_participant_status(self, status):
        """Update participant status"""
        try:
            if self.participant:
                self.participant.status = status
                if status == 'left':
                    self.participant.left_at = timezone.now()
                self.participant.save()
        except Exception as e:
            logger.error(f"Error updating participant status: {e}")
    
    @database_sync_to_async
    def save_chat_message(self, content):
        """Save chat message to database"""
        try:
            room = VideoRoom.objects.get(id=self.room_id)
            message = VideoMessage.objects.create(
                room=room,
                sender=self.user,
                content=content,
                message_type='text'
            )
            return message
        except Exception as e:
            logger.error(f"Error saving chat message: {e}")
            return None
    
    @database_sync_to_async
    def create_screen_share(self, screen_type, resolution):
        """Create screen share record"""
        try:
            from .models import ScreenShare
            room = VideoRoom.objects.get(id=self.room_id)
            
            # End any existing screen shares by this user
            ScreenShare.objects.filter(
                room=room,
                presenter=self.user,
                status='active'
            ).update(status='ended', ended_at=timezone.now())
            
            # Create new screen share
            screen_share = ScreenShare.objects.create(
                room=room,
                presenter=self.user,
                screen_type=screen_type,
                resolution=resolution,
                status='active'
            )
            return screen_share
            
        except Exception as e:
            logger.error(f"Error creating screen share: {e}")
            return None
    
    @database_sync_to_async
    def end_screen_share(self):
        """End screen share"""
        try:
            from .models import ScreenShare
            room = VideoRoom.objects.get(id=self.room_id)
            
            ScreenShare.objects.filter(
                room=room,
                presenter=self.user,
                status='active'
            ).update(status='ended', ended_at=timezone.now())
            
        except Exception as e:
            logger.error(f"Error ending screen share: {e}")
    
    @database_sync_to_async
    def update_whiteboard(self, canvas_data):
        """Update whiteboard data"""
        try:
            from .models import Whiteboard
            room = VideoRoom.objects.get(id=self.room_id)
            
            whiteboard, created = Whiteboard.objects.get_or_create(
                room=room,
                defaults={'title': f'Whiteboard for {room.name}'}
            )
            
            whiteboard.canvas_data = canvas_data
            whiteboard.last_edited_by = self.user
            whiteboard.save()
            
        except Exception as e:
            logger.error(f"Error updating whiteboard: {e}")
    
    @database_sync_to_async
    def can_record(self):
        """Check if user can record"""
        try:
            return (self.participant and 
                    self.participant.can_record and 
                    self.participant.room.is_recording_enabled)
        except Exception:
            return False
    
    @database_sync_to_async
    def start_recording(self, data):
        """Start recording session"""
        try:
            from .models import VideoRecording
            room = VideoRoom.objects.get(id=self.room_id)
            
            recording = VideoRecording.objects.create(
                room=room,
                title=data.get('title', f'Recording of {room.name}'),
                quality=data.get('quality', '720p'),
                status='recording',
                started_at=timezone.now(),
                created_by=self.user
            )
            
            return recording.id
            
        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            return None
    
    @database_sync_to_async
    def stop_recording(self):
        """Stop recording session"""
        try:
            from .models import VideoRecording
            room = VideoRoom.objects.get(id=self.room_id)
            
            VideoRecording.objects.filter(
                room=room,
                status='recording'
            ).update(
                status='processing',
                ended_at=timezone.now(),
                processing_started_at=timezone.now()
            )
            
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
    
    @database_sync_to_async
    def log_connection_event(self, event_type):
        """Log connection event"""
        try:
            room = VideoRoom.objects.get(id=self.room_id)
            
            ConnectionLog.objects.create(
                room=room,
                user=self.user,
                event_type=event_type,
                details={
                    'channel_name': self.channel_name,
                    'room_group': self.room_group_name
                }
            )
            
        except Exception as e:
            logger.error(f"Error logging connection event: {e}")


# Global WebRTC service instance
webrtc_service = WebRTCSignalingService()
