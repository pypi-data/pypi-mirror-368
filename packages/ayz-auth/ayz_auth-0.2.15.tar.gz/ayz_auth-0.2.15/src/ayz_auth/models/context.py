"""
Pydantic models for Stytch authentication context.

Contains the StytchContext model that represents authenticated user session data
returned by the Stytch B2B API.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_serializer


class StytchContext(BaseModel):
    """
    Represents authenticated user context from Stytch B2B session verification.

    This model contains only the essential Stytch session data needed for
    authentication and authorization decisions. The consuming application
    can use the member_id to fetch additional user data from their own database.
    """

    # Core Stytch identifiers
    member_id: Optional[str] = Field(
        default=None, description="Unique Stytch member identifier"
    )
    session_id: Optional[str] = Field(
        default=None, description="Unique Stytch session identifier"
    )
    organization_id: Optional[str] = Field(
        default=None, description="Stytch organization identifier"
    )

    # Session timing information
    session_started_at: Optional[datetime] = Field(
        default=None, description="When the session was initially created"
    )
    session_expires_at: Optional[datetime] = Field(
        default=None, description="When the session will expire"
    )
    session_last_accessed_at: Optional[datetime] = Field(
        default=None, description="When the session was last accessed"
    )

    # Member information from Stytch
    member_email: Optional[str] = Field(
        default=None, description="Member email address from Stytch"
    )
    member_name: Optional[str] = Field(
        default=None, description="Member display name from Stytch"
    )

    # Session metadata
    session_custom_claims: Dict[str, Any] = Field(
        default_factory=dict, description="Custom claims attached to the session"
    )

    # Authentication metadata
    authenticated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this context was created by the middleware",
    )
    authentication_factors: List[str] = Field(
        default_factory=list, description="Authentication factors used for this session"
    )

    # Raw Stytch session data for extensibility
    raw_session_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Complete raw session response from Stytch API",
    )

    model_config = {
        "extra": "forbid",  # Don't allow extra fields
        "validate_assignment": True,  # Validate on assignment
    }

    @field_serializer(
        "session_started_at",
        "session_expires_at",
        "session_last_accessed_at",
        "authenticated_at",
    )
    def serialize_datetime(self, value: datetime) -> str:
        """Serialize datetime fields to ISO format."""
        return value.isoformat()

    @property
    def is_expired(self) -> bool:
        """Check if the session has expired."""
        if not self.session_expires_at:
            return True
        return datetime.now(timezone.utc) > self.session_expires_at

    @property
    def time_until_expiry(self) -> Optional[float]:
        """Get seconds until session expires, or None if already expired."""
        if not self.session_expires_at or self.is_expired:
            return None
        return (self.session_expires_at - datetime.now(timezone.utc)).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return self.model_dump(mode="json")

    def __str__(self) -> str:
        """String representation for logging (without sensitive data)."""
        expires = (
            self.session_expires_at.isoformat() if self.session_expires_at else None
        )
        return (
            f"StytchContext(member_id={self.member_id}, "
            f"organization_id={self.organization_id}, "
            f"expires_at={expires})"
        )
