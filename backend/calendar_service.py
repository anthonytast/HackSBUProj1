from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import os
import json
import secrets
from dotenv import load_dotenv
from schemas import StudyTask, CalendarEventResponse

# Load environment variables
load_dotenv()


class CalendarService:
    """Service for managing Google Calendar events"""
    
    # If modifying these scopes, delete the token.json file
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self):
        self.creds = None
        self.service = None
        self.calendar_id = 'primary'  # Use primary calendar by default
        self.oauth_flow = None
        
        # Color IDs for different priorities
        self.color_map = {
            'high': '11',      # Red
            'medium': '5',     # Yellow
            'low': '10'        # Green
        }
        
        # OAuth configuration
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            raise ValueError("Missing required Google OAuth credentials. Please check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env")
            
        self.client_config = {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/google/auth/callback")]
            }
        }
    
    async def get_authorization_url(self) -> str:
        """
        Generate Google OAuth authorization URL
        
        Returns:
            str: Authorization URL for user to visit
        """
        try:
            # Create flow instance with explicit redirect URI
            redirect_uri = "http://localhost:8000/google/auth/callback"
            self.oauth_flow = Flow.from_client_config(
                self.client_config,
                scopes=self.SCOPES,
                redirect_uri=redirect_uri
            )
            
            # Generate authorization URL with state for CSRF protection
            authorization_url, state = self.oauth_flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'  # Force consent screen to get refresh token
            )
            
            return authorization_url
            
        except Exception as e:
            print(f"Error generating authorization URL: {e}")
            raise
    
    async def handle_oauth_callback(self, code: str, state: Optional[str] = None) -> dict:
        """
        Handle OAuth callback and exchange code for credentials
        
        Args:
            code: Authorization code from Google
            state: State parameter for CSRF protection
            
        Returns:
            dict: Credentials dictionary
        """
        try:
            if not self.oauth_flow:
                # Recreate flow if needed with explicit redirect URI
                redirect_uri = "http://localhost:8000/google/auth/callback"
                self.oauth_flow = Flow.from_client_config(
                    self.client_config,
                    scopes=self.SCOPES,
                    redirect_uri=redirect_uri
                )
            
            # Exchange authorization code for credentials
            self.oauth_flow.fetch_token(code=code)
            
            # Get credentials
            credentials = self.oauth_flow.credentials
            
            # Convert to dictionary for storage
            creds_dict = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            
            # Store credentials
            self.creds = credentials
            self.service = build('calendar', 'v3', credentials=self.creds)
            
            return creds_dict
            
        except Exception as e:
            print(f"OAuth callback error: {e}")
            raise
    
    async def authenticate(self, credentials: dict) -> bool:
        """
        Authenticate with Google Calendar API
        
        Args:
            credentials: OAuth credentials dictionary
            
        Returns:
            bool: True if authentication successful
        """
        try:
            # Load credentials from dictionary
            self.creds = Credentials.from_authorized_user_info(credentials, self.SCOPES)
            
            # Refresh credentials if expired
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            
            # Build the service
            self.service = build('calendar', 'v3', credentials=self.creds)
            
            # Test by fetching calendar list
            calendars = self.service.calendarList().list().execute()
            return len(calendars.get('items', [])) > 0
            
        except Exception as e:
            print(f"Google Calendar authentication error: {e}")
            return False
    
    def authenticate_with_file(self, token_path: str = 'token.json', 
                               credentials_path: str = 'credentials.json') -> bool:
        """
        Authenticate using local credentials file (for development)
        
        Args:
            token_path: Path to token.json file
            credentials_path: Path to credentials.json file
            
        Returns:
            bool: True if authentication successful
        """
        try:
            # Load existing token
            if os.path.exists(token_path):
                self.creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
            
            # If no valid credentials, get new ones
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, self.SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)
                
                # Save credentials
                with open(token_path, 'w') as token:
                    token.write(self.creds.to_json())
            
            self.service = build('calendar', 'v3', credentials=self.creds)
            return True
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    async def create_study_events(self, tasks: List[StudyTask]) -> List[CalendarEventResponse]:
        """
        Create calendar events for study tasks
        
        Args:
            tasks: List of study tasks to schedule
            
        Returns:
            List of created calendar events
        """
        if not self.service:
            raise Exception("Not authenticated with Google Calendar")
        
        created_events = []
        
        for task in tasks:
            try:
                event = await self.create_event(task)
                created_events.append(event)
            except Exception as e:
                print(f"Failed to create event for task '{task.task_name}': {e}")
                # Continue creating other events even if one fails
        
        return created_events
    
    async def create_event(self, task: StudyTask) -> CalendarEventResponse:
        """
        Create a single calendar event from a study task
        
        Args:
            task: Study task to schedule
            
        Returns:
            CalendarEventResponse with event details
        """
        try:
            # Parse date and time
            start_datetime = datetime.fromisoformat(f"{task.suggested_date}T{task.suggested_start_time}:00")
            end_datetime = start_datetime + timedelta(minutes=task.duration_minutes)
            
            # Build event
            event = {
                'summary': f"📚 Study: {task.assignment_title}",
                'description': f"""
{task.task_name}

Course: {task.course_name}
Duration: {task.duration_minutes} minutes
Priority: {task.priority.upper()}

{task.description or ''}

---
Created by Study Planner
""".strip(),
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'America/New_York',  # Update based on user's timezone
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'America/New_York',
                },
                'colorId': self.color_map.get(task.priority, '5'),
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 30},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }
            
            # Create the event
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            return CalendarEventResponse(
                event_id=created_event['id'],
                summary=created_event['summary'],
                start_time=datetime.fromisoformat(created_event['start']['dateTime'].replace('Z', '+00:00')),
                end_time=datetime.fromisoformat(created_event['end']['dateTime'].replace('Z', '+00:00')),
                description=created_event.get('description', ''),
                html_link=created_event.get('htmlLink', ''),
                status=created_event.get('status', 'confirmed')
            )
            
        except Exception as e:
            print(f"Error creating calendar event: {e}")
            raise Exception(f"Failed to create calendar event: {str(e)}")
    
    async def get_free_slots(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Get available free time slots in the calendar
        
        Args:
            start_date: Start date in ISO format
            end_date: End date in ISO format
            
        Returns:
            List of free time slots
        """
        if not self.service:
            raise Exception("Not authenticated with Google Calendar")
        
        try:
            # Parse dates
            time_min = datetime.fromisoformat(start_date).isoformat() + 'Z'
            time_max = datetime.fromisoformat(end_date).isoformat() + 'Z'
            
            # Fetch busy times
            body = {
                "timeMin": time_min,
                "timeMax": time_max,
                "items": [{"id": self.calendar_id}]
            }
            
            events_result = self.service.freebusy().query(body=body).execute()
            busy_times = events_result['calendars'][self.calendar_id]['busy']
            
            # Calculate free slots
            free_slots = []
            current_time = datetime.fromisoformat(start_date)
            end_time = datetime.fromisoformat(end_date)
            
            for busy in busy_times:
                busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                
                if current_time < busy_start:
                    free_slots.append({
                        'start': current_time.isoformat(),
                        'end': busy_start.isoformat(),
                        'duration_minutes': int((busy_start - current_time).total_seconds() / 60)
                    })
                
                current_time = max(current_time, busy_end)
            
            # Add final free slot if exists
            if current_time < end_time:
                free_slots.append({
                    'start': current_time.isoformat(),
                    'end': end_time.isoformat(),
                    'duration_minutes': int((end_time - current_time).total_seconds() / 60)
                })
            
            return free_slots
            
        except Exception as e:
            print(f"Error fetching free slots: {e}")
            raise Exception(f"Failed to get free slots: {str(e)}")
    
    async def delete_event(self, event_id: str) -> bool:
        """
        Delete a calendar event
        
        Args:
            event_id: ID of the event to delete
            
        Returns:
            bool: True if deletion successful
        """
        if not self.service:
            raise Exception("Not authenticated with Google Calendar")
        
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            return True
        except Exception as e:
            print(f"Error deleting event: {e}")
            return False
    
    async def update_event(self, event_id: str, task: StudyTask) -> CalendarEventResponse:
        """
        Update an existing calendar event
        
        Args:
            event_id: ID of the event to update
            task: Updated study task data
            
        Returns:
            Updated CalendarEventResponse
        """
        if not self.service:
            raise Exception("Not authenticated with Google Calendar")
        
        try:
            # Get existing event
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            # Update fields
            start_datetime = datetime.fromisoformat(f"{task.suggested_date}T{task.suggested_start_time}:00")
            end_datetime = start_datetime + timedelta(minutes=task.duration_minutes)
            
            event['summary'] = f"📚 Study: {task.assignment_title}"
            event['description'] = f"{task.task_name}\n\n{task.description or ''}"
            event['start'] = {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'America/New_York',
            }
            event['end'] = {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'America/New_York',
            }
            event['colorId'] = self.color_map.get(task.priority, '5')
            
            # Update the event
            updated_event = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            return CalendarEventResponse(
                event_id=updated_event['id'],
                summary=updated_event['summary'],
                start_time=datetime.fromisoformat(updated_event['start']['dateTime'].replace('Z', '+00:00')),
                end_time=datetime.fromisoformat(updated_event['end']['dateTime'].replace('Z', '+00:00')),
                description=updated_event.get('description', ''),
                html_link=updated_event.get('htmlLink', ''),
                status=updated_event.get('status', 'confirmed')
            )
            
        except Exception as e:
            print(f"Error updating event: {e}")
            raise Exception(f"Failed to update event: {str(e)}")
