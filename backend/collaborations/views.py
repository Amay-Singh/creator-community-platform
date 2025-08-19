"""
Collaboration views for project management (REQ-7, REQ-8)
"""
from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Collaboration, CollaborationInvite
from .serializers import CollaborationSerializer, CollaborationInviteSerializer

class CollaborationListView(generics.ListCreateAPIView):
    """List and create collaborations"""
    serializer_class = CollaborationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Collaboration.objects.filter(participants=self.request.user.profile)

class CollaborationInviteView(generics.ListCreateAPIView):
    """Handle collaboration invites"""
    serializer_class = CollaborationInviteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CollaborationInvite.objects.filter(recipient=self.request.user.profile)
