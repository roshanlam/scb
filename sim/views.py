import json
import os

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import requests
from django.contrib.sessions.models import Session

from .models import CustomUser, Class, Post

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session
from .models import CustomUser, Class


@csrf_exempt
def enroll_in_class(request):
    """
    Enrolls the user in the specified class.
    """
    if request.method == 'POST':
        try:
            # Get params from post
            data = json.loads(request.body.decode('utf-8'))
            session_id = data.get('sessionID')
            class_code = data.get('classCode')
            print(session_id, class_code)

            # Retrieve the session object using session_id
            session = Session.objects.get(session_key=session_id)
            session_user_data = session.get_decoded().get('user_data', {})

            # Extract email from session user data
            email = session_user_data.get('email')

            if not email:
                return JsonResponse({'error': 'Email not found in session data'}, status=400)

            # Get the user object based on the email
            user = CustomUser.objects.get(email=email)

            # Get the class object based on the class ID
            class_obj = Class.objects.get(class_code=class_code)

            # Add the user to the class's students list
            class_obj.students.add(user)
            return JsonResponse({'message': 'Enrolled in class successfully'}, status=200)
        except Session.DoesNotExist:
            return JsonResponse({'error': 'Session not found'}, status=404)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Class.DoesNotExist:
            return JsonResponse({'error': 'Class not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def post_to_forum(request):
    """
    Creates a new post.
    """
    if request.method == 'POST':
        try:
            # Get params from post
            data = json.loads(request.body.decode('utf-8'))
            session_id = data.get('sessionID')
            class_id = data.get('classID')
            title = data.get('title')
            content = data.get('content')
            print(session_id, class_id, title, content)

            # Retrieve the session object using session_id
            session = Session.objects.get(session_key=session_id)
            session_user_data = session.get_decoded().get('user_data', {})

            # Extract email from session user data
            email = session_user_data.get('email')

            if not email:
                return JsonResponse({'error': 'Email not found in session data'}, status=400)

            # Get the user object based on the email
            user = CustomUser.objects.get(email=email)

            # Get the class object based on the class ID
            class_obj = Class.objects.get(pk=class_id)

            # Check if title and content are not None
            if title is None or content is None:
                return JsonResponse({'error': 'Title or content is missing'}, status=400)

            # Create the post with the retrieved user as the owner
            post = Post.objects.create(
                user=user, class_field=class_obj, title=title, content=content)

            return JsonResponse({'message': 'Post created successfully'}, status=201)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Class.DoesNotExist:
            return JsonResponse({'error': 'Class not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def get_all_posts(request):
    """
    Retrieves all posts for a specific class and only displays posts belonging to classes in which the user is enrolled.
    """
    if request.method == 'POST':
        try:
            # Get params from post
            data = json.loads(request.body.decode('utf-8'))
            session_id = data.get('sessionID')
            class_id = data.get('classID')

            if not session_id or not class_id:
                return JsonResponse({'error': 'Session ID or class ID missing'}, status=400)

            # Retrieve the session object using session_id
            session = Session.objects.get(session_key=session_id)
            session_user_data = session.get_decoded().get('user_data', {})

            # Extract email from session user data
            email = session_user_data.get('email')

            if not email:
                return JsonResponse({'error': 'Email not found in session data'}, status=400)

            # Get the user object based on the email
            user = CustomUser.objects.get(email=email)

            # Retrieve the class object based on the class ID
            class_obj = Class.objects.get(pk=class_id)

            # Check if the user is enrolled in the class
            if user in class_obj.students.all():
                # Retrieve all posts for the class
                posts = Post.objects.filter(class_field=class_obj)
                post_data = [{'title': post.title, 'content': post.content,
                              'created_at': post.created_at} for post in posts]

                return JsonResponse({'posts': post_data}, status=200)
            else:
                return JsonResponse({'error': 'User is not enrolled in the specified class'}, status=403)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Class.DoesNotExist:
            return JsonResponse({'error': 'Class not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def get_enrolled_classes(request):
    """
    Retrieves all classes in which the user is enrolled.
    """
    if request.method == 'POST':
        try:
            # Get params from post
            data = json.loads(request.body.decode('utf-8'))
            session_id = data.get('sessionID')
            print(session_id)

            if not session_id:
                return JsonResponse({'error': 'Session ID missing'}, status=400)

            # Retrieve the session object using session_id
            session = Session.objects.get(session_key=session_id)
            session_user_data = session.get_decoded().get('user_data', {})

            # Extract email from session user data
            email = session_user_data.get('email')

            if not email:
                return JsonResponse({'error': 'Email not found in session data'}, status=400)

            # Get the user object based on the email
            user = CustomUser.objects.get(email=email)

            # Retrieve all classes in which the user is enrolled
            enrolled_classes = Class.objects.filter(students=user)

            # Serialize the class data
            class_data = [{'id': cls.id, 'class_code': cls.class_code, 'class_name': cls.class_name} for cls in enrolled_classes]

            return JsonResponse({'enrolled_classes': class_data}, status=200)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
@csrf_exempt
def create_new_class(request):
    """
    Creates a new class with class name and ID passed in from the JSON request.
    """
    if request.method == 'POST':
        try:
            # Get params from post
            data = json.loads(request.body.decode('utf-8'))
            session_id = data.get('sessionID')
            class_name = data.get('class_name')
            class_code = data.get('class_code')

            if not class_name or not class_code or not session_id:
                return JsonResponse({'error': 'Class name, code, or session ID missing'}, status=400)

            # Retrieve the session object using session_id
            session = Session.objects.get(session_key=session_id)
            session_user_data = session.get_decoded().get('user_data', {})
            email = session_user_data.get('email')

            if not email:
                return JsonResponse({'error': 'Email not found in session data'}, status=400)

            # Get the user object based on the email
            user = CustomUser.objects.get(email=email)

            # Create a new class object
            new_class = Class.objects.create(class_name=class_name, class_code=class_code, teacher=user)

            return JsonResponse({'message': 'Class created successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def auth_receiver(request):
    """
    Google calls this URL after the user has signed in with their Google account.
    """
    authorization_code = request.headers.get('Authorization')

    if not authorization_code:
        return HttpResponse(status=400)

    try:
        token_request_data = {
            'code': authorization_code,
            'client_id': os.environ['GOOGLE_OAUTH_CLIENT_ID'],
            'client_secret': os.environ['GOOGLE_OAUTH_CLIENT_SECRET'],
            'redirect_uri': 'http://localhost:5173',
            'grant_type': 'authorization_code'
        }
        token_response = requests.post(
            'https://oauth2.googleapis.com/token', data=token_request_data)
        token_response_data = token_response.json()
        access_token = token_response_data.get('access_token')

        # Use the access token to retrieve user data if necessary
        if access_token:
            # Example: Fetch user data using the access token
            user_data_response = requests.get(
                'https://www.googleapis.com/oauth2/v3/userinfo', headers={'Authorization': f'Bearer {access_token}'})
            user_data = user_data_response.json()

            # Check if the user already exists
            try:
                user = CustomUser.objects.get(username=user_data['email'])
            except CustomUser.DoesNotExist:
                # User doesn't exist, create a new one
                user = CustomUser(
                    username=user_data['email'], email=user_data['email'], user_type=2)
                user.save()

            # Set user type to student if not already set
            if not user.user_type:
                user.user_type = 'student'
                user.save()

            # Store user data in session
            request.session['user_data'] = user_data
            request.session.save()

            session_key = request.session.session_key

            response_data = {
                'user_data': user_data,
                'session_key': session_key
            }

            # In a real app, save any new user data here to the database.
            # You could also authenticate the user here using the details from Google.

            return JsonResponse(response_data, status=200)
    except Exception as e:
        print(f"Failed to exchange authorization code for token: {e}")
        return JsonResponse({'error': 'Failed to exchange authorization code for token'}, status=403)


def sign_out(request, session_id):
    try:
        # Retrieve the session object using session_id
        session = Session.objects.get(session_key=session_id)

        # Delete the session data
        session.delete()

        # Optionally, perform additional cleanup or logging
        # ...

        # Return a JSON response indicating successful sign-out
        return JsonResponse({'message': 'User signed out successfully'}, status=200)
    except Session.DoesNotExist:
        # Handle case where session with given ID does not exist
        return JsonResponse({'error': 'Session not found'}, status=404)
    except Exception as e:
        # Handle other exceptions
        return JsonResponse({'error': str(e)}, status=500)
