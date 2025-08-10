"""TestAPIX HTTP Client.

This module provides the core HTTP client functionality for TestAPIX. The client
is built on top of httpx but adds API testing-specific features:

1. Enhanced Response Objects: Responses include testing methods like json_path()
2. Automatic Retries: Configurable retry logic for handling transient failures
3. Authentication Management: Pluggable authentication with automatic token refresh
4. Request/Response Logging: Detailed logging for debugging test failures
5. Synchronous and Asynchronous: Support both programming styles

The design philosophy prioritizes testing needs over general HTTP usage. Every
feature is designed to make API testing more effective and debugging easier.
"""

import asyncio
import logging
import time
from collections.abc import Mapping
from typing import Any, TypeVar
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, ConfigDict, Field

# Import authentication providers from auth module (for backward compatibility)
# These are re-exported here to maintain the existing API
from testapix.auth.legacy import APIKeyAuth, AuthProvider, BearerTokenAuth

from .exceptions import AuthenticationError, RequestError, TimeoutError
from .logging_utils import get_logger

# Type variable for generic response handling
T = TypeVar("T")

# Configure logging with enhanced TestAPIX logger
logger = get_logger(__name__)


class RequestConfig(BaseModel):
    """Configuration for individual requests.

    This configuration can be set at the client level (as defaults) or
    overridden for specific requests. The defaults are chosen based on
    typical API testing needs.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    timeout: float = Field(
        default=30.0,
        description="Request timeout in seconds. 30s is generous for most APIs.",
        gt=0,
    )
    retries: int = Field(
        default=3, description="Number of retry attempts for failed requests", ge=0
    )
    retry_delay: float = Field(
        default=1.0, description="Base delay between retries in seconds", ge=0
    )
    retry_backoff: float = Field(
        default=2.0,
        description="Backoff multiplier for exponential retry delay",
        ge=1.0,
    )
    follow_redirects: bool = Field(
        default=True, description="Whether to automatically follow HTTP redirects"
    )
    verify_ssl: bool = Field(
        default=True, description="Whether to verify SSL certificates"
    )


# Authentication providers are now imported from testapix.auth.legacy above
# This maintains backward compatibility while centralizing auth code


class EnhancedResponse:
    """Enhanced response wrapper that adds testing-specific functionality.

    This wraps httpx.Response to provide methods commonly needed in API testing:
    - Easy JSON path extraction
    - Response time tracking
    - Convenient data access methods

    The wrapper delegates unknown attributes to the underlying response,
    so it can be used wherever httpx.Response is expected.
    """

    def __init__(self, response: httpx.Response, request_start_time: float):
        """Initialize enhanced response.

        Args:
        ----
            response: The httpx response to wrap
            request_start_time: Unix timestamp when request started

        """
        self._response = response
        self.request_start_time = request_start_time
        self.response_time = time.time() - request_start_time
        self._json_cache: dict[str, Any] | None = None

    def __getattr__(self, name: str) -> Any:
        """Delegate unknown attributes to wrapped response."""
        return getattr(self._response, name)

    def __repr__(self) -> str:
        """Provide helpful representation for debugging."""
        return (
            f"<EnhancedResponse [{self._response.status_code}] "
            f"{self._response.request.method} {self._response.request.url}>"
        )

    @property
    def ok(self) -> bool:
        """Check if response has successful status code (2xx)."""
        return bool(200 <= self._response.status_code < 300)

    @property
    def json_data(self) -> dict[str, Any]:
        """Get JSON data with caching and better error messages.

        Returns
        -------
            Parsed JSON data

        Raises
        ------
            RequestError: If response is not valid JSON

        """
        if self._json_cache is None:
            try:
                self._json_cache = self._response.json()
            except Exception as e:
                # Provide helpful error message with response preview
                preview = self._response.text[:500]
                if len(self._response.text) > 500:
                    preview += "..."

                raise RequestError(
                    f"Failed to parse response as JSON: {e}",
                    response_data={
                        "content_preview": preview,
                        "content_type": self._response.headers.get(
                            "content-type", "unknown"
                        ),
                        "status_code": self._response.status_code,
                    },
                )
        return self._json_cache

    def json_path(self, path: str, default: Any = None) -> Any:
        """Extract data using a simple JSON path syntax.

        Supports:
        - Nested access: "user.profile.name"
        - Array access: "users[0].email"
        - Mixed: "data.users[0].addresses[1].city"

        Args:
        ----
            path: JSON path string
            default: Value to return if path not found

        Returns:
        -------
            Value at the path or default if not found

        Examples:
        --------
            response.json_path("user.name")  # {"user": {"name": "John"}}
            response.json_path("items[0].id")  # {"items": [{"id": 1}]}

        """
        try:
            current: Any = self.json_data
            parts = path.split(".")
            for part in parts:
                if "[" in part and part.endswith("]"):
                    key, index_str = part.split("[", 1)
                    index_str = index_str.rstrip("]")
                    if key:
                        if not isinstance(current, dict):
                            raise KeyError(
                                f"Expected dict for key access, got {type(current)}"
                            )
                        current = current[key]
                    if not isinstance(current, list):
                        raise KeyError(
                            f"Cannot index non-list with int: {type(current)}"
                        )
                    index = int(index_str)
                    current = current[index]
                else:
                    if not isinstance(current, dict):
                        raise KeyError(
                            f"Expected dict for key access, got {type(current)}"
                        )
                    current = current[part]
            return current
        except (KeyError, IndexError, TypeError, AttributeError):
            return default

    def has_json_path(self, path: str) -> bool:
        """Check if a JSON path exists in the response.

        Args:
        ----
            path: JSON path to check

        Returns:
        -------
            True if path exists, False otherwise

        """
        sentinel = object()  # Unique object to distinguish from None
        return self.json_path(path, default=sentinel) is not sentinel


class HTTPClient:
    """Enhanced HTTP client for API testing.

    This client provides a high-level interface for making HTTP requests with
    features specifically designed for API testing:

    - Automatic retry logic with exponential backoff
    - Pluggable authentication with refresh support
    - Enhanced responses with testing utilities
    - Comprehensive logging for debugging
    - Configurable timeouts and behaviors

    The client can be used as a context manager for proper cleanup:
        async with HTTPClient(base_url="https://api.example.com") as client:
            response = await client.get("/users")
    """

    def __init__(
        self,
        base_url: str | None = None,
        default_headers: dict[str, str] | None = None,
        request_config: RequestConfig | None = None,
        auth_provider: AuthProvider | None = None,
        logger: logging.Logger | None = None,
    ):
        """Initialize HTTP client.

        Args:
        ----
            base_url: Base URL for all requests (can be overridden per request)
            default_headers: Headers to include in all requests
            request_config: Default request configuration
            auth_provider: Authentication provider
            logger: Logger instance (uses module logger by default)

        """
        self.base_url = base_url or ""
        self.default_headers = default_headers or {}
        self.request_config = request_config or RequestConfig()
        self.auth_provider = auth_provider
        self.logger = logger or logging.getLogger(__name__)

        # Create underlying httpx client with appropriate settings
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.request_config.timeout),
            follow_redirects=self.request_config.follow_redirects,
            verify=self.request_config.verify_ssl,
            headers=self.default_headers,
        )

        # Track if we're in a context manager
        self._in_context = False

    def set_auth(self, auth_provider: AuthProvider) -> None:
        """Set or update the authentication provider."""
        self.auth_provider = auth_provider

    def set_default_header(self, name: str, value: str) -> None:
        """Add or update a default header."""
        self.default_headers[name] = value
        self._client.headers[name] = value

    async def close(self) -> None:
        """Close the underlying HTTP client and release resources."""
        await self._client.aclose()

    async def __aenter__(self) -> "HTTPClient":
        """Enter context manager."""
        self._in_context = True
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Exit context manager and cleanup."""
        self._in_context = False
        await self.close()

    def _build_url(self, path: str) -> str:
        """Build full URL from base URL and path.

        Handles:
        - Absolute URLs (returned as-is)
        - Relative paths (combined with base_url)
        - Path joining edge cases

        Args:
        ----
            path: URL path or full URL

        Returns:
        -------
            Complete URL

        """
        # If path is already a full URL, return it
        if path.startswith(("http://", "https://")):
            return path

        # Ensure base URL ends with / and path starts with /
        # This prevents urljoin from dropping path components
        if self.base_url:
            base = self.base_url.rstrip("/") + "/"
            path = path.lstrip("/")
            return urljoin(base, path)

        return path

    async def _apply_auth(self, request: httpx.Request) -> httpx.Request:
        """Apply authentication to request if configured."""
        if self.auth_provider:
            try:
                # Check if we need to refresh credentials
                await self.auth_provider.refresh_if_needed()

                # Apply authentication
                request = await self.auth_provider.apply_auth(request)
            except Exception as e:
                raise AuthenticationError(
                    f"Failed to apply authentication: {e}",
                    auth_type=type(self.auth_provider).__name__,
                )

        return request

    async def _execute_with_retries(
        self,
        request: httpx.Request,
        retries: int | None = None,
        retry_delay: float | None = None,
        retry_backoff: float | None = None,
    ) -> httpx.Response:
        """Execute request with retry logic.

        Implements exponential backoff for retries, which helps handle
        temporary failures and rate limiting gracefully.

        Args:
        ----
            request: The request to execute
            retries: Override number of retries
            retry_delay: Override initial retry delay
            retry_backoff: Override backoff multiplier

        Returns:
        -------
            The response

        Raises:
        ------
            RequestError: If all retries are exhausted

        """
        retries = retries if retries is not None else self.request_config.retries
        delay = retry_delay or self.request_config.retry_delay
        backoff = retry_backoff or self.request_config.retry_backoff

        last_exception: Exception | None = None

        for attempt in range(retries + 1):
            try:
                self.logger.debug(
                    f"Executing {request.method} {request.url} "
                    f"(attempt {attempt + 1}/{retries + 1})"
                )

                response = await self._client.send(request)

                # Check for auth failures that might be recoverable
                if response.status_code in (401, 403) and self.auth_provider:
                    if await self.auth_provider.handle_auth_failure(response):
                        # Auth was refreshed, retry the request
                        request = await self._apply_auth(request)
                        continue

                # Success! Return the response
                return response

            except httpx.TimeoutException:
                last_exception = TimeoutError(
                    f"Request timed out after {self.request_config.timeout}s",
                    timeout_seconds=self.request_config.timeout,
                    request_data={"method": request.method, "url": str(request.url)},
                )

            except httpx.RequestError as e:
                last_exception = RequestError(
                    f"Request failed: {e}",
                    request_data={
                        "method": request.method,
                        "url": str(request.url),
                        "headers": dict(request.headers),
                    },
                )

            # Don't retry on the last attempt
            if attempt < retries:
                self.logger.warning(
                    f"Request failed on attempt {attempt + 1}: {last_exception}. "
                    f"Retrying in {delay}s..."
                )
                await asyncio.sleep(delay)
                delay *= backoff

        # All retries exhausted
        raise RequestError(
            f"Request failed after {retries + 1} attempts",
            request_data={
                "method": request.method,
                "url": str(request.url),
                "attempts": retries + 1,
            },
        ) from last_exception

    async def request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        data: Mapping[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> EnhancedResponse:
        """Make an HTTP request with all enhancements.

        This is the core method that all convenience methods delegate to.
        It handles URL building, authentication, retries, and response
        enhancement.

        Args:
        ----
            method: HTTP method (GET, POST, etc.)
            url: URL path or full URL
            params: Query parameters
            json: JSON data to send
            data: Form data or raw bytes to send
            files: Files to upload
            headers: Additional headers (merged with defaults)
            timeout: Override timeout for this request
            **kwargs: Additional arguments passed to httpx

        Returns:
        -------
            Enhanced response object

        """
        # Build full URL
        full_url = self._build_url(url)

        # Merge headers
        merged_headers = {**self.default_headers}
        if headers:
            merged_headers.update(headers)

        # Create request
        request = self._client.build_request(
            method=method,
            url=full_url,
            params=params,
            json=json,
            data=data,
            files=files,
            headers=merged_headers,
            timeout=timeout,
            **kwargs,
        )

        # Apply authentication
        request = await self._apply_auth(request)

        # Log request with sanitization
        logger.log_request(request, level=logging.DEBUG)

        # Execute with retries
        start_time = time.time()
        with logger.operation_context(f"{method} {full_url}"):
            response = await self._execute_with_retries(request)

        # Calculate response time
        response_time = time.time() - start_time

        # Log response with sanitization
        logger.log_response(response, response_time, level=logging.DEBUG)

        # Return enhanced response
        return EnhancedResponse(response, start_time)

    # Convenience methods for common HTTP verbs
    async def get(self, url: str, **kwargs: Any) -> EnhancedResponse:
        """Make a GET request."""
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> EnhancedResponse:
        """Make a POST request."""
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs: Any) -> EnhancedResponse:
        """Make a PUT request."""
        return await self.request("PUT", url, **kwargs)

    async def patch(self, url: str, **kwargs: Any) -> EnhancedResponse:
        """Make a PATCH request."""
        return await self.request("PATCH", url, **kwargs)

    async def delete(self, url: str, **kwargs: Any) -> EnhancedResponse:
        """Make a DELETE request."""
        return await self.request("DELETE", url, **kwargs)

    async def head(self, url: str, **kwargs: Any) -> EnhancedResponse:
        """Make a HEAD request."""
        return await self.request("HEAD", url, **kwargs)

    async def options(self, url: str, **kwargs: Any) -> EnhancedResponse:
        """Make an OPTIONS request."""
        return await self.request("OPTIONS", url, **kwargs)


