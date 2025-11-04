"""
Processing Node: LLM-based content analysis.
Extracts contextual tags, action items, and emotional tone from journal entries.
Uses LangChain with structured output via Pydantic.
"""

from typing import Dict, Any, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field
import os

from data_models.pydantic_schemas import JournalEntry


# ===========================
# Pydantic Models for LLM Output
# ===========================

class ProcessedContent(BaseModel):
    """Structured output from the processing LLM."""
    contextual_tags: List[str] = Field(
        description="Categorized tags from: [Work, Personal, Task, Idea, Reference, Urgent, Meeting, Health, Finance, Learning, Creative]"
    )
    extracted_action_items: List[str] = Field(
        description="Specific, executable action phrases (e.g., 'Email John about project', 'Review budget')"
    )
    inferred_emotion: Optional[str] = Field(
        description="Emotional tone from: [High Focus, Stressed, Reflective, Routine, Excited, Concerned, Neutral]"
    )
    priority_score: int = Field(
        description="Priority score from 1-10, where 10 is most urgent/important"
    )
    key_entities: List[str] = Field(
        default=[],
        description="Important entities mentioned: people, places, projects, dates"
    )


class ProcessEntry:
    """
    LLM-based processing for journal entries.
    Configurable to use different LLM providers.
    """

    def __init__(self):
        """Initialize the processor with configured LLM."""
        # Configuration
        self.llm_provider = os.getenv("LLM_PROVIDER", "openai")  # openai, anthropic, or ollama
        self.model_name = os.getenv("LLM_MODEL_NAME", "gpt-4")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.3"))

        # Initialize LLM
        self.llm = self._initialize_llm()

        # Create output parser
        self.output_parser = PydanticOutputParser(pydantic_object=ProcessedContent)

        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("user", "{input_content}\n\n{format_instructions}")
        ])

        # Create chain
        self.chain = self.prompt | self.llm | self.output_parser

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

    def _get_system_prompt(self) -> str:
        """Get the system prompt for processing."""
        return """You are an intelligent journal entry analyzer. Your role is to:

1. **Extract Contextual Tags**: Categorize the content using relevant tags
   - Available tags: Work, Personal, Task, Idea, Reference, Urgent, Meeting, Health, Finance, Learning, Creative
   - Use multiple tags if applicable
   - Be specific and accurate

2. **Identify Action Items**: Extract concrete, actionable tasks
   - Each action should be specific and executable
   - Format: Clear verb + object (e.g., "Email John about Q3 report")
   - Exclude vague items like "think about" or "consider"

3. **Infer Emotional Tone**: Detect the emotional context
   - Options: High Focus, Stressed, Reflective, Routine, Excited, Concerned, Neutral
   - Base this on language patterns, urgency, and content type

4. **Assign Priority Score**: Rate urgency/importance (1-10)
   - 10: Critical, time-sensitive, high-impact
   - 7-9: Important, near-term deadlines
   - 4-6: Moderate importance
   - 1-3: Low priority, informational

5. **Extract Key Entities**: Identify important names, places, projects, dates
   - People: Names of individuals mentioned
   - Projects: Project names or initiatives
   - Dates: Specific dates or deadlines
   - Organizations: Companies or teams

Analyze the following journal entry and provide structured output."""

    def process(self, journal_entry: JournalEntry) -> JournalEntry:
        """
        Process a journal entry using LLM analysis.

        Args:
            journal_entry: JournalEntry with raw_content populated

        Returns:
            JournalEntry with processed fields filled
        """
        try:
            # Prepare input
            format_instructions = self.output_parser.get_format_instructions()

            # Run LLM chain
            result: ProcessedContent = self.chain.invoke({
                "input_content": journal_entry.raw_content,
                "format_instructions": format_instructions
            })

            # Update journal entry with processed data
            journal_entry.contextual_tags = result.contextual_tags
            journal_entry.extracted_action_items = result.extracted_action_items
            journal_entry.inferred_emotion = result.inferred_emotion

            return journal_entry

        except Exception as e:
            # Fallback: return entry with error tags
            print(f"Error processing entry: {e}")
            journal_entry.contextual_tags = ["Processing Error"]
            journal_entry.extracted_action_items = []
            journal_entry.inferred_emotion = "Neutral"

            return journal_entry


class SimpleProcessor:
    """
    Fallback processor that doesn't require LLM API.
    Uses rule-based heuristics for basic processing.
    """

    def __init__(self):
        """Initialize the simple processor."""
        self.action_verbs = [
            "email", "call", "schedule", "review", "complete", "finish",
            "send", "prepare", "write", "update", "fix", "create", "plan"
        ]

        self.urgency_keywords = [
            "urgent", "asap", "critical", "important", "deadline",
            "immediately", "priority", "emergency"
        ]

        self.emotion_keywords = {
            "Stressed": ["stress", "overwhelm", "pressure", "anxious", "worried"],
            "Excited": ["excited", "great", "amazing", "wonderful", "thrilled"],
            "Concerned": ["concern", "worried", "issue", "problem", "trouble"],
            "High Focus": ["focus", "concentrate", "deep work", "productive"],
            "Reflective": ["reflect", "think", "consider", "ponder", "contemplate"]
        }

    def process(self, journal_entry: JournalEntry) -> JournalEntry:
        """
        Process entry using rule-based approach.

        Args:
            journal_entry: JournalEntry with raw_content populated

        Returns:
            JournalEntry with processed fields filled
        """
        content_lower = journal_entry.raw_content.lower()

        # Extract tags based on input type and keywords
        tags = []

        if journal_entry.input_type == "email":
            tags.append("Work")
        elif journal_entry.input_type == "calendar_event":
            tags.extend(["Work", "Meeting"])
        elif journal_entry.input_type == "code_snippet":
            tags.extend(["Work", "Reference"])

        # Check for urgency
        if any(keyword in content_lower for keyword in self.urgency_keywords):
            tags.append("Urgent")

        # Check for task indicators
        if any(verb in content_lower for verb in self.action_verbs):
            tags.append("Task")

        # Set default tags if none found
        if not tags:
            tags.append("Personal")

        journal_entry.contextual_tags = list(set(tags))

        # Extract action items (simple sentence extraction)
        action_items = []
        sentences = journal_entry.raw_content.split(".")

        for sentence in sentences:
            sentence_lower = sentence.lower().strip()
            if any(verb in sentence_lower for verb in self.action_verbs):
                action_items.append(sentence.strip())

        journal_entry.extracted_action_items = action_items[:5]  # Limit to 5

        # Infer emotion
        detected_emotion = "Routine"
        for emotion, keywords in self.emotion_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                detected_emotion = emotion
                break

        journal_entry.inferred_emotion = detected_emotion

        return journal_entry


def processing_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node for processing journal entries.

    Args:
        state: Current agent state with new_entry populated

    Returns:
        Updated state with processed new_entry
    """
    new_entry = state.get("new_entry")

    if not new_entry:
        return state

    # Determine which processor to use
    use_llm = os.getenv("USE_LLM_PROCESSING", "true").lower() == "true"

    try:
        if use_llm:
            processor = ProcessEntry()
        else:
            processor = SimpleProcessor()

        # Process the entry
        processed_entry = processor.process(new_entry)

        # Update state
        state["new_entry"] = processed_entry

    except Exception as e:
        print(f"Error in processing node: {e}")
        # Use fallback processor
        fallback_processor = SimpleProcessor()
        processed_entry = fallback_processor.process(new_entry)
        state["new_entry"] = processed_entry

    return state
