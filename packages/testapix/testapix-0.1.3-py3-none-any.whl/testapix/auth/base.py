"""Base authentication interfaces and abstract classes.

This module defines the core authentication abstractions that enable
persona-aware authentication with business context support.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import timedelta

import httpx
from pydantic import BaseModel, ConfigDict, Field

from testapix.auth.personas import UserPersona
from testapix.core.events import global_event_bus
from testapix.core.exceptions import TestAPIXError

logger = logging.getLogger(__name__)


class ProviderError(TestAPIXError):
    """Raised when authentication provider operations fail."""

    def __init__(self, message: str, provider_type: str | None = None) -> None:
        super().__init__(message)
        self.provider_type = provider_type


class SessionConfig(BaseModel):
    """Configuration for session management."""

    model_config = ConfigDict(validate_assignment=True)

    session_timeout_minutes: int = Field(
        default=30, description="Session timeout in minutes", gt=0, le=1440
    )
    refresh_threshold_minutes: int = Field(
        default=5,
        description="Minutes before expiry to trigger refresh",
        gt=0,
        le=60,
    )
    max_refresh_retries: int = Field(
        default=3, description="Maximum refresh attempts", ge=0, le=10
    )
    auto_refresh_enabled: bool = Field(
        default=True, description="Enable automatic token refresh"
    )
    persistent_sessions: bool = Field(
        default=True, description="Enable persistent session storage"
    )


class EnhancedAuthProvider(ABC):
    """Enhanced authentication provider interface with persona support.

    This extends the Phase 1 AuthProvider interface to support:
    - Persona-aware authentication
    - Session management
    - Automatic credential refresh
    - Business context awareness
    """

    def __init__(
        self,
        session_config: SessionConfig | None = None,
        refresh_callback: Callable[[str], None] | None = None,
    ) -> None:
        """Initialize enhanced authentication provider.

        Args:
        ----
            session_config: Configuration for session management
            refresh_callback: Optional callback when credentials are refreshed

        """
        self.session_config = session_config or SessionConfig()
        self.refresh_callback = refresh_callback
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    async def authenticate_persona(self, persona: UserPersona) -> bool:
        """Authenticate a persona using their credentials.

        Args:
        ----
            persona: UserPersona to authenticate

        Returns:
        -------
            True if authentication successful, False otherwise

        """
        pass

    @abstractmethod
    async def apply_auth(
        self, request: httpx.Request, persona: UserPersona
    ) -> httpx.Request:
        """Apply persona authentication to a request.

        Args:
        ----
            request: Request to authenticate
            persona: UserPersona to use for authentication

        Returns:
        -------
            Authenticated request

        """
        pass

    @abstractmethod
    async def refresh_credentials(self, persona: UserPersona) -> bool:
        """Refresh persona credentials if possible.

        Args:
        ----
            persona: UserPersona whose credentials to refresh

        Returns:
        -------
            True if refresh successful, False otherwise

        """
        pass

    async def check_expiry(self, persona: UserPersona) -> bool:
        """Check if persona credentials are near expiry.

        Args:
        ----
            persona: UserPersona to check

        Returns:
        -------
            True if credentials need refresh, False otherwise

        """
        credentials = persona.auth_credentials
        if not credentials.expires_at:
            return False

        time_until_expiry = credentials.time_until_expiry()
        if not time_until_expiry:
            return False

        threshold = timedelta(minutes=self.session_config.refresh_threshold_minutes)
        return time_until_expiry <= threshold

    async def handle_auth_failure(
        self, response: httpx.Response, persona: UserPersona
    ) -> bool:
        """Handle authentication failure for a persona.

        Args:
        ----
            response: Response indicating auth failure
            persona: UserPersona that failed auth

        Returns:
        -------
            True if failure was handled and request should be retried

        """
        if response.status_code == 401:
            self._logger.warning(
                f"Authentication failed for persona {persona.name}. Attempting refresh."
            )

            # Emit authentication failure event
            global_event_bus.emit(
                "auth.persona.failed",
                {
                    "persona_id": persona.persona_id,
                    "persona_name": persona.name,
                    "status_code": response.status_code,
                    "response_data": response.text[:500],
                },
                source="EnhancedAuthProvider",
            )

            if self.session_config.auto_refresh_enabled:
                return await self.refresh_credentials(persona)

        return False

    def emit_refresh_event(self, persona: UserPersona, success: bool) -> None:
        """Emit credential refresh event."""
        event_type = (
            "auth.persona.refreshed" if success else "auth.persona.refresh_failed"
        )
        global_event_bus.emit(
            event_type,
            {
                "persona_id": persona.persona_id,
                "persona_name": persona.name,
                "auth_method": persona.auth_credentials.method.value,
            },
            source=self.__class__.__name__,
        )
