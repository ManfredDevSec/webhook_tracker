from django.urls import path
from . import views

app_name = 'tracking'

urlpatterns = [
    # Tracking
    path('track/<str:tracking_id>/', views.TrackView.as_view(), name='track'),
    path('view/<str:tracking_id>/', views.RequestListView.as_view(), name='view_requests'),
    path('request/<uuid:pk>/', views.RequestDetailView.as_view(), name='request_detail'),
    
    # Campaign Management
    path('campaigns/', views.CampaignListView.as_view(), name='campaign_list'),
    path('campaigns/create/', views.CampaignCreateView.as_view(), name='campaign_create'),
    path('campaigns/<int:pk>/', views.CampaignDetailView.as_view(), name='campaign_detail'),
    path('campaigns/<int:pk>/edit/', views.CampaignUpdateView.as_view(), name='campaign_edit'),
    path('campaigns/<int:pk>/delete/', views.CampaignDeleteView.as_view(), name='campaign_delete'),
    
    # Dashboard & API
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('api/requests/<str:tracking_id>/', views.RequestDataAPI.as_view(), name='api_requests'),
]