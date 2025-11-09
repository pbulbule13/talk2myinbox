"""
Firebase Firestore Storage Service
Implements cloud-based storage for calendar events per the tech spec
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

from data_models.pydantic_schemas import UnifiedEvent


class FirebaseCalendarStorage:
    """
    Cloud storage for calendar events using Firebase Firestore.

    Storage structure:
    /artifacts/{appId}/users/{userId}/events/{eventId}
    """

    def __init__(
        self,
        app_id: str = "cognitive_journal",
        user_id: str = "default_user"
    ):
        """
        Initialize Firebase connection.

        Args:
            app_id: Application identifier
            user_id: User identifier for data isolation
        """
        if not FIREBASE_AVAILABLE:
            raise ImportError(
                "Firebase not available. Install: pip install firebase-admin"
            )

        self.app_id = app_id
        self.user_id = user_id

        # Initialize Firebase app if not already done
        if not firebase_admin._apps:
            # Try to get credentials from environment or file
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")

            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                # Try to initialize with default credentials or application default
                try:
                    firebase_admin.initialize_app()
                except Exception as e:
                    raise ValueError(
                        f"Firebase initialization failed. "
                        f"Set FIREBASE_CREDENTIALS_PATH env variable or use: {str(e)}"
                    )

        self.db = firestore.client()
        self.collection_path = f"artifacts/{app_id}/users/{user_id}/events"

    def save_event(self, event: UnifiedEvent) -> bool:
        """
        Save a single event to Firestore.

        Args:
            event: UnifiedEvent to save

        Returns:
            True if successful
        """
        try:
            doc_ref = self.db.collection(self.collection_path).document(event.event_id)

            event_data = {
                "date": event.start_time.strftime("%Y-%m-%d"),
                "time": self._format_time(event),
                "eventName": event.title,
                "location": event.location,
                "description": event.description,
                "sourceImageId": event.raw_data.get("source_image") if event.raw_data else None,
                "timestamp": firestore.SERVER_TIMESTAMP,
                # Additional fields for compatibility
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat(),
                "all_day": event.all_day,
                "source_id": event.source_id,
                "timezone": event.timezone
            }

            doc_ref.set(event_data)
            return True

        except Exception as e:
            print(f"Error saving event to Firebase: {e}")
            return False

    def save_events(self, events: List[UnifiedEvent]) -> int:
        """
        Save multiple events to Firestore in batch.

        Args:
            events: List of UnifiedEvent objects

        Returns:
            Number of successfully saved events
        """
        success_count = 0

        # Use batch writes for efficiency
        batch = self.db.batch()

        for event in events:
            try:
                doc_ref = self.db.collection(self.collection_path).document(event.event_id)

                event_data = {
                    "date": event.start_time.strftime("%Y-%m-%d"),
                    "time": self._format_time(event),
                    "eventName": event.title,
                    "location": event.location,
                    "description": event.description,
                    "sourceImageId": event.raw_data.get("source_image") if event.raw_data else None,
                    "timestamp": firestore.SERVER_TIMESTAMP,
                    "start_time": event.start_time.isoformat(),
                    "end_time": event.end_time.isoformat(),
                    "all_day": event.all_day,
                    "source_id": event.source_id,
                    "timezone": event.timezone
                }

                batch.set(doc_ref, event_data)
                success_count += 1

            except Exception as e:
                print(f"Error preparing event for batch: {e}")

        # Commit batch
        try:
            batch.commit()
            return success_count
        except Exception as e:
            print(f"Error committing batch to Firebase: {e}")
            return 0

    def get_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve events from Firestore with optional date filtering.

        Args:
            start_date: Filter events from this date
            end_date: Filter events until this date

        Returns:
            List of event dictionaries
        """
        try:
            query = self.db.collection(self.collection_path)

            # Apply date filters
            if start_date:
                query = query.where("date", ">=", start_date.strftime("%Y-%m-%d"))

            if end_date:
                query = query.where("date", "<=", end_date.strftime("%Y-%m-%d"))

            # Order by date and time
            query = query.order_by("date")

            # Execute query
            docs = query.stream()

            events = []
            for doc in docs:
                event_data = doc.to_dict()
                event_data["id"] = doc.id
                events.append(event_data)

            return events

        except Exception as e:
            print(f"Error retrieving events from Firebase: {e}")
            return []

    def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific event by ID.

        Args:
            event_id: Event identifier

        Returns:
            Event dictionary or None
        """
        try:
            doc_ref = self.db.collection(self.collection_path).document(event_id)
            doc = doc_ref.get()

            if doc.exists:
                event_data = doc.to_dict()
                event_data["id"] = doc.id
                return event_data

            return None

        except Exception as e:
            print(f"Error getting event from Firebase: {e}")
            return None

    def delete_event(self, event_id: str) -> bool:
        """
        Delete an event from Firestore.

        Args:
            event_id: Event identifier

        Returns:
            True if successful
        """
        try:
            doc_ref = self.db.collection(self.collection_path).document(event_id)
            doc_ref.delete()
            return True

        except Exception as e:
            print(f"Error deleting event from Firebase: {e}")
            return False

    def get_all_consolidated(self) -> List[Dict[str, Any]]:
        """
        Get all events for the current user (consolidated view).

        Returns:
            List of all events sorted by date
        """
        return self.get_events()

    def _format_time(self, event: UnifiedEvent) -> str:
        """Format event time as string per spec."""
        if event.all_day:
            return "All Day"

        return event.start_time.strftime("%I:%M %p").lstrip("0")


class DualStorageManager:
    """
    Manages both local (SQLite) and cloud (Firebase) storage.
    Provides fallback and sync capabilities.
    """

    def __init__(
        self,
        use_firebase: bool = True,
        app_id: str = "cognitive_journal",
        user_id: str = "default_user"
    ):
        """
        Initialize dual storage.

        Args:
            use_firebase: Enable Firebase cloud storage
            app_id: Application identifier
            user_id: User identifier
        """
        # Always use local storage
        from nodes.calendar_storage import CalendarStorageManager
        self.local_storage = CalendarStorageManager()

        # Optionally use Firebase
        self.firebase_storage = None
        if use_firebase and FIREBASE_AVAILABLE:
            try:
                self.firebase_storage = FirebaseCalendarStorage(app_id, user_id)
            except Exception as e:
                print(f"Firebase initialization failed: {e}")
                print("Falling back to local storage only")

    def save_events(self, events: List[UnifiedEvent]) -> bool:
        """
        Save events to both local and cloud storage.

        Args:
            events: List of events to save

        Returns:
            True if at least one storage succeeded
        """
        local_success = False
        firebase_success = False

        # Save to local storage
        try:
            self.local_storage.save_events(events)
            local_success = True
        except Exception as e:
            print(f"Local storage save failed: {e}")

        # Save to Firebase if available
        if self.firebase_storage:
            try:
                count = self.firebase_storage.save_events(events)
                firebase_success = count > 0
            except Exception as e:
                print(f"Firebase save failed: {e}")

        return local_success or firebase_success

    def get_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        prefer_cloud: bool = True
    ) -> List[Any]:
        """
        Get events with cloud-first or local-first strategy.

        Args:
            start_date: Filter from date
            end_date: Filter to date
            prefer_cloud: Try cloud first, fallback to local

        Returns:
            List of events (format depends on source)
        """
        if prefer_cloud and self.firebase_storage:
            try:
                events = self.firebase_storage.get_events(start_date, end_date)
                if events:
                    return events
            except Exception as e:
                print(f"Firebase retrieval failed: {e}")

        # Fallback to local or local-first
        try:
            return self.local_storage.get_events(start_date, end_date)
        except Exception as e:
            print(f"Local storage retrieval failed: {e}")
            return []

    def sync_local_to_cloud(self) -> int:
        """
        Sync local events to Firebase cloud.

        Returns:
            Number of events synced
        """
        if not self.firebase_storage:
            return 0

        try:
            # Get all local events
            local_events = self.local_storage.get_events()

            # Save to Firebase
            count = self.firebase_storage.save_events(local_events)

            print(f"Synced {count} events to Firebase")
            return count

        except Exception as e:
            print(f"Sync failed: {e}")
            return 0
