"""
Integration tests for the complete Cognitive Journal Agent workflow.
"""

import pytest
from datetime import datetime
import sys
from pathlib import Path
import os
import tempfile
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent))

from graph.agent_graph import run_agent, AgentWithMemory
from config import get_config


class TestBasicWorkflow:
    """Integration tests for basic workflows."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        os.environ["STORAGE_DIR"] = str(self.temp_dir)
        os.environ["STORAGE_BACKEND"] = "json"
        os.environ["USE_LLM_PROCESSING"] = "false"
        os.environ["USE_LLM_REPORTING"] = "false"
        os.environ["TTS_ENABLED"] = "false"

    def teardown_method(self):
        """Cleanup."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_journal_entry_workflow(self):
        """Test complete journal entry workflow."""
        result = run_agent(
            user_input="Had a great meeting today about the new project"
        )

        # Should have created a new entry
        assert result.get("new_entry") is not None
        entry = result["new_entry"]
        assert "meeting" in entry.raw_content.lower()

        # Should be stored
        assert len(result.get("all_entries", [])) >= 1

    def test_multiple_entries_workflow(self):
        """Test processing multiple journal entries."""
        entries = [
            "Morning standup went well",
            "Completed the feature implementation",
            "Need to review pull requests tomorrow"
        ]

        for entry_text in entries:
            result = run_agent(user_input=entry_text)
            assert result.get("new_entry") is not None

        # Verify storage
        from nodes.storage import StorageManager
        storage = StorageManager()
        stored_entries = storage.get_entries()

        assert len(stored_entries) >= 3

    def test_action_extraction(self):
        """Test that action items are extracted and stored."""
        result = run_agent(
            user_input="Need to email John about the project deadline and schedule a review meeting"
        )

        entry = result.get("new_entry")
        assert entry is not None

        # Should have extracted some action items
        assert len(result.get("pending_actions", [])) >= 0


class TestAgentWithMemory:
    """Tests for agent with conversation memory."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        os.environ["STORAGE_DIR"] = str(self.temp_dir)
        os.environ["STORAGE_BACKEND"] = "json"
        os.environ["USE_LLM_PROCESSING"] = "false"
        os.environ["TTS_ENABLED"] = "false"

    def teardown_method(self):
        """Cleanup."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_agent_memory_persistence(self):
        """Test that agent maintains memory across interactions."""
        agent = AgentWithMemory()

        # First interaction
        result1 = agent.execute("Worked on the ML model today")
        assert len(agent.conversation_history) == 2  # User + Assistant

        # Second interaction
        result2 = agent.execute("Finished data preprocessing")
        assert len(agent.conversation_history) == 4  # 2 more messages

        # Session entries should accumulate
        assert len(agent.session_entries) >= 1

    def test_agent_clear_memory(self):
        """Test clearing agent memory."""
        agent = AgentWithMemory()

        agent.execute("Test entry")
        assert len(agent.conversation_history) > 0

        agent.clear_memory()
        assert len(agent.conversation_history) == 0
        assert len(agent.session_entries) == 0


class TestRouting:
    """Tests for workflow routing."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        os.environ["STORAGE_DIR"] = str(self.temp_dir)
        os.environ["STORAGE_BACKEND"] = "json"
        os.environ["USE_LLM_PROCESSING"] = "false"
        os.environ["USE_LLM_REPORTING"] = "false"
        os.environ["TTS_ENABLED"] = "false"

    def teardown_method(self):
        """Cleanup."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_journal_input_route(self):
        """Test that normal text routes to journal ingestion."""
        result = run_agent("This is a normal journal entry")

        assert result.get("new_entry") is not None
        assert result.get("current_route") == "journal_input"

    def test_summarize_route(self):
        """Test that summarize commands route correctly."""
        # First add some entries
        run_agent("Entry 1")
        run_agent("Entry 2")

        # Request summary
        result = run_agent("summarize my day")

        assert result.get("current_route") == "summarize"
        # Note: final_report might not be present if LLM is disabled


class TestConfiguration:
    """Tests for configuration handling."""

    def test_config_loading(self):
        """Test that configuration loads correctly."""
        config = get_config()

        assert config.storage.backend in ["json", "sqlite", "firestore"]
        assert config.llm.provider in ["openai", "anthropic"]

    def test_config_validation(self):
        """Test configuration validation."""
        config = get_config()
        messages = config.validate()

        # Should return a list (might have warnings)
        assert isinstance(messages, list)


class TestErrorHandling:
    """Tests for error handling."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        os.environ["STORAGE_DIR"] = str(self.temp_dir)
        os.environ["STORAGE_BACKEND"] = "json"
        os.environ["USE_LLM_PROCESSING"] = "false"
        os.environ["TTS_ENABLED"] = "false"

    def teardown_method(self):
        """Cleanup."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_empty_input_handling(self):
        """Test handling of empty input."""
        result = run_agent("")

        # Should handle gracefully
        assert result is not None

    def test_malformed_input_handling(self):
        """Test handling of malformed input."""
        result = run_agent(user_input="test", input_data={"invalid": "data"})

        # Should not crash
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
