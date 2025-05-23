from django.urls import path
from . import views

urlpatterns = [
    path('videopost/', views.videopost, name='videopost'),
    path('track-watch/', views.track_video_watch, name='track_video_watch'),
]
