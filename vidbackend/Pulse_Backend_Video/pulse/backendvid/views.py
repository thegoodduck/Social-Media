from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json


@csrf_exempt
@require_POST
def custom_token_auth(request):
    try:
        data = json.loads(request.body.decode())
        username = data.get('username')
        password = data.get('password')
        if username == 'sync' and password == 'supersync96':
            token, _ = Token.objects.get_or_create(user_id=1)  # user_id=1 is usually the first superuser
            return JsonResponse({'token': token.key})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_POST
def videopost(request):
    # Token authentication
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Token '):
        return JsonResponse({'error': 'Missing or invalid token'}, status=401)
    token_key = auth_header.split(' ')[1]
    try:
        token = Token.objects.get(key=token_key)
    except Token.DoesNotExist:
        return JsonResponse({'error': 'Invalid token'}, status=401)

    # Get user from param or token
    user_param = request.POST.get('user')
    if user_param:
        try:
            user = User.objects.get(username=user_param)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=400)
    else:
        user = token.user

    # Handle file upload
    video_file = request.FILES.get('video')
    if not video_file:
        return JsonResponse({'error': 'No video file provided'}, status=400)
    filename = default_storage.save(video_file.name, ContentFile(video_file.read()))
    video_url = default_storage.url(filename)

    # Save VideoPost
    from .models import VideoPost
    caption = request.POST.get('caption', '')
    VideoPost.objects.create(user=user, caption=caption, video_url=video_url)
    return JsonResponse({'success': True, 'video_url': video_url, 'user': user.username, 'caption': caption})