"""
Pydantic schemas for Cognitive Journal Agent (CJA).
All data shared between LangGraph nodes must conform to these schemas.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime


class JournalEntry(BaseModel):
    """Represents a single captured piece of information."""
    timestamp: datetime = Field(description="Time of capture.")
    input_type: str = Field(
        description="e.g., 'email', 'voice_memo', 'photo_ocr', 'text_note', 'code_snippet', 'calendar_event'."
    )
    raw_content: str = Field(description="The original, unsummarized text content.")
    source_id: str = Field(description="Unique ID of the source (e.g., email ID, filename).")

    # Processed Fields (Filled by Processing Node)
    contextual_tags: List[str] = Field(
        default=[],
        description="Automatically categorized tags: [Work, Personal, Task, Idea, Reference, Urgent]."
    )
    extracted_action_items: List[str] = Field(
        default=[],
        description="Specific, executable action phrases extracted."
    )
    inferred_emotion: Optional[str] = Field(
        default=None,
        description="Brief emotional tone: [High Focus, Stressed, Reflective, Routine]."
    )


class DailySummaryOutput(BaseModel):
    """The final structured output for the user."""
    date: str
    daily_theme: str = Field(description="A concise, one-sentence summary of the day's main focus.")
    key_decisions_and_learnings: List[str] = Field(description="Top 3-5 key outcomes or insights.")
    journal_narrative: str = Field(description="A brief, thematic narrative of the day.")


class ActionItem(BaseModel):
    """A single task for the Next Day Planner."""
    task_id: str
    task_description: str
    priority: str = Field(description="P1 (Urgent), P2 (High), P3 (Medium).")
    source_entry_id: str
    due_date: Optional[datetime] = None


class FinalAgentReport(BaseModel):
    """Complete daily report including summary and action items."""
    summary: DailySummaryOutput
    pending_actions: List[ActionItem]
    suggested_first_task: str = Field(description="The highest priority task to start the next day.")


class AgentState(BaseModel):
    """LangGraph state containing all workflow data."""
    new_entry: Optional[JournalEntry] = None
    all_entries: List[JournalEntry] = Field(default_factory=list)
    pending_actions: List[ActionItem] = Field(default_factory=list)
    final_report: Optional[FinalAgentReport] = None
    audio_output_path: Optional[str] = None
    tool_response: Optional[str] = None
    user_input: str = ""
    current_route: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True


# ============================================================================
# MULTI-CALENDAR INTEGRATION MODELS
# ============================================================================

class CalendarSource(BaseModel):
    """Represents a calendar source (Google, Outlook, OCR, iCal, etc.)."""
    source_id: str = Field(description="Unique identifier for this calendar source.")
    source_type: Literal["google", "outlook", "ical", "ocr", "manual", "caldav", "apple"] = Field(
        description="Type of calendar source."
    )
    display_name: str = Field(description="User-friendly name (e.g., 'Work Calendar', 'Personal Google').")
    is_active: bool = Field(default=True, description="Whether this source is currently syncing.")
    color: Optional[str] = Field(default=None, description="Hex color code for UI display (#FF5733).")

    # OAuth/Credentials
    requires_oauth: bool = Field(default=False, description="Whether this source needs OAuth authentication.")
    oauth_credentials: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Encrypted OAuth tokens (access_token, refresh_token, expires_at)."
    )

    # Sync Settings
    last_sync: Optional[datetime] = Field(default=None, description="Last successful sync timestamp.")
    sync_frequency_minutes: int = Field(default=60, description="How often to sync (in minutes).")
    sync_window_days: int = Field(default=90, description="How many days forward/backward to sync.")

    # File-based sources
    file_path: Optional[str] = Field(default=None, description="Path to iCal/ICS file or OCR image.")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class UnifiedEvent(BaseModel):
    """Standardized event format combining all calendar sources."""
    event_id: str = Field(description="Unique ID (combination of source_id + original event ID).")
    source_id: str = Field(description="Which calendar source this came from.")

    # Core Event Data
    title: str = Field(description="Event title/subject.")
    description: Optional[str] = Field(default=None, description="Event description/notes.")
    location: Optional[str] = Field(default=None, description="Physical or virtual location.")

    # Time
    start_time: datetime = Field(description="Event start time (timezone-aware).")
    end_time: datetime = Field(description="Event end time (timezone-aware).")
    all_day: bool = Field(default=False, description="Whether this is an all-day event.")
    timezone: str = Field(default="UTC", description="Timezone string (e.g., 'America/New_York').")

    # Participants
    attendees: List[str] = Field(default_factory=list, description="List of attendee emails.")
    organizer: Optional[str] = Field(default=None, description="Organizer email.")

    # Recurrence
    is_recurring: bool = Field(default=False, description="Whether event repeats.")
    recurrence_rule: Optional[str] = Field(default=None, description="RRULE format (e.g., 'FREQ=WEEKLY;BYDAY=MO,WE,FR').")

    # Status
    status: Literal["confirmed", "tentative", "cancelled"] = Field(default="confirmed")
    response_status: Optional[Literal["accepted", "declined", "tentative", "needsAction"]] = Field(default=None)

    # Metadata
    original_event_id: str = Field(description="Original ID from the source calendar.")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Conflict Detection
    has_conflict: bool = Field(default=False, description="Whether this overlaps with another event.")
    conflicting_event_ids: List[str] = Field(default_factory=list, description="IDs of conflicting events.")

    # Source Metadata
    source_url: Optional[str] = Field(default=None, description="Deep link to original event.")
    raw_data: Optional[Dict[str, Any]] = Field(default=None, description="Original raw event data for debugging.")


class EventConflict(BaseModel):
    """Represents a conflict between two or more events."""
    conflict_id: str = Field(description="Unique conflict identifier.")
    conflicting_events: List[UnifiedEvent] = Field(description="List of events that overlap.")
    conflict_type: Literal["full_overlap", "partial_overlap", "adjacent"] = Field(
        description="Type of conflict."
    )
    resolution_suggestion: Optional[str] = Field(
        default=None,
        description="AI-generated suggestion for resolving conflict."
    )
    is_resolved: bool = Field(default=False)
    resolved_at: Optional[datetime] = Field(default=None)


class CalendarConnection(BaseModel):
    """OAuth connection details for external calendar providers."""
    connection_id: str = Field(description="Unique connection ID.")
    provider: Literal["google", "outlook", "apple", "caldav"] = Field(description="Calendar provider.")
    user_email: str = Field(description="User's email/account identifier.")

    # OAuth Flow
    client_id: str = Field(description="OAuth client ID.")
    client_secret: str = Field(description="OAuth client secret (encrypted).")
    access_token: Optional[str] = Field(default=None, description="Current access token (encrypted).")
    refresh_token: Optional[str] = Field(default=None, description="Refresh token (encrypted).")
    token_expires_at: Optional[datetime] = Field(default=None, description="When access token expires.")

    # Scopes
    scopes: List[str] = Field(
        default_factory=list,
        description="OAuth scopes granted (e.g., ['https://www.googleapis.com/auth/calendar.readonly'])."
    )

    # Status
    is_connected: bool = Field(default=False)
    last_auth_at: Optional[datetime] = Field(default=None)
    auth_error: Optional[str] = Field(default=None, description="Last authentication error.")


class CalendarInsight(BaseModel):
    """Analytics and insights from unified calendar."""
    date: str = Field(description="Date for this insight (YYYY-MM-DD).")
    total_events: int = Field(description="Total events for the day.")
    total_duration_minutes: int = Field(description="Total scheduled time in minutes.")
    busiest_hours: List[int] = Field(
        default_factory=list,
        description="Hours with most events (0-23)."
    )
    free_time_slots: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Available time slots [{'start': '10:00', 'end': '11:30'}]."
    )
    event_breakdown: Dict[str, int] = Field(
        default_factory=dict,
        description="Event count by source {'google': 5, 'outlook': 3}."
    )
    suggested_focus_time: Optional[str] = Field(
        default=None,
        description="AI suggestion for best focus time block."
    )
    conflict_count: int = Field(default=0, description="Number of scheduling conflicts.")

    # Integration with Journal
    related_journal_entries: List[str] = Field(
        default_factory=list,
        description="Journal entry IDs related to calendar events."
    )
