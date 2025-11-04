"""
Configuration management for Cognitive Journal Agent.
Centralizes all environment variables and settings.
Supports .env files and provides sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

# Try to load from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    ENV_LOADED = True
except ImportError:
    ENV_LOADED = False
    print("Warning: python-dotenv not installed. Environment variables must be set manually.")


# ===========================
# LLM Configuration
# ===========================

@dataclass
class LLMConfig:
    """Configuration for LLM providers."""
    provider: str = os.getenv("LLM_PROVIDER", "openai")
    model_name: str = os.getenv("LLM_MODEL_NAME", "gpt-4")
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))

    # API Keys
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")

    # Agent-specific settings
    agent_model_name: str = os.getenv("AGENT_MODEL_NAME", "gpt-4")
    agent_temperature: float = float(os.getenv("AGENT_TEMPERATURE", "0.2"))
    agent_max_iterations: int = int(os.getenv("AGENT_MAX_ITERATIONS", "10"))
    agent_verbose: bool = os.getenv("AGENT_VERBOSE", "true").lower() == "true"

    # Processing settings
    use_llm_processing: bool = os.getenv("USE_LLM_PROCESSING", "true").lower() == "true"
    use_llm_reporting: bool = os.getenv("USE_LLM_REPORTING", "true").lower() == "true"


# ===========================
# Storage Configuration
# ===========================

@dataclass
class StorageConfig:
    """Configuration for storage backends."""
    backend: str = os.getenv("STORAGE_BACKEND", "json")  # firestore, json, sqlite

    # Firestore settings
    google_cloud_credentials: Optional[str] = os.getenv("GOOGLE_CLOUD_CREDENTIALS")
    user_id: str = os.getenv("USER_ID", "default_user")

    # Local storage settings
    storage_dir: Path = field(default_factory=lambda: Path(os.getenv("STORAGE_DIR", "./data")))
    sqlite_db_path: Path = field(default_factory=lambda: Path(os.getenv("SQLITE_DB_PATH", "./data/journal.db")))


# ===========================
# TTS Configuration
# ===========================

@dataclass
class TTSConfig:
    """Configuration for text-to-speech."""
    backend: str = os.getenv("TTS_BACKEND", "elevenlabs")  # elevenlabs, local, none
    enabled: bool = os.getenv("TTS_ENABLED", "true").lower() == "true"

    # ElevenLabs settings
    elevenlabs_api_key: Optional[str] = os.getenv("ELEVENLABS_API_KEY")
    elevenlabs_voice_id: str = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
    elevenlabs_model_id: str = os.getenv("ELEVENLABS_MODEL_ID", "eleven_monolingual_v1")
    elevenlabs_stability: float = float(os.getenv("ELEVENLABS_STABILITY", "0.5"))
    elevenlabs_similarity: float = float(os.getenv("ELEVENLABS_SIMILARITY", "0.75"))

    # Local TTS settings
    tts_rate: int = int(os.getenv("TTS_RATE", "150"))
    tts_volume: float = float(os.getenv("TTS_VOLUME", "0.9"))

    # Output settings
    audio_output_dir: Path = field(default_factory=lambda: Path(os.getenv("AUDIO_OUTPUT_DIR", "./audio_output")))


# ===========================
# Email Configuration
# ===========================

@dataclass
class EmailConfig:
    """Configuration for email operations."""
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: Optional[str] = os.getenv("SMTP_USERNAME")
    smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")


# ===========================
# Calendar Configuration
# ===========================

@dataclass
class CalendarConfig:
    """Configuration for calendar operations."""
    backend: str = os.getenv("CALENDAR_BACKEND", "local")  # google, outlook, local

    # Google Calendar
    google_calendar_credentials: Optional[str] = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")

    # Outlook
    outlook_client_id: Optional[str] = os.getenv("OUTLOOK_CLIENT_ID")
    outlook_client_secret: Optional[str] = os.getenv("OUTLOOK_CLIENT_SECRET")

    # Local calendar
    calendar_file: Path = field(default_factory=lambda: Path(os.getenv("CALENDAR_FILE", "./calendar_events.json")))


# ===========================
# Ingestion Configuration
# ===========================

@dataclass
class IngestionConfig:
    """Configuration for multimodal ingestion."""
    temp_ingestion_dir: Path = field(default_factory=lambda: Path(os.getenv("TEMP_INGESTION_DIR", "./temp_ingestion")))
    tesseract_cmd: Optional[str] = os.getenv("TESSERACT_CMD")


# ===========================
# File Operations Configuration
# ===========================

@dataclass
class FileOpsConfig:
    """Configuration for file operations."""
    base_dir: Path = field(default_factory=lambda: Path(os.getenv("FILE_OPERATIONS_BASE_DIR", os.getcwd())))


# ===========================
# Web Search Configuration
# ===========================

@dataclass
class WebSearchConfig:
    """Configuration for web search."""
    search_api_key: Optional[str] = os.getenv("SEARCH_API_KEY")
    search_engine_id: Optional[str] = os.getenv("SEARCH_ENGINE_ID")


# ===========================
# API Configuration (for FastAPI)
# ===========================

@dataclass
class APIConfig:
    """Configuration for API server."""
    host: str = os.getenv("API_HOST", "0.0.0.0")
    port: int = int(os.getenv("API_PORT", "8000"))
    reload: bool = os.getenv("API_RELOAD", "true").lower() == "true"
    cors_origins: list = field(default_factory=lambda: os.getenv("CORS_ORIGINS", "*").split(","))


# ===========================
# Main Configuration Class
# ===========================

@dataclass
class Config:
    """Main configuration container."""
    llm: LLMConfig = field(default_factory=LLMConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    email: EmailConfig = field(default_factory=EmailConfig)
    calendar: CalendarConfig = field(default_factory=CalendarConfig)
    ingestion: IngestionConfig = field(default_factory=IngestionConfig)
    file_ops: FileOpsConfig = field(default_factory=FileOpsConfig)
    web_search: WebSearchConfig = field(default_factory=WebSearchConfig)
    api: APIConfig = field(default_factory=APIConfig)

    def validate(self) -> list:
        """
        Validate configuration and return list of warnings/errors.

        Returns:
            List of validation messages
        """
        messages = []

        # Check LLM configuration
        if self.llm.provider == "openai" and not self.llm.openai_api_key:
            messages.append("WARNING: OpenAI API key not set (USE_LLM_PROCESSING and USE_LLM_REPORTING will be disabled)")

        if self.llm.provider == "anthropic" and not self.llm.anthropic_api_key:
            messages.append("WARNING: Anthropic API key not set")

        # Check TTS configuration
        if self.tts.enabled and self.tts.backend == "elevenlabs" and not self.tts.elevenlabs_api_key:
            messages.append("WARNING: ElevenLabs API key not set (TTS will fall back to local)")

        # Check storage configuration
        if self.storage.backend == "firestore" and not self.storage.google_cloud_credentials:
            messages.append("WARNING: Google Cloud credentials not set (storage will fall back to JSON)")

        # Check email configuration
        if not self.email.smtp_username or not self.email.smtp_password:
            messages.append("INFO: Email credentials not configured (email tool will not work)")

        # Create necessary directories
        self.storage.storage_dir.mkdir(exist_ok=True)
        self.tts.audio_output_dir.mkdir(exist_ok=True)
        self.ingestion.temp_ingestion_dir.mkdir(exist_ok=True)

        return messages

    def print_config(self):
        """Print current configuration."""
        print("\n" + "="*60)
        print("COGNITIVE JOURNAL AGENT CONFIGURATION")
        print("="*60)

        print(f"\n[LLM]")
        print(f"  Provider: {self.llm.provider}")
        print(f"  Model: {self.llm.model_name}")
        print(f"  Temperature: {self.llm.temperature}")
        print(f"  Use LLM Processing: {self.llm.use_llm_processing}")
        print(f"  Use LLM Reporting: {self.llm.use_llm_reporting}")

        print(f"\n[Storage]")
        print(f"  Backend: {self.storage.backend}")
        print(f"  Directory: {self.storage.storage_dir}")

        print(f"\n[TTS]")
        print(f"  Backend: {self.tts.backend}")
        print(f"  Enabled: {self.tts.enabled}")

        print(f"\n[Email]")
        print(f"  SMTP Host: {self.email.smtp_host}")
        print(f"  Configured: {'Yes' if self.email.smtp_username else 'No'}")

        print(f"\n[Calendar]")
        print(f"  Backend: {self.calendar.backend}")

        print("\n" + "="*60 + "\n")


# ===========================
# Global Configuration Instance
# ===========================

# Create global config instance
config = Config()

# Validate on import
validation_messages = config.validate()
if validation_messages:
    print("\nConfiguration Validation:")
    for msg in validation_messages:
        print(f"  {msg}")
    print()


# ===========================
# Configuration Helper Functions
# ===========================

def get_config() -> Config:
    """Get the global configuration instance."""
    return config


def reload_config():
    """Reload configuration from environment."""
    global config
    if ENV_LOADED:
        load_dotenv(override=True)
    config = Config()
    return config


def create_env_template():
    """Create a .env.template file with all configuration options."""
    template = """
