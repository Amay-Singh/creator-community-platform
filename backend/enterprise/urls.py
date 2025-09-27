"""
URL patterns for enterprise app
P9-004: Enterprise Team Management
"""
from django.urls import path
from . import views

app_name = 'enterprise'

urlpatterns = [
    # Organization management
    path('organizations/create/', views.create_organization, name='create_organization'),
    path('organizations/', views.list_user_organizations, name='list_user_organizations'),
    path('organizations/<uuid:org_id>/', views.get_organization_details, name='get_organization_details'),
    path('organizations/<uuid:org_id>/analytics/', views.get_organization_analytics, name='get_organization_analytics'),
    
    # Member management
    path('organizations/<uuid:org_id>/invite/', views.invite_member, name='invite_member'),
    path('organizations/<uuid:org_id>/members/', views.list_organization_members, name='list_organization_members'),
    
    # Team management
    path('organizations/<uuid:org_id>/teams/create/', views.create_team, name='create_team'),
    
    # Project management
    path('organizations/<uuid:org_id>/projects/create/', views.create_organization_project, name='create_organization_project'),
    
    # Health check
    path('health/', views.enterprise_health_check, name='enterprise_health_check'),
]
