"""
LangGraph Workflow Definition for Cognitive Journal Agent.
Defines the state machine, nodes, edges, and routing logic.
"""

from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
import os

# Import all node functions
from nodes.ingestion import ingestion_node
from nodes.processing import processing_node
from nodes.storage import storage_node
from nodes.reporting import reporting_node
from nodes.output import tts_node
from nodes.agent import agent_node


# ===========================
# State Definition
# ===========================

class AgentState(TypedDict):
    """
    LangGraph state containing all workflow data.
    TypedDict is used instead of Pydantic for LangGraph compatibility.
    """
    # Input
    user_input: str
    input_data: Dict[str, Any]

    # Processing
    new_entry: Any  # JournalEntry
    all_entries: list  # List[JournalEntry]
    pending_actions: list  # List[ActionItem]

    # Output
    final_report: Any  # FinalAgentReport
    audio_output_path: str
    tool_response: str
    tool_execution_log: str

    # Routing
    current_route: str
    next_step: str


# ===========================
# Router Logic
# ===========================

def route_input(state: AgentState) -> str:
    """
    Router function that determines the next step based on input.
    This is used in conditional_edges, not as a node.

    Routes:
    - "action_command" → Tool Agent (for immediate actions)
    - "journal_input" → Ingestion (for journal entries)
    - "summarize" → Reporting (for generating summaries)

    Args:
        state: Current agent state

    Returns:
        Next node name
    """
    user_input = state.get("user_input", "").lower()

    # Keywords that indicate action commands
    action_keywords = [
        "send email", "schedule", "calendar", "block time",
        "add event", "create meeting", "search for",
        "find", "read file", "write file", "delete"
    ]

    # Keywords that indicate summary request
    summary_keywords = [
        "summarize", "summary", "report", "review",
        "what did i do", "daily report", "journal summary"
    ]

    # Check for summary request
    if any(keyword in user_input for keyword in summary_keywords):
        return "reporting"

    # Check for action command
    if any(keyword in user_input for keyword in action_keywords):
        return "agent"

    # Default: treat as journal input
    return "ingestion"


def route_after_agent(state: AgentState) -> str:
    """
    Router after agent execution.
    Determines whether to store the tool response as a journal entry.

    Args:
        state: Current agent state

    Returns:
        Next node name
    """
    tool_response = state.get("tool_response", "")

    # If there's a meaningful response, create a journal entry for it
    if tool_response and len(tool_response) > 10:
        # Create a journal entry for the tool execution
        state["input_data"] = {
            "type": "text_note",
            "content": f"Action executed: {state.get('user_input')}\nResult: {tool_response}"
        }
        return "ingestion"
    else:
        return "end"


def route_after_storage(state: AgentState) -> str:
    """
    Router after storage.
    Determines whether to end or continue.

    Args:
        state: Current agent state

    Returns:
        Next node name
    """
    return "end"


def route_after_reporting(state: AgentState) -> str:
    """
    Router after reporting.
    Determines whether to generate audio output.

    Args:
        state: Current agent state

    Returns:
        Next node name
    """
    # Check if TTS is enabled
    tts_enabled = os.getenv("TTS_ENABLED", "true").lower() == "true"

    if tts_enabled and state.get("final_report"):
        return "tts"
    else:
        return "end"


# ===========================
# Graph Construction
# ===========================

def create_agent_graph() -> StateGraph:
    """
    Create the LangGraph workflow.

    Graph Structure:
    - Start → Router
    - Router → [Agent, Ingestion, Reporting]
    - Agent → Router (after agent)
    - Ingestion → Processing → Storage → End
    - Reporting → TTS → End

    Returns:
        Compiled StateGraph
    """
    # Initialize graph
    workflow = StateGraph(AgentState)

    # ===========================
    # Add Nodes
    # ===========================
    workflow.add_node("ingestion", ingestion_node)
    workflow.add_node("processing", processing_node)
    workflow.add_node("storage", storage_node)
    workflow.add_node("reporting", reporting_node)
    workflow.add_node("tts", tts_node)
    workflow.add_node("agent", agent_node)

    # ===========================
    # Add Edges
    # ===========================

    # Entry point with conditional routing
    workflow.set_conditional_entry_point(
        route_input,
        {
            "ingestion": "ingestion",
            "agent": "agent",
            "reporting": "reporting"
        }
    )

    # Journal input flow: Ingestion → Processing → Storage → End
    workflow.add_edge("ingestion", "processing")
    workflow.add_edge("processing", "storage")
    workflow.add_edge("storage", END)

    # Agent flow: Agent → Ingestion (to log) or End
    workflow.add_conditional_edges(
        "agent",
        route_after_agent,
        {
            "ingestion": "ingestion",
            "end": END
        }
    )

    # Reporting flow: Reporting → TTS → End
    workflow.add_conditional_edges(
        "reporting",
        route_after_reporting,
        {
            "tts": "tts",
            "end": END
        }
    )

    workflow.add_edge("tts", END)

    # Compile graph
    return workflow.compile()