class SyncHTTPClient:
    """Synchronous wrapper around the async HTTP client.

    This provides a synchronous interface for users who prefer not to work
    with async/await. It manages its own event loop to run async operations.

    Note: For new projects, we recommend using the async client for better
    performance and concurrency. The sync client is provided for easier
    migration and simpler test scenarios.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize sync client with same arguments as async client."""
        self._async_client = HTTPClient(*args, **kwargs)
        self._loop: asyncio.AbstractEventLoop | None = None

    def _get_event_loop(self) -> asyncio.AbstractEventLoop:
        """Get or create event loop for running async operations."""
        try:
            # Try to get existing loop
            loop = asyncio.get_running_loop()
            # If we're here, we're already in an async context
            # This shouldn't happen in normal sync usage
            raise RuntimeError(
                "SyncHTTPClient cannot be used within an async context. "
                "Use HTTPClient (async) instead."
            )
        except RuntimeError:
            # No running loop, create or reuse one
            if self._loop is None or self._loop.is_closed():
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
            return self._loop

    def _run_async(self, coro: Any) -> Any:
        """Run an async coroutine in the sync context."""
        loop = self._get_event_loop()
        return loop.run_until_complete(coro)

    def set_auth(self, auth_provider: AuthProvider) -> None:
        """Set or update the authentication provider."""
        self._async_client.set_auth(auth_provider)

    def set_default_header(self, name: str, value: str) -> None:
        """Add or update a default header."""
        self._async_client.set_default_header(name, value)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._run_async(self._async_client.close())
        if self._loop and not self._loop.is_closed():
            self._loop.close()

    def __enter__(self) -> "SyncHTTPClient":
        """Enter context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Exit context manager and cleanup."""
        self.close()

    def request(self, method: str, url: str, **kwargs: Any) -> EnhancedResponse:
        """Make an HTTP request synchronously."""
        result = self._run_async(self._async_client.request(method, url, **kwargs))
        if not isinstance(result, EnhancedResponse):
            raise TypeError("Expected EnhancedResponse from coroutine")
        return result

    # Convenience methods
    def get(self, url: str, **kwargs: Any) -> EnhancedResponse:
        """Make a GET request."""
        result = self._run_async(self._async_client.get(url, **kwargs))
        if not isinstance(result, EnhancedResponse):
            raise TypeError("Expected EnhancedResponse from coroutine")
        return result

    def post(self, url: str, **kwargs: Any) -> EnhancedResponse:
        """Make a POST request."""
        result = self._run_async(self._async_client.post(url, **kwargs))
        if not isinstance(result, EnhancedResponse):
            raise TypeError("Expected EnhancedResponse from coroutine")
        return result

    def put(self, url: str, **kwargs: Any) -> EnhancedResponse:
        """Make a PUT request."""
        result = self._run_async(self._async_client.put(url, **kwargs))
        if not isinstance(result, EnhancedResponse):
            raise TypeError("Expected EnhancedResponse from coroutine")
        return result

    def patch(self, url: str, **kwargs: Any) -> EnhancedResponse:
        """Make a PATCH request."""
        result = self._run_async(self._async_client.patch(url, **kwargs))
        if not isinstance(result, EnhancedResponse):
            raise TypeError("Expected EnhancedResponse from coroutine")
        return result

    def delete(self, url: str, **kwargs: Any) -> EnhancedResponse:
        """Make a DELETE request."""
        result = self._run_async(self._async_client.delete(url, **kwargs))
        if not isinstance(result, EnhancedResponse):
            raise TypeError("Expected EnhancedResponse from coroutine")
        return result

    def head(self, url: str, **kwargs: Any) -> EnhancedResponse:
        """Make a HEAD request."""
        result = self._run_async(self._async_client.head(url, **kwargs))
        if not isinstance(result, EnhancedResponse):
            raise TypeError("Expected EnhancedResponse from coroutine")
        return result

    def options(self, url: str, **kwargs: Any) -> EnhancedResponse:
        """Make an OPTIONS request."""
        result = self._run_async(self._async_client.options(url, **kwargs))
        if not isinstance(result, EnhancedResponse):
            raise TypeError("Expected EnhancedResponse from coroutine")
        return result


# Exported symbols
__all__ = [
    "HTTPClient",
    "SyncHTTPClient",
    "EnhancedResponse",
    "RequestConfig",
    "AuthProvider",
    "BearerTokenAuth",
    "APIKeyAuth",
]
