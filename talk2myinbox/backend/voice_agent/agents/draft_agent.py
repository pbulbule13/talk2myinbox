"""
Draft Generation Agent
Generates email drafts and calendar action proposals
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from ..graph.state import VoiceAgentState
from ..models.email_models import EmailDraft
from ..models.calendar_models import CalendarAction
import json
import uuid
from datetime import datetime


class DraftGenerationAgent:
    """
    Generates drafts for emails and calendar actions.
    Drafts are prepared for user review before sending.
    """

    def __init__(self, model_name: str = "gpt-4"):
        self.llm = ChatOpenAI(model=model_name, temperature=0.8)

        self.email_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are {agent_name}, an executive assistant AI.

Generate a professional email draft that sounds natural and human.

Tone: {tone}
Context: {context}
Sender History: {sender_history}

The email should:
- Be concise and actionable
- Match the requested tone
- Include concrete next steps
- Sound like it came from the user, not a robot

Generate ONLY the email body. No subject line, no greetings beyond what's natural."""),
            ("human", """Draft an email in response to:

From: {from_email}
Subject: {subject}
Message: {message}

User wants to: {action}

Write the email body:""")
        ])

        self.calendar_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are {agent_name}, an executive assistant AI.

Generate a clear, professional response for a calendar action.

The response should:
- Be polite and professional
- Clearly state what you're doing (accepting, declining, proposing alternative)
- If proposing alternatives, suggest 2-3 specific time slots
- Be brief and actionable"""),
            ("human", """Calendar Action: {action}
Event: {event_title}
Organizer: {organizer}
Proposed Time: {proposed_time}
User's Availability: {availability}

Generate a response:""")
        ])

    async def run(self, state: VoiceAgentState) -> VoiceAgentState:
        """Generate drafts based on recommended action"""
        recommended_action = state.get("recommended_action", "")
        intent = state["intent"]

        # Initialize draft lists if not present
        state.setdefault("email_drafts", [])
        state.setdefault("calendar_actions", [])
        state.setdefault("requires_authorization", False)

        try:
            if "draft_reply" in recommended_action or intent == "draft_reply":
                draft = await self._generate_email_draft(state)
                if draft:
                    state["email_drafts"].append(draft)
                    state["requires_authorization"] = True

            elif "meeting" in recommended_action or intent == "schedule_meeting":
                action = await self._generate_calendar_action(state)
                if action:
                    state["calendar_actions"].append(action)
                    state["requires_authorization"] = True

        except Exception as e:
            state["error"] = f"Draft generation error: {str(e)}"

        return state

    async def _generate_email_draft(self, state: VoiceAgentState) -> dict | None:
        """Generate an email draft"""
        email_threads = state.get("email_threads", [])
        if not email_threads:
            return None

        # Get the first email thread for now
        thread = email_threads[0]
        sender_history = state.get("sender_history", {})

        # Get settings (in real implementation, load from config)
        agent_name = "Vinegar"
        tone = "warm"  # Could come from settings or be detected from context

        # Prepare prompt
        prompt_value = self.email_prompt.format_messages(
            agent_name=agent_name,
            tone=tone,
            context=state.get("reasoning", ""),
            sender_history=json.dumps(sender_history.get(thread["from"], {})),
            from_email=thread["from"],
            subject=thread["subject"],
            message=thread["preview"],
            action=state.get("recommended_action", "reply")
        )

        # Generate draft
        response = await self.llm.ainvoke(prompt_value)
        draft_body = response.content

        # Create draft object
        draft = {
            "draft_id": f"draft_{uuid.uuid4().hex[:8]}",
            "thread_id": thread["thread_id"],
            "subject": f"Re: {thread['subject']}",
            "to": [thread["from"]],
            "cc": [],
            "body": draft_body,
            "tone": tone,
            "requires_authorization": True,
            "previous_thread_summary": thread["preview"],
            "reasoning": f"Generated reply based on: {state.get('reasoning', 'user request')}",
            "created_at": datetime.utcnow().isoformat(),
            "version": 1
        }

        return draft

    async def _generate_calendar_action(self, state: VoiceAgentState) -> dict | None:
        """Generate a calendar action proposal"""
        calendar_events = state.get("calendar_events", [])
        if not calendar_events:
            # User wants to create a new event
            return self._propose_new_event(state)

        # Respond to existing event
        event = calendar_events[0]
        availability = state.get("availability_slots", [])

        # Get settings
        agent_name = "Vinegar"
        action = state.get("recommended_action", "review")

        # Prepare prompt
        prompt_value = self.calendar_prompt.format_messages(
            agent_name=agent_name,
            action=action,
            event_title=event["title"],
            organizer=event.get("attendees", ["Unknown"])[0],
            proposed_time=event["start"],
            availability=json.dumps(availability, indent=2)
        )

        # Generate response
        response = await self.llm.ainvoke(prompt_value)
        draft_response = response.content

        # Create calendar action object
        action_obj = {
            "action_id": f"cal_action_{uuid.uuid4().hex[:8]}",
            "action_type": self._map_action_to_type(action),
            "event": event,
            "availability_conflict": False,  # TODO: Check actual availability
            "proposed_status": self._map_action_to_status(action),
            "alternative_times": availability[:3] if availability else [],
            "reasoning": state.get("reasoning", ""),
            "requires_authorization": True,
            "draft_response": draft_response
        }

        return action_obj

    def _propose_new_event(self, state: VoiceAgentState) -> dict:
        """Propose a new calendar event"""
        # TODO: Implement new event creation
        return {}

    def _map_action_to_type(self, action: str) -> str:
        """Map recommended action to calendar action type"""
        if "accept" in action:
            return "accept_invite"
        elif "decline" in action:
            return "decline_invite"
        elif "propose" in action or "alternative" in action:
            return "propose_alternative"
        else:
            return "create_event"

    def _map_action_to_status(self, action: str) -> str:
        """Map recommended action to proposed status"""
        if "accept" in action:
            return "accept"
        elif "decline" in action:
            return "decline"
        elif "propose" in action:
            return "propose_alternative"
        else:
            return "tentative"
