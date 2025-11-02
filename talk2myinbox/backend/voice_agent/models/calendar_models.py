"""
Calendar Models
Pydantic models for calendar management and scheduling
"""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, EmailStr


class AvailabilitySlot(BaseModel):
    """Time slot availability"""
    start_time: datetime
    end_time: datetime
    is_available: bool
    conflicting_events: list[str] = Field(
        default_factory=list,
        description="Event IDs that conflict with this slot"
    )


class CalendarEvent(BaseModel):
    """Calendar event representation"""
    event_id: str = Field(description="Unique event identifier")
    title: str
    description: str | None = None
    start_time: datetime
    end_time: datetime
    location: str | None = None
    is_virtual: bool = Field(default=False)
    meeting_url: str | None = None
    organizer: EmailStr
    attendees: list[EmailStr] = Field(default_factory=list)
    status: Literal["confirmed", "tentative", "cancelled"] = Field(default="tentative")
    reminder_minutes: list[int] = Field(
        default_factory=lambda: [30, 10],
        description="Reminder times before event"
    )
    requires_prep: bool = Field(default=False)
    prep_time_minutes: int = Field(default=0, ge=0)


class CalendarAction(BaseModel):
    """Proposed calendar action"""
    action_id: str = Field(description="Unique action identifier")
    action_type: Literal[
        "accept_invite",
        "decline_invite",
        "propose_alternative",
        "create_event",
        "block_time",
        "add_prep_time"
    ]
    event: CalendarEvent
    availability_conflict: bool = Field(
        default=False,
        description="Whether this conflicts with existing events"
    )
    proposed_status: Literal["accept", "decline", "tentative", "propose_alternative"]
    alternative_times: list[AvailabilitySlot] = Field(
        default_factory=list,
        description="Alternative time slots if proposing changes"
    )
    reasoning: str = Field(description="Why this action is proposed")
    requires_authorization: bool = Field(
        default=True,
        description="Whether this needs auth code to execute"
    )
    draft_response: str | None = Field(
        default=None,
        description="Draft email response for calendar action"
    )


class CalendarHold(BaseModel):
    """Temporary calendar hold/block"""
    hold_id: str
    title: str = Field(default="[HOLD] Time Block")
    start_time: datetime
    end_time: datetime
    reason: str
    expires_at: datetime
    can_be_overridden: bool = Field(default=True)
