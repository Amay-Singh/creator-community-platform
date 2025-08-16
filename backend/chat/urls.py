from django.urls import path
from . import views

urlpatterns = [
    # Chat management
    path('', views.ChatListView.as_view(), name='chat-list'),
    path('<int:chat_id>/messages/', views.MessageListView.as_view(), name='message-list'),
    path('<int:chat_id>/messages/', views.SendMessageView.as_view(), name='send-message'),
    path('messages/<int:message_id>/translate/', views.TranslateMessageView.as_view(), name='translate-message'),
    
    # Meeting invites
    path('meetings/', views.MeetingInviteView.as_view(), name='meeting-invite'),
    path('meetings/<int:invite_id>/respond/', views.MeetingResponseView.as_view(), name='meeting-response'),
]
