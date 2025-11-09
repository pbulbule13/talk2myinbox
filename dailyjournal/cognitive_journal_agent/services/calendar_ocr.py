"""
Calendar OCR Service: Extract calendar events from images using OCR and LLM.
"""

from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime, timedelta
import os
import re
import uuid

# OCR
try:
    import pytesseract
    from PIL import Image

    # Configure Tesseract path for Windows
    if os.name == 'nt':  # Windows
        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# LLM for parsing
try:
    from langchain_openai import ChatOpenAI
    from langchain_anthropic import ChatAnthropic
    from langchain.schema import HumanMessage, SystemMessage
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

from data_models.pydantic_schemas import CalendarSource, UnifiedEvent
from nodes.calendar_storage import CalendarStorageManager


class CalendarOCRProcessor:
    """Process calendar images to extract events using OCR and LLM."""

    def __init__(self):
        """Initialize OCR processor."""
        if not OCR_AVAILABLE:
            raise ImportError("OCR not available. Install: pytesseract pillow")
        if not LLM_AVAILABLE:
            raise ImportError("LLM not available. Install: langchain-openai or langchain-anthropic")

        self.storage = CalendarStorageManager()

        # Initialize LLM
        llm_provider = os.getenv("LLM_PROVIDER", "openai")
        if llm_provider == "anthropic":
            self.llm = ChatAnthropic(
                model=os.getenv("LLM_MODEL", "claude-3-5-sonnet-20241022"),
                temperature=0.1
            )
        else:
            self.llm = ChatOpenAI(
                model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
                temperature=0.1
            )

    def process_calendar_image(
        self,
        source: CalendarSource,
        image_path: str,
        reference_date: Optional[datetime] = None
    ) -> Tuple[List[UnifiedEvent], Optional[str]]:
        """
        Process a calendar image and extract events.

        Args:
            source: CalendarSource configuration
            image_path: Path to calendar image
            reference_date: Reference date to help with relative date parsing

        Returns:
            Tuple of (events: List[UnifiedEvent], error_message: Optional[str])
        """
        try:
            # Step 1: Extract text from image using OCR
            ocr_text = self._extract_text_from_image(image_path)
            if not ocr_text.strip():
                return [], "No text could be extracted from the image."

            print(f"OCR extracted text ({len(ocr_text)} chars):\n{ocr_text[:500]}...")

            # Step 2: Use LLM to parse calendar events from OCR text
            events_data = self._parse_events_with_llm(ocr_text, reference_date)

            if not events_data:
                return [], "No calendar events could be parsed from the image."

            # Step 3: Convert to UnifiedEvent format
            unified_events = []
            for event_data in events_data:
                event = self._create_unified_event(event_data, source.source_id)
                if event:
                    unified_events.append(event)

            # Step 4: Save events to storage
            if unified_events:
                self.storage.save_events(unified_events)

                # Update source's last_sync
                source.last_sync = datetime.now()
                source.updated_at = datetime.now()
                source.file_path = image_path
                self.storage.save_calendar_source(source)

            return unified_events, None

        except Exception as e:
            return [], f"Failed to process calendar image: {str(e)}"

    def _extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using Tesseract OCR."""
        try:
            # Open image
            image = Image.open(image_path)

            # Perform OCR
            text = pytesseract.image_to_string(image, config='--psm 6')

            return text

        except Exception as e:
            raise Exception(f"OCR extraction failed: {str(e)}")

    def _parse_events_with_llm(
        self,
        ocr_text: str,
        reference_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Use LLM to parse calendar events from OCR text."""
        try:
            if not reference_date:
                reference_date = datetime.now()

            system_prompt = """You are an expert at parsing calendar events from OCR-extracted text.
Your task is to identify and extract calendar events from the provided text, which may be messy or imperfect due to OCR errors from Google Calendar, Outlook, or other calendar applications.

IMPORTANT GUIDELINES:
1. The text may show a calendar grid with dates, day names, and events
2. Events may appear with times like "3pm", "9am", "2:30pm", or "14:00"
3. Events may span multiple lines or be abbreviated
4. Look for patterns like "Event Name" followed by time or date indicators
5. Month and year context will be in the reference date provided
6. If you see abbreviated text like "Prashil sf conference", expand it reasonably

Extract the following information for each event:
- title: Event title/subject (be liberal - extract anything that looks like an event)
- date: Event date (in ISO format YYYY-MM-DD, infer from context and reference date)
- start_time: Start time (in HH:MM format, 24-hour clock)
- end_time: End time (in HH:MM format, 24-hour clock - if not specified, add 1 hour to start)
- location: Location (if mentioned)
- description: Any additional details

EXTRACT ALL EVENTS even if information is partial. For missing fields:
- If no time: assume 09:00 to 10:00
- If only one time: assume it's start time, add 1 hour for end
- If date unclear: use reference date to infer (e.g., if reference is Nov 2025, "Nov 5" = 2025-11-05)

Example output format (MUST be valid JSON):
[
  {
    "title": "Team Meeting",
    "date": "2025-11-15",
    "start_time": "14:00",
    "end_time": "15:00",
    "location": "Conference Room",
    "description": null
  },
  {
    "title": "Prashil SF Conference",
    "date": "2025-11-05",
    "start_time": "15:00",
    "end_time": "16:00",
    "location": null,
    "description": null
  }
]

CRITICAL: Return ONLY the JSON array, no additional text, markdown formatting, or explanation. Start with [ and end with ]."""

            user_prompt = f"""Reference date: {reference_date.strftime('%Y-%m-%d')}

OCR Text:
{ocr_text}

Extract all calendar events from the above text."""

            # Call LLM
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            response = self.llm.invoke(messages)
            response_text = response.content

            # Parse JSON response
            import json

            # Try to extract JSON array from response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                events_data = json.loads(json_match.group())
                return events_data
            else:
                print(f"Could not parse LLM response as JSON: {response_text[:200]}")
                return []

        except Exception as e:
            print(f"Error parsing events with LLM: {e}")
            return []

    def _create_unified_event(self, event_data: Dict[str, Any], source_id: str) -> Optional[UnifiedEvent]:
        """Convert parsed event data to UnifiedEvent."""
        try:
            # Parse date and times
            event_date = datetime.fromisoformat(event_data['date'])

            if event_data.get('start_time'):
                start_hour, start_min = map(int, event_data['start_time'].split(':'))
                start_time = event_date.replace(hour=start_hour, minute=start_min)
                all_day = False
            else:
                start_time = event_date
                all_day = True

            if event_data.get('end_time'):
                end_hour, end_min = map(int, event_data['end_time'].split(':'))
                end_time = event_date.replace(hour=end_hour, minute=end_min)
            else:
                # Default to 1 hour duration or end of day for all-day events
                if all_day:
                    end_time = event_date + timedelta(days=1)
                else:
                    end_time = start_time + timedelta(hours=1)

            # Generate unique event ID
            event_id = f"{source_id}_{uuid.uuid4().hex[:8]}"

            return UnifiedEvent(
                event_id=event_id,
                source_id=source_id,
                title=event_data.get('title', 'Untitled Event'),
                description=event_data.get('description'),
                location=event_data.get('location'),
                start_time=start_time,
                end_time=end_time,
                all_day=all_day,
                timezone='UTC',
                original_event_id=event_id,
                raw_data=event_data
            )

        except Exception as e:
            print(f"Error creating unified event: {e}")
            return None


