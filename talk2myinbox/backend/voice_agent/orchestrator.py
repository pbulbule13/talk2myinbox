"""
Voice Agent Orchestrator
Main service that coordinates the voice-enabled email & calendar automation system
"""

from typing import Dict, Any
from .graph.graph_builder import create_voice_agent_graph
from .graph.state import VoiceAgentState
from .models.settings import SystemSettings
from .adapters.email.factory import EmailAdapterFactory
from .adapters.calendar.google_calendar_adapter import GoogleCalendarAdapter
import uuid
from datetime import datetime


class VoiceAgentOrchestrator:
    """
    Main orchestrator for the voice agent system.
    Coordinates LangGraph execution, adapter initialization, and session management.
    """

    def __init__(self, settings: SystemSettings | None = None):
        self.settings = settings or SystemSettings()

        # Initialize adapters FIRST (before creating graph)
        self.email_adapter = self._create_email_adapter()
        self.calendar_adapter = self._create_calendar_adapter()

        # Create graph WITH adapters so they're passed to Context and Execution agents
        self.graph = create_voice_agent_graph(
            email_adapter=self.email_adapter,
            calendar_adapter=self.calendar_adapter
        )

        # Session management (in production, use Redis or database)
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def _create_email_adapter(self):
        """Create email adapter based on settings using factory pattern"""
        try:
            return EmailAdapterFactory.create(
                provider=self.settings.email_provider,
                credentials_path=self.settings.gmail_credentials_path,
                use_mock=False  # Set to True for testing without real email
            )
        except Exception as e:
            print(f"⚠️  Failed to create email adapter: {e}")
            print("⚠️  Using mock mode for testing")
            return EmailAdapterFactory.create(
                provider="gmail_api",
                use_mock=True  # Fall back to mock mode
            )

    def _create_calendar_adapter(self):
        """Create calendar adapter based on settings"""
        provider = self.settings.calendar_provider
        if provider == "google_calendar":
            return GoogleCalendarAdapter(credentials_path=self.settings.calendar_credentials_path)
        # TODO: Add other providers (CalDAV, Outlook)
        return None

    async def process_query(
        self,
        query: str,
        mode: str = "text",
        user_id: str | None = None,
        session_id: str | None = None,
        authorization_code: str | None = None
    ) -> Dict[str, Any]:
        """
        Process a user query through the voice agent system.

        Args:
            query: User's natural language query or command
            mode: Interaction mode ("voice" or "text")
            user_id: Optional user identifier
            session_id: Optional session identifier (for continuing conversations)
            authorization_code: Optional authorization code for executing actions

        Returns:
            Response dictionary with results, drafts, logs, etc.
        """

        # Create or retrieve session
        if not session_id:
            session_id = f"session_{uuid.uuid4().hex[:12]}"

        # Initialize state
        initial_state: VoiceAgentState = {
            "user_query": query,
            "interaction_mode": mode,
            "session_id": session_id,
            "user_id": user_id,
            "intent": "unknown",
            "confidence": 0.0,
            "email_threads": [],
            "calendar_events": [],
            "sender_history": {},
            "availability_slots": [],
            "follow_up_tasks": [],
            "priority_assessment": {},
            "recommended_action": "",
            "reasoning": "",
            "email_drafts": [],
            "calendar_actions": [],
            "follow_ups": [],
            "requires_authorization": False,
            "authorization_code": authorization_code,
            "pending_actions": [],
            "executed_actions": [],
            "execution_status": {},
            "action_logs": [],
            "voice_response": "",
            "text_response": "",
            "final_response": {},
            "error": None,
            "retry_count": 0
        }

        # Execute the LangGraph workflow
        try:
            result_state = await self.graph.ainvoke(initial_state)

            # Store session for continuity
            self.sessions[session_id] = {
                "last_activity": datetime.utcnow().isoformat(),
                "state": result_state,
                "user_id": user_id
            }

            return result_state["final_response"]

        except Exception as e:
            return {
                "error": str(e),
                "text": f"I encountered an error processing your request: {str(e)}",
                "intent": "unknown",
                "drafts": [],
                "calendar_actions": [],
                "executed": [],
                "logs": []
            }

    async def get_session(self, session_id: str) -> Dict[str, Any] | None:
        """Retrieve a session by ID"""
        return self.sessions.get(session_id)

    async def summarize_inbox(self, user_id: str | None = None) -> Dict[str, Any]:
        """
        Summarize the user's inbox.
        Convenience method that internally calls process_query.
        """
        return await self.process_query(
            query="What's in my inbox? Summarize what needs my attention.",
            mode="text",
            user_id=user_id
        )

    async def draft_reply(
        self,
        thread_id: str,
        user_message: str,
        user_id: str | None = None
    ) -> Dict[str, Any]:
        """
        Draft a reply to a specific email thread.
        Convenience method for the draft_reply intent.
        """
        query = f"Draft a reply to thread {thread_id}: {user_message}"
        return await self.process_query(
            query=query,
            mode="text",
            user_id=user_id
        )

    async def check_calendar(
        self,
        timeframe: str = "today",
        user_id: str | None = None
    ) -> Dict[str, Any]:
        """
        Check calendar for a specific timeframe.
        Convenience method for calendar queries.
        """
        return await self.process_query(
            query=f"What's on my calendar {timeframe}?",
            mode="text",
            user_id=user_id
        )

    def get_agent_name(self) -> str:
        """Get the configured agent name (e.g., 'Vinegar')"""
        return self.settings.voice_agent_name
