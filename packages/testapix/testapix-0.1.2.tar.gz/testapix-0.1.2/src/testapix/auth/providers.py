"""Concrete authentication provider implementations.

This module provides persona-aware authentication providers for different
authentication methods including Bearer tokens, API keys, and OAuth2.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime, timedelta

import httpx

from testapix.auth.base import EnhancedAuthProvider, ProviderError, SessionConfig
from testapix.auth.personas import AuthenticationMethod, UserPersona
from testapix.core.events import global_event_bus

logger = logging.getLogger(__name__)


class PersonaBearerTokenProvider(EnhancedAuthProvider):
    """Bearer token authentication provider for personas."""

    def __init__(
        self,
        token_refresh_url: str | None = None,
        session_config: SessionConfig | None = None,
        refresh_callback: Callable[[str], None] | None = None,
    ) -> None:
        """Initialize persona bearer token provider.

        Args:
        ----
            token_refresh_url: URL for token refresh (optional)
            session_config: Session configuration
            refresh_callback: Callback when token is refreshed

        """
        super().__init__(session_config, refresh_callback)
        self.token_refresh_url = token_refresh_url

    async def authenticate_persona(self, persona: UserPersona) -> bool:
        """Authenticate persona with bearer token."""
        try:
            credentials = persona.auth_credentials
            if credentials.method != AuthenticationMethod.BEARER_TOKEN:
                raise ProviderError(
                    f"Expected bearer token credentials, got {credentials.method.value}",
                    provider_type="PersonaBearerTokenProvider",
                )

            token = credentials.get_credential("token")
            if not token:
                self._logger.error(f"No bearer token found for persona {persona.name}")
                return False

            # Check if token is expired
            if credentials.is_expired():
                self._logger.warning(f"Bearer token expired for persona {persona.name}")
                if self.session_config.auto_refresh_enabled:
                    return await self.refresh_credentials(persona)
                return False

            self._logger.info(
                f"Successfully authenticated persona {persona.name} with bearer token"
            )

            # Emit authentication success event
            global_event_bus.emit(
                "auth.persona.authenticated",
                {
                    "persona_id": persona.persona_id,
                    "persona_name": persona.name,
                    "auth_method": "bearer_token",
                },
                source="PersonaBearerTokenProvider",
            )

            return True

        except ProviderError:
            # Re-raise ProviderError to caller - these are expected validation errors
            raise
        except Exception as e:
            self._logger.error(
                f"Bearer token authentication failed for persona {persona.name}: {e}"
            )
            return False

    async def apply_auth(
        self, request: httpx.Request, persona: UserPersona
    ) -> httpx.Request:
        """Apply bearer token authentication to request."""
        credentials = persona.auth_credentials
        token = credentials.get_credential("token")
        token_prefix = credentials.get_credential("token_prefix") or "Bearer"

        if token:
            request.headers["Authorization"] = f"{token_prefix} {token}"

        return request

    async def refresh_credentials(self, persona: UserPersona) -> bool:
        """Refresh bearer token credentials."""
        try:
            credentials = persona.auth_credentials
            refresh_token = credentials.refresh_token

            if not refresh_token or not self.token_refresh_url:
                self._logger.debug(
                    f"Cannot refresh token for persona {persona.name}: missing refresh token or URL"
                )
                return False

            # Make refresh request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_refresh_url,
                    json={"refresh_token": refresh_token},
                    timeout=30.0,
                )

                if response.status_code == 200:
                    token_data = response.json()
                    new_token = token_data.get("access_token")
                    new_refresh_token = token_data.get("refresh_token")
                    expires_in = token_data.get("expires_in", 3600)

                    if new_token:
                        # Update credentials
                        credentials.set_credential("token", new_token)
                        if new_refresh_token:
                            credentials.refresh_token = new_refresh_token
                        credentials.expires_at = datetime.now() + timedelta(
                            seconds=expires_in
                        )

                        # Update persona
                        persona.update_credentials(credentials)

                        self._logger.info(
                            f"Successfully refreshed token for persona {persona.name}"
                        )

                        # Trigger callback if provided
                        if self.refresh_callback:
                            self.refresh_callback(new_token)

                        self.emit_refresh_event(persona, success=True)
                        return True

            self._logger.error(f"Token refresh failed for persona {persona.name}")
            self.emit_refresh_event(persona, success=False)
            return False

        except Exception as e:
            self._logger.error(f"Token refresh error for persona {persona.name}: {e}")
            self.emit_refresh_event(persona, success=False)
            return False


class PersonaAPIKeyProvider(EnhancedAuthProvider):
    """API Key authentication provider for personas."""

    async def authenticate_persona(self, persona: UserPersona) -> bool:
        """Authenticate persona with API key."""
        try:
            credentials = persona.auth_credentials
            if credentials.method != AuthenticationMethod.API_KEY:
                raise ProviderError(
                    f"Expected API key credentials, got {credentials.method.value}",
                    provider_type="PersonaAPIKeyProvider",
                )

            api_key = credentials.get_credential("api_key")
            if not api_key:
                self._logger.error(f"No API key found for persona {persona.name}")
                return False

            self._logger.info(
                f"Successfully authenticated persona {persona.name} with API key"
            )

            # Emit authentication success event
            global_event_bus.emit(
                "auth.persona.authenticated",
                {
                    "persona_id": persona.persona_id,
                    "persona_name": persona.name,
                    "auth_method": "api_key",
                },
                source="PersonaAPIKeyProvider",
            )

            return True

        except ProviderError:
            # Re-raise ProviderError to caller - these are expected validation errors
            raise
        except Exception as e:
            self._logger.error(
                f"API key authentication failed for persona {persona.name}: {e}"
            )
            return False

    async def apply_auth(
        self, request: httpx.Request, persona: UserPersona
    ) -> httpx.Request:
        """Apply API key authentication to request."""
        credentials = persona.auth_credentials
        api_key = credentials.get_credential("api_key")
        header_name = credentials.get_credential("header_name") or "X-API-Key"

        if api_key:
            request.headers[header_name] = api_key

        return request

    async def refresh_credentials(self, persona: UserPersona) -> bool:
        """API keys typically don't expire, so no refresh needed."""
        self._logger.debug(f"API key refresh not needed for persona {persona.name}")
        return True


