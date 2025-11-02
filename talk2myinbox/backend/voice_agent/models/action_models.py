"""
Action Models
Models for action logging, follow-ups, and audit trails
"""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class ActionStatus(BaseModel):
    """Status of an action"""
    status: Literal["pending_user_auth", "draft_only", "approved", "executing", "completed", "failed"]
    status_message: str | None = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ActionLog(BaseModel):
    """
    Comprehensive action log entry.
    This is emitted for every significant interaction and consumed by the dashboard.
    """
    log_id: str = Field(description="Unique log entry ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    actor: str = Field(default="Voice Agent", description="Who performed the action")
    mode: Literal["voice", "text", "automated"] = Field(
        description="How the user interacted"
    )
    object_type: Literal["email", "calendar", "followup", "summary", "config"]
    object_ref: str = Field(
        description="Reference to the object (e.g., email subject, event title)"
    )
    action: str = Field(
        description="Action taken (e.g., 'drafted_reply', 'proposed_meeting', 'scheduled_followup')"
    )
    reason: str = Field(description="Short justification for the action")
    status: ActionStatus
    user_id: str | None = Field(default=None, description="User who initiated")
    authorization_code_used: bool = Field(default=False)
    metadata: dict = Field(
        default_factory=dict,
        description="Additional context (email IDs, event IDs, etc.)"
    )


class FollowUpTask(BaseModel):
    """Follow-up task for tracking commitments and pending responses"""
    task_id: str = Field(description="Unique task identifier")
    thread_id: str | None = Field(default=None, description="Related email thread")
    event_id: str | None = Field(default=None, description="Related calendar event")
    contact: str = Field(description="Person or organization to follow up with")
    subject: str = Field(description="What this follow-up is about")
    due_at: datetime = Field(description="When to follow up")
    status: Literal["scheduled", "reminded", "done", "cancelled"] = Field(default="scheduled")
    note: str | None = Field(default=None, description="Additional context")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    reminded_count: int = Field(default=0, ge=0)
    action_taken: str | None = Field(
        default=None,
        description="What action was taken when completed"
    )


class VoiceInteraction(BaseModel):
    """Record of a voice interaction session"""
    interaction_id: str
    user_id: str | None = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: datetime | None = None
    transcript: list[dict] = Field(
        default_factory=list,
        description="Full conversation transcript"
    )
    actions_proposed: list[str] = Field(
        default_factory=list,
        description="Action IDs proposed during this session"
    )
    actions_completed: list[str] = Field(
        default_factory=list,
        description="Action IDs completed during this session"
    )
    session_summary: str | None = Field(
        default=None,
        description="Summary of what was accomplished"
    )
