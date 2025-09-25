"""
Collaboration Invitation API Views for Creator Community Platform
Implements P5-003: COLL-001 REST API endpoints
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()
from django.core.cache import cache
from .invitation_system import NewCollaborationInvite, InviteTemplate, InviteManager
from .serializers import (
    CollaborationInviteSerializer, 
    InviteTemplateSerializer,
    InviteStatsSerializer,
    SendInviteSerializer,
    RespondInviteSerializer
)
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_invite(request):
    """
    Send a collaboration invite
    
    POST /api/collaborations/invites/send/
    Body: {
        "to_user_id": "uuid",
        "project_title": "string",
        "project_brief": "string",
        "scope_of_work": "string",
        "start_date": "2025-01-01",
        "end_date": "2025-02-01",
        "estimated_hours": 40,
        "compensation_type": "fixed",
        "compensation_amount": "1000.00",
        "compensation_currency": "USD",
        "compensation_details": "string",
        "nda_required": false,
        "message": "string"
    }
    """
    try:
        serializer = SendInviteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Get target user
        try:
            to_user = User.objects.get(id=data['to_user_id'])
        except User.DoesNotExist:
            return Response(
                {'error': 'Target user not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Remove to_user_id from data before creating invite
        invite_data = {k: v for k, v in data.items() if k != 'to_user_id'}
        
        # Send invite
        invite = InviteManager.send_invite(
            from_user=request.user,
            to_user=to_user,
            **invite_data
        )
        
        # Check if invite was created successfully
        if invite is None:
            logger.error("InviteManager.send_invite returned None")
            return Response(
                {'error': 'Failed to create invite'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Serialize response
        response_serializer = CollaborationInviteSerializer(invite)
        
        logger.info(f"Collaboration invite sent: {invite.id}")
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
    except ValidationError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        import traceback
        logger.error(f"Error sending invite: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return Response(
            {'error': 'Failed to send invite'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_sent_invites(request):
    """
    List invites sent by the current user
    
    GET /api/collaborations/invites/sent/?status=pending&page=1&page_size=20
    """
    try:
        status_filter = request.GET.get('status')
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)
        
        # Get invites
        invites = InviteManager.get_user_invites_sent(request.user, status_filter)
        
        # Apply pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated_invites = invites[start:end]
        
        # Serialize
        serializer = CollaborationInviteSerializer(paginated_invites, many=True)
        
        return Response({
            'invites': serializer.data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': len(invites),
                'has_next': end < len(invites),
                'has_previous': page > 1
            }
        })
        
    except Exception as e:
        logger.error(f"Error listing sent invites: {str(e)}")
        return Response(
            {'error': 'Failed to list invites'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_received_invites(request):
    """
    List invites received by the current user
    
    GET /api/collaborations/invites/received/?status=pending&page=1&page_size=20
    """
    try:
        status_filter = request.GET.get('status')
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)
        
        # Get invites
        invites = InviteManager.get_user_invites_received(request.user, status_filter)
        
        # Apply pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated_invites = invites[start:end]
        
        # Serialize
        serializer = CollaborationInviteSerializer(paginated_invites, many=True)
        
        return Response({
            'invites': serializer.data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': len(invites),
                'has_next': end < len(invites),
                'has_previous': page > 1
            }
        })
        
    except Exception as e:
        logger.error(f"Error listing received invites: {str(e)}")
        return Response(
            {'error': 'Failed to list invites'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_invite_detail(request, invite_id):
    """
    Get detailed information about a specific invite
    
    GET /api/collaborations/invites/{invite_id}/
    """
    try:
        invite = get_object_or_404(NewCollaborationInvite, id=invite_id)
        
        # Check permissions - user must be sender or recipient
        if invite.from_user != request.user and invite.to_user != request.user:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CollaborationInviteSerializer(invite)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error getting invite detail: {str(e)}")
        return Response(
            {'error': 'Failed to get invite details'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_invite(request, invite_id):
    """
    Accept a collaboration invite
    
    POST /api/collaborations/invites/{invite_id}/accept/
    Body: {
        "response_message": "string (optional)"
    }
    """
    try:
        invite = get_object_or_404(NewCollaborationInvite, id=invite_id)
        
        # Check permissions - only recipient can accept
        if invite.to_user != request.user:
            return Response(
                {'error': 'Only the recipient can accept this invite'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = RespondInviteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        response_message = serializer.validated_data.get('response_message', '')
        
        # Accept invite
        project = invite.accept(response_message)
        
        # Return updated invite and created project
        invite_serializer = CollaborationInviteSerializer(invite)
        
        return Response({
            'invite': invite_serializer.data,
            'project': {
                'id': str(project.id),
                'title': project.title,
                'status': project.status
            },
            'message': 'Invite accepted successfully'
        })
        
    except ValidationError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error accepting invite: {str(e)}")
        return Response(
            {'error': 'Failed to accept invite'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def decline_invite(request, invite_id):
    """
    Decline a collaboration invite
    
    POST /api/collaborations/invites/{invite_id}/decline/
    Body: {
        "response_message": "string (optional)"
    }
    """
    try:
        invite = get_object_or_404(NewCollaborationInvite, id=invite_id)
        
        # Check permissions - only recipient can decline
        if invite.to_user != request.user:
            return Response(
                {'error': 'Only the recipient can decline this invite'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = RespondInviteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        response_message = serializer.validated_data.get('response_message', '')
        
        # Decline invite
        invite.decline(response_message)
        
        # Return updated invite
        invite_serializer = CollaborationInviteSerializer(invite)
        
        return Response({
            'invite': invite_serializer.data,
            'message': 'Invite declined'
        })
        
    except ValidationError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error declining invite: {str(e)}")
        return Response(
            {'error': 'Failed to decline invite'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def counter_offer_invite(request, invite_id):
    """
    Make a counter offer on a collaboration invite
    
    POST /api/collaborations/invites/{invite_id}/counter/
    Body: {
        "response_message": "string",
        "counter_details": {
            "compensation_type": "hourly",
            "compensation_amount": "50.00",
            "start_date": "2025-02-01",
            "estimated_hours": 60
        }
    }
    """
    try:
        invite = get_object_or_404(NewCollaborationInvite, id=invite_id)
        
        # Check permissions - only recipient can counter
        if invite.to_user != request.user:
            return Response(
                {'error': 'Only the recipient can counter this invite'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not request.data.get('counter_details'):
            return Response(
                {'error': 'Counter offer details are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        response_message = request.data.get('response_message', '')
        counter_details = request.data['counter_details']
        
        # Make counter offer
        invite.counter_offer(counter_details, response_message)
        
        # Return updated invite
        invite_serializer = CollaborationInviteSerializer(invite)
        
        return Response({
            'invite': invite_serializer.data,
            'message': 'Counter offer submitted'
        })
        
    except ValidationError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error making counter offer: {str(e)}")
        return Response(
            {'error': 'Failed to make counter offer'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_invite(request, invite_id):
    """
    Cancel a collaboration invite (only by sender)
    
    POST /api/collaborations/invites/{invite_id}/cancel/
    """
    try:
        invite = get_object_or_404(NewCollaborationInvite, id=invite_id)
        
        # Check permissions - only sender can cancel
        if invite.from_user != request.user:
            return Response(
                {'error': 'Only the sender can cancel this invite'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Cancel invite
        invite.cancel()
        
        # Return updated invite
        invite_serializer = CollaborationInviteSerializer(invite)
        
        return Response({
            'invite': invite_serializer.data,
            'message': 'Invite cancelled'
        })
        
    except ValidationError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error cancelling invite: {str(e)}")
        return Response(
            {'error': 'Failed to cancel invite'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_invite_stats(request):
    """
    Get invitation statistics for the current user
    
    GET /api/collaborations/invites/stats/
    """
    try:
        stats = InviteManager.get_invite_stats(request.user)
        serializer = InviteStatsSerializer(stats)
        
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error getting invite stats: {str(e)}")
        return Response(
            {'error': 'Failed to get invite statistics'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def invite_templates(request):
    """
    List or create invite templates
    
    GET /api/collaborations/invites/templates/
    POST /api/collaborations/invites/templates/
    """
    if request.method == 'GET':
        try:
            templates = InviteTemplate.objects.filter(user=request.user)
            serializer = InviteTemplateSerializer(templates, many=True)
            
            return Response({
                'templates': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error listing templates: {str(e)}")
            return Response(
                {'error': 'Failed to list templates'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    elif request.method == 'POST':
        try:
            serializer = InviteTemplateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            template = serializer.save(user=request.user)
            
            response_serializer = InviteTemplateSerializer(template)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating template: {str(e)}")
            return Response(
                {'error': 'Failed to create template'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def invite_template_detail(request, template_id):
    """
    Get, update, or delete an invite template
    
    GET /api/collaborations/invites/templates/{template_id}/
    PUT /api/collaborations/invites/templates/{template_id}/
    DELETE /api/collaborations/invites/templates/{template_id}/
    """
    try:
        template = get_object_or_404(InviteTemplate, id=template_id, user=request.user)
        
        if request.method == 'GET':
            serializer = InviteTemplateSerializer(template)
            return Response(serializer.data)
        
        elif request.method == 'PUT':
            serializer = InviteTemplateSerializer(template, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            template = serializer.save()
            response_serializer = InviteTemplateSerializer(template)
            return Response(response_serializer.data)
        
        elif request.method == 'DELETE':
            template.delete()
            return Response({'message': 'Template deleted'}, status=status.HTTP_204_NO_CONTENT)
            
    except Exception as e:
        logger.error(f"Error with template detail: {str(e)}")
        return Response(
            {'error': 'Failed to process template request'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def use_template(request, template_id):
    """
    Create an invite using a template
    
    POST /api/collaborations/invites/templates/{template_id}/use/
    Body: {
        "to_user_id": "uuid",
        "overrides": {
            "start_date": "2025-01-01",
            "compensation_amount": "1500.00"
        }
    }
    """
    try:
        template = get_object_or_404(InviteTemplate, id=template_id, user=request.user)
        
        # Get target user
        to_user_id = request.data.get('to_user_id')
        if not to_user_id:
            return Response(
                {'error': 'to_user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            to_user = User.objects.get(id=to_user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Target user not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get overrides
        overrides = request.data.get('overrides', {})
        
        # Use template to create invite
        invite = template.use_template(to_user, **overrides)
        
        # Serialize response
        response_serializer = CollaborationInviteSerializer(invite)
        
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
    except ValidationError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error using template: {str(e)}")
        return Response(
            {'error': 'Failed to use template'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])  # Health endpoints should be public
def simple_invite_health(request):
    """Simple invitation health check"""
    return Response({
        'status': 'healthy',
        'service': 'collaboration_invites',
        'timestamp': timezone.now()
    })

@api_view(['GET'])
@permission_classes([AllowAny])  # Health endpoints should be public
def invite_health(request):
    """
    Health check for invitation system
    
    GET /api/collaborations/invites/health/
    """
    try:
        # Basic health checks
        total_invites = NewCollaborationInvite.objects.count()
        pending_invites = NewCollaborationInvite.objects.filter(status='pending').count()
        
        # Test cache
        cache_key = "invite_health_test"
        cache.set(cache_key, "ok", 60)
        cache_test = cache.get(cache_key) == "ok"
        
        health_data = {
            'status': 'healthy',
            'total_invites': total_invites,
            'pending_invites': pending_invites,
            'cache_working': cache_test,
            'invitation_system': 'operational',
            'timestamp': '2025-08-20T08:06:00Z'
        }
        
        return Response(health_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Invitation health check failed: {str(e)}")
        return Response(
            {'status': 'unhealthy', 'error': str(e)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
