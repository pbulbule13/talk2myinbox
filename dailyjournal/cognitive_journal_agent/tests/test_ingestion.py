"""
Tests for ingestion node.
"""

import pytest
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from nodes.ingestion import MultimodalIngest, ingestion_node
from data_models.pydantic_schemas import JournalEntry


class TestMultimodalIngest:
    """Tests for MultimodalIngest class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.processor = MultimodalIngest()

    def test_process_text_note(self):
        """Test processing plain text notes."""
        entry = self.processor.process_text_note(
            content="This is a test note about my day"
        )

        assert isinstance(entry, JournalEntry)
        assert entry.input_type == "text_note"
        assert "test note" in entry.raw_content
        assert entry.source_id.startswith("text_")

    def test_process_code_snippet(self):
        """Test processing code snippets."""
        code = "def hello():\n    print('Hello, World!')"
        entry = self.processor.process_code_snippet(
            code=code,
            language="python"
        )

        assert entry.input_type == "code_snippet"
        assert "python" in entry.raw_content
        assert "def hello()" in entry.raw_content

    def test_process_email(self):
        """Test processing email data."""
        email_data = {
            "from": "john@example.com",
            "subject": "Project Update",
            "body": "Here's the latest on the project...",
            "timestamp": datetime.now(),
            "id": "email_123"
        }

        entry = self.processor.process_email(email_data)

        assert entry.input_type == "email"
        assert "john@example.com" in entry.raw_content
        assert "Project Update" in entry.raw_content
        assert entry.source_id == "email_email_123"

    def test_process_calendar_event(self):
        """Test processing calendar events."""
        event_data = {
            "title": "Team Meeting",
            "start": "2024-01-15 10:00",
            "end": "2024-01-15 11:00",
            "description": "Q1 Planning",
            "attendees": ["alice@example.com", "bob@example.com"]
        }

        entry = self.processor.process_calendar_event(event_data)

        assert entry.input_type == "calendar_event"
        assert "Team Meeting" in entry.raw_content
        assert "alice@example.com" in entry.raw_content

    def test_ingest_routing(self):
        """Test that ingest() routes to correct processor."""
        # Text note
        result = self.processor.ingest({
            "type": "text_note",
            "content": "Test content"
        })
        assert result.input_type == "text_note"

        # Code snippet
        result = self.processor.ingest({
            "type": "code_snippet",
            "content": "print('hello')",
            "language": "python"
        })
        assert result.input_type == "code_snippet"

        # Email
        result = self.processor.ingest({
            "type": "email",
            "email_data": {
                "from": "test@example.com",
                "subject": "Test",
                "body": "Body"
            }
        })
        assert result.input_type == "email"


class TestIngestionNode:
    """Tests for ingestion_node function."""

    def test_ingestion_node_with_text(self):
        """Test ingestion node with text input."""
        state = {
            "user_input": "This is a test journal entry",
            "input_data": {}
        }

        result = ingestion_node(state)

        assert "new_entry" in result
        assert result["new_entry"].input_type == "text_note"
        assert "test journal entry" in result["new_entry"].raw_content

    def test_ingestion_node_with_structured_data(self):
        """Test ingestion node with structured input."""
        state = {
            "user_input": "",
            "input_data": {
                "type": "code_snippet",
                "content": "x = 42",
                "language": "python"
            }
        }

        result = ingestion_node(state)

        assert result["new_entry"].input_type == "code_snippet"
        assert "x = 42" in result["new_entry"].raw_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
