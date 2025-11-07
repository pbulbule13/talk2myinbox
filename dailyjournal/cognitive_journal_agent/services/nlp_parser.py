"""
Natural Language Parser for Date/Time and Command Intent Detection.
Handles phrases like "tomorrow 2-3pm", "next Tuesday at 10am", "remind me at 8pm".
"""

from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta
import dateparser
import re
from enum import Enum


class CommandIntent(Enum):
    """Supported command intents."""
    CALENDAR_BLOCK = "calendar_block"
    CALENDAR_SCHEDULE = "calendar_schedule"
    REMINDER = "reminder"
    NOTE = "note"
    TASK = "task"
    JOURNAL = "journal"
    UNKNOWN = "unknown"


class NaturalLanguageParser:
    """Parse natural language commands and extract structured information."""

    def __init__(self):
        """Initialize the parser with timezone settings."""
        self.timezone = 'UTC'  # Can be configured

        # Intent patterns
        self.intent_patterns = {
            CommandIntent.CALENDAR_BLOCK: [
                r'block\s+calendar',
                r'block\s+time',
                r'block\s+\d',
                r'block.*(?:for|tomorrow|today|next)',
            ],
            CommandIntent.CALENDAR_SCHEDULE: [
                r'schedule',
                r'add\s+(?:to\s+)?calendar',
                r'put\s+(?:on\s+)?calendar',
                r'calendar\s+for',
            ],
            CommandIntent.REMINDER: [
                r'remind\s+me',
                r'reminder',
                r'remind\s+(?:someone|him|her|them)',
                r'set\s+reminder',
            ],
            CommandIntent.NOTE: [
                r'add\s+note',
                r'take\s+note',
                r'note\s+to',
                r'make\s+note',
                r'note:',
            ],
            CommandIntent.TASK: [
                r'add\s+task',
                r'to\s+do',
                r'todo',
                r'need\s+to',
                r'must\s+(?:finish|complete|do)',
            ],
        }

    def parse_command(self, text: str) -> Dict[str, Any]:
        """
        Parse a natural language command and extract intent and entities.

        Args:
            text: The natural language command

        Returns:
            Dictionary with intent, entities, and parsed information
        """
        text_lower = text.lower().strip()

        # Detect intent
        intent = self._detect_intent(text_lower)

        # Extract entities based on intent
        result = {
            "original_text": text,
            "intent": intent.value,
            "confidence": 0.8,  # Can be improved with ML model
            "entities": {}
        }

        if intent == CommandIntent.CALENDAR_BLOCK:
            result["entities"] = self._parse_calendar_block(text_lower)

        elif intent == CommandIntent.CALENDAR_SCHEDULE:
            result["entities"] = self._parse_calendar_schedule(text_lower)

        elif intent == CommandIntent.REMINDER:
            result["entities"] = self._parse_reminder(text_lower)

        elif intent == CommandIntent.NOTE:
            result["entities"] = self._parse_note(text_lower)

        elif intent == CommandIntent.TASK:
            result["entities"] = self._parse_task(text_lower)

        else:
            # Default to journal entry
            result["intent"] = CommandIntent.JOURNAL.value
            result["entities"] = {"content": text}

        return result

    def _detect_intent(self, text: str) -> CommandIntent:
        """Detect the intent of the command."""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return intent

        return CommandIntent.JOURNAL

    def _parse_calendar_block(self, text: str) -> Dict[str, Any]:
        """
        Parse calendar block command.
        Example: "block calendar for 2-3 tomorrow for kids pickup"
        """
        entities = {}

        # Extract purpose/description (text after last "for")
        # Split by "for" and take the last one that's not a time range
        parts = text.split(' for ')
        if len(parts) > 1:
            # The last part is likely the purpose unless it's a time
            potential_title = parts[-1].strip()
            # Check if it looks like a time (contains numbers and dashes/colons)
            if not re.search(r'\d+[-:]\d+', potential_title):
                entities["title"] = potential_title
            else:
                entities["title"] = "Blocked Time"
        else:
            entities["title"] = "Blocked Time"

        # Extract time range - try explicit time range first
        time_range = self._extract_time_range(text)
        if time_range:
            entities["start_time"] = time_range[0]
            entities["end_time"] = time_range[1]
            entities["duration_minutes"] = int((time_range[1] - time_range[0]).total_seconds() / 60)

        # If no time range found, try to parse simple hour ranges like "2-3"
        if "start_time" not in entities:
            # Try to find duration like "2-3", "2 to 3"
            duration_match = re.search(r'(?:for\s+)?(\d+)\s*[-to]+\s*(\d+)', text, re.IGNORECASE)
            if duration_match:
                start_hour = int(duration_match.group(1))
                end_hour = int(duration_match.group(2))

                # Determine if it's AM or PM
                # If hours are small (1-11), assume PM if in work context
                if start_hour <= 11 and start_hour >= 1:
                    # Check for explicit PM/AM
                    if 'pm' in text.lower():
                        if start_hour < 12:
                            start_hour += 12
                        if end_hour < 12:
                            end_hour += 12
                    elif start_hour < 8:  # Assume PM for small hours in work context
                        start_hour += 12
                        end_hour += 12

                # Find the date context
                date_str = "tomorrow" if "tomorrow" in text.lower() else "today"
                base_date = self._parse_natural_date(date_str)

                if base_date:
                    try:
                        start_dt = base_date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
                        end_dt = base_date.replace(hour=end_hour, minute=0, second=0, microsecond=0)

                        entities["start_time"] = start_dt
                        entities["end_time"] = end_dt
                        entities["duration_minutes"] = (end_hour - start_hour) * 60
                    except ValueError:
                        # Invalid hour, skip
                        pass

        return entities

    def _parse_calendar_schedule(self, text: str) -> Dict[str, Any]:
        """
        Parse calendar scheduling command.
        Example: "schedule 5 minutes tomorrow for interview prep"
        """
        entities = {}

        # Extract duration
        duration_match = re.search(r'(\d+)\s*(?:minute|min|hour|hr)s?', text, re.IGNORECASE)
        if duration_match:
            duration = int(duration_match.group(1))

            # Check if it's hours or minutes
            if 'hour' in text.lower() or 'hr' in text.lower():
                entities["duration_minutes"] = duration * 60
            else:
                entities["duration_minutes"] = duration

        # Extract date/time
        date_time = self._parse_natural_date(text)
        if date_time:
            entities["start_time"] = date_time

            # Calculate end time if we have duration
            if "duration_minutes" in entities:
                entities["end_time"] = date_time + timedelta(minutes=entities["duration_minutes"])

        # Extract title (text after "for")
        title_match = re.search(r'for\s+(.+?)(?:\s*$)', text)
        if title_match:
            entities["title"] = title_match.group(1).strip()
        else:
            entities["title"] = "Scheduled Time"

        return entities

    def _parse_reminder(self, text: str) -> Dict[str, Any]:
        """
        Parse reminder command.
        Example: "remind me at 8pm to call Mr. A for interview"
        """
        entities = {}

        # Extract time - try specific time patterns first
        reminder_time = None

        # Look for specific time patterns like "at 8pm", "at 8:00", etc.
        time_patterns = [
            r'at\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)?)',
            r'(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM))',
            r'(?:in|after)\s+(\d+)\s*(?:minute|min|hour|hr)s?',
        ]

        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                time_phrase = match.group(1)
                # Add context if needed
                if 'tomorrow' in text.lower():
                    time_phrase = f"tomorrow {time_phrase}"
                elif 'today' in text.lower():
                    time_phrase = f"today {time_phrase}"

                reminder_time = self._parse_natural_date(time_phrase)
                if reminder_time:
                    break

        # If no specific pattern found, try full text
        if not reminder_time:
            reminder_time = self._parse_natural_date(text)

        if reminder_time:
            entities["reminder_time"] = reminder_time

        # Extract person to remind
        person_match = re.search(r'remind\s+(?:me|(?:mr|ms|mrs|dr)\.?\s+\w+)', text, re.IGNORECASE)
        if person_match:
            person = person_match.group(0).replace('remind', '').strip()
            entities["recipient"] = person if person != "me" else "self"
        else:
            entities["recipient"] = "self"

        # Extract reminder message (text after "to" or "for")
        message_match = re.search(r'(?:to|for|about)\s+(.+?)(?:\s+(?:at|on|tomorrow|today)|\s*$)', text)
        if message_match:
            entities["message"] = message_match.group(1).strip()
        else:
            # Fall back to the original text
            entities["message"] = text

        return entities

    def _parse_note(self, text: str) -> Dict[str, Any]:
        """
        Parse note command.
        Example: "add note to ensure we finish production deployment"
        """
        entities = {}

        # Extract note content (everything after "note" keywords)
        note_match = re.search(r'(?:add\s+note|take\s+note|note)[:\s]+(.+)', text, re.IGNORECASE)
        if note_match:
            entities["content"] = note_match.group(1).strip()
        else:
            entities["content"] = text

        # Check if it's an action item
        if any(keyword in text.lower() for keyword in ['ensure', 'must', 'need to', 'should', 'finish', 'complete']):
            entities["is_action_item"] = True
            entities["priority"] = "high"

        return entities

    def _parse_task(self, text: str) -> Dict[str, Any]:
        """
        Parse task command.
        Example: "need to finish the project report by Friday"
        """
        entities = {}

        # Extract task description
        task_match = re.search(r'(?:need\s+to|must|should|todo:?)\s+(.+?)(?:\s+by|\s+before|\s*$)', text, re.IGNORECASE)
        if task_match:
            entities["task_description"] = task_match.group(1).strip()
        else:
            entities["task_description"] = text

        # Extract deadline
        deadline = self._parse_natural_date(text)
        if deadline:
            entities["due_date"] = deadline

        # Determine priority
        if any(word in text.lower() for word in ['urgent', 'asap', 'immediately', 'critical']):
            entities["priority"] = "P1"
        elif any(word in text.lower() for word in ['important', 'soon']):
            entities["priority"] = "P2"
        else:
            entities["priority"] = "P3"

        return entities

    def _parse_natural_date(self, text: str) -> Optional[datetime]:
        """
        Parse natural language date/time expressions.
        Examples: "tomorrow", "next Tuesday", "at 8pm", "2-3pm tomorrow"
        """
        # Use dateparser library for robust parsing
        settings = {
            'PREFER_DATES_FROM': 'future',
            'RELATIVE_BASE': datetime.now(),
            'TIMEZONE': self.timezone,
            'RETURN_AS_TIMEZONE_AWARE': False
        }

        parsed = dateparser.parse(text, settings=settings)
        return parsed

    def _extract_time_range(self, text: str) -> Optional[Tuple[datetime, datetime]]:
        """
        Extract time range from text.
        Examples: "2-3pm tomorrow", "from 2pm to 3pm today"
        """
        # Try to find explicit time ranges
        range_patterns = [
            r'(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s*-\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)',
            r'from\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s+to\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)',
        ]

        for pattern in range_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                start_str = match.group(1)
                end_str = match.group(2)

                # Find the date context
                date_context = text

                # Parse start time
                start_time = dateparser.parse(f"{start_str} {date_context}", settings={
                    'PREFER_DATES_FROM': 'future',
                    'TIMEZONE': self.timezone
                })

                # Parse end time
                end_time = dateparser.parse(f"{end_str} {date_context}", settings={
                    'PREFER_DATES_FROM': 'future',
                    'TIMEZONE': self.timezone
                })

                if start_time and end_time:
                    # If end time is before start time, assume it's the same day but later
                    if end_time <= start_time:
                        end_time = end_time.replace(hour=end_time.hour + 12)

                    return (start_time, end_time)

        return None

    def parse_time_duration(self, text: str) -> Optional[int]:
        """
        Extract duration in minutes from text.
        Examples: "5 minutes", "2 hours", "30 min"
        """
        duration_match = re.search(r'(\d+)\s*(?:minute|min|hour|hr)s?', text, re.IGNORECASE)
        if duration_match:
            duration = int(duration_match.group(1))

            if 'hour' in text.lower() or 'hr' in text.lower():
                return duration * 60
            else:
                return duration

        return None


# Convenience function for quick parsing
def parse_natural_command(text: str) -> Dict[str, Any]:
    """
    Quick function to parse a natural language command.

    Args:
        text: Natural language command

    Returns:
        Parsed command with intent and entities
    """
    parser = NaturalLanguageParser()
    return parser.parse_command(text)
