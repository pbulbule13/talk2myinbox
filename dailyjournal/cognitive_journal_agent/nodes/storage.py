"""
Storage Node: Persists journal entries and action items.
Supports Firestore, local JSON, and SQLite backends.
Configurable via environment variables.
"""

from typing import Dict, Any, List
import os
import json
from datetime import datetime
from pathlib import Path

# Conditional Firestore import
try:
    from google.cloud import firestore
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False

# SQLite support
import sqlite3

from data_models.pydantic_schemas import JournalEntry, ActionItem


class FirestoreStorage:
    """Firestore-based storage backend."""

    def __init__(self):
        """Initialize Firestore client."""
        if not FIRESTORE_AVAILABLE:
            raise ImportError("Firestore not available. Install google-cloud-firestore.")

        credentials_path = os.getenv("GOOGLE_CLOUD_CREDENTIALS")
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

        self.db = firestore.Client()
        self.user_id = os.getenv("USER_ID", "default_user")

    def save_entry(self, entry: JournalEntry) -> bool:
        """Save a journal entry to Firestore."""
        try:
            collection = self.db.collection("users").document(self.user_id).collection("journal_entries")

            entry_dict = entry.dict()
            entry_dict["timestamp"] = entry.timestamp.isoformat()

            collection.document(entry.source_id).set(entry_dict)
            return True

        except Exception as e:
            print(f"Error saving to Firestore: {e}")
            return False

    def get_entries(self, date: str = None) -> List[JournalEntry]:
        """Retrieve journal entries, optionally filtered by date."""
        try:
            collection = self.db.collection("users").document(self.user_id).collection("journal_entries")

            query = collection.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(100)

            docs = query.stream()

            entries = []
            for doc in docs:
                data = doc.to_dict()
                data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                entries.append(JournalEntry(**data))

            return entries

        except Exception as e:
            print(f"Error retrieving from Firestore: {e}")
            return []

    def save_action_items(self, action_items: List[ActionItem]) -> bool:
        """Save action items to Firestore."""
        try:
            collection = self.db.collection("users").document(self.user_id).collection("action_items")

            for item in action_items:
                item_dict = item.dict()
                if item.due_date:
                    item_dict["due_date"] = item.due_date.isoformat()
                collection.document(item.task_id).set(item_dict)

            return True

        except Exception as e:
            print(f"Error saving action items to Firestore: {e}")
            return False

    def get_pending_actions(self) -> List[ActionItem]:
        """Retrieve pending action items."""
        try:
            collection = self.db.collection("users").document(self.user_id).collection("action_items")
            docs = collection.stream()

            action_items = []
            for doc in docs:
                data = doc.to_dict()
                if data.get("due_date"):
                    data["due_date"] = datetime.fromisoformat(data["due_date"])
                action_items.append(ActionItem(**data))

            return action_items

        except Exception as e:
            print(f"Error retrieving action items from Firestore: {e}")
            return []


