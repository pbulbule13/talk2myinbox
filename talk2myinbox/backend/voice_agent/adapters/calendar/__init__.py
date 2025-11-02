"""
Calendar Adapters Package
Adapters for various calendar providers (Google Calendar, CalDAV, Outlook)
"""

from .base import BaseCalendarAdapter
from .google_calendar_adapter import GoogleCalendarAdapter

__all__ = ["BaseCalendarAdapter", "GoogleCalendarAdapter"]
