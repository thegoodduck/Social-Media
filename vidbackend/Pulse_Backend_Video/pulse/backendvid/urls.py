from django.urls import path
from . import views
from .views import custom_token_auth

urlpatterns = [
    path('videopost/', views.videopost, name='videopost'),
    path('track-watch/', views.track_video_watch, name='track_video_watch'),
    path('create-post/', views.create_post, name='create_post'),
    path('feed-json/', views.video_feed_json, name='video_feed_json'),
    path('', views.feed, name='feed'),
    path('api-token-auth/', custom_token_auth, name='api_token_auth'),
]
