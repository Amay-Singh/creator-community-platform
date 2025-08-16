from django.urls import path
from . import views

urlpatterns = [
    # Collaboration invites
    path('invites/', views.CollaborationInviteListView.as_view(), name='collaboration-invites'),
    path('invites/', views.SendCollaborationInviteView.as_view(), name='send-invite'),
    path('invites/<int:invite_id>/respond/', views.RespondToInviteView.as_view(), name='respond-invite'),
    
    # Active collaborations
    path('', views.CollaborationListView.as_view(), name='collaboration-list'),
    path('<int:collab_id>/', views.CollaborationDetailView.as_view(), name='collaboration-detail'),
    
    # AI suggestions
    path('suggestions/', views.CollaborationSuggestionsView.as_view(), name='collaboration-suggestions'),
]
