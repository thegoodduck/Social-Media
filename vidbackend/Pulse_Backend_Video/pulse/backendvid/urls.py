from django.urls import path
from . import views

urlpatterns = [
    path('videopost/', views.videopost, name='videopost'),
]
