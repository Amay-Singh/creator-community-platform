"""
WebSocket routing for video collaboration
P9-003: Advanced Video Collaboration Tools
"""
from django.urls import re_path
from . import webrtc_service

websocket_urlpatterns = [
    re_path(r'ws/video/(?P<room_id>[0-9a-f-]+)/$', webrtc_service.VideoRoomConsumer.as_asgi()),
]
