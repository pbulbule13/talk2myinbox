"""
Tests for Pydantic schemas.
"""

import pytest
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from data_models.pydantic_schemas import (
    JournalEntry,
    DailySummaryOutput,
    ActionItem,
    FinalAgentReport,
    AgentState
)


class TestJournalEntry:
    """Tests for JournalEntry model."""

    def test_journal_entry_creation(self):
        """Test basic journal entry creation."""
        entry = JournalEntry(
            timestamp=datetime.now(),
            input_type="text_note",
            raw_content="Test content",
            source_id="test_123"
        )

        assert entry.input_type == "text_note"
        assert entry.raw_content == "Test content"
        assert entry.source_id == "test_123"
        assert entry.contextual_tags == []
        assert entry.extracted_action_items == []
        assert entry.inferred_emotion is None

    def test_journal_entry_with_processed_fields(self):
        """Test journal entry with processed fields."""
        entry = JournalEntry(
            timestamp=datetime.now(),
            input_type="email",
            raw_content="Important meeting notes",
            source_id="email_456",
            contextual_tags=["Work", "Meeting", "Urgent"],
            extracted_action_items=["Send follow-up email"],
            inferred_emotion="High Focus"
        )

        assert len(entry.contextual_tags) == 3
        assert "Work" in entry.contextual_tags
        assert len(entry.extracted_action_items) == 1
        assert entry.inferred_emotion == "High Focus"


class TestDailySummaryOutput:
    """Tests for DailySummaryOutput model."""

    def test_daily_summary_creation(self):
        """Test daily summary creation."""
        summary = DailySummaryOutput(
            date="2024-01-01",
            daily_theme="Productive day focused on project work",
            key_decisions_and_learnings=[
                "Decided to use LangGraph for workflow",
                "Learned about Pydantic output parsers"
            ],
            journal_narrative="Today was highly productive. Focused on development."
        )

        assert summary.date == "2024-01-01"
        assert len(summary.key_decisions_and_learnings) == 2
        assert "productive" in summary.journal_narrative.lower()


class TestActionItem:
    """Tests for ActionItem model."""

    def test_action_item_creation(self):
        """Test action item creation."""
        action = ActionItem(
            task_id="action_1",
            task_description="Email John about project",
            priority="P1",
            source_entry_id="entry_123"
        )

        assert action.task_id == "action_1"
        assert action.priority == "P1"
        assert action.due_date is None

    def test_action_item_with_due_date(self):
        """Test action item with due date."""
        due = datetime(2024, 12, 31, 17, 0)
        action = ActionItem(
            task_id="action_2",
            task_description="Complete report",
            priority="P2",
            source_entry_id="entry_456",
            due_date=due
        )

        assert action.due_date == due


class TestFinalAgentReport:
    """Tests for FinalAgentReport model."""

    def test_final_report_creation(self):
        """Test final report creation."""
        summary = DailySummaryOutput(
            date="2024-01-01",
            daily_theme="Test theme",
            key_decisions_and_learnings=["Decision 1"],
            journal_narrative="Narrative"
        )

        action = ActionItem(
            task_id="action_1",
            task_description="Test task",
            priority="P1",
            source_entry_id="entry_1"
        )

        report = FinalAgentReport(
            summary=summary,
            pending_actions=[action],
            suggested_first_task="Test task"
        )

        assert report.summary.date == "2024-01-01"
        assert len(report.pending_actions) == 1
        assert report.suggested_first_task == "Test task"


class TestAgentState:
    """Tests for AgentState model."""

    def test_agent_state_creation(self):
        """Test agent state creation."""
        state = AgentState(
            new_entry=None,
            all_entries=[],
            pending_actions=[],
            final_report=None,
            audio_output_path=None,
            tool_response=None,
            user_input="Test input",
            current_route=None
        )

        assert state.user_input == "Test input"
        assert state.all_entries == []
        assert state.pending_actions == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
