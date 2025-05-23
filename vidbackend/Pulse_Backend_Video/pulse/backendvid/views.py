from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from .models import VideoWatch, VideoPost  # Replace with your actual model
import os
import json


# Create your views here.
# Will take a GET request with video ID as a query parameter and return the video data this is an API endpoint to fetch video data in video page of pulse
def videopost(request):
    if request.method == 'GET':
        video_id = request.GET.get('video_id')
        user_id = request.GET.get('user_id')  # Optional user identification
        
        # Use absolute path to the videos directory at the project root
        video_path = os.path.join(settings.BASE_DIR, 'videos', f'{video_id}.mp4')
        print(f"Looking for video at: {video_path}")
        
        if os.path.exists(video_path):
            # Log the video watch
            log_video_watch(request, video_id, user_id)
            
            try:
                return FileResponse(open(video_path, 'rb'), content_type='video/mp4')
            except Exception as e:
                return JsonResponse({'error': f'Error reading file: {str(e)}'}, status=500)
        else:
            return JsonResponse({'error': 'Video not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

# Will receive a POST request with video ID and video data and save the video to the server
def upload_video(request):
    if request.method == 'POST':
        video_id = request.POST.get('video_id')
        video_file = request.FILES.get('video_file')
        if video_id and video_file:
            # Use absolute path to the videos directory at the project root
            video_path = os.path.join(settings.BASE_DIR, 'videos', f'{video_id}.mp4')
            try:
                with open(video_path, 'wb+') as destination:
                    for chunk in video_file.chunks():
                        destination.write(chunk)
                return JsonResponse({'message': 'Video uploaded successfully'}, status=201)
            except Exception as e:
                return JsonResponse({'error': f'Error saving file: {str(e)}'}, status=500)
        else:
            return JsonResponse({'error': 'Missing video ID or file'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def log_video_watch(request, video_id, user_id=None):
    """Helper function to log video watch"""
    try:
        # Get client IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Create video watch record
        VideoWatch.objects.create(
            video_id=video_id,
            user_id=user_id or request.session.session_key,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        print(f"Logged video watch: {video_id} by user: {user_id or 'anonymous'}")
        
    except Exception as e:
        print(f"Error logging video watch: {str(e)}")

@csrf_exempt
def track_video_watch(request):
    """API endpoint to manually track video watches"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            video_id = data.get('video_id')
            user_id = data.get('user_id')
            
            if not video_id:
                return JsonResponse({'error': 'video_id is required'}, status=400)
            
            log_video_watch(request, video_id, user_id)
            
            return JsonResponse({'message': 'Video watch logged successfully'}, status=200)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error logging watch: {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def video_feed(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id is required'}, status=400)

    # Get IDs of videos the user has already watched
    watched_videos = VideoWatch.objects.filter(user_id=user_id).values_list('video_id', flat=True)

    # Recommend videos not yet watched, ordered by popularity (number of watches)
    recommended = (
        VideoWatch.objects
        .exclude(video_id__in=watched_videos)
        .values('video_id')
        .annotate(watch_count=models.Count('id'))
        .order_by('-watch_count')[:10]
    )

    # Return just the video IDs for simplicity
    return JsonResponse({'feed': [v['video_id'] for v in recommended]}, status=200)

def feed(request):
    # Fetch latest posts, adjust model/fields as needed
    posts = VideoPost.objects.order_by('-created_at')[:20]
    return render(request, 'index.html', {'posts': posts})