class PersonaOAuth2Provider(EnhancedAuthProvider):
    """OAuth2 authentication provider for personas."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_url: str,
        session_config: SessionConfig | None = None,
        refresh_callback: Callable[[str], None] | None = None,
    ) -> None:
        """Initialize OAuth2 provider.

        Args:
        ----
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            token_url: OAuth2 token endpoint URL
            session_config: Session configuration
            refresh_callback: Callback when token is refreshed

        """
        super().__init__(session_config, refresh_callback)
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url

    async def authenticate_persona(self, persona: UserPersona) -> bool:
        """Authenticate persona with OAuth2."""
        try:
            credentials = persona.auth_credentials
            if credentials.method != AuthenticationMethod.OAUTH2:
                raise ProviderError(
                    f"Expected OAuth2 credentials, got {credentials.method.value}",
                    provider_type="PersonaOAuth2Provider",
                )

            access_token = credentials.get_credential("access_token")
            if not access_token:
                # Try to get initial token
                return await self._obtain_initial_token(persona)

            # Check if token is expired
            if credentials.is_expired():
                self._logger.warning(f"OAuth2 token expired for persona {persona.name}")
                if self.session_config.auto_refresh_enabled:
                    return await self.refresh_credentials(persona)
                return False

            self._logger.info(
                f"Successfully authenticated persona {persona.name} with OAuth2"
            )

            # Emit authentication success event
            global_event_bus.emit(
                "auth.persona.authenticated",
                {
                    "persona_id": persona.persona_id,
                    "persona_name": persona.name,
                    "auth_method": "oauth2",
                },
                source="PersonaOAuth2Provider",
            )

            return True

        except ProviderError:
            # Re-raise ProviderError to caller - these are expected validation errors
            raise
        except Exception as e:
            self._logger.error(
                f"OAuth2 authentication failed for persona {persona.name}: {e}"
            )
            return False

    async def apply_auth(
        self, request: httpx.Request, persona: UserPersona
    ) -> httpx.Request:
        """Apply OAuth2 authentication to request."""
        credentials = persona.auth_credentials
        access_token = credentials.get_credential("access_token")
        token_type = credentials.get_credential("token_type") or "Bearer"

        if access_token:
            request.headers["Authorization"] = f"{token_type} {access_token}"

        return request

    async def refresh_credentials(self, persona: UserPersona) -> bool:
        """Refresh OAuth2 access token."""
        try:
            credentials = persona.auth_credentials
            refresh_token = credentials.refresh_token

            if not refresh_token:
                self._logger.debug(
                    f"No refresh token available for persona {persona.name}"
                )
                return False

            # Make token refresh request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_url,
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=30.0,
                )

                if response.status_code == 200:
                    token_data = response.json()
                    new_access_token = token_data.get("access_token")
                    new_refresh_token = token_data.get("refresh_token")
                    expires_in = token_data.get("expires_in", 3600)
                    token_type = token_data.get("token_type", "Bearer")

                    if new_access_token:
                        # Update credentials
                        credentials.set_credential("access_token", new_access_token)
                        credentials.set_credential("token_type", token_type)
                        if new_refresh_token:
                            credentials.refresh_token = new_refresh_token
                        credentials.expires_at = datetime.now() + timedelta(
                            seconds=expires_in
                        )

                        # Update persona
                        persona.update_credentials(credentials)

                        self._logger.info(
                            f"Successfully refreshed OAuth2 token for persona {persona.name}"
                        )

                        # Trigger callback if provided
                        if self.refresh_callback:
                            self.refresh_callback(new_access_token)

                        self.emit_refresh_event(persona, success=True)
                        return True

            self._logger.error(
                f"OAuth2 token refresh failed for persona {persona.name}"
            )
            self.emit_refresh_event(persona, success=False)
            return False

        except Exception as e:
            self._logger.error(
                f"OAuth2 token refresh error for persona {persona.name}: {e}"
            )
            self.emit_refresh_event(persona, success=False)
            return False

    async def _obtain_initial_token(self, persona: UserPersona) -> bool:
        """Obtain initial OAuth2 token using client credentials."""
        try:
            # Use client credentials grant for service-to-service authentication
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_url,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=30.0,
                )

                if response.status_code == 200:
                    token_data = response.json()
                    access_token = token_data.get("access_token")
                    expires_in = token_data.get("expires_in", 3600)
                    token_type = token_data.get("token_type", "Bearer")
                    refresh_token = token_data.get("refresh_token")

                    if access_token:
                        # Update credentials
                        credentials = persona.auth_credentials
                        credentials.set_credential("access_token", access_token)
                        credentials.set_credential("token_type", token_type)
                        if refresh_token:
                            credentials.refresh_token = refresh_token
                        credentials.expires_at = datetime.now() + timedelta(
                            seconds=expires_in
                        )

                        # Update persona
                        persona.update_credentials(credentials)

                        self._logger.info(
                            f"Successfully obtained initial OAuth2 token for persona {persona.name}"
                        )
                        return True

            self._logger.error(
                f"Failed to obtain initial OAuth2 token for persona {persona.name}"
            )
            return False

        except Exception as e:
            self._logger.error(
                f"Error obtaining initial OAuth2 token for persona {persona.name}: {e}"
            )
            return False


class PersonaBasicAuthProvider(EnhancedAuthProvider):
    """Basic authentication provider for personas."""

    async def authenticate_persona(self, persona: UserPersona) -> bool:
        """Authenticate persona with basic auth."""
        try:
            credentials = persona.auth_credentials
            if credentials.method != AuthenticationMethod.BASIC_AUTH:
                raise ProviderError(
                    f"Expected basic auth credentials, got {credentials.method.value}",
                    provider_type="PersonaBasicAuthProvider",
                )

            username = credentials.get_credential("username")
            password = credentials.get_credential("password")

            if not username or not password:
                self._logger.error(
                    f"Missing username or password for persona {persona.name}"
                )
                return False

            self._logger.info(
                f"Successfully authenticated persona {persona.name} with basic auth"
            )

            # Emit authentication success event
            global_event_bus.emit(
                "auth.persona.authenticated",
                {
                    "persona_id": persona.persona_id,
                    "persona_name": persona.name,
                    "auth_method": "basic_auth",
                },
                source="PersonaBasicAuthProvider",
            )

            return True

        except ProviderError:
            # Re-raise ProviderError to caller - these are expected validation errors
            raise
        except Exception as e:
            self._logger.error(
                f"Basic auth authentication failed for persona {persona.name}: {e}"
            )
            return False

    async def apply_auth(
        self, request: httpx.Request, persona: UserPersona
    ) -> httpx.Request:
        """Apply basic auth authentication to request."""
        credentials = persona.auth_credentials
        username = credentials.get_credential("username")
        password = credentials.get_credential("password")

        if username and password:
            import base64

            auth_string = base64.b64encode(f"{username}:{password}".encode()).decode()
            request.headers["Authorization"] = f"Basic {auth_string}"

        return request

    async def refresh_credentials(self, persona: UserPersona) -> bool:
        """Basic auth credentials typically don't expire."""
        self._logger.debug(f"Basic auth refresh not needed for persona {persona.name}")
        return True
