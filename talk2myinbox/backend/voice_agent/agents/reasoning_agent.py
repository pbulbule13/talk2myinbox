"""
Reasoning Agent
Analyzes context and decides the best course of action
"""

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from ..graph.state import VoiceAgentState
import json
import os


class ReasoningAgent:
    """
    Reasons about emails, calendar, and context to determine:
    - Priority of emails
    - Whether to accept/decline meetings
    - What actions to take
    - Tone and approach for communications

    Supports cascading fallback through multiple models when token limits are exceeded.
    """

    def __init__(self, model_name: str = "gpt-4", fallback_models: list = None):
        """
        Initialize ReasoningAgent with cascading fallback models.

        Args:
            model_name: Primary model to use
            fallback_models: List of model names to try in order if token limit exceeded
        """
        self.model_name = model_name
        self.primary_llm = self._create_llm_client(model_name)

        # Parse fallback models from environment or use provided list
        if fallback_models is None:
            fallback_models_str = os.getenv("FALLBACK_MODELS", "gpt-4o-mini")
            fallback_models = [m.strip() for m in fallback_models_str.split(",")]

        self.fallback_models = fallback_models
        self.fallback_llms = [self._create_llm_client(model) for model in fallback_models]

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the reasoning engine for {agent_name}, a highly capable executive assistant to a busy CEO.

**Your Mission:**
Act as the CEO's trusted personal secretary. Your role is to protect their time, anticipate their needs, and help them focus on what truly matters. Think strategically about how each communication or meeting impacts their goals and priorities.

**Analysis Framework:**
Analyze emails, calendar events, and context to determine:

1. **Priority Level** (urgent/high/medium/low) and WHY
   - Consider business impact, time sensitivity, sender importance
   - Flag anything that could become urgent if delayed

2. **Recommended Action** (specific and actionable)
   - reply: Draft a response (specify tone and key points)
   - schedule: Propose meeting times (check calendar first)
   - decline: Politely decline with reason
   - delegate: Suggest who should handle this
   - snooze: When to revisit
   - archive: Low priority, no action needed

3. **Strategic Reasoning**
   - Explain your thinking like a trusted advisor
   - Consider: sender relationship, urgency, CEO's schedule, business priorities
   - Be proactive: suggest follow-ups or related actions

**Context to Consider:**
- Sender relationship and history
- Urgency indicators and deadlines
- CEO's current calendar and availability
- Previous interactions and context
- VIP senders and partners: {vip_domains}
- Business priorities and strategic goals

**Your Personality:**
- Protective of the CEO's time and attention
- Proactive and anticipatory
- Clear and decisive in recommendations
- Explain reasoning like a knowledgeable colleague
- Think beyond the immediate request

