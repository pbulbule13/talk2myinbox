"""
Google Calendar OAuth Handler (Environment Variable Based)
Uses OAuth credentials from environment variables (same as Gmail)
"""

import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


class GoogleCalendarOAuthEnvHandler:
    """
    Handle OAuth authentication for Google Calendar using environment variables.
    Reuses the same credentials as Gmail.
    """

    def __init__(self):
        # Load credentials from environment
        self.client_id = os.getenv("CALENDAR_CLIENT_ID") or os.getenv("GMAIL_CLIENT_ID")
        self.client_secret = os.getenv("CALENDAR_CLIENT_SECRET") or os.getenv("GMAIL_CLIENT_SECRET")
        self.refresh_token = os.getenv("CALENDAR_REFRESH_TOKEN") or os.getenv("GMAIL_REFRESH_TOKEN")

        if not all([self.client_id, self.client_secret, self.refresh_token]):
            raise ValueError("Google Calendar OAuth credentials not found in environment variables")

    def get_calendar_service(self):
        """
        Build and return an authenticated Google Calendar API service.
        """
        # Create credentials object from environment variables
        creds = Credentials(
            token=None,  # Will be refreshed
            refresh_token=self.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=["https://www.googleapis.com/auth/calendar"]
        )

        # Refresh the access token
        print("Refreshing Google Calendar access token...")
        creds.refresh(Request())
        print("SUCCESS: Google Calendar credentials refreshed successfully")

        # Build and return the Calendar service
        service = build('calendar', 'v3', credentials=creds)
        return service
