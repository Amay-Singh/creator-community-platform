"""
URL patterns for collaborations app
"""
from django.urls import path
from . import views
from .enhanced_views import (
    CollaborationInviteListView, CollaborationInviteDetailView,
    CollaborationInviteCreateView, collaboration_suggestions
)
from .collaboration_tools_views import (
    create_whiteboard_session, get_whiteboard_data, update_whiteboard_canvas,
    upload_collaboration_file, get_collaboration_files, delete_collaboration_file,
    create_collaboration_folder, get_collaboration_overview
)

app_name = 'collaborations'

urlpatterns = [
    # Enhanced collaboration invites with AI match explanations (REQ-8)
    path('invites/', CollaborationInviteListView.as_view(), name='invite_list'),
    path('invites/<uuid:pk>/', CollaborationInviteDetailView.as_view(), name='invite_detail'),
    path('invites/create/', CollaborationInviteCreateView.as_view(), name='invite_create'),
    path('suggestions/', collaboration_suggestions, name='collaboration_suggestions'),
    
    # Collaboration Tools (REQ-12)
    path('<uuid:collaboration_id>/overview/', get_collaboration_overview, name='collaboration_overview'),
    
    # Whiteboard functionality
    path('<uuid:collaboration_id>/whiteboard/create/', create_whiteboard_session, name='create_whiteboard'),
    path('whiteboard/<uuid:session_id>/', get_whiteboard_data, name='get_whiteboard'),
    path('whiteboard/<uuid:session_id>/update/', update_whiteboard_canvas, name='update_whiteboard'),
    
    # File sharing functionality
    path('<uuid:collaboration_id>/files/', get_collaboration_files, name='collaboration_files'),
    path('<uuid:collaboration_id>/files/upload/', upload_collaboration_file, name='upload_file'),
    path('<uuid:collaboration_id>/files/<uuid:file_id>/delete/', delete_collaboration_file, name='delete_file'),
    path('<uuid:collaboration_id>/folders/create/', create_collaboration_folder, name='create_folder'),
    
    # Legacy endpoints
    path('legacy/invites/', views.CollaborationInviteListView.as_view(), name='legacy_invite_list'),
    path('legacy/invites/<uuid:pk>/', views.CollaborationInviteDetailView.as_view(), name='legacy_invite_detail'),
    path('legacy/invites/create/', views.CollaborationInviteCreateView.as_view(), name='legacy_invite_create'),
    
    # Original endpoints for backward compatibility
    path('', views.CollaborationInviteListView.as_view(), name='list'),
    path('<uuid:pk>/', views.CollaborationInviteDetailView.as_view(), name='detail'),
    path('create/', views.CollaborationInviteCreateView.as_view(), name='create'),
]
