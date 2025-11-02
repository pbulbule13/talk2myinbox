"""
Email Adapters Package
Adapters for various email providers (Gmail API, IMAP/SMTP, Outlook Graph)
"""

from .base import BaseEmailAdapter
from .gmail_adapter import GmailAdapter
from .factory import EmailAdapterFactory

__all__ = ["BaseEmailAdapter", "GmailAdapter", "EmailAdapterFactory"]
