"""
Google Calendar API Adapter - REAL Implementation
Fetches actual calendar data from Google Calendar
"""

from .base import BaseCalendarAdapter
from .google_calendar_oauth_env import GoogleCalendarOAuthEnvHandler
from typing import Any
from datetime import datetime, timedelta
import os


class GoogleCalendarAdapter(BaseCalendarAdapter):
    """
    Google Calendar adapter using Google Calendar API with real data.
    """

    def __init__(self, credentials_path: str | None = None):
        from dotenv import load_dotenv
        load_dotenv(override=True)

        # Check for CALENDAR_MOCK_MODE
        calendar_mock_mode = os.getenv("CALENDAR_MOCK_MODE", "false").lower() == "true"

        self.use_mock = calendar_mock_mode
        print(f"[GoogleCalendarAdapter] Initializing - use_mock={self.use_mock}")

        # Initialize OAuth handler
        try:
            self.oauth_handler = GoogleCalendarOAuthEnvHandler()
            self._service = None
        except Exception as e:
            print(f"[Calendar] WARNING: Could not initialize OAuth: {e}")
            self.use_mock = True

    @property
    def service(self):
        """Lazy load Google Calendar service"""
        if self.use_mock:
            return None

        if self._service is None:
            try:
                print("[Calendar Service] Initializing Google Calendar API service...")
                self._service = self.oauth_handler.get_calendar_service()
                print("[Calendar Service] SUCCESS: Google Calendar API service initialized")
            except Exception as e:
                print(f"[Calendar Service] ERROR: Failed to initialize: {e}")
                self.use_mock = True
                return None

        return self._service

    async def get_events(
        self,
        start_time: datetime,
        end_time: datetime,
        calendar_id: str = "primary"
    ) -> list[dict[str, Any]]:
        """Fetch events from Google Calendar"""

        if self.use_mock or not self.service:
            print("[Calendar] Using MOCK data (credentials not configured)")
            return []  # Return empty instead of mock events

        try:
            print(f"[Calendar] Fetching events from {start_time} to {end_time}")

            # Call Google Calendar API
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=start_time.isoformat(),
                timeMax=end_time.isoformat(),
                singleEvents=True,
                orderBy='startTime',
                maxResults=50
            ).execute()

            events = events_result.get('items', [])
            print(f"[Calendar] Fetched {len(events)} real calendar events")

            # Format events for our system
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))

                formatted_events.append({
                    "event_id": event['id'],
                    "title": event.get('summary', 'Untitled Event'),
                    "description": event.get('description', ''),
                    "start": start,
                    "end": end,
                    "attendees": [att.get('email') for att in event.get('attendees', [])],
                    "organizer": event.get('organizer', {}).get('email', ''),
                    "status": event.get('status', 'confirmed'),
                    "location": event.get('location', '')
                })

            return formatted_events

        except Exception as e:
            print(f"[Calendar] Error fetching events: {e}")
            return []

    async def get_event(self, event_id: str) -> dict[str, Any]:
        """Get event details from Google Calendar"""

        if self.use_mock or not self.service:
            return {}

        try:
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()

            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))

            return {
                "event_id": event['id'],
                "title": event.get('summary', 'Untitled Event'),
                "description": event.get('description', ''),
                "start": start,
                "end": end,
                "attendees": [att.get('email') for att in event.get('attendees', [])],
                "organizer": event.get('organizer', {}).get('email', ''),
                "status": event.get('status', 'confirmed'),
                "location": event.get('location', '')
            }

        except Exception as e:
            print(f"[Calendar] Error fetching event {event_id}: {e}")
            return {}

    async def create_event(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        attendees: list[str] | None = None,
        description: str | None = None,
        location: str | None = None,
        calendar_id: str = "primary"
    ) -> dict[str, Any]:
        """Create event in Google Calendar"""

        if self.use_mock or not self.service:
            print("[Calendar] MOCK MODE: Cannot create real events")
            return {"success": False, "error": "Calendar not configured"}

        try:
            event = {
                'summary': title,
                'description': description or '',
                'location': location or '',
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }

            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]

            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()

            print(f"[Calendar] Created event: {created_event.get('htmlLink')}")

            return {
                "success": True,
                "event_id": created_event['id'],
                "link": created_event.get('htmlLink')
            }

        except Exception as e:
            print(f"[Calendar] Error creating event: {e}")
            return {"success": False, "error": str(e)}

    async def update_event(
        self,
        event_id: str,
        title: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        attendees: list[str] | None = None,
        description: str | None = None,
        location: str | None = None,
        calendar_id: str = "primary"
    ) -> bool:
        """Update event in Google Calendar"""

        if self.use_mock or not self.service:
            return False

        try:
            # Get existing event
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

            # Update fields
            if title:
                event['summary'] = title
            if description is not None:
                event['description'] = description
            if location is not None:
                event['location'] = location
            if start_time:
                event['start'] = {'dateTime': start_time.isoformat(), 'timeZone': 'UTC'}
            if end_time:
                event['end'] = {'dateTime': end_time.isoformat(), 'timeZone': 'UTC'}
            if attendees is not None:
                event['attendees'] = [{'email': email} for email in attendees]

            # Update event
            self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()

            print(f"[Calendar] Updated event: {event_id}")
            return True

        except Exception as e:
            print(f"[Calendar] Error updating event: {e}")
            return False

    async def delete_event(self, event_id: str, calendar_id: str = "primary") -> bool:
        """Delete event from Google Calendar"""

        if self.use_mock or not self.service:
            return False

        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

            print(f"[Calendar] Deleted event: {event_id}")
            return True

        except Exception as e:
            print(f"[Calendar] Error deleting event: {e}")
            return False

    async def rsvp_event(
        self,
        event_id: str,
        response: str,
        calendar_id: str = "primary"
    ) -> bool:
        """RSVP to calendar event"""

        if self.use_mock or not self.service:
            return False

        try:
            # Get event
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

            # Update attendee response
            # (This is simplified - in production you'd find the specific attendee)
            self.service.events().patch(
                calendarId=calendar_id,
                eventId=event_id,
                body={
                    'attendees': [
                        {'email': att['email'], 'responseStatus': response}
                        for att in event.get('attendees', [])
                    ]
                }
            ).execute()

            print(f"[Calendar] RSVP'd to event {event_id}: {response}")
            return True

        except Exception as e:
            print(f"[Calendar] Error RSVPing to event: {e}")
            return False

    async def accept_event(self, event_id: str) -> dict[str, Any]:
        """Accept a calendar invite"""
        result = await self.rsvp_event(event_id, "accepted")
        return {"success": result, "event_id": event_id, "response": "accepted"}

    async def decline_event(self, event_id: str, message: str | None = None) -> dict[str, Any]:
        """Decline a calendar invite"""
        result = await self.rsvp_event(event_id, "declined")
        return {"success": result, "event_id": event_id, "response": "declined"}

    async def propose_alternative(
        self,
        event_id: str,
        alternative_times: list[dict],
        message: str | None = None
    ) -> dict[str, Any]:
        """Propose alternative times for an event"""
        # Google Calendar API doesn't have direct support for proposing alternative times
        # This would typically be done via email or calendar app
        return {
            "success": False,
            "error": "Proposing alternative times not supported via API",
            "event_id": event_id
        }

    async def check_availability(
        self,
        start_time: datetime,
        end_time: datetime,
        calendar_id: str = "primary"
    ) -> dict[str, Any]:
        """Check availability for a time slot"""
        if self.use_mock or not self.service:
            return {"available": True, "conflicting_events": []}

        try:
            # Get events in the time range
            events = await self.get_events(start_time, end_time, calendar_id)

            # Check for conflicts
            conflicting_events = []
            for event in events:
                if event.get('status') != 'cancelled':
                    conflicting_events.append({
                        "title": event.get('title', 'Untitled'),
                        "start": event.get('start', ''),
                        "end": event.get('end', '')
                    })

            available = len(conflicting_events) == 0

            return {
                "available": available,
                "conflicting_events": conflicting_events
            }

        except Exception as e:
            print(f"[Calendar] Error checking availability: {e}")
            return {"available": True, "conflicting_events": [], "error": str(e)}
