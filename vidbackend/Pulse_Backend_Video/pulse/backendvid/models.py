from django.db import models
from django.contrib.auth.models import User

class VideoWatch(models.Model):
    video_id = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100, null=True, blank=True)  # For anonymous users, can be session ID
    watched_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'video_watches'
        
    def __str__(self):
        return f"Video {self.video_id} watched at {self.watched_at}"
