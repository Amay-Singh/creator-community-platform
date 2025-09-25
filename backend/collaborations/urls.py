"""
URL patterns for collaborations app
Includes P5-003 Collaboration Invitation System endpoints
P5-005 Project Management Tools endpoints
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.http import JsonResponse
from . import views
from . import invitation_api

def projects_list(request):
    """List projects endpoint"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    return JsonResponse({
        'projects': [],
        'count': 0,
        'message': 'Projects endpoint operational'
    })

# P5-005 Project Management Router
router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'tasks', views.TaskViewSet, basename='task')
router.register(r'task-comments', views.TaskCommentViewSet, basename='taskcomment')
router.register(r'project-files', views.ProjectFileViewSet, basename='projectfile')
router.register(r'milestones', views.ProjectMilestoneViewSet, basename='milestone')
# from .enhanced_views import (
#     CollaborationInviteListView, CollaborationInviteDetailView,
#     CollaborationInviteCreateView, collaboration_suggestions
# )
# from .collaboration_tools_views import (
#     create_whiteboard_session, get_whiteboard_data, update_whiteboard_canvas,
#     upload_collaboration_file, get_collaboration_files, delete_collaboration_file,
#     create_collaboration_folder, get_collaboration_overview
# )

app_name = 'collaborations'

urlpatterns = [
    # P5-005 Project Management API
    path('api/', include(router.urls)),
    path('projects/', projects_list, name='projects_list'),  # Simple projects endpoint
    
    # Basic collaboration endpoints
    path('', views.CollaborationListView.as_view(), name='collaboration_list'),
    path('invites/', views.CollaborationInviteView.as_view(), name='collaboration_invites'),
    
    # P5-003 New Collaboration Invitation System
    path('invites/send/', invitation_api.send_invite, name='send_invite'),
    path('invites/sent/', invitation_api.list_sent_invites, name='list_sent_invites'),
    path('invites/received/', invitation_api.list_received_invites, name='list_received_invites'),
    path('invites/stats/', invitation_api.get_invite_stats, name='get_invite_stats'),
    path('invites/<uuid:invite_id>/detail/', invitation_api.get_invite_detail, name='get_invite_detail'),
    path('invites/<uuid:invite_id>/accept/', invitation_api.accept_invite, name='accept_invite'),
    path('invites/<uuid:invite_id>/decline/', invitation_api.decline_invite, name='decline_invite'),
    path('invites/<uuid:invite_id>/counter/', invitation_api.counter_offer_invite, name='counter_offer_invite'),
    path('invites/<uuid:invite_id>/cancel/', invitation_api.cancel_invite, name='cancel_invite'),
    path('invites/health/', invitation_api.simple_invite_health, name='simple_invite_health'),
    
    # Invite Templates
    path('invites/templates/', invitation_api.invite_templates, name='invite_templates'),
    path('invites/templates/<uuid:template_id>/', invitation_api.invite_template_detail, name='invite_template_detail'),
    path('invites/templates/<uuid:template_id>/use/', invitation_api.use_template, name='use_template'),
    
    # Enhanced collaboration invites with AI match explanations (REQ-8) - Temporarily disabled
    # path('invites/list/', CollaborationInviteListView.as_view(), name='invite_list'),
    # path('invites/<uuid:pk>/', CollaborationInviteDetailView.as_view(), name='invite_detail'),
    # path('invites/create/', CollaborationInviteCreateView.as_view(), name='invite_create'),
    # path('suggestions/', collaboration_suggestions, name='collaboration_suggestions'),
    
    # Collaboration Tools (REQ-12) - Temporarily disabled
    # path('<uuid:collaboration_id>/overview/', get_collaboration_overview, name='collaboration_overview'),
    
    # Whiteboard functionality - Temporarily disabled
    # path('<uuid:collaboration_id>/whiteboard/create/', create_whiteboard_session, name='create_whiteboard'),
    # path('whiteboard/<uuid:session_id>/', get_whiteboard_data, name='get_whiteboard'),
    # path('whiteboard/<uuid:session_id>/update/', update_whiteboard_canvas, name='update_whiteboard'),
    
    # File sharing functionality - Temporarily disabled
    # path('<uuid:collaboration_id>/files/', get_collaboration_files, name='collaboration_files'),
    # path('<uuid:collaboration_id>/files/upload/', upload_collaboration_file, name='upload_file'),
    # path('<uuid:collaboration_id>/files/<uuid:file_id>/delete/', delete_collaboration_file, name='delete_file'),
    # path('<uuid:collaboration_id>/folders/create/', create_collaboration_folder, name='create_folder'),
]
