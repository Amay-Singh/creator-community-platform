"""
Enterprise Permission System
P9-004: Enterprise Team Management - Role-Based Access Control
"""
from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model
from .models import Organization, OrganizationMembership, Team, TeamMembership

User = get_user_model()


class OrganizationPermission(BasePermission):
    """Base permission class for organization-level permissions"""
    
    def has_permission(self, request, view):
        """Check if user has basic organization access"""
        if not request.user.is_authenticated:
            return False
        
        # Get organization from view kwargs or request data
        org_id = view.kwargs.get('org_id') or request.data.get('organization_id')
        if not org_id:
            return True  # Let view handle missing org_id
        
        try:
            organization = Organization.objects.get(id=org_id)
            membership = OrganizationMembership.objects.get(
                organization=organization,
                user=request.user,
                status='active'
            )
            return True
        except (Organization.DoesNotExist, OrganizationMembership.DoesNotExist):
            return False
    
    def has_object_permission(self, request, view, obj):
        """Check object-level permissions"""
        if hasattr(obj, 'organization'):
            organization = obj.organization
        elif isinstance(obj, Organization):
            organization = obj
        else:
            return False
        
        try:
            membership = OrganizationMembership.objects.get(
                organization=organization,
                user=request.user,
                status='active'
            )
            return self.check_permission(request, membership, obj)
        except OrganizationMembership.DoesNotExist:
            return False
    
    def check_permission(self, request, membership, obj):
        """Override in subclasses to implement specific permission logic"""
        return True


class CanManageOrganization(OrganizationPermission):
    """Permission to manage organization settings"""
    
    def check_permission(self, request, membership, obj):
        permissions = membership.get_permissions()
        return permissions.get('manage_organization', False)


class CanManageMembers(OrganizationPermission):
    """Permission to manage organization members"""
    
    def check_permission(self, request, membership, obj):
        permissions = membership.get_permissions()
        return permissions.get('manage_members', False)


class CanManageBilling(OrganizationPermission):
    """Permission to manage billing and subscriptions"""
    
    def check_permission(self, request, membership, obj):
        permissions = membership.get_permissions()
        return permissions.get('manage_billing', False)


class CanManageProjects(OrganizationPermission):
    """Permission to manage projects"""
    
    def check_permission(self, request, membership, obj):
        permissions = membership.get_permissions()
        
        # Project managers can manage their own projects
        if hasattr(obj, 'project_manager') and obj.project_manager == request.user:
            return True
        
        # Team leads can manage team projects
        if hasattr(obj, 'assigned_team') and obj.assigned_team:
            try:
                team_membership = TeamMembership.objects.get(
                    team=obj.assigned_team,
                    user=request.user,
                    role='lead'
                )
                return True
            except TeamMembership.DoesNotExist:
                pass
        
        return permissions.get('manage_projects', False)


class CanViewAnalytics(OrganizationPermission):
    """Permission to view organization analytics"""
    
    def check_permission(self, request, membership, obj):
        permissions = membership.get_permissions()
        return permissions.get('view_analytics', False)


class CanManageIntegrations(OrganizationPermission):
    """Permission to manage integrations"""
    
    def check_permission(self, request, membership, obj):
        permissions = membership.get_permissions()
        return permissions.get('manage_integrations', False)


class CanManageBranding(OrganizationPermission):
    """Permission to manage branding and white-labeling"""
    
    def check_permission(self, request, membership, obj):
        permissions = membership.get_permissions()
        return permissions.get('manage_branding', False)


