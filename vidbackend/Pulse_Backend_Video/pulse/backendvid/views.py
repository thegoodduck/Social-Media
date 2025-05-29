from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import VideoWatch, VideoPost  # Replace with your actual model
import os
import json
import uuid  # Import the UUID module


# Create your views here.
# Will take a GET request with video ID as a query parameter and return the video data this is an API endpoint to fetch video data in video page of pulse
def videopost(request):
    if request.method == 'GET':
        video_id = request.GET.get('video_id')
        user_id = request.GET.get('user_id')  # Optional user identification
        
        # Use absolute path to the videos directory at the project root
        base_videos_path = os.path.join(settings.BASE_DIR, 'videos')
        video_path = os.path.normpath(os.path.join(base_videos_path, f'{video_id}.mp4'))
        
        # Ensure the video_path is within the base_videos_path
        if not video_path.startswith(base_videos_path):
            return JsonResponse({'error': 'Invalid video path'}, status=400)
        
        print(f"Looking for video at: {video_path}")
        
        if os.path.exists(video_path):
            # Log the video watch
            log_video_watch(request, video_id, user_id)
            
            try:
                return FileResponse(open(video_path, 'rb'), content_type='video/mp4')
            except Exception as e:
                import logging
                logging.error(f"Error reading file: {str(e)}")
                return JsonResponse({'error': 'An internal error has occurred'}, status=500)
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
            base_videos_path = os.path.join(settings.BASE_DIR, 'videos')
            video_path = os.path.normpath(os.path.join(base_videos_path, f'{video_id}.mp4'))
            
            # Ensure the video_path is within the base_videos_path
            if not video_path.startswith(base_videos_path):
                return JsonResponse({'error': 'Invalid video path'}, status=400)
            
            try:
                with open(video_path, 'wb+') as destination:
                    for chunk in video_file.chunks():
                        destination.write(chunk)
                return JsonResponse({'message': 'Video uploaded successfully'}, status=201)
            except Exception as e:
                import logging
                logging.error(f"Error saving file: {str(e)}")
                return JsonResponse({'error': 'An internal error has occurred'}, status=500)
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
        import logging
        logging.error(f"Error logging video watch: {str(e)}")

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
            import logging
            logging.error(f"Error logging watch: {str(e)}")
            return JsonResponse({'error': 'An internal error has occurred'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def video_feed(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id is required'}, status=400)

    # Recommend videos ordered by popularity (number of watches), regardless of watched status
    recommended = (
        VideoWatch.objects
        .values('video_id')
        .annotate(watch_count=models.Count('id'))
        .order_by('-watch_count')[:10]
    )

    # Return just the video IDs for simplicity
    return JsonResponse({'feed': [v['video_id'] for v in recommended]}, status=200)

def feed(request):
    user_id = request.GET.get('user_id') or request.session.session_key
    if not user_id:
        request.session.save()
        user_id = request.session.session_key

    # 1. Get watched and unwatched video_ids
    watched_videos = set(VideoWatch.objects.filter(user_id=user_id).values_list('video_id', flat=True))
    all_posts = list(VideoPost.objects.all())

    # 2. Recommend unwatched videos first, ordered by popularity
    unwatched_recommended = (
        VideoWatch.objects
        .exclude(video_id__in=watched_videos)
        .values('video_id')
        .annotate(watch_count=models.Count('id'))
        .order_by('-watch_count')
    )
    unwatched_ids = [str(v['video_id']).strip() for v in unwatched_recommended]
    unwatched_posts = [p for p in all_posts if p.video_id in unwatched_ids]

    # 3. Add any remaining unwatched posts not in recommended (new uploads, etc)
    extra_unwatched_posts = [p for p in all_posts if (p.video_id not in watched_videos and p not in unwatched_posts)]

    # 4. Then show watched videos, ordered by most recently watched
    recently_watched_ids = list(VideoWatch.objects.filter(user_id=user_id).order_by('-watched_at').values_list('video_id', flat=True))
    watched_posts = [p for vid in recently_watched_ids for p in all_posts if p.video_id == vid]

    # 5. Add any posts not yet included (guarantee all posts are shown eventually)
    included_ids = set([p.video_id for p in unwatched_posts] + [p.video_id for p in extra_unwatched_posts] + [p.video_id for p in watched_posts])
    missing_posts = [p for p in all_posts if p.video_id not in included_ids]

    # 6. Final feed: addictive order
    posts = unwatched_posts + extra_unwatched_posts + watched_posts + missing_posts

    print("Feed order:", [p.video_id for p in posts])
    return render(request, 'index.html', {'posts': posts, 'user_id': user_id})

@csrf_exempt
def create_post(request):
    if request.method == 'POST':
        from django.contrib.auth.models import User

        # Generate a unique video_id
        video_id = str(uuid.uuid4())  # Generate a UUID
        caption = request.POST.get('caption')
        video_file = request.FILES.get('video_file')
        user = User.objects.first()  # Replace with actual user logic

        if not caption or not video_file:
            return JsonResponse({'error': 'Missing caption or file'}, status=400)

        # Save the video file to the "videos" directory
        video_path = os.path.join(settings.BASE_DIR, 'videos', f'{video_id}.mp4')
        with open(video_path, 'wb') as f:
            for chunk in video_file.chunks():
                f.write(chunk)

        # Create a new VideoPost
        VideoPost.objects.create(
            user=user,
            caption=caption,
            video_url=f'/api/videopost/?video_id={video_id}',
            video_id=video_id  # Use the unique video_id
        )

        # Debugging: Log the details of the newly created post
        print(f"New VideoPost created: video_id={video_id}, caption={caption}, user={user}")

        return JsonResponse({'message': 'Post created successfully'}, status=201)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)