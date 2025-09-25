"""
Enterprise Team Management Models
P9-004: Enterprise Team Management
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class Organization(models.Model):
    """Multi-tenant organization model"""
    
    ORGANIZATION_TYPES = [
        ('startup', 'Startup'),
        ('agency', 'Creative Agency'),
        ('enterprise', 'Enterprise'),
        ('nonprofit', 'Non-Profit'),
        ('freelancer', 'Freelancer Collective'),
    ]
    
    SUBSCRIPTION_TIERS = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    organization_type = models.CharField(max_length=20, choices=ORGANIZATION_TYPES, default='startup')
    
    # Contact information
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Address
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Subscription and billing
    subscription_tier = models.CharField(max_length=20, choices=SUBSCRIPTION_TIERS, default='free')
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    subscription_status = models.CharField(max_length=20, default='active')
    subscription_start_date = models.DateTimeField(null=True, blank=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    
    # Limits and quotas
    max_members = models.IntegerField(default=5)
    max_projects = models.IntegerField(default=10)
    max_storage_gb = models.IntegerField(default=5)
    max_video_hours = models.IntegerField(default=10)
    
    # Settings
    is_active = models.BooleanField(default=True)
    allow_public_signup = models.BooleanField(default=False)
    require_email_verification = models.BooleanField(default=True)
    enable_sso = models.BooleanField(default=False)
    
    # Branding (white-labeling)
    logo_url = models.URLField(blank=True)
    primary_color = models.CharField(max_length=7, default='#007bff')  # Hex color
    secondary_color = models.CharField(max_length=7, default='#6c757d')
    custom_domain = models.CharField(max_length=200, blank=True)
    
    # Ownership
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_organizations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'organizations'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def member_count(self):
        return self.memberships.filter(status='active').count()
    
    @property
    def is_over_member_limit(self):
        return self.member_count > self.max_members


class OrganizationMembership(models.Model):
    """Organization membership with roles and permissions"""
    
    MEMBERSHIP_ROLES = [
        ('owner', 'Owner'),
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('member', 'Member'),
        ('guest', 'Guest'),
    ]
    
    MEMBERSHIP_STATUS = [
        ('invited', 'Invited'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('left', 'Left'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organization_memberships')
    role = models.CharField(max_length=20, choices=MEMBERSHIP_ROLES, default='member')
    status = models.CharField(max_length=20, choices=MEMBERSHIP_STATUS, default='invited')
    
    # Invitation details
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_invitations')
    invited_at = models.DateTimeField(auto_now_add=True)
    invitation_token = models.CharField(max_length=100, blank=True)
    
    # Membership timeline
    joined_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)
    
    # Custom permissions (override role defaults)
    custom_permissions = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'organization_memberships'
        unique_together = ['organization', 'user']
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.organization.name} ({self.role})"
    
    def get_permissions(self):
        """Get effective permissions for this membership"""
        # Base permissions by role
        role_permissions = {
            'owner': {
                'manage_organization': True,
                'manage_members': True,
                'manage_billing': True,
                'manage_projects': True,
                'view_analytics': True,
                'manage_integrations': True,
                'manage_branding': True,
            },
            'admin': {
                'manage_organization': False,
                'manage_members': True,
                'manage_billing': False,
                'manage_projects': True,
                'view_analytics': True,
                'manage_integrations': True,
                'manage_branding': False,
            },
            'manager': {
                'manage_organization': False,
                'manage_members': False,
                'manage_billing': False,
                'manage_projects': True,
                'view_analytics': True,
                'manage_integrations': False,
                'manage_branding': False,
            },
            'member': {
                'manage_organization': False,
                'manage_members': False,
                'manage_billing': False,
                'manage_projects': False,
                'view_analytics': False,
                'manage_integrations': False,
                'manage_branding': False,
            },
            'guest': {
                'manage_organization': False,
                'manage_members': False,
                'manage_billing': False,
                'manage_projects': False,
                'view_analytics': False,
                'manage_integrations': False,
                'manage_branding': False,
            }
        }
        
        # Get base permissions for role
        permissions = role_permissions.get(self.role, {})
        
        # Apply custom permission overrides
        permissions.update(self.custom_permissions)
        
        return permissions


class Team(models.Model):
    """Teams within organizations"""
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Team settings
    is_private = models.BooleanField(default=False)
    auto_join = models.BooleanField(default=False)  # Auto-join new org members
    
    # Team lead
    lead = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='led_teams')
    members = models.ManyToManyField(User, through='TeamMembership', related_name='teams')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_teams')
    
    class Meta:
        db_table = 'teams'
        unique_together = ['organization', 'name']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class TeamMembership(models.Model):
    """Team membership within organizations"""
    
    TEAM_ROLES = [
        ('lead', 'Team Lead'),
        ('member', 'Team Member'),
    ]
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    role = models.CharField(max_length=20, choices=TEAM_ROLES, default='member')
    
    joined_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='added_team_members')
    
    class Meta:
        db_table = 'team_memberships'
        unique_together = ['team', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.team.name} ({self.role})"


class OrganizationProject(models.Model):
    """Projects within organizations"""
    
    PROJECT_STATUS = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PROJECT_PRIORITY = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Project details
    status = models.CharField(max_length=20, choices=PROJECT_STATUS, default='planning')
    priority = models.CharField(max_length=20, choices=PROJECT_PRIORITY, default='medium')
    
    # Timeline
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    
    # Assignment
    assigned_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_projects')
    assigned_members = models.ManyToManyField(User, blank=True, related_name='assigned_projects')
    project_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_projects')
    
    # Budget and resources
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_hours = models.IntegerField(null=True, blank=True)
    actual_hours = models.IntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_org_projects')
    
    # Tags and categories
    tags = models.JSONField(default=list, blank=True)
    
    class Meta:
        db_table = 'organization_projects'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"
    
    @property
    def is_overdue(self):
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return timezone.now().date() > self.due_date
        return False
    
    @property
    def progress_percentage(self):
        if self.estimated_hours and self.actual_hours:
            return min(100, (self.actual_hours / self.estimated_hours) * 100)
        return 0


class OrganizationInvitation(models.Model):
    """Invitations to join organizations"""
    
    INVITATION_STATUS = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=OrganizationMembership.MEMBERSHIP_ROLES, default='member')
    status = models.CharField(max_length=20, choices=INVITATION_STATUS, default='pending')
    
    # Invitation details
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_org_invitations')
    invitation_token = models.CharField(max_length=100, unique=True)
    message = models.TextField(blank=True)
    
    # Timeline
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    responded_at = models.DateTimeField(null=True, blank=True)
    
    # Accepted invitation details
    accepted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='accepted_org_invitations')
    
    class Meta:
        db_table = 'organization_invitations'
        unique_together = ['organization', 'email']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invitation to {self.email} for {self.organization.name}"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at and self.status == 'pending'


class OrganizationSettings(models.Model):
    """Organization-specific settings and configurations"""
    
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='settings')
    
    # Feature toggles
    enable_time_tracking = models.BooleanField(default=True)
    enable_project_management = models.BooleanField(default=True)
    enable_video_collaboration = models.BooleanField(default=True)
    enable_ai_features = models.BooleanField(default=True)
    enable_integrations = models.BooleanField(default=True)
    
    # Notification settings
    email_notifications = models.BooleanField(default=True)
    slack_notifications = models.BooleanField(default=False)
    slack_webhook_url = models.URLField(blank=True)
    
    # Security settings
    require_2fa = models.BooleanField(default=False)
    session_timeout_minutes = models.IntegerField(default=480)  # 8 hours
    allowed_domains = models.JSONField(default=list, blank=True)  # Email domain restrictions
    
    # Workflow settings
    default_project_template = models.CharField(max_length=100, blank=True)
    auto_assign_new_members = models.BooleanField(default=False)
    require_project_approval = models.BooleanField(default=False)
    
    # Integration settings
    google_workspace_domain = models.CharField(max_length=200, blank=True)
    microsoft_tenant_id = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'organization_settings'
    
    def __str__(self):
        return f"Settings for {self.organization.name}"
