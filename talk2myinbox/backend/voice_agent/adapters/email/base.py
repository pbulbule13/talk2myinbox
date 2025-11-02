"""
Base Email Adapter
Abstract interface that all email adapters must implement
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseEmailAdapter(ABC):
    """
    Abstract base class for email providers.
    Implementations: Gmail API, IMAP/SMTP, Microsoft Graph (Outlook)
    """

    @abstractmethod
    async def fetch_threads(
        self,
        max_results: int = 50,
        unread_only: bool = False,
        query: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Fetch email threads from the inbox.

        Args:
            max_results: Maximum number of threads to return
            unread_only: Only fetch unread threads
            query: Provider-specific query string

        Returns:
            List of email thread dictionaries
        """
        pass

    @abstractmethod
    async def get_thread(self, thread_id: str) -> dict[str, Any]:
        """
        Get full details of a specific email thread.

        Args:
            thread_id: Unique thread identifier

        Returns:
            Complete thread data with all messages
        """
        pass

    @abstractmethod
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
        """
        Send an email (or reply to a thread).

        Args:
            to: List of recipient email addresses
            subject: Email subject
            body: Email body (can be HTML or plain text)
            cc: CC recipients
            bcc: BCC recipients
            thread_id: If replying, the thread ID to reply to
            attachments: List of attachment dictionaries

        Returns:
            Result dictionary with message_id and status
        """
        pass

    @abstractmethod
    async def mark_read(self, thread_id: str) -> bool:
        """
        Mark a thread as read.

        Args:
            thread_id: Thread to mark as read

        Returns:
            Success status
        """
        pass

    @abstractmethod
    async def archive_thread(self, thread_id: str) -> bool:
        """
        Archive a thread (remove from inbox).

        Args:
            thread_id: Thread to archive

        Returns:
            Success status
        """
        pass

    @abstractmethod
    async def get_sender_history(self, email_address: str) -> dict[str, Any]:
        """
        Get historical context about a sender.

        Args:
            email_address: Sender's email address

        Returns:
            Dictionary with interaction count, avg response time, etc.
        """
        pass

    @abstractmethod
    async def search_emails(
        self,
        query: str,
        max_results: int = 50
    ) -> list[dict[str, Any]]:
        """
        Search emails using provider-specific query.

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            List of matching email threads
        """
        pass