class ConflictDetector:
    """Detect and manage calendar event conflicts."""

    def __init__(self):
        """Initialize conflict detector."""
        self.storage = CalendarStorageManager()

    def detect_conflicts(
        self,
        events: Optional[List[UnifiedEvent]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Tuple[UnifiedEvent, UnifiedEvent, str]]:
        """
        Detect conflicts between calendar events.

        Args:
            events: Optional list of events to check (if None, fetches from storage)
            start_date: Optional filter start date
            end_date: Optional filter end date

        Returns:
            List of tuples (event1, event2, conflict_type)
        """
        # Fetch events if not provided
        if events is None:
            events = self.storage.get_events(start_date, end_date)

        if not events:
            return []

        # Sort events by start time
        sorted_events = sorted(events, key=lambda e: e.start_time)

        conflicts = []

        # Check each pair of events
        for i, event1 in enumerate(sorted_events):
            for event2 in sorted_events[i+1:]:
                # Skip if event2 starts after event1 ends (no overlap possible)
                if event2.start_time >= event1.end_time:
                    break

                # Check for overlap
                conflict_type = self._check_overlap(event1, event2)
                if conflict_type:
                    conflicts.append((event1, event2, conflict_type))

                    # Mark events as having conflicts
                    if not event1.has_conflict:
                        event1.has_conflict = True
                        event1.conflicting_event_ids.append(event2.event_id)

                    if not event2.has_conflict:
                        event2.has_conflict = True
                        event2.conflicting_event_ids.append(event1.event_id)

        # Update events with conflict information
        if conflicts:
            conflicted_events = []
            for event1, event2, _ in conflicts:
                if event1 not in conflicted_events:
                    conflicted_events.append(event1)
                if event2 not in conflicted_events:
                    conflicted_events.append(event2)

            self.storage.save_events(conflicted_events)

        return conflicts

    def _check_overlap(self, event1: UnifiedEvent, event2: UnifiedEvent) -> Optional[str]:
        """
        Check if two events overlap and return conflict type.

        Returns:
            "full_overlap", "partial_overlap", "adjacent", or None
        """
        # Check for full overlap
        if (event1.start_time >= event2.start_time and event1.end_time <= event2.end_time) or \
           (event2.start_time >= event1.start_time and event2.end_time <= event1.end_time):
            return "full_overlap"

        # Check for partial overlap
        if (event1.start_time < event2.end_time and event1.end_time > event2.start_time):
            return "partial_overlap"

        # Check for adjacent events (within 5 minutes)
        if abs((event1.end_time - event2.start_time).total_seconds()) < 300 or \
           abs((event2.end_time - event1.start_time).total_seconds()) < 300:
            return "adjacent"

        return None

    def get_free_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        min_duration_minutes: int = 30,
        work_hours_only: bool = True
    ) -> List[Dict[str, datetime]]:
        """
        Find free time slots between events.

        Args:
            start_date: Start of search range
            end_date: End of search range
            min_duration_minutes: Minimum slot duration in minutes
            work_hours_only: Only return slots during work hours (9am-5pm)

        Returns:
            List of free slot dictionaries with 'start' and 'end' keys
        """
        # Fetch events in range
        events = self.storage.get_events(start_date, end_date)

        if not events:
            # No events, entire range is free
            return [{'start': start_date, 'end': end_date}]

        # Sort events by start time
        sorted_events = sorted(events, key=lambda e: e.start_time)

        free_slots = []

        # Check slot before first event
        if sorted_events[0].start_time > start_date:
            slot_duration = (sorted_events[0].start_time - start_date).total_seconds() / 60
            if slot_duration >= min_duration_minutes:
                if self._is_work_hours(start_date, sorted_events[0].start_time, work_hours_only):
                    free_slots.append({
                        'start': start_date,
                        'end': sorted_events[0].start_time
                    })

        # Check slots between events
        for i in range(len(sorted_events) - 1):
            current_event = sorted_events[i]
            next_event = sorted_events[i + 1]

            if current_event.end_time < next_event.start_time:
                slot_duration = (next_event.start_time - current_event.end_time).total_seconds() / 60
                if slot_duration >= min_duration_minutes:
                    if self._is_work_hours(current_event.end_time, next_event.start_time, work_hours_only):
                        free_slots.append({
                            'start': current_event.end_time,
                            'end': next_event.start_time
                        })

        # Check slot after last event
        if sorted_events[-1].end_time < end_date:
            slot_duration = (end_date - sorted_events[-1].end_time).total_seconds() / 60
            if slot_duration >= min_duration_minutes:
                if self._is_work_hours(sorted_events[-1].end_time, end_date, work_hours_only):
                    free_slots.append({
                        'start': sorted_events[-1].end_time,
                        'end': end_date
                    })

        return free_slots

    def _is_work_hours(self, start: datetime, end: datetime, check: bool) -> bool:
        """Check if a time slot is within work hours."""
        if not check:
            return True

        # Work hours: 9am - 5pm
        work_start_hour = 9
        work_end_hour = 17

        # Check if slot overlaps with work hours
        return (start.hour >= work_start_hour or end.hour <= work_end_hour) and \
               start.weekday() < 5  # Monday-Friday

    def deduplicate_events(self, events: List[UnifiedEvent]) -> List[UnifiedEvent]:
        """
        Remove duplicate events based on title, time, and location.

        Returns:
            List of unique events
        """
        unique_events = []
        seen_signatures = set()

        for event in events:
            # Create a signature for the event
            signature = (
                event.title.lower().strip(),
                event.start_time,
                event.end_time,
                (event.location or '').lower().strip()
            )

            if signature not in seen_signatures:
                seen_signatures.add(signature)
                unique_events.append(event)
            else:
                print(f"Duplicate event detected and skipped: {event.title} at {event.start_time}")

        return unique_events
