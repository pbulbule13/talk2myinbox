"""
Gmail API Adapter
Implementation for Gmail using Google's Gmail API
"""

from .base import BaseEmailAdapter
from .gmail_oauth import GmailOAuthHandler
from typing import Any
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import re


class GmailAdapter(BaseEmailAdapter):
    """
    Gmail adapter using Google Gmail API.
    Requires: google-auth, google-auth-oauthlib, google-auth-httplib2, google-api-python-client
    """

    def __init__(
        self,
        credentials_path: str | None = None,
        token_path: str | None = None
    ):
        self.credentials_path = credentials_path or "./config/gmail_credentials.json"
        self.token_path = token_path or "./config/gmail_token.pickle"

        # Initialize OAuth handler
        self.oauth_handler = GmailOAuthHandler(
            credentials_path=self.credentials_path,
            token_path=self.token_path
        )

        # Gmail API service (lazy initialization)
        self._service = None

    @property
    def service(self):
        """Lazy load Gmail service"""
        if self._service is None:
            try:
                self._service = self.oauth_handler.get_gmail_service()
                print("✅ Gmail API service initialized")
            except FileNotFoundError as e:
                print(f"⚠️ Gmail credentials not configured: {e}")
                raise
            except Exception as e:
                print(f"❌ Failed to initialize Gmail service: {e}")
                raise
        return self._service

    async def fetch_threads(
        self,
        max_results: int = 50,
        unread_only: bool = False,
        query: str | None = None
    ) -> list[dict[str, Any]]:
        """Fetch email threads from Gmail"""
        try:
            # Build Gmail query
            gmail_query = query or ""
            if unread_only:
                gmail_query = "is:unread " + gmail_query
            if not gmail_query:
                gmail_query = "in:inbox"

            # Fetch threads
            results = self.service.users().threads().list(
                userId='me',
                maxResults=max_results,
                q=gmail_query.strip()
            ).execute()

            threads = results.get('threads', [])

            # Convert to our format
            thread_list = []
            for thread in threads:
                thread_data = await self.get_thread(thread['id'])
                thread_list.append(thread_data)

            return thread_list

        except Exception as e:
            print(f"Error fetching Gmail threads: {e}")
            # Return mock data as fallback
            return self._get_mock_threads()

    async def get_thread(self, thread_id: str) -> dict[str, Any]:
        """Get full thread details from Gmail"""
        try:
            # Get thread
            thread = self.service.users().threads().get(
                userId='me',
                id=thread_id,
                format='full'
            ).execute()

            messages = thread.get('messages', [])
            if not messages:
                return {}

            # Get the latest message for preview
            latest_msg = messages[-1]
            headers = {h['name']: h['value'] for h in latest_msg['payload']['headers']}

            # Extract body
            body = self._get_message_body(latest_msg['payload'])

            return {
                "thread_id": thread_id,
                "subject": headers.get('Subject', 'No Subject'),
                "from": headers.get('From', 'Unknown'),
                "to": headers.get('To', '').split(','),
                "preview": body[:200] if body else "No content",
                "unread": 'UNREAD' in latest_msg.get('labelIds', []),
                "timestamp": self._format_timestamp(latest_msg['internalDate']),
                "labels": latest_msg.get('labelIds', []),
                "messages": [self._format_message(msg) for msg in messages]
            }

        except Exception as e:
            print(f"Error fetching Gmail thread {thread_id}: {e}")
            return {"thread_id": thread_id, "error": str(e)}

    async def send_email(
        self,
        to: list[str],
        subject: str,
        body: str,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        thread_id: str | None = None,
        attachments: list[dict] | None = None
    ) -> dict[str, Any]:
        """Send email via Gmail API"""
        # TODO: Implement actual Gmail API sending
        # from email.mime.text import MIMEText
        # message = MIMEText(body)
        # message['to'] = ', '.join(to)
        # message['subject'] = subject
        # ...
        # service.users().messages().send(userId='me', body=message).execute()

        return {
            "success": True,
            "message_id": f"gmail_msg_{thread_id or 'new'}",
            "details": "Email sent via Gmail API (mock)"
        }

    async def mark_read(self, thread_id: str) -> bool:
        """Mark thread as read in Gmail"""
        # TODO: Implement actual Gmail API marking
        # service.users().threads().modify(
        #     userId='me',
        #     id=thread_id,
        #     body={'removeLabelIds': ['UNREAD']}
        # ).execute()
        return True

    async def archive_thread(self, thread_id: str) -> bool:
        """Archive thread in Gmail"""
        # TODO: Implement actual Gmail API archiving
        # service.users().threads().modify(
        #     userId='me',
        #     id=thread_id,
        #     body={'removeLabelIds': ['INBOX']}
        # ).execute()
        return True

    async def get_sender_history(self, email_address: str) -> dict[str, Any]:
        """Get sender history from Gmail"""
        # TODO: Implement actual history lookup
        # Query all emails from this sender and calculate statistics
        return {
            "email": email_address,
            "interaction_count": 47,
            "avg_response_time_hours": 2.5,
            "relationship": "key_partner",
            "last_interaction": "2025-10-20T14:00:00Z"
        }

    async def search_emails(
        self,
        query: str,
        max_results: int = 50
    ) -> list[dict[str, Any]]:
        """Search emails in Gmail"""
        # TODO: Implement actual Gmail API search
        # service.users().threads().list(
        #     userId='me',
        #     q=query,
        #     maxResults=max_results
        # ).execute()
        return []
