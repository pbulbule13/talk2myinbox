"""
Response Generation Agent
Creates friendly, human-like responses with personality and reasoning
"""

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from ..graph.state import VoiceAgentState
import os


class ResponseGenerationAgent:
    """
    Generates natural, conversational responses with personality.
    Acts as the voice and personality of the executive assistant.

    Supports multiple LLM providers:
    - OpenAI (GPT-4, GPT-3.5)
    - Google Gemini
    - DeepSeek
    """

    def __init__(self, model_name: str = None):
        """
        Initialize with configurable LLM provider for natural language generation.

        Args:
            model_name: Optional model name. If not provided, reads from environment.

        Environment Variables:
            RESPONSE_MODEL: Model to use (default: gpt-4)
            OPENAI_API_KEY: Required for OpenAI/DeepSeek
            GOOGLE_API_KEY: Required for Gemini
            DEEPSEEK_API_KEY: Optional, falls back to OPENAI_API_KEY
        """
        if model_name is None:
            model_name = os.getenv("RESPONSE_MODEL", os.getenv("MODEL_NAME", "gpt-4"))

        self.model_name = model_name
        self.llm = self._create_llm_client(model_name)

        # Define prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are {agent_name}, a highly capable and personable executive assistant to the CEO of HealthCare Sciences.

**Your Personality:**
- Warm, professional, and proactive
- Speak naturally like a trusted colleague, not a robot
- Use occasional contractions and conversational language
- Show empathy and understanding of the CEO's workload
- Be confident but never arrogant
- Think like a personal secretary who truly cares about helping

**Your Role:**
You're not just answering questions - you're managing the CEO's day, protecting their time, and helping them focus on what matters most. You anticipate needs, offer suggestions, and take initiative when appropriate.

**Communication Style:**
- Start with a warm greeting or acknowledgment when appropriate
- Be concise but thorough - the CEO's time is valuable
- Always provide reasoning for your recommendations
- Use phrases like "I've reviewed...", "Based on my analysis...", "I recommend..."
- End with offers to help further: "Would you like me to...", "I can also...", "Shall I..."

**Context Awareness:**
- Remember that every interaction is part of managing their executive responsibilities
- Prioritize urgent matters and flag them clearly
- Be proactive about calendar conflicts and important deadlines
- Think strategically about how your assistance impacts their goals

**Current Situation:**
Intent: {intent}
User Query: "{query}"

Analysis: {reasoning}
Recommended Action: {recommended_action}

Email Context: {email_summary}
Calendar Context: {calendar_summary}

Drafts Prepared: {drafts_count}
Actions Executed: {actions_executed}

**Your Task:**
Generate a natural, conversational response that:
1. Directly addresses their query
2. Explains your reasoning clearly
3. Presents any drafts or actions taken
4. Offers next steps or follow-up actions
5. Sounds like a capable human assistant, not an AI"""),
            ("human", "Generate a warm, professional response:")
        ])

    def _create_llm_client(self, model_name: str):
        """
        Create appropriate LLM client based on model name.

        Supports:
        - OpenAI models (gpt-*, o1-*)
        - DeepSeek models (deepseek-*)
        - Google Gemini models (gemini-*)
        """
        model_lower = model_name.lower()

        try:
            # Google Gemini models
            if "gemini" in model_lower:
                api_key = os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    raise ValueError("GOOGLE_API_KEY environment variable is required for Gemini models")

                return ChatGoogleGenerativeAI(
                    model=model_name,
                    temperature=0.8,  # Higher temperature for personality
                    max_tokens=1500,
                    google_api_key=api_key
                )

            # DeepSeek models
            elif "deepseek" in model_lower:
                api_key = os.getenv("DEEPSEEK_API_KEY", os.getenv("OPENAI_API_KEY"))
                api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")

                if not api_key:
                    raise ValueError("DEEPSEEK_API_KEY or OPENAI_API_KEY required for DeepSeek")

                return ChatOpenAI(
                    model=model_name,
                    temperature=0.8,
                    max_tokens=1500,
                    openai_api_base=api_base,
                    openai_api_key=api_key
                )

            # OpenAI models (default)
            else:
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI models")

                return ChatOpenAI(
                    model=model_name,
                    temperature=0.8,
                    max_tokens=1500
                )

        except Exception as e:
            print(f"[ERROR] Failed to create LLM client for {model_name}: {e}")
            raise

    async def run(self, state: VoiceAgentState) -> VoiceAgentState:
        """Generate friendly, human-like response"""

        # Get agent name from settings
        agent_name = os.getenv("VOICE_AGENT_NAME", "Vinegar")

        # Prepare context summaries
        email_summary = self._summarize_emails(state.get("email_threads", []))
        calendar_summary = self._summarize_calendar(state.get("calendar_events", []))

        drafts_count = len(state.get("email_drafts", []))
        actions_executed = len(state.get("executed_actions", []))

        # Generate response
        prompt_value = self.prompt.format_messages(
            agent_name=agent_name,
            intent=state.get("intent", "unknown"),
            query=state.get("user_query", ""),
            reasoning=state.get("reasoning", "No reasoning available"),
            recommended_action=state.get("recommended_action", "review"),
            email_summary=email_summary,
            calendar_summary=calendar_summary,
            drafts_count=drafts_count,
            actions_executed=actions_executed
        )

        try:
            response = await self.llm.ainvoke(prompt_value)
            response_text = response.content

            # Store in both voice and text formats
            state["voice_response"] = response_text
            state["text_response"] = response_text

            # Build final response object
            final_response = {
                "text": response_text,
                "intent": state.get("intent"),
                "confidence": state.get("confidence", 0.0),
                "reasoning": state.get("reasoning", ""),
                "drafts": state.get("email_drafts", []),
                "calendar_actions": state.get("calendar_actions", []),
                "executed": state.get("executed_actions", []),
                "pending": state.get("pending_actions", []),
                "logs": state.get("action_logs", []),
                "requires_authorization": state.get("requires_authorization", False),
                "session_id": state.get("session_id")
            }

            state["final_response"] = final_response

            return state

        except Exception as e:
            error_msg = f"I apologize, but I encountered a technical issue: {str(e)}. Let me try a different approach."

            state["voice_response"] = error_msg
            state["text_response"] = error_msg
            state["final_response"] = {
                "text": error_msg,
                "error": str(e),
                "intent": state.get("intent"),
                "drafts": [],
                "calendar_actions": [],
                "executed": [],
                "logs": []
            }
            state["error"] = str(e)

            return state

    def _summarize_emails(self, email_threads: list) -> str:
        """Create a brief summary of email context"""
        if not email_threads:
            return "No emails in context"

        count = len(email_threads)
        if count == 1:
            return f"1 email thread analyzed"
        return f"{count} email threads analyzed"

    def _summarize_calendar(self, calendar_events: list) -> str:
        """Create a brief summary of calendar context"""
        if not calendar_events:
            return "No calendar events in context"

        count = len(calendar_events)
        if count == 1:
            return f"1 calendar event found"
        return f"{count} calendar events found"
