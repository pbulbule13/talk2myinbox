"""
System Settings and Configuration
All behavior is configurable and environment-agnostic
"""

from typing import Literal
from pydantic import BaseModel, Field


class SystemSettings(BaseModel):
    """
    Main configuration for the voice-enabled email & calendar automation system.
    The voice_agent_name can be customized (default: "Vinegar").
    """

    # Voice Agent Identity
    voice_agent_name: str = Field(
        default="Vinegar",
        description="Friendly name users call the voice agent"
    )

    # Cloud & Deployment
    cloud_provider: Literal["gcp", "aws", "azure", "on_prem"] = Field(
        default="gcp",
        description="Target cloud platform for deployment"
    )

    # Authorization & Security
    auth_code_length: int = Field(default=4, ge=4, le=8)
    auth_code_expiry_minutes: int = Field(default=10, ge=5, le=60)

    # Tone & Communication
    tone_default: Literal["formal", "warm", "concise", "friendly"] = Field(
        default="formal"
    )
    vip_domains: list[str] = Field(
        default_factory=lambda: ["partner.com", "investor.org"],
        description="Email domains that get high priority"
    )

    # Follow-up & Scheduling
    followup_default_days: int = Field(default=3, ge=1, le=14)
    calendar_block_rules: list[str] = Field(
        default_factory=lambda: ["Friday 14:00-18:00 avoid"],
        description="Calendar rules for blocking/avoiding times"
    )

    # Storage & Database
    storage_backend: Literal["postgres", "sqlite", "firestore", "bigquery"] = Field(
        default="postgres"
    )
    realtime_logs: bool = Field(
        default=True,
        description="Enable real-time log streaming to dashboard"
    )

    # Email Integration
    email_provider: Literal["gmail_api", "imap_smtp", "outlook_graph"] = Field(
        default="gmail_api"
    )
    gmail_credentials_path: str = Field(default="./config/gmail_credentials.json")

    # Calendar Integration
    calendar_provider: Literal["google_calendar", "caldav", "outlook_calendar"] = Field(
        default="google_calendar"
    )
    calendar_credentials_path: str = Field(default="./config/calendar_credentials.json")

    # Voice I/O
    tts_provider: Literal["elevenlabs", "google_tts", "azure_tts"] = Field(
        default="elevenlabs"
    )
    stt_provider: Literal["whisper", "google_stt", "azure_stt"] = Field(
        default="whisper"
    )
    elevenlabs_api_key: str | None = Field(default=None)
    elevenlabs_voice_id: str = Field(default="21m00Tcm4TlvDq8ikWAM")  # Default voice

    # LLM Configuration
    llm_provider: Literal["openai", "anthropic", "azure_openai"] = Field(
        default="openai"
    )
    llm_model: str = Field(default="gpt-4")
    llm_temperature: float = Field(default=0.7, ge=0.0, le=2.0)

    # API & Endpoints
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000, ge=1000, le=65535)
    websocket_enabled: bool = Field(default=True)

    class Config:
        env_file = ".env"
        env_prefix = "VOICE_AGENT_"