class TeamPermission(BasePermission):
    """Base permission class for team-level permissions"""
    
    def has_permission(self, request, view):
        """Check if user has team access"""
        if not request.user.is_authenticated:
            return False
        
        team_id = view.kwargs.get('team_id')
        if not team_id:
            return True
        
        try:
            team = Team.objects.get(id=team_id)
            
            # Check organization membership first
            org_membership = OrganizationMembership.objects.get(
                organization=team.organization,
                user=request.user,
                status='active'
            )
            
            # Check team membership or organization permissions
            try:
                team_membership = TeamMembership.objects.get(
                    team=team,
                    user=request.user
                )
                return True
            except TeamMembership.DoesNotExist:
                # Allow if user has organization-level project management permissions
                permissions = org_membership.get_permissions()
                return permissions.get('manage_projects', False)
                
        except (Team.DoesNotExist, OrganizationMembership.DoesNotExist):
            return False
    
    def has_object_permission(self, request, view, obj):
        """Check object-level team permissions"""
        if isinstance(obj, Team):
            team = obj
        elif hasattr(obj, 'team'):
            team = obj.team
        else:
            return False
        
        try:
            # Check organization membership
            org_membership = OrganizationMembership.objects.get(
                organization=team.organization,
                user=request.user,
                status='active'
            )
            
            # Check team membership
            try:
                team_membership = TeamMembership.objects.get(
                    team=team,
                    user=request.user
                )
                return self.check_team_permission(request, team_membership, obj)
            except TeamMembership.DoesNotExist:
                # Check organization permissions
                permissions = org_membership.get_permissions()
                return permissions.get('manage_projects', False)
                
        except OrganizationMembership.DoesNotExist:
            return False
    
    def check_team_permission(self, request, team_membership, obj):
        """Override in subclasses for specific team permission logic"""
        return True


class CanManageTeam(TeamPermission):
    """Permission to manage team settings and members"""
    
    def check_team_permission(self, request, team_membership, obj):
        # Team leads can manage their teams
        if team_membership.role == 'lead':
            return True
        
        # Check organization-level permissions
        org_membership = OrganizationMembership.objects.get(
            organization=team_membership.team.organization,
            user=request.user,
            status='active'
        )
        permissions = org_membership.get_permissions()
        return permissions.get('manage_members', False)


class IsProjectAssigned(BasePermission):
    """Permission for users assigned to a project"""
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Project manager has full access
        if hasattr(obj, 'project_manager') and obj.project_manager == request.user:
            return True
        
        # Assigned members have access
        if hasattr(obj, 'assigned_members') and obj.assigned_members.filter(id=request.user.id).exists():
            return True
        
        # Team members have access if project is assigned to their team
        if hasattr(obj, 'assigned_team') and obj.assigned_team:
            try:
                TeamMembership.objects.get(
                    team=obj.assigned_team,
                    user=request.user
                )
                return True
            except TeamMembership.DoesNotExist:
                pass
        
        return False


def check_organization_limits(organization, action_type):
    """Check if organization is within limits for various actions"""
    
    limits_check = {
        'add_member': organization.member_count < organization.max_members,
        'create_project': organization.projects.count() < organization.max_projects,
        'video_session': True,  # Would check video hours usage
        'storage_usage': True,  # Would check storage usage
    }
    
    return limits_check.get(action_type, True)


def get_user_organizations(user):
    """Get all organizations user has access to"""
    if not user.is_authenticated:
        return Organization.objects.none()
    
    return Organization.objects.filter(
        memberships__user=user,
        memberships__status='active'
    ).distinct()


def get_user_organization_role(user, organization):
    """Get user's role in an organization"""
    try:
        membership = OrganizationMembership.objects.get(
            organization=organization,
            user=user,
            status='active'
        )
        return membership.role
    except OrganizationMembership.DoesNotExist:
        return None


def get_user_permissions_in_organization(user, organization):
    """Get user's effective permissions in an organization"""
    try:
        membership = OrganizationMembership.objects.get(
            organization=organization,
            user=user,
            status='active'
        )
        return membership.get_permissions()
    except OrganizationMembership.DoesNotExist:
        return {}


class RoleBasedAccessMixin:
    """Mixin to add role-based access control to views"""
    
    required_permission = None
    organization_field = 'organization'
    
    def check_permissions(self, request):
        """Check permissions including role-based access"""
        super().check_permissions(request)
        
        if self.required_permission and hasattr(self, 'get_object'):
            obj = self.get_object()
            organization = getattr(obj, self.organization_field, None)
            
            if organization:
                permissions = get_user_permissions_in_organization(request.user, organization)
                if not permissions.get(self.required_permission, False):
                    self.permission_denied(
                        request,
                        message=f"You don't have permission to {self.required_permission}"
                    )
    
    def get_queryset(self):
        """Filter queryset based on user's organization access"""
        queryset = super().get_queryset()
        
        if not self.request.user.is_authenticated:
            return queryset.none()
        
        # Filter by organizations user has access to
        user_orgs = get_user_organizations(self.request.user)
        
        if hasattr(queryset.model, 'organization'):
            return queryset.filter(organization__in=user_orgs)
        
        return queryset