# Cognitive Journal Agent Configuration Template
# Copy this file to .env and fill in your values

# ===========================
# LLM Configuration
# ===========================
LLM_PROVIDER=openai
LLM_MODEL_NAME=gpt-4
LLM_TEMPERATURE=0.3
OPENAI_API_KEY=your_openai_api_key_here
# ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Agent Settings
AGENT_MODEL_NAME=gpt-4
AGENT_TEMPERATURE=0.2
AGENT_MAX_ITERATIONS=10
AGENT_VERBOSE=true

# Processing Settings
USE_LLM_PROCESSING=true
USE_LLM_REPORTING=true

# ===========================
# Storage Configuration
# ===========================
STORAGE_BACKEND=json
STORAGE_DIR=./data
# GOOGLE_CLOUD_CREDENTIALS=/path/to/credentials.json
USER_ID=default_user

# ===========================
# TTS Configuration
# ===========================
TTS_BACKEND=elevenlabs
TTS_ENABLED=true
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
AUDIO_OUTPUT_DIR=./audio_output

# ===========================
# Email Configuration
# ===========================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here

# ===========================
# Calendar Configuration
# ===========================
CALENDAR_BACKEND=local
CALENDAR_FILE=./calendar_events.json

# ===========================
# Ingestion Configuration
# ===========================
TEMP_INGESTION_DIR=./temp_ingestion
# TESSERACT_CMD=/usr/local/bin/tesseract

# ===========================
# API Configuration
# ===========================
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
CORS_ORIGINS=*
    """.strip()

    with open(".env.template", "w") as f:
        f.write(template)

    print(".env.template created successfully!")


if __name__ == "__main__":
    # Print configuration when run directly
    config.print_config()

    # Create .env template
    create_env_template()
