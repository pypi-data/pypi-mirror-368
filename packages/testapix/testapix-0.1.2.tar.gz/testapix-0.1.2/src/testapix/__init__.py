r"""TestAPIX - Comprehensive Python API Testing Framework.

TestAPIX provides everything you need to build robust, maintainable API tests.
This package follows the principle of "convention over configuration" while
remaining flexible for advanced use cases.

Basic usage:
    from testapix import APIClient, assert_that

    # Async client (recommended)
    async with APIClient(base_url="https://api.example.com") as client:
        response = await client.get("/users")
        assert_that(response).has_status(200).has_json_path("users")

    # Sync client for simpler cases
    with SyncAPIClient(base_url="https://api.example.com") as client:
        response = client.get("/users")
        assert_that(response).has_status(200)

For more information, see the documentation at https://testapix.readthedocs.io
"""

# Version information - single source of truth
__version__ = "0.1.0"
__author__ = "TestAPIX Team"
__email__ = "team@testapix.dev"
__license__ = "MIT"

# Import core functionality to make it available at package level
# This creates a clean, intuitive API for users
from testapix.assertions import ResponseAssertion, assert_that
from testapix.auth import APIKeyAuth, AuthProvider, BearerTokenAuth
from testapix.core.batch_error_reporter import (
    BatchErrorAggregator,
    batch_operation,
    get_batch_aggregator,
)
from testapix.core.client import EnhancedResponse, HTTPClient, SyncHTTPClient
from testapix.core.config import TestAPIXConfig, get_current_config, load_config
from testapix.core.exceptions import (
    AuthenticationError,
    ConfigurationError,
    RequestError,
    ResponseValidationError,
    TestAPIXError,
)
from testapix.core.logging_utils import get_logger, setup_logging
from testapix.generators import BaseGenerator

# Create convenient aliases for the most common classes
# This allows both explicit (HTTPClient) and convenient (APIClient) naming
APIClient = HTTPClient
SyncAPIClient = SyncHTTPClient

# Define what's available when someone does "from testapix import *"
# We're explicit about exports to maintain a stable API
__all__ = [
    # Version and metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    # Client classes (both names for flexibility)
    "APIClient",
    "HTTPClient",
    "SyncAPIClient",
    "SyncHTTPClient",
    "EnhancedResponse",
    # Authentication providers
    "BearerTokenAuth",
    "APIKeyAuth",
    "AuthProvider",
    # Configuration management
    "load_config",
    "get_current_config",
    "TestAPIXConfig",
    # Exception types for proper error handling
    "TestAPIXError",
    "ConfigurationError",
    "AuthenticationError",
    "RequestError",
    "ResponseValidationError",
    # Assertion system
    "assert_that",
    "ResponseAssertion",
    # Enhanced logging and error handling
    "get_logger",
    "setup_logging",
    "BatchErrorAggregator",
    "batch_operation",
    "get_batch_aggregator",
    # Test data generation
    "BaseGenerator",
]


# Module-level initialization
# This could be used for one-time setup, but we keep it minimal
# to avoid import-time side effects
def _initialize() -> None:
    """Initialize the TestAPIX module.

    Currently no initialization needed, but this provides
    a hook for future needs without breaking changes.
    """
    pass


_initialize()
