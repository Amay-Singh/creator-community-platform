from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications_list, name='notifications-list'),
    path('mark-read/', views.mark_notifications_read, name='mark-notifications-read'),
    path('unread-count/', views.unread_count, name='unread-count'),
]
