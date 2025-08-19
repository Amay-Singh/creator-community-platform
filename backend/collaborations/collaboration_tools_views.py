"""
Collaboration Tools Views
Implements REQ-12: Collaboration tools - whiteboards, file sharing
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404

from .collaboration_tools import collaboration_tools_service
from .models import CollaborationInvite
from accounts.models import CreatorProfile

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_whiteboard_session(request, collaboration_id):
    """Create a new whiteboard session for collaboration"""
    
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    title = request.data.get('title')
    result = collaboration_tools_service.create_whiteboard_session(collaboration_id, profile, title)
    
    if result['success']:
        return Response(result, status=status.HTTP_201_CREATED)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_whiteboard_data(request, session_id):
    """Get whiteboard data for session"""
    
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    result = collaboration_tools_service.get_whiteboard_data(session_id, profile)
    
    if result['success']:
        return Response(result['data'], status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_whiteboard_canvas(request, session_id):
    """Update whiteboard canvas data"""
    
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    canvas_data = request.data.get('canvas_data', {})
    result = collaboration_tools_service.update_whiteboard_canvas(session_id, profile, canvas_data)
    
    if result['success']:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_collaboration_file(request, collaboration_id):
    """Upload file for collaboration sharing"""
    
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    file = request.FILES.get('file')
    if not file:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    description = request.data.get('description', '')
    result = collaboration_tools_service.upload_collaboration_file(collaboration_id, profile, file, description)
    
    if result['success']:
        return Response(result, status=status.HTTP_201_CREATED)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_collaboration_files(request, collaboration_id):
    """Get all files shared in collaboration"""
    
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    result = collaboration_tools_service.get_collaboration_files(collaboration_id, profile)
    
    if result['success']:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_collaboration_file(request, collaboration_id, file_id):
    """Delete a collaboration file"""
    
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    result = collaboration_tools_service.delete_collaboration_file(collaboration_id, file_id, profile)
    
    if result['success']:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_collaboration_folder(request, collaboration_id):
    """Create a folder for organizing collaboration files"""
    
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    folder_name = request.data.get('folder_name')
    if not folder_name:
        return Response({'error': 'Folder name required'}, status=status.HTTP_400_BAD_REQUEST)
    
    result = collaboration_tools_service.create_collaboration_folder(collaboration_id, profile, folder_name)
    
    if result['success']:
        return Response(result, status=status.HTTP_201_CREATED)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_collaboration_overview(request, collaboration_id):
    """Get collaboration overview with tools status"""
    
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        collaboration = CollaborationInvite.objects.get(
            id=collaboration_id,
            status='accepted'
        )
        
        # Check if creator is part of collaboration
        if profile not in [collaboration.sender, collaboration.recipient]:
            return Response({'error': 'Not authorized for this collaboration'}, status=status.HTTP_403_FORBIDDEN)
        
        # Get files overview
        files_result = collaboration_tools_service.get_collaboration_files(collaboration_id, profile)
        files_count = len(files_result.get('files', [])) if files_result['success'] else 0
        
        overview = {
            'collaboration': {
                'id': str(collaboration.id),
                'title': collaboration.title,
                'status': collaboration.status,
                'created_at': collaboration.created_at,
                'participants': [
                    {
                        'id': str(collaboration.sender.id),
                        'name': collaboration.sender.display_name,
                        'avatar': collaboration.sender.avatar.url if collaboration.sender.avatar else None,
                        'role': 'sender'
                    },
                    {
                        'id': str(collaboration.recipient.id),
                        'name': collaboration.recipient.display_name,
                        'avatar': collaboration.recipient.avatar.url if collaboration.recipient.avatar else None,
                        'role': 'recipient'
                    }
                ]
            },
            'tools': {
                'whiteboard': {
                    'available': True,
                    'active_sessions': 0,  # Would track active sessions in production
                    'last_used': None
                },
                'file_sharing': {
                    'available': True,
                    'total_files': files_count,
                    'storage_used': '0 MB',  # Would calculate in production
                    'storage_limit': '1 GB'
                },
                'chat': {
                    'available': True,
                    'room_id': None,  # Would link to chat room in production
                    'last_message': None
                }
            },
            'activity': {
                'recent_files': files_result.get('files', [])[:5] if files_result['success'] else [],
                'recent_whiteboards': [],  # Would track in production
                'last_activity': collaboration.updated_at
            }
        }
        
        return Response(overview, status=status.HTTP_200_OK)
    
    except CollaborationInvite.DoesNotExist:
        return Response({'error': 'Collaboration not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'Failed to get overview: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
