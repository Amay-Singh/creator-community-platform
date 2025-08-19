"""
Collaboration Tools Service
Implements REQ-12: Collaboration tools - whiteboards, file sharing
"""
import os
import uuid
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone
from typing import Dict, List, Optional
from .models import CollaborationInvite
from accounts.models import CreatorProfile

class CollaborationToolsService:
    """
    Service for collaboration tools including whiteboards and file sharing
    """
    
    def __init__(self):
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.allowed_file_types = [
            'pdf', 'doc', 'docx', 'txt', 'rtf',  # Documents
            'jpg', 'jpeg', 'png', 'gif', 'svg', 'webp',  # Images
            'mp4', 'mov', 'avi', 'mkv',  # Videos
            'mp3', 'wav', 'flac', 'm4a',  # Audio
            'zip', 'rar', '7z',  # Archives
            'psd', 'ai', 'sketch', 'fig',  # Design files
            'blend', 'obj', 'fbx',  # 3D files
        ]
    
    def create_whiteboard_session(self, collaboration_id: str, creator: CreatorProfile, title: str = None) -> Dict:
        """Create a new whiteboard session for collaboration"""
        
        try:
            collaboration = CollaborationInvite.objects.get(
                id=collaboration_id,
                status='accepted'
            )
            
            # Check if creator is part of collaboration
            if creator not in [collaboration.sender, collaboration.recipient]:
                return {
                    'success': False,
                    'error': 'Not authorized for this collaboration'
                }
            
            session_id = str(uuid.uuid4())
            whiteboard_data = {
                'session_id': session_id,
                'collaboration_id': collaboration_id,
                'title': title or f"Whiteboard - {collaboration.title}",
                'created_by': str(creator.id),
                'created_at': timezone.now().isoformat(),
                'participants': [
                    {
                        'id': str(collaboration.sender.id),
                        'name': collaboration.sender.display_name,
                        'avatar': collaboration.sender.avatar.url if collaboration.sender.avatar else None
                    },
                    {
                        'id': str(collaboration.recipient.id),
                        'name': collaboration.recipient.display_name,
                        'avatar': collaboration.recipient.avatar.url if collaboration.recipient.avatar else None
                    }
                ],
                'canvas_data': {
                    'objects': [],
                    'background': '#ffffff',
                    'dimensions': {'width': 1920, 'height': 1080}
                },
                'tools': {
                    'pen': {'color': '#000000', 'size': 2},
                    'highlighter': {'color': '#ffff00', 'size': 10},
                    'eraser': {'size': 20},
                    'text': {'font': 'Arial', 'size': 16, 'color': '#000000'}
                },
                'version': 1,
                'last_updated': timezone.now().isoformat()
            }
            
            # Store whiteboard data (in production, use Redis or database)
            self._store_whiteboard_data(session_id, whiteboard_data)
            
            return {
                'success': True,
                'session_id': session_id,
                'whiteboard_url': f"/collaboration/whiteboard/{session_id}",
                'participants': whiteboard_data['participants']
            }
        
        except CollaborationInvite.DoesNotExist:
            return {
                'success': False,
                'error': 'Collaboration not found or not accepted'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to create whiteboard: {str(e)}'
            }
    
    def update_whiteboard_canvas(self, session_id: str, creator: CreatorProfile, canvas_data: Dict) -> Dict:
        """Update whiteboard canvas data"""
        
        try:
            whiteboard_data = self._get_whiteboard_data(session_id)
            if not whiteboard_data:
                return {
                    'success': False,
                    'error': 'Whiteboard session not found'
                }
            
            # Check if creator is participant
            participant_ids = [p['id'] for p in whiteboard_data['participants']]
            if str(creator.id) not in participant_ids:
                return {
                    'success': False,
                    'error': 'Not authorized for this whiteboard'
                }
            
            # Update canvas data
            whiteboard_data['canvas_data'] = canvas_data
            whiteboard_data['version'] += 1
            whiteboard_data['last_updated'] = timezone.now().isoformat()
            whiteboard_data['last_updated_by'] = str(creator.id)
            
            self._store_whiteboard_data(session_id, whiteboard_data)
            
            return {
                'success': True,
                'version': whiteboard_data['version'],
                'last_updated': whiteboard_data['last_updated']
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to update whiteboard: {str(e)}'
            }
    
    def get_whiteboard_data(self, session_id: str, creator: CreatorProfile) -> Dict:
        """Get whiteboard data for session"""
        
        try:
            whiteboard_data = self._get_whiteboard_data(session_id)
            if not whiteboard_data:
                return {
                    'success': False,
                    'error': 'Whiteboard session not found'
                }
            
            # Check if creator is participant
            participant_ids = [p['id'] for p in whiteboard_data['participants']]
            if str(creator.id) not in participant_ids:
                return {
                    'success': False,
                    'error': 'Not authorized for this whiteboard'
                }
            
            return {
                'success': True,
                'data': whiteboard_data
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get whiteboard data: {str(e)}'
            }
    
    def upload_collaboration_file(self, collaboration_id: str, creator: CreatorProfile, file, description: str = None) -> Dict:
        """Upload file for collaboration sharing"""
        
        try:
            collaboration = CollaborationInvite.objects.get(
                id=collaboration_id,
                status='accepted'
            )
            
            # Check if creator is part of collaboration
            if creator not in [collaboration.sender, collaboration.recipient]:
                return {
                    'success': False,
                    'error': 'Not authorized for this collaboration'
                }
            
            # Validate file
            validation_result = self._validate_file(file)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            # Generate unique filename
            file_extension = file.name.split('.')[-1].lower()
            unique_filename = f"collaboration_{collaboration_id}_{uuid.uuid4().hex}.{file_extension}"
            file_path = f"collaborations/{collaboration_id}/files/{unique_filename}"
            
            # Save file
            saved_path = default_storage.save(file_path, file)
            file_url = default_storage.url(saved_path)
            
            # Create file metadata
            file_metadata = {
                'id': str(uuid.uuid4()),
                'collaboration_id': collaboration_id,
                'uploaded_by': str(creator.id),
                'uploader_name': creator.display_name,
                'original_filename': file.name,
                'file_path': saved_path,
                'file_url': file_url,
                'file_size': file.size,
                'file_type': file_extension,
                'description': description,
                'uploaded_at': timezone.now().isoformat(),
                'downloads': 0
            }
            
            # Store file metadata
            self._store_file_metadata(collaboration_id, file_metadata)
            
            return {
                'success': True,
                'file_id': file_metadata['id'],
                'file_url': file_url,
                'filename': file.name,
                'file_size': file.size
            }
        
        except CollaborationInvite.DoesNotExist:
            return {
                'success': False,
                'error': 'Collaboration not found or not accepted'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to upload file: {str(e)}'
            }
    
    def get_collaboration_files(self, collaboration_id: str, creator: CreatorProfile) -> Dict:
        """Get all files shared in collaboration"""
        
        try:
            collaboration = CollaborationInvite.objects.get(
                id=collaboration_id,
                status='accepted'
            )
            
            # Check if creator is part of collaboration
            if creator not in [collaboration.sender, collaboration.recipient]:
                return {
                    'success': False,
                    'error': 'Not authorized for this collaboration'
                }
            
            files = self._get_collaboration_files(collaboration_id)
            
            return {
                'success': True,
                'files': files,
                'total_files': len(files)
            }
        
        except CollaborationInvite.DoesNotExist:
            return {
                'success': False,
                'error': 'Collaboration not found or not accepted'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get files: {str(e)}'
            }
    
    def delete_collaboration_file(self, collaboration_id: str, file_id: str, creator: CreatorProfile) -> Dict:
        """Delete a collaboration file"""
        
        try:
            collaboration = CollaborationInvite.objects.get(
                id=collaboration_id,
                status='accepted'
            )
            
            # Check if creator is part of collaboration
            if creator not in [collaboration.sender, collaboration.recipient]:
                return {
                    'success': False,
                    'error': 'Not authorized for this collaboration'
                }
            
            file_metadata = self._get_file_metadata(collaboration_id, file_id)
            if not file_metadata:
                return {
                    'success': False,
                    'error': 'File not found'
                }
            
            # Check if creator uploaded the file or is collaboration owner
            if (file_metadata['uploaded_by'] != str(creator.id) and 
                str(creator.id) != str(collaboration.sender.id)):
                return {
                    'success': False,
                    'error': 'Not authorized to delete this file'
                }
            
            # Delete file from storage
            if default_storage.exists(file_metadata['file_path']):
                default_storage.delete(file_metadata['file_path'])
            
            # Remove file metadata
            self._remove_file_metadata(collaboration_id, file_id)
            
            return {
                'success': True,
                'message': 'File deleted successfully'
            }
        
        except CollaborationInvite.DoesNotExist:
            return {
                'success': False,
                'error': 'Collaboration not found or not accepted'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to delete file: {str(e)}'
            }
    
    def create_collaboration_folder(self, collaboration_id: str, creator: CreatorProfile, folder_name: str) -> Dict:
        """Create a folder for organizing collaboration files"""
        
        try:
            collaboration = CollaborationInvite.objects.get(
                id=collaboration_id,
                status='accepted'
            )
            
            # Check if creator is part of collaboration
            if creator not in [collaboration.sender, collaboration.recipient]:
                return {
                    'success': False,
                    'error': 'Not authorized for this collaboration'
                }
            
            folder_metadata = {
                'id': str(uuid.uuid4()),
                'collaboration_id': collaboration_id,
                'name': folder_name,
                'created_by': str(creator.id),
                'creator_name': creator.display_name,
                'created_at': timezone.now().isoformat(),
                'file_count': 0
            }
            
            self._store_folder_metadata(collaboration_id, folder_metadata)
            
            return {
                'success': True,
                'folder_id': folder_metadata['id'],
                'folder_name': folder_name
            }
        
        except CollaborationInvite.DoesNotExist:
            return {
                'success': False,
                'error': 'Collaboration not found or not accepted'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to create folder: {str(e)}'
            }
    
    def _validate_file(self, file) -> Dict:
        """Validate uploaded file"""
        
        # Check file size
        if file.size > self.max_file_size:
            return {
                'valid': False,
                'error': f'File size exceeds {self.max_file_size // (1024*1024)}MB limit'
            }
        
        # Check file type
        file_extension = file.name.split('.')[-1].lower()
        if file_extension not in self.allowed_file_types:
            return {
                'valid': False,
                'error': f'File type .{file_extension} not allowed'
            }
        
        return {'valid': True}
    
    def _store_whiteboard_data(self, session_id: str, data: Dict):
        """Store whiteboard data (mock implementation - use Redis in production)"""
        # In production, store in Redis or database
        pass
    
    def _get_whiteboard_data(self, session_id: str) -> Optional[Dict]:
        """Get whiteboard data (mock implementation)"""
        # In production, retrieve from Redis or database
        return None
    
    def _store_file_metadata(self, collaboration_id: str, metadata: Dict):
        """Store file metadata (mock implementation)"""
        # In production, store in database
        pass
    
    def _get_collaboration_files(self, collaboration_id: str) -> List[Dict]:
        """Get collaboration files (mock implementation)"""
        # In production, retrieve from database
        return []
    
    def _get_file_metadata(self, collaboration_id: str, file_id: str) -> Optional[Dict]:
        """Get file metadata (mock implementation)"""
        # In production, retrieve from database
        return None
    
    def _remove_file_metadata(self, collaboration_id: str, file_id: str):
        """Remove file metadata (mock implementation)"""
        # In production, remove from database
        pass
    
    def _store_folder_metadata(self, collaboration_id: str, metadata: Dict):
        """Store folder metadata (mock implementation)"""
        # In production, store in database
        pass

# Service instance
collaboration_tools_service = CollaborationToolsService()
