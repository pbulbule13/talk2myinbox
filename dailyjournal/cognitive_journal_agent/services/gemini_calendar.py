"""
Gemini-based Calendar Extraction Service
Implements the AI Calendar Consolidation spec with Gemini 2.5 Flash
"""

import os
import base64
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from data_models.pydantic_schemas import CalendarSource, UnifiedEvent


class GeminiCalendarExtractor:
    """Extract calendar events from images using Gemini 2.5 Flash multimodal AI."""

    def __init__(self):
        """Initialize Gemini API."""
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai not available. Install: pip install google-generativeai")

        # Get API key from environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        genai.configure(api_key=api_key)

        # Use Gemini 2.5 Flash for fast, accurate multimodal processing
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def extract_events_from_image(
        self,
        image_path: str,
        source: CalendarSource,
        reference_date: Optional[datetime] = None
    ) -> tuple[List[UnifiedEvent], Optional[str]]:
        """
        Extract calendar events from image using Gemini multimodal AI.

        Args:
            image_path: Path to calendar image
            source: CalendarSource configuration
            reference_date: Reference date for context

        Returns:
            Tuple of (events: List[UnifiedEvent], error_message: Optional[str])
        """
        try:
            if not reference_date:
                reference_date = datetime.now()

            # Read and encode image
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # Create multimodal prompt with JSON schema
            prompt = self._build_extraction_prompt(reference_date)

            # Upload image to Gemini
            image_parts = [
                {
                    "mime_type": self._get_mime_type(image_path),
                    "data": base64.b64encode(image_data).decode('utf-8')
                }
            ]

            # Generate content with image and prompt
            response = self.model.generate_content([prompt, image_parts[0]])

            # Parse JSON response
            events_data = self._parse_response(response.text)

            if not events_data:
                return [], "No events could be extracted from the calendar image"

            # Convert to UnifiedEvent objects
            unified_events = []
            for event_data in events_data:
                event = self._create_unified_event(event_data, source.source_id, image_path)
                if event:
                    unified_events.append(event)

            return unified_events, None

        except Exception as e:
            return [], f"Gemini extraction failed: {str(e)}"

    def _build_extraction_prompt(self, reference_date: datetime) -> str:
        """Build structured prompt for Gemini with JSON schema."""
        return f"""You are an expert at extracting calendar events from images.

Analyze this calendar image and extract ALL events visible.

**Reference Date:** {reference_date.strftime('%Y-%m-%d')}

**Instructions:**
1. Identify the calendar grid structure (days, dates, month/year)
2. Extract ALL events shown, including:
   - Event titles/names
   - Dates (infer from calendar context)
   - Times (if visible)
   - Locations (if visible)
3. Handle various formats: Google Calendar, Outlook, Apple Calendar, paper calendars
4. Be liberal - extract anything that looks like an event
5. For missing information:
   - If no time visible: use "All Day" or infer from context
   - If date unclear: use the calendar's month/year to infer
   - If abbreviated: expand reasonably

**Output Format (STRICT JSON):**
Return a JSON array with this exact structure:

```json
[
  {{
    "date": "YYYY-MM-DD",
    "time": "HH:MM AM/PM or All Day",
    "eventName": "Event title",
    "location": "Location if visible or null",
    "description": "Additional details or null"
  }}
]
```

**Example:**
```json
[
  {{
    "date": "2025-11-20",
    "time": "10:00 AM",
    "eventName": "Team Meeting",
    "location": "Conference Room A",
    "description": "Weekly standup"
  }},
  {{
    "date": "2025-11-20",
    "time": "All Day",
    "eventName": "Project Deadline",
    "location": null,
    "description": "Final submission"
  }}
]
```

**CRITICAL:** Return ONLY the JSON array. No markdown, no explanation, no additional text.
Start with [ and end with ].
"""

    def _parse_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse JSON response from Gemini."""
        try:
            # Clean response
            text = response_text.strip()

            # Remove markdown code blocks if present
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]

            text = text.strip()

            # Parse JSON
            events_data = json.loads(text)

            if not isinstance(events_data, list):
                return []

            return events_data

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {response_text[:200]}")
            return []

    def _create_unified_event(
        self,
        event_data: Dict[str, Any],
        source_id: str,
        image_path: str
    ) -> Optional[UnifiedEvent]:
        """Convert extracted event data to UnifiedEvent."""
        try:
            import uuid
            from datetime import timedelta

            # Parse date
            date_str = event_data.get('date', '')
            event_date = datetime.fromisoformat(date_str)

            # Parse time
            time_str = event_data.get('time', 'All Day')
            all_day = False

            if time_str.lower() == 'all day' or not time_str:
                # All-day event
                start_time = event_date.replace(hour=0, minute=0, second=0)
                end_time = event_date.replace(hour=23, minute=59, second=59)
                all_day = True
            else:
                # Parse time string (e.g., "10:00 AM", "14:30")
                start_time = self._parse_time_string(time_str, event_date)
                end_time = start_time + timedelta(hours=1)  # Default 1-hour duration

            # Generate event ID
            event_id = f"{source_id}_{uuid.uuid4().hex[:8]}"

            return UnifiedEvent(
                event_id=event_id,
                source_id=source_id,
                title=event_data.get('eventName', 'Untitled Event'),
                description=event_data.get('description'),
                location=event_data.get('location'),
                start_time=start_time,
                end_time=end_time,
                all_day=all_day,
                timezone='UTC',
                original_event_id=event_id,
                raw_data={
                    **event_data,
                    'source_image': image_path,
                    'extraction_method': 'gemini_multimodal'
                }
            )

        except Exception as e:
            print(f"Error creating unified event: {e}")
            return None

    def _parse_time_string(self, time_str: str, event_date: datetime) -> datetime:
        """Parse various time string formats."""
        try:
            # Remove extra spaces
            time_str = time_str.strip()

            # Try parsing with AM/PM
            for fmt in ['%I:%M %p', '%I %p', '%H:%M', '%H']:
                try:
                    time_obj = datetime.strptime(time_str, fmt)
                    return event_date.replace(
                        hour=time_obj.hour,
                        minute=time_obj.minute,
                        second=0
                    )
                except ValueError:
                    continue

            # Default to 9 AM if parsing fails
            return event_date.replace(hour=9, minute=0, second=0)

        except Exception:
            return event_date.replace(hour=9, minute=0, second=0)

    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type from file extension."""
        ext = file_path.lower().split('.')[-1]
        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'bmp': 'image/bmp'
        }
        return mime_types.get(ext, 'image/jpeg')


