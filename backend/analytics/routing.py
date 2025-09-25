"""
WebSocket routing for analytics
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/analytics/$', consumers.AnalyticsConsumer.as_asgi()),
    re_path(r'ws/analytics/live/$', consumers.LiveMetricsConsumer.as_asgi()),
]
