import os

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import requests
import jwt
from django.contrib.sessions.models import Session



def sign_in(request):
    return render(request, 'sign_in.html')


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
        token_response = requests.post('https://oauth2.googleapis.com/token', data=token_request_data)
        token_response_data = token_response.json()
        access_token = token_response_data.get('access_token')

        # Use the access token to retrieve user data if necessary
        if access_token:
            # Example: Fetch user data using the access token
            user_data_response = requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers={'Authorization': f'Bearer {access_token}'})
            user_data = user_data_response.json()

            # Store user data in session
            request.session['user_data'] = user_data
            request.session.save()
            print(request.session.get('user_data'))

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