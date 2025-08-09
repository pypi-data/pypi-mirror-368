"""Enhanced Logging Utilities for TestAPIX

This module provides structured logging capabilities with configurable levels,
request/response debugging with sanitization, and comprehensive error context.
"""

import json
import logging
import sys
import time
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx


# Configure logging levels
class LogLevel(str, Enum):
    """Logging levels for TestAPIX"""

    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    TRACE = "TRACE"  # Custom level for very detailed debugging


@dataclass
class ErrorSuggestion:
    """A suggestion for resolving an error"""

    suggestion: str
    action: str
    priority: int = 1  # 1=high, 2=medium, 3=low


@dataclass
class ErrorContext:
    """Enhanced error context with suggestions and debugging info"""

    error_type: str
    assertion_chain: list[str] = field(default_factory=list)
    request_context: dict[str, Any] | None = None
    response_context: dict[str, Any] | None = None
    suggestions: list[ErrorSuggestion] = field(default_factory=list)
    debug_info: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class SanitizedRequestLogger:
    """Handles request/response logging with sensitive data sanitization"""

    # Patterns for sensitive data that should be sanitized
    SENSITIVE_HEADERS = {
        "authorization",
        "x-api-key",
        "x-auth-token",
        "cookie",
        "set-cookie",
        "x-access-token",
        "x-refresh-token",
        "bearer",
        "basic",
        "digest",
        "oauth",
        "jwt",
    }

    SENSITIVE_QUERY_PARAMS = {
        "password",
        "token",
        "key",
        "secret",
        "api_key",
        "apikey",
        "access_token",
        "refresh_token",
        "auth",
        "authorization",
    }

    SENSITIVE_BODY_FIELDS = {
        "password",
        "token",
        "secret",
        "api_key",
        "apikey",
        "key",
        "access_token",
        "refresh_token",
        "client_secret",
        "private_key",
        "credential",
        "auth",
        "authorization",
    }

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._redact_value = "[REDACTED]"

    def sanitize_headers(self, headers: dict[str, str]) -> dict[str, str]:
        """Sanitize sensitive headers"""
        sanitized = {}
        for key, value in headers.items():
            if key.lower() in self.SENSITIVE_HEADERS or any(
                sensitive in key.lower() for sensitive in self.SENSITIVE_HEADERS
            ):
                sanitized[key] = self._redact_value
            else:
                sanitized[key] = value
        return sanitized

    def sanitize_query_params(self, url: str) -> str:
        """Sanitize sensitive query parameters in URL"""
        parsed = urlparse(url)
        if not parsed.query:
            return url

        # Parse query parameters
        params = []
        for param in parsed.query.split("&"):
            try:
                key, value = param.split("=", 1)
                if key.lower() in self.SENSITIVE_QUERY_PARAMS:
                    params.append(f"{key}={self._redact_value}")
                else:
                    params.append(param)
            except ValueError:
                params.append(param)  # Handle parameters without values

        # Reconstruct URL
        sanitized_query = "&".join(params)
        return url.replace(parsed.query, sanitized_query)

    def sanitize_json_body(self, body: str | dict[str, Any]) -> str | dict[str, Any]:
        """Sanitize sensitive fields in JSON body"""
        if isinstance(body, str):
            try:
                data = json.loads(body)
                sanitized = self._sanitize_dict(data)
                return json.dumps(sanitized)
            except json.JSONDecodeError:
                return body
        else:  # isinstance(body, dict)
            return self._sanitize_dict(body)

    def _sanitize_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """Recursively sanitize dictionary values"""
        sanitized: dict[str, Any] = {}
        for key, value in data.items():
            if key.lower() in self.SENSITIVE_BODY_FIELDS:
                sanitized[key] = self._redact_value
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        return sanitized

    def log_request(self, request: httpx.Request, level: int = logging.DEBUG) -> None:
        """Log HTTP request with sanitization"""
        if not self.logger.isEnabledFor(level):
            return

        # Sanitize request data
        sanitized_headers = self.sanitize_headers(dict(request.headers))
        sanitized_url = self.sanitize_query_params(str(request.url))

        # Prepare request body
        sanitized_body = None
        if request.content:
            try:
                body_text = request.content.decode("utf-8")
                if request.headers.get("content-type", "").startswith(
                    "application/json"
                ):
                    sanitized_body = self.sanitize_json_body(body_text)
                else:
                    sanitized_body = (
                        body_text[:1000] + "..." if len(body_text) > 1000 else body_text
                    )
            except UnicodeDecodeError:
                sanitized_body = f"[Binary content, {len(request.content)} bytes]"

        # Log request
        self.logger.log(
            level,
            "HTTP Request: %s %s",
            request.method,
            sanitized_url,
            extra={
                "request_method": request.method,
                "request_url": sanitized_url,
                "request_headers": sanitized_headers,
                "request_body": sanitized_body,
                "event_type": "http_request",
            },
        )

    def log_response(
        self, response: httpx.Response, request_time: float, level: int = logging.DEBUG
    ) -> None:
        """Log HTTP response with sanitization"""
        if not self.logger.isEnabledFor(level):
            return

        # Sanitize response headers
        sanitized_headers = self.sanitize_headers(dict(response.headers))

        # Prepare response body
        sanitized_body = None
        try:
            body_text = response.text
            if response.headers.get("content-type", "").startswith("application/json"):
                try:
                    # Don't sanitize response bodies unless they contain auth info
                    json_data = json.loads(body_text)
                    if any(
                        key in str(json_data).lower()
                        for key in ["token", "key", "secret", "password"]
                    ):
                        sanitized_body = self.sanitize_json_body(json_data)
                    else:
                        sanitized_body = (
                            body_text[:2000] + "..."
                            if len(body_text) > 2000
                            else body_text
                        )
                except json.JSONDecodeError:
                    sanitized_body = (
                        body_text[:2000] + "..." if len(body_text) > 2000 else body_text
                    )
            else:
                sanitized_body = (
                    body_text[:1000] + "..." if len(body_text) > 1000 else body_text
                )
        except Exception:
            sanitized_body = "[Unable to decode response body]"

        # Log response
        self.logger.log(
            level,
            "HTTP Response: %d %s (%.3fs)",
            response.status_code,
            response.reason_phrase or "Unknown",
            request_time,
            extra={
                "response_status": response.status_code,
                "response_reason": response.reason_phrase,
                "response_headers": sanitized_headers,
                "response_body": sanitized_body,
                "response_time": request_time,
                "event_type": "http_response",
            },
        )


