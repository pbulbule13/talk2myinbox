"""
Calendar Synchronization Services.
Handles OAuth flows, event fetching, and synchronization for multiple calendar providers.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import os
import uuid
import hashlib
from pathlib import Path

# Google Calendar API
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError:
    GOOGLE_CALENDAR_AVAILABLE = False

# Microsoft Graph API
try:
    from msal import PublicClientApplication, ConfidentialClientApplication
    import requests
    MICROSOFT_GRAPH_AVAILABLE = True
except ImportError:
    MICROSOFT_GRAPH_AVAILABLE = False

# iCal/ICS parsing
try:
    from icalendar import Calendar as ICalendar
    import recurring_ical_events
    ICAL_AVAILABLE = True
except ImportError:
    ICAL_AVAILABLE = False

from data_models.pydantic_schemas import (
    CalendarSource,
    UnifiedEvent,
    CalendarConnection
)
from nodes.calendar_storage import CalendarStorageManager


class GoogleCalendarSync:
    """Google Calendar OAuth and synchronization service."""

    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    def __init__(self):
        """Initialize Google Calendar sync."""
        if not GOOGLE_CALENDAR_AVAILABLE:
            raise ImportError("Google Calendar API not available. Install: google-auth google-auth-oauthlib google-api-python-client")

        self.storage = CalendarStorageManager()
        self.credentials_path = os.getenv("GOOGLE_CALENDAR_CREDENTIALS", "./config/google_calendar_credentials.json")
        self.token_path = os.getenv("GOOGLE_CALENDAR_TOKEN", "./data/google_calendar_token.json")

    def authenticate(self, user_email: str) -> Tuple[bool, Optional[str]]:
        """
        Initiate OAuth flow for Google Calendar.

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            creds = None

            # Check if we have saved credentials
            token_path = Path(self.token_path)
            if token_path.exists():
                creds = Credentials.from_authorized_user_file(str(token_path), self.SCOPES)

            # If credentials are invalid or don't exist, run OAuth flow
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not Path(self.credentials_path).exists():
                        return False, f"Google Calendar credentials file not found at {self.credentials_path}"

                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                # Save the credentials for future use
                token_path.parent.mkdir(exist_ok=True)
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())

            # Save connection to storage
            connection = CalendarConnection(
                connection_id=f"google_{user_email}",
                provider="google",
                user_email=user_email,
                client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
                client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
                access_token=creds.token,
                refresh_token=creds.refresh_token if hasattr(creds, 'refresh_token') else None,
                token_expires_at=datetime.fromtimestamp(creds.expiry.timestamp()) if creds.expiry else None,
                scopes=self.SCOPES,
                is_connected=True,
                last_auth_at=datetime.now()
            )

            self.storage.save_connection(connection)

            return True, None

        except Exception as e:
            return False, f"Google Calendar authentication failed: {str(e)}"

    def fetch_events(
        self,
        source: CalendarSource,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[List[UnifiedEvent], Optional[str]]:
        """
        Fetch events from Google Calendar.

        Returns:
            Tuple of (events: List[UnifiedEvent], error_message: Optional[str])
        """
        try:
            # Load credentials
            token_path = Path(self.token_path)
            if not token_path.exists():
                return [], "Google Calendar not authenticated. Please run authenticate() first."

            creds = Credentials.from_authorized_user_file(str(token_path), self.SCOPES)

            # Build service
            service = build('calendar', 'v3', credentials=creds)

            # Set default date range
            if not start_date:
                start_date = datetime.now() - timedelta(days=source.sync_window_days)
            if not end_date:
                end_date = datetime.now() + timedelta(days=source.sync_window_days)

            # Fetch events
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_date.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                maxResults=250,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            google_events = events_result.get('items', [])

            # Convert to UnifiedEvent format
            unified_events = []
            for event in google_events:
                unified_event = self._convert_google_event(event, source.source_id)
                if unified_event:
                    unified_events.append(unified_event)

            # Save events to storage
            if unified_events:
                self.storage.save_events(unified_events)

                # Update source's last_sync
                source.last_sync = datetime.now()
                source.updated_at = datetime.now()
                self.storage.save_calendar_source(source)

            return unified_events, None

        except Exception as e:
            return [], f"Failed to fetch Google Calendar events: {str(e)}"

    def _convert_google_event(self, google_event: Dict[str, Any], source_id: str) -> Optional[UnifiedEvent]:
        """Convert Google Calendar event to UnifiedEvent format."""
        try:
            # Extract times
            start = google_event.get('start', {})
            end = google_event.get('end', {})

            # Handle all-day events
            if 'date' in start:
                start_time = datetime.fromisoformat(start['date'])
                end_time = datetime.fromisoformat(end['date'])
                all_day = True
            else:
                start_time = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
                all_day = False

            # Extract attendees
            attendees = []
            for attendee in google_event.get('attendees', []):
                if attendee.get('email'):
                    attendees.append(attendee['email'])

            # Extract organizer
            organizer = google_event.get('organizer', {}).get('email')

            # Extract recurrence
            is_recurring = 'recurrence' in google_event
            recurrence_rule = google_event.get('recurrence', [None])[0] if is_recurring else None

            # Extract status
            status_map = {
                'confirmed': 'confirmed',
                'tentative': 'tentative',
                'cancelled': 'cancelled'
            }
            status = status_map.get(google_event.get('status', 'confirmed'), 'confirmed')

            # Response status
            response_status = None
            if 'attendees' in google_event:
                for attendee in google_event['attendees']:
                    if attendee.get('self', False):
                        response_status = attendee.get('responseStatus')

            # Generate unique event ID
            event_id = f"{source_id}_{google_event['id']}"

            return UnifiedEvent(
                event_id=event_id,
                source_id=source_id,
                title=google_event.get('summary', 'Untitled Event'),
                description=google_event.get('description'),
                location=google_event.get('location'),
                start_time=start_time,
                end_time=end_time,
                all_day=all_day,
                timezone=start.get('timeZone', 'UTC'),
                attendees=attendees,
                organizer=organizer,
                is_recurring=is_recurring,
                recurrence_rule=recurrence_rule,
                status=status,
                response_status=response_status,
                original_event_id=google_event['id'],
                source_url=google_event.get('htmlLink'),
                raw_data=google_event
            )

        except Exception as e:
            print(f"Error converting Google event: {e}")
            return None


class MicrosoftCalendarSync:
    """Microsoft Outlook/365 Calendar OAuth and synchronization service."""

    SCOPES = ['Calendars.Read', 'Calendars.ReadWrite']

    def __init__(self):
        """Initialize Microsoft Calendar sync."""
        if not MICROSOFT_GRAPH_AVAILABLE:
            raise ImportError("Microsoft Graph API not available. Install: msal requests")

        self.storage = CalendarStorageManager()
        self.client_id = os.getenv("MICROSOFT_CLIENT_ID")
        self.client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")
        self.tenant_id = os.getenv("MICROSOFT_TENANT_ID", "common")
        self.redirect_uri = os.getenv("MICROSOFT_REDIRECT_URI", "http://localhost:8000/auth/microsoft/callback")

        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"

    def get_auth_url(self) -> str:
        """Get the authorization URL for Microsoft OAuth flow."""
        app = PublicClientApplication(
            self.client_id,
            authority=self.authority
        )

        flow = app.initiate_auth_code_flow(
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )

        return flow['auth_uri']

    def authenticate(self, auth_code: str, user_email: str) -> Tuple[bool, Optional[str]]:
        """
        Complete OAuth flow with authorization code.

        Args:
            auth_code: Authorization code from OAuth redirect
            user_email: User's email address

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            app = PublicClientApplication(
                self.client_id,
                authority=self.authority
            )

            # Exchange auth code for tokens
            result = app.acquire_token_by_auth_code_flow(
                auth_code_flow={'scopes': self.SCOPES},
                auth_response={'code': auth_code}
            )

            if 'access_token' in result:
                # Save connection to storage
                connection = CalendarConnection(
                    connection_id=f"microsoft_{user_email}",
                    provider="outlook",
                    user_email=user_email,
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    access_token=result['access_token'],
                    refresh_token=result.get('refresh_token'),
                    token_expires_at=datetime.now() + timedelta(seconds=result.get('expires_in', 3600)),
                    scopes=self.SCOPES,
                    is_connected=True,
                    last_auth_at=datetime.now()
                )

                self.storage.save_connection(connection)

                return True, None
            else:
                return False, f"Authentication failed: {result.get('error_description', 'Unknown error')}"

        except Exception as e:
            return False, f"Microsoft Calendar authentication failed: {str(e)}"

    def fetch_events(
        self,
        source: CalendarSource,
        user_email: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[List[UnifiedEvent], Optional[str]]:
        """
        Fetch events from Microsoft Calendar.

        Returns:
            Tuple of (events: List[UnifiedEvent], error_message: Optional[str])
        """
        try:
            # Get connection
            connection = self.storage.get_connection("outlook", user_email)
            if not connection or not connection.access_token:
                return [], "Microsoft Calendar not authenticated."

            # Check if token is expired
            if connection.token_expires_at and datetime.now() >= connection.token_expires_at:
                # TODO: Implement token refresh
                return [], "Access token expired. Please re-authenticate."

            # Set default date range
            if not start_date:
                start_date = datetime.now() - timedelta(days=source.sync_window_days)
            if not end_date:
                end_date = datetime.now() + timedelta(days=source.sync_window_days)

            # Build Graph API request
            graph_url = "https://graph.microsoft.com/v1.0/me/events"
            headers = {
                'Authorization': f'Bearer {connection.access_token}',
                'Content-Type': 'application/json'
            }
            params = {
                '$select': 'subject,body,start,end,location,attendees,organizer,isAllDay,recurrence,responseStatus',
                '$filter': f"start/dateTime ge '{start_date.isoformat()}' and start/dateTime le '{end_date.isoformat()}'",
                '$orderby': 'start/dateTime',
                '$top': 250
            }

            response = requests.get(graph_url, headers=headers, params=params)
            response.raise_for_status()

            ms_events = response.json().get('value', [])

            # Convert to UnifiedEvent format
            unified_events = []
            for event in ms_events:
                unified_event = self._convert_microsoft_event(event, source.source_id)
                if unified_event:
                    unified_events.append(unified_event)

            # Save events to storage
            if unified_events:
                self.storage.save_events(unified_events)

                # Update source's last_sync
                source.last_sync = datetime.now()
                source.updated_at = datetime.now()
                self.storage.save_calendar_source(source)

            return unified_events, None

        except Exception as e:
            return [], f"Failed to fetch Microsoft Calendar events: {str(e)}"

    def _convert_microsoft_event(self, ms_event: Dict[str, Any], source_id: str) -> Optional[UnifiedEvent]:
        """Convert Microsoft Calendar event to UnifiedEvent format."""
        try:
            # Extract times
            start = ms_event['start']
            end = ms_event['end']

            start_time = datetime.fromisoformat(start['dateTime'])
            end_time = datetime.fromisoformat(end['dateTime'])
            all_day = ms_event.get('isAllDay', False)

            # Extract attendees
            attendees = []
            for attendee in ms_event.get('attendees', []):
                if attendee.get('emailAddress', {}).get('address'):
                    attendees.append(attendee['emailAddress']['address'])

            # Extract organizer
            organizer = ms_event.get('organizer', {}).get('emailAddress', {}).get('address')

            # Extract recurrence
            is_recurring = 'recurrence' in ms_event and ms_event['recurrence'] is not None
            recurrence_rule = None  # Would need to convert MS recurrence format to RRULE

            # Extract status and response
            status = 'confirmed'  # Microsoft doesn't have exact equivalent
            response_status = ms_event.get('responseStatus', {}).get('response')

            # Generate unique event ID
            event_id = f"{source_id}_{ms_event['id']}"

            return UnifiedEvent(
                event_id=event_id,
                source_id=source_id,
                title=ms_event.get('subject', 'Untitled Event'),
                description=ms_event.get('body', {}).get('content'),
                location=ms_event.get('location', {}).get('displayName'),
                start_time=start_time,
                end_time=end_time,
                all_day=all_day,
                timezone=start.get('timeZone', 'UTC'),
                attendees=attendees,
                organizer=organizer,
                is_recurring=is_recurring,
                recurrence_rule=recurrence_rule,
                status=status,
                response_status=response_status,
                original_event_id=ms_event['id'],
                source_url=ms_event.get('webLink'),
                raw_data=ms_event
            )

        except Exception as e:
            print(f"Error converting Microsoft event: {e}")
            return None


class ICalSync:
    """iCal/ICS file import service."""

    def __init__(self):
        """Initialize iCal sync."""
        if not ICAL_AVAILABLE:
            raise ImportError("iCal library not available. Install: icalendar")

        self.storage = CalendarStorageManager()

    def import_ical_file(
        self,
        source: CalendarSource,
        file_path: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[List[UnifiedEvent], Optional[str]]:
        """
        Import events from iCal/ICS file.

        Args:
            source: CalendarSource configuration
            file_path: Path to .ics file
            start_date: Optional filter start date
            end_date: Optional filter end date

        Returns:
            Tuple of (events: List[UnifiedEvent], error_message: Optional[str])
        """
        try:
            # Read iCal file
            with open(file_path, 'rb') as f:
                cal = ICalendar.from_ical(f.read())

            # Set default date range
            if not start_date:
                start_date = datetime.now() - timedelta(days=source.sync_window_days)
            if not end_date:
                end_date = datetime.now() + timedelta(days=source.sync_window_days)

            # Extract events
            unified_events = []

            for component in cal.walk('VEVENT'):
                unified_event = self._convert_ical_event(component, source.source_id, start_date, end_date)
                if unified_event:
                    unified_events.append(unified_event)

            # Save events to storage
            if unified_events:
                self.storage.save_events(unified_events)

                # Update source's last_sync
                source.last_sync = datetime.now()
                source.updated_at = datetime.now()
                self.storage.save_calendar_source(source)

            return unified_events, None

        except Exception as e:
            return [], f"Failed to import iCal file: {str(e)}"

    def _convert_ical_event(
        self,
        ical_event: Any,
        source_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[UnifiedEvent]:
        """Convert iCal event to UnifiedEvent format."""
        try:
            # Extract times
            dtstart = ical_event.get('dtstart').dt
            dtend = ical_event.get('dtend').dt if ical_event.get('dtend') else dtstart

            # Handle date vs datetime
            if isinstance(dtstart, datetime):
                start_time = dtstart
                all_day = False
            else:
                start_time = datetime.combine(dtstart, datetime.min.time())
                all_day = True

            if isinstance(dtend, datetime):
                end_time = dtend
            else:
                end_time = datetime.combine(dtend, datetime.min.time())

            # Filter by date range
            if start_time < start_date or start_time > end_date:
                return None

            # Extract other fields
            title = str(ical_event.get('summary', 'Untitled Event'))
            description = str(ical_event.get('description', '')) if ical_event.get('description') else None
            location = str(ical_event.get('location', '')) if ical_event.get('location') else None

            # Extract organizer
            organizer = None
            if ical_event.get('organizer'):
                organizer_str = str(ical_event.get('organizer'))
                if 'MAILTO:' in organizer_str:
                    organizer = organizer_str.split('MAILTO:')[1].strip()

            # Extract attendees
            attendees = []
            if ical_event.get('attendee'):
                attendee_list = ical_event.get('attendee')
                if not isinstance(attendee_list, list):
                    attendee_list = [attendee_list]

                for attendee in attendee_list:
                    attendee_str = str(attendee)
                    if 'MAILTO:' in attendee_str:
                        attendees.append(attendee_str.split('MAILTO:')[1].strip())

            # Recurrence
            is_recurring = ical_event.get('rrule') is not None
            recurrence_rule = str(ical_event.get('rrule')) if is_recurring else None

            # Status
            status_map = {
                'CONFIRMED': 'confirmed',
                'TENTATIVE': 'tentative',
                'CANCELLED': 'cancelled'
            }
            status = status_map.get(str(ical_event.get('status', 'CONFIRMED')).upper(), 'confirmed')

            # Generate unique event ID
            original_uid = str(ical_event.get('uid', hashlib.md5(title.encode()).hexdigest()))
            event_id = f"{source_id}_{original_uid}"

            return UnifiedEvent(
                event_id=event_id,
                source_id=source_id,
                title=title,
                description=description,
                location=location,
                start_time=start_time,
                end_time=end_time,
                all_day=all_day,
                timezone='UTC',  # iCal events default to UTC
                attendees=attendees,
                organizer=organizer,
                is_recurring=is_recurring,
                recurrence_rule=recurrence_rule,
                status=status,
                original_event_id=original_uid,
                raw_data={'ical_component': str(ical_event)}
            )

        except Exception as e:
            print(f"Error converting iCal event: {e}")
            return None
