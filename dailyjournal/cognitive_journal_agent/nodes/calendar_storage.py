"""
Calendar Storage: Manages calendar sources, unified events, and connections.
Supports Firestore, local JSON, and SQLite backends.
Configurable via environment variables.
"""

from typing import List, Optional, Dict, Any
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3

# Conditional Firestore import
try:
    from google.cloud import firestore
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False

from data_models.pydantic_schemas import (
    CalendarSource,
    UnifiedEvent,
    CalendarConnection,
    EventConflict,
    CalendarInsight
)


class FirestoreCalendarStorage:
    """Firestore-based calendar storage backend."""

    def __init__(self):
        """Initialize Firestore client."""
        if not FIRESTORE_AVAILABLE:
            raise ImportError("Firestore not available. Install google-cloud-firestore.")

        credentials_path = os.getenv("GOOGLE_CLOUD_CREDENTIALS")
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

        self.db = firestore.Client()
        self.user_id = os.getenv("USER_ID", "default_user")

    def save_calendar_source(self, source: CalendarSource) -> bool:
        """Save a calendar source to Firestore."""
        try:
            collection = self.db.collection("users").document(self.user_id).collection("calendar_sources")
            source_dict = source.dict()

            # Convert datetime fields
            if source.last_sync:
                source_dict["last_sync"] = source.last_sync.isoformat()
            source_dict["created_at"] = source.created_at.isoformat()
            source_dict["updated_at"] = source.updated_at.isoformat()

            collection.document(source.source_id).set(source_dict)
            return True
        except Exception as e:
            print(f"Error saving calendar source to Firestore: {e}")
            return False

    def get_calendar_sources(self, active_only: bool = False) -> List[CalendarSource]:
        """Retrieve calendar sources."""
        try:
            collection = self.db.collection("users").document(self.user_id).collection("calendar_sources")

            if active_only:
                query = collection.where("is_active", "==", True)
            else:
                query = collection

            docs = query.stream()

            sources = []
            for doc in docs:
                data = doc.to_dict()
                # Convert datetime strings back
                if data.get("last_sync"):
                    data["last_sync"] = datetime.fromisoformat(data["last_sync"])
                data["created_at"] = datetime.fromisoformat(data["created_at"])
                data["updated_at"] = datetime.fromisoformat(data["updated_at"])

                sources.append(CalendarSource(**data))

            return sources
        except Exception as e:
            print(f"Error retrieving calendar sources from Firestore: {e}")
            return []

    def save_events(self, events: List[UnifiedEvent]) -> bool:
        """Save unified events to Firestore."""
        try:
            collection = self.db.collection("users").document(self.user_id).collection("unified_events")

            for event in events:
                event_dict = event.dict()
                # Convert datetime fields
                event_dict["start_time"] = event.start_time.isoformat()
                event_dict["end_time"] = event.end_time.isoformat()
                event_dict["created_at"] = event.created_at.isoformat()
                event_dict["updated_at"] = event.updated_at.isoformat()

                collection.document(event.event_id).set(event_dict)

            return True
        except Exception as e:
            print(f"Error saving events to Firestore: {e}")
            return False

    def get_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        source_ids: Optional[List[str]] = None
    ) -> List[UnifiedEvent]:
        """Retrieve unified events with optional filtering."""
        try:
            collection = self.db.collection("users").document(self.user_id).collection("unified_events")

            query = collection

            if start_date:
                query = query.where("start_time", ">=", start_date.isoformat())
            if end_date:
                query = query.where("start_time", "<=", end_date.isoformat())

            docs = query.stream()

            events = []
            for doc in docs:
                data = doc.to_dict()

                # Filter by source_ids if specified
                if source_ids and data.get("source_id") not in source_ids:
                    continue

                # Convert datetime strings back
                data["start_time"] = datetime.fromisoformat(data["start_time"])
                data["end_time"] = datetime.fromisoformat(data["end_time"])
                data["created_at"] = datetime.fromisoformat(data["created_at"])
                data["updated_at"] = datetime.fromisoformat(data["updated_at"])

                events.append(UnifiedEvent(**data))

            return events
        except Exception as e:
            print(f"Error retrieving events from Firestore: {e}")
            return []

    def save_connection(self, connection: CalendarConnection) -> bool:
        """Save calendar connection details."""
        try:
            collection = self.db.collection("users").document(self.user_id).collection("calendar_connections")

            conn_dict = connection.dict()
            # Convert datetime fields
            if connection.token_expires_at:
                conn_dict["token_expires_at"] = connection.token_expires_at.isoformat()
            if connection.last_auth_at:
                conn_dict["last_auth_at"] = connection.last_auth_at.isoformat()

            collection.document(connection.connection_id).set(conn_dict)
            return True
        except Exception as e:
            print(f"Error saving connection to Firestore: {e}")
            return False

    def get_connection(self, provider: str, user_email: str) -> Optional[CalendarConnection]:
        """Retrieve calendar connection by provider and email."""
        try:
            collection = self.db.collection("users").document(self.user_id).collection("calendar_connections")

            query = collection.where("provider", "==", provider).where("user_email", "==", user_email)
            docs = list(query.stream())

            if not docs:
                return None

            data = docs[0].to_dict()
            # Convert datetime strings back
            if data.get("token_expires_at"):
                data["token_expires_at"] = datetime.fromisoformat(data["token_expires_at"])
            if data.get("last_auth_at"):
                data["last_auth_at"] = datetime.fromisoformat(data["last_auth_at"])

            return CalendarConnection(**data)
        except Exception as e:
            print(f"Error retrieving connection from Firestore: {e}")
            return None