class ErrorSuggestionEngine:
    """Generates helpful suggestions based on error types and context"""

    def __init__(self) -> None:
        self.suggestion_rules = {
            "status_code": self._suggest_status_code_fixes,
            "json_path": self._suggest_json_path_fixes,
            "schema_validation": self._suggest_schema_fixes,
            "timeout": self._suggest_timeout_fixes,
            "authentication": self._suggest_auth_fixes,
            "network": self._suggest_network_fixes,
        }

    def generate_suggestions(
        self, error_context: ErrorContext
    ) -> list[ErrorSuggestion]:
        """Generate suggestions based on error context"""
        suggestions = []

        # Get suggestions based on error type
        if error_context.error_type in self.suggestion_rules:
            suggestions.extend(
                self.suggestion_rules[error_context.error_type](error_context)
            )

        # Add general debugging suggestions
        suggestions.extend(self._suggest_general_debugging(error_context))

        # Sort by priority
        return sorted(suggestions, key=lambda s: s.priority)

    def _suggest_status_code_fixes(
        self, context: ErrorContext
    ) -> list[ErrorSuggestion]:
        """Suggest fixes for status code errors"""
        suggestions = []

        if context.response_context:
            status = context.response_context.get("status_code")

            if status is not None and status == 401:
                suggestions.extend(
                    [
                        ErrorSuggestion(
                            "Check authentication credentials",
                            "Verify auth token/API key is valid and not expired",
                            1,
                        ),
                        ErrorSuggestion(
                            "Check authorization header format",
                            "Ensure Bearer token or API key header is correctly formatted",
                            2,
                        ),
                    ]
                )
            elif status is not None and status == 403:
                suggestions.append(
                    ErrorSuggestion(
                        "Check user permissions",
                        "Verify the authenticated user has permission for this resource",
                        1,
                    )
                )
            elif status is not None and status == 404:
                suggestions.extend(
                    [
                        ErrorSuggestion(
                            "Verify API endpoint URL",
                            "Check if the endpoint path and base URL are correct",
                            1,
                        ),
                        ErrorSuggestion(
                            "Check resource existence",
                            "Verify the requested resource exists and ID is correct",
                            2,
                        ),
                    ]
                )
            elif status is not None and status == 429:
                suggestions.append(
                    ErrorSuggestion(
                        "Implement rate limiting backoff",
                        "Add delays between requests or reduce request frequency",
                        1,
                    )
                )
            elif status is not None and status >= 500:
                suggestions.extend(
                    [
                        ErrorSuggestion(
                            "Retry the request",
                            "Server errors are often transient - implement retry logic",
                            1,
                        ),
                        ErrorSuggestion(
                            "Check server status",
                            "Verify the API server is operational",
                            2,
                        ),
                    ]
                )

        return suggestions

    def _suggest_json_path_fixes(self, context: ErrorContext) -> list[ErrorSuggestion]:
        """Suggest fixes for JSON path errors"""
        suggestions = [
            ErrorSuggestion(
                "Verify JSON structure",
                "Check the actual response structure matches expected paths",
                1,
            ),
            ErrorSuggestion(
                "Use response.json_data inspection",
                "Print or log the full response to understand the structure",
                2,
            ),
            ErrorSuggestion(
                "Check for null values",
                "Ensure intermediate objects in the path are not null",
                2,
            ),
        ]

        return suggestions

    def _suggest_schema_fixes(self, context: ErrorContext) -> list[ErrorSuggestion]:
        """Suggest fixes for schema validation errors"""
        return [
            ErrorSuggestion(
                "Update schema definition",
                "Ensure schema matches the actual API response format",
                1,
            ),
            ErrorSuggestion(
                "Check API version compatibility",
                "Verify you're using the correct API version and schema",
                2,
            ),
            ErrorSuggestion(
                "Review validation errors",
                "Check specific field validation failures in error details",
                1,
            ),
        ]

    def _suggest_timeout_fixes(self, context: ErrorContext) -> list[ErrorSuggestion]:
        """Suggest fixes for timeout errors"""
        return [
            ErrorSuggestion(
                "Increase timeout value",
                "Consider increasing the request timeout for slow endpoints",
                1,
            ),
            ErrorSuggestion(
                "Check network connectivity",
                "Verify network connection to the API server",
                2,
            ),
            ErrorSuggestion(
                "Optimize request payload",
                "Reduce request size if sending large payloads",
                3,
            ),
        ]

    def _suggest_auth_fixes(self, context: ErrorContext) -> list[ErrorSuggestion]:
        """Suggest fixes for authentication errors"""
        return [
            ErrorSuggestion(
                "Refresh authentication token",
                "Check if token has expired and needs refreshing",
                1,
            ),
            ErrorSuggestion(
                "Verify credentials configuration",
                "Ensure auth credentials are correctly configured",
                1,
            ),
            ErrorSuggestion(
                "Check auth provider settings",
                "Verify authentication provider type and settings",
                2,
            ),
        ]

    def _suggest_network_fixes(self, context: ErrorContext) -> list[ErrorSuggestion]:
        """Suggest fixes for network errors"""
        return [
            ErrorSuggestion(
                "Check network connectivity",
                "Verify internet connection and DNS resolution",
                1,
            ),
            ErrorSuggestion(
                "Review proxy settings",
                "Check if corporate proxy or firewall is blocking requests",
                2,
            ),
            ErrorSuggestion(
                "Verify SSL/TLS settings",
                "Check certificate validation and SSL configuration",
                3,
            ),
        ]

    def _suggest_general_debugging(
        self, context: ErrorContext
    ) -> list[ErrorSuggestion]:
        """General debugging suggestions"""
        suggestions = []

        # If there's an assertion chain, suggest reviewing it
        if context.assertion_chain:
            suggestions.append(
                ErrorSuggestion(
                    "Review assertion chain",
                    f"Check assertion sequence: {' -> '.join(context.assertion_chain)}",
                    3,
                )
            )

        # Always suggest logging for debugging
        suggestions.append(
            ErrorSuggestion(
                "Enable debug logging",
                "Set log level to DEBUG for detailed request/response information",
                3,
            )
        )

        return suggestions


