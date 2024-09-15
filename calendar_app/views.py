from django.shortcuts import render, redirect
from django.conf import settings
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Enable http for local development


from django.shortcuts import redirect

def home(request):
    return redirect('google_auth')

def google_auth(request):
    # Initiating OAuth2 flow
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRET_FILE,
        scopes=['https://www.googleapis.com/auth/calendar'],
        redirect_uri='http://localhost:8000/oauth2callback/')

    authorization_url, state = flow.authorization_url(access_type='offline')

    # Store state for later validation in the callback
    request.session['state'] = state
    return redirect(authorization_url)


def oauth2callback(request):
    state = request.session['state']

    # Rebuild the OAuth2 flow to get tokens
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRET_FILE,
        scopes=['https://www.googleapis.com/auth/calendar'],
        state=state,
        redirect_uri='http://localhost:8000/oauth2callback/')

    # Fetch the token using the authorization response
    flow.fetch_token(authorization_response=request.build_absolute_uri())

    # Save the credentials to the session
    credentials = flow.credentials
    request.session['credentials'] = credentials_to_dict(credentials)

    return redirect('create_event')


def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }


def create_event(request):
    if request.method == 'POST':
        # Get event details from the form
        summary = request.POST.get('summary')
        location = request.POST.get('location')
        description = request.POST.get('description')
        start_time = request.POST.get('start')
        end_time = request.POST.get('end')

        # Load credentials from session
        credentials_data = request.session.get('credentials')

        if not credentials_data:
            return redirect('google_auth')

        # Convert the dictionary to credentials object
        credentials = Credentials(**credentials_data)

        # Build the service with authorized credentials
        service = build('calendar', 'v3', credentials=credentials)

        # Create event details
        event = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'UTC',
            },
        }

        # Insert the event into the user's calendar
        created_event = service.events().insert(calendarId='primary', body=event).execute()

        # Redirect to the event_created page
        return redirect('event_created', event_id=created_event['id'])
    
    return render(request, 'create_event.html')


def event_created(request, event_id):
    return render(request, 'event_created.html', {'event_id': event_id})
