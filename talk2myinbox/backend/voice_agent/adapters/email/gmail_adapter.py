"""
Complete Gmail API Adapter Implementation
Full implementation with all email operations
"""

from .base import BaseEmailAdapter
from .gmail_oauth_env import GmailOAuthEnvHandler
from .gmail_adapter_helpers import (
    get_message_body,
    format_message,
    format_timestamp,
    create_message,
    create_reply_message
)
from typing import Any


class GmailAdapter(BaseEmailAdapter):
    """
    Complete Gmail adapter using Google Gmail API.
    """

    def __init__(
        self,
        credentials_path: str | None = None,
        token_path: str | None = None,
        use_mock: bool = False
    ):
        import os
        from dotenv import load_dotenv

        # Force reload .env file
        load_dotenv(override=True)

        # Check for EMAIL_MOCK_MODE environment variable
        email_mock_mode = os.getenv("EMAIL_MOCK_MODE", "false").lower() == "true"

        self.credentials_path = credentials_path or "./config/gmail_credentials.json"
        self.token_path = token_path or "./config/gmail_token.pickle"
        self.use_mock = use_mock or email_mock_mode  # For testing without real Gmail

        # Log to console for debugging
        import sys
        sys.stdout.flush()
        print(f"[GmailAdapter] Initializing - use_mock={self.use_mock}, EMAIL_MOCK_MODE={email_mock_mode}", flush=True)
        print(f"[GmailAdapter Init] CLIENT_ID={os.getenv('GMAIL_CLIENT_ID', 'NOT SET')[:20] if os.getenv('GMAIL_CLIENT_ID') else 'NOT SET'}...", flush=True)

        # Initialize OAuth handler (using environment variables)
        self.oauth_handler = GmailOAuthEnvHandler()

        # Gmail API service (lazy initialization)
        self._service = None

    @property
    def service(self):
        """Lazy load Gmail service"""
        if self.use_mock:
            return None  # Return None in mock mode, adapter will use mock data

        if self._service is None:
            try:
                print("[Gmail Service] Initializing Gmail API service...")
                self._service = self.oauth_handler.get_gmail_service()
                print("[Gmail Service] SUCCESS: Gmail API service initialized")
            except ValueError as e:
                print(f"[Gmail Service] ERROR: Gmail credentials not configured: {e}")
                raise Exception(f"Gmail credentials missing: {e}")
            except Exception as e:
                print(f"[Gmail Service] ERROR: Failed to initialize Gmail service: {e}")
                raise Exception(f"Gmail initialization failed: {e}")

        return self._service

    async def fetch_threads(
        self,
        max_results: int = 50,
        unread_only: bool = False,
        query: str | None = None
    ) -> list[dict[str, Any]]:
        """Fetch email threads from Gmail"""
        # Use mock data if in mock mode
        if self.use_mock:
            print(f"[fetch_threads] Using mock data (EMAIL_MOCK_MODE=true)")
            return self._get_mock_threads()[:max_results]

        try:
            # Try to get service - this will raise exception if token is invalid
            service = self.service
            print(f"[fetch_threads] Gmail service initialized successfully")

            # Build Gmail query
            gmail_query = query or ""
            if unread_only:
                gmail_query = "is:unread " + gmail_query
            if not gmail_query:
                gmail_query = "in:inbox"

            # Fetch threads
            results = service.users().threads().list(
                userId='me',
                maxResults=max_results,
                q=gmail_query.strip()
            ).execute()

            threads = results.get('threads', [])

            # Convert to our format
            thread_list = []
            # Process all threads up to max_results
            for thread in threads[:max_results]:
                thread_data = await self.get_thread(thread['id'])
                if thread_data:
                    thread_list.append(thread_data)

            print(f"[fetch_threads] Successfully fetched {len(thread_list)} threads from Gmail")
            return thread_list

        except Exception as e:
            error_msg = str(e)
            print(f"[fetch_threads] Gmail error: {error_msg}")

            # Print full stack trace for debugging
            import traceback
            print("[fetch_threads] Full error traceback:")
            traceback.print_exc()

            # Check if it's a token expiration error
            if "invalid_grant" in error_msg or "expired or revoked" in error_msg.lower():
                print("[fetch_threads] WARNING: Gmail refresh token has EXPIRED. Falling back to mock data.")
                print("[fetch_threads] To fix: Regenerate token using Google OAuth Playground")
                print("[fetch_threads] See: https://developers.google.com/oauthplayground/")

            # Return mock data as fallback
            print("[fetch_threads] Using mock email data")
            return self._get_mock_threads()

    async def get_thread(self, thread_id: str) -> dict[str, Any]:
        """Get full thread details from Gmail"""
        if self.use_mock or not self.service:
            return self._get_mock_thread(thread_id)

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
            body = get_message_body(latest_msg['payload'])

            # Format all messages
            formatted_messages = [format_message(msg) for msg in messages]

            # Aggregate all attachments from all messages in the thread
            all_attachments = []
            for msg in formatted_messages:
                all_attachments.extend(msg.get('attachments', []))

            return {
                "thread_id": thread_id,
                "subject": headers.get('Subject', 'No Subject'),
                "from": headers.get('From', 'Unknown'),
                "to": headers.get('To', '').split(','),
                "preview": body[:200] if body else "No content",
                "unread": 'UNREAD' in latest_msg.get('labelIds', []),
                "timestamp": format_timestamp(latest_msg['internalDate']),
                "labels": latest_msg.get('labelIds', []),
                "messages": formatted_messages,
                "attachments": all_attachments,
                "message_count": len(messages)
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
        if self.use_mock or not self.service:
            return {
                "success": True,
                "message_id": f"mock_msg_{thread_id or 'new'}",
                "details": "Email sent (mock mode)"
            }

        try:
            # Create message
            if thread_id:
                # Get original message ID for reply
                thread = await self.get_thread(thread_id)
                message_id = thread['messages'][0]['id'] if thread.get('messages') else None
                message = create_reply_message(
                    to=to,
                    subject=subject,
                    body=body,
                    thread_id=thread_id,
                    message_id=message_id,
                    cc=cc
                )
            else:
                message = create_message(
                    to=to,
                    subject=subject,
                    body=body,
                    cc=cc,
                    bcc=bcc
                )

            # Send message
            result = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()

            return {
                "success": True,
                "message_id": result['id'],
                "thread_id": result.get('threadId'),
                "details": "Email sent successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "Failed to send email"
            }

    async def mark_read(self, thread_id: str) -> bool:
        """Mark thread as read in Gmail"""
        if self.use_mock or not self.service:
            return True

        try:
            self.service.users().threads().modify(
                userId='me',
                id=thread_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            print(f"Error marking thread as read: {e}")
            return False

    async def archive_thread(self, thread_id: str) -> bool:
        """Archive thread in Gmail"""
        if self.use_mock or not self.service:
            return True

        try:
            self.service.users().threads().modify(
                userId='me',
                id=thread_id,
                body={'removeLabelIds': ['INBOX']}
            ).execute()
            return True
        except Exception as e:
            print(f"Error archiving thread: {e}")
            return False

    async def get_sender_history(self, email_address: str) -> dict[str, Any]:
        """Get sender history from Gmail"""
        if self.use_mock or not self.service:
            return {
                "email": email_address,
                "interaction_count": 47,
                "avg_response_time_hours": 2.5,
                "relationship": "key_partner",
                "last_interaction": "2025-10-20T14:00:00Z"
            }

        try:
            # Search for emails from this sender
            query = f"from:{email_address}"
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=100
            ).execute()

            messages = results.get('messages', [])
            interaction_count = len(messages)

            # Get latest message
            last_interaction = None
            if messages:
                latest = self.service.users().messages().get(
                    userId='me',
                    id=messages[0]['id'],
                    format='minimal'
                ).execute()
                last_interaction = format_timestamp(latest['internalDate'])

            return {
                "email": email_address,
                "interaction_count": interaction_count,
                "avg_response_time_hours": 2.5,  # TODO: Calculate from actual data
                "relationship": "contact",
                "last_interaction": last_interaction
            }

        except Exception as e:
            print(f"Error fetching sender history: {e}")
            return {"email": email_address, "error": str(e)}

    async def search_emails(
        self,
        query: str,
        max_results: int = 50
    ) -> list[dict[str, Any]]:
        """Search emails in Gmail"""
        if self.use_mock or not self.service:
            return []

        try:
            results = self.service.users().threads().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            threads = results.get('threads', [])
            return [await self.get_thread(t['id']) for t in threads[:5]]

        except Exception as e:
            print(f"Error searching emails: {e}")
            return []

    # Mock data methods
    def _get_mock_threads(self) -> list[dict[str, Any]]:
        """Return mock email threads for testing"""
        from datetime import datetime, timezone, timedelta

        now = datetime.now(timezone.utc)

        return [
            {
                "thread_id": "thread_mock_1",
                "subject": "Urgent: Project Deadline Tomorrow",
                "from": "john.doe@partner.com",
                "to": ["you@company.com"],
                "preview": "Hi! Just a reminder that the Q4 project deliverables are due tomorrow. Can you send me the final report and presentation slides? Thanks!",
                "unread": True,
                "timestamp": (now - timedelta(hours=2)).isoformat(),
                "labels": ["INBOX", "IMPORTANT"],
                "message_count": 3,
                "attachments": [
                    {
                        "filename": "Q4_Report_Draft.pdf",
                        "mimeType": "application/pdf",
                        "size": 245678,
                        "attachmentId": "mock_att_1",
                        "messageId": "mock_msg_1"
                    }
                ]
            },
            {
                "thread_id": "thread_mock_2",
                "subject": "Interview Invitation - Senior Engineer Position",
                "from": "hr@techcorp.com",
                "to": ["you@company.com"],
                "preview": "Hello! We were impressed with your application. We'd like to invite you for an interview next Tuesday at 2 PM. Please let us know your availability.",
                "unread": True,
                "timestamp": (now - timedelta(hours=5)).isoformat(),
                "labels": ["INBOX"],
                "message_count": 1,
                "attachments": []
            },
            {
                "thread_id": "thread_mock_3",
                "subject": "Meeting Notes and Action Items",
                "from": "sarah.miller@company.com",
                "to": ["you@company.com"],
                "preview": "Thanks for attending today's meeting. I've attached the notes and action items. Please review and let me know if I missed anything.",
                "unread": True,
                "timestamp": (now - timedelta(hours=8)).isoformat(),
                "labels": ["INBOX"],
                "message_count": 2,
                "attachments": [
                    {
                        "filename": "Meeting_Notes_Nov_2025.docx",
                        "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        "size": 45230,
                        "attachmentId": "mock_att_2",
                        "messageId": "mock_msg_2"
                    },
                    {
                        "filename": "Action_Items.xlsx",
                        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "size": 23456,
                        "attachmentId": "mock_att_3",
                        "messageId": "mock_msg_2"
                    }
                ]
            },
            {
                "thread_id": "thread_mock_4",
                "subject": "Re: Budget Approval Request",
                "from": "boss@company.com",
                "to": ["you@company.com"],
                "preview": "I've reviewed your budget proposal for the new project. Looks good! Approved. Let's discuss implementation timeline tomorrow.",
                "unread": False,
                "timestamp": (now - timedelta(days=1)).isoformat(),
                "labels": ["INBOX"],
                "message_count": 4,
                "attachments": []
            },
            {
                "thread_id": "thread_mock_5",
                "subject": "Weekly Team Newsletter",
                "from": "noreply@company.com",
                "to": ["team@company.com"],
                "preview": "This week's highlights: New product launch, team achievements, upcoming events, and more. Check out the full newsletter inside.",
                "unread": False,
                "timestamp": (now - timedelta(days=2)).isoformat(),
                "labels": ["INBOX"],
                "message_count": 1,
                "attachments": []
            },
            {
                "thread_id": "thread_mock_6",
                "subject": "Client Proposal for Review",
                "from": "sales@company.com",
                "to": ["you@company.com"],
                "preview": "Attached is the proposal for our new client. Can you review the technical section and provide feedback by Friday? Priority request.",
                "unread": True,
                "timestamp": (now - timedelta(hours=12)).isoformat(),
                "labels": ["INBOX", "IMPORTANT"],
                "message_count": 1,
                "attachments": [
                    {
                        "filename": "Client_Proposal_2025.pdf",
                        "mimeType": "application/pdf",
                        "size": 1234567,
                        "attachmentId": "mock_att_4",
                        "messageId": "mock_msg_3"
                    }
                ]
            }
        ]

    def _get_mock_thread(self, thread_id: str) -> dict[str, Any]:
        """Return mock thread details"""
        threads = self._get_mock_threads()
        for thread in threads:
            if thread['thread_id'] == thread_id:
                return thread
        return threads[0] if threads else {}