class TestAPIXLogger:
    """Enhanced logger for TestAPIX with structured logging and error context"""

    def __init__(self, name: str, level: str | int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Add custom TRACE level
        if not hasattr(logging, "TRACE"):
            logging.addLevelName(5, "TRACE")
            logging.TRACE = 5  # type: ignore[attr-defined]

        # Create sanitized request logger
        self.request_logger = SanitizedRequestLogger(self.logger)

        # Create error suggestion engine
        self.suggestion_engine = ErrorSuggestionEngine()

        # Ensure we have at least one handler
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def trace(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log at TRACE level (very detailed debugging)"""
        self.logger.log(5, msg, *args, **kwargs)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log at DEBUG level"""
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log at INFO level"""
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log at WARNING level"""
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log at ERROR level"""
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log at CRITICAL level"""
        self.logger.critical(msg, *args, **kwargs)

    def log_error_with_context(
        self, error_context: ErrorContext, level: int = logging.ERROR
    ) -> None:
        """Log error with comprehensive context and suggestions"""
        # Generate suggestions
        suggestions = self.suggestion_engine.generate_suggestions(error_context)

        # Build comprehensive error message
        error_parts = [
            f"Error Type: {error_context.error_type}",
            f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(error_context.timestamp))}",
        ]

        if error_context.assertion_chain:
            error_parts.append(
                f"Assertion Chain: {' → '.join(error_context.assertion_chain)}"
            )

        if error_context.request_context:
            error_parts.append("Request Context:")
            for key, value in error_context.request_context.items():
                error_parts.append(f"  {key}: {value}")

        if error_context.response_context:
            error_parts.append("Response Context:")
            for key, value in error_context.response_context.items():
                error_parts.append(f"  {key}: {value}")

        if suggestions:
            error_parts.append("\nSuggestions:")
            for i, suggestion in enumerate(
                suggestions[:5], 1
            ):  # Limit to top 5 suggestions
                priority_marker = (
                    "🔴"
                    if suggestion.priority == 1
                    else "🟡"
                    if suggestion.priority == 2
                    else "🟢"
                )
                error_parts.append(f"  {i}. {priority_marker} {suggestion.suggestion}")
                error_parts.append(f"     Action: {suggestion.action}")

        if error_context.debug_info:
            error_parts.append("\nDebug Information:")
            for key, value in error_context.debug_info.items():
                error_parts.append(f"  {key}: {value}")

        # Log the comprehensive error
        self.logger.log(
            level,
            "\n".join(error_parts),
            extra={
                "error_context": error_context,
                "suggestions": suggestions,
                "event_type": "enhanced_error",
            },
        )

    def log_request(self, request: httpx.Request, level: int = logging.DEBUG) -> None:
        """Log HTTP request with sanitization"""
        self.request_logger.log_request(request, level)

    def log_response(
        self, response: httpx.Response, request_time: float, level: int = logging.DEBUG
    ) -> None:
        """Log HTTP response with sanitization"""
        self.request_logger.log_response(response, request_time, level)

    @contextmanager
    def operation_context(self, operation: str) -> Generator[None, None, None]:
        """Context manager for logging operation start/end"""
        start_time = time.time()
        self.debug(f"Starting operation: {operation}")

        try:
            yield
            duration = time.time() - start_time
            self.debug(f"Completed operation: {operation} (took {duration:.3f}s)")
        except Exception as e:
            duration = time.time() - start_time
            self.error(f"Failed operation: {operation} (took {duration:.3f}s): {e}")
            raise


def get_logger(name: str, level: str | int = logging.INFO) -> TestAPIXLogger:
    """Get or create a TestAPIX logger instance"""
    return TestAPIXLogger(name, level)


def setup_logging(
    level: str | int = logging.INFO,
    format_string: str | None = None,
    log_file: str | Path | None = None,
    enable_json_logging: bool = False,
) -> None:
    """Setup global logging configuration for TestAPIX"""
    # Configure root logger level
    logging.getLogger("testapix").setLevel(level)

    # Default format
    if format_string is None:
        if enable_json_logging:
            format_string = '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
        else:
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(format_string)

    # Remove existing handlers
    for handler in logging.getLogger("testapix").handlers[:]:
        logging.getLogger("testapix").removeHandler(handler)

    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logging.getLogger("testapix").addHandler(console_handler)

    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logging.getLogger("testapix").addHandler(file_handler)

    # Add TRACE level if not exists
    if not hasattr(logging, "TRACE"):
        logging.addLevelName(5, "TRACE")
        logging.TRACE = 5  # type: ignore[attr-defined]
