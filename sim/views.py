import json
import os
import re

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import requests
from django.contrib.sessions.models import Session
from openai import OpenAI

client = OpenAI()

from youtube_transcript_api import YouTubeTranscriptApi

from .models import CustomUser, Class, Post, Comment

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session
from .models import CustomUser, Class, Video, VideoQuestion


def get_session_user_data(session_id):
    try:
        session = Session.objects.get(session_key=session_id)
        session_user_data = session.get_decoded().get('user_data', {})
        return session_user_data.get('email')
    except Session.DoesNotExist:
        return None


def get_user_by_email(email):
    try:
        return CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return None


def create_response(data, status=200):
    return JsonResponse(data, status=status)

@csrf_exempt
def update_user_points(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            session_id = data.get('sessionID')
            points_delta = data.get('pointsDelta')

            email = get_session_user_data(session_id)
            if not email:
                return JsonResponse({'error': 'Email not found in session data'}, status=400)

            if not session_id or not email or not points_delta:
                return create_response({'error': 'Session ID, email, or pointsDelta parameter missing'}, status=400)

            session_email = get_session_user_data(session_id)
            if not session_email or session_email != email:
                return create_response({'error': 'Session user email does not match the provided email'}, status=400)

            user = get_user_by_email(email)
            if not user:
                return create_response({'error': 'User not found'}, status=404)

            # Update user points
            user.points += points_delta
            user.save()

            return create_response({'success': 'User points updated successfully'})

        except Exception as e:
            return create_response({'error': str(e)}, status=500)
    else:
        return create_response({'error': 'Invalid request method'}, status=400)

def parse_youtube_url(url):
    # Regular expression pattern to match YouTube video ID
    pattern = r"(?<=v=)[a-zA-Z0-9_-]+(?=&|\?|$)"
    match = re.search(pattern, url)
    if match:
        return match.group(0)
    else:
        return None

@csrf_exempt
def post_class_video(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            session_id = data.get('sessionID')
            video_url = data.get('videoURL')
            video_title = data.get('videoTitle')
            class_id = data.get('classID')

            if not session_id or not video_url or not video_title or not class_id:
                return create_response({'error': 'Session ID, video URL, video title, or class ID parameter missing'}, status=400)

            # Check if the class exists
            try:
                class_instance = Class.objects.get(pk=class_id)
            except Class.DoesNotExist:
                return create_response({'error': 'Class with ID {} does not exist'.format(class_id)}, status=404)

            # Create a new Video instance
            video = Video.objects.create(
                video_link=video_url,
                title=video_title,
                class_field=class_instance
            )

            # Get Video transcription
            video_id = parse_youtube_url(video_url)
            video_transcript = YouTubeTranscriptApi.get_transcript(video_id)

            # Convert transcript into a single string
            transcript_text = ' '.join([item['text'] for item in video_transcript])

            response_summary = ''
            gptPromptSummary=f"summarize this transcript in 40 words {transcript_text}",
            summary = get_gpt_response(gptPromptSummary, 0, 150).choices[0].text
            print(summary)

            gptPromptQA=f"Based on summary {summary} Generate 1 short single question. (MAKE NEW LINE SPLIT). Generate possible answer A (NEWLINE). Generate possible answer B (NEWLINE). Generate possible answer C (NEWLINE). Generate possible answer D (NEWLINE). Generate correct answer choice ( dont add prefixes to your responses NEWLINE)",
            response = get_gpt_response(gptPromptQA, 0, 150)
            
            # remove all instances of the word (NEWLINE)
            gpt_response = re.sub(r'\(NEWLINE\)|\(NEWLINE HERE\)', '', response.choices[0].text)
            print("GPT RESPONSE: ", gpt_response)
            split_text = gpt_response.split('\n')
            filtered_list = [item for item in split_text if item.strip()]
            print(filtered_list)
            question = filtered_list[0]
            answers = [item[3:] for item in filtered_list[1:5]]
            answer_choice = filtered_list[5][:3]
            answer_index = ['A', 'B', 'C', 'D'].index(answer_choice[:1])

            print("Question: ", question)
            print("Answers: ", answers)
            print("Answer: ", answer_index)

            video_question = VideoQuestion.objects.create(
                question=question,
                answers=answers,
                correct_answer_index=answer_index,
            )

            # Add the video to the class's video list
            class_instance.videos.add(video)

            # Associate the VideoQuestion with the Video
            video.video_questions.add(video_question)

            return create_response({'success': 'Video posted and questions generated successfully'})

        except Exception as e:
            return create_response({'error': str(e)}, status=500)
    else:
        return create_response({'error': 'Invalid request method'}, status=400)
    
def get_gpt_response(prompt, temp, tokens):
    try:
        response = client.completions.create(model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        temperature=0,
        max_tokens=200)
        return response
    except Exception as e:
        print("An error occurred while generating the question:", e)
        return None

@csrf_exempt
def get_class_video_list(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            session_id = data.get('sessionID')
            class_id = data.get('classID')

            if not session_id:
                return JsonResponse({'error': 'Session ID missing'}, status=400)

            email = get_session_user_data(session_id)
            if not email:
                return JsonResponse({'error': 'Email not found in session data'}, status=400)

            if not class_id:
                return JsonResponse({'error': 'Class ID missing'}, status=400)

            try:
                class_instance = Class.objects.get(pk=class_id)
                videos = class_instance.videos.all()
                video_list = []

                for video in videos:
                    video_data = {
                        'title': video.title,
                        'video_link': video.video_link,
                        'questions': []
                    }

                    # Fetch associated questions for the video
                    questions = video.video_questions.all()
                    for question in questions:
                        question_data = {
                            'question': question.question,
                            'answers': question.answers,
                            'correct_answer_index': question.correct_answer_index
                        }
                        video_data['questions'].append(question_data)

                    video_list.append(video_data)

                print(len(video_list))
                return JsonResponse({'videos': video_list})
            except Class.DoesNotExist:
                return JsonResponse({'error': 'Class with ID {} does not exist'.format(class_id)}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def get_user_points(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            session_id = data.get('sessionID')

            if not session_id:
                return create_response({'error': 'Session ID missing'}, status=400)

            email = get_session_user_data(session_id)
            if not email:
                return create_response({'error': 'Email not found in session data'}, status=400)

            user = get_user_by_email(email)
            if not user:
                return create_response({'error': 'User not found'}, status=404)

            points = user.points
            return create_response({'points': points})

        except Exception as e:
            return create_response({'error': str(e)}, status=500)
    else:
        return create_response({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def get_post_comments(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            session_id = data.get('sessionID')
            post_id = data.get('postID')
            if not session_id or not post_id:
                return create_response({'error': 'Session ID or post ID missing'}, status=400)

            email = get_session_user_data(session_id)
            if not email:
                return create_response({'error': 'Email not found in session data'}, status=400)

            post = Post.objects.get(pk=post_id)
            sub_posts = post.sub_posts.all()

            # Sort sub_posts by creation date, newest to oldest
            sorted_sub_posts = sorted(sub_posts, key=lambda x: x.created_at)

            sub_post_data = []
            for sub_post in sorted_sub_posts:
                sub_post_data.append({
                    'id': sub_post.id,
                    'title': sub_post.title,
                    'content': sub_post.content,
                    'created_at': sub_post.created_at,
                    # Add more fields as needed
                })

            return create_response({'sub_posts': sub_post_data})

        except Exception as e:
            return create_response({'error': str(e)}, status=500)
    else:
        return create_response({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def enroll_in_class(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            session_id = data.get('sessionID')
            class_code = data.get('classCode')

            if not session_id or not class_code:
                return create_response({'error': 'Session ID or class code missing'}, status=400)

            email = get_session_user_data(session_id)
            if not email:
                return create_response({'error': 'Email not found in session data'}, status=400)

            user = get_user_by_email(email)
            if not user:
                return create_response({'error': 'User not found'}, status=404)

            class_obj = Class.objects.get(class_code=class_code)
            class_obj.students.add(user)

            return create_response({'message': 'Enrolled in class successfully'})

        except Exception as e:
            return create_response({'error': str(e)}, status=500)
    else:
        return create_response({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def post_to_forum(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        try:
            data = json.loads(request.body.decode('utf-8'))
            session_id = data.get('sessionID')
            class_id = data.get('classID')
            title = data.get('title')
            content = data.get('content')

            if not session_id or not class_id or not title or not content:
                return create_response({'error': 'Session ID, class ID, title, or content missing'}, status=400)

            email = get_session_user_data(session_id)
            if not email:
                return create_response({'error': 'Email not found in session data'}, status=400)

            user = get_user_by_email(email)
            if not user:
                return create_response({'error': 'User not found'}, status=404)

            class_obj = Class.objects.get(pk=class_id)

            post = Post.objects.create(
                user=user, class_field=class_obj, title=title, content=content)
            
            #Generate AI Response
            response = ''
            try:
                response = client.completions.create(model="gpt-3.5-turbo-instruct",
                prompt="Respond to this question: Title: " + title + "body: " + content + "\n",
                max_tokens=75)
            except Exception as e:
                print("An error occurred while generating the question:", e)

            sub_post = Post.objects.create(
                user=user,
                class_field=class_obj,
                title="GPT RESPONSE",
                content=response.choices[0].text,
            )
            post.sub_posts.add(sub_post)

            return create_response({'message': 'Post created successfully'}, status=201)

        except Exception as e:
            return create_response({'error': str(e)}, status=500)
    else:
        return create_response({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def post_comment_to_forum(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            session_id = data.get('sessionID')
            class_id = data.get('classID')
            title = data.get('title')
            content = data.get('content')
            parent_post_id = data.get('parentPostID')

            if not session_id or not class_id or not title or not content:
                return create_response({'error': 'Session ID, class ID, title, or content missing'}, status=400)

            email = get_session_user_data(session_id)
            if not email:
                return create_response({'error': 'Email not found in session data'}, status=400)

            user = get_user_by_email(email)
            if not user:
                return create_response({'error': 'User not found'}, status=404)

            class_obj = Class.objects.get(pk=class_id)

            if not parent_post_id:
                post = Post.objects.create(
                    user=user,
                    class_field=class_obj,
                    title=title,
                    content=content
                )
            else:
                parent_post = Post.objects.get(pk=parent_post_id)
                post = Post.objects.create(
                    user=user,
                    class_field=class_obj,
                    title=title,
                    content=content,
                )
                parent_post.sub_posts.add(post)

            return create_response({'message': 'Post created successfully'}, status=201)
        except Exception as e:
            return create_response({'error': str(e)}, status=500)
    else:
        return create_response({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def get_all_posts(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            session_id = data.get('sessionID')
            class_id = data.get('classID')

            if not session_id or not class_id:
                return create_response({'error': 'Session ID or class ID missing'}, status=400)

            email = get_session_user_data(session_id)
            if not email:
                return create_response({'error': 'Email not found in session data'}, status=400)

            user = get_user_by_email(email)
            if not user:
                return create_response({'error': 'User not found'}, status=404)

            class_obj = Class.objects.get(pk=class_id)

            # Fetch top level posts and order them by newest first
            top_level_posts = Post.objects.filter(
                class_field=class_obj, parent_post__isnull=True).order_by('-created_at')

            post_data = []
            for post in top_level_posts:
                sub_posts = post.sub_posts.all()
                post_data.append({
                    'id': post.id,
                    'title': post.title,
                    'content': post.content,
                    'created_at': post.created_at,
                    'teacher_post': post.user == class_obj.teacher,
                    'sub_posts': [
                        {
                            'id': sub_post.id,
                            'content': sub_post.content,
                            'created_at': sub_post.created_at,
                            'teacher_post': sub_post.user == class_obj.teacher
                        } for sub_post in sub_posts
                    ]
                })

            return create_response({'posts': post_data}, status=200)
        except Exception as e:
            return create_response({'error': str(e)}, status=500)
    else:
        return create_response({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def get_enrolled_classes(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            session_id = data.get('sessionID')

            if not session_id:
                return create_response({'error': 'Session ID missing'}, status=400)

            email = get_session_user_data(session_id)
            if not email:
                return create_response({'error': 'Email not found in session data'}, status=400)

            user = get_user_by_email(email)
            if not user:
                return create_response({'error': 'User not found'}, status=404)

            enrolled_classes = Class.objects.filter(students=user)

            class_data = [{'id': cls.id, 'class_code': cls.class_code,
                           'class_name': cls.class_name} for cls in enrolled_classes]

            return create_response({'enrolled_classes': class_data}, status=200)
        except Exception as e:
            return create_response({'error': str(e)}, status=500)
    else:
        return create_response({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def create_new_class(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            session_id = data.get('sessionID')
            class_name = data.get('class_name')
            class_code = data.get('class_code')

            if not (class_name and class_code and session_id):
                return create_response({'error': 'All parameters must be provided'}, status=400)

            user = get_user_by_email(get_session_user_data(session_id))
            if not user:
                return create_response({'error': 'User not found'}, status=404)

            new_class = Class.objects.create(class_name=class_name, class_code=class_code, teacher=user)
            return create_response({'message': 'Class created successfully'}, status=201)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return create_response({'error': str(e)}, status=500)
    else:
        return create_response({'error': 'Invalid request method'}, status=400)

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