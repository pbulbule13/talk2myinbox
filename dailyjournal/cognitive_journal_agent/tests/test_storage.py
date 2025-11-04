"""
Tests for storage node.
"""

import pytest
from datetime import datetime
import sys
from pathlib import Path
import tempfile
import shutil
import os

sys.path.insert(0, str(Path(__file__).parent.parent))

from nodes.storage import JSONStorage, SQLiteStorage, StorageManager, storage_node
from data_models.pydantic_schemas import JournalEntry, ActionItem


class TestJSONStorage:
    """Tests for JSON storage backend."""

    def setup_method(self):
        """Setup test fixtures with temporary directory."""
        self.temp_dir = Path(tempfile.mkdtemp())
        os.environ["STORAGE_DIR"] = str(self.temp_dir)
        self.storage = JSONStorage()

    def teardown_method(self):
        """Cleanup temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_entry(self):
        """Test saving a journal entry."""
        entry = JournalEntry(
            timestamp=datetime.now(),
            input_type="text_note",
            raw_content="Test entry",
            source_id="test_1"
        )

        result = self.storage.save_entry(entry)
        assert result is True

        # Verify file was created
        assert self.storage.entries_file.exists()

    def test_get_entries(self):
        """Test retrieving entries."""
        # Save two entries
        entry1 = JournalEntry(
            timestamp=datetime.now(),
            input_type="text_note",
            raw_content="Entry 1",
            source_id="test_1"
        )
        entry2 = JournalEntry(
            timestamp=datetime.now(),
            input_type="email",
            raw_content="Entry 2",
            source_id="test_2"
        )

        self.storage.save_entry(entry1)
        self.storage.save_entry(entry2)

        # Retrieve entries
        entries = self.storage.get_entries()

        assert len(entries) == 2
        assert any(e.source_id == "test_1" for e in entries)
        assert any(e.source_id == "test_2" for e in entries)

    def test_save_action_items(self):
        """Test saving action items."""
        actions = [
            ActionItem(
                task_id="action_1",
                task_description="Task 1",
                priority="P1",
                source_entry_id="entry_1"
            ),
            ActionItem(
                task_id="action_2",
                task_description="Task 2",
                priority="P2",
                source_entry_id="entry_2"
            )
        ]

        result = self.storage.save_action_items(actions)
        assert result is True

    def test_get_pending_actions(self):
        """Test retrieving pending actions."""
        actions = [
            ActionItem(
                task_id="action_1",
                task_description="Task 1",
                priority="P1",
                source_entry_id="entry_1"
            )
        ]

        self.storage.save_action_items(actions)

        retrieved = self.storage.get_pending_actions()
        assert len(retrieved) == 1
        assert retrieved[0].task_id == "action_1"


class TestSQLiteStorage:
    """Tests for SQLite storage backend."""

    def setup_method(self):
        """Setup test fixtures with temporary database."""
        self.temp_dir = Path(tempfile.mkdtemp())
        db_path = self.temp_dir / "test.db"
        os.environ["SQLITE_DB_PATH"] = str(db_path)
        self.storage = SQLiteStorage()

    def teardown_method(self):
        """Cleanup temporary database."""
        self.storage.conn.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_entry(self):
        """Test saving entry to SQLite."""
        entry = JournalEntry(
            timestamp=datetime.now(),
            input_type="text_note",
            raw_content="SQLite test entry",
            source_id="sqlite_1",
            contextual_tags=["Test", "SQLite"]
        )

        result = self.storage.save_entry(entry)
        assert result is True

    def test_get_entries(self):
        """Test retrieving entries from SQLite."""
        entry = JournalEntry(
            timestamp=datetime.now(),
            input_type="text_note",
            raw_content="Test",
            source_id="sqlite_2"
        )

        self.storage.save_entry(entry)
        entries = self.storage.get_entries()

        assert len(entries) >= 1
        assert any(e.source_id == "sqlite_2" for e in entries)

    def test_save_and_get_action_items(self):
        """Test saving and retrieving action items."""
        actions = [
            ActionItem(
                task_id="sql_action_1",
                task_description="SQL Task",
                priority="P1",
                source_entry_id="entry_1"
            )
        ]

        self.storage.save_action_items(actions)
        retrieved = self.storage.get_pending_actions()

        assert len(retrieved) >= 1
        assert any(a.task_id == "sql_action_1" for a in retrieved)


class TestStorageNode:
    """Tests for storage_node function."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        os.environ["STORAGE_DIR"] = str(self.temp_dir)
        os.environ["STORAGE_BACKEND"] = "json"

    def teardown_method(self):
        """Cleanup."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_storage_node_saves_entry(self):
        """Test that storage node saves entries correctly."""
        entry = JournalEntry(
            timestamp=datetime.now(),
            input_type="text_note",
            raw_content="Node test",
            source_id="node_1",
            extracted_action_items=["Test action"]
        )

        state = {
            "new_entry": entry,
            "all_entries": [],
            "pending_actions": []
        }

        result = storage_node(state)

        assert "all_entries" in result
        assert len(result["all_entries"]) >= 1

    def test_storage_node_extracts_actions(self):
        """Test that storage node extracts action items."""
        entry = JournalEntry(
            timestamp=datetime.now(),
            input_type="text_note",
            raw_content="Test with actions",
            source_id="node_2",
            extracted_action_items=["Action 1", "Action 2"]
        )

        state = {
            "new_entry": entry,
            "all_entries": [],
            "pending_actions": []
        }

        result = storage_node(state)

        assert "pending_actions" in result
        # Should have created action items from extracted_action_items
        assert len(result["pending_actions"]) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
