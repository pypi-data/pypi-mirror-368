"""Persona-based authentication system for business-context-aware API testing.

This module provides a sophisticated persona system that goes beyond traditional
authentication to include business roles, permissions, and contextual information.
It enables testing realistic user scenarios with proper business logic validation.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from testapix.core.events import global_event_bus
from testapix.core.exceptions import TestAPIXError

logger = logging.getLogger(__name__)


class PersonaError(TestAPIXError):
    """Raised when persona operations fail."""

    def __init__(self, message: str, persona_id: str | None = None) -> None:
        super().__init__(message)
        self.persona_id = persona_id


class PersonaRole(Enum):
    """Standard user roles for business contexts."""

    GUEST = "guest"
    USER = "user"
    PREMIUM_USER = "premium_user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    API_CLIENT = "api_client"
    SERVICE_ACCOUNT = "service_account"


class AuthenticationMethod(Enum):
    """Supported authentication methods for personas."""

    BEARER_TOKEN = "bearer_token"  # nosec B105
    API_KEY = "api_key"  # nosec B105
    OAUTH2 = "oauth2"  # nosec B105
    BASIC_AUTH = "basic_auth"  # nosec B105
    JWT = "jwt"  # nosec B105
    CUSTOM = "custom"  # nosec B105


@dataclass
class BusinessContext:
    """Business context information for a persona.

    This captures the business domain, organizational structure,
    and operational context that influences API behavior.
    """

    organization_id: str | None = None
    department: str | None = None
    region: str | None = None
    subscription_tier: str | None = None
    feature_flags: dict[str, bool] = field(default_factory=dict)
    quota_limits: dict[str, int] = field(default_factory=dict)
    custom_attributes: dict[str, Any] = field(default_factory=dict)

    def has_feature(self, feature_name: str) -> bool:
        """Check if a feature is enabled for this business context."""
        return self.feature_flags.get(feature_name, False)

    def get_quota_limit(self, resource: str) -> int | None:
        """Get quota limit for a specific resource."""
        return self.quota_limits.get(resource)

    def merge_context(self, other: BusinessContext) -> BusinessContext:
        """Merge another business context into this one."""
        return BusinessContext(
            organization_id=other.organization_id or self.organization_id,
            department=other.department or self.department,
            region=other.region or self.region,
            subscription_tier=other.subscription_tier or self.subscription_tier,
            feature_flags={**self.feature_flags, **other.feature_flags},
            quota_limits={**self.quota_limits, **other.quota_limits},
            custom_attributes={**self.custom_attributes, **other.custom_attributes},
        )


@dataclass
class AuthenticationCredentials:
    """Authentication credentials for a persona.

    Stores the actual authentication data needed to authenticate
    as this persona. The structure is flexible to support different
    authentication methods.
    """

    method: AuthenticationMethod
    credentials: dict[str, Any] = field(default_factory=dict)
    expires_at: datetime | None = None
    refresh_token: str | None = None

    def is_expired(self) -> bool:
        """Check if credentials are expired."""
        if self.expires_at is None:
            return False
        return datetime.now() >= self.expires_at

    def time_until_expiry(self) -> timedelta | None:
        """Get time until credentials expire."""
        if self.expires_at is None:
            return None
        return self.expires_at - datetime.now()

    def get_credential(self, key: str) -> Any:
        """Get a specific credential value."""
        return self.credentials.get(key)

    def set_credential(self, key: str, value: Any) -> None:
        """Set a specific credential value."""
        self.credentials[key] = value

    def to_auth_header(self) -> dict[str, str]:
        """Convert credentials to HTTP authorization header."""
        if self.method == AuthenticationMethod.BEARER_TOKEN:
            token = self.get_credential("token")
            if token:
                return {"Authorization": f"Bearer {token}"}
        elif self.method == AuthenticationMethod.API_KEY:
            api_key = self.get_credential("api_key")
            header_name = self.get_credential("header_name") or "X-API-Key"
            if api_key:
                return {header_name: api_key}
        elif self.method == AuthenticationMethod.BASIC_AUTH:
            username = self.get_credential("username")
            password = self.get_credential("password")
            if username and password:
                import base64

                credentials = base64.b64encode(
                    f"{username}:{password}".encode()
                ).decode()
                return {"Authorization": f"Basic {credentials}"}

        return {}


class UserPersona(BaseModel):
    """Represents a user persona with identity, authentication, and business context.

    A UserPersona encapsulates all the information needed to test API behavior
    from the perspective of a specific type of user. This includes not just
    authentication credentials, but also business context, permissions,
    and behavioral patterns.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    # Core Identity
    persona_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(max_length=100)
    description: str = Field(default="", max_length=500)
    role: PersonaRole = PersonaRole.USER

    # Authentication
    auth_credentials: AuthenticationCredentials = Field(
        default_factory=lambda: AuthenticationCredentials(
            method=AuthenticationMethod.BEARER_TOKEN
        )
    )

    # Business Context
    business_context: BusinessContext = Field(default_factory=BusinessContext)

    # Metadata
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True

    # Test Data Preferences
    preferred_data_patterns: dict[str, Any] = Field(default_factory=dict)
    test_scenarios: list[str] = Field(default_factory=list)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate that tags are non-empty strings."""
        return [tag.strip() for tag in v if tag.strip()]

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate persona name."""
        if not v.strip():
            raise ValueError("Persona name cannot be empty")
        return v.strip()

    def has_role(self, role: PersonaRole) -> bool:
        """Check if persona has a specific role."""
        return self.role == role

    def has_any_role(self, roles: list[PersonaRole]) -> bool:
        """Check if persona has any of the specified roles."""
        return self.role in roles

    def is_admin(self) -> bool:
        """Check if persona has admin privileges."""
        return self.role in [PersonaRole.ADMIN, PersonaRole.SUPER_ADMIN]

    def is_authenticated(self) -> bool:
        """Check if persona has valid authentication credentials."""
        return not self.auth_credentials.is_expired() and self.is_active

    def has_tag(self, tag: str) -> bool:
        """Check if persona has a specific tag."""
        return tag in self.tags

    def add_tag(self, tag: str) -> None:
        """Add a tag to the persona."""
        tag = tag.strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the persona."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()

    def update_credentials(self, credentials: AuthenticationCredentials) -> None:
        """Update authentication credentials."""
        self.auth_credentials = credentials
        self.updated_at = datetime.now()

    def update_business_context(self, context: BusinessContext) -> None:
        """Update business context."""
        self.business_context = context
        self.updated_at = datetime.now()

    def merge_business_context(self, context: BusinessContext) -> None:
        """Merge business context with existing context."""
        self.business_context = self.business_context.merge_context(context)
        self.updated_at = datetime.now()

    def to_auth_headers(self) -> dict[str, str]:
        """Get HTTP authorization headers for this persona."""
        return self.auth_credentials.to_auth_header()

    def clone(self, **overrides: Any) -> UserPersona:
        """Create a copy of this persona with optional overrides."""
        data = self.model_dump()
        data.update(overrides)
        # Generate new ID for clone unless explicitly provided
        if "persona_id" not in overrides:
            data["persona_id"] = str(uuid.uuid4())
        data["created_at"] = datetime.now()
        data["updated_at"] = datetime.now()
        return UserPersona(**data)

    def to_dict(self) -> dict[str, Any]:
        """Convert persona to dictionary representation."""
        return self.model_dump()

    def __str__(self) -> str:
        """String representation of the persona."""
        return f"UserPersona({self.name}, {self.role.value}, {self.persona_id[:8]})"

    def __repr__(self) -> str:
        """Detailed string representation of the persona."""
        return (
            f"UserPersona(id={self.persona_id[:8]}, name='{self.name}', "
            f"role={self.role.value}, active={self.is_active})"
        )


