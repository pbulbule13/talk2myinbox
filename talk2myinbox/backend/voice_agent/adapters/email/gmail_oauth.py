"""
Gmail OAuth2 Authentication Handler
Handles Gmail API authentication with OAuth2
"""

import os
import pickle
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# Gmail API scopes - what permissions we need
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose'
]


class GmailOAuthHandler:
    """
    Handles Gmail OAuth2 authentication flow and credential management.

    Usage:
        handler = GmailOAuthHandler()
        service = handler.get_gmail_service()
    """

    def __init__(
        self,
        credentials_path: str = "./config/gmail_credentials.json",
        token_path: str = "./config/gmail_token.pickle"
    ):
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.creds: Optional[Credentials] = None

    def get_credentials(self) -> Credentials:
        """
        Get valid Gmail API credentials.

        Returns:
            Credentials object for Gmail API

        Raises:
            FileNotFoundError: If credentials.json is not found
            Exception: If authentication fails
        """
        # Check if we have saved credentials
        if self.token_path.exists():
            with open(self.token_path, 'rb') as token:
                self.creds = pickle.load(token)

        # If credentials don't exist or are invalid, get new ones
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                # Refresh expired credentials
                print("Refreshing Gmail credentials...")
                self.creds.refresh(Request())
            else:
                # Run OAuth2 flow to get new credentials
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"Gmail credentials file not found: {self.credentials_path}\n\n"
                        "To set up Gmail API:\n"
                        "1. Go to https://console.cloud.google.com/\n"
                        "2. Create a new project or select existing\n"
                        "3. Enable Gmail API\n"
                        "4. Create OAuth 2.0 credentials (Desktop app)\n"
                        "5. Download credentials and save to: {}\n".format(self.credentials_path)
                    )

                print("Starting Gmail OAuth2 flow...")
                print("A browser window will open for authorization.")

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path),
                    SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            # Save credentials for future use
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, 'wb') as token:
                pickle.dump(self.creds, token)
            print("✅ Gmail credentials saved successfully")

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

    def revoke_credentials(self):
        """Revoke and delete saved credentials"""
        if self.token_path.exists():
            self.token_path.unlink()
            print("✅ Gmail credentials revoked")