Be thorough but concise - every minute of the CEO's time is valuable."""),
            ("human", """**Current Situation:**
Intent: {intent}
CEO's Request: "{query}"

**Email Context:**
{email_context}

**Calendar Context:**
{calendar_context}

**Sender History:**
{sender_history}

**Your Analysis:**
Provide a strategic analysis with:
1. Priority assessment with clear reasoning
2. Specific recommended action
3. Strategic considerations and next steps""")
        ])

    def _create_llm_client(self, model_name: str):
        """
        Create appropriate LLM client based on model name.

        Supports:
        - OpenAI models (gpt-*, deepseek-*, grok-*)
        - Anthropic models (claude-*)
        - Google models (gemini-*)
        """
        model_lower = model_name.lower()

        try:
            # Anthropic models
            if "claude" in model_lower or "anthropic" in model_lower:
                return ChatAnthropic(model=model_name, temperature=0.7)

            # Google Gemini models
            elif "gemini" in model_lower:
                return ChatGoogleGenerativeAI(model=model_name, temperature=0.7)

            # OpenAI and OpenAI-compatible models (GPT, DeepSeek, Grok, etc.)
            else:
                # For DeepSeek and Grok, they use OpenAI-compatible APIs
                # DeepSeek uses base_url="https://api.deepseek.com"
                # Grok uses base_url="https://api.x.ai/v1"
                if "deepseek" in model_lower:
                    # DeepSeek uses OpenAI-compatible API
                    return ChatOpenAI(
                        model=model_name,
                        temperature=0.7,
                        openai_api_base=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"),
                        openai_api_key=os.getenv("DEEPSEEK_API_KEY", os.getenv("OPENAI_API_KEY"))
                    )
                elif "grok" in model_lower:
                    # Grok uses OpenAI-compatible API
                    return ChatOpenAI(
                        model=model_name,
                        temperature=0.7,
                        openai_api_base=os.getenv("GROK_API_BASE", "https://api.x.ai/v1"),
                        openai_api_key=os.getenv("GROK_API_KEY", os.getenv("OPENAI_API_KEY"))
                    )
                else:
                    # Standard OpenAI models
                    return ChatOpenAI(model=model_name, temperature=0.7)

        except Exception as e:
            print(f"[WARNING] Failed to create LLM client for {model_name}: {e}")
            # Fallback to standard OpenAI client
            return ChatOpenAI(model=model_name, temperature=0.7)

    async def run(self, state: VoiceAgentState) -> VoiceAgentState:
        """Run reasoning analysis with cascading fallback"""
        intent = state["intent"]
        query = state["user_query"]

        # Prepare context
        email_context = json.dumps(state.get("email_threads", []), indent=2)
        calendar_context = json.dumps(state.get("calendar_events", []), indent=2)
        sender_history = json.dumps(state.get("sender_history", {}), indent=2)

        # Get settings (in real implementation, load from config)
        agent_name = os.getenv("VOICE_AGENT_voice_agent_name", "Vinegar")
        vip_domains = ["partner.com", "investor.org"]

        # Prepare prompt
        prompt_value = self.prompt.format_messages(
            agent_name=agent_name,
            vip_domains=", ".join(vip_domains),
            intent=intent,
            query=query,
            email_context=email_context,
            calendar_context=calendar_context,
            sender_history=sender_history
        )

        # Try primary model first, then cascade through fallbacks
        models_to_try = [(self.model_name, self.primary_llm)] + list(zip(self.fallback_models, self.fallback_llms))

        last_error = None
        for model_name, llm_client in models_to_try:
            try:
                print(f"[LLM] Attempting reasoning with model: {model_name}")
                response = await llm_client.ainvoke(prompt_value)
                reasoning_text = response.content

                # Parse the reasoning (in production, use structured output)
                state["reasoning"] = reasoning_text
                state["priority_assessment"] = self._extract_priority(reasoning_text)
                state["recommended_action"] = self._extract_action(reasoning_text)
                state["model_used"] = model_name

                print(f"[SUCCESS] Completed reasoning with model: {model_name}")
                return state

            except Exception as e:
                error_str = str(e)
                last_error = e

                # Check if it's a context length error that we should retry
                is_token_error = (
                    "context_length_exceeded" in error_str or
                    "maximum context length" in error_str.lower() or
                    "token limit" in error_str.lower() or
                    "too many tokens" in error_str.lower()
                )

                if is_token_error:
                    print(f"[WARNING] Token limit exceeded on {model_name}, trying next fallback model...")
                    continue  # Try next model
                else:
                    # Non-token error, still try fallback but log it
                    print(f"[WARNING] Error with {model_name}: {error_str}")
                    continue  # Try next model anyway

        # If we get here, all models failed
        print(f"[ERROR] All models failed. Last error: {str(last_error)}")
        state["error"] = f"All models failed. Last error: {str(last_error)}"
        state["reasoning"] = "Unable to analyze context - all models exhausted"
        state["recommended_action"] = "manual_review"

        return state

    def _extract_priority(self, reasoning: str) -> dict:
        """Extract priority assessment from reasoning text"""
        # Simple keyword-based extraction (in production, use structured output)
        if "high priority" in reasoning.lower() or "urgent" in reasoning.lower():
            return {"level": "high", "reason": "Urgent or high-priority sender"}
        elif "low priority" in reasoning.lower():
            return {"level": "low", "reason": "Routine or informational"}
        else:
            return {"level": "medium", "reason": "Standard priority"}

    def _extract_action(self, reasoning: str) -> str:
        """Extract recommended action from reasoning text"""
        reasoning_lower = reasoning.lower()
        if "draft a reply" in reasoning_lower or "respond" in reasoning_lower:
            return "draft_reply"
        elif "decline" in reasoning_lower:
            return "decline_meeting"
        elif "accept" in reasoning_lower:
            return "accept_meeting"
        elif "schedule" in reasoning_lower:
            return "propose_meeting"
        else:
            return "review"
