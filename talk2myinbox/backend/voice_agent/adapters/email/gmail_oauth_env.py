"""
Gmail OAuth2 Handler that uses credentials from environment variables
Works with refresh tokens without requiring interactive browser flow
"""

import os
from pathlib import Path
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv


# Gmail API scopes - use standard modify scope (compatible with most tokens)
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]


class GmailOAuthEnvHandler:
    """
    Handles Gmail OAuth2 using credentials from environment variables.
    This avoids the need for interactive browser-based authentication.
    """

    def __init__(self):
        # Load environment variables
        load_dotenv()

        self.client_id = os.getenv("GMAIL_CLIENT_ID")
        self.client_secret = os.getenv("GMAIL_CLIENT_SECRET")
        self.refresh_token = os.getenv("GMAIL_REFRESH_TOKEN")

        self.creds: Optional[Credentials] = None

    def get_credentials(self) -> Credentials:
        """
        Get valid Gmail API credentials from environment variables.

        Returns:
            Credentials object for Gmail API

        Raises:
            ValueError: If environment variables are missing
            Exception: If authentication fails
        """
        # Validate environment variables
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            missing = []
            if not self.client_id:
                missing.append("GMAIL_CLIENT_ID")
            if not self.client_secret:
                missing.append("GMAIL_CLIENT_SECRET")
            if not self.refresh_token:
                missing.append("GMAIL_REFRESH_TOKEN")

            raise ValueError(
                f"Missing Gmail credentials in .env file: {', '.join(missing)}\n\n"
                "Please add these to your .env file:\n"
                "GMAIL_CLIENT_ID=your_client_id\n"
                "GMAIL_CLIENT_SECRET=your_client_secret\n"
                "GMAIL_REFRESH_TOKEN=your_refresh_token\n"
            )

        # Create credentials from refresh token
        self.creds = Credentials(
            token=None,  # Access token will be auto-generated from refresh token
            refresh_token=self.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=SCOPES
        )

        # Refresh the credentials to get a valid access token
        print("Refreshing Gmail access token from refresh token...")
        try:
            self.creds.refresh(Request())
            print("SUCCESS: Gmail credentials refreshed successfully")
        except Exception as e:
            print(f"ERROR refreshing credentials: {e}")
            raise Exception(
                f"Failed to refresh Gmail credentials: {e}\n\n"
                "Your refresh token might be expired or invalid. "
                "Please check your GMAIL_REFRESH_TOKEN in .env"
            )

        return self.creds

    def get_gmail_service(self):
        """
        Get authenticated Gmail API service.

        Returns:
            Gmail API service object
        """
        creds = self.get_credentials()
        service = build('gmail', 'v1', credentials=creds)
        return service
