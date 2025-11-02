"""
Pytest configuration and fixtures for talk2myinbox tests
"""

import pytest
import asyncio
import os
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone

# Set test environment
os.environ["ENV"] = "test"
os.environ["EMAIL_MOCK_MODE"] = "true"
os.environ["CALENDAR_MOCK_MODE"] = "true"


# ============================================================================
# EVENT LOOP FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# APPLICATION FIXTURES
# ============================================================================

@pytest.fixture
def test_app():
    """Create FastAPI test application."""
    from server import app
    return app


@pytest.fixture
def client(test_app):
    """Create test client for API testing."""
    with TestClient(test_app) as test_client:
        yield test_client


# ============================================================================
# MOCK DATA FIXTURES
# ============================================================================

@pytest.fixture
def mock_email_data():
    """Mock email data for testing."""
    return {
        "id": "msg_123456",
        "thread_id": "thread_123",
        "from": "sender@example.com",
        "to": ["user@example.com"],
        "subject": "Test Email Subject",
        "body": "This is a test email body with some content.",
        "preview": "This is a test email body...",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "unread": True,
        "labels": ["INBOX", "UNREAD"],
        "attachments": []
    }


@pytest.fixture
def mock_email_list():
    """Mock list of emails."""
    return [
        {
            "id": f"msg_{i}",
            "thread_id": f"thread_{i}",
            "from": f"sender{i}@example.com",
            "to": ["user@example.com"],
            "subject": f"Test Email {i}",
            "preview": f"Email content {i}...",
            "timestamp": (datetime.now(timezone.utc) - timedelta(days=i)).isoformat(),
            "unread": i % 2 == 0,
        }
        for i in range(10)
    ]


@pytest.fixture
def mock_calendar_event():
    """Mock calendar event data."""
    now = datetime.now(timezone.utc)
    return {
        "id": "event_123",
        "title": "Test Meeting",
        "summary": "Test Meeting",
        "description": "This is a test meeting",
        "start": now.isoformat(),
        "end": (now + timedelta(hours=1)).isoformat(),
        "location": "Conference Room A",
        "attendees": [
            {"email": "user1@example.com", "responseStatus": "accepted"},
            {"email": "user2@example.com", "responseStatus": "tentative"}
        ],
        "organizer": {"email": "organizer@example.com"},
        "status": "confirmed"
    }


@pytest.fixture
def mock_calendar_events():
    """Mock list of calendar events."""
    now = datetime.now(timezone.utc)
    return [
        {
            "id": f"event_{i}",
            "title": f"Meeting {i}",
            "start": (now + timedelta(hours=i)).isoformat(),
            "end": (now + timedelta(hours=i+1)).isoformat(),
            "location": f"Room {i}",
        }
        for i in range(5)
    ]


@pytest.fixture
def mock_draft_data():
    """Mock email draft data."""
    return {
        "id": "draft_123",
        "to": ["recipient@example.com"],
        "subject": "Re: Test Email",
        "body": "Thank you for your email. I will respond shortly.",
        "thread_id": "thread_123",
        "reasoning": "This is a polite acknowledgment response",
        "status": "pending"
    }


@pytest.fixture
def mock_voice_query():
    """Mock voice query data."""
    return {
        "query": "Show me my unread emails",
        "mode": "voice",
        "user_id": "test_user",
        "session_id": "session_123"
    }


# ============================================================================
# ADAPTER FIXTURES (MOCKS)
# ============================================================================

@pytest.fixture
def mock_gmail_adapter():
    """Mock Gmail adapter."""
    adapter = AsyncMock()
    adapter.fetch_threads = AsyncMock(return_value=[])
    adapter.get_message = AsyncMock(return_value={})
    adapter.send_email = AsyncMock(return_value={"success": True, "message_id": "msg_123"})
    adapter.mark_as_read = AsyncMock(return_value=True)
    adapter.archive = AsyncMock(return_value=True)
    adapter.delete = AsyncMock(return_value=True)
    return adapter


@pytest.fixture
def mock_calendar_adapter():
    """Mock Calendar adapter."""
    adapter = AsyncMock()
    adapter.get_events = AsyncMock(return_value=[])
    adapter.create_event = AsyncMock(return_value={"success": True, "event_id": "event_123"})
    adapter.update_event = AsyncMock(return_value={"success": True})
    adapter.delete_event = AsyncMock(return_value={"success": True})
    return adapter


@pytest.fixture
def mock_tts_adapter():
    """Mock Text-to-Speech adapter."""
    adapter = Mock()
    adapter.synthesize = Mock(return_value=b"fake_audio_data")
    return adapter


@pytest.fixture
def mock_stt_adapter():
    """Mock Speech-to-Text adapter."""
    adapter = Mock()
    adapter.transcribe = Mock(return_value="transcribed text")
    return adapter


# ============================================================================
# AGENT FIXTURES (MOCKS)
# ============================================================================

@pytest.fixture
def mock_intent_agent():
    """Mock Intent Agent."""
    agent = AsyncMock()
    agent.process = AsyncMock(return_value={
        "intent": "query_emails",
        "entities": {"filter": "unread"},
        "confidence": 0.95
    })
    return agent


@pytest.fixture
def mock_reasoning_agent():
    """Mock Reasoning Agent."""
    agent = AsyncMock()
    agent.process = AsyncMock(return_value={
        "actions": [{"type": "fetch_emails", "params": {"unread_only": True}}],
        "reasoning": "User wants to see unread emails"
    })
    return agent


@pytest.fixture
def mock_draft_agent():
    """Mock Draft Agent."""
    agent = AsyncMock()
    agent.generate_draft = AsyncMock(return_value={
        "to": ["recipient@example.com"],
        "subject": "Re: Test",
        "body": "Draft response",
        "reasoning": "Generated response based on context"
    })
    return agent


