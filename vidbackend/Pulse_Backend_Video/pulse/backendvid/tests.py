from django.test import TestCase, Client
import os

class VideoPostViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.video_id = '4171'
        self.video_path = os.path.join('videos', f'{self.video_id}.mp4')
        # Ensure the video file exists for the test
        if not os.path.exists('videos'):
            os.makedirs('videos')
        with open(self.video_path, 'wb') as f:
            f.write(b'Test video content')

    def tearDown(self):
        # Clean up the video file after the test
        if os.path.exists(self.video_path):
            os.remove(self.video_path)

    def test_videopost_success(self):
        response = self.client.get('/api/videopost/', {'video_id': self.video_id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'video/mp4')

    def test_videopost_not_found(self):
        response = self.client.get('/api/videopost/', {'video_id': 'nonexistent'})
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(response.content, {'error': 'Video not found'})

    def test_videopost_invalid_method(self):
        response = self.client.post('/api/videopost/', {'video_id': self.video_id})
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Invalid request method'})
