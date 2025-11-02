"""
Voice Agent Graph Builder
Creates the LangGraph workflow for the voice agent system
"""

from langgraph.graph import StateGraph, END
from .state import VoiceAgentState
from ..agents.intent_agent import IntentClassificationAgent
from ..agents.context_agent import ContextRetrievalAgent
from ..agents.reasoning_agent import ReasoningAgent
from ..agents.draft_agent import DraftGenerationAgent
from ..agents.authorization_agent import AuthorizationAgent
from ..agents.execution_agent import ExecutionAgent
from ..agents.response_agent import ResponseGenerationAgent
from ..agents.logging_agent import LoggingAgent


def create_voice_agent_graph(email_adapter=None, calendar_adapter=None) -> StateGraph:
    """
    Creates the LangGraph for the voice-enabled email & calendar automation system.

    Pipeline Flow:
    1. Intent Classification → Determine what user wants
    2. Context Retrieval → Fetch relevant emails, calendar, history
    3. Reasoning → Assess priority, decide best action
    4. Draft Generation → Create email drafts or calendar proposals
    5. Authorization → Request auth code if needed
    6. Execution → Perform actions (send email, update calendar)
    7. Logging → Record all actions for audit trail

    This follows the gotoHuman-style human-in-the-loop pattern.
    """

    # Initialize the graph
    workflow = StateGraph(VoiceAgentState)

    # Initialize agents with adapters
    intent_agent = IntentClassificationAgent()
    context_agent = ContextRetrievalAgent(email_adapter=email_adapter, calendar_adapter=calendar_adapter)

    # Get model configuration from environment
    # ReasoningAgent will automatically load FALLBACK_MODELS from .env
    import os
    model_name = os.getenv("MODEL_NAME", "gpt-4")

    # Initialize reasoning agent with cascading fallback support
    # It will automatically parse FALLBACK_MODELS env var (e.g., "deepseek-chat,grok-2,gpt-4o-mini,gemini-1.5-pro")
    reasoning_agent = ReasoningAgent(model_name=model_name)

    draft_agent = DraftGenerationAgent()
    auth_agent = AuthorizationAgent()
    execution_agent = ExecutionAgent(email_adapter=email_adapter, calendar_adapter=calendar_adapter)
    response_agent = ResponseGenerationAgent()
    logging_agent = LoggingAgent()

    # Add nodes to the graph
    workflow.add_node("classify_intent", intent_agent.run)
    workflow.add_node("retrieve_context", context_agent.run)
    workflow.add_node("reason", reasoning_agent.run)
    workflow.add_node("generate_drafts", draft_agent.run)
    workflow.add_node("check_authorization", auth_agent.run)
    workflow.add_node("execute_actions", execution_agent.run)
    workflow.add_node("generate_response", response_agent.run)
    workflow.add_node("log_actions", logging_agent.run)

    # Set entry point
    workflow.set_entry_point("classify_intent")

    # Define edges (flow)
    workflow.add_edge("classify_intent", "retrieve_context")
    workflow.add_edge("retrieve_context", "reason")
    workflow.add_edge("reason", "generate_drafts")

    # Conditional edge: Check if authorization is needed
    def needs_authorization(state: VoiceAgentState) -> str:
        """Route based on whether authorization is required"""
        if state.get("requires_authorization", False):
            # If auth code is provided, go straight to execution
            if state.get("authorization_code"):
                return "execute_actions"
            # Otherwise, ask for authorization
            return "check_authorization"
        # No authorization needed (e.g., just generating drafts, reading inbox)
        return "generate_response"

    workflow.add_conditional_edges(
        "generate_drafts",
        needs_authorization,
        {
            "check_authorization": "check_authorization",
            "execute_actions": "execute_actions",
            "generate_response": "generate_response"
        }
    )

    # Authorization flow
    def authorization_result(state: VoiceAgentState) -> str:
        """Route based on authorization status"""
        auth_code = state.get("authorization_code")
        if auth_code:
            # User provided code, proceed to execution
            return "execute_actions"
        # No code provided yet, wait for user input (end for now)
        return "end_awaiting_auth"

    workflow.add_conditional_edges(
        "check_authorization",
        authorization_result,
        {
            "execute_actions": "execute_actions",
            "end_awaiting_auth": "generate_response"
        }
    )

    # After execution, generate friendly response
    workflow.add_edge("execute_actions", "generate_response")

    # After response generation, log everything
    workflow.add_edge("generate_response", "log_actions")

    # Log actions is the final step
    workflow.add_edge("log_actions", END)

    return workflow.compile()
