"""
Ingestion Node: Handles multimodal input processing.
Supports: text, voice, images (OCR), PDFs, code snippets, calendar events.
All processors are configurable via environment variables.
"""

from typing import Dict, Any
from datetime import datetime
import os
import base64
import uuid
from pathlib import Path

# Conditional imports for multimodal processing
try:
    from PIL import Image
    import pytesseract

    # Configure Tesseract path for Windows
    if os.name == 'nt':  # Windows
        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from data_models.pydantic_schemas import JournalEntry


class MultimodalIngest:
    """
    Multimodal ingestion processor.
    Handles various input types and converts them to structured JournalEntry objects.
    """

    def __init__(self):
        """Initialize the ingestion processor with configuration."""
        self.supported_types = [
            "text_note",
            "voice_memo",
            "photo_ocr",
            "pdf_document",
            "code_snippet",
            "email",
            "calendar_event",
            "file_upload",
        ]

        # Configuration
        self.tesseract_cmd = os.getenv("TESSERACT_CMD", None)
        if self.tesseract_cmd and TESSERACT_AVAILABLE:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

        self.temp_dir = Path(os.getenv("TEMP_INGESTION_DIR", "./temp_ingestion"))
        self.temp_dir.mkdir(exist_ok=True)

    def process_text_note(self, content: str, metadata: Dict[str, Any] = None) -> JournalEntry:
        """Process a plain text note."""
        return JournalEntry(
            timestamp=datetime.now(),
            input_type="text_note",
            raw_content=content,
            source_id=f"text_{uuid.uuid4()}",
        )

    def process_voice_memo(self, audio_file_path: str, metadata: Dict[str, Any] = None) -> JournalEntry:
        """
        Process a voice memo using speech-to-text.
        Supports: WAV, MP3, FLAC, OGG
        """
        if not SPEECH_RECOGNITION_AVAILABLE:
            return JournalEntry(
                timestamp=datetime.now(),
                input_type="voice_memo",
                raw_content="[Speech recognition not available. Install speech_recognition package.]",
                source_id=f"voice_{uuid.uuid4()}",
            )

        try:
            recognizer = sr.Recognizer()

            # Load audio file
            with sr.AudioFile(audio_file_path) as source:
                audio_data = recognizer.record(source)

            # Transcribe using Google Speech Recognition (free, no API key required)
            # For production, use: Google Cloud Speech, Whisper API, or Azure Speech
            transcription = recognizer.recognize_google(audio_data)

            return JournalEntry(
                timestamp=datetime.now(),
                input_type="voice_memo",
                raw_content=transcription,
                source_id=f"voice_{Path(audio_file_path).stem}",
            )

        except sr.UnknownValueError:
            return JournalEntry(
                timestamp=datetime.now(),
                input_type="voice_memo",
                raw_content="[Could not understand audio]",
                source_id=f"voice_{uuid.uuid4()}",
            )
        except Exception as e:
            return JournalEntry(
                timestamp=datetime.now(),
                input_type="voice_memo",
                raw_content=f"[Error processing voice memo: {str(e)}]",
                source_id=f"voice_{uuid.uuid4()}",
            )

    def process_photo_ocr(self, image_path: str, metadata: Dict[str, Any] = None) -> JournalEntry:
        """
        Process an image using Gemini multimodal AI (primary) or OCR (fallback).
        Supports: PNG, JPG, JPEG, TIFF, BMP
        """
        # Try Gemini first (best results)
        try:
            from services.gemini_multimodal import GeminiMultimodalProcessor

            gemini = GeminiMultimodalProcessor()
            extracted_text, error = gemini.extract_text_from_image(image_path)

            if not error and extracted_text:
                # Store image path for later display
                image_metadata = {
                    "image_path": image_path,
                    "extraction_method": "gemini_multimodal",
                    **(metadata or {})
                }

                return JournalEntry(
                    timestamp=datetime.now(),
                    input_type="photo_ocr",
                    raw_content=extracted_text.strip(),
                    source_id=f"img_{Path(image_path).stem}",
                    metadata=image_metadata
                )
        except Exception as e:
            print(f"Gemini extraction failed, falling back to Tesseract: {e}")

        # Fallback to Tesseract OCR
        if not TESSERACT_AVAILABLE:
            return JournalEntry(
                timestamp=datetime.now(),
                input_type="photo_ocr",
                raw_content="[OCR not available. Install Pillow and pytesseract, and configure Tesseract.]",
                source_id=f"ocr_{uuid.uuid4()}",
            )

        try:
            image = Image.open(image_path)
            extracted_text = pytesseract.image_to_string(image)

            # Store image path
            image_metadata = {
                "image_path": image_path,
                "extraction_method": "tesseract_ocr",
                **(metadata or {})
            }

            return JournalEntry(
                timestamp=datetime.now(),
                input_type="photo_ocr",
                raw_content=extracted_text.strip() if extracted_text.strip() else "[No text detected in image]",
                source_id=f"ocr_{Path(image_path).stem}",
                metadata=image_metadata
            )

        except Exception as e:
            return JournalEntry(
                timestamp=datetime.now(),
                input_type="photo_ocr",
                raw_content=f"[Error processing image: {str(e)}]",
                source_id=f"ocr_{uuid.uuid4()}",
            )

    def process_pdf_document(self, pdf_path: str, metadata: Dict[str, Any] = None) -> JournalEntry:
        """
        Process a PDF document and extract text.
        """
        if not PDF_AVAILABLE:
            return JournalEntry(
                timestamp=datetime.now(),
                input_type="pdf_document",
                raw_content="[PDF processing not available. Install PyPDF2.]",
                source_id=f"pdf_{uuid.uuid4()}",
            )

        try:
            with open(pdf_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                extracted_text = []

                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    extracted_text.append(page.extract_text())

                full_text = "\n\n".join(extracted_text)

            return JournalEntry(
                timestamp=datetime.now(),
                input_type="pdf_document",
                raw_content=full_text.strip() if full_text.strip() else "[No text extracted from PDF]",
                source_id=f"pdf_{Path(pdf_path).stem}",
            )

        except Exception as e:
            return JournalEntry(
                timestamp=datetime.now(),
                input_type="pdf_document",
                raw_content=f"[Error processing PDF: {str(e)}]",
                source_id=f"pdf_{uuid.uuid4()}",
            )

    def process_code_snippet(self, code: str, language: str = "python", metadata: Dict[str, Any] = None) -> JournalEntry:
        """Process a code snippet."""
        content = f"[Code Snippet - {language}]\n\n{code}"

        return JournalEntry(
            timestamp=datetime.now(),
            input_type="code_snippet",
            raw_content=content,
            source_id=f"code_{uuid.uuid4()}",
        )

    def process_email(self, email_data: Dict[str, Any]) -> JournalEntry:
        """
        Process an email.
        Expected format: {
            'from': sender,
            'subject': subject,
            'body': body,
            'timestamp': datetime,
            'id': email_id
        }
        """
        content = f"""
From: {email_data.get('from', 'Unknown')}
Subject: {email_data.get('subject', 'No Subject')}

{email_data.get('body', '')}
        """.strip()

        return JournalEntry(
            timestamp=email_data.get('timestamp', datetime.now()),
            input_type="email",
            raw_content=content,
            source_id=f"email_{email_data.get('id', uuid.uuid4())}",
        )

    def process_calendar_event(self, event_data: Dict[str, Any]) -> JournalEntry:
        """
        Process a calendar event.
        Expected format: {
            'title': event_title,
            'start': start_time,
            'end': end_time,
            'description': description,
            'attendees': [list of attendees]
        }
        """
        content = f"""
Calendar Event: {event_data.get('title', 'Untitled Event')}
Start: {event_data.get('start', 'Unknown')}
End: {event_data.get('end', 'Unknown')}
Description: {event_data.get('description', 'No description')}
Attendees: {', '.join(event_data.get('attendees', []))}
        """.strip()

        return JournalEntry(
            timestamp=datetime.now(),
            input_type="calendar_event",
            raw_content=content,
            source_id=f"calendar_{uuid.uuid4()}",
        )

    def ingest(self, input_data: Dict[str, Any]) -> JournalEntry:
        """
        Main ingestion method. Routes to appropriate processor based on input type.

        Args:
            input_data: Dictionary with 'type' and type-specific fields

        Returns:
            JournalEntry object
        """
        input_type = input_data.get("type", "text_note")

        if input_type == "text_note":
            return self.process_text_note(
                content=input_data.get("content", ""),
                metadata=input_data.get("metadata")
            )

        elif input_type == "voice_memo":
            return self.process_voice_memo(
                audio_file_path=input_data.get("file_path", ""),
                metadata=input_data.get("metadata")
            )

        elif input_type == "photo_ocr":
            return self.process_photo_ocr(
                image_path=input_data.get("file_path", ""),
                metadata=input_data.get("metadata")
            )

        elif input_type == "pdf_document":
            return self.process_pdf_document(
                pdf_path=input_data.get("file_path", ""),
                metadata=input_data.get("metadata")
            )

        elif input_type == "code_snippet":
            return self.process_code_snippet(
                code=input_data.get("content", ""),
                language=input_data.get("language", "python"),
                metadata=input_data.get("metadata")
            )

        elif input_type == "email":
            return self.process_email(
                email_data=input_data.get("email_data", {})
            )

        elif input_type == "calendar_event":
            return self.process_calendar_event(
                event_data=input_data.get("event_data", {})
            )

        else:
            # Default to text processing for unknown types
            return self.process_text_note(
                content=str(input_data.get("content", "")),
                metadata=input_data.get("metadata")
            )


def ingestion_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node for ingestion processing.

    Args:
        state: Current agent state

    Returns:
        Updated state with new_entry populated
    """
    processor = MultimodalIngest()

    # Extract input data from state
    user_input = state.get("user_input", "")
    input_data = state.get("input_data", {})

    # If no structured input_data, treat as text note
    if not input_data:
        input_data = {
            "type": "text_note",
            "content": user_input
        }

    # Process the input
    journal_entry = processor.ingest(input_data)

    # Update state
    state["new_entry"] = journal_entry

    return state