@dataclass
class PersonaSession:
    """Represents an active authentication session for a persona.

    Manages the runtime state of a persona's authentication,
    including session tracking, refresh logic, and event emission.
    """

    persona: UserPersona
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    session_data: dict[str, Any] = field(default_factory=dict)
    is_authenticated: bool = False

    def __post_init__(self) -> None:
        """Initialize session after creation."""
        # Emit session creation event
        global_event_bus.emit(
            "persona.session.created",
            {
                "persona_id": self.persona.persona_id,
                "session_id": self.session_id,
                "persona_name": self.persona.name,
                "role": self.persona.role.value,
            },
            source="PersonaSession",
        )

    def authenticate(self) -> bool:
        """Authenticate this session.

        Returns
        -------
            True if authentication successful, False otherwise

        """
        try:
            # Check if persona is active and has valid credentials
            if not self.persona.is_active:
                logger.warning(
                    f"Cannot authenticate inactive persona: {self.persona.name}"
                )
                return False

            if self.persona.auth_credentials.is_expired():
                logger.warning(f"Credentials expired for persona: {self.persona.name}")
                return False

            self.is_authenticated = True
            self.last_activity = datetime.now()

            # Emit authentication event
            global_event_bus.emit(
                "persona.authenticated",
                {
                    "persona_id": self.persona.persona_id,
                    "session_id": self.session_id,
                    "persona_name": self.persona.name,
                    "role": self.persona.role.value,
                    "auth_method": self.persona.auth_credentials.method.value,
                },
                source="PersonaSession",
            )

            logger.info(f"Successfully authenticated persona: {self.persona.name}")
            return True

        except Exception as e:
            logger.error(f"Authentication failed for persona {self.persona.name}: {e}")
            self.is_authenticated = False

            # Emit authentication failure event
            global_event_bus.emit(
                "persona.authentication.failed",
                {
                    "persona_id": self.persona.persona_id,
                    "session_id": self.session_id,
                    "persona_name": self.persona.name,
                    "error": str(e),
                },
                source="PersonaSession",
            )

            return False

    def refresh_authentication(self) -> bool:
        """Refresh authentication credentials if possible.

        Returns
        -------
            True if refresh successful, False otherwise

        """
        try:
            # Check if we have a refresh token
            if not self.persona.auth_credentials.refresh_token:
                logger.debug(
                    f"No refresh token available for persona: {self.persona.name}"
                )
                return False

            # This would typically make an API call to refresh the token
            # For now, we'll simulate successful refresh
            logger.info(f"Refreshed authentication for persona: {self.persona.name}")

            self.last_activity = datetime.now()

            # Emit refresh event
            global_event_bus.emit(
                "persona.authentication.refreshed",
                {
                    "persona_id": self.persona.persona_id,
                    "session_id": self.session_id,
                    "persona_name": self.persona.name,
                },
                source="PersonaSession",
            )

            return True

        except Exception as e:
            logger.error(
                f"Failed to refresh authentication for persona {self.persona.name}: {e}"
            )
            return False

    def logout(self) -> None:
        """Logout and end this session."""
        self.is_authenticated = False

        # Emit logout event
        global_event_bus.emit(
            "persona.logged_out",
            {
                "persona_id": self.persona.persona_id,
                "session_id": self.session_id,
                "persona_name": self.persona.name,
                "session_duration": (datetime.now() - self.started_at).total_seconds(),
            },
            source="PersonaSession",
        )

        logger.info(f"Logged out persona: {self.persona.name}")

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now()

    def get_session_duration(self) -> timedelta:
        """Get total session duration."""
        return datetime.now() - self.started_at

    def is_session_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if session has expired due to inactivity."""
        timeout = timedelta(minutes=timeout_minutes)
        return (datetime.now() - self.last_activity) > timeout

    def get_session_data(self, key: str) -> Any:
        """Get session-specific data."""
        return self.session_data.get(key)

    def set_session_data(self, key: str, value: Any) -> None:
        """Set session-specific data."""
        self.session_data[key] = value
        self.update_activity()

    def __str__(self) -> str:
        """String representation of the session."""
        status = "authenticated" if self.is_authenticated else "unauthenticated"
        return f"PersonaSession({self.persona.name}, {status}, {self.session_id[:8]})"


class PersonaPool:
    """Manages a collection of user personas for testing scenarios.

    The PersonaPool provides high-level operations for managing personas,
    including creation, retrieval, filtering, and session management.
    It acts as the primary interface for persona-based testing.
    """

    def __init__(self, name: str = "default") -> None:
        """Initialize the persona pool.

        Args:
        ----
            name: Name identifier for this persona pool

        """
        self.name = name
        self._personas: dict[str, UserPersona] = {}
        self._sessions: dict[str, PersonaSession] = {}
        self._logger = logging.getLogger(f"{__name__}.{name}")

    def add_persona(self, persona: UserPersona) -> None:
        """Add a persona to the pool.

        Args:
        ----
            persona: Persona to add

        Raises:
        ------
            PersonaError: If persona with same ID already exists

        """
        if persona.persona_id in self._personas:
            raise PersonaError(
                f"Persona with ID {persona.persona_id} already exists",
                persona_id=persona.persona_id,
            )

        self._personas[persona.persona_id] = persona
        self._logger.info(f"Added persona: {persona.name} ({persona.persona_id[:8]})")

        # Emit persona added event
        global_event_bus.emit(
            "persona.added",
            {
                "persona_id": persona.persona_id,
                "persona_name": persona.name,
                "role": persona.role.value,
                "pool_name": self.name,
            },
            source="PersonaPool",
        )

    def remove_persona(self, persona_id: str) -> bool:
        """Remove a persona from the pool.

        Args:
        ----
            persona_id: ID of persona to remove

        Returns:
        -------
            True if persona was removed, False if not found

        """
        if persona_id not in self._personas:
            return False

        persona = self._personas[persona_id]

        # End any active sessions for this persona
        sessions_to_end = [
            session_id
            for session_id, session in self._sessions.items()
            if session.persona.persona_id == persona_id
        ]

        for session_id in sessions_to_end:
            self.end_session(session_id)

        del self._personas[persona_id]
        self._logger.info(f"Removed persona: {persona.name} ({persona_id[:8]})")

        # Emit persona removed event
        global_event_bus.emit(
            "persona.removed",
            {
                "persona_id": persona_id,
                "persona_name": persona.name,
                "pool_name": self.name,
            },
            source="PersonaPool",
        )

        return True

    def get_persona(self, persona_id: str) -> UserPersona | None:
        """Get a persona by ID."""
        return self._personas.get(persona_id)

    def get_persona_by_name(self, name: str) -> UserPersona | None:
        """Get a persona by name (returns first match)."""
        for persona in self._personas.values():
            if persona.name == name:
                return persona
        return None

    def list_personas(
        self,
        role: PersonaRole | None = None,
        tags: list[str] | None = None,
        active_only: bool = True,
    ) -> list[UserPersona]:
        """List personas with optional filtering.

        Args:
        ----
            role: Filter by specific role
            tags: Filter by tags (persona must have all specified tags)
            active_only: Only return active personas

        Returns:
        -------
            List of matching personas

        """
        personas = list(self._personas.values())

        if active_only:
            personas = [p for p in personas if p.is_active]

        if role is not None:
            personas = [p for p in personas if p.role == role]

        if tags:
            personas = [p for p in personas if all(p.has_tag(tag) for tag in tags)]

        return personas

    def get_personas_by_role(self, role: PersonaRole) -> list[UserPersona]:
        """Get all personas with a specific role."""
        return [p for p in self._personas.values() if p.role == role]

    def get_by_role(self, role: PersonaRole) -> list[UserPersona]:
        """Get all active personas with a specific role.

        Args:
        ----
            role: PersonaRole to filter by

        Returns:
        -------
            List of active personas with the specified role

        """
        return [p for p in self._personas.values() if p.role == role and p.is_active]

    def get_first_by_role(self, role: PersonaRole) -> UserPersona | None:
        """Get first active persona with a specific role.

        Args:
        ----
            role: PersonaRole to search for

        Returns:
        -------
            First matching active persona, or None if not found

        """
        personas = self.get_by_role(role)
        return personas[0] if personas else None

    def get_by_business_context(self, **filters: Any) -> list[UserPersona]:
        """Filter active personas by business context attributes.

        Args:
        ----
            **filters: Business context filters to apply
                      Supported filters:
                      - organization_id: str
                      - department: str
                      - region: str
                      - subscription_tier: str
                      - feature_flags: dict[str, bool]
                      - quota_limits: dict[str, int]
                      - custom_attributes: dict[str, Any]

        Returns:
        -------
            List of personas matching all specified filters

        Examples:
        --------
            # Find premium users in engineering
            personas = pool.get_by_business_context(
                subscription_tier="premium",
                department="engineering"
            )

            # Find users with specific feature flags
            personas = pool.get_by_business_context(
                feature_flags={"billing_enabled": True, "analytics": True}
            )

        """
        active_personas = [p for p in self._personas.values() if p.is_active]
        return self._filter_by_business_context(active_personas, filters)

    def get_by_tags(self, tags: list[str], match_all: bool = True) -> list[UserPersona]:
        """Filter active personas by tags.

        Args:
        ----
            tags: List of tags to filter by
            match_all: If True, persona must have all tags. If False, any tag matches.

        Returns:
        -------
            List of personas matching tag criteria

        Examples:
        --------
            # Find personas with both "testing" and "automation" tags
            personas = pool.get_by_tags(["testing", "automation"], match_all=True)

            # Find personas with either "admin" or "moderator" tags
            personas = pool.get_by_tags(["admin", "moderator"], match_all=False)

        """
        if not tags:
            return []

        matching = []
        for persona in self._personas.values():
            if not persona.is_active:
                continue

            if match_all:
                if all(persona.has_tag(tag) for tag in tags):
                    matching.append(persona)
            else:
                if any(persona.has_tag(tag) for tag in tags):
                    matching.append(persona)

        return matching

    def find_personas(
        self,
        role: PersonaRole | None = None,
        tags: list[str] | None = None,
        business_context_filters: dict[str, Any] | None = None,
        match_all_tags: bool = True,
        active_only: bool = True,
    ) -> list[UserPersona]:
        """Advanced persona search with multiple criteria.

        Args:
        ----
            role: Optional role filter
            tags: Optional tag filters
            business_context_filters: Optional business context filters
            match_all_tags: If True, persona must have all tags
            active_only: If True, only return active personas

        Returns:
        -------
            List of personas matching all specified criteria

        Examples:
        --------
            # Find active premium engineering admins with testing tag
            personas = pool.find_personas(
                role=PersonaRole.ADMIN,
                tags=["testing"],
                business_context_filters={
                    "department": "engineering",
                    "subscription_tier": "premium"
                }
            )

        """
        personas = list(self._personas.values())

        personas = self._filter_by_active_status(personas, active_only)
        personas = self._filter_by_role(personas, role)
        personas = self._filter_by_tags(personas, tags, match_all_tags)
        personas = self._filter_by_business_context(personas, business_context_filters)

        return personas

    def _filter_by_active_status(
        self, personas: list[UserPersona], active_only: bool
    ) -> list[UserPersona]:
        """Filter personas by active status."""
        if active_only:
            return [p for p in personas if p.is_active]
        return personas

    def _filter_by_role(
        self, personas: list[UserPersona], role: PersonaRole | None
    ) -> list[UserPersona]:
        """Filter personas by role."""
        if role is not None:
            return [p for p in personas if p.role == role]
        return personas

    def _filter_by_tags(
        self, personas: list[UserPersona], tags: list[str] | None, match_all_tags: bool
    ) -> list[UserPersona]:
        """Filter personas by tags."""
        if not tags:
            return personas

        if match_all_tags:
            return [p for p in personas if all(p.has_tag(tag) for tag in tags)]
        else:
            return [p for p in personas if any(p.has_tag(tag) for tag in tags)]

    def _filter_by_business_context(
        self, personas: list[UserPersona], filters: dict[str, Any] | None
    ) -> list[UserPersona]:
        """Filter personas by business context."""
        if not filters:
            return personas

        filtered_personas = []
        for persona in personas:
            if self._matches_business_context(persona.business_context, filters):
                filtered_personas.append(persona)
        return filtered_personas

    def _matches_business_context(self, context: Any, filters: dict[str, Any]) -> bool:
        """Check if business context matches all filters."""
        for key, expected_value in filters.items():
            if not self._matches_context_field(context, key, expected_value):
                return False
        return True

    def _matches_context_field(
        self, context: Any, key: str, expected_value: Any
    ) -> bool:
        """Check if a specific context field matches the expected value."""
        if key in ("organization_id", "department", "region", "subscription_tier"):
            actual_value = getattr(context, key)
            return bool(actual_value == expected_value)
        elif key == "feature_flags":
            return self._matches_feature_flags(context.feature_flags, expected_value)
        elif key == "quota_limits":
            return self._matches_quota_limits(context.quota_limits, expected_value)
        elif key == "custom_attributes":
            return self._matches_custom_attributes(
                context.custom_attributes, expected_value
            )
        return False  # Unknown filter key - no match

    def _matches_feature_flags(self, flags: dict[str, Any], expected: Any) -> bool:
        """Check if feature flags match expected values."""
        if not isinstance(expected, dict):
            return False  # Invalid type - no match

        for flag, expected_value in expected.items():
            if flags.get(flag) != expected_value:
                return False
        return True

    def _matches_quota_limits(self, limits: dict[str, Any], expected: Any) -> bool:
        """Check if quota limits match expected values."""
        if not isinstance(expected, dict):
            return False  # Invalid type - no match

        for resource, expected_limit in expected.items():
            if limits.get(resource) != expected_limit:
                return False
        return True

    def _matches_custom_attributes(
        self, attributes: dict[str, Any], expected: Any
    ) -> bool:
        """Check if custom attributes match expected values."""
        if not isinstance(expected, dict):
            return False  # Invalid type - no match

        for attr, expected_val in expected.items():
            if attributes.get(attr) != expected_val:
                return False
        return True

    def create_session(self, persona_id: str) -> PersonaSession | None:
        """Create an authentication session for a persona.

        Args:
        ----
            persona_id: ID of persona to create session for

        Returns:
        -------
            PersonaSession if successful, None if persona not found

        """
        persona = self.get_persona(persona_id)
        if not persona:
            self._logger.warning(
                f"Cannot create session for unknown persona: {persona_id}"
            )
            return None

        session = PersonaSession(persona=persona)
        self._sessions[session.session_id] = session

        self._logger.info(
            f"Created session for persona: {persona.name} ({session.session_id[:8]})"
        )

        return session

    def get_session(self, session_id: str) -> PersonaSession | None:
        """Get a session by ID."""
        return self._sessions.get(session_id)

    def end_session(self, session_id: str) -> bool:
        """End an authentication session.

        Args:
        ----
            session_id: ID of session to end

        Returns:
        -------
            True if session was ended, False if not found

        """
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.logout()
        del self._sessions[session_id]

        self._logger.info(f"Ended session: {session_id[:8]}")
        return True

    def list_active_sessions(self) -> list[PersonaSession]:
        """Get all active authentication sessions."""
        return [
            session for session in self._sessions.values() if session.is_authenticated
        ]

    def cleanup_expired_sessions(self, timeout_minutes: int = 30) -> int:
        """Clean up expired sessions.

        Args:
        ----
            timeout_minutes: Session timeout in minutes

        Returns:
        -------
            Number of sessions cleaned up

        """
        expired_sessions = [
            session_id
            for session_id, session in self._sessions.items()
            if session.is_session_expired(timeout_minutes)
        ]

        for session_id in expired_sessions:
            self.end_session(session_id)

        if expired_sessions:
            self._logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

        return len(expired_sessions)

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about the persona pool."""
        active_personas = len([p for p in self._personas.values() if p.is_active])
        role_counts: dict[str, int] = {}

        for persona in self._personas.values():
            role = persona.role.value
            role_counts[role] = role_counts.get(role, 0) + 1

        return {
            "total_personas": len(self._personas),
            "active_personas": active_personas,
            "inactive_personas": len(self._personas) - active_personas,
            "active_sessions": len(self.list_active_sessions()),
            "total_sessions": len(self._sessions),
            "role_distribution": role_counts,
            "pool_name": self.name,
        }

    def clear(self) -> None:
        """Remove all personas and end all sessions."""
        # End all sessions
        session_ids = list(self._sessions.keys())
        for session_id in session_ids:
            self.end_session(session_id)

        # Clear personas
        persona_count = len(self._personas)
        self._personas.clear()

        self._logger.info(f"Cleared {persona_count} personas from pool")

        # Emit pool cleared event
        global_event_bus.emit(
            "persona.pool.cleared",
            {
                "pool_name": self.name,
                "personas_removed": persona_count,
            },
            source="PersonaPool",
        )

    def __len__(self) -> int:
        """Return number of personas in the pool."""
        return len(self._personas)

    def __contains__(self, persona_id: str) -> bool:
        """Check if persona ID exists in the pool."""
        return persona_id in self._personas

    def __iter__(self) -> Iterator[UserPersona]:
        """Iterate over personas in the pool."""
        return iter(self._personas.values())

    def __str__(self) -> str:
        """String representation of the persona pool."""
        return f"PersonaPool({self.name}, {len(self._personas)} personas)"
