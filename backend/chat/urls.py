"""
URL patterns for chat app - P5-004 Real-time Messaging
"""
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
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
