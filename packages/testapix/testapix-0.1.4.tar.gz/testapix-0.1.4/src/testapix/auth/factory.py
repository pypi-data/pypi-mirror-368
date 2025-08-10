"""Factory functions and convenience methods for authentication providers.

This module provides easy-to-use factory functions for creating authentication
providers and session managers with sensible defaults.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from testapix.auth.base import SessionConfig
from testapix.auth.personas import AuthenticationMethod
from testapix.auth.providers import (
    PersonaAPIKeyProvider,
    PersonaBasicAuthProvider,
    PersonaBearerTokenProvider,
    PersonaOAuth2Provider,
)
from testapix.auth.session import SessionManager


def create_bearer_token_provider(
    token_refresh_url: str | None = None,
    session_config: SessionConfig | None = None,
    refresh_callback: Callable[[str], None] | None = None,
) -> PersonaBearerTokenProvider:
    """Create a bearer token provider with default configuration.

    Args:
    ----
        token_refresh_url: Optional URL for token refresh
        session_config: Optional session configuration
        refresh_callback: Optional callback when token is refreshed

    Returns:
    -------
        Configured PersonaBearerTokenProvider

    Examples:
    --------
        # Basic bearer token provider
        provider = create_bearer_token_provider()

        # With token refresh support
        provider = create_bearer_token_provider(
            token_refresh_url="https://api.example.com/auth/refresh"
        )

        # With custom session config
        config = SessionConfig(session_timeout_minutes=60)
        provider = create_bearer_token_provider(session_config=config)

    """
    return PersonaBearerTokenProvider(
        token_refresh_url=token_refresh_url,
        session_config=session_config,
        refresh_callback=refresh_callback,
    )


def create_api_key_provider(
    session_config: SessionConfig | None = None,
    refresh_callback: Callable[[str], None] | None = None,
) -> PersonaAPIKeyProvider:
    """Create an API key provider with default configuration.

    Args:
    ----
        session_config: Optional session configuration
        refresh_callback: Optional callback (not typically used for API keys)

    Returns:
    -------
        Configured PersonaAPIKeyProvider

    Examples:
    --------
        # Basic API key provider
        provider = create_api_key_provider()

        # With custom session config
        config = SessionConfig(persistent_sessions=False)
        provider = create_api_key_provider(session_config=config)

    """
    return PersonaAPIKeyProvider(
        session_config=session_config,
        refresh_callback=refresh_callback,
    )


def create_oauth2_provider(
    client_id: str,
    client_secret: str,
    token_url: str,
    session_config: SessionConfig | None = None,
    refresh_callback: Callable[[str], None] | None = None,
) -> PersonaOAuth2Provider:
    """Create an OAuth2 provider with default configuration.

    Args:
    ----
        client_id: OAuth2 client ID
        client_secret: OAuth2 client secret
        token_url: OAuth2 token endpoint URL
        session_config: Optional session configuration
        refresh_callback: Optional callback when token is refreshed

    Returns:
    -------
        Configured PersonaOAuth2Provider

    Examples:
    --------
        # Basic OAuth2 provider
        provider = create_oauth2_provider(
            client_id="your-client-id",
            client_secret="your-client-secret",
            token_url="https://auth.example.com/oauth/token"
        )

        # With custom session config and callback
        def token_refreshed(new_token: str) -> None:
            print(f"Token refreshed: {new_token[:10]}...")

        config = SessionConfig(auto_refresh_enabled=True, refresh_threshold_minutes=10)
        provider = create_oauth2_provider(
            client_id="your-client-id",
            client_secret="your-client-secret",
            token_url="https://auth.example.com/oauth/token",
            session_config=config,
            refresh_callback=token_refreshed,
        )

    """
    return PersonaOAuth2Provider(
        client_id=client_id,
        client_secret=client_secret,
        token_url=token_url,
        session_config=session_config,
        refresh_callback=refresh_callback,
    )


def create_basic_auth_provider(
    session_config: SessionConfig | None = None,
    refresh_callback: Callable[[str], None] | None = None,
) -> PersonaBasicAuthProvider:
    """Create a basic authentication provider with default configuration.

    Args:
    ----
        session_config: Optional session configuration
        refresh_callback: Optional callback (not typically used for basic auth)

    Returns:
    -------
        Configured PersonaBasicAuthProvider

    Examples:
    --------
        # Basic auth provider
        provider = create_basic_auth_provider()

        # With custom session config
        config = SessionConfig(session_timeout_minutes=15)
        provider = create_basic_auth_provider(session_config=config)

    """
    return PersonaBasicAuthProvider(
        session_config=session_config,
        refresh_callback=refresh_callback,
    )


def create_default_session_manager(
    session_config: SessionConfig | None = None,
) -> SessionManager:
    """Create a session manager with default providers registered.

    This is a convenience function that creates a SessionManager with
    standard authentication providers pre-registered for common use cases.

    Args:
    ----
        session_config: Optional session configuration

    Returns:
    -------
        SessionManager with default providers registered

    Examples:
    --------
        # Basic session manager with defaults
        session_manager = create_default_session_manager()

        # With custom session config
        config = SessionConfig(
            session_timeout_minutes=60,
            auto_refresh_enabled=True,
            refresh_threshold_minutes=5
        )
        session_manager = create_default_session_manager(session_config=config)

    """
    session_manager = SessionManager(session_config)

    # Register default providers
    session_manager.register_provider(
        AuthenticationMethod.BEARER_TOKEN,
        create_bearer_token_provider(session_config=session_config),
    )
    session_manager.register_provider(
        AuthenticationMethod.API_KEY,
        create_api_key_provider(session_config=session_config),
    )
    session_manager.register_provider(
        AuthenticationMethod.BASIC_AUTH,
        create_basic_auth_provider(session_config=session_config),
    )

    return session_manager


def create_custom_session_manager(
    providers: dict[AuthenticationMethod, tuple[type, dict[Any, Any]]] | None = None,
    session_config: SessionConfig | None = None,
) -> SessionManager:
    """Create a session manager with custom provider configuration.

    Args:
    ----
        providers: Dictionary mapping auth methods to (provider_class, kwargs) tuples
        session_config: Optional session configuration

    Returns:
    -------
        SessionManager with custom providers registered

    Examples:
    --------
        # Custom OAuth2 configuration
        providers = {
            AuthenticationMethod.OAUTH2: (
                PersonaOAuth2Provider,
                {
                    "client_id": "my-client-id",
                    "client_secret": "my-client-secret",
                    "token_url": "https://auth.example.com/token",
                }
            ),
            AuthenticationMethod.BEARER_TOKEN: (
                PersonaBearerTokenProvider,
                {
                    "token_refresh_url": "https://api.example.com/refresh",
                }
            ),
        }

        session_manager = create_custom_session_manager(providers=providers)

    """
    session_manager = SessionManager(session_config)

    if providers:
        for auth_method, (provider_class, kwargs) in providers.items():
            if session_config and "session_config" not in kwargs:
                kwargs["session_config"] = session_config
            provider = provider_class(**kwargs)
            session_manager.register_provider(auth_method, provider)

    return session_manager


def create_session_config(
    session_timeout_minutes: int = 30,
    refresh_threshold_minutes: int = 5,
    max_refresh_retries: int = 3,
    auto_refresh_enabled: bool = True,
    persistent_sessions: bool = True,
) -> SessionConfig:
    """Create a session configuration with specified parameters.

    Args:
    ----
        session_timeout_minutes: Session timeout in minutes
        refresh_threshold_minutes: Minutes before expiry to trigger refresh
        max_refresh_retries: Maximum refresh attempts
        auto_refresh_enabled: Enable automatic token refresh
        persistent_sessions: Enable persistent session storage

    Returns:
    -------
        Configured SessionConfig

    Examples:
    --------
        # Conservative configuration
        config = create_session_config(
            session_timeout_minutes=15,
            refresh_threshold_minutes=2,
            auto_refresh_enabled=True
        )

        # High-performance configuration
        config = create_session_config(
            session_timeout_minutes=120,
            refresh_threshold_minutes=10,
            max_refresh_retries=5,
            persistent_sessions=True
        )

    """
    return SessionConfig(
        session_timeout_minutes=session_timeout_minutes,
        refresh_threshold_minutes=refresh_threshold_minutes,
        max_refresh_retries=max_refresh_retries,
        auto_refresh_enabled=auto_refresh_enabled,
        persistent_sessions=persistent_sessions,
    )


# Convenience aliases for common configurations
def create_testing_session_config() -> SessionConfig:
    """Create session config optimized for testing scenarios."""
    return create_session_config(
        session_timeout_minutes=10,  # Short timeout for faster test cycles
        refresh_threshold_minutes=1,  # Quick refresh for testing
        max_refresh_retries=2,  # Fewer retries to fail fast
        auto_refresh_enabled=True,
        persistent_sessions=False,  # Don't persist test sessions
    )


def create_production_session_config() -> SessionConfig:
    """Create session config optimized for production use."""
    return create_session_config(
        session_timeout_minutes=60,  # Longer timeout for production
        refresh_threshold_minutes=10,  # Conservative refresh timing
        max_refresh_retries=5,  # More retries for reliability
        auto_refresh_enabled=True,
        persistent_sessions=True,  # Persist production sessions
    )


def create_development_session_config() -> SessionConfig:
    """Create session config optimized for development use."""
    return create_session_config(
        session_timeout_minutes=30,  # Reasonable timeout
        refresh_threshold_minutes=5,  # Standard refresh timing
        max_refresh_retries=3,  # Standard retry count
        auto_refresh_enabled=True,
        persistent_sessions=True,  # Convenient for development
    )
