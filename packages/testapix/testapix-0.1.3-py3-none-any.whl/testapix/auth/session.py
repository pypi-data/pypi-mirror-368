"""Session management for persona-based authentication.

This module provides centralized session management with automatic refresh,
session persistence, and lifecycle management for authenticated personas.
"""

from __future__ import annotations

import logging
from typing import Any

from testapix.auth.base import EnhancedAuthProvider, SessionConfig
from testapix.auth.personas import AuthenticationMethod, PersonaSession, UserPersona
from testapix.core.events import global_event_bus

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages persistent authentication sessions for personas.

    Provides centralized session management with automatic refresh,
    session persistence, and lifecycle management.
    """

    def __init__(self, session_config: SessionConfig | None = None) -> None:
        """Initialize session manager.

        Args:
        ----
            session_config: Configuration for session management

        """
        self.session_config = session_config or SessionConfig()
        self._sessions: dict[str, PersonaSession] = {}
        self._providers: dict[AuthenticationMethod, EnhancedAuthProvider] = {}
        self._logger = logging.getLogger(f"{__name__}.SessionManager")

    def register_provider(
        self, auth_method: AuthenticationMethod, provider: EnhancedAuthProvider
    ) -> None:
        """Register an authentication provider for a specific method.

        Args:
        ----
            auth_method: Authentication method this provider handles
            provider: Authentication provider instance

        """
        self._providers[auth_method] = provider
        self._logger.info(f"Registered provider for {auth_method.value}")

    async def create_session(self, persona: UserPersona) -> PersonaSession | None:
        """Create and authenticate a session for a persona.

        Args:
        ----
            persona: UserPersona to create session for

        Returns:
        -------
            PersonaSession if successful, None otherwise

        """
        try:
            # Get appropriate provider
            provider = self._get_provider(persona.auth_credentials.method)
            if not provider:
                self._logger.error(
                    f"No provider registered for {persona.auth_credentials.method.value}"
                )
                return None

            # Authenticate persona
            if not await provider.authenticate_persona(persona):
                self._logger.error(f"Failed to authenticate persona {persona.name}")
                return None

            # Create session
            session = PersonaSession(persona=persona)
            session_authenticated = session.authenticate()
            if session_authenticated:
                self._sessions[session.session_id] = session
                self._logger.info(f"Created session for persona {persona.name}")

                # Emit session creation event
                global_event_bus.emit(
                    "auth.session.created",
                    {
                        "session_id": session.session_id,
                        "persona_id": persona.persona_id,
                        "persona_name": persona.name,
                        "auth_method": persona.auth_credentials.method.value,
                    },
                    source="SessionManager",
                )

                return session

            return None

        except Exception as e:
            self._logger.error(
                f"Failed to create session for persona {persona.name}: {e}"
            )
            return None

    async def get_session(self, session_id: str) -> PersonaSession | None:
        """Get an active session by ID.

        Args:
        ----
            session_id: Session ID to retrieve

        Returns:
        -------
            PersonaSession if found and active, None otherwise

        """
        session = self._sessions.get(session_id)
        if not session:
            return None

        # Check if session is expired
        if session.is_session_expired(self.session_config.session_timeout_minutes):
            await self.end_session(session_id)
            return None

        # Check if credentials need refresh
        if session.persona.auth_credentials.is_expired():
            provider = self._get_provider(session.persona.auth_credentials.method)
            if provider and self.session_config.auto_refresh_enabled:
                await provider.refresh_credentials(session.persona)

        return session

    async def end_session(self, session_id: str) -> bool:
        """End a session.

        Args:
        ----
            session_id: Session ID to end

        Returns:
        -------
            True if session was ended, False if not found

        """
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.logout()
        del self._sessions[session_id]

        self._logger.info(f"Ended session {session_id}")

        # Emit session end event
        global_event_bus.emit(
            "auth.session.ended",
            {
                "session_id": session_id,
                "persona_id": session.persona.persona_id,
                "persona_name": session.persona.name,
            },
            source="SessionManager",
        )

        return True

    async def refresh_session(self, session_id: str) -> bool:
        """Refresh credentials for a session.

        Args:
        ----
            session_id: Session ID to refresh

        Returns:
        -------
            True if refresh successful, False otherwise

        """
        session = self._sessions.get(session_id)
        if not session:
            return False

        provider = self._get_provider(session.persona.auth_credentials.method)
        if not provider:
            return False

        return await provider.refresh_credentials(session.persona)

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions.

        Returns
        -------
            Number of sessions cleaned up

        """
        expired_sessions = []
        timeout_minutes = self.session_config.session_timeout_minutes

        for session_id, session in self._sessions.items():
            if session.is_session_expired(timeout_minutes):
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            await self.end_session(session_id)

        if expired_sessions:
            self._logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

        return len(expired_sessions)

    def get_active_sessions(self) -> list[PersonaSession]:
        """Get all active sessions.

        Returns
        -------
            List of active PersonaSession objects

        """
        return [
            session
            for session in self._sessions.values()
            if session.is_authenticated
            and not session.is_session_expired(
                self.session_config.session_timeout_minutes
            )
        ]

    def get_sessions_for_persona(self, persona_id: str) -> list[PersonaSession]:
        """Get all sessions for a specific persona.

        Args:
        ----
            persona_id: Persona ID to search for

        Returns:
        -------
            List of PersonaSession objects for the persona

        """
        return [
            session
            for session in self._sessions.values()
            if session.persona.persona_id == persona_id
        ]

    async def end_all_sessions_for_persona(self, persona_id: str) -> int:
        """End all sessions for a specific persona.

        Args:
        ----
            persona_id: Persona ID whose sessions to end

        Returns:
        -------
            Number of sessions ended

        """
        sessions_to_end = [
            session.session_id
            for session in self._sessions.values()
            if session.persona.persona_id == persona_id
        ]

        for session_id in sessions_to_end:
            await self.end_session(session_id)

        return len(sessions_to_end)

    async def refresh_all_sessions(self) -> dict[str, bool]:
        """Refresh credentials for all active sessions.

        Returns
        -------
            Dictionary mapping session IDs to refresh success status

        """
        results = {}

        for session_id, session in self._sessions.items():
            if session.is_authenticated:
                provider = self._get_provider(session.persona.auth_credentials.method)
                if provider:
                    success = await provider.refresh_credentials(session.persona)
                    results[session_id] = success
                else:
                    results[session_id] = False

        return results

    def get_session_stats(self) -> dict[str, Any]:
        """Get session statistics.

        Returns
        -------
            Dictionary with session statistics

        """
        active_sessions = self.get_active_sessions()

        # Group sessions by authentication method
        method_counts: dict[str, int] = {}
        for session in self._sessions.values():
            method = session.persona.auth_credentials.method.value
            method_counts[method] = method_counts.get(method, 0) + 1

        return {
            "total_sessions": len(self._sessions),
            "active_sessions": len(active_sessions),
            "registered_providers": len(self._providers),
            "provider_types": [method.value for method in self._providers],
            "session_timeout_minutes": self.session_config.session_timeout_minutes,
            "auto_refresh_enabled": self.session_config.auto_refresh_enabled,
            "sessions_by_auth_method": method_counts,
        }

    async def validate_all_sessions(self) -> dict[str, dict[str, Any]]:
        """Validate all sessions and their credentials.

        Returns
        -------
            Dictionary mapping session IDs to validation results

        """
        results = {}

        for session_id, session in self._sessions.items():
            provider = self._get_provider(session.persona.auth_credentials.method)

            validation_result = {
                "session_valid": not session.is_session_expired(
                    self.session_config.session_timeout_minutes
                ),
                "credentials_valid": not session.persona.auth_credentials.is_expired(),
                "provider_available": provider is not None,
                "is_authenticated": session.is_authenticated,
                "persona_active": session.persona.is_active,
            }

            # Overall session health
            validation_result["healthy"] = all(
                [
                    validation_result["session_valid"],
                    validation_result["credentials_valid"],
                    validation_result["provider_available"],
                    validation_result["is_authenticated"],
                    validation_result["persona_active"],
                ]
            )

            results[session_id] = validation_result

        return results

    def _get_provider(
        self, auth_method: AuthenticationMethod
    ) -> EnhancedAuthProvider | None:
        """Get provider for authentication method."""
        return self._providers.get(auth_method)

    def __len__(self) -> int:
        """Return total number of sessions."""
        return len(self._sessions)

    def __contains__(self, session_id: str) -> bool:
        """Check if session ID exists."""
        return session_id in self._sessions

    def __str__(self) -> str:
        """String representation of session manager."""
        active_count = len(self.get_active_sessions())
        return f"SessionManager({len(self._sessions)} total, {active_count} active)"