# ===========================
# Helper Functions
# ===========================

def run_agent(user_input: str, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Run the agent with user input.

    Args:
        user_input: Natural language input from user
        input_data: Optional structured input data

    Returns:
        Final state after execution
    """
    # Create graph
    graph = create_agent_graph()

    # Initialize state
    initial_state = {
        "user_input": user_input,
        "input_data": input_data or {},
        "new_entry": None,
        "all_entries": [],
        "pending_actions": [],
        "final_report": None,
        "audio_output_path": "",
        "tool_response": "",
        "tool_execution_log": "",
        "current_route": "",
        "next_step": ""
    }

    # Execute graph
    final_state = graph.invoke(initial_state)

    return final_state


def visualize_graph():
    """
    Generate a visualization of the graph.
    Requires: graphviz, pygraphviz
    """
    try:
        from IPython.display import Image, display

        graph = create_agent_graph()

        # Generate image
        img = graph.get_graph().draw_mermaid_png()

        # Save to file
        output_path = "agent_graph.png"
        with open(output_path, "wb") as f:
            f.write(img)

        print(f"Graph visualization saved to: {output_path}")

        return img

    except ImportError:
        print("Visualization requires IPython, graphviz, and pygraphviz")
        return None
    except Exception as e:
        print(f"Error generating visualization: {e}")
        return None


# ===========================
# Advanced Features
# ===========================

class AgentWithMemory:
    """
    Agent wrapper that maintains conversation memory.
    Useful for multi-turn interactions.
    """

    def __init__(self):
        """Initialize agent with memory."""
        self.graph = create_agent_graph()
        self.conversation_history = []
        self.session_entries = []

    def execute(self, user_input: str, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute with memory context.

        Args:
            user_input: User input
            input_data: Optional structured data

        Returns:
            Execution result
        """
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": user_input})

        # Run agent
        state = {
            "user_input": user_input,
            "input_data": input_data or {},
            "new_entry": None,
            "all_entries": self.session_entries,
            "pending_actions": [],
            "final_report": None,
            "audio_output_path": "",
            "tool_response": "",
            "tool_execution_log": "",
            "current_route": "",
            "next_step": ""
        }

        final_state = self.graph.invoke(state)

        # Update session entries
        if final_state.get("new_entry"):
            self.session_entries.append(final_state["new_entry"])

        # Add response to history
        response = final_state.get("tool_response") or "Entry recorded successfully"
        self.conversation_history.append({"role": "assistant", "content": response})

        return final_state

    def clear_memory(self):
        """Clear conversation memory."""
        self.conversation_history = []
        self.session_entries = []


# ===========================
# Streaming Support
# ===========================

async def stream_agent(user_input: str, input_data: Dict[str, Any] = None):
    """
    Stream agent execution (for async/real-time applications).

    Args:
        user_input: User input
        input_data: Optional structured data

    Yields:
        State updates as they occur
    """
    graph = create_agent_graph()

    initial_state = {
        "user_input": user_input,
        "input_data": input_data or {},
        "new_entry": None,
        "all_entries": [],
        "pending_actions": [],
        "final_report": None,
        "audio_output_path": "",
        "tool_response": "",
        "tool_execution_log": "",
        "current_route": "",
        "next_step": ""
    }

    # Stream execution
    async for state in graph.astream(initial_state):
        yield state
