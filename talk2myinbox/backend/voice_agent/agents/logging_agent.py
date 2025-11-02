"""
Logging Agent
Records all actions to audit trail and dashboard
"""

from ..graph.state import VoiceAgentState
from ..models.action_models import ActionLog, ActionStatus
from datetime import datetime
import uuid
import json


class LoggingAgent:
    """
    Final node in the pipeline.
    Records all actions, decisions, and outcomes for:
    - Audit trail
    - Dashboard display
    - Historical context
    """

    def __init__(self, log_storage=None):
        self.log_storage = log_storage  # Could be database, file, or API
        self.logs_buffer = []

    async def run(self, state: VoiceAgentState) -> VoiceAgentState:
        """Generate and store action logs"""
        # Initialize action logs
        state.setdefault("action_logs", [])

        # Determine the agent name (from settings in production)
        agent_name = "Vinegar"
        mode = state.get("interaction_mode", "text")
        user_id = state.get("user_id")

        # Log intent classification
        if state.get("intent"):
            log = self._create_log(
                actor=agent_name,
                mode=mode,
                object_type="summary",
                object_ref=f"Intent: {state['intent']}",
                action="classified_intent",
                reason=state.get("reasoning", "")[:200],
                status=ActionStatus(
                    status="completed",
                    status_message="Intent classified successfully"
                ),
                user_id=user_id
            )
            state["action_logs"].append(log)

        # Log email drafts
        for draft in state.get("email_drafts", []):
            log = self._create_log(
                actor=agent_name,
                mode=mode,
                object_type="email",
                object_ref=draft.get("subject", "Email Draft"),
                action="drafted_reply",
                reason=draft.get("reasoning", "User requested email draft"),
                status=self._determine_status(draft, state),
                user_id=user_id,
                metadata={
                    "draft_id": draft.get("draft_id"),
                    "to": draft.get("to", []),
                    "thread_id": draft.get("thread_id")
                }
            )
            state["action_logs"].append(log)

        # Log calendar actions
        for cal_action in state.get("calendar_actions", []):
            log = self._create_log(
                actor=agent_name,
                mode=mode,
                object_type="calendar",
                object_ref=cal_action.get("event", {}).get("title", "Calendar Event"),
                action=cal_action.get("action_type", "calendar_action"),
                reason=cal_action.get("reasoning", "User requested calendar action"),
                status=self._determine_status(cal_action, state),
                user_id=user_id,
                metadata={
                    "action_id": cal_action.get("action_id"),
                    "event_id": cal_action.get("event", {}).get("event_id"),
                    "proposed_status": cal_action.get("proposed_status")
                }
            )
            state["action_logs"].append(log)

        # Log execution results
        for executed in state.get("executed_actions", []):
            log = self._create_log(
                actor=agent_name,
                mode=mode,
                object_type=executed["action_type"].split("_")[0],  # "send_email" -> "email"
                object_ref=f"Action {executed['action_id']}",
                action="executed",
                reason="Action executed after authorization",
                status=ActionStatus(
                    status="completed" if executed["result"].get("success") else "failed",
                    status_message=executed["result"].get("details", "")
                ),
                user_id=user_id,
                authorization_code_used=True,
                metadata=executed["result"]
            )
            state["action_logs"].append(log)

        # Store logs persistently
        await self._persist_logs(state["action_logs"])

        # Generate final response
        state = self._generate_final_response(state)

        return state

    def _create_log(
        self,
        actor: str,
        mode: str,
        object_type: str,
        object_ref: str,
        action: str,
        reason: str,
        status: ActionStatus,
        user_id: str | None = None,
        authorization_code_used: bool = False,
        metadata: dict | None = None
    ) -> dict:
        """Create a structured action log entry"""
        return {
            "log_id": f"log_{uuid.uuid4().hex[:12]}",
            "timestamp": datetime.utcnow().isoformat(),
            "actor": actor,
            "mode": mode,
            "object_type": object_type,
            "object_ref": object_ref,
            "action": action,
            "reason": reason,
            "status": {
                "status": status.status,
                "status_message": status.status_message,
                "updated_at": status.updated_at.isoformat() if hasattr(status.updated_at, 'isoformat') else str(status.updated_at)
            },
            "user_id": user_id,
            "authorization_code_used": authorization_code_used,
            "metadata": metadata or {}
        }

    def _determine_status(self, item: dict, state: VoiceAgentState) -> ActionStatus:
        """Determine the status of an action"""
        item_id = item.get("draft_id") or item.get("action_id")

        # Check if executed
        for executed in state.get("executed_actions", []):
            if executed["action_id"] == item_id:
                if executed["result"].get("success"):
                    return ActionStatus(
                        status="completed",
                        status_message="Action executed successfully"
                    )
                else:
                    return ActionStatus(
                        status="failed",
                        status_message=executed["result"].get("error", "Execution failed")
                    )

        # Check if awaiting authorization
        if item_id in state.get("pending_actions", []):
            return ActionStatus(
                status="pending_user_auth",
                status_message="Awaiting user authorization code"
            )

        # Draft only
        return ActionStatus(
            status="draft_only",
            status_message="Draft prepared, no execution requested"
        )

    async def _persist_logs(self, logs: list[dict]):
        """Persist logs to storage"""
        if self.log_storage:
            try:
                await self.log_storage.save_logs(logs)
            except Exception as e:
                # Log storage failed, buffer locally
                self.logs_buffer.extend(logs)
        else:
            # No storage configured, just buffer
            self.logs_buffer.extend(logs)

    def _generate_final_response(self, state: VoiceAgentState) -> VoiceAgentState:
        """Generate user-facing final response"""
        intent = state.get("intent", "unknown")
        email_drafts = state.get("email_drafts", [])
        calendar_actions = state.get("calendar_actions", [])
        executed_actions = state.get("executed_actions", [])
        error = state.get("error")

        # Build response based on what happened
        if error:
            response_text = f"I encountered an issue: {error}"
        elif executed_actions:
            response_text = f"I've successfully completed {len(executed_actions)} action(s). "
            if any(not ex["result"].get("success") for ex in executed_actions):
                response_text += "However, some actions failed. Please check the details."
        elif email_drafts or calendar_actions:
            response_text = "I've prepared the following for your review:\n\n"
            for draft in email_drafts:
                response_text += f"- Email draft: '{draft['subject']}' (to {', '.join(draft['to'])})\n"
            for action in calendar_actions:
                response_text += f"- Calendar action: {action['action_type']} for '{action['event']['title']}'\n"
            response_text += "\nWould you like me to proceed? I'll need your authorization code."
        else:
            response_text = f"I've analyzed your request (intent: {intent}). No actions were required."

        state["text_response"] = response_text
        state["voice_response"] = response_text  # Same for now, could be tailored for voice
        state["final_response"] = {
            "text": response_text,
            "intent": intent,
            "drafts": email_drafts,
            "calendar_actions": calendar_actions,
            "executed": executed_actions,
            "logs": state["action_logs"]
        }

        return state
