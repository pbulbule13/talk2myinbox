"""
Pydantic schemas for Cognitive Journal Agent (CJA).
All data shared between LangGraph nodes must conform to these schemas.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
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
