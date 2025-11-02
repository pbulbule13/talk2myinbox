"""
Voice Agent Models Package
Core Pydantic models for email, calendar, actions, and logging
"""

from .email_models import EmailDraft, EmailThread, EmailCategory, EmailPriority
from .calendar_models import CalendarEvent, CalendarAction, AvailabilitySlot
from .action_models import ActionLog, ActionStatus, FollowUpTask
from .auth_models import AuthorizationCode, AuthSession
from .settings import SystemSettings

__all__ = [
    "EmailDraft",
    "EmailThread",
    "EmailCategory",
    "EmailPriority",
    "CalendarEvent",
    "CalendarAction",
    "AvailabilitySlot",
    "ActionLog",
    "ActionStatus",
    "FollowUpTask",
    "AuthorizationCode",
    "AuthSession",
    "SystemSettings",
]
