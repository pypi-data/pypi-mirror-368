"""Legacy authentication providers for backward compatibility.

This module provides Phase 1 compatible authentication providers that maintain
the original interface while being integrated into the new auth module structure.
These providers are used to maintain backward compatibility with existing code.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import httpx


class AuthProvider(ABC):
    """Abstract base class for authentication providers.

    This design allows for pluggable authentication strategies without
    changing the client code. Each provider knows how to:
    1. Apply authentication to requests
    2. Refresh credentials when needed
    3. Handle authentication failures

    This is the Phase 1 interface maintained for backward compatibility.
    """

    @abstractmethod
    async def apply_auth(self, request: httpx.Request) -> httpx.Request:
        """Apply authentication to a request.

        Args:
        ----
            request: The request to authenticate

        Returns:
        -------
            The authenticated request

        """
        pass

    async def refresh_if_needed(self) -> bool:
        """Refresh authentication if needed.

        Returns
        -------
            True if credentials were refreshed, False otherwise

        """
        return False

    async def handle_auth_failure(self, response: httpx.Response) -> bool:
        """Handle authentication failure.

        Args:
        ----
            response: The response indicating auth failure

        Returns:
        -------
            True if the failure was handled and request should be retried

        """
        return False


class BearerTokenAuth(AuthProvider):
    """Bearer token authentication provider.

    This is the most common authentication method for modern APIs.
    Tokens can be static or dynamic (with refresh logic).

    This is the Phase 1 implementation maintained for backward compatibility.
    """

    def __init__(self, token: str, token_prefix: str = "Bearer"):  # nosec B107
        """Initialize bearer token authentication.

        Args:
        ----
            token: The authentication token
            token_prefix: Prefix for the Authorization header (default: "Bearer")

        """
        self.token = token
        self.token_prefix = token_prefix

    async def apply_auth(self, request: httpx.Request) -> httpx.Request:
        """Apply bearer token to request."""
        request.headers["Authorization"] = f"{self.token_prefix} {self.token}"
        return request

    def update_token(self, new_token: str) -> None:
        """Update the token (useful for refresh scenarios)."""
        self.token = new_token


class APIKeyAuth(AuthProvider):
    """API Key authentication provider.

    Supports API key in headers with configurable header name.
    Some APIs use X-API-Key, others use custom headers.

    This is the Phase 1 implementation maintained for backward compatibility.
    """

    def __init__(self, api_key: str, header_name: str = "X-API-Key"):
        """Initialize API key authentication.

        Args:
        ----
            api_key: The API key value
            header_name: Name of the header to use

        """
        self.api_key = api_key
        self.header_name = header_name

    async def apply_auth(self, request: httpx.Request) -> httpx.Request:
        """Apply API key to request."""
        request.headers[self.header_name] = self.api_key
        return request


class BasicAuth(AuthProvider):
    """Basic authentication provider.

    Implements HTTP Basic Authentication using username and password.
    Credentials are base64 encoded and sent in the Authorization header.

    This is the Phase 1 implementation maintained for backward compatibility.
    """

    def __init__(self, username: str, password: str):
        """Initialize basic authentication.

        Args:
        ----
            username: Username for basic auth
            password: Password for basic auth

        """
        self.username = username
        self.password = password
        # Use httpx's built-in BasicAuth for encoding
        self._httpx_auth = httpx.BasicAuth(username, password)

    async def apply_auth(self, request: httpx.Request) -> httpx.Request:
        """Apply basic authentication to request."""
        # Use httpx BasicAuth to properly encode credentials
        auth_flow = self._httpx_auth.auth_flow(request)
        auth_request = next(auth_flow)
        return auth_request

    def update_credentials(self, username: str, password: str) -> None:
        """Update credentials (useful for changing login scenarios)."""
        self.username = username
        self.password = password
        self._httpx_auth = httpx.BasicAuth(username, password)
