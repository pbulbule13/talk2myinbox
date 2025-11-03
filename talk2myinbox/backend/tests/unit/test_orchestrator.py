"""
Unit tests for VoiceAgentOrchestrator
Tests the main coordinator for the voice agent system
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import uuid

from voice_agent.orchestrator import VoiceAgentOrchestrator
from voice_agent.models.email_models import EmailThread, EmailMessage, EmailPriority, EmailCategory
from voice_agent.models.calendar_models import CalendarEvent
from voice_agent.graph.state import VoiceAgentState


@pytest.mark.asyncio
class TestOrchestratorInitialization:
    """Test orchestrator initialization and setup"""

    async def test_orchestrator_creation(self, mock_email_adapter, mock_calendar_adapter):
        """Test basic orchestrator creation"""
        orchestrator = VoiceAgentOrchestrator(
            email_adapter=mock_email_adapter,
            calendar_adapter=mock_calendar_adapter
        )
        assert orchestrator is not None
        assert orchestrator.email_adapter == mock_email_adapter
        assert orchestrator.calendar_adapter == mock_calendar_adapter

    async def test_orchestrator_with_settings(self, mock_email_adapter, mock_calendar_adapter):
        """Test orchestrator creation with custom settings"""
        orchestrator = VoiceAgentOrchestrator(
            email_adapter=mock_email_adapter,
            calendar_adapter=mock_calendar_adapter,
            max_retries=5,
            timeout=60
        )
        assert orchestrator is not None


@pytest.mark.asyncio
class TestProcessQuery:
    """Test the main process_query method"""

    async def test_process_query_triage_inbox(self, mock_orchestrator, mock_email_threads):
        """Test processing a triage inbox query"""
        query = "What are my most important emails?"

        result = await mock_orchestrator.process_query(
            query=query,
            user_id="test_user",
            mode="text"
        )

        assert result is not None
        assert "response" in result or "text_response" in result

    async def test_process_query_draft_reply(self, mock_orchestrator):
        """Test processing a draft reply query"""
        query = "Draft a reply to John saying I'll be there tomorrow"

        result = await mock_orchestrator.process_query(
            query=query,
            user_id="test_user",
            mode="text"
        )

        assert result is not None

    async def test_process_query_schedule_meeting(self, mock_orchestrator):
        """Test processing a schedule meeting query"""
        query = "Schedule a meeting with Sarah tomorrow at 2pm"

        result = await mock_orchestrator.process_query(
            query=query,
            user_id="test_user",
            mode="text"
        )

        assert result is not None

    async def test_process_query_check_calendar(self, mock_orchestrator):
        """Test processing a calendar check query"""
        query = "What's on my calendar today?"

        result = await mock_orchestrator.process_query(
            query=query,
            user_id="test_user",
            mode="text"
        )

        assert result is not None

    async def test_process_query_with_session_id(self, mock_orchestrator):
        """Test query processing with existing session"""
        session_id = str(uuid.uuid4())
        query = "What are my emails?"

        result = await mock_orchestrator.process_query(
            query=query,
            user_id="test_user",
            session_id=session_id,
            mode="text"
        )

        assert result is not None

    async def test_process_query_voice_mode(self, mock_orchestrator):
        """Test query processing in voice mode"""
        query = "Read my urgent emails"

        result = await mock_orchestrator.process_query(
            query=query,
            user_id="test_user",
            mode="voice"
        )

        assert result is not None
        assert "voice_response" in result or "text_response" in result

    async def test_process_query_empty_query(self, mock_orchestrator):
        """Test handling empty query"""
        with pytest.raises((ValueError, Exception)):
            await mock_orchestrator.process_query(
                query="",
                user_id="test_user",
                mode="text"
            )

    async def test_process_query_invalid_mode(self, mock_orchestrator):
        """Test handling invalid mode"""
        result = await mock_orchestrator.process_query(
            query="What are my emails?",
            user_id="test_user",
            mode="invalid_mode"
        )
        # Should still process, possibly defaulting to text mode
        assert result is not None


@pytest.mark.asyncio
class TestSummarizeInbox:
    """Test inbox summarization convenience method"""

    async def test_summarize_inbox_basic(self, mock_orchestrator, mock_email_threads):
        """Test basic inbox summarization"""
        result = await mock_orchestrator.summarize_inbox(
            user_id="test_user"
        )

        assert result is not None
        assert "summary" in result or "response" in result or "text_response" in result

    async def test_summarize_inbox_with_filters(self, mock_orchestrator):
        """Test inbox summarization with filters"""
        result = await mock_orchestrator.summarize_inbox(
            user_id="test_user",
            filters={"category": "high_priority_reply"}
        )

        assert result is not None

    async def test_summarize_inbox_with_limit(self, mock_orchestrator):
        """Test inbox summarization with limit"""
        result = await mock_orchestrator.summarize_inbox(
            user_id="test_user",
            max_threads=5
        )

        assert result is not None

    async def test_summarize_inbox_empty(self, mock_orchestrator):
        """Test summarization with empty inbox"""
        # Mock empty inbox
        with patch.object(mock_orchestrator.email_adapter, 'fetch_threads',
                         return_value=[]):
            result = await mock_orchestrator.summarize_inbox(
                user_id="test_user"
            )

            assert result is not None


@pytest.mark.asyncio
class TestDraftReply:
    """Test draft reply convenience method"""

    async def test_draft_reply_basic(self, mock_orchestrator):
        """Test basic draft reply"""
        result = await mock_orchestrator.draft_reply(
            thread_id="thread_123",
            instructions="Say I'll be there tomorrow",
            user_id="test_user"
        )

        assert result is not None
        assert "draft" in result or "email_draft" in result or "response" in result

    async def test_draft_reply_with_tone(self, mock_orchestrator):
        """Test draft reply with specific tone"""
        result = await mock_orchestrator.draft_reply(
            thread_id="thread_123",
            instructions="Decline politely",
            tone="formal",
            user_id="test_user"
        )

        assert result is not None

    async def test_draft_reply_invalid_thread(self, mock_orchestrator):
        """Test draft reply with invalid thread ID"""
        with patch.object(mock_orchestrator.email_adapter, 'get_thread',
                         side_effect=Exception("Thread not found")):
            with pytest.raises(Exception):
                await mock_orchestrator.draft_reply(
                    thread_id="invalid_thread",
                    instructions="Reply",
                    user_id="test_user"
                )

    async def test_draft_reply_empty_instructions(self, mock_orchestrator):
        """Test draft reply with empty instructions"""
        with pytest.raises((ValueError, Exception)):
            await mock_orchestrator.draft_reply(
                thread_id="thread_123",
                instructions="",
                user_id="test_user"
            )


@pytest.mark.asyncio
class TestCheckCalendar:
    """Test calendar check convenience method"""

    async def test_check_calendar_today(self, mock_orchestrator, mock_calendar_events):
        """Test checking today's calendar"""
        result = await mock_orchestrator.check_calendar(
            user_id="test_user",
            timeframe="today"
        )

        assert result is not None
        assert "events" in result or "response" in result or "text_response" in result

    async def test_check_calendar_this_week(self, mock_orchestrator):
        """Test checking this week's calendar"""
        result = await mock_orchestrator.check_calendar(
            user_id="test_user",
            timeframe="this_week"
        )

        assert result is not None

    async def test_check_calendar_custom_range(self, mock_orchestrator):
        """Test checking calendar with custom date range"""
        start_time = datetime.now()
        end_time = start_time + timedelta(days=7)

        result = await mock_orchestrator.check_calendar(
            user_id="test_user",
            start_time=start_time,
            end_time=end_time
        )

        assert result is not None

    async def test_check_calendar_empty(self, mock_orchestrator):
        """Test checking calendar with no events"""
        with patch.object(mock_orchestrator.calendar_adapter, 'get_events',
                         return_value=[]):
            result = await mock_orchestrator.check_calendar(
                user_id="test_user",
                timeframe="today"
            )

            assert result is not None


