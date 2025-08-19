"""
URL patterns for chat app
"""
from django.urls import path
from . import views
from .enhanced_views import (
    ChatRoomListView, ChatRoomDetailView, MessageListCreateView,
    MeetingInviteListCreateView, MeetingInviteDetailView,
    translate_message, batch_translate_messages, respond_to_meeting,
    get_translation_suggestions, add_participants_to_room
)

app_name = 'chat'

urlpatterns = [
    # Enhanced Chat Rooms (REQ-9)
    path('rooms/', ChatRoomListView.as_view(), name='room_list'),
    path('rooms/<uuid:pk>/', ChatRoomDetailView.as_view(), name='room_detail'),
    path('rooms/<uuid:room_id>/messages/', MessageListCreateView.as_view(), name='room_messages'),
    path('rooms/<uuid:room_id>/participants/', add_participants_to_room, name='add_participants'),
    
    # Real-time Translation (REQ-11)
    path('messages/<uuid:message_id>/translate/', translate_message, name='translate_message'),
    path('messages/<uuid:message_id>/translation-suggestions/', get_translation_suggestions, name='translation_suggestions'),
    path('rooms/<uuid:room_id>/translate-batch/', batch_translate_messages, name='batch_translate'),
    
    # Meeting Invites (REQ-10)
    path('meetings/', MeetingInviteListCreateView.as_view(), name='meeting_list'),
    path('meetings/<uuid:pk>/', MeetingInviteDetailView.as_view(), name='meeting_detail'),
    path('meetings/<uuid:meeting_id>/respond/', respond_to_meeting, name='respond_meeting'),
    
    # Legacy endpoints
    path('legacy/rooms/', views.ChatRoomListView.as_view(), name='legacy_room_list'),
    path('legacy/rooms/<uuid:pk>/', views.ChatRoomDetailView.as_view(), name='legacy_room_detail'),
    path('legacy/messages/', views.MessageListView.as_view(), name='legacy_message_list'),
]
