"""TestAPIX authentication module.

This module provides persona-based authentication capabilities that enable
business-context-aware API testing. It includes user personas, permissions,
session management, and enhanced authentication providers.

It also provides backward compatibility with Phase 1 authentication providers.
"""

# Phase 2: Persona-based authentication
# Phase 2: Enhanced providers and session management
from testapix.auth.base import EnhancedAuthProvider, ProviderError, SessionConfig
from testapix.auth.factory import (
    create_api_key_provider,
    create_basic_auth_provider,
    create_bearer_token_provider,
    create_default_session_manager,
    create_oauth2_provider,
    create_session_config,
)

# Phase 1: Legacy compatibility providers
from testapix.auth.legacy import APIKeyAuth, AuthProvider, BearerTokenAuth
from testapix.auth.personas import (
    AuthenticationCredentials,
    AuthenticationMethod,
    BusinessContext,
    PersonaPool,
    PersonaRole,
    PersonaSession,
    UserPersona,
)
from testapix.auth.providers import (
    PersonaAPIKeyProvider,
    PersonaBasicAuthProvider,
    PersonaBearerTokenProvider,
    PersonaOAuth2Provider,
)
from testapix.auth.session import SessionManager

__all__ = [
    # Phase 2: Core persona system
    "UserPersona",
    "PersonaPool",
    "PersonaSession",
    "AuthenticationCredentials",
    "AuthenticationMethod",
    "BusinessContext",
    "PersonaRole",
    # Phase 2: Enhanced providers
    "EnhancedAuthProvider",
    "PersonaBearerTokenProvider",
    "PersonaAPIKeyProvider",
    "PersonaOAuth2Provider",
    "PersonaBasicAuthProvider",
    # Phase 2: Session management
    "SessionManager",
    "SessionConfig",
    # Phase 2: Factory functions
    "create_bearer_token_provider",
    "create_api_key_provider",
    "create_oauth2_provider",
    "create_basic_auth_provider",
    "create_default_session_manager",
    "create_session_config",
    # Phase 2: Exceptions
    "ProviderError",
    # Phase 1: Legacy compatibility
    "AuthProvider",
    "BearerTokenAuth",
    "APIKeyAuth",
]
