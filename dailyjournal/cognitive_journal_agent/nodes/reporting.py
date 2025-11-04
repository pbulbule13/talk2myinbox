"""
Reporting Node: Generates daily summaries and action plans.
Uses LLM to synthesize journal entries into structured reports.
"""

from typing import Dict, Any, List
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import os

from data_models.pydantic_schemas import (
    JournalEntry,
    ActionItem,
    DailySummaryOutput,
    FinalAgentReport
)


class DailyReporter:
    """
    LLM-based daily summary and action planning.
    Synthesizes all journal entries into a cohesive narrative and actionable plan.
    """

    def __init__(self):
        """Initialize the reporter with configured LLM."""
        # Configuration
        self.llm_provider = os.getenv("LLM_PROVIDER", "openai")
        self.model_name = os.getenv("LLM_MODEL_NAME", "gpt-4")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.5"))

        # Initialize LLM
        self.llm = self._initialize_llm()

        # Create output parser
        self.output_parser = PydanticOutputParser(pydantic_object=FinalAgentReport)

        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("user", "{journal_content}\n\n{format_instructions}")
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
        """Get the system prompt for report generation."""
        return """You are an intelligent personal assistant that synthesizes daily journal entries into meaningful insights and actionable plans.

Your responsibilities:

1. **Daily Theme**: Identify the overarching theme or focus of the day
   - What was the main area of work or attention?
   - What patterns emerge across entries?
   - Summarize in one clear, concise sentence

2. **Key Decisions & Learnings**: Extract the most important insights
   - Decisions made (3-5 bullet points)
   - Lessons learned
   - Important realizations
   - Progress on goals

3. **Journal Narrative**: Create a brief, coherent story of the day
   - 2-3 paragraphs
   - Capture emotional arc and progression
   - Connect different entries thematically
   - Write in a reflective, personal tone

4. **Pending Actions**: Organize and prioritize action items
   - Extract all actionable tasks from entries
   - Assign realistic priorities (P1=Urgent, P2=High, P3=Medium)
   - Each action must be specific and executable
   - Include source context

5. **Suggested First Task**: Recommend the best task to start tomorrow
   - Consider urgency, importance, and momentum
   - Explain why this task should be first
   - Make it motivating

Guidelines:
- Be insightful but concise
- Focus on what matters most
- Maintain a supportive, reflective tone
- Connect patterns across entries
- Prioritize ruthlessly

Analyze the following journal entries and generate a comprehensive daily report."""

    def _format_journal_entries(self, entries: List[JournalEntry]) -> str:
        """Format journal entries for LLM input."""
        if not entries:
            return "No journal entries recorded today."

        formatted = []
        for idx, entry in enumerate(entries, 1):
            formatted.append(f"""
--- Entry {idx} ---
Time: {entry.timestamp.strftime('%Y-%m-%d %H:%M')}
Type: {entry.input_type}
Content: {entry.raw_content}
Tags: {', '.join(entry.contextual_tags)}
Emotion: {entry.inferred_emotion or 'N/A'}
""")

        return "\n".join(formatted)

    def generate_report(
        self,
        entries: List[JournalEntry],
        existing_actions: List[ActionItem]
    ) -> FinalAgentReport:
        """
        Generate a comprehensive daily report.

        Args:
            entries: List of journal entries from the day
            existing_actions: Previously extracted action items

        Returns:
            FinalAgentReport with summary and action plan
        """
        try:
            # Format entries for input
            journal_content = self._format_journal_entries(entries)

            # Get format instructions
            format_instructions = self.output_parser.get_format_instructions()

            # Generate report using LLM
            report: FinalAgentReport = self.chain.invoke({
                "journal_content": journal_content,
                "format_instructions": format_instructions
            })

            return report

        except Exception as e:
            print(f"Error generating report: {e}")

            # Fallback: Create basic report
            return self._generate_fallback_report(entries, existing_actions)

    def _generate_fallback_report(
        self,
        entries: List[JournalEntry],
        existing_actions: List[ActionItem]
    ) -> FinalAgentReport:
        """Generate a basic report without LLM."""
        # Count entries by type
        entry_types = {}
        for entry in entries:
            entry_types[entry.input_type] = entry_types.get(entry.input_type, 0) + 1

        # Basic summary
        daily_theme = f"Recorded {len(entries)} journal entries today"

        key_decisions = []
        for entry in entries[:5]:
            if entry.contextual_tags:
                key_decisions.append(f"{', '.join(entry.contextual_tags)}: {entry.raw_content[:100]}...")

        journal_narrative = f"Today you recorded {len(entries)} entries across various activities. "
        journal_narrative += f"Primary focus areas: {', '.join(entry_types.keys())}."

        summary = DailySummaryOutput(
            date=datetime.now().strftime('%Y-%m-%d'),
            daily_theme=daily_theme,
            key_decisions_and_learnings=key_decisions[:5],
            journal_narrative=journal_narrative
        )

        # Use existing actions or extract from entries
        if not existing_actions:
            existing_actions = []
            for entry in entries:
                for action_text in entry.extracted_action_items:
                    existing_actions.append(ActionItem(
                        task_id=f"action_{len(existing_actions)}",
                        task_description=action_text,
                        priority="P2",
                        source_entry_id=entry.source_id
                    ))

        # Sort by priority
        existing_actions.sort(key=lambda x: x.priority)

        suggested_first = existing_actions[0].task_description if existing_actions else "Review your journal entries"

        return FinalAgentReport(
            summary=summary,
            pending_actions=existing_actions[:10],  # Limit to top 10
            suggested_first_task=suggested_first
        )


