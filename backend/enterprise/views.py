"""
Enterprise Team Management Views
P9-004: Enterprise Team Management
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
import uuid
import secrets

from .models import (
    Organization, OrganizationMembership, Team, TeamMembership,
    OrganizationProject, OrganizationInvitation, OrganizationSettings
)
from .permissions import (
    CanManageOrganization, CanManageMembers, CanManageBilling,
    CanManageProjects, CanViewAnalytics, check_organization_limits,
    get_user_organizations, get_user_permissions_in_organization
)
from analytics.services import AnalyticsCollector

User = get_user_model()
logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_organization(request):
    """Create a new organization"""
    try:
        data = request.data
        
        # Generate unique slug
        base_slug = data.get('name', '').lower().replace(' ', '-').replace('_', '-')
        slug = base_slug
        counter = 1
        while Organization.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        organization = Organization.objects.create(
            name=data.get('name'),
            slug=slug,
            description=data.get('description', ''),
            organization_type=data.get('organization_type', 'startup'),
            website=data.get('website', ''),
            email=data.get('email', ''),
            owner=request.user
        )
        
        # Create owner membership
        OrganizationMembership.objects.create(
            organization=organization,
            user=request.user,
            role='owner',
            status='active',
            joined_at=timezone.now()
        )
        
        # Create default settings
        OrganizationSettings.objects.create(organization=organization)
        
        # Track analytics
        AnalyticsCollector.track_event(
            'organization_created',
            user=request.user,
            event_data={
                'organization_id': str(organization.id),
                'organization_type': organization.organization_type,
                'subscription_tier': organization.subscription_tier
            }
        )
        
        return Response({
            'organization_id': str(organization.id),
            'name': organization.name,
            'slug': organization.slug,
            'subscription_tier': organization.subscription_tier,
            'member_count': 1,
            'created_at': organization.created_at
        })
        
    except Exception as e:
        logger.error(f"Error creating organization: {e}")
        return Response({
            'error': 'Failed to create organization',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_user_organizations(request):
    """List organizations user belongs to"""
    try:
        organizations = get_user_organizations(request.user)
        
        org_data = []
        for org in organizations:
            membership = OrganizationMembership.objects.get(
                organization=org,
                user=request.user,
                status='active'
            )
            
            org_data.append({
                'organization_id': str(org.id),
                'name': org.name,
                'slug': org.slug,
                'organization_type': org.organization_type,
                'subscription_tier': org.subscription_tier,
                'member_count': org.member_count,
                'user_role': membership.role,
                'permissions': membership.get_permissions(),
                'is_owner': org.owner == request.user,
                'created_at': org.created_at
            })
        
        return Response({
            'organizations': org_data,
            'total_count': len(org_data)
        })
        
    except Exception as e:
        logger.error(f"Error listing user organizations: {e}")
        return Response({
            'error': 'Failed to list organizations',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organization_details(request, org_id):
    """Get detailed organization information"""
    try:
        organization = Organization.objects.get(id=org_id)
        
        # Check membership
        membership = OrganizationMembership.objects.get(
            organization=organization,
            user=request.user,
            status='active'
        )
        
        # Get organization stats
        member_count = organization.memberships.filter(status='active').count()
        project_count = organization.projects.count()
        team_count = organization.teams.count()
        
        # Get recent activity (last 30 days)
        recent_projects = organization.projects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        recent_members = organization.memberships.filter(
            joined_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        return Response({
            'organization_id': str(organization.id),
            'name': organization.name,
            'slug': organization.slug,
            'description': organization.description,
            'organization_type': organization.organization_type,
            'website': organization.website,
            'email': organization.email,
            'subscription_tier': organization.subscription_tier,
            'subscription_status': organization.subscription_status,
            'owner_id': organization.owner.id,
            'owner_username': organization.owner.username,
            'user_role': membership.role,
            'user_permissions': membership.get_permissions(),
            'stats': {
                'member_count': member_count,
                'project_count': project_count,
                'team_count': team_count,
                'recent_projects': recent_projects,
                'recent_members': recent_members
            },
            'limits': {
                'max_members': organization.max_members,
                'max_projects': organization.max_projects,
                'max_storage_gb': organization.max_storage_gb,
                'max_video_hours': organization.max_video_hours
            },
            'branding': {
                'logo_url': organization.logo_url,
                'primary_color': organization.primary_color,
                'secondary_color': organization.secondary_color,
                'custom_domain': organization.custom_domain
            },
            'created_at': organization.created_at,
            'updated_at': organization.updated_at
        })
        
    except Organization.DoesNotExist:
        return Response({
            'error': 'Organization not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except OrganizationMembership.DoesNotExist:
        return Response({
            'error': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        logger.error(f"Error getting organization details: {e}")
        return Response({
            'error': 'Failed to get organization details',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invite_member(request, org_id):
    """Invite a new member to organization"""
    try:
        organization = Organization.objects.get(id=org_id)
        
        # Check permissions
        membership = OrganizationMembership.objects.get(
            organization=organization,
            user=request.user,
            status='active'
        )
        
        permissions = membership.get_permissions()
        if not permissions.get('manage_members', False):
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check organization limits
        if not check_organization_limits(organization, 'add_member'):
            return Response({
                'error': 'Organization member limit reached'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data
        email = data.get('email')
        role = data.get('role', 'member')
        message = data.get('message', '')
        
        if not email:
            return Response({
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user is already a member
        if OrganizationMembership.objects.filter(
            organization=organization,
            user__email=email
        ).exists():
            return Response({
                'error': 'User is already a member'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if invitation already exists
        existing_invitation = OrganizationInvitation.objects.filter(
            organization=organization,
            email=email,
            status='pending'
        ).first()
        
        if existing_invitation:
            return Response({
                'error': 'Invitation already sent'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create invitation
        invitation_token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(days=7)
        
        invitation = OrganizationInvitation.objects.create(
            organization=organization,
            email=email,
            role=role,
            invited_by=request.user,
            invitation_token=invitation_token,
            message=message,
            expires_at=expires_at
        )
        
        # TODO: Send invitation email
        
        # Track analytics
        AnalyticsCollector.track_event(
            'organization_member_invited',
            user=request.user,
            event_data={
                'organization_id': str(organization.id),
                'invited_email': email,
                'role': role
            }
        )
        
        return Response({
            'message': 'Invitation sent successfully',
            'invitation_id': invitation.id,
            'expires_at': invitation.expires_at
        })
        
    except Organization.DoesNotExist:
        return Response({
            'error': 'Organization not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except OrganizationMembership.DoesNotExist:
        return Response({
            'error': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        logger.error(f"Error inviting member: {e}")
        return Response({
            'error': 'Failed to invite member',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_organization_members(request, org_id):
    """List organization members"""
    try:
        organization = Organization.objects.get(id=org_id)
        
        # Check membership
        OrganizationMembership.objects.get(
            organization=organization,
            user=request.user,
            status='active'
        )
        
        members = OrganizationMembership.objects.filter(
            organization=organization,
            status='active'
        ).select_related('user')
        
        members_data = [
            {
                'user_id': member.user.id,
                'username': member.user.username,
                'email': member.user.email,
                'first_name': member.user.first_name,
                'last_name': member.user.last_name,
                'role': member.role,
                'joined_at': member.joined_at,
                'permissions': member.get_permissions(),
                'is_owner': organization.owner == member.user
            }
            for member in members
        ]
        
        return Response({
            'members': members_data,
            'total_count': len(members_data)
        })
        
    except Organization.DoesNotExist:
        return Response({
            'error': 'Organization not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except OrganizationMembership.DoesNotExist:
        return Response({
            'error': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        logger.error(f"Error listing organization members: {e}")
        return Response({
            'error': 'Failed to list members',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_team(request, org_id):
    """Create a new team within organization"""
    try:
        organization = Organization.objects.get(id=org_id)
        
        # Check permissions
        membership = OrganizationMembership.objects.get(
            organization=organization,
            user=request.user,
            status='active'
        )
        
        permissions = membership.get_permissions()
        if not permissions.get('manage_projects', False):
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data
        
        team = Team.objects.create(
            organization=organization,
            name=data.get('name'),
            description=data.get('description', ''),
            is_private=data.get('is_private', False),
            auto_join=data.get('auto_join', False),
            created_by=request.user
        )
        
        # Add creator as team lead
        TeamMembership.objects.create(
            team=team,
            user=request.user,
            role='lead',
            added_by=request.user
        )
        
        # Add initial members
        member_ids = data.get('member_ids', [])
        for member_id in member_ids:
            try:
                user = User.objects.get(id=member_id)
                # Verify user is organization member
                OrganizationMembership.objects.get(
                    organization=organization,
                    user=user,
                    status='active'
                )
                
                TeamMembership.objects.create(
                    team=team,
                    user=user,
                    role='member',
                    added_by=request.user
                )
            except (User.DoesNotExist, OrganizationMembership.DoesNotExist):
                continue
        
        # Track analytics
        AnalyticsCollector.track_event(
            'team_created',
            user=request.user,
            event_data={
                'organization_id': str(organization.id),
                'team_id': team.id,
                'initial_member_count': len(member_ids) + 1
            }
        )
        
        return Response({
            'team_id': team.id,
            'name': team.name,
            'member_count': team.members.count(),
            'created_at': team.created_at
        })
        
    except Organization.DoesNotExist:
        return Response({
            'error': 'Organization not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except OrganizationMembership.DoesNotExist:
        return Response({
            'error': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        logger.error(f"Error creating team: {e}")
        return Response({
            'error': 'Failed to create team',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_organization_project(request, org_id):
    """Create a new project within organization"""
    try:
        organization = Organization.objects.get(id=org_id)
        
        # Check permissions
        membership = OrganizationMembership.objects.get(
            organization=organization,
            user=request.user,
            status='active'
        )
        
        permissions = membership.get_permissions()
        if not permissions.get('manage_projects', False):
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check organization limits
        if not check_organization_limits(organization, 'create_project'):
            return Response({
                'error': 'Organization project limit reached'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data
        
        project = OrganizationProject.objects.create(
            organization=organization,
            name=data.get('name'),
            description=data.get('description', ''),
            status=data.get('status', 'planning'),
            priority=data.get('priority', 'medium'),
            start_date=data.get('start_date'),
            due_date=data.get('due_date'),
            budget=data.get('budget'),
            estimated_hours=data.get('estimated_hours'),
            created_by=request.user,
            project_manager=request.user,
            tags=data.get('tags', [])
        )
        
        # Assign team if specified
        team_id = data.get('team_id')
        if team_id:
            try:
                team = Team.objects.get(id=team_id, organization=organization)
                project.assigned_team = team
                project.save()
            except Team.DoesNotExist:
                pass
        
        # Assign members
        member_ids = data.get('assigned_member_ids', [])
        for member_id in member_ids:
            try:
                user = User.objects.get(id=member_id)
                # Verify user is organization member
                OrganizationMembership.objects.get(
                    organization=organization,
                    user=user,
                    status='active'
                )
                project.assigned_members.add(user)
            except (User.DoesNotExist, OrganizationMembership.DoesNotExist):
                continue
        
        # Track analytics
        AnalyticsCollector.track_event(
            'organization_project_created',
            user=request.user,
            event_data={
                'organization_id': str(organization.id),
                'project_id': str(project.id),
                'project_priority': project.priority,
                'assigned_member_count': project.assigned_members.count()
            }
        )
        
        return Response({
            'project_id': str(project.id),
            'name': project.name,
            'status': project.status,
            'priority': project.priority,
            'assigned_member_count': project.assigned_members.count(),
            'created_at': project.created_at
        })
        
    except Organization.DoesNotExist:
        return Response({
            'error': 'Organization not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except OrganizationMembership.DoesNotExist:
        return Response({
            'error': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        logger.error(f"Error creating organization project: {e}")
        return Response({
            'error': 'Failed to create project',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organization_analytics(request, org_id):
    """Get organization analytics and insights"""
    try:
        organization = Organization.objects.get(id=org_id)
        
        # Check permissions
        membership = OrganizationMembership.objects.get(
            organization=organization,
            user=request.user,
            status='active'
        )
        
        permissions = membership.get_permissions()
        if not permissions.get('view_analytics', False):
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Calculate analytics
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)
        
        # Member analytics
        total_members = organization.memberships.filter(status='active').count()
        new_members_30d = organization.memberships.filter(
            joined_at__gte=last_30_days
        ).count()
        
        # Project analytics
        total_projects = organization.projects.count()
        active_projects = organization.projects.filter(status='active').count()
        completed_projects = organization.projects.filter(status='completed').count()
        overdue_projects = organization.projects.filter(
            due_date__lt=now.date(),
            status__in=['planning', 'active']
        ).count()
        
        # Team analytics
        total_teams = organization.teams.count()
        
        # Activity analytics
        recent_activity = {
            'projects_created_7d': organization.projects.filter(
                created_at__gte=last_7_days
            ).count(),
            'members_joined_7d': organization.memberships.filter(
                joined_at__gte=last_7_days
            ).count(),
            'teams_created_7d': organization.teams.filter(
                created_at__gte=last_7_days
            ).count()
        }
        
        return Response({
            'organization_id': str(organization.id),
            'analytics': {
                'members': {
                    'total': total_members,
                    'new_30d': new_members_30d,
                    'utilization': min(100, (total_members / organization.max_members) * 100)
                },
                'projects': {
                    'total': total_projects,
                    'active': active_projects,
                    'completed': completed_projects,
                    'overdue': overdue_projects,
                    'completion_rate': (completed_projects / max(total_projects, 1)) * 100
                },
                'teams': {
                    'total': total_teams,
                    'avg_team_size': total_members / max(total_teams, 1)
                },
                'activity': recent_activity,
                'subscription': {
                    'tier': organization.subscription_tier,
                    'status': organization.subscription_status,
                    'member_limit_usage': (total_members / organization.max_members) * 100,
                    'project_limit_usage': (total_projects / organization.max_projects) * 100
                }
            },
            'generated_at': now
        })
        
    except Organization.DoesNotExist:
        return Response({
            'error': 'Organization not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except OrganizationMembership.DoesNotExist:
        return Response({
            'error': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        logger.error(f"Error getting organization analytics: {e}")
        return Response({
            'error': 'Failed to get analytics',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def enterprise_health_check(request):
    """Health check for enterprise management service"""
    try:
        # Check database connectivity
        org_count = Organization.objects.count()
        member_count = OrganizationMembership.objects.filter(status='active').count()
        
        return Response({
            'status': 'healthy',
            'database_connected': True,
            'total_organizations': org_count,
            'total_active_members': member_count,
            'enterprise_service': 'operational',
            'timestamp': timezone.now()
        })
        
    except Exception as e:
        logger.error(f"Enterprise health check failed: {e}")
        return Response({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