class JSONStorage:
    """Local JSON file-based storage backend."""

    def __init__(self):
        """Initialize JSON storage."""
        self.storage_dir = Path(os.getenv("STORAGE_DIR", "./data"))
        self.storage_dir.mkdir(exist_ok=True)

        self.entries_file = self.storage_dir / "journal_entries.json"
        self.actions_file = self.storage_dir / "action_items.json"

        # Initialize files if they don't exist
        if not self.entries_file.exists():
            self.entries_file.write_text("[]")
        if not self.actions_file.exists():
            self.actions_file.write_text("[]")

    def save_entry(self, entry: JournalEntry) -> bool:
        """Save a journal entry to JSON file."""
        try:
            # Load existing entries
            with open(self.entries_file, "r") as f:
                entries = json.load(f)

            # Add new entry
            entry_dict = entry.dict()
            entry_dict["timestamp"] = entry.timestamp.isoformat()
            entries.append(entry_dict)

            # Save back
            with open(self.entries_file, "w") as f:
                json.dump(entries, f, indent=2)

            return True

        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return False

    def get_entries(self, date: str = None) -> List[JournalEntry]:
        """Retrieve journal entries from JSON file."""
        try:
            with open(self.entries_file, "r") as f:
                entries_data = json.load(f)

            entries = []
            for data in entries_data:
                data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                entries.append(JournalEntry(**data))

            # Sort by timestamp descending
            entries.sort(key=lambda x: x.timestamp, reverse=True)

            return entries

        except Exception as e:
            print(f"Error retrieving from JSON: {e}")
            return []

    def save_action_items(self, action_items: List[ActionItem]) -> bool:
        """Save action items to JSON file."""
        try:
            # Load existing actions
            with open(self.actions_file, "r") as f:
                actions = json.load(f)

            # Add new actions
            for item in action_items:
                item_dict = item.dict()
                if item.due_date:
                    item_dict["due_date"] = item.due_date.isoformat()

                # Check if already exists, update if so
                existing_index = next(
                    (i for i, a in enumerate(actions) if a["task_id"] == item.task_id),
                    None
                )

                if existing_index is not None:
                    actions[existing_index] = item_dict
                else:
                    actions.append(item_dict)

            # Save back
            with open(self.actions_file, "w") as f:
                json.dump(actions, f, indent=2)

            return True

        except Exception as e:
            print(f"Error saving action items to JSON: {e}")
            return False

    def get_pending_actions(self) -> List[ActionItem]:
        """Retrieve pending action items from JSON file."""
        try:
            with open(self.actions_file, "r") as f:
                actions_data = json.load(f)

            action_items = []
            for data in actions_data:
                if data.get("due_date"):
                    data["due_date"] = datetime.fromisoformat(data["due_date"])
                action_items.append(ActionItem(**data))

            return action_items

        except Exception as e:
            print(f"Error retrieving action items from JSON: {e}")
            return []


