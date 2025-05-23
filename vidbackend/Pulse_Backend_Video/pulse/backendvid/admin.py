from django.contrib import admin
from .models import VideoWatch

@admin.register(VideoWatch)
class VideoWatchAdmin(admin.ModelAdmin):
    list_display = ['video_id', 'user_id', 'watched_at', 'ip_address']
    list_filter = ['watched_at', 'video_id']
    search_fields = ['video_id', 'user_id', 'ip_address']
    readonly_fields = ['watched_at']
