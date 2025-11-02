"""
Authorization Models
Models for authorization codes and session management
"""

from datetime import datetime, timedelta
from typing import Literal
from pydantic import BaseModel, Field
import secrets


class AuthorizationCode(BaseModel):
    """
    One-time authorization code for confirming actions.
    Required before sending emails, accepting invites, or modifying calendar.
    """
    code: str = Field(
        description="The authorization code (e.g., '1234')"
    )
    action_id: str = Field(
        description="The action this code authorizes"
    )
    action_type: Literal["send_email", "calendar_action", "bulk_action"]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    is_used: bool = Field(default=False)
    used_at: datetime | None = None
    attempts: int = Field(default=0, ge=0)
    max_attempts: int = Field(default=3)

    @classmethod
    def generate(
        cls,
        action_id: str,
        action_type: Literal["send_email", "calendar_action", "bulk_action"],
        code_length: int = 4,
        expiry_minutes: int = 10
    ) -> "AuthorizationCode":
        """Generate a new authorization code"""
        code = "".join([str(secrets.randbelow(10)) for _ in range(code_length)])
        expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)

        return cls(
            code=code,
            action_id=action_id,
            action_type=action_type,
            expires_at=expires_at
        )

    def is_valid(self) -> bool:
        """Check if code is still valid"""
        if self.is_used:
            return False
        if self.attempts >= self.max_attempts:
            return False
        if datetime.utcnow() > self.expires_at:
            return False
        return True

    def verify(self, input_code: str) -> bool:
        """Verify an input code"""
        self.attempts += 1
        if not self.is_valid():
            return False
        if self.code == input_code:
            self.is_used = True
            self.used_at = datetime.utcnow()
            return True
        return False


class AuthSession(BaseModel):
    """User session for tracking authorization context"""
    session_id: str
    user_id: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    active_codes: dict[str, AuthorizationCode] = Field(
        default_factory=dict,
        description="Active authorization codes by action_id"
    )
    completed_actions: list[str] = Field(
        default_factory=list,
        description="Action IDs completed in this session"
    )
    pending_actions: list[str] = Field(
        default_factory=list,
        description="Action IDs awaiting authorization"
    )

    def add_code(self, code: AuthorizationCode) -> None:
        """Add an authorization code to the session"""
        self.active_codes[code.action_id] = code
        if code.action_id not in self.pending_actions:
            self.pending_actions.append(code.action_id)
        self.last_activity = datetime.utcnow()

    def verify_code(self, action_id: str, input_code: str) -> bool:
        """Verify a code for a specific action"""
        if action_id not in self.active_codes:
            return False
        code = self.active_codes[action_id]
        is_valid = code.verify(input_code)
        if is_valid:
            self.completed_actions.append(action_id)
            if action_id in self.pending_actions:
                self.pending_actions.remove(action_id)
        self.last_activity = datetime.utcnow()
        return is_valid

    def cleanup_expired(self) -> None:
        """Remove expired codes from the session"""
        expired = [
            action_id for action_id, code in self.active_codes.items()
            if not code.is_valid()
        ]
        for action_id in expired:
            del self.active_codes[action_id]
            if action_id in self.pending_actions:
                self.pending_actions.remove(action_id)