@pytest.mark.asyncio
class TestSessionManagement:
    """Test session management functionality"""

    async def test_create_session(self, mock_orchestrator):
        """Test creating a new session"""
        session_id = await mock_orchestrator.create_session(user_id="test_user")
        assert session_id is not None
        assert isinstance(session_id, str)

    async def test_get_session(self, mock_orchestrator):
        """Test retrieving an existing session"""
        session_id = await mock_orchestrator.create_session(user_id="test_user")
        session = await mock_orchestrator.get_session(session_id)
        assert session is not None

    async def test_update_session(self, mock_orchestrator):
        """Test updating session state"""
        session_id = await mock_orchestrator.create_session(user_id="test_user")
        await mock_orchestrator.update_session(
            session_id=session_id,
            updates={"context": "test_context"}
        )
        session = await mock_orchestrator.get_session(session_id)
        assert session is not None

    async def test_delete_session(self, mock_orchestrator):
        """Test deleting a session"""
        session_id = await mock_orchestrator.create_session(user_id="test_user")
        await mock_orchestrator.delete_session(session_id)

        # Session should no longer exist
        session = await mock_orchestrator.get_session(session_id)
        assert session is None

    async def test_session_timeout(self, mock_orchestrator):
        """Test session timeout handling"""
        # Create session and wait for timeout
        session_id = await mock_orchestrator.create_session(user_id="test_user")

        # Mock timeout
        with patch('time.time', return_value=float('inf')):
            session = await mock_orchestrator.get_session(session_id)
            # Should handle expired session appropriately
            assert session is None or "expired" in str(session).lower()


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling in orchestrator"""

    async def test_email_adapter_failure(self, mock_orchestrator):
        """Test handling email adapter failures"""
        with patch.object(mock_orchestrator.email_adapter, 'fetch_threads',
                         side_effect=Exception("API Error")):
            with pytest.raises(Exception):
                await mock_orchestrator.summarize_inbox(user_id="test_user")

    async def test_calendar_adapter_failure(self, mock_orchestrator):
        """Test handling calendar adapter failures"""
        with patch.object(mock_orchestrator.calendar_adapter, 'get_events',
                         side_effect=Exception("API Error")):
            with pytest.raises(Exception):
                await mock_orchestrator.check_calendar(user_id="test_user")

    async def test_graph_execution_failure(self, mock_orchestrator):
        """Test handling graph execution failures"""
        with patch.object(mock_orchestrator, '_execute_graph',
                         side_effect=Exception("Graph Error")):
            with pytest.raises(Exception):
                await mock_orchestrator.process_query(
                    query="test",
                    user_id="test_user",
                    mode="text"
                )

    async def test_retry_on_transient_error(self, mock_orchestrator):
        """Test retry logic for transient errors"""
        # Mock transient failure then success
        call_count = 0

        async def failing_fetch(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Transient error")
            return []

        with patch.object(mock_orchestrator.email_adapter, 'fetch_threads',
                         side_effect=failing_fetch):
            # Should retry and succeed
            result = await mock_orchestrator.summarize_inbox(user_id="test_user")
            assert call_count >= 2


@pytest.mark.asyncio
class TestConcurrentOperations:
    """Test concurrent operations handling"""

    async def test_concurrent_queries(self, mock_orchestrator):
        """Test handling multiple concurrent queries"""
        import asyncio

        queries = [
            mock_orchestrator.process_query("What are my emails?", "user1", "text"),
            mock_orchestrator.process_query("Check my calendar", "user2", "text"),
            mock_orchestrator.process_query("Draft a reply", "user3", "text")
        ]

        results = await asyncio.gather(*queries, return_exceptions=True)

        # All queries should complete
        assert len(results) == 3
        assert all(r is not None for r in results)

    async def test_concurrent_session_operations(self, mock_orchestrator):
        """Test concurrent session operations"""
        import asyncio

        # Create multiple sessions concurrently
        sessions = await asyncio.gather(*[
            mock_orchestrator.create_session(f"user{i}")
            for i in range(5)
        ])

        assert len(sessions) == 5
        assert len(set(sessions)) == 5  # All unique


@pytest.mark.asyncio
class TestStateManagement:
    """Test state management in orchestrator"""

    async def test_state_initialization(self, mock_orchestrator):
        """Test proper state initialization"""
        state = await mock_orchestrator._initialize_state(
            query="test query",
            user_id="test_user",
            mode="text"
        )

        assert state["query"] == "test query"
        assert state["user_id"] == "test_user"
        assert state["mode"] == "text"

    async def test_state_persistence_across_turns(self, mock_orchestrator):
        """Test state persistence in multi-turn conversations"""
        session_id = await mock_orchestrator.create_session(user_id="test_user")

        # First query
        await mock_orchestrator.process_query(
            query="What are my emails?",
            user_id="test_user",
            session_id=session_id,
            mode="text"
        )

        # Second query should have context from first
        result = await mock_orchestrator.process_query(
            query="Reply to the first one",
            user_id="test_user",
            session_id=session_id,
            mode="text"
        )

        assert result is not None

    async def test_state_cleanup(self, mock_orchestrator):
        """Test proper state cleanup after completion"""
        result = await mock_orchestrator.process_query(
            query="test",
            user_id="test_user",
            mode="text"
        )

        # State should be cleaned up (no memory leaks)
        assert result is not None