class SQLiteStorage:
    """SQLite-based storage backend."""

    def __init__(self):
        """Initialize SQLite database."""
        self.db_path = Path(os.getenv("SQLITE_DB_PATH", "./data/journal.db"))
        self.db_path.parent.mkdir(exist_ok=True)

        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._initialize_schema()

    def _initialize_schema(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()

        # Journal entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS journal_entries (
                source_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                input_type TEXT NOT NULL,
                raw_content TEXT NOT NULL,
                contextual_tags TEXT,
                extracted_action_items TEXT,
                inferred_emotion TEXT
            )
        """)

        # Action items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS action_items (
                task_id TEXT PRIMARY KEY,
                task_description TEXT NOT NULL,
                priority TEXT NOT NULL,
                source_entry_id TEXT NOT NULL,
                due_date TEXT,
                status TEXT DEFAULT 'pending'
            )
        """)

        self.conn.commit()

    def save_entry(self, entry: JournalEntry) -> bool:
        """Save a journal entry to SQLite."""
        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO journal_entries
                (source_id, timestamp, input_type, raw_content, contextual_tags, extracted_action_items, inferred_emotion)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.source_id,
                entry.timestamp.isoformat(),
                entry.input_type,
                entry.raw_content,
                json.dumps(entry.contextual_tags),
                json.dumps(entry.extracted_action_items),
                entry.inferred_emotion
            ))

            self.conn.commit()
            return True

        except Exception as e:
            print(f"Error saving to SQLite: {e}")
            return False

    def get_entries(self, date: str = None) -> List[JournalEntry]:
        """Retrieve journal entries from SQLite."""
        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                SELECT source_id, timestamp, input_type, raw_content, contextual_tags, extracted_action_items, inferred_emotion
                FROM journal_entries
                ORDER BY timestamp DESC
                LIMIT 100
            """)

            rows = cursor.fetchall()

            entries = []
            for row in rows:
                entries.append(JournalEntry(
                    source_id=row[0],
                    timestamp=datetime.fromisoformat(row[1]),
                    input_type=row[2],
                    raw_content=row[3],
                    contextual_tags=json.loads(row[4]) if row[4] else [],
                    extracted_action_items=json.loads(row[5]) if row[5] else [],
                    inferred_emotion=row[6]
                ))

            return entries

        except Exception as e:
            print(f"Error retrieving from SQLite: {e}")
            return []

    def save_action_items(self, action_items: List[ActionItem]) -> bool:
        """Save action items to SQLite."""
        try:
            cursor = self.conn.cursor()

            for item in action_items:
                cursor.execute("""
                    INSERT OR REPLACE INTO action_items
                    (task_id, task_description, priority, source_entry_id, due_date, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    item.task_id,
                    item.task_description,
                    item.priority,
                    item.source_entry_id,
                    item.due_date.isoformat() if item.due_date else None,
                    'pending'
                ))

            self.conn.commit()
            return True

        except Exception as e:
            print(f"Error saving action items to SQLite: {e}")
            return False

    def get_pending_actions(self) -> List[ActionItem]:
        """Retrieve pending action items from SQLite."""
        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                SELECT task_id, task_description, priority, source_entry_id, due_date
                FROM action_items
                WHERE status = 'pending'
                ORDER BY priority DESC
            """)

            rows = cursor.fetchall()

            action_items = []
            for row in rows:
                action_items.append(ActionItem(
                    task_id=row[0],
                    task_description=row[1],
                    priority=row[2],
                    source_entry_id=row[3],
                    due_date=datetime.fromisoformat(row[4]) if row[4] else None
                ))

            return action_items

        except Exception as e:
            print(f"Error retrieving action items from SQLite: {e}")
            return []


class StorageManager:
    """Main storage manager that handles different backends."""

    def __init__(self):
        """Initialize storage backend based on configuration."""
        self.backend_type = os.getenv("STORAGE_BACKEND", "json")  # firestore, json, sqlite

        if self.backend_type == "firestore":
            self.backend = FirestoreStorage()
        elif self.backend_type == "sqlite":
            self.backend = SQLiteStorage()
        else:  # Default to JSON
            self.backend = JSONStorage()

    def save_entry(self, entry: JournalEntry) -> bool:
        """Save a journal entry."""
        return self.backend.save_entry(entry)

    def get_entries(self, date: str = None) -> List[JournalEntry]:
        """Retrieve journal entries."""
        return self.backend.get_entries(date)

    def save_action_items(self, action_items: List[ActionItem]) -> bool:
        """Save action items."""
        return self.backend.save_action_items(action_items)

    def get_pending_actions(self) -> List[ActionItem]:
        """Retrieve pending action items."""
        return self.backend.get_pending_actions()


def storage_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node for storage operations.

    Args:
        state: Current agent state

    Returns:
        Updated state with entry and actions saved
    """
    storage = StorageManager()

    # Save new entry if present
    new_entry = state.get("new_entry")
    if new_entry:
        storage.save_entry(new_entry)

        # Update all_entries in state
        all_entries = state.get("all_entries", [])
        all_entries.append(new_entry)
        state["all_entries"] = all_entries

        # Extract and save action items from the entry
        if new_entry.extracted_action_items:
            action_items = []
            for idx, action_desc in enumerate(new_entry.extracted_action_items):
                action_item = ActionItem(
                    task_id=f"{new_entry.source_id}_action_{idx}",
                    task_description=action_desc,
                    priority="P2",  # Default priority
                    source_entry_id=new_entry.source_id
                )
                action_items.append(action_item)

            storage.save_action_items(action_items)

            # Update pending_actions in state
            pending_actions = state.get("pending_actions", [])
            pending_actions.extend(action_items)
            state["pending_actions"] = pending_actions

    # Load all entries and actions into state (for reporting)
    state["all_entries"] = storage.get_entries()
    state["pending_actions"] = storage.get_pending_actions()

    return state