class SimpleSummaryGenerator:
    """
    Fallback summary generator that doesn't require LLM.
    Uses rule-based approach for basic reporting.
    """

    def generate_report(
        self,
        entries: List[JournalEntry],
        existing_actions: List[ActionItem]
    ) -> FinalAgentReport:
        """Generate a basic report using rule-based approach."""
        if not entries:
            return FinalAgentReport(
                summary=DailySummaryOutput(
                    date=datetime.now().strftime('%Y-%m-%d'),
                    daily_theme="No entries recorded today",
                    key_decisions_and_learnings=[],
                    journal_narrative="No journal entries were recorded today."
                ),
                pending_actions=[],
                suggested_first_task="Start by recording your first journal entry"
            )

        # Analyze entries
        total_entries = len(entries)
        entry_types = {}
        all_tags = []
        emotions = []

        for entry in entries:
            # Count types
            entry_types[entry.input_type] = entry_types.get(entry.input_type, 0) + 1

            # Collect tags
            all_tags.extend(entry.contextual_tags)

            # Collect emotions
            if entry.inferred_emotion:
                emotions.append(entry.inferred_emotion)

        # Most common tags
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:3]

        # Generate summary
        daily_theme = f"Recorded {total_entries} entries focusing on: {', '.join([tag for tag, _ in top_tags])}"

        key_decisions = []
        for entry in entries[:5]:
            if entry.raw_content:
                key_decisions.append(entry.raw_content[:100] + "...")

        journal_narrative = f"Today you captured {total_entries} journal entries. "
        if entry_types:
            journal_narrative += f"Activity breakdown: {', '.join([f'{count} {type}' for type, count in entry_types.items()])}. "
        if emotions:
            most_common_emotion = max(set(emotions), key=emotions.count)
            journal_narrative += f"Overall emotional tone: {most_common_emotion}."

        summary = DailySummaryOutput(
            date=datetime.now().strftime('%Y-%m-%d'),
            daily_theme=daily_theme,
            key_decisions_and_learnings=key_decisions,
            journal_narrative=journal_narrative
        )

        # Organize actions by priority
        if not existing_actions:
            existing_actions = []
            for entry in entries:
                for idx, action_text in enumerate(entry.extracted_action_items):
                    priority = "P1" if "Urgent" in entry.contextual_tags else "P2"
                    existing_actions.append(ActionItem(
                        task_id=f"{entry.source_id}_action_{idx}",
                        task_description=action_text,
                        priority=priority,
                        source_entry_id=entry.source_id
                    ))

        # Sort by priority
        existing_actions.sort(key=lambda x: x.priority)

        suggested_first = existing_actions[0].task_description if existing_actions else "Review your journal"

        return FinalAgentReport(
            summary=summary,
            pending_actions=existing_actions[:10],
            suggested_first_task=suggested_first
        )


def reporting_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node for report generation.

    Args:
        state: Current agent state with all_entries and pending_actions

    Returns:
        Updated state with final_report populated
    """
    all_entries = state.get("all_entries", [])
    pending_actions = state.get("pending_actions", [])

    # Determine which reporter to use
    use_llm = os.getenv("USE_LLM_REPORTING", "true").lower() == "true"

    try:
        if use_llm:
            reporter = DailyReporter()
        else:
            reporter = SimpleSummaryGenerator()

        # Generate report
        report = reporter.generate_report(all_entries, pending_actions)

        # Update state
        state["final_report"] = report

    except Exception as e:
        print(f"Error in reporting node: {e}")

        # Use fallback
        fallback_reporter = SimpleSummaryGenerator()
        report = fallback_reporter.generate_report(all_entries, pending_actions)
        state["final_report"] = report

    return state