class JSONCalendarStorage:
    """Local JSON file-based calendar storage backend."""

    def __init__(self):
        """Initialize JSON storage."""
        self.storage_dir = Path(os.getenv("STORAGE_DIR", "./data"))
        self.storage_dir.mkdir(exist_ok=True)

        self.sources_file = self.storage_dir / "calendar_sources.json"
        self.events_file = self.storage_dir / "unified_events.json"
        self.connections_file = self.storage_dir / "calendar_connections.json"

        # Initialize files if they don't exist
        for file in [self.sources_file, self.events_file, self.connections_file]:
            if not file.exists():
                file.write_text("[]")

    def save_calendar_source(self, source: CalendarSource) -> bool:
        """Save a calendar source to JSON file."""
        try:
            with open(self.sources_file, "r") as f:
                sources = json.load(f)

            # Convert to dict
            source_dict = source.dict()
            if source.last_sync:
                source_dict["last_sync"] = source.last_sync.isoformat()
            source_dict["created_at"] = source.created_at.isoformat()
            source_dict["updated_at"] = source.updated_at.isoformat()

            # Update existing or append new
            existing_index = next(
                (i for i, s in enumerate(sources) if s["source_id"] == source.source_id),
                None
            )

            if existing_index is not None:
                sources[existing_index] = source_dict
            else:
                sources.append(source_dict)

            with open(self.sources_file, "w") as f:
                json.dump(sources, f, indent=2)

            return True
        except Exception as e:
            print(f"Error saving calendar source to JSON: {e}")
            return False

    def get_calendar_sources(self, active_only: bool = False) -> List[CalendarSource]:
        """Retrieve calendar sources from JSON file."""
        try:
            with open(self.sources_file, "r") as f:
                sources_data = json.load(f)

            sources = []
            for data in sources_data:
                if active_only and not data.get("is_active", False):
                    continue

                # Convert datetime strings back
                if data.get("last_sync"):
                    data["last_sync"] = datetime.fromisoformat(data["last_sync"])
                data["created_at"] = datetime.fromisoformat(data["created_at"])
                data["updated_at"] = datetime.fromisoformat(data["updated_at"])

                sources.append(CalendarSource(**data))

            return sources
        except Exception as e:
            print(f"Error retrieving calendar sources from JSON: {e}")
            return []

    def save_events(self, events: List[UnifiedEvent]) -> bool:
        """Save unified events to JSON file."""
        try:
            with open(self.events_file, "r") as f:
                all_events = json.load(f)

            for event in events:
                event_dict = event.dict()
                # Convert datetime fields
                event_dict["start_time"] = event.start_time.isoformat()
                event_dict["end_time"] = event.end_time.isoformat()
                event_dict["created_at"] = event.created_at.isoformat()
                event_dict["updated_at"] = event.updated_at.isoformat()

                # Update existing or append new
                existing_index = next(
                    (i for i, e in enumerate(all_events) if e["event_id"] == event.event_id),
                    None
                )

                if existing_index is not None:
                    all_events[existing_index] = event_dict
                else:
                    all_events.append(event_dict)

            with open(self.events_file, "w") as f:
                json.dump(all_events, f, indent=2)

            return True
        except Exception as e:
            print(f"Error saving events to JSON: {e}")
            return False

    def get_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        source_ids: Optional[List[str]] = None
    ) -> List[UnifiedEvent]:
        """Retrieve unified events with optional filtering."""
        try:
            with open(self.events_file, "r") as f:
                events_data = json.load(f)

            events = []
            for data in events_data:
                # Convert datetime strings back
                data["start_time"] = datetime.fromisoformat(data["start_time"])
                data["end_time"] = datetime.fromisoformat(data["end_time"])
                data["created_at"] = datetime.fromisoformat(data["created_at"])
                data["updated_at"] = datetime.fromisoformat(data["updated_at"])

                event = UnifiedEvent(**data)

                # Apply filters
                if start_date and event.start_time < start_date:
                    continue
                if end_date and event.start_time > end_date:
                    continue
                if source_ids and event.source_id not in source_ids:
                    continue

                events.append(event)

            # Sort by start time
            events.sort(key=lambda x: x.start_time)

            return events
        except Exception as e:
            print(f"Error retrieving events from JSON: {e}")
            return []

    def save_connection(self, connection: CalendarConnection) -> bool:
        """Save calendar connection details."""
        try:
            with open(self.connections_file, "r") as f:
                connections = json.load(f)

            conn_dict = connection.dict()
            # Convert datetime fields
            if connection.token_expires_at:
                conn_dict["token_expires_at"] = connection.token_expires_at.isoformat()
            if connection.last_auth_at:
                conn_dict["last_auth_at"] = connection.last_auth_at.isoformat()

            # Update existing or append new
            existing_index = next(
                (i for i, c in enumerate(connections) if c["connection_id"] == connection.connection_id),
                None
            )

            if existing_index is not None:
                connections[existing_index] = conn_dict
            else:
                connections.append(conn_dict)

            with open(self.connections_file, "w") as f:
                json.dump(connections, f, indent=2)

            return True
        except Exception as e:
            print(f"Error saving connection to JSON: {e}")
            return False

    def get_connection(self, provider: str, user_email: str) -> Optional[CalendarConnection]:
        """Retrieve calendar connection by provider and email."""
        try:
            with open(self.connections_file, "r") as f:
                connections_data = json.load(f)

            for data in connections_data:
                if data["provider"] == provider and data["user_email"] == user_email:
                    # Convert datetime strings back
                    if data.get("token_expires_at"):
                        data["token_expires_at"] = datetime.fromisoformat(data["token_expires_at"])
                    if data.get("last_auth_at"):
                        data["last_auth_at"] = datetime.fromisoformat(data["last_auth_at"])

                    return CalendarConnection(**data)

            return None
        except Exception as e:
            print(f"Error retrieving connection from JSON: {e}")
            return None


