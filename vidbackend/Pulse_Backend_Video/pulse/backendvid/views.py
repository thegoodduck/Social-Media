from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from django.conf import settings
import os

# Create your views here.
# Will take a GET request with video ID as a query parameter and return the video data this is an API endpoint to fetch video data in video page of pulse
def videopost(request):
    if request.method == 'GET':
        video_id = request.GET.get('video_id')
        # Use absolute path to the videos directory at the project root
        video_path = os.path.join(settings.BASE_DIR, 'videos', f'{video_id}.mp4')
        print(f"Looking for video at: {video_path}")
        if os.path.exists(video_path):
            try:
                return FileResponse(open(video_path, 'rb'), content_type='video/mp4')
            except Exception as e:
                return JsonResponse({'error': f'Error reading file: {str(e)}'}, status=500)
        else:
            return JsonResponse({'error': 'Video not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
