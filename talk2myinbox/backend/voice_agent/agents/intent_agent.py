"""
Intent Classification Agent
Determines what the user wants to do from their query
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Literal
from ..graph.state import VoiceAgentState


class IntentClassification(BaseModel):
    """Structured output for intent classification"""
    intent: Literal[
        "triage_inbox",
        "draft_reply",
        "schedule_meeting",
        "check_calendar",
        "follow_up",
        "summarize",
        "manage_communications",
        "send_email",
        "archive_email",
        "prioritize_inbox",
        "config",
        "unknown"
    ] = Field(description="The classified intent")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")
    reasoning: str = Field(description="Why this intent was chosen")


class IntentClassificationAgent:
    """
    Classifies user intent from voice or text input.
    This is the first node in the LangGraph pipeline.
    """

    def __init__(self, model_name: str = "gpt-4"):
        self.llm = ChatOpenAI(model=model_name, temperature=0.3)
        self.parser = PydanticOutputParser(pydantic_object=IntentClassification)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an intent classification system for an executive assistant AI named Vinegar.
Your job is to determine what the CEO wants to do based on their query.

Available intents:
- triage_inbox: User wants to know what's in their inbox, what needs attention
- draft_reply: User wants to compose or draft an email reply
- schedule_meeting: User wants to schedule, accept, or propose a meeting
- check_calendar: User wants to see their schedule or availability
- follow_up: User wants to set up or check follow-up tasks
- summarize: User wants a summary of emails, meetings, or activity
- manage_communications: User wants to manage their Communications tab (view, organize, etc.)
- send_email: User wants to send or compose a new email
- archive_email: User wants to archive, delete, or organize emails
- prioritize_inbox: User wants help prioritizing or organizing their inbox
- config: User wants to change settings or configuration
- unknown: Intent is unclear

**Context:** You're helping a busy CEO manage their day. Be proactive and decisive in classification.

{format_instructions}"""),
            ("human", "{query}")
        ])

    async def run(self, state: VoiceAgentState) -> VoiceAgentState:
        """Run intent classification"""
        query = state["user_query"]

        # Prepare prompt
        prompt_value = self.prompt.format_messages(
            query=query,
            format_instructions=self.parser.get_format_instructions()
        )

        # Get LLM response
        response = await self.llm.ainvoke(prompt_value)

        # Parse structured output
        try:
            classification = self.parser.parse(response.content)
            state["intent"] = classification.intent
            state["confidence"] = classification.confidence
            state["reasoning"] = classification.reasoning
        except Exception as e:
            # Fallback if parsing fails
            state["intent"] = "unknown"
            state["confidence"] = 0.0
            state["reasoning"] = f"Failed to classify: {str(e)}"
            state["error"] = str(e)

        return state
