"""
Gemini Multimodal Service
Universal image processing using Gemini 1.5 Flash/Pro for text extraction,
calendar events, and general image understanding.
"""

import os
import base64
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class GeminiMultimodalProcessor:
    """Process images using Gemini 1.5 Flash/Pro multimodal capabilities."""

    def __init__(self):
        """Initialize Gemini API."""
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai not available. Install: pip install google-generativeai")

        # Get API key
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not found in environment variables")

        genai.configure(api_key=api_key)

        # Use Gemini 2.5 Flash for fast, cost-effective processing
        # Available models: gemini-2.5-flash, gemini-2.0-flash, gemini-flash-latest
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.model = genai.GenerativeModel(model_name)

    def extract_text_from_image(
        self,
        image_path: str,
        context: Optional[str] = None
    ) -> Tuple[str, Optional[str]]:
        """
        Extract text from any image using Gemini vision.

        Args:
            image_path: Path to image file
            context: Optional context hint (e.g., "calendar", "receipt", "document")

        Returns:
            Tuple of (extracted_text, error_message)
        """
        try:
            # Read and encode image
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # Build prompt based on context
            if context and "calendar" in context.lower():
                prompt = self._build_calendar_extraction_prompt()
            else:
                prompt = """Extract ALL text visible in this image.

Be comprehensive and accurate:
1. Extract all readable text, preserving structure
2. Include headings, labels, and body text
3. Maintain logical reading order
4. If it's a document, preserve formatting
5. If it's handwritten, do your best to transcribe
6. If there's a calendar, extract all events with dates and times

Return the extracted text in a clear, readable format."""

            # Create image part
            image_parts = [
                {
                    "mime_type": self._get_mime_type(image_path),
                    "data": base64.b64encode(image_data).decode('utf-8')
                }
            ]

            # Generate content
            response = self.model.generate_content([prompt, image_parts[0]])

            if not response or not response.text:
                return "", "Gemini returned empty response"

            return response.text.strip(), None

        except Exception as e:
            return "", f"Gemini extraction failed: {str(e)}"

    def extract_calendar_events(
        self,
        image_path: str,
        reference_date: Optional[datetime] = None
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Extract calendar events from image using Gemini.

        Returns:
            Tuple of (events_list, error_message)
        """
        try:
            if not reference_date:
                reference_date = datetime.now()

            # Read and encode image
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # Build calendar extraction prompt
            prompt = self._build_calendar_extraction_prompt(reference_date)

            # Create image part
            image_parts = [
                {
                    "mime_type": self._get_mime_type(image_path),
                    "data": base64.b64encode(image_data).decode('utf-8')
                }
            ]

            # Generate content
            response = self.model.generate_content([prompt, image_parts[0]])

            if not response or not response.text:
                return [], "Gemini returned empty response"

            # Parse JSON response
            events_data = self._parse_calendar_response(response.text)

            return events_data, None

        except Exception as e:
            return [], f"Calendar extraction failed: {str(e)}"

    def analyze_image(
        self,
        image_path: str,
        question: str = "What's in this image?"
    ) -> Tuple[str, Optional[str]]:
        """
        Analyze image and answer questions about it.

        Args:
            image_path: Path to image
            question: Question to ask about the image

        Returns:
            Tuple of (answer, error_message)
        """
        try:
            # Read and encode image
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # Create image part
            image_parts = [
                {
                    "mime_type": self._get_mime_type(image_path),
                    "data": base64.b64encode(image_data).decode('utf-8')
                }
            ]

            # Generate content
            response = self.model.generate_content([question, image_parts[0]])

            if not response or not response.text:
                return "", "Gemini returned empty response"

            return response.text.strip(), None

        except Exception as e:
            return "", f"Image analysis failed: {str(e)}"

    def _build_calendar_extraction_prompt(self, reference_date: Optional[datetime] = None) -> str:
        """Build structured prompt for calendar event extraction."""
        if not reference_date:
            reference_date = datetime.now()

        return f"""You are an expert at extracting calendar events from images.

Analyze this image and extract ALL calendar events visible.

**Reference Date:** {reference_date.strftime('%Y-%m-%d')} (Use this for context)

**Instructions:**
1. Identify calendar events in the image
2. Extract for each event:
   - Event title/name
   - Date (YYYY-MM-DD format - infer from calendar context)
   - Start time (HH:MM format, 24-hour clock)
   - End time (if visible)
   - Location (if visible)
   - Any additional details

3. Be liberal - extract anything that looks like an event
4. For missing information:
   - If no time: mark as "all-day" or infer from context
   - If date unclear: use calendar's month/year + day number
   - If abbreviated: expand reasonably

**Output Format (STRICT JSON):**
Return ONLY a JSON array with this structure:

```json
[
  {{
    "title": "Event Name",
    "date": "YYYY-MM-DD",
    "start_time": "HH:MM",
    "end_time": "HH:MM",
    "all_day": false,
    "location": "Location or null",
    "description": "Additional details or null"
  }}
]
```

**CRITICAL:** Return ONLY the JSON array. No markdown, no explanation.
Start with [ and end with ].
If no events found, return []
"""

    def _parse_calendar_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse JSON response from Gemini."""
        try:
            # Clean response
            text = response_text.strip()

            # Remove markdown code blocks if present
            if text.startswith('```json'):
                text = text[7:]
            elif text.startswith('```'):
                text = text[3:]

            if text.endswith('```'):
                text = text[:-3]

            text = text.strip()

            # Parse JSON
            events_data = json.loads(text)

            if not isinstance(events_data, list):
                print(f"Response is not a list: {type(events_data)}")
                return []

            return events_data

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {response_text[:500]}")
            return []
        except Exception as e:
            print(f"Error parsing response: {e}")
            return []

    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type from file extension."""
        ext = file_path.lower().split('.')[-1]
        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'bmp': 'image/bmp',
            'tiff': 'image/tiff',
            'tif': 'image/tiff'
        }
        return mime_types.get(ext, 'image/jpeg')

    def is_calendar_image(self, image_path: str) -> Tuple[bool, float]:
        """
        Determine if an image contains a calendar.

        Returns:
            Tuple of (is_calendar, confidence_score)
        """
        try:
            answer, error = self.analyze_image(
                image_path,
                "Is this image a calendar, schedule, or agenda? Answer with just 'yes' or 'no', followed by your confidence (0-100%)."
            )

            if error:
                return False, 0.0

            # Parse response
            answer_lower = answer.lower()
            is_calendar = 'yes' in answer_lower[:20]

            # Try to extract confidence
            import re
            confidence_match = re.search(r'(\d+)%', answer)
            confidence = float(confidence_match.group(1)) / 100.0 if confidence_match else 0.7

            return is_calendar, confidence

        except Exception as e:
            print(f"Error checking if calendar: {e}")
            return False, 0.0
