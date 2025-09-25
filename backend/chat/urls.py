"""
URL patterns for chat app - P5-004 Real-time Messaging
"""
from django.urls import path
from django.http import JsonResponse
from . import views

def chat_health(request):
    """Chat service health check"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'chat',
        'endpoints': {
            'conversations': '/api/chat/conversations/',
            'rooms': '/api/chat/rooms/',
            'presence': '/api/chat/presence/'
        }
    })

def conversations_list(request):
    """List conversations endpoint"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    return JsonResponse({
        'conversations': [],
        'count': 0,
        'message': 'Chat conversations endpoint operational'
    })

app_name = 'chat'

urlpatterns = [
    # Health and basic endpoints
    path('health/', chat_health, name='chat_health'),
    path('conversations/', conversations_list, name='conversations_list'),
    
    # Real-time Chat API Endpoints
    path('rooms/', views.ChatRoomListView.as_view(), name='room_list'),
    path('rooms/<uuid:room_id>/', views.room_detail, name='room_detail'),
    path('rooms/<uuid:room_id>/messages/', views.MessageListView.as_view(), name='room_messages'),
    path('rooms/<uuid:room_id>/read/', views.mark_messages_read, name='mark_messages_read'),
    path('rooms/<uuid:room_id>/typing/', views.typing_status, name='typing_status'),
    path('rooms/<uuid:room_id>/upload/', views.upload_file, name='upload_file'),
    
    # User presence
    path('presence/', views.user_presence, name='user_presence'),
]
