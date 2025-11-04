"""
Output Node: Converts reports to audio using Text-to-Speech.
Supports ElevenLabs API and local TTS engines.
"""

from typing import Dict, Any, Optional
import os
from pathlib import Path
import requests

# Conditional imports for local TTS
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

from data_models.pydantic_schemas import FinalAgentReport


class ElevenLabsOutput:
    """
    ElevenLabs API integration for high-quality text-to-speech.
    """

    def __init__(self):
        """Initialize ElevenLabs client."""
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not set in environment")

        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Default voice
        self.model_id = os.getenv("ELEVENLABS_MODEL_ID", "eleven_monolingual_v1")

        self.base_url = "https://api.elevenlabs.io/v1"
        self.output_dir = Path(os.getenv("AUDIO_OUTPUT_DIR", "./audio_output"))
        self.output_dir.mkdir(exist_ok=True)

    def text_to_speech(self, text: str, output_filename: str = "report.mp3") -> str:
        """
        Convert text to speech using ElevenLabs API.

        Args:
            text: Text to convert to speech
            output_filename: Name of output audio file

        Returns:
            Path to generated audio file
        """
        try:
            url = f"{self.base_url}/text-to-speech/{self.voice_id}"

            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }

            data = {
                "text": text,
                "model_id": self.model_id,
                "voice_settings": {
                    "stability": float(os.getenv("ELEVENLABS_STABILITY", "0.5")),
                    "similarity_boost": float(os.getenv("ELEVENLABS_SIMILARITY", "0.75"))
                }
            }

            response = requests.post(url, json=data, headers=headers)

            if response.status_code == 200:
                output_path = self.output_dir / output_filename

                with open(output_path, "wb") as f:
                    f.write(response.content)

                return str(output_path)
            else:
                raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"Error in ElevenLabs TTS: {e}")
            raise

    def format_report_for_speech(self, report: FinalAgentReport) -> str:
        """
        Format the report text for natural speech output.

        Args:
            report: FinalAgentReport object

        Returns:
            Formatted text suitable for TTS
        """
        speech_text = f"""
Good morning! Here's your daily journal summary for {report.summary.date}.

Daily Theme: {report.summary.daily_theme}

Here are your key decisions and learnings:
"""

        for idx, item in enumerate(report.summary.key_decisions_and_learnings, 1):
            speech_text += f"\n{idx}. {item}"

        speech_text += f"\n\nJournal Narrative:\n{report.summary.journal_narrative}"

        if report.pending_actions:
            speech_text += f"\n\nYou have {len(report.pending_actions)} pending action items. "

            # Announce top 3 priorities
            top_actions = report.pending_actions[:3]
            speech_text += "Here are your top priorities:\n"

            for idx, action in enumerate(top_actions, 1):
                speech_text += f"\n{idx}. {action.task_description}"

        speech_text += f"\n\nSuggested first task for today: {report.suggested_first_task}"

        speech_text += "\n\nHave a productive day!"

        return speech_text


class LocalTTSOutput:
    """
    Local text-to-speech using pyttsx3 (offline, free).
    Useful for development and testing.
    """

    def __init__(self):
        """Initialize local TTS engine."""
        if not PYTTSX3_AVAILABLE:
            raise ImportError("pyttsx3 not available. Install with: pip install pyttsx3")

        self.engine = pyttsx3.init()

        # Configure voice properties
        rate = int(os.getenv("TTS_RATE", "150"))
        volume = float(os.getenv("TTS_VOLUME", "0.9"))

        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)

        self.output_dir = Path(os.getenv("AUDIO_OUTPUT_DIR", "./audio_output"))
        self.output_dir.mkdir(exist_ok=True)

    def text_to_speech(self, text: str, output_filename: str = "report.mp3") -> str:
        """
        Convert text to speech using local TTS engine.

        Args:
            text: Text to convert to speech
            output_filename: Name of output audio file

        Returns:
            Path to generated audio file
        """
        try:
            output_path = self.output_dir / output_filename

            self.engine.save_to_file(text, str(output_path))
            self.engine.runAndWait()

            return str(output_path)

        except Exception as e:
            print(f"Error in local TTS: {e}")
            raise

    def format_report_for_speech(self, report: FinalAgentReport) -> str:
        """Format the report for speech (same as ElevenLabs)."""
        return ElevenLabsOutput().format_report_for_speech(report)


class TTSManager:
    """
    Main TTS manager that handles different TTS backends.
    """

    def __init__(self):
        """Initialize TTS backend based on configuration."""
        self.backend_type = os.getenv("TTS_BACKEND", "elevenlabs")  # elevenlabs, local, none

        if self.backend_type == "elevenlabs":
            try:
                self.backend = ElevenLabsOutput()
            except ValueError:
                print("ElevenLabs API key not configured. Falling back to local TTS.")
                self.backend = LocalTTSOutput() if PYTTSX3_AVAILABLE else None
        elif self.backend_type == "local":
            self.backend = LocalTTSOutput() if PYTTSX3_AVAILABLE else None
        else:
            self.backend = None

    def generate_audio(self, report: FinalAgentReport, output_filename: str = None) -> Optional[str]:
        """
        Generate audio from report.

        Args:
            report: FinalAgentReport object
            output_filename: Optional custom filename

        Returns:
            Path to audio file, or None if TTS disabled
        """
        if not self.backend:
            print("TTS disabled or not available.")
            return None

        try:
            # Format report for speech
            speech_text = self.backend.format_report_for_speech(report)

            # Generate filename if not provided
            if not output_filename:
                output_filename = f"report_{report.summary.date}.mp3"

            # Generate audio
            audio_path = self.backend.text_to_speech(speech_text, output_filename)

            return audio_path

        except Exception as e:
            print(f"Error generating audio: {e}")
            return None


def tts_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node for text-to-speech output.

    Args:
        state: Current agent state with final_report populated

    Returns:
        Updated state with audio_output_path
    """
    final_report = state.get("final_report")

    if not final_report:
        print("No report available for TTS")
        return state

    # Initialize TTS manager
    tts_manager = TTSManager()

    # Generate audio
    audio_path = tts_manager.generate_audio(final_report)

    if audio_path:
        state["audio_output_path"] = audio_path
        print(f"Audio report generated: {audio_path}")
    else:
        print("Audio generation skipped or failed")

    return state


def format_text_output(report: FinalAgentReport) -> str:
    """
    Format the report as text output (for console or file).

    Args:
        report: FinalAgentReport object

    Returns:
        Formatted text representation
    """
    output = f"""
{'='*60}
DAILY JOURNAL SUMMARY - {report.summary.date}
{'='*60}

DAILY THEME
{'-'*60}
{report.summary.daily_theme}

KEY DECISIONS & LEARNINGS
{'-'*60}
"""

    for idx, item in enumerate(report.summary.key_decisions_and_learnings, 1):
        output += f"{idx}. {item}\n"

    output += f"""
JOURNAL NARRATIVE
{'-'*60}
{report.summary.journal_narrative}

PENDING ACTIONS ({len(report.pending_actions)})
{'-'*60}
"""

    for idx, action in enumerate(report.pending_actions, 1):
        output += f"{idx}. [{action.priority}] {action.task_description}\n"

    output += f"""
SUGGESTED FIRST TASK
{'-'*60}
{report.suggested_first_task}

{'='*60}
"""

    return output