class CalendarAnalyzer:
    """Analyze consolidated calendar data for summaries and free time."""

    def __init__(self):
        """Initialize analyzer with Gemini."""
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai not available")

        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None

    def summarize_day(self, events: List[UnifiedEvent], date: datetime) -> str:
        """Generate natural language summary of a day's schedule using Gemini."""
        if not self.model:
            return "Summary unavailable - Gemini API not configured"

        # Format events for LLM
        events_text = self._format_events_for_analysis(events, date)

        prompt = f"""Analyze this schedule for {date.strftime('%A, %B %d, %Y')}:

{events_text}

Provide a friendly, natural-language summary including:
1. Overview of the day (busy, light, balanced)
2. Key events and their times
3. Any important deadlines or appointments
4. Helpful reminders

Make it conversational and helpful, like a personal assistant briefing you on your day.
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Summary generation failed: {str(e)}"

    def identify_free_time(
        self,
        events: List[UnifiedEvent],
        date: datetime,
        min_duration_minutes: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Identify free time blocks between events.

        Returns list of free blocks with start, end, and duration.
        """
        # Filter events for the specified date
        day_events = [
            e for e in events
            if e.start_time.date() == date.date()
        ]

        if not day_events:
            # Entire day is free
            start = date.replace(hour=8, minute=0, second=0)
            end = date.replace(hour=18, minute=0, second=0)
            return [{
                'start': start,
                'end': end,
                'duration_minutes': 600,
                'description': 'Full day available'
            }]

        # Sort events by start time
        sorted_events = sorted(day_events, key=lambda e: e.start_time)

        free_blocks = []

        # Check time before first event
        day_start = date.replace(hour=8, minute=0, second=0)
        first_event = sorted_events[0]

        if first_event.start_time > day_start:
            duration = int((first_event.start_time - day_start).total_seconds() / 60)
            if duration >= min_duration_minutes:
                free_blocks.append({
                    'start': day_start,
                    'end': first_event.start_time,
                    'duration_minutes': duration,
                    'description': f'{duration} minutes before first event'
                })

        # Check gaps between events
        for i in range(len(sorted_events) - 1):
            current = sorted_events[i]
            next_event = sorted_events[i + 1]

            if current.end_time < next_event.start_time:
                duration = int((next_event.start_time - current.end_time).total_seconds() / 60)
                if duration >= min_duration_minutes:
                    free_blocks.append({
                        'start': current.end_time,
                        'end': next_event.start_time,
                        'duration_minutes': duration,
                        'description': f'{duration} minutes between events'
                    })

        # Check time after last event
        day_end = date.replace(hour=18, minute=0, second=0)
        last_event = sorted_events[-1]

        if last_event.end_time < day_end:
            duration = int((day_end - last_event.end_time).total_seconds() / 60)
            if duration >= min_duration_minutes:
                free_blocks.append({
                    'start': last_event.end_time,
                    'end': day_end,
                    'duration_minutes': duration,
                    'description': f'{duration} minutes after last event'
                })

        return free_blocks

    def get_longest_free_block(
        self,
        events: List[UnifiedEvent],
        date: datetime
    ) -> Optional[Dict[str, Any]]:
        """Find the longest continuous free time block."""
        free_blocks = self.identify_free_time(events, date)

        if not free_blocks:
            return None

        longest = max(free_blocks, key=lambda b: b['duration_minutes'])
        return longest

    def _format_events_for_analysis(self, events: List[UnifiedEvent], date: datetime) -> str:
        """Format events as readable text for LLM analysis."""
        day_events = [
            e for e in events
            if e.start_time.date() == date.date()
        ]

        if not day_events:
            return "No events scheduled."

        sorted_events = sorted(day_events, key=lambda e: e.start_time)

        lines = []
        for event in sorted_events:
            time_str = event.start_time.strftime('%I:%M %p')
            if not event.all_day:
                end_str = event.end_time.strftime('%I:%M %p')
                time_str = f"{time_str} - {end_str}"
            else:
                time_str = "All Day"

            line = f"- {time_str}: {event.title}"
            if event.location:
                line += f" @ {event.location}"
            lines.append(line)

        return '\n'.join(lines)
