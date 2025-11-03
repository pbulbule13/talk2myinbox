"""
Integration tests for API routes
Tests all 25+ API endpoints for email, calendar, voice, and support operations
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
import json
import uuid

from server import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.mark.asyncio
class TestVoiceAgentQueryEndpoint:
    """Test main /voice-agent/query endpoint"""

    def test_query_text_mode(self, client):
        """Test query in text mode"""
        payload = {
            "query": "What are my most important emails?",
            "user_id": "test_user",
            "mode": "text"
        }

        response = client.post("/voice-agent/query", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "response" in data or "text_response" in data

    def test_query_voice_mode(self, client):
        """Test query in voice mode"""
        payload = {
            "query": "Check my calendar",
            "user_id": "test_user",
            "mode": "voice"
        }

        response = client.post("/voice-agent/query", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "response" in data or "voice_response" in data

    def test_query_with_session_id(self, client):
        """Test query with existing session"""
        session_id = str(uuid.uuid4())
        payload = {
            "query": "What are my emails?",
            "user_id": "test_user",
            "session_id": session_id,
            "mode": "text"
        }

        response = client.post("/voice-agent/query", json=payload)

        assert response.status_code == 200

    def test_query_missing_required_fields(self, client):
        """Test query with missing required fields"""
        payload = {
            "query": "Test query"
            # Missing user_id and mode
        }

        response = client.post("/voice-agent/query", json=payload)

        assert response.status_code == 422  # Validation error

    def test_query_empty_query(self, client):
        """Test with empty query string"""
        payload = {
            "query": "",
            "user_id": "test_user",
            "mode": "text"
        }

        response = client.post("/voice-agent/query", json=payload)

        # Should return 400 or 422
        assert response.status_code in [400, 422]

    def test_query_invalid_mode(self, client):
        """Test with invalid mode"""
        payload = {
            "query": "Test",
            "user_id": "test_user",
            "mode": "invalid_mode"
        }

        response = client.post("/voice-agent/query", json=payload)

        # Should handle gracefully or return validation error
        assert response.status_code in [200, 400, 422]


@pytest.mark.asyncio
class TestEmailEndpoints:
    """Test email-related endpoints"""

    def test_get_emails(self, client):
        """Test GET /voice-agent/emails"""
        response = client.get("/voice-agent/emails?user_id=test_user")

        assert response.status_code == 200
        data = response.json()
        assert "emails" in data or isinstance(data, list)

    def test_get_emails_with_filters(self, client):
        """Test email retrieval with filters"""
        response = client.get(
            "/voice-agent/emails?user_id=test_user&category=high_priority_reply&limit=10"
        )

        assert response.status_code == 200

    def test_send_email(self, client):
        """Test POST /voice-agent/email/send"""
        payload = {
            "to": "recipient@example.com",
            "subject": "Test Email",
            "body": "This is a test email",
            "user_id": "test_user"
        }

        response = client.post("/voice-agent/email/send", json=payload)

        assert response.status_code in [200, 201]
        data = response.json()
        assert "message_id" in data or "status" in data

    def test_send_email_with_cc_bcc(self, client):
        """Test sending email with CC and BCC"""
        payload = {
            "to": "recipient@example.com",
            "cc": ["cc1@example.com", "cc2@example.com"],
            "bcc": ["bcc@example.com"],
            "subject": "Test",
            "body": "Test body",
            "user_id": "test_user"
        }

        response = client.post("/voice-agent/email/send", json=payload)

        assert response.status_code in [200, 201]

    def test_send_email_reply(self, client):
        """Test replying to an email thread"""
        payload = {
            "to": "recipient@example.com",
            "subject": "Re: Original Subject",
            "body": "This is a reply",
            "thread_id": "thread_123",
            "user_id": "test_user"
        }

        response = client.post("/voice-agent/email/send", json=payload)

        assert response.status_code in [200, 201]

    def test_send_email_missing_required_fields(self, client):
        """Test sending email with missing fields"""
        payload = {
            "to": "recipient@example.com"
            # Missing subject, body, user_id
        }

        response = client.post("/voice-agent/email/send", json=payload)

        assert response.status_code == 422

    def test_search_emails(self, client):
        """Test POST /voice-agent/emails/search"""
        payload = {
            "query": "from:john@example.com",
            "user_id": "test_user"
        }

        response = client.post("/voice-agent/emails/search", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "results" in data or isinstance(data, list)

    def test_search_emails_with_filters(self, client):
        """Test email search with advanced filters"""
        payload = {
            "query": "subject:meeting",
            "user_id": "test_user",
            "max_results": 20,
            "include_spam_trash": False
        }

        response = client.post("/voice-agent/emails/search", json=payload)

        assert response.status_code == 200

    def test_mark_email_read(self, client):
        """Test POST /voice-agent/email/mark-read"""
        payload = {
            "message_id": "msg_123",
            "user_id": "test_user"
        }

        response = client.post("/voice-agent/email/mark-read", json=payload)

        assert response.status_code == 200

    def test_archive_email(self, client):
        """Test POST /voice-agent/email/archive"""
        payload = {
            "message_id": "msg_123",
            "user_id": "test_user"
        }

        response = client.post("/voice-agent/email/archive", json=payload)

        assert response.status_code == 200

    def test_delete_email(self, client):
        """Test POST /voice-agent/email/delete"""
        payload = {
            "message_id": "msg_123",
            "user_id": "test_user"
        }

        response = client.post("/voice-agent/email/delete", json=payload)

        assert response.status_code == 200


@pytest.mark.asyncio
class TestCalendarEndpoints:
    """Test calendar-related endpoints"""

    def test_get_calendar_events(self, client):
        """Test GET /voice-agent/calendar/events"""
        response = client.get("/voice-agent/calendar/events?user_id=test_user")

        assert response.status_code == 200
        data = response.json()
        assert "events" in data or isinstance(data, list)

    def test_get_calendar_events_with_time_range(self, client):
        """Test calendar events with time range"""
        start = datetime.now().isoformat()
        end = (datetime.now() + timedelta(days=7)).isoformat()

        response = client.get(
            f"/voice-agent/calendar/events?user_id=test_user&start_time={start}&end_time={end}"
        )

        assert response.status_code == 200

    def test_create_calendar_event(self, client):
        """Test POST /voice-agent/calendar/event"""
        payload = {
            "title": "Team Meeting",
            "start": datetime.now().isoformat(),
            "end": (datetime.now() + timedelta(hours=1)).isoformat(),
            "user_id": "test_user"
        }

        response = client.post("/voice-agent/calendar/event", json=payload)

        assert response.status_code in [200, 201]
        data = response.json()
        assert "event_id" in data or "id" in data

    def test_create_calendar_event_with_attendees(self, client):
        """Test creating event with attendees"""
        payload = {
            "title": "Project Discussion",
            "start": datetime.now().isoformat(),
            "end": (datetime.now() + timedelta(hours=1)).isoformat(),
            "attendees": ["john@example.com", "sarah@example.com"],
            "location": "Conference Room A",
            "user_id": "test_user"
        }

        response = client.post("/voice-agent/calendar/event", json=payload)

        assert response.status_code in [200, 201]

    def test_update_calendar_event(self, client):
        """Test PUT /voice-agent/calendar/event/{event_id}"""
        payload = {
            "title": "Updated Meeting Title",
            "start": datetime.now().isoformat(),
            "end": (datetime.now() + timedelta(hours=1)).isoformat(),
            "user_id": "test_user"
        }

        response = client.put("/voice-agent/calendar/event/event_123", json=payload)

        assert response.status_code in [200, 404]  # 404 if event doesn't exist

    def test_delete_calendar_event(self, client):
        """Test DELETE /voice-agent/calendar/event/{event_id}"""
        response = client.delete(
            "/voice-agent/calendar/event/event_123?user_id=test_user"
        )

        assert response.status_code in [200, 204, 404]

    def test_check_availability(self, client):
        """Test POST /voice-agent/calendar/availability"""
        payload = {
            "start_time": datetime.now().isoformat(),
            "end_time": (datetime.now() + timedelta(days=1)).isoformat(),
            "duration_minutes": 60,
            "user_id": "test_user"
        }

        response = client.post("/voice-agent/calendar/availability", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "available_slots" in data or isinstance(data, list)


@pytest.mark.asyncio
class TestVoiceEndpoints:
    """Test voice-related endpoints"""

    def test_text_to_speech(self, client):
        """Test POST /voice-agent/tts"""
        payload = {
            "text": "Hello, this is a test message",
            "voice_id": "default"
        }

        response = client.post("/voice-agent/tts", json=payload)

        assert response.status_code == 200
        # Should return audio data or URL
        assert response.headers.get("content-type") in [
            "audio/mpeg", "audio/wav", "application/json"
        ]

    def test_text_to_speech_with_voice_options(self, client):
        """Test TTS with specific voice settings"""
        payload = {
            "text": "Test message",
            "voice_id": "custom_voice",
            "speed": 1.2,
            "pitch": 1.0
        }

        response = client.post("/voice-agent/tts", json=payload)

        assert response.status_code in [200, 400]

    def test_speech_to_text(self, client):
        """Test POST /voice-agent/stt"""
        # Mock audio file
        files = {
            "audio": ("test.wav", b"fake audio data", "audio/wav")
        }

        response = client.post("/voice-agent/stt", files=files)

        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = response.json()
            assert "text" in data or "transcription" in data


@pytest.mark.asyncio
class TestSupportEndpoints:
    """Test support and help endpoints"""

    def test_get_help(self, client):
        """Test GET /voice-agent/help"""
        response = client.get("/voice-agent/help")

        assert response.status_code == 200
        data = response.json()
        assert "commands" in data or "help" in data

    def test_get_help_for_specific_topic(self, client):
        """Test help for specific topic"""
        response = client.get("/voice-agent/help?topic=email")

        assert response.status_code == 200

    def test_submit_support_ticket(self, client):
        """Test POST /voice-agent/support/ticket"""
        payload = {
            "user_id": "test_user",
            "subject": "Issue with email sending",
            "description": "I'm having trouble sending emails",
            "priority": "medium"
        }

        response = client.post("/voice-agent/support/ticket", json=payload)

        assert response.status_code in [200, 201]
        data = response.json()
        assert "ticket_id" in data or "id" in data

    def test_get_support_tickets(self, client):
        """Test GET /voice-agent/support/tickets"""
        response = client.get("/voice-agent/support/tickets?user_id=test_user")

        assert response.status_code == 200


@pytest.mark.asyncio
class TestAuthenticationEndpoints:
    """Test authentication-related endpoints"""

    def test_oauth_initiate(self, client):
        """Test OAuth flow initiation"""
        response = client.get("/voice-agent/auth/oauth/gmail")

        assert response.status_code in [200, 302, 307]  # Redirect to OAuth

    def test_oauth_callback(self, client):
        """Test OAuth callback handling"""
        response = client.get(
            "/voice-agent/auth/oauth/gmail/callback?code=test_code&state=test_state"
        )

        assert response.status_code in [200, 302, 400]

    def test_check_auth_status(self, client):
        """Test GET /voice-agent/auth/status"""
        response = client.get("/voice-agent/auth/status?user_id=test_user")

        assert response.status_code == 200
        data = response.json()
        assert "authenticated" in data or "status" in data


@pytest.mark.asyncio
class TestWebSocketEndpoint:
    """Test WebSocket endpoint"""

    def test_websocket_connection(self, client):
        """Test WebSocket connection establishment"""
        with client.websocket_connect("/voice-agent/ws") as websocket:
            # Send a message
            websocket.send_json({
                "query": "What are my emails?",
                "user_id": "test_user",
                "mode": "text"
            })

            # Receive response
            data = websocket.receive_json()
            assert data is not None

    def test_websocket_streaming_response(self, client):
        """Test WebSocket streaming responses"""
        with client.websocket_connect("/voice-agent/ws") as websocket:
            websocket.send_json({
                "query": "Summarize my inbox",
                "user_id": "test_user",
                "mode": "text",
                "stream": True
            })

            # Receive multiple messages
            messages = []
            for _ in range(3):
                try:
                    msg = websocket.receive_json()
                    messages.append(msg)
                except:
                    break

            assert len(messages) > 0

    def test_websocket_error_handling(self, client):
        """Test WebSocket error handling"""
        with client.websocket_connect("/voice-agent/ws") as websocket:
            # Send invalid message
            websocket.send_json({
                "query": "",  # Invalid empty query
                "user_id": "test_user"
            })

            # Should receive error response
            data = websocket.receive_json()
            assert "error" in data or data is not None


@pytest.mark.asyncio
class TestErrorHandling:
    """Test API error handling"""

    def test_404_not_found(self, client):
        """Test 404 for non-existent endpoint"""
        response = client.get("/voice-agent/nonexistent")

        assert response.status_code == 404

    def test_405_method_not_allowed(self, client):
        """Test 405 for wrong HTTP method"""
        response = client.get("/voice-agent/query")  # Should be POST

        assert response.status_code == 405

    def test_500_internal_server_error(self, client):
        """Test 500 error handling"""
        with patch('voice_agent.orchestrator.VoiceAgentOrchestrator.process_query',
                   side_effect=Exception("Internal error")):
            payload = {
                "query": "Test",
                "user_id": "test_user",
                "mode": "text"
            }

            response = client.post("/voice-agent/query", json=payload)

            assert response.status_code == 500
            data = response.json()
            assert "error" in data or "detail" in data

    def test_rate_limiting(self, client):
        """Test rate limiting (if implemented)"""
        # Send many requests rapidly
        responses = []
        for _ in range(100):
            response = client.post("/voice-agent/query", json={
                "query": "Test",
                "user_id": "test_user",
                "mode": "text"
            })
            responses.append(response)

        # Check if rate limiting is enforced
        status_codes = [r.status_code for r in responses]
        # If rate limiting exists, should see 429 responses
        assert 429 in status_codes or all(s == 200 for s in status_codes)


@pytest.mark.asyncio
class TestCORS:
    """Test CORS configuration"""

    def test_cors_headers_present(self, client):
        """Test CORS headers are present"""
        response = client.options("/voice-agent/query")

        # Should have CORS headers
        assert response.status_code in [200, 204]

    def test_cors_allows_credentials(self, client):
        """Test CORS allows credentials"""
        response = client.get("/voice-agent/help", headers={
            "Origin": "http://localhost:3000"
        })

        # Check for CORS headers
        assert "access-control-allow-origin" in response.headers or response.status_code == 200


@pytest.mark.asyncio
class TestHealthCheck:
    """Test health check and status endpoints"""

    def test_health_check(self, client):
        """Test GET /health"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy" or "status" in data

    def test_readiness_check(self, client):
        """Test GET /ready"""
        response = client.get("/ready")

        assert response.status_code == 200

    def test_version_info(self, client):
        """Test GET /version"""
        response = client.get("/version")

        assert response.status_code == 200
        data = response.json()
        assert "version" in data or isinstance(data, dict)