class SQLiteCalendarStorage:
    """SQLite-based calendar storage backend."""

    def __init__(self):
        """Initialize SQLite database."""
        self.db_path = Path(os.getenv("SQLITE_DB_PATH", "./data/journal.db"))
        self.db_path.parent.mkdir(exist_ok=True)

        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._initialize_schema()

    def _initialize_schema(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()

        # Calendar sources table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calendar_sources (
                source_id TEXT PRIMARY KEY,
                source_type TEXT NOT NULL,
                display_name TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                color TEXT,
                requires_oauth INTEGER DEFAULT 0,
                oauth_credentials TEXT,
                last_sync TEXT,
                sync_frequency_minutes INTEGER DEFAULT 60,
                sync_window_days INTEGER DEFAULT 90,
                file_path TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Unified events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS unified_events (
                event_id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                location TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                all_day INTEGER DEFAULT 0,
                timezone TEXT DEFAULT 'UTC',
                attendees TEXT,
                organizer TEXT,
                is_recurring INTEGER DEFAULT 0,
                recurrence_rule TEXT,
                status TEXT DEFAULT 'confirmed',
                response_status TEXT,
                original_event_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                has_conflict INTEGER DEFAULT 0,
                conflicting_event_ids TEXT,
                source_url TEXT,
                raw_data TEXT
            )
        """)

        # Create index on start_time for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_start_time
            ON unified_events(start_time)
        """)

        # Calendar connections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calendar_connections (
                connection_id TEXT PRIMARY KEY,
                provider TEXT NOT NULL,
                user_email TEXT NOT NULL,
                client_id TEXT NOT NULL,
                client_secret TEXT NOT NULL,
                access_token TEXT,
                refresh_token TEXT,
                token_expires_at TEXT,
                scopes TEXT,
                is_connected INTEGER DEFAULT 0,
                last_auth_at TEXT,
                auth_error TEXT
            )
        """)

        self.conn.commit()

    def save_calendar_source(self, source: CalendarSource) -> bool:
        """Save a calendar source to SQLite."""
        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO calendar_sources
                (source_id, source_type, display_name, is_active, color, requires_oauth,
                 oauth_credentials, last_sync, sync_frequency_minutes, sync_window_days,
                 file_path, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                source.source_id,
                source.source_type,
                source.display_name,
                1 if source.is_active else 0,
                source.color,
                1 if source.requires_oauth else 0,
                json.dumps(source.oauth_credentials) if source.oauth_credentials else None,
                source.last_sync.isoformat() if source.last_sync else None,
                source.sync_frequency_minutes,
                source.sync_window_days,
                source.file_path,
                source.created_at.isoformat(),
                source.updated_at.isoformat()
            ))

            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving calendar source to SQLite: {e}")
            return False

    def get_calendar_sources(self, active_only: bool = False) -> List[CalendarSource]:
        """Retrieve calendar sources from SQLite."""
        try:
            cursor = self.conn.cursor()

            query = "SELECT * FROM calendar_sources"
            if active_only:
                query += " WHERE is_active = 1"

            cursor.execute(query)
            rows = cursor.fetchall()

            sources = []
            for row in rows:
                sources.append(CalendarSource(
                    source_id=row[0],
                    source_type=row[1],
                    display_name=row[2],
                    is_active=bool(row[3]),
                    color=row[4],
                    requires_oauth=bool(row[5]),
                    oauth_credentials=json.loads(row[6]) if row[6] else None,
                    last_sync=datetime.fromisoformat(row[7]) if row[7] else None,
                    sync_frequency_minutes=row[8],
                    sync_window_days=row[9],
                    file_path=row[10],
                    created_at=datetime.fromisoformat(row[11]),
                    updated_at=datetime.fromisoformat(row[12])
                ))

            return sources
        except Exception as e:
            print(f"Error retrieving calendar sources from SQLite: {e}")
            return []

    def save_events(self, events: List[UnifiedEvent]) -> bool:
        """Save unified events to SQLite."""
        try:
            cursor = self.conn.cursor()

            for event in events:
                cursor.execute("""
                    INSERT OR REPLACE INTO unified_events
                    (event_id, source_id, title, description, location, start_time, end_time,
                     all_day, timezone, attendees, organizer, is_recurring, recurrence_rule,
                     status, response_status, original_event_id, created_at, updated_at,
                     has_conflict, conflicting_event_ids, source_url, raw_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.event_id,
                    event.source_id,
                    event.title,
                    event.description,
                    event.location,
                    event.start_time.isoformat(),
                    event.end_time.isoformat(),
                    1 if event.all_day else 0,
                    event.timezone,
                    json.dumps(event.attendees),
                    event.organizer,
                    1 if event.is_recurring else 0,
                    event.recurrence_rule,
                    event.status,
                    event.response_status,
                    event.original_event_id,
                    event.created_at.isoformat(),
                    event.updated_at.isoformat(),
                    1 if event.has_conflict else 0,
                    json.dumps(event.conflicting_event_ids),
                    event.source_url,
                    json.dumps(event.raw_data) if event.raw_data else None
                ))

            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving events to SQLite: {e}")
            return False

    def get_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        source_ids: Optional[List[str]] = None
    ) -> List[UnifiedEvent]:
        """Retrieve unified events with optional filtering."""
        try:
            cursor = self.conn.cursor()

            query = "SELECT * FROM unified_events WHERE 1=1"
            params = []

            if start_date:
                query += " AND start_time >= ?"
                params.append(start_date.isoformat())
            if end_date:
                query += " AND start_time <= ?"
                params.append(end_date.isoformat())
            if source_ids:
                placeholders = ','.join('?' * len(source_ids))
                query += f" AND source_id IN ({placeholders})"
                params.extend(source_ids)

            query += " ORDER BY start_time ASC"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            events = []
            for row in rows:
                events.append(UnifiedEvent(
                    event_id=row[0],
                    source_id=row[1],
                    title=row[2],
                    description=row[3],
                    location=row[4],
                    start_time=datetime.fromisoformat(row[5]),
                    end_time=datetime.fromisoformat(row[6]),
                    all_day=bool(row[7]),
                    timezone=row[8],
                    attendees=json.loads(row[9]) if row[9] else [],
                    organizer=row[10],
                    is_recurring=bool(row[11]),
                    recurrence_rule=row[12],
                    status=row[13],
                    response_status=row[14],
                    original_event_id=row[15],
                    created_at=datetime.fromisoformat(row[16]),
                    updated_at=datetime.fromisoformat(row[17]),
                    has_conflict=bool(row[18]),
                    conflicting_event_ids=json.loads(row[19]) if row[19] else [],
                    source_url=row[20],
                    raw_data=json.loads(row[21]) if row[21] else None
                ))

            return events
        except Exception as e:
            print(f"Error retrieving events from SQLite: {e}")
            return []

    def save_connection(self, connection: CalendarConnection) -> bool:
        """Save calendar connection details."""
        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO calendar_connections
                (connection_id, provider, user_email, client_id, client_secret,
                 access_token, refresh_token, token_expires_at, scopes,
                 is_connected, last_auth_at, auth_error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                connection.connection_id,
                connection.provider,
                connection.user_email,
                connection.client_id,
                connection.client_secret,
                connection.access_token,
                connection.refresh_token,
                connection.token_expires_at.isoformat() if connection.token_expires_at else None,
                json.dumps(connection.scopes),
                1 if connection.is_connected else 0,
                connection.last_auth_at.isoformat() if connection.last_auth_at else None,
                connection.auth_error
            ))

            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving connection to SQLite: {e}")
            return False

    def get_connection(self, provider: str, user_email: str) -> Optional[CalendarConnection]:
        """Retrieve calendar connection by provider and email."""
        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                SELECT * FROM calendar_connections
                WHERE provider = ? AND user_email = ?
            """, (provider, user_email))

            row = cursor.fetchone()

            if not row:
                return None

            return CalendarConnection(
                connection_id=row[0],
                provider=row[1],
                user_email=row[2],
                client_id=row[3],
                client_secret=row[4],
                access_token=row[5],
                refresh_token=row[6],
                token_expires_at=datetime.fromisoformat(row[7]) if row[7] else None,
                scopes=json.loads(row[8]) if row[8] else [],
                is_connected=bool(row[9]),
                last_auth_at=datetime.fromisoformat(row[10]) if row[10] else None,
                auth_error=row[11]
            )
        except Exception as e:
            print(f"Error retrieving connection from SQLite: {e}")
            return None


class CalendarStorageManager:
    """Main calendar storage manager that handles different backends."""

    def __init__(self):
        """Initialize storage backend based on configuration."""
        self.backend_type = os.getenv("STORAGE_BACKEND", "json")  # firestore, json, sqlite

        if self.backend_type == "firestore":
            self.backend = FirestoreCalendarStorage()
        elif self.backend_type == "sqlite":
            self.backend = SQLiteCalendarStorage()
        else:  # Default to JSON
            self.backend = JSONCalendarStorage()

    def save_calendar_source(self, source: CalendarSource) -> bool:
        """Save a calendar source."""
        return self.backend.save_calendar_source(source)

    def get_calendar_sources(self, active_only: bool = False) -> List[CalendarSource]:
        """Retrieve calendar sources."""
        return self.backend.get_calendar_sources(active_only)

    def save_events(self, events: List[UnifiedEvent]) -> bool:
        """Save unified events."""
        return self.backend.save_events(events)

    def get_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        source_ids: Optional[List[str]] = None
    ) -> List[UnifiedEvent]:
        """Retrieve unified events with optional filtering."""
        return self.backend.get_events(start_date, end_date, source_ids)

    def save_connection(self, connection: CalendarConnection) -> bool:
        """Save calendar connection details."""
        return self.backend.save_connection(connection)

    def get_connection(self, provider: str, user_email: str) -> Optional[CalendarConnection]:
        """Retrieve calendar connection by provider and email."""
        return self.backend.get_connection(provider, user_email)

    def delete_calendar_source(self, source_id: str) -> bool:
        """Delete a calendar source and its associated events."""
        # This would need backend-specific implementations
        # For now, mark as inactive
        sources = self.get_calendar_sources()
        for source in sources:
            if source.source_id == source_id:
                source.is_active = False
                source.updated_at = datetime.now()
                return self.save_calendar_source(source)
        return False
