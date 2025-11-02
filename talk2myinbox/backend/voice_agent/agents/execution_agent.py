"""
Execution Agent
Executes authorized actions (send emails, update calendar)
"""

from ..graph.state import VoiceAgentState
from ..adapters.email.base import BaseEmailAdapter
from ..adapters.calendar.base import BaseCalendarAdapter
from typing import Any


class ExecutionAgent:
    """
    Executes actions after authorization is confirmed.
    This is where emails are actually sent and calendar events are modified.
    """

    def __init__(
        self,
        email_adapter: BaseEmailAdapter | None = None,
        calendar_adapter: BaseCalendarAdapter | None = None
    ):
        self.email_adapter = email_adapter
        self.calendar_adapter = calendar_adapter

    async def run(self, state: VoiceAgentState) -> VoiceAgentState:
        """Execute all authorized actions"""
        # Initialize execution tracking
        state.setdefault("executed_actions", [])
        state.setdefault("execution_status", {})

        # Check if we have authorization
        auth_code = state.get("authorization_code")
        if not auth_code:
            # No authorization provided, don't execute
            state["execution_status"] = {
                "status": "awaiting_authorization",
                "message": "Actions prepared but awaiting user authorization"
            }
            return state

        try:
            # Execute email actions
            for draft in state.get("email_drafts", []):
                if draft["draft_id"] in state.get("pending_actions", []):
                    result = await self._send_email(draft)
                    state["executed_actions"].append({
                        "action_id": draft["draft_id"],
                        "action_type": "send_email",
                        "result": result
                    })

            # Execute calendar actions
            for cal_action in state.get("calendar_actions", []):
                if cal_action["action_id"] in state.get("pending_actions", []):
                    result = await self._execute_calendar_action(cal_action)
                    state["executed_actions"].append({
                        "action_id": cal_action["action_id"],
                        "action_type": "calendar_action",
                        "result": result
                    })

            state["execution_status"] = {
                "status": "completed",
                "message": f"Successfully executed {len(state['executed_actions'])} action(s)"
            }

        except Exception as e:
            state["error"] = f"Execution error: {str(e)}"
            state["execution_status"] = {
                "status": "failed",
                "message": str(e)
            }

        return state

    async def _send_email(self, draft: dict) -> dict[str, Any]:
        """Send an email"""
        if self.email_adapter:
            try:
                # Call the actual email adapter to send
                result = await self.email_adapter.send_email(
                    to=draft["to"],
                    cc=draft.get("cc", []),
                    subject=draft["subject"],
                    body=draft["body"],
                    thread_id=draft.get("thread_id")
                )
                return {
                    "success": True,
                    "message_id": result.get("message_id", "unknown"),
                    "details": "Email sent successfully"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "details": "Failed to send email"
                }
        else:
            # Mock execution for testing
            return {
                "success": True,
                "message_id": f"mock_{draft['draft_id']}",
                "details": "Email sent (mock)"
            }

    async def _execute_calendar_action(self, action: dict) -> dict[str, Any]:
        """Execute a calendar action"""
        if self.calendar_adapter:
            try:
                action_type = action["action_type"]

                if action_type == "accept_invite":
                    result = await self.calendar_adapter.accept_event(
                        event_id=action["event"]["event_id"]
                    )
                elif action_type == "decline_invite":
                    result = await self.calendar_adapter.decline_event(
                        event_id=action["event"]["event_id"],
                        message=action.get("draft_response")
                    )
                elif action_type == "propose_alternative":
                    result = await self.calendar_adapter.propose_alternative(
                        event_id=action["event"]["event_id"],
                        alternative_times=action.get("alternative_times", []),
                        message=action.get("draft_response")
                    )
                elif action_type == "create_event":
                    result = await self.calendar_adapter.create_event(
                        event=action["event"]
                    )
                else:
                    return {
                        "success": False,
                        "error": f"Unknown action type: {action_type}"
                    }

                return {
                    "success": True,
                    "event_id": result.get("event_id", "unknown"),
                    "details": f"Calendar action '{action_type}' completed"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "details": f"Failed to execute calendar action"
                }
        else:
            # Mock execution for testing
            return {
                "success": True,
                "event_id": f"mock_{action['action_id']}",
                "details": f"Calendar action '{action['action_type']}' executed (mock)"
            }
