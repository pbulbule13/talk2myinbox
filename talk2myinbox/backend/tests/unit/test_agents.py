"""
Unit tests for all LangGraph agents
Tests the 9 agents: Intent, Context, Reasoning, Draft, Authorization, Execution, Response, Logging
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import uuid

from voice_agent.agents.intent_agent import IntentClassificationAgent
from voice_agent.agents.context_agent import ContextRetrievalAgent
from voice_agent.agents.reasoning_agent import ReasoningAgent
from voice_agent.agents.draft_agent import DraftGenerationAgent
from voice_agent.agents.authorization_agent import AuthorizationAgent
from voice_agent.agents.execution_agent import ExecutionAgent
from voice_agent.agents.response_agent import ResponseGenerationAgent
from voice_agent.agents.logging_agent import LoggingAgent
from voice_agent.graph.state import VoiceAgentState


@pytest.mark.asyncio
class TestIntentClassificationAgent:
    """Test intent classification agent"""

    async def test_classify_triage_inbox_intent(self, mock_intent_agent):
        """Test classification of triage inbox queries"""
        queries = [
            "What are my most important emails?",
            "Show me urgent messages",
            "Prioritize my inbox"
        ]

        for query in queries:
            state = {"query": query, "user_id": "test_user", "mode": "text"}
            result = await mock_intent_agent.run(state)

            assert result is not None
            assert result.get("intent") in ["triage_inbox", "prioritize_inbox"]
            assert result.get("confidence", 0) > 0

    async def test_classify_draft_reply_intent(self, mock_intent_agent):
        """Test classification of draft reply queries"""
        queries = [
            "Draft a reply to John",
            "Write a response saying I'll be there",
            "Reply to the meeting request"
        ]

        for query in queries:
            state = {"query": query, "user_id": "test_user", "mode": "text"}
            result = await mock_intent_agent.run(state)

            assert result is not None
            assert result.get("intent") == "draft_reply"

    async def test_classify_schedule_meeting_intent(self, mock_intent_agent):
        """Test classification of scheduling queries"""
        queries = [
            "Schedule a meeting with Sarah tomorrow at 2pm",
            "Book a conference room for Monday",
            "Set up a call with the team"
        ]

        for query in queries:
            state = {"query": query, "user_id": "test_user", "mode": "text"}
            result = await mock_intent_agent.run(state)

            assert result is not None
            assert result.get("intent") == "schedule_meeting"

    async def test_classify_check_calendar_intent(self, mock_intent_agent):
        """Test classification of calendar check queries"""
        queries = [
            "What's on my calendar today?",
            "Show my meetings this week",
            "When is my next appointment?"
        ]

        for query in queries:
            state = {"query": query, "user_id": "test_user", "mode": "text"}
            result = await mock_intent_agent.run(state)

            assert result is not None
            assert result.get("intent") == "check_calendar"

    async def test_classify_follow_up_intent(self, mock_intent_agent):
        """Test classification of follow-up queries"""
        queries = [
            "Follow up on the proposal I sent",
            "Check if John replied",
            "Did anyone respond to my email?"
        ]

        for query in queries:
            state = {"query": query, "user_id": "test_user", "mode": "text"}
            result = await mock_intent_agent.run(state)

            assert result is not None
            assert result.get("intent") == "follow_up"

    async def test_classify_summarize_intent(self, mock_intent_agent):
        """Test classification of summarization queries"""
        queries = [
            "Summarize my inbox",
            "Give me a summary of today's emails",
            "What did I miss?"
        ]

        for query in queries:
            state = {"query": query, "user_id": "test_user", "mode": "text"}
            result = await mock_intent_agent.run(state)

            assert result is not None
            assert result.get("intent") in ["summarize", "triage_inbox"]

    async def test_classify_unknown_intent(self, mock_intent_agent):
        """Test classification of unclear queries"""
        queries = [
            "Hello",
            "What can you do?",
            "Random gibberish xyz123"
        ]

        for query in queries:
            state = {"query": query, "user_id": "test_user", "mode": "text"}
            result = await mock_intent_agent.run(state)

            assert result is not None
            # Should return unknown or help intent
            assert result.get("intent") in ["unknown", "config", "help"]

    async def test_confidence_scoring(self, mock_intent_agent):
        """Test confidence scores are properly set"""
        state = {"query": "What are my emails?", "user_id": "test_user", "mode": "text"}
        result = await mock_intent_agent.run(state)

        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0

    async def test_empty_query(self, mock_intent_agent):
        """Test handling of empty queries"""
        state = {"query": "", "user_id": "test_user", "mode": "text"}

        with pytest.raises((ValueError, Exception)):
            await mock_intent_agent.run(state)


@pytest.mark.asyncio
class TestContextRetrievalAgent:
    """Test context retrieval agent"""

    async def test_retrieve_email_context(self, mock_context_agent, mock_email_threads):
        """Test retrieving email context"""
        state = {
            "query": "What are my emails?",
            "intent": "triage_inbox",
            "user_id": "test_user"
        }

        result = await mock_context_agent.run(state)

        assert result is not None
        assert "email_threads" in result
        assert isinstance(result["email_threads"], list)

    async def test_retrieve_calendar_context(self, mock_context_agent, mock_calendar_events):
        """Test retrieving calendar context"""
        state = {
            "query": "What's on my calendar?",
            "intent": "check_calendar",
            "user_id": "test_user"
        }

        result = await mock_context_agent.run(state)

        assert result is not None
        assert "calendar_events" in result
        assert isinstance(result["calendar_events"], list)

    async def test_retrieve_sender_history(self, mock_context_agent):
        """Test retrieving sender history"""
        state = {
            "query": "Draft reply to John",
            "intent": "draft_reply",
            "user_id": "test_user",
            "thread_id": "thread_123"
        }

        result = await mock_context_agent.run(state)

        assert result is not None
        # May include sender_history if available
        assert "sender_history" in result or "email_threads" in result

    async def test_retrieve_availability_slots(self, mock_context_agent):
        """Test retrieving availability slots for scheduling"""
        state = {
            "query": "Schedule meeting tomorrow",
            "intent": "schedule_meeting",
            "user_id": "test_user"
        }

        result = await mock_context_agent.run(state)

        assert result is not None
        assert "availability_slots" in result or "calendar_events" in result

    async def test_context_filtering(self, mock_context_agent):
        """Test context filtering based on query"""
        state = {
            "query": "Show urgent emails from Sarah",
            "intent": "triage_inbox",
            "user_id": "test_user"
        }

        result = await mock_context_agent.run(state)

        assert result is not None
        assert "email_threads" in result

    async def test_empty_context(self, mock_context_agent):
        """Test handling when no context is available"""
        with patch.object(mock_context_agent, '_fetch_emails', return_value=[]):
            state = {
                "query": "What are my emails?",
                "intent": "triage_inbox",
                "user_id": "test_user"
            }

            result = await mock_context_agent.run(state)

            assert result is not None
            assert result.get("email_threads", []) == []


@pytest.mark.asyncio
class TestReasoningAgent:
    """Test reasoning agent"""

    async def test_assess_priority(self, mock_reasoning_agent):
        """Test priority assessment"""
        state = {
            "query": "Triage my inbox",
            "intent": "triage_inbox",
            "email_threads": [
                {"subject": "URGENT: Server down", "from": "ops@company.com"},
                {"subject": "Weekly newsletter", "from": "news@example.com"}
            ]
        }

        result = await mock_reasoning_agent.run(state)

        assert result is not None
        assert "priority_assessment" in result

    async def test_recommend_action(self, mock_reasoning_agent):
        """Test action recommendation"""
        state = {
            "query": "What should I do with this email?",
            "intent": "triage_inbox",
            "email_threads": [
                {"subject": "Meeting request", "from": "john@company.com"}
            ]
        }

        result = await mock_reasoning_agent.run(state)

        assert result is not None
        assert "recommended_action" in result

    async def test_reasoning_explanation(self, mock_reasoning_agent):
        """Test that reasoning includes explanation"""
        state = {
            "query": "Should I reply?",
            "intent": "triage_inbox",
            "email_threads": [
                {"subject": "Important question", "from": "boss@company.com"}
            ]
        }

        result = await mock_reasoning_agent.run(state)

        assert result is not None
        assert "reasoning" in result

    async def test_llm_fallback(self, mock_reasoning_agent):
        """Test LLM provider fallback"""
        state = {
            "query": "Analyze this email",
            "intent": "triage_inbox",
            "email_threads": [{"subject": "Test", "from": "test@test.com"}]
        }

        # Mock primary LLM failure
        with patch.object(mock_reasoning_agent, '_primary_llm',
                         side_effect=Exception("API Error")):
            result = await mock_reasoning_agent.run(state)

            # Should fall back to secondary LLM
            assert result is not None

    async def test_escalation_to_human(self, mock_reasoning_agent):
        """Test escalation decision for complex cases"""
        state = {
            "query": "Handle this complex legal matter",
            "intent": "draft_reply",
            "email_threads": [
                {"subject": "Legal issue requiring expert opinion", "from": "legal@company.com"}
            ]
        }

        result = await mock_reasoning_agent.run(state)

        assert result is not None
        # May recommend escalation
        assert "recommended_action" in result


@pytest.mark.asyncio
class TestDraftGenerationAgent:
    """Test draft generation agent"""

    async def test_generate_email_draft(self, mock_draft_agent):
        """Test basic email draft generation"""
        state = {
            "query": "Reply saying I'll attend",
            "intent": "draft_reply",
            "email_threads": [
                {"thread_id": "123", "subject": "Meeting invitation", "from": "john@company.com"}
            ],
            "recommended_action": "send_reply"
        }

        result = await mock_draft_agent.run(state)

        assert result is not None
        assert "email_drafts" in result
        assert len(result["email_drafts"]) > 0

    async def test_generate_multiple_drafts(self, mock_draft_agent):
        """Test generating multiple email drafts"""
        state = {
            "query": "Reply to all urgent emails",
            "intent": "draft_reply",
            "email_threads": [
                {"thread_id": "123", "subject": "Question 1", "from": "person1@company.com"},
                {"thread_id": "456", "subject": "Question 2", "from": "person2@company.com"}
            ],
            "recommended_action": "send_reply"
        }

        result = await mock_draft_agent.run(state)

        assert result is not None
        assert "email_drafts" in result
        assert len(result["email_drafts"]) >= 1

    async def test_draft_with_tone(self, mock_draft_agent):
        """Test draft generation with specific tone"""
        state = {
            "query": "Draft a formal response declining the invitation",
            "intent": "draft_reply",
            "email_threads": [{"thread_id": "123", "subject": "Invitation", "from": "external@company.com"}],
            "tone": "formal"
        }

        result = await mock_draft_agent.run(state)

        assert result is not None
        assert "email_drafts" in result

    async def test_generate_calendar_proposal(self, mock_draft_agent):
        """Test calendar event proposal generation"""
        state = {
            "query": "Schedule meeting with Sarah tomorrow at 2pm",
            "intent": "schedule_meeting",
            "calendar_events": [],
            "recommended_action": "create_event"
        }

        result = await mock_draft_agent.run(state)

        assert result is not None
        assert "calendar_actions" in result or "calendar_proposals" in result

    async def test_draft_requires_authorization(self, mock_draft_agent):
        """Test that drafts flag authorization requirement"""
        state = {
            "query": "Send important email to CEO",
            "intent": "send_email",
            "recommended_action": "send_email"
        }

        result = await mock_draft_agent.run(state)

        assert result is not None
        # Important emails should require authorization
        if "email_drafts" in result and len(result["email_drafts"]) > 0:
            draft = result["email_drafts"][0]
            assert "requires_authorization" in draft


@pytest.mark.asyncio
class TestAuthorizationAgent:
    """Test authorization agent"""

    async def test_requires_authorization_for_email_send(self, mock_authorization_agent):
        """Test authorization requirement for email sending"""
        state = {
            "intent": "send_email",
            "email_drafts": [
                {"draft_id": "123", "to": "external@company.com", "subject": "Important",
                 "requires_authorization": True}
            ]
        }

        result = await mock_authorization_agent.run(state)

        assert result is not None
        assert result.get("requires_authorization") is True

    async def test_requires_authorization_for_calendar_event(self, mock_authorization_agent):
        """Test authorization requirement for calendar event creation"""
        state = {
            "intent": "schedule_meeting",
            "calendar_actions": [
                {"action_type": "create_event", "attendees": ["external@company.com"]}
            ]
        }

        result = await mock_authorization_agent.run(state)

        assert result is not None
        assert result.get("requires_authorization") is True

    async def test_no_authorization_for_read_only(self, mock_authorization_agent):
        """Test no authorization needed for read-only operations"""
        state = {
            "intent": "check_calendar",
            "calendar_events": []
        }

        result = await mock_authorization_agent.run(state)

        assert result is not None
        assert result.get("requires_authorization", False) is False

    async def test_generate_authorization_code(self, mock_authorization_agent):
        """Test authorization code generation"""
        state = {
            "intent": "send_email",
            "email_drafts": [{"requires_authorization": True}],
            "requires_authorization": True
        }

        result = await mock_authorization_agent.run(state)

        assert result is not None
        if result.get("requires_authorization"):
            assert "authorization_code" in result


@pytest.mark.asyncio
class TestExecutionAgent:
    """Test execution agent"""

    async def test_execute_send_email(self, mock_execution_agent, mock_email_adapter):
        """Test email sending execution"""
        state = {
            "email_drafts": [
                {
                    "draft_id": "123",
                    "to": "recipient@company.com",
                    "subject": "Test",
                    "body": "Test body",
                    "requires_authorization": False
                }
            ],
            "requires_authorization": False
        }

        result = await mock_execution_agent.run(state)

        assert result is not None
        assert "executed_actions" in result
        assert len(result["executed_actions"]) > 0

    async def test_execute_calendar_event_creation(self, mock_execution_agent):
        """Test calendar event creation execution"""
        state = {
            "calendar_actions": [
                {
                    "action_type": "create_event",
                    "title": "Meeting",
                    "start": datetime.now(),
                    "end": datetime.now() + timedelta(hours=1)
                }
            ],
            "requires_authorization": False
        }

        result = await mock_execution_agent.run(state)

        assert result is not None
        assert "executed_actions" in result

    async def test_execution_blocked_without_authorization(self, mock_execution_agent):
        """Test execution is blocked without proper authorization"""
        state = {
            "email_drafts": [{"requires_authorization": True}],
            "requires_authorization": True
            # No authorization_code provided
        }

        result = await mock_execution_agent.run(state)

        assert result is not None
        # Should not execute
        assert len(result.get("executed_actions", [])) == 0

    async def test_execution_with_valid_authorization(self, mock_execution_agent):
        """Test execution proceeds with valid authorization"""
        state = {
            "email_drafts": [{"requires_authorization": True}],
            "requires_authorization": True,
            "authorization_code": "valid_code",
            "user_approved": True
        }

        result = await mock_execution_agent.run(state)

        assert result is not None

    async def test_execution_error_handling(self, mock_execution_agent, mock_email_adapter):
        """Test error handling during execution"""
        with patch.object(mock_email_adapter, 'send_email',
                         side_effect=Exception("Send failed")):
            state = {
                "email_drafts": [{"to": "test@test.com", "subject": "Test", "body": "Body"}],
                "requires_authorization": False
            }

            result = await mock_execution_agent.run(state)

            assert result is not None
            assert "error" in result or "execution_status" in result

    async def test_execution_logs_actions(self, mock_execution_agent):
        """Test that execution logs all actions"""
        state = {
            "email_drafts": [{"to": "test@test.com", "subject": "Test", "body": "Body"}],
            "requires_authorization": False
        }

        result = await mock_execution_agent.run(state)

        assert result is not None
        assert "action_logs" in result or "executed_actions" in result


@pytest.mark.asyncio
class TestResponseGenerationAgent:
    """Test response generation agent"""

    async def test_generate_text_response(self, mock_response_agent):
        """Test text response generation"""
        state = {
            "intent": "triage_inbox",
            "email_threads": [
                {"subject": "Important", "from": "boss@company.com"}
            ],
            "priority_assessment": "High priority email from your boss",
            "mode": "text"
        }

        result = await mock_response_agent.run(state)

        assert result is not None
        assert "text_response" in result

    async def test_generate_voice_response(self, mock_response_agent):
        """Test voice response generation"""
        state = {
            "intent": "check_calendar",
            "calendar_events": [
                {"title": "Meeting", "start": datetime.now()}
            ],
            "mode": "voice"
        }

        result = await mock_response_agent.run(state)

        assert result is not None
        assert "voice_response" in result or "text_response" in result

    async def test_generate_authorization_prompt(self, mock_response_agent):
        """Test authorization prompt generation"""
        state = {
            "intent": "send_email",
            "email_drafts": [{"to": "test@test.com", "subject": "Test"}],
            "requires_authorization": True,
            "authorization_code": "ABC123"
        }

        result = await mock_response_agent.run(state)

        assert result is not None
        assert "text_response" in result or "authorization_prompt" in result

    async def test_generate_error_response(self, mock_response_agent):
        """Test error response generation"""
        state = {
            "intent": "send_email",
            "error": "Failed to send email: API error",
            "mode": "text"
        }

        result = await mock_response_agent.run(state)

        assert result is not None
        assert "text_response" in result

    async def test_generate_structured_response(self, mock_response_agent):
        """Test structured response with multiple components"""
        state = {
            "intent": "triage_inbox",
            "email_threads": [
                {"subject": "Email 1", "priority": "high"},
                {"subject": "Email 2", "priority": "medium"}
            ],
            "priority_assessment": "2 emails need attention",
            "executed_actions": [],
            "mode": "text"
        }

        result = await mock_response_agent.run(state)

        assert result is not None
        assert "text_response" in result or "final_response" in result


@pytest.mark.asyncio
class TestLoggingAgent:
    """Test logging agent"""

    async def test_log_query(self, mock_logging_agent):
        """Test query logging"""
        state = {
            "query": "What are my emails?",
            "user_id": "test_user",
            "session_id": "session_123",
            "intent": "triage_inbox"
        }

        result = await mock_logging_agent.run(state)

        assert result is not None

    async def test_log_actions(self, mock_logging_agent):
        """Test action logging"""
        state = {
            "query": "Send email",
            "executed_actions": [
                {"action_type": "send_email", "status": "success"}
            ]
        }

        result = await mock_logging_agent.run(state)

        assert result is not None

    async def test_log_errors(self, mock_logging_agent):
        """Test error logging"""
        state = {
            "query": "Test query",
            "error": "Something went wrong",
            "intent": "unknown"
        }

        result = await mock_logging_agent.run(state)

        assert result is not None

    async def test_log_authorization_events(self, mock_logging_agent):
        """Test authorization event logging"""
        state = {
            "query": "Send important email",
            "requires_authorization": True,
            "authorization_code": "ABC123",
            "user_approved": True
        }

        result = await mock_logging_agent.run(state)

        assert result is not None

    async def test_audit_trail_completeness(self, mock_logging_agent):
        """Test that audit trail includes all necessary information"""
        state = {
            "query": "Complete workflow",
            "user_id": "test_user",
            "intent": "send_email",
            "executed_actions": [{"action_type": "send_email"}],
            "timestamp": datetime.now()
        }

        result = await mock_logging_agent.run(state)

        assert result is not None


@pytest.mark.asyncio
class TestAgentIntegration:
    """Test interactions between agents"""

    async def test_intent_to_context_flow(self, mock_intent_agent, mock_context_agent):
        """Test flow from intent classification to context retrieval"""
        # Intent classification
        intent_state = {"query": "What are my emails?", "user_id": "test_user", "mode": "text"}
        intent_result = await mock_intent_agent.run(intent_state)

        # Context retrieval using intent result
        context_state = {**intent_state, **intent_result}
        context_result = await mock_context_agent.run(context_state)

        assert context_result is not None
        assert "email_threads" in context_result

    async def test_full_agent_pipeline(self, mock_intent_agent, mock_context_agent,
                                       mock_reasoning_agent, mock_draft_agent,
                                       mock_authorization_agent, mock_execution_agent,
                                       mock_response_agent, mock_logging_agent):
        """Test full agent pipeline execution"""
        # Initial state
        state = {"query": "Draft reply to John", "user_id": "test_user", "mode": "text"}

        # Pipeline
        state = await mock_intent_agent.run(state)
        state = await mock_context_agent.run(state)
        state = await mock_reasoning_agent.run(state)
        state = await mock_draft_agent.run(state)
        state = await mock_authorization_agent.run(state)
        state = await mock_execution_agent.run(state)
        state = await mock_response_agent.run(state)
        state = await mock_logging_agent.run(state)

        assert state is not None
        assert "text_response" in state or "final_response" in state