@pytest.fixture
def mock_execution_agent():
    """Mock Execution Agent."""
    agent = AsyncMock()
    agent.execute = AsyncMock(return_value={
        "success": True,
        "results": [{"action": "fetch_emails", "data": []}]
    })
    return agent


# ============================================================================
# ORCHESTRATOR FIXTURES
# ============================================================================

@pytest.fixture
def mock_orchestrator():
    """Mock Voice Agent Orchestrator."""
    orchestrator = AsyncMock()
    orchestrator.process_query = AsyncMock(return_value={
        "text": "You have 5 unread emails",
        "intent": "query_emails",
        "drafts": [],
        "calendar_actions": [],
        "executed": [{"action": "fetch_emails"}],
        "logs": []
    })
    orchestrator.summarize_inbox = AsyncMock(return_value={
        "total": 10,
        "unread": 5,
        "drafts": [],
        "summary": "You have 5 unread emails out of 10 total"
    })
    return orchestrator


# ============================================================================
# DATABASE FIXTURES (if needed in future)
# ============================================================================

@pytest.fixture
async def db_session():
    """Mock database session."""
    # For now, return None as we don't have a database
    # In future, this would create a test database session
    return None


# ============================================================================
# AUTHENTICATION FIXTURES
# ============================================================================

@pytest.fixture
def mock_user():
    """Mock authenticated user."""
    return {
        "id": "user_123",
        "email": "testuser@example.com",
        "name": "Test User",
        "authenticated": True
    }


@pytest.fixture
def auth_headers(mock_user):
    """Mock authentication headers."""
    return {
        "Authorization": "Bearer test_token_123",
        "X-User-ID": mock_user["id"]
    }


# ============================================================================
# FILE FIXTURES
# ============================================================================

@pytest.fixture
def temp_audio_file(tmp_path):
    """Create temporary audio file for testing."""
    audio_file = tmp_path / "test_audio.mp3"
    audio_file.write_bytes(b"fake_audio_content")
    return audio_file


@pytest.fixture
def temp_credentials_file(tmp_path):
    """Create temporary credentials file."""
    creds_file = tmp_path / "credentials.json"
    creds_file.write_text('{"type": "test", "client_id": "test_client"}')
    return creds_file


# ============================================================================
# ENVIRONMENT FIXTURES
# ============================================================================

@pytest.fixture
def test_env_vars(monkeypatch):
    """Set test environment variables."""
    env_vars = {
        "ENV": "test",
        "EMAIL_MOCK_MODE": "true",
        "CALENDAR_MOCK_MODE": "true",
        "OPENAI_API_KEY": "test_openai_key",
        "ANTHROPIC_API_KEY": "test_anthropic_key",
        "ELEVENLABS_API_KEY": "test_elevenlabs_key",
        "LOG_LEVEL": "DEBUG"
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


# ============================================================================
# CLEANUP FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Cleanup after each test."""
    yield
    # Add any cleanup logic here
    # For example: clear caches, reset mocks, etc.


# ============================================================================
# MARKER FIXTURES
# ============================================================================

@pytest.fixture
def use_real_services():
    """Marker for tests that need real external services."""
    # Check if we should run tests against real services
    return os.getenv("USE_REAL_SERVICES", "false").lower() == "true"


# ============================================================================
# RESPONSE FIXTURES
# ============================================================================

@pytest.fixture
def mock_api_success_response():
    """Mock successful API response."""
    return {
        "status": "success",
        "data": {},
        "message": "Operation completed successfully"
    }


@pytest.fixture
def mock_api_error_response():
    """Mock error API response."""
    return {
        "status": "error",
        "error": "Something went wrong",
        "code": "ERR_UNKNOWN"
    }


# ============================================================================
# TIME FIXTURES
# ============================================================================

@pytest.fixture
def freeze_time():
    """Fixture to freeze time for testing."""
    frozen_time = datetime(2025, 11, 2, 12, 0, 0, tzinfo=timezone.utc)
    return frozen_time


# ============================================================================
# PERFORMANCE FIXTURES
# ============================================================================

@pytest.fixture
def performance_monitor():
    """Monitor test performance."""
    import time
    start_time = time.time()
    yield
    end_time = time.time()
    duration = end_time - start_time
    if duration > 1.0:  # Warn if test takes more than 1 second
        pytest.warn(f"Slow test detected: {duration:.2f}s")


# ============================================================================
# PARAMETRIZE FIXTURES
# ============================================================================

@pytest.fixture(params=["text", "semi-voice", "full-voice"])
def voice_mode(request):
    """Parametrize voice modes for testing."""
    return request.param


@pytest.fixture(params=["openai", "anthropic", "google"])
def llm_provider(request):
    """Parametrize LLM providers for testing."""
    return request.param


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_mock_response(status_code: int, json_data: dict):
    """Create a mock HTTP response."""
    response = Mock()
    response.status_code = status_code
    response.json = Mock(return_value=json_data)
    response.text = str(json_data)
    response.ok = 200 <= status_code < 300
    return response


def assert_valid_email(email_data: dict):
    """Assert that email data has valid structure."""
    assert "id" in email_data
    assert "from" in email_data
    assert "subject" in email_data
    assert "timestamp" in email_data


def assert_valid_calendar_event(event_data: dict):
    """Assert that calendar event has valid structure."""
    assert "id" in event_data
    assert "title" in event_data or "summary" in event_data
    assert "start" in event_data
    assert "end" in event_data


# Make helper functions available to all tests
pytest.create_mock_response = create_mock_response
pytest.assert_valid_email = assert_valid_email
pytest.assert_valid_calendar_event = assert_valid_calendar_event
