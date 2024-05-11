from django.test import TestCase, Client
from django.urls import reverse
import json
from .models import CustomUser, Class, Post

class BackendTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create a user
        self.user = CustomUser.objects.create(
            username="test",
            email="test@example.com",
            user_type=2,
            points=0
        )
       
        # Force client to create a session
        self.client.force_login(self.user) 

        # Retrieve the session object
        self.session = self.client.session

        # Store the session ID
        self.session_id = self.session.session_key

        # Modify the session data (if needed)
        self.session['user_data'] = {'email': self.user.email}
        self.session.save()

        # Mock Class
        self.class1 = Class.objects.create(
            class_name="Test Class 1",
            class_code="101",
            teacher=CustomUser.objects.create(username="testteacher", email="testteacher@example.com", user_type=1)
        )
        self.class1.students.add(self.user)

        # Mock Post
        self.post1 = Post.objects.create(
            title="Test Post 1",
            content="Test Content 1",
            class_field=self.class1,
            user=self.user
        )

    def test_create_new_class(self):
        url = reverse('create_new_class')
        data = {
            'sessionID': self.session_id,
            'class_name': 'Test Class',
            'class_code': 123456
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Class.objects.count(), 2)
    
    def test_get_enrolled_classes(self):
        url = reverse('get_enrolled_classes')
        data = {
            'sessionID': self.session_id,
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 200)

    def test_enroll_in_class(self):
        url = reverse('enroll_in_class')
        data = {
            'sessionID': self.session_id,
            'classCode': 101,
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Class.objects.count(), 1)

    #Cant Mock GPT Code to test post_to_forum
        
    def test_get_user_points(self):
        url = reverse('get_user_points')
        data = {
            'sessionID': self.session_id,
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 200)

    def test_update_user_points(self):
        url = reverse('update_user_points')
        data = {
            'sessionID': self.session_id,
            'pointsDelta': 1,
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.user.refresh_from_db()  

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.points, 1)

    def test_get_class_video_list(self):
        url = reverse('get_class_video_list')
        data = {
            'sessionID': self.session_id,
            'classID': 101,
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.user.refresh_from_db()  

        self.assertEqual(response.status_code, 404)

    def test_post_comment_to_forum(self):
        url = reverse('post_comment_to_forum')
        data = {
            'sessionID': self.session_id,
            'classID': self.class1.id,
            'title': "Test Comment 1",
            'content': "Test Content 1",
            'parentPostID': self.post1.id,
        }

        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.user.refresh_from_db()  

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Post.objects.count(), 2)

    def test_get_class_video_list(self):
        url = reverse('get_class_video_list')
        data = {
            'sessionID': self.session_id,
            'classID': self.class1.id,
        }

        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.user.refresh_from_db()  

        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        # Clean up after the tests
        self.session.delete()