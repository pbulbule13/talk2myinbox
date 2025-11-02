"""
Email Models
Pydantic models for email triage, drafting, and management
"""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, EmailStr


class EmailPriority(BaseModel):
    """Priority classification for incoming emails"""
    level: Literal["high", "medium", "low"] = Field(description="Priority level")
    reason: str = Field(description="Why this priority was assigned")
    requires_reply: bool = Field(default=False)
    deadline: datetime | None = Field(default=None)


class EmailCategory(BaseModel):
    """Email category classification"""
    category: Literal[
        "high_priority_reply",
        "medium_priority_monitor",
        "low_priority_informational",
        "scheduling_calendar",
        "marketing_bulk",
        "internal_team"
    ]
    confidence: float = Field(ge=0.0, le=1.0, description="Classification confidence")
    tags: list[str] = Field(default_factory=list)


class EmailThread(BaseModel):
    """Email thread with full context"""
    thread_id: str = Field(description="Unique thread identifier")
    subject: str
    participants: list[EmailStr]
    messages: list[dict] = Field(default_factory=list, description="All messages in thread")
    latest_message: dict
    unread_count: int = Field(default=0, ge=0)
    priority: EmailPriority | None = None
    category: EmailCategory | None = None
    sender_history: dict = Field(
        default_factory=dict,
        description="Historical context about the sender"
    )
    requires_action: bool = Field(default=False)
    suggested_action: str | None = Field(
        default=None,
        description="AI-suggested next step"
    )


class EmailDraft(BaseModel):
    """Draft email reply prepared by the system"""
    draft_id: str = Field(description="Unique draft identifier")
    thread_id: str = Field(description="Thread this draft replies to")
    subject: str
    to: list[EmailStr]
    cc: list[EmailStr] = Field(default_factory=list)
    bcc: list[EmailStr] = Field(default_factory=list)
    body: str = Field(description="Draft email body")
    tone: Literal["formal", "warm", "concise", "friendly"]
    requires_authorization: bool = Field(
        default=True,
        description="Whether this needs auth code to send"
    )
    previous_thread_summary: str | None = Field(
        default=None,
        description="Summary of the email thread context"
    )
    reasoning: str = Field(
        description="Why this draft was generated this way"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = Field(default=1, description="Draft version for iterative refinement")


class EmailAction(BaseModel):
    """Proposed email action"""
    action_type: Literal["send_reply", "archive", "snooze", "flag", "forward"]
    email_id: str
    draft: EmailDraft | None = None
    snooze_until: datetime | None = None
    forward_to: list[EmailStr] = Field(default_factory=list)
    reasoning: str = Field(description="Why this action is proposed")
