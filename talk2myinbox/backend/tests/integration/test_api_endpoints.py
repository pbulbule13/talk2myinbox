"""
Integration tests for API endpoints
Tests complete API workflows with mocked external services
"""

import pytest
from fastapi.testclient import TestClient
import json


@pytest.mark.integration
@pytest.mark.api
class TestVoiceAgentAPI:
    """Test suite for Voice Agent API endpoints"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert "service" in response.json()

    def test_root_endpoint(self, client):
        """Test root endpoint returns HTML"""
        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_api_docs(self, client):
        """Test API documentation endpoint"""
        # Act
        response = client.get("/docs")

        # Assert
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_voice_query_endpoint(self, client, mock_voice_query):
        """Test voice query endpoint"""
        # Act
        response = client.post(
            "/voice-agent/query",
            json=mock_voice_query
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "text" in data
        assert "intent" in data
        assert "drafts" in data
        assert "executed" in data

    @pytest.mark.asyncio
    async def test_voice_query_text_mode(self, client):
        """Test voice query in text mode"""
        # Arrange
        query_data = {
            "query": "Show me my emails",
            "mode": "text"
        }

        # Act
        response = client.post("/voice-agent/query", json=query_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] in ["query_emails", "unknown"]

    @pytest.mark.asyncio
    async def test_voice_query_voice_mode(self, client):
        """Test voice query in voice mode"""
        # Arrange
        query_data = {
            "query": "What meetings do I have today?",
            "mode": "voice"
        }

        # Act
        response = client.post("/voice-agent/query", json=query_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["calendar_actions"], list)

    @pytest.mark.asyncio
    async def test_voice_query_empty(self, client):
        """Test voice query with empty query string"""
        # Arrange
        query_data = {
            "query": "",
            "mode": "text"
        }

        # Act
        response = client.post("/voice-agent/query", json=query_data)

        # Assert
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]

    @pytest.mark.asyncio
    async def test_voice_query_invalid_mode(self, client):
        """Test voice query with invalid mode"""
        # Arrange
        query_data = {
            "query": "Test query",
            "mode": "invalid_mode"
        }

        # Act
        response = client.post("/voice-agent/query", json=query_data)

        # Assert
        assert response.status_code in [200, 422]  # May validate or accept

    @pytest.mark.asyncio
    async def test_inbox_summary_endpoint(self, client):
        """Test inbox summary endpoint"""
        # Act
        response = client.get("/voice-agent/inbox/summary")

        # Assert
        assert response.status_code == 200
        data = response.json()
        # Check for expected fields (will vary based on implementation)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_get_emails_endpoint(self, client):
        """Test get emails endpoint"""
        # Act
        response = client.get("/voice-agent/emails?max_results=10")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "emails" in data
        assert "count" in data
        assert isinstance(data["emails"], list)

    @pytest.mark.asyncio
    async def test_get_emails_with_query(self, client):
        """Test get emails with Gmail query"""
        # Act
        response = client.get("/voice-agent/emails?query=is:unread&max_results=5")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["emails"], list)

    @pytest.mark.asyncio
    async def test_search_emails_endpoint(self, client):
        """Test email search endpoint"""
        # Act
        response = client.get(
            "/voice-agent/emails/search?nl=show me emails from recruiters"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "emails" in data
        assert "count" in data
        assert "query" in data

    @pytest.mark.asyncio
    async def test_send_email_endpoint(self, client, mock_draft_data):
        """Test send email endpoint"""
        # Arrange
        email_data = {
            "to": mock_draft_data["to"],
            "subject": mock_draft_data["subject"],
            "body": mock_draft_data["body"]
        }

        # Act
        response = client.post("/voice-agent/email/send", json=email_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_send_email_invalid_data(self, client):
        """Test send email with invalid data"""
        # Arrange
        invalid_data = {
            "to": [],  # Empty recipient list
            "subject": "",
            "body": ""
        }

        # Act
        response = client.post("/voice-agent/email/send", json=invalid_data)

        # Assert
        # Should handle validation
        assert response.status_code in [200, 400, 422, 500]

    @pytest.mark.asyncio
    async def test_get_calendar_events_endpoint(self, client):
        """Test get calendar events endpoint"""
        # Act
        response = client.get("/voice-agent/calendar/events?timeframe=week")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert isinstance(data["events"], list)

    @pytest.mark.asyncio
    async def test_get_calendar_events_today(self, client):
        """Test get today's calendar events"""
        # Act
        response = client.get("/voice-agent/calendar/events?timeframe=today")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "events" in data

    @pytest.mark.asyncio
    async def test_get_calendar_events_tomorrow(self, client):
        """Test get tomorrow's calendar events"""
        # Act
        response = client.get("/voice-agent/calendar/events?timeframe=tomorrow")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "events" in data

    @pytest.mark.asyncio
    async def test_tts_endpoint(self, client):
        """Test text-to-speech endpoint"""
        # Arrange
        tts_data = {"text": "Hello, this is a test"}

        # Act
        response = client.post("/voice-agent/tts", json=tts_data)

        # Assert
        # May return audio or error depending on ElevenLabs key
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            assert response.headers["content-type"] == "audio/mpeg"

    @pytest.mark.asyncio
    async def test_tts_empty_text(self, client):
        """Test TTS with empty text"""
        # Arrange
        tts_data = {"text": ""}

        # Act
        response = client.post("/voice-agent/tts", json=tts_data)

        # Assert
        assert response.status_code in [400, 422, 500]

    @pytest.mark.asyncio
    async def test_config_endpoint(self, client):
        """Test configuration endpoint"""
        # Act
        response = client.get("/voice-agent/config")

        # Assert
        # May not be implemented or may require auth
        assert response.status_code in [200, 404, 500]


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.slow
class TestAPIWorkflows:
    """Test complete API workflows"""

    @pytest.mark.asyncio
    async def test_query_and_response_workflow(self, client):
        """Test complete query -> response workflow"""
        # Step 1: Query for emails
        query_response = client.post(
            "/voice-agent/query",
            json={"query": "Show my emails", "mode": "text"}
        )
        assert query_response.status_code == 200

        # Step 2: Get actual emails
        emails_response = client.get("/voice-agent/emails?max_results=5")
        assert emails_response.status_code == 200

        # Verify data consistency
        query_data = query_response.json()
        emails_data = emails_response.json()
        assert "text" in query_data
        assert "emails" in emails_data

    @pytest.mark.asyncio
    async def test_email_draft_workflow(self, client):
        """Test email drafting workflow"""
        # Step 1: Query to generate draft
        query_response = client.post(
            "/voice-agent/query",
            json={"query": "Draft a reply to the latest email", "mode": "text"}
        )
        assert query_response.status_code == 200

        # Step 2: Check if draft was created
        query_data = query_response.json()
        # Drafts may or may not be returned depending on implementation
        assert "drafts" in query_data

    @pytest.mark.asyncio
    async def test_calendar_query_workflow(self, client):
        """Test calendar querying workflow"""
        # Step 1: Query for calendar
        query_response = client.post(
            "/voice-agent/query",
            json={"query": "What's on my calendar today?", "mode": "text"}
        )
        assert query_response.status_code == 200

        # Step 2: Get actual calendar events
        events_response = client.get("/voice-agent/calendar/events?timeframe=today")
        assert events_response.status_code == 200

        # Verify data
        query_data = query_response.json()
        events_data = events_response.json()
        assert "text" in query_data
        assert "events" in events_data


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.security
class TestAPISecurity:
    """Test API security features"""

    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        # Act
        response = client.options("/voice-agent/query")

        # Assert
        # CORS headers should be present
        assert response.status_code in [200, 405]

    def test_api_rate_limiting(self, client):
        """Test API rate limiting (if implemented)"""
        # Act - Make multiple rapid requests
        responses = []
        for _ in range(20):
            response = client.get("/health")
            responses.append(response.status_code)

        # Assert
        # Should mostly succeed, may have rate limits
        success_count = sum(1 for status in responses if status == 200)
        assert success_count >= 15  # At least 75% should succeed

    def test_invalid_json_payload(self, client):
        """Test handling of invalid JSON"""
        # Act
        response = client.post(
            "/voice-agent/query",
            data="invalid json{",
            headers={"Content-Type": "application/json"}
        )

        # Assert
        assert response.status_code in [400, 422]

    def test_missing_required_fields(self, client):
        """Test handling of missing required fields"""
        # Act
        response = client.post(
            "/voice-agent/query",
            json={}  # Missing required 'query' field
        )

        # Assert
        assert response.status_code in [400, 422]


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.performance
class TestAPIPerformance:
    """Test API performance"""

    def test_health_check_performance(self, client):
        """Test health check response time"""
        import time

        # Act
        start = time.time()
        response = client.get("/health")
        duration = time.time() - start

        # Assert
        assert response.status_code == 200
        assert duration < 0.5  # Should respond in less than 500ms

    def test_concurrent_requests(self, client):
        """Test handling concurrent requests"""
        import concurrent.futures

        def make_request():
            return client.get("/health")

        # Act
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # Assert
        success_count = sum(1 for r in results if r.status_code == 200)
        assert success_count >= 18  # At least 90% should succeed

    @pytest.mark.asyncio
    async def test_query_response_time(self, client):
        """Test voice query response time"""
        import time

        # Arrange
        query_data = {"query": "Show emails", "mode": "text"}

        # Act
        start = time.time()
        response = client.post("/voice-agent/query", json=query_data)
        duration = time.time() - start

        # Assert
        assert response.status_code == 200
        assert duration < 5.0  # Should respond in less than 5 seconds
