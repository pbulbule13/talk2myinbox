"""
Base Calendar Adapter
Abstract interface that all calendar adapters must implement
"""

from abc import ABC, abstractmethod
from typing import Any
from datetime import datetime


class BaseCalendarAdapter(ABC):
    """
    Abstract base class for calendar providers.
    Implementations: Google Calendar, CalDAV, Microsoft Graph (Outlook)
    """

    @abstractmethod
    async def get_events(
        self,
        start_time: datetime,
        end_time: datetime,
        calendar_id: str = "primary"
    ) -> list[dict[str, Any]]:
        """
        Fetch calendar events within a time range.

        Args:
            start_time: Start of time range
            end_time: End of time range
            calendar_id: Calendar identifier (default: primary)

        Returns:
            List of calendar event dictionaries
        """
        pass

    @abstractmethod
    async def get_event(self, event_id: str) -> dict[str, Any]:
        """
        Get full details of a specific calendar event.

        Args:
            event_id: Unique event identifier

        Returns:
            Complete event data
        """
        pass

    @abstractmethod
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
        """
        Create a new calendar event.

        Args:
            title: Event title
            start_time: Event start time
            end_time: Event end time
            attendees: List of attendee email addresses
            description: Event description
            location: Event location
            calendar_id: Calendar to create event in

        Returns:
            Created event data with event_id
        """
        pass

    @abstractmethod
    async def accept_event(self, event_id: str) -> dict[str, Any]:
        """
        Accept a calendar invite.

        Args:
            event_id: Event to accept

        Returns:
            Updated event data
        """
        pass

    @abstractmethod
    async def decline_event(
        self,
        event_id: str,
        message: str | None = None
    ) -> dict[str, Any]:
        """
        Decline a calendar invite.

        Args:
            event_id: Event to decline
            message: Optional decline message

        Returns:
            Updated event data
        """
        pass

    @abstractmethod
    async def propose_alternative(
        self,
        event_id: str,
        alternative_times: list[dict],
        message: str | None = None
    ) -> dict[str, Any]:
        """
        Propose alternative times for an event.

        Args:
            event_id: Event to propose alternatives for
            alternative_times: List of alternative time slots
            message: Message to organizer

        Returns:
            Response data
        """
        pass

    @abstractmethod
    async def check_availability(
        self,
        start_time: datetime,
        end_time: datetime,
        calendar_id: str = "primary"
    ) -> dict[str, Any]:
        """
        Check availability for a time slot.

        Args:
            start_time: Start of time slot
            end_time: End of time slot
            calendar_id: Calendar to check

        Returns:
            Availability status and conflicting events
        """
        pass

    @abstractmethod
    async def delete_event(self, event_id: str) -> bool:
        """
        Delete a calendar event.

        Args:
            event_id: Event to delete

        Returns:
            Success status
        """
        pass
