"""
Authorization Agent
Manages authorization codes and user confirmation
"""

from ..graph.state import VoiceAgentState
from ..models.auth_models import AuthorizationCode
import uuid


class AuthorizationAgent:
    """
    Handles authorization for actions that require user confirmation.
    Generates auth codes and validates them before execution.
    """

    def __init__(self, code_length: int = 4, expiry_minutes: int = 10):
        self.code_length = code_length
        self.expiry_minutes = expiry_minutes
        # In production, this would be a persistent session store
        self.active_codes: dict[str, AuthorizationCode] = {}

    async def run(self, state: VoiceAgentState) -> VoiceAgentState:
        """Check authorization status and generate codes if needed"""
        requires_auth = state.get("requires_authorization", False)
        auth_code_input = state.get("authorization_code")

        # Initialize pending actions list
        state.setdefault("pending_actions", [])

        if not requires_auth:
            # No authorization needed
            return state

        # Collect all actions that need authorization
        pending_actions = []

        for draft in state.get("email_drafts", []):
            if draft.get("requires_authorization", True):
                action_id = draft["draft_id"]
                pending_actions.append(action_id)

                # Generate auth code if not already exists
                if action_id not in self.active_codes and not auth_code_input:
                    code = AuthorizationCode.generate(
                        action_id=action_id,
                        action_type="send_email",
                        code_length=self.code_length,
                        expiry_minutes=self.expiry_minutes
                    )
                    self.active_codes[action_id] = code

        for cal_action in state.get("calendar_actions", []):
            if cal_action.get("requires_authorization", True):
                action_id = cal_action["action_id"]
                pending_actions.append(action_id)

                # Generate auth code if not already exists
                if action_id not in self.active_codes and not auth_code_input:
                    code = AuthorizationCode.generate(
                        action_id=action_id,
                        action_type="calendar_action",
                        code_length=self.code_length,
                        expiry_minutes=self.expiry_minutes
                    )
                    self.active_codes[action_id] = code

        state["pending_actions"] = pending_actions

        # If user provided an auth code, validate it
        if auth_code_input:
            validation_result = self._validate_code(auth_code_input, pending_actions)
            if not validation_result["valid"]:
                state["error"] = validation_result["message"]
                # Clear the authorization code so user can try again
                state["authorization_code"] = None

        return state

    def _validate_code(self, input_code: str, pending_actions: list[str]) -> dict:
        """Validate an authorization code"""
        # Try to validate against any pending action
        for action_id in pending_actions:
            if action_id in self.active_codes:
                code_obj = self.active_codes[action_id]
                if code_obj.verify(input_code):
                    return {
                        "valid": True,
                        "action_id": action_id,
                        "message": "Authorization successful"
                    }

        return {
            "valid": False,
            "message": "Invalid or expired authorization code. Please try again."
        }

    def get_code_for_action(self, action_id: str) -> str | None:
        """Get the authorization code for a specific action"""
        if action_id in self.active_codes:
            return self.active_codes[action_id].code
        return None
