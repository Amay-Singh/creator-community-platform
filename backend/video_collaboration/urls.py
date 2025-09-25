"""
URL patterns for video collaboration app
P9-003: Advanced Video Collaboration Tools
"""
from django.urls import path
from . import views

app_name = 'video_collaboration'

urlpatterns = [
    # Room management
    path('rooms/create/', views.create_video_room, name='create_video_room'),
    path('rooms/<uuid:room_id>/', views.get_video_room, name='get_video_room'),
    path('rooms/<uuid:room_id>/join/', views.join_video_room, name='join_video_room'),
    path('rooms/<uuid:room_id>/leave/', views.leave_video_room, name='leave_video_room'),
    path('rooms/<uuid:room_id>/settings/', views.update_room_settings, name='update_room_settings'),
    path('rooms/', views.list_user_rooms, name='list_user_rooms'),
    
    # Recordings
    path('rooms/<uuid:room_id>/recordings/', views.get_room_recordings, name='get_room_recordings'),
    
    # Chat messages
    path('rooms/<uuid:room_id>/messages/', views.get_room_messages, name='get_room_messages'),
    
    # Analytics
    path('analytics/', views.get_video_analytics, name='get_video_analytics'),
    
    # Health check
    path('health/', views.simple_video_health, name='simple_video_health'),
]
