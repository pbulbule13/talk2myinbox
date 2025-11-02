"""
Voice Agent State
LangGraph state definition for the email & calendar automation system
"""

from typing import TypedDict, Literal, Annotated
from operator import add


class VoiceAgentState(TypedDict):
    """
    State that flows through the LangGraph pipeline.
    Each node reads from and writes to this state.
    """

    # User Input
    user_query: str
    interaction_mode: Literal["voice", "text", "automated"]
    session_id: str
    user_id: str | None

    # Intent Classification
    intent: Literal[
        "triage_inbox",
        "draft_reply",
        "schedule_meeting",
        "check_calendar",
        "follow_up",
        "summarize",
        "config",
        "unknown"
    ]
    confidence: float

    # Context Retrieval
    email_threads: list[dict]
    calendar_events: list[dict]
    sender_history: dict
    availability_slots: list[dict]
    follow_up_tasks: list[dict]

    # Reasoning & Decision
    priority_assessment: dict
    recommended_action: str
    reasoning: str

    # Draft Generation
    email_drafts: Annotated[list[dict], add]
    calendar_actions: Annotated[list[dict], add]
    follow_ups: Annotated[list[dict], add]

    # Authorization
    requires_authorization: bool
    authorization_code: str | None
    pending_actions: Annotated[list[str], add]

    # Execution
    executed_actions: Annotated[list[str], add]
    execution_status: dict

    # Logging
    action_logs: Annotated[list[dict], add]

    # Response
    voice_response: str
    text_response: str
    final_response: dict

    # Error Handling
    error: str | None
    retry_count: int
