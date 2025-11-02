"""
Context Retrieval Agent
Fetches relevant emails, calendar events, and historical context
"""

from typing import Dict, Any
from ..graph.state import VoiceAgentState
from ..adapters.email.base import BaseEmailAdapter
from ..adapters.calendar.base import BaseCalendarAdapter


class ContextRetrievalAgent:
    """
    Retrieves context needed for reasoning and action generation.
    Fetches email threads, calendar events, sender history, and availability.
    """

    def __init__(
        self,
        email_adapter: BaseEmailAdapter | None = None,
        calendar_adapter: BaseCalendarAdapter | None = None
    ):
        self.email_adapter = email_adapter
        self.calendar_adapter = calendar_adapter

    async def run(self, state: VoiceAgentState) -> VoiceAgentState:
        """Retrieve relevant context based on intent"""
        intent = state["intent"]

        # Initialize context fields
        state.setdefault("email_threads", [])
        state.setdefault("calendar_events", [])
        state.setdefault("sender_history", {})
        state.setdefault("availability_slots", [])
        state.setdefault("follow_up_tasks", [])

        try:
            # Fetch email context for relevant intents
            if intent in ["triage_inbox", "draft_reply", "summarize"]:
                if self.email_adapter:
                    state["email_threads"] = await self._fetch_email_context(state)
                    state["sender_history"] = await self._fetch_sender_history(state)

            # Fetch calendar context for relevant intents
            if intent in ["schedule_meeting", "check_calendar", "summarize"]:
                if self.calendar_adapter:
                    state["calendar_events"] = await self._fetch_calendar_events(state)
                    state["availability_slots"] = await self._fetch_availability(state)

            # Fetch follow-up tasks for relevant intents
            if intent in ["follow_up", "summarize"]:
                state["follow_up_tasks"] = await self._fetch_follow_ups(state)

        except Exception as e:
            state["error"] = f"Context retrieval error: {str(e)}"

        return state

    async def _fetch_email_context(self, state: VoiceAgentState) -> list[dict]:
        """Fetch relevant email threads from Gmail"""
        if not self.email_adapter:
            return []

        try:
            # Fetch recent email threads (last 20)
            email_threads = await self.email_adapter.fetch_threads(max_results=20)
            return email_threads
        except Exception as e:
            print(f"Error fetching emails: {e}")
            # Return empty list instead of failing
            return []

    async def _fetch_sender_history(self, state: VoiceAgentState) -> Dict[str, Any]:
        """Fetch historical context about senders from Gmail"""
        if not self.email_adapter:
            return {}

        try:
            # Get sender history from email adapter
            email_threads = state.get("email_threads", [])
            sender_history = {}

            for thread in email_threads[:10]:  # Analyze top 10 senders
                sender = thread.get("from", "")
                if sender and sender not in sender_history:
                    history = await self.email_adapter.get_sender_history(sender)
                    if history:
                        sender_history[sender] = history

            return sender_history
        except Exception as e:
            print(f"Error fetching sender history: {e}")
            return {}

    async def _fetch_calendar_events(self, state: VoiceAgentState) -> list[dict]:
        """Fetch upcoming calendar events"""
        # TODO: Implement actual calendar fetching
        return [
            {
                "event_id": "event_1",
                "title": "Executive Team Meeting",
                "start": "2025-10-27T09:00:00Z",
                "end": "2025-10-27T10:00:00Z",
                "attendees": ["team@company.com"]
            }
        ]

    async def _fetch_availability(self, state: VoiceAgentState) -> list[dict]:
        """Fetch availability slots"""
        # TODO: Implement actual availability checking
        return [
            {
                "start": "2025-10-28T14:00:00Z",
                "end": "2025-10-28T15:00:00Z",
                "available": True
            }
        ]

    async def _fetch_follow_ups(self, state: VoiceAgentState) -> list[dict]:
        """Fetch pending follow-up tasks"""
        # TODO: Implement actual follow-up task fetching
        return []
