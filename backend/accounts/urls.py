from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify/', views.VerifyAccountView.as_view(), name='verify'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Profile management
    path('me/', views.ProfileDetailView.as_view(), name='profile-detail'),
    path('me/stats/', views.ProfileStatsView.as_view(), name='profile-stats'),
    path('portfolio/', views.PortfolioUploadView.as_view(), name='portfolio-upload'),
    path('browse/', views.ProfileBrowseView.as_view(), name='profile-browse'),
]
