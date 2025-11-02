"""
End-to-End tests for Voice Modes
Tests complete user workflows for all three voice modes
"""

import pytest
from fastapi.testclient import TestClient
import time


@pytest.mark.e2e
@pytest.mark.voice
class TestTextMode:
    """E2E tests for Text Mode"""

    def test_text_mode_complete_flow(self, client):
        """Test complete text mode workflow"""
        # Step 1: User types query
        query_data = {
            "query": "Show me my unread emails",
            "mode": "text"
        }

        # Step 2: Submit query
        response = client.post("/voice-agent/query", json=query_data)
        assert response.status_code == 200
        result = response.json()

        # Step 3: Verify text response
        assert "text" in result
        assert isinstance(result["text"], str)
        assert len(result["text"]) > 0

        # Step 4: No audio involved
        assert "drafts" in result  # May be empty
        assert "executed" in result  # May be empty

    def test_text_mode_email_query(self, client):
        """Test email query in text mode"""
        # Act
        response = client.post(
            "/voice-agent/query",
            json={"query": "What emails did I receive today?", "mode": "text"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "intent" in data
        assert data["intent"] in ["query_emails", "unknown"]

    def test_text_mode_calendar_query(self, client):
        """Test calendar query in text mode"""
        # Act
        response = client.post(
            "/voice-agent/query",
            json={"query": "What meetings do I have tomorrow?", "mode": "text"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "text" in data

    def test_text_mode_draft_generation(self, client):
        """Test draft generation in text mode"""
        # Act
        response = client.post(
            "/voice-agent/query",
            json={"query": "Draft a thank you reply to the latest email", "mode": "text"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "drafts" in data

    def test_text_mode_multiple_queries(self, client):
        """Test multiple sequential queries in text mode"""
        queries = [
            "Show my emails",
            "What's my calendar today?",
            "How many unread emails do I have?"
        ]

        for query in queries:
            response = client.post(
                "/voice-agent/query",
                json={"query": query, "mode": "text"}
            )
            assert response.status_code == 200
            assert "text" in response.json()


@pytest.mark.e2e
@pytest.mark.voice
class TestSemiVoiceMode:
    """E2E tests for Semi-Voice Mode"""

    def test_semi_voice_mode_complete_flow(self, client):
        """Test complete semi-voice mode workflow"""
        # Step 1: User types query
        query_data = {
            "query": "Read my inbox summary",
            "mode": "voice"  # Backend treats as voice mode
        }

        # Step 2: Submit query
        query_response = client.post("/voice-agent/query", json=query_data)
        assert query_response.status_code == 200
        query_result = query_response.json()

        # Step 3: Verify text response exists
        assert "text" in query_result
        response_text = query_result["text"]

        # Step 4: Request TTS for response (semi-voice specific)
        tts_response = client.post(
            "/voice-agent/tts",
            json={"text": response_text}
        )

        # Assert
        # TTS may fail without API key, but structure should be correct
        assert tts_response.status_code in [200, 500]
        if tts_response.status_code == 200:
            assert tts_response.headers["content-type"] == "audio/mpeg"

    def test_semi_voice_mode_with_tts(self, client):
        """Test semi-voice mode with TTS enabled"""
        # Step 1: Query
        response = client.post(
            "/voice-agent/query",
            json={"query": "Tell me about my calendar", "mode": "voice"}
        )
        assert response.status_code == 200

        # Step 2: Convert response to speech
        text = response.json().get("text", "")
        if text:
            tts_response = client.post("/voice-agent/tts", json={"text": text[:100]})
            # TTS may or may not work depending on API key
            assert tts_response.status_code in [200, 500]

    def test_semi_voice_mode_long_response(self, client):
        """Test semi-voice with longer response"""
        # Act
        response = client.post(
            "/voice-agent/query",
            json={"query": "Summarize all my emails from this week", "mode": "voice"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "text" in data

        # Try TTS with truncated text
        if data["text"]:
            truncated = data["text"][:500]  # Limit for testing
            tts_response = client.post("/voice-agent/tts", json={"text": truncated})
            assert tts_response.status_code in [200, 500]


@pytest.mark.e2e
@pytest.mark.voice
@pytest.mark.slow
class TestFullVoiceMode:
    """E2E tests for Full-Voice Mode"""

    def test_full_voice_mode_flow_simulated(self, client):
        """Test full-voice mode with simulated speech-to-text"""
        # Step 1: Simulate STT - transcript from speech
        transcript = "Show me my emails"

        # Step 2: Process query
        query_response = client.post(
            "/voice-agent/query",
            json={"query": transcript, "mode": "voice"}
        )
        assert query_response.status_code == 200
        query_data = query_response.json()

        # Step 3: Verify response
        assert "text" in query_data
        response_text = query_data["text"]

        # Step 4: Simulate TTS - convert to speech
        tts_response = client.post(
            "/voice-agent/tts",
            json={"text": response_text}
        )

        # Assert complete flow
        assert tts_response.status_code in [200, 500]

    def test_full_voice_mode_email_query(self, client):
        """Test email query in full-voice mode"""
        # Simulate: User speaks -> STT -> Query -> TTS

        # Step 1: STT result (simulated)
        transcript = "What unread emails do I have?"

        # Step 2: Process
        response = client.post(
            "/voice-agent/query",
            json={"query": transcript, "mode": "voice"}
        )

        # Assert
        assert response.status_code == 200
        assert "text" in response.json()

    def test_full_voice_mode_calendar_query(self, client):
        """Test calendar query in full-voice mode"""
        # Simulate voice input
        transcript = "Do I have any meetings today?"

        # Process
        response = client.post(
            "/voice-agent/query",
            json={"query": transcript, "mode": "voice"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "calendar_actions" in data

    def test_full_voice_mode_stt_endpoint(self, client):
        """Test STT endpoint (if available)"""
        # This tests the backend STT fallback
        response = client.post("/voice-agent/stt")

        # Should return 501 (not implemented) or handle audio
        assert response.status_code in [405, 501, 422]  # Method not fully implemented


@pytest.mark.e2e
@pytest.mark.voice
class TestModeIntegration:
    """Test integration between different modes"""

    def test_switch_between_modes(self, client):
        """Test switching between different voice modes"""
        # Text mode
        text_response = client.post(
            "/voice-agent/query",
            json={"query": "Show emails", "mode": "text"}
        )
        assert text_response.status_code == 200

        # Voice mode
        voice_response = client.post(
            "/voice-agent/query",
            json={"query": "Show emails", "mode": "voice"}
        )
        assert voice_response.status_code == 200

        # Both should work
        assert "text" in text_response.json()
        assert "text" in voice_response.json()

    def test_session_persistence(self, client):
        """Test session persistence across queries"""
        session_id = "test_session_123"

        # Query 1
        response1 = client.post(
            "/voice-agent/query",
            json={"query": "Show my emails", "mode": "text", "session_id": session_id}
        )
        assert response1.status_code == 200

        # Query 2 in same session
        response2 = client.post(
            "/voice-agent/query",
            json={"query": "What about calendar?", "mode": "text", "session_id": session_id}
        )
        assert response2.status_code == 200

    def test_user_context_handling(self, client):
        """Test handling of user context"""
        user_id = "test_user_456"

        response = client.post(
            "/voice-agent/query",
            json={"query": "Show my data", "mode": "text", "user_id": user_id}
        )

        assert response.status_code == 200


@pytest.mark.e2e
@pytest.mark.voice
@pytest.mark.performance
class TestVoiceModePerformance:
    """Performance tests for voice modes"""

    def test_text_mode_response_time(self, client):
        """Test text mode response time"""
        start = time.time()

        response = client.post(
            "/voice-agent/query",
            json={"query": "Show emails", "mode": "text"}
        )

        duration = time.time() - start

        assert response.status_code == 200
        assert duration < 5.0  # Should respond within 5 seconds

    def test_voice_mode_total_latency(self, client):
        """Test total latency for voice mode (query + TTS)"""
        start = time.time()

        # Query
        query_response = client.post(
            "/voice-agent/query",
            json={"query": "Quick test", "mode": "voice"}
        )
        assert query_response.status_code == 200

        # TTS
        text = query_response.json().get("text", "test")[:100]
        tts_response = client.post("/voice-agent/tts", json={"text": text})

        duration = time.time() - start

        # Total flow should complete reasonably fast
        assert duration < 15.0  # 15 seconds max for full flow

    def test_multiple_concurrent_voice_queries(self, client):
        """Test multiple concurrent voice queries"""
        import concurrent.futures

        def make_query(query_text):
            return client.post(
                "/voice-agent/query",
                json={"query": query_text, "mode": "voice"}
            )

        queries = [
            "Show emails",
            "Show calendar",
            "Count unread",
            "Show urgent"
        ]

        # Execute concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(make_query, q) for q in queries]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should succeed
        assert all(r.status_code == 200 for r in results)


@pytest.mark.e2e
@pytest.mark.voice
@pytest.mark.smoke
class TestCriticalPaths:
    """Smoke tests for critical user paths"""

    def test_basic_email_query_smoke(self, client):
        """Smoke test: Basic email query"""
        response = client.post(
            "/voice-agent/query",
            json={"query": "Show emails", "mode": "text"}
        )
        assert response.status_code == 200
        assert "text" in response.json()

    def test_basic_calendar_query_smoke(self, client):
        """Smoke test: Basic calendar query"""
        response = client.post(
            "/voice-agent/query",
            json={"query": "Show calendar", "mode": "text"}
        )
        assert response.status_code == 200
        assert "text" in response.json()

    def test_email_sending_smoke(self, client):
        """Smoke test: Email sending"""
        response = client.post(
            "/voice-agent/email/send",
            json={
                "to": ["test@example.com"],
                "subject": "Test",
                "body": "Test body"
            }
        )
        assert response.status_code in [200, 500]  # May fail without real Gmail

    def test_tts_smoke(self, client):
        """Smoke test: TTS generation"""
        response = client.post(
            "/voice-agent/tts",
            json={"text": "Hello"}
        )
        assert response.status_code in [200, 500]  # May fail without API key

    def test_get_emails_smoke(self, client):
        """Smoke test: Get emails"""
        response = client.get("/voice-agent/emails?max_results=5")
        assert response.status_code == 200
        assert "emails" in response.json()

    def test_get_calendar_smoke(self, client):
        """Smoke test: Get calendar"""
        response = client.get("/voice-agent/calendar/events?timeframe=today")
        assert response.status_code == 200
        assert "events" in response.json()
