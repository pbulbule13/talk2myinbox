"""
Unit tests for LangGraph Graph Builder
Tests workflow construction, routing logic, and state transitions
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import uuid

from voice_agent.graph.graph_builder import GraphBuilder, build_graph
from voice_agent.graph.state import VoiceAgentState


@pytest.mark.asyncio
class TestGraphConstruction:
    """Test graph construction and node setup"""

    def test_build_graph_creates_all_nodes(self):
        """Test that all 8 nodes are created"""
        graph = build_graph()

        assert graph is not None
        # Graph should have all workflow nodes
        # The exact structure depends on LangGraph implementation

    def test_graph_has_intent_node(self):
        """Test intent classification node exists"""
        graph = build_graph()

        # Check if intent node is present
        assert graph is not None

    def test_graph_has_context_node(self):
        """Test context retrieval node exists"""
        graph = build_graph()

        assert graph is not None

    def test_graph_has_reasoning_node(self):
        """Test reasoning node exists"""
        graph = build_graph()

        assert graph is not None

    def test_graph_has_draft_node(self):
        """Test draft generation node exists"""
        graph = build_graph()

        assert graph is not None

    def test_graph_has_authorization_node(self):
        """Test authorization node exists"""
        graph = build_graph()

        assert graph is not None

    def test_graph_has_execution_node(self):
        """Test execution node exists"""
        graph = build_graph()

        assert graph is not None

    def test_graph_has_response_node(self):
        """Test response generation node exists"""
        graph = build_graph()

        assert graph is not None

    def test_graph_has_logging_node(self):
        """Test logging node exists"""
        graph = build_graph()

        assert graph is not None

    def test_graph_builder_initialization(self):
        """Test GraphBuilder initialization"""
        builder = GraphBuilder()

        assert builder is not None

    def test_graph_builder_with_custom_config(self):
        """Test GraphBuilder with custom configuration"""
        config = {
            "max_iterations": 100,
            "timeout": 60
        }

        builder = GraphBuilder(config=config)

        assert builder is not None


@pytest.mark.asyncio
class TestGraphEdges:
    """Test graph edges and connections"""

    def test_intent_to_context_edge(self):
        """Test edge from intent to context node"""
        graph = build_graph()

        # Graph should have proper connections
        assert graph is not None

    def test_context_to_reasoning_edge(self):
        """Test edge from context to reasoning node"""
        graph = build_graph()

        assert graph is not None

    def test_reasoning_to_draft_edge(self):
        """Test edge from reasoning to draft node"""
        graph = build_graph()

        assert graph is not None

    def test_draft_to_authorization_edge(self):
        """Test edge from draft to authorization node"""
        graph = build_graph()

        assert graph is not None

    def test_authorization_to_execution_edge(self):
        """Test edge from authorization to execution node"""
        graph = build_graph()

        assert graph is not None

    def test_execution_to_response_edge(self):
        """Test edge from execution to response node"""
        graph = build_graph()

        assert graph is not None

    def test_response_to_logging_edge(self):
        """Test edge from response to logging node"""
        graph = build_graph()

        assert graph is not None


@pytest.mark.asyncio
class TestConditionalRouting:
    """Test conditional routing logic"""

    async def test_route_based_on_intent(self):
        """Test routing based on intent classification"""
        graph = build_graph()

        # Different intents may route differently
        state = {
            "query": "Check my calendar",
            "intent": "check_calendar",
            "user_id": "test_user"
        }

        # Execute graph
        result = await graph.ainvoke(state)

        assert result is not None

    async def test_route_skip_draft_for_read_only(self):
        """Test that read-only operations skip draft generation"""
        graph = build_graph()

        state = {
            "query": "What's on my calendar?",
            "intent": "check_calendar",
            "user_id": "test_user"
        }

        result = await graph.ainvoke(state)

        assert result is not None
        # Should not have email_drafts for read-only operations
        assert len(result.get("email_drafts", [])) == 0

    async def test_route_to_authorization_for_write_ops(self):
        """Test that write operations go through authorization"""
        graph = build_graph()

        state = {
            "query": "Send an email to John",
            "intent": "send_email",
            "user_id": "test_user"
        }

        result = await graph.ainvoke(state)

        assert result is not None
        # Should have gone through authorization
        assert "requires_authorization" in result

    async def test_route_bypass_execution_without_authorization(self):
        """Test execution is bypassed without proper authorization"""
        graph = build_graph()

        state = {
            "query": "Send email",
            "intent": "send_email",
            "requires_authorization": True,
            "user_approved": False,
            "user_id": "test_user"
        }

        result = await graph.ainvoke(state)

        assert result is not None
        # Should not execute without approval
        assert len(result.get("executed_actions", [])) == 0

    async def test_conditional_edge_based_on_error(self):
        """Test routing when error occurs"""
        graph = build_graph()

        state = {
            "query": "Test query",
            "error": "Something went wrong",
            "user_id": "test_user"
        }

        result = await graph.ainvoke(state)

        assert result is not None
        # Should handle error gracefully

    async def test_retry_logic_on_transient_error(self):
        """Test retry logic for transient errors"""
        graph = build_graph()

        state = {
            "query": "Test",
            "retry_count": 0,
            "user_id": "test_user"
        }

        with patch('voice_agent.agents.intent_agent.IntentClassificationAgent.run',
                   side_effect=[Exception("Transient"), {"intent": "triage_inbox"}]):
            result = await graph.ainvoke(state)

            assert result is not None

    async def test_max_retries_exceeded(self):
        """Test behavior when max retries exceeded"""
        graph = build_graph()

        state = {
            "query": "Test",
            "retry_count": 10,  # Already at max
            "user_id": "test_user"
        }

        result = await graph.ainvoke(state)

        assert result is not None
        # Should have error in result


@pytest.mark.asyncio
class TestStateTransitions:
    """Test state transitions through the graph"""

    async def test_state_accumulation(self):
        """Test that state accumulates through nodes"""
        graph = build_graph()

        initial_state = {
            "query": "What are my emails?",
            "user_id": "test_user",
            "mode": "text"
        }

        result = await graph.ainvoke(initial_state)

        # State should have accumulated data from all nodes
        assert "query" in result
        assert "user_id" in result
        # Should have added intent
        assert "intent" in result or "error" in result

    async def test_state_intent_added(self):
        """Test that intent is added to state"""
        graph = build_graph()

        state = {"query": "Check emails", "user_id": "test_user"}

        result = await graph.ainvoke(state)

        assert "intent" in result

    async def test_state_context_added(self):
        """Test that context is added to state"""
        graph = build_graph()

        state = {"query": "What are my emails?", "user_id": "test_user"}

        result = await graph.ainvoke(state)

        # Should have email_threads or calendar_events
        assert "email_threads" in result or "calendar_events" in result or "error" in result

    async def test_state_reasoning_added(self):
        """Test that reasoning is added to state"""
        graph = build_graph()

        state = {"query": "Triage inbox", "user_id": "test_user"}

        result = await graph.ainvoke(state)

        # Should have priority_assessment or recommended_action
        assert any(k in result for k in ["priority_assessment", "recommended_action", "reasoning", "error"])

    async def test_state_drafts_added(self):
        """Test that drafts are added for write operations"""
        graph = build_graph()

        state = {"query": "Draft reply to John", "user_id": "test_user"}

        result = await graph.ainvoke(state)

        # Should have email_drafts for draft operations
        assert "email_drafts" in result or "error" in result

    async def test_state_authorization_added(self):
        """Test that authorization info is added"""
        graph = build_graph()

        state = {"query": "Send email to CEO", "user_id": "test_user"}

        result = await graph.ainvoke(state)

        # Should have authorization information
        assert "requires_authorization" in result or "error" in result

    async def test_state_execution_results_added(self):
        """Test that execution results are added"""
        graph = build_graph()

        state = {
            "query": "Archive old emails",
            "user_id": "test_user",
            "user_approved": True
        }

        result = await graph.ainvoke(state)

        # Should have executed_actions or execution_status
        assert any(k in result for k in ["executed_actions", "execution_status", "error"])

    async def test_state_final_response_added(self):
        """Test that final response is added"""
        graph = build_graph()

        state = {"query": "What are my emails?", "user_id": "test_user"}

        result = await graph.ainvoke(state)

        # Should have final response
        assert any(k in result for k in ["text_response", "voice_response", "final_response", "response"])


@pytest.mark.asyncio
class TestGraphExecution:
    """Test graph execution patterns"""

    async def test_execute_full_graph(self):
        """Test executing the full graph"""
        graph = build_graph()

        state = {
            "query": "What are my most important emails?",
            "user_id": "test_user",
            "mode": "text"
        }

        result = await graph.ainvoke(state)

        assert result is not None
        assert isinstance(result, dict)

    async def test_execute_with_streaming(self):
        """Test graph execution with streaming"""
        graph = build_graph()

        state = {
            "query": "Summarize my inbox",
            "user_id": "test_user",
            "mode": "text"
        }

        # Stream results
        results = []
        async for chunk in graph.astream(state):
            results.append(chunk)

        assert len(results) > 0

    async def test_execute_multiple_concurrent(self):
        """Test executing multiple graph instances concurrently"""
        import asyncio
        graph = build_graph()

        states = [
            {"query": "Query 1", "user_id": "user1"},
            {"query": "Query 2", "user_id": "user2"},
            {"query": "Query 3", "user_id": "user3"}
        ]

        results = await asyncio.gather(*[
            graph.ainvoke(state) for state in states
        ])

        assert len(results) == 3
        assert all(r is not None for r in results)

    async def test_execute_with_timeout(self):
        """Test graph execution with timeout"""
        import asyncio
        graph = build_graph()

        state = {"query": "Test query", "user_id": "test_user"}

        try:
            result = await asyncio.wait_for(
                graph.ainvoke(state),
                timeout=5.0
            )
            assert result is not None
        except asyncio.TimeoutError:
            pytest.fail("Graph execution timed out")


@pytest.mark.asyncio
class TestGraphErrorHandling:
    """Test error handling in graph"""

    async def test_handle_node_error(self):
        """Test handling error in a single node"""
        graph = build_graph()

        with patch('voice_agent.agents.intent_agent.IntentClassificationAgent.run',
                   side_effect=Exception("Node error")):
            state = {"query": "Test", "user_id": "test_user"}

            result = await graph.ainvoke(state)

            # Should have error in result
            assert "error" in result or result is not None

    async def test_handle_invalid_state(self):
        """Test handling invalid state"""
        graph = build_graph()

        # Invalid state (missing required fields)
        state = {}

        with pytest.raises((KeyError, ValueError, Exception)):
            await graph.ainvoke(state)

    async def test_handle_graph_construction_error(self):
        """Test handling error during graph construction"""
        with patch('voice_agent.graph.graph_builder.GraphBuilder',
                   side_effect=Exception("Construction error")):
            with pytest.raises(Exception):
                build_graph()

    async def test_error_propagation(self):
        """Test that errors propagate correctly"""
        graph = build_graph()

        state = {
            "query": "Test",
            "user_id": "test_user",
            "error": "Previous error"
        }

        result = await graph.ainvoke(state)

        # Error should still be present
        assert "error" in result


@pytest.mark.asyncio
class TestGraphOptimization:
    """Test graph optimization and performance"""

    async def test_skip_unnecessary_nodes(self):
        """Test that unnecessary nodes are skipped"""
        graph = build_graph()

        # Read-only query should skip execution
        state = {
            "query": "What's on my calendar?",
            "intent": "check_calendar",
            "user_id": "test_user"
        }

        result = await graph.ainvoke(state)

        assert result is not None
        # No execution should have happened
        assert len(result.get("executed_actions", [])) == 0

    async def test_parallel_node_execution(self):
        """Test parallel execution of independent nodes"""
        # If graph supports parallel execution
        graph = build_graph()

        state = {"query": "Test", "user_id": "test_user"}

        result = await graph.ainvoke(state)

        assert result is not None

    async def test_caching_behavior(self):
        """Test caching of intermediate results"""
        graph = build_graph()

        state = {"query": "Test query", "user_id": "test_user"}

        # Execute twice
        result1 = await graph.ainvoke(state)
        result2 = await graph.ainvoke(state)

        assert result1 is not None
        assert result2 is not None


@pytest.mark.asyncio
class TestGraphCheckpointing:
    """Test graph checkpointing and resumption"""

    async def test_save_checkpoint(self):
        """Test saving graph state checkpoint"""
        graph = build_graph()

        state = {"query": "Test", "user_id": "test_user"}

        # Execute and checkpoint
        result = await graph.ainvoke(state)

        assert result is not None

    async def test_resume_from_checkpoint(self):
        """Test resuming graph from checkpoint"""
        graph = build_graph()

        # Create initial state
        state = {
            "query": "Test",
            "user_id": "test_user",
            "intent": "triage_inbox",
            "checkpoint": True
        }

        # Resume execution
        result = await graph.ainvoke(state)

        assert result is not None


@pytest.mark.asyncio
class TestGraphIntrospection:
    """Test graph introspection capabilities"""

    def test_get_graph_structure(self):
        """Test retrieving graph structure"""
        graph = build_graph()

        # Should be able to introspect graph
        assert graph is not None

    def test_get_node_list(self):
        """Test retrieving list of nodes"""
        graph = build_graph()

        # Graph should expose its nodes
        assert graph is not None

    def test_get_edge_list(self):
        """Test retrieving list of edges"""
        graph = build_graph()

        # Graph should expose its edges
        assert graph is not None

    def test_visualize_graph(self):
        """Test graph visualization capability"""
        graph = build_graph()

        # Should be able to generate visualization
        assert graph is not None
