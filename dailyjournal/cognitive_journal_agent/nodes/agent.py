"""
Tool Agent Node: Agentic execution using LangChain Agent Executor.
Enables the agent to autonomously use tools based on user commands.
"""

from typing import Dict, Any
import os
from langchain.agents import AgentExecutor, create_openai_functions_agent, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from tools.external_tools import get_all_tools


class ToolExecutionAgent:
    """
    LangChain-based agent that can autonomously execute tools.
    Fully configurable and extensible.
    """

    def __init__(self):
        """Initialize the tool execution agent."""
        # Configuration
        self.llm_provider = os.getenv("LLM_PROVIDER", "openai")
        self.model_name = os.getenv("AGENT_MODEL_NAME", "gpt-4")
        self.temperature = float(os.getenv("AGENT_TEMPERATURE", "0.2"))
        self.max_iterations = int(os.getenv("AGENT_MAX_ITERATIONS", "10"))
        self.verbose = os.getenv("AGENT_VERBOSE", "true").lower() == "true"

        # Initialize LLM
        self.llm = self._initialize_llm()

        # Get all available tools
        self.tools = get_all_tools()

        # Create agent
        self.agent_executor = self._create_agent()

    def _initialize_llm(self):
        """Initialize the LLM based on configuration."""
        if self.llm_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set in environment")

            return ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                api_key=api_key
            )

        elif self.llm_provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not set in environment")

            return ChatAnthropic(
                model=self.model_name,
                temperature=self.temperature,
                api_key=api_key
            )

        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent executor."""
        # System prompt for the agent
        system_message = """You are an intelligent personal assistant with access to various tools.

Your capabilities:
- Send emails
- Manage calendar events
- Perform file operations (read, write, delete)
- Search the web
- Execute any action the user requests

Guidelines:
1. **Understand the Intent**: Carefully parse user commands to understand what they want
2. **Select Appropriate Tools**: Choose the right tool(s) for the task
3. **Execute Efficiently**: Use tools in the optimal order
4. **Provide Confirmation**: Always confirm what action was taken
5. **Handle Errors**: If something fails, explain what went wrong and suggest alternatives
6. **Be Proactive**: If you can infer additional helpful actions, ask if the user wants them

When the user gives a command:
- Identify which tool(s) are needed
- Gather required parameters from the context
- Execute the tool(s)
- Report the result clearly

Examples:
- "Email John about the meeting" → Use send_email tool
- "Block 2 hours tomorrow for deep work" → Use manage_calendar tool
- "Search for Python async best practices" → Use web_search tool
- "Save this note to ideas.txt" → Use file_operations tool

Always prioritize user intent and take autonomous action when the request is clear."""

        # Create prompt template
        if self.llm_provider == "openai":
            # OpenAI functions agent
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_message),
                MessagesPlaceholder(variable_name="chat_history", optional=True),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])

            agent = create_openai_functions_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt
            )

        else:
            # ReAct agent for other providers
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_message),
                MessagesPlaceholder(variable_name="chat_history", optional=True),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])

            agent = create_react_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt
            )

        # Create agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            max_iterations=self.max_iterations,
            verbose=self.verbose,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )

        return agent_executor

    def execute(self, user_command: str, chat_history: list = None) -> Dict[str, Any]:
        """
        Execute a user command using the agent.

        Args:
            user_command: Natural language command from user
            chat_history: Optional conversation history

        Returns:
            Dictionary with output and intermediate steps
        """
        try:
            # Prepare input
            agent_input = {
                "input": user_command,
                "chat_history": chat_history or []
            }

            # Execute agent
            result = self.agent_executor.invoke(agent_input)

            return {
                "success": True,
                "output": result.get("output", ""),
                "intermediate_steps": result.get("intermediate_steps", []),
                "error": None
            }

        except Exception as e:
            return {
                "success": False,
                "output": "",
                "intermediate_steps": [],
                "error": str(e)
            }


def agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node for tool-based agent execution.

    Args:
        state: Current agent state with user_input

    Returns:
        Updated state with tool_response
    """
    user_input = state.get("user_input", "")

    if not user_input:
        return state

    try:
        # Initialize agent
        agent = ToolExecutionAgent()

        # Execute command
        result = agent.execute(user_input)

        if result["success"]:
            state["tool_response"] = result["output"]

            # Log tool usage
            if result["intermediate_steps"]:
                steps_summary = []
                for step in result["intermediate_steps"]:
                    if len(step) >= 2:
                        action, observation = step[0], step[1]
                        steps_summary.append(f"Tool: {action.tool}, Result: {str(observation)[:100]}")

                state["tool_execution_log"] = "\n".join(steps_summary)
        else:
            state["tool_response"] = f"Error executing command: {result['error']}"

    except Exception as e:
        state["tool_response"] = f"Agent error: {str(e)}"

    return state


class SimpleCommandExecutor:
    """
    Fallback command executor that doesn't require LLM.
    Uses rule-based command parsing for basic operations.
    """

    def __init__(self):
        """Initialize simple executor."""
        from tools.external_tools import (
            SendEmailTool,
            CalendarManagementTool,
            FileOperationsTool,
            WebSearchTool
        )

        self.tools = {
            "email": SendEmailTool(),
            "calendar": CalendarManagementTool(),
            "file": FileOperationsTool(),
            "search": WebSearchTool()
        }

    def execute(self, user_command: str) -> str:
        """
        Execute command using simple pattern matching.

        Args:
            user_command: User command

        Returns:
            Execution result
        """
        command_lower = user_command.lower()

        # Email commands
        if any(word in command_lower for word in ["email", "send email", "mail"]):
            return "Email command detected. Please provide recipient, subject, and body."

        # Calendar commands
        elif any(word in command_lower for word in ["calendar", "schedule", "meeting", "block time"]):
            return "Calendar command detected. Please provide event details."

        # File commands
        elif any(word in command_lower for word in ["file", "save", "write", "read"]):
            return "File operation detected. Please specify operation and file path."

        # Search commands
        elif any(word in command_lower for word in ["search", "find", "look up"]):
            return "Search command detected. Please specify search query."

        else:
            return "Command not recognized. Available commands: email, calendar, file operations, search"


def simple_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple agent node that doesn't require LLM API.
    Uses rule-based command execution.

    Args:
        state: Current agent state

    Returns:
        Updated state with tool_response
    """
    user_input = state.get("user_input", "")

    if not user_input:
        return state

    executor = SimpleCommandExecutor()
    response = executor.execute(user_input)

    state["tool_response"] = response

    return state
