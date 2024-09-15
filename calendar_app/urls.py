from django.urls import path
from calendar_app import views

urlpatterns = [
    path('', views.home, name='home'),  # Add this line
    path('google_auth/', views.google_auth, name='google_auth'),
    path('oauth2callback/', views.oauth2callback, name='oauth2callback'),
    path('create_event/', views.create_event, name='create_event'),
    path('event_created/<str:event_id>/', views.event_created, name='event_created'),
]
