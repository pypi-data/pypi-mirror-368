"""Response Assertion Implementation

This module provides the fluent assertion interface for API responses. The design
follows these principles:

1. Readability: Assertions should read like natural language
2. Chainability: Multiple assertions can be chained together
3. Clear Failures: Error messages should pinpoint exactly what went wrong
4. Extensibility: New assertion methods can be easily added

The ResponseAssertion class wraps an API response and provides methods that
return self, enabling the fluent interface pattern.
"""

import json
import re
from pathlib import Path
from re import Pattern
from typing import Any

from pydantic import BaseModel

from testapix.core.client import EnhancedResponse
from testapix.core.exceptions import ResponseValidationError
from testapix.core.logging_utils import ErrorContext, get_logger
from testapix.validation import (
    JSONSchemaValidator,
    OpenAPIValidator,
    PydanticValidator,
    SchemaValidationError,
)


class ResponseAssertion:
    """Fluent assertion interface for API responses.

    This class provides a chainable interface for making assertions about
    API responses. Each method returns self, allowing for natural test writing:

        assert_that(response)
            .has_status(200)
            .has_json_path("user.id")
            .response_time_less_than(1.0)

    The class is designed to provide helpful error messages that make debugging
    test failures easier.
    """

    def __init__(self, response: EnhancedResponse):
        """Initialize assertion wrapper for a response.

        Args:
        ----
            response: The enhanced response to make assertions about

        """
        self.response = response
        self._json_cache: dict[str, Any] | None = None
        self._assertion_chain: list[str] = []  # Track assertions for error context
        self._logger = get_logger(f"{__name__}.ResponseAssertion")

        # Initialize schema validators
        self._json_schema_validator = JSONSchemaValidator()
        self._openapi_validator = OpenAPIValidator()
        self._pydantic_validator = PydanticValidator()

    def _add_assertion(self, assertion_type: str) -> None:
        """Track assertion for better error messages."""
        self._assertion_chain.append(assertion_type)

    def _create_error_context(
        self,
        error_type: str,
        base_message: str,
        expected: Any = None,
        actual: Any = None,
        details: str | None = None,
    ) -> ErrorContext:
        """Create comprehensive error context for enhanced logging and suggestions."""
        # Build request context
        request_context = {}
        if hasattr(self.response, "_request"):
            request = self.response._request
            request_context = {
                "method": getattr(request, "method", "Unknown"),
                "url": str(getattr(request, "url", "Unknown")),
                "headers_count": len(getattr(request, "headers", {})),
            }

        # Build response context
        response_context = {
            "status_code": self.response.status_code,
            "url": str(self.response.url),
            "headers_count": len(self.response.headers),
            "content_length": len(self.response.content),
            "response_time": getattr(self.response, "response_time", 0),
            "content_type": self.response.headers.get("content-type", "Unknown"),
        }

        # Build debug info
        debug_info = {
            "base_message": base_message,
            "expected": str(expected) if expected is not None else None,
            "actual": str(actual) if actual is not None else None,
            "details": details,
        }

        if details:
            debug_info["details"] = details

        return ErrorContext(
            error_type=error_type,
            assertion_chain=self._assertion_chain.copy(),
            request_context=request_context,
            response_context=response_context,
            debug_info=debug_info,
        )

    def _format_error_message(
        self,
        base_message: str,
        expected: Any = None,
        actual: Any = None,
        details: str | None = None,
        error_type: str = "assertion_failure",
    ) -> str:
        """Format a comprehensive error message with context and log it.

        This method creates error messages that help developers quickly
        understand what went wrong and where, with actionable suggestions.
        """
        # Create error context for enhanced logging
        error_context = self._create_error_context(
            error_type, base_message, expected, actual, details
        )

        # Log error with context and suggestions
        self._logger.log_error_with_context(error_context)

        # Build user-facing error message
        parts = [base_message]

        # Add expected vs actual if provided
        if expected is not None and actual is not None:
            parts.append(f"\n  Expected: {expected}")
            parts.append(f"  Actual: {actual}")

        # Add additional details if provided
        if details:
            parts.append(f"\n  Details: {details}")

        # Add response preview for context
        parts.append(f"\n  Response Status: {self.response.status_code}")
        parts.append(f"  Response URL: {self.response.url}")

        # Add response body preview (truncated for large responses)
        try:
            body_preview = self.response.text[:500]
            if len(self.response.text) > 500:
                body_preview += "..."
            parts.append(f"  Response Preview: {body_preview}")
        except:
            parts.append("  Response Preview: [Unable to get response body]")

        # Add assertion chain context
        if self._assertion_chain:
            parts.append(f"\n  Assertion Chain: {' → '.join(self._assertion_chain)}")

        # Add quick suggestions (top 2 only for brevity in exception message)
        suggestions = self._logger.suggestion_engine.generate_suggestions(error_context)
        if suggestions:
            parts.append("\n  Quick Suggestions:")
            for i, suggestion in enumerate(suggestions[:2], 1):
                parts.append(f"    {i}. {suggestion.suggestion}")
            if len(suggestions) > 2:
                parts.append(
                    f"    (See logs for {len(suggestions) - 2} more suggestions)"
                )

        return "\n".join(parts)

    # Status Code Assertions

    def has_status(self, expected_status: int) -> "ResponseAssertion":
        """Assert that response has the expected status code.

        Args:
        ----
            expected_status: Expected HTTP status code

        Returns:
        -------
            Self for method chaining

        Raises:
        ------
            ResponseValidationError: If status doesn't match

        Example:
        -------
            assert_that(response).has_status(200)

        """
        self._add_assertion(f"has_status({expected_status})")

        actual_status = self.response.status_code
        if actual_status != expected_status:
            raise ResponseValidationError(
                self._format_error_message(
                    f"Expected status {expected_status} but got {actual_status}",
                    expected=expected_status,
                    actual=actual_status,
                    error_type="status_code",
                ),
                expected=expected_status,
                actual=actual_status,
                assertion_type="status_code",
            )

        return self

    def has_status_in(self, expected_statuses: list[int]) -> "ResponseAssertion":
        """Assert that response status is one of the expected values.

        Useful when multiple status codes are acceptable, like 200 or 201
        for successful creation.

        Args:
        ----
            expected_statuses: List of acceptable status codes

        Returns:
        -------
            Self for method chaining

        Example:
        -------
            assert_that(response).has_status_in([200, 201, 202])

        """
        self._add_assertion(f"has_status_in({expected_statuses})")

        actual_status = self.response.status_code
        if actual_status not in expected_statuses:
            raise ResponseValidationError(
                self._format_error_message(
                    f"Expected status to be one of {expected_statuses} but got {actual_status}",
                    expected=expected_statuses,
                    actual=actual_status,
                ),
                expected=expected_statuses,
                actual=actual_status,
                assertion_type="status_code_in",
            )

        return self

    def has_success_status(self) -> "ResponseAssertion":
        """Assert that response has a 2xx success status code.

        Returns:
        -------
            Self for method chaining

        Example:
        -------
            assert_that(response).has_success_status()

        """
        self._add_assertion("has_success_status()")

        actual_status = self.response.status_code
        if not (200 <= actual_status < 300):
            raise ResponseValidationError(
                self._format_error_message(
                    f"Expected success status (2xx) but got {actual_status}",
                    expected="2xx",
                    actual=actual_status,
                ),
                expected="2xx",
                actual=actual_status,
                assertion_type="success_status",
            )

        return self

    def has_error_status(self) -> "ResponseAssertion":
        """Assert that response has a 4xx or 5xx error status code.

        Returns:
        -------
            Self for method chaining

        Example:
        -------
            assert_that(response).has_error_status()

        """
        self._add_assertion("has_error_status()")

        actual_status = self.response.status_code
        if not (400 <= actual_status < 600):
            raise ResponseValidationError(
                self._format_error_message(
                    f"Expected error status (4xx or 5xx) but got {actual_status}",
                    expected="4xx or 5xx",
                    actual=actual_status,
                ),
                expected="4xx or 5xx",
                actual=actual_status,
                assertion_type="error_status",
            )

        return self

    # Header Assertions

    def has_header(
        self, header_name: str, expected_value: str | None = None
    ) -> "ResponseAssertion":
        """Assert that response has a specific header.

        Header names are case-insensitive. If expected_value is provided,
        also checks that the header has that specific value.

        Args:
        ----
            header_name: Name of the header to check
            expected_value: Optional expected value

        Returns:
        -------
            Self for method chaining

        Example:
        -------
            assert_that(response).has_header("content-type", "application/json")

        """
        self._add_assertion(f"has_header('{header_name}')")

        # Case-insensitive header lookup
        headers_lower = {k.lower(): v for k, v in self.response.headers.items()}
        header_name_lower = header_name.lower()

        if header_name_lower not in headers_lower:
            available_headers = list(self.response.headers.keys())
            raise ResponseValidationError(
                self._format_error_message(
                    f"Expected header '{header_name}' not found",
                    expected=header_name,
                    actual=None,
                    details=f"Available headers: {available_headers}",
                ),
                expected=header_name,
                actual=None,
                assertion_type="header_exists",
            )

        actual_value = headers_lower[header_name_lower]

        if expected_value is not None and actual_value != expected_value:
            raise ResponseValidationError(
                self._format_error_message(
                    f"Header '{header_name}' has unexpected value",
                    expected=expected_value,
                    actual=actual_value,
                ),
                expected=expected_value,
                actual=actual_value,
                assertion_type="header_value",
            )

        return self

    def has_content_type(self, expected_content_type: str) -> "ResponseAssertion":
        """Assert that response has the expected content type.

        This method ignores charset and other parameters, focusing only
        on the main content type.

        Args:
        ----
            expected_content_type: Expected content type (e.g., 'application/json')

        Returns:
        -------
            Self for method chaining

        Example:
        -------
            assert_that(response).has_content_type("application/json")

        """
        self._add_assertion(f"has_content_type('{expected_content_type}')")

        actual_content_type = self.response.headers.get("content-type", "")

        # Extract main content type (before semicolon)
        main_type = actual_content_type.split(";")[0].strip()

        if main_type != expected_content_type:
            raise ResponseValidationError(
                self._format_error_message(
                    f"Expected content type '{expected_content_type}' but got '{main_type}'",
                    expected=expected_content_type,
                    actual=main_type,
                ),
                expected=expected_content_type,
                actual=main_type,
                assertion_type="content_type",
            )

        return self

    # JSON Assertions

    def has_json(self) -> "ResponseAssertion":
        """Assert that response contains valid JSON.

        Returns:
        -------
            Self for method chaining

        Example:
        -------
            assert_that(response).has_json()

        """
        self._add_assertion("has_json()")

        try:
            self._get_json()
        except Exception as e:
            raise ResponseValidationError(
                self._format_error_message(
                    f"Expected valid JSON but parsing failed: {e}",
                    expected="valid JSON",
                    actual=f"parse error: {e}",
                ),
                expected="valid JSON",
                actual=str(e),
                assertion_type="json_valid",
            )

        return self

    def has_json_path(
        self, path: str, expected_value: Any = None
    ) -> "ResponseAssertion":
        """Assert that JSON response contains a specific path.

        Supports dot notation for nested access and array indices:
        - "user.name" -> data['user']['name']
        - "users[0].email" -> data['users'][0]['email']
        - "metadata.tags[2]" -> data['metadata']['tags'][2]

        Args:
        ----
            path: JSON path using dot notation
            expected_value: Optional expected value at that path

        Returns:
        -------
            Self for method chaining

        Example:
        -------
            assert_that(response).has_json_path("data.user.email", "test@example.com")

        """
        self._add_assertion(f"has_json_path('{path}')")

        try:
            actual_value = self._extract_json_path(path)

            if expected_value is not None and actual_value != expected_value:
                raise ResponseValidationError(
                    self._format_error_message(
                        f"JSON path '{path}' has unexpected value",
                        expected=expected_value,
                        actual=actual_value,
                        error_type="json_path",
                    ),
                    expected=expected_value,
                    actual=actual_value,
                    assertion_type="json_path_value",
                )

        except (KeyError, IndexError, TypeError) as e:
            # Provide helpful error about what part of the path failed
            json_preview = self._get_json_preview()
            raise ResponseValidationError(
                self._format_error_message(
                    f"JSON path '{path}' not found",
                    expected=f"path '{path}' to exist",
                    actual="path not found",
                    details=f"Error: {e}\nJSON structure: {json_preview}",
                    error_type="json_path",
                ),
                expected=f"path '{path}'",
                actual="not found",
                assertion_type="json_path_exists",
            )

        return self

    def has_json_matching(self, expected_subset: dict[str, Any]) -> "ResponseAssertion":
        """Assert that JSON response contains all key-value pairs from expected subset.

        This performs partial matching - the response can contain additional
        fields not specified in expected_subset.

        Args:
        ----
            expected_subset: Dictionary of expected key-value pairs

        Returns:
        -------
            Self for method chaining

        Example:
        -------
            assert_that(response).has_json_matching({
                "status": "success",
                "data": {"id": 123}
            })

        """
        self._add_assertion(f"has_json_matching({list(expected_subset.keys())})")

        json_data = self._get_json()

        if not isinstance(json_data, dict):
            raise ResponseValidationError(
                self._format_error_message(
                    f"Expected JSON object for matching but got {type(json_data).__name__}",
                    expected="JSON object (dict)",
                    actual=type(json_data).__name__,
                ),
                expected="dict",
                actual=type(json_data).__name__,
                assertion_type="json_type",
            )

        self._match_nested_dict(json_data, expected_subset, "")

        return self

    def _match_nested_dict(
        self, actual: dict[str, Any], expected: dict[str, Any], path: str
    ) -> None:
        """Recursively match nested dictionaries for has_json_matching."""
        for key, expected_value in expected.items():
            current_path = f"{path}.{key}" if path else key

            if key not in actual:
                raise ResponseValidationError(
                    self._format_error_message(
                        f"Expected key '{current_path}' not found in JSON",
                        expected=key,
                        actual="missing",
                        details=f"Available keys at this level: {list(actual.keys())}",
                    ),
                    expected=key,
                    actual="missing",
                    assertion_type="json_key_exists",
                )

            actual_value = actual[key]

            # Recursively check nested dictionaries
            if isinstance(expected_value, dict) and isinstance(actual_value, dict):
                self._match_nested_dict(actual_value, expected_value, current_path)
            else:
                if actual_value != expected_value:
                    raise ResponseValidationError(
                        self._format_error_message(
                            f"Value mismatch at '{current_path}'",
                            expected=expected_value,
                            actual=actual_value,
                        ),
                        expected=expected_value,
                        actual=actual_value,
                        assertion_type="json_value_match",
                    )

    # Text Content Assertions

    def has_text_containing(
        self, expected_text: str, case_sensitive: bool = True
    ) -> "ResponseAssertion":
        """Assert that response body contains the expected text.

        Args:
        ----
            expected_text: Text that should be present
            case_sensitive: Whether to perform case-sensitive matching

        Returns:
        -------
            Self for method chaining

        Example:
        -------
            assert_that(response).has_text_containing("Success", case_sensitive=False)

        """
        self._add_assertion(f"has_text_containing('{expected_text}')")

        response_text = self.response.text

        if case_sensitive:
            contains = expected_text in response_text
        else:
            contains = expected_text.lower() in response_text.lower()

        if not contains:
            # Show where in the response we might find similar text
            preview_start = max(0, len(response_text) // 2 - 100)
            preview = response_text[preview_start : preview_start + 200]

            raise ResponseValidationError(
                self._format_error_message(
                    f"Expected response to contain '{expected_text}'",
                    expected=expected_text,
                    actual="not found",
                    details=f"Response excerpt: ...{preview}...",
                ),
                expected=expected_text,
                actual="not found",
                assertion_type="text_contains",
            )

        return self

    def has_text_matching(self, pattern: str | Pattern[str]) -> "ResponseAssertion":
        """Assert that response text matches a regular expression.

        Args:
        ----
            pattern: Regular expression pattern (string or compiled pattern)

        Returns:
        -------
            Self for method chaining

        Example:
        -------
            assert_that(response).has_text_matching(r'"id":\\s*\\d+')

        """
        if isinstance(pattern, str):
            pattern_str = pattern
            pattern = re.compile(pattern)
        else:
            pattern_str = pattern.pattern

        self._add_assertion(f"has_text_matching('{pattern_str}')")

        response_text = self.response.text

        if not pattern.search(response_text):
            # Try to find partial matches to help debugging
            partial_matches = []
            for line_num, line in enumerate(response_text.split("\n")[:20], 1):
                if any(part in line for part in pattern_str.split(".*")):
                    partial_matches.append(f"Line {line_num}: {line.strip()}")

            details = "No partial matches found"
            if partial_matches:
                details = "Partial matches found:\n" + "\n".join(partial_matches[:3])

            raise ResponseValidationError(
                self._format_error_message(
                    f"Expected response to match pattern '{pattern_str}'",
                    expected=pattern_str,
                    actual="no match",
                    details=details,
                ),
                expected=pattern_str,
                actual="no match",
                assertion_type="text_regex",
            )

        return self

    # Error Message Assertions

    def has_error_message_containing(self, expected_text: str) -> "ResponseAssertion":
        """Assert that error response contains specific text.

        Searches common error fields: 'error', 'message', 'detail', 'description'

        Args:
        ----
            expected_text: Text that should appear in error message

        Returns:
        -------
            Self for method chaining

        Example:
        -------
            assert_that(response).has_error_message_containing("unauthorized")

        """
        self._add_assertion(f"has_error_message_containing('{expected_text}')")

        error_messages = self._extract_error_messages()
        response_text = self.response.text

        found_in_json = self._text_found_in_messages(expected_text, error_messages)
        found_in_text = expected_text.lower() in response_text.lower()

        if not (found_in_json or found_in_text):
            self._raise_error_message_not_found(expected_text, error_messages)

        return self

    def _extract_error_messages(self) -> list[str]:
        """Extract error messages from JSON response."""
        error_fields = [
            "error",
            "message",
            "detail",
            "details",
            "description",
            "msg",
            "reason",
            "error_message",
            "error_description",
        ]

        error_messages = []

        try:
            json_data = self._get_json()
            error_messages.extend(
                self._extract_top_level_errors(json_data, error_fields)
            )
            error_messages.extend(self._extract_nested_errors(json_data, error_fields))
        except:
            # If not JSON, continue without JSON error extraction
            pass

        return error_messages

    def _extract_top_level_errors(
        self, json_data: dict, error_fields: list[str]
    ) -> list[str]:
        """Extract error messages from top-level JSON fields."""
        messages = []

        for field in error_fields:
            if field in json_data:
                value = json_data[field]
                messages.extend(self._process_error_value(value))

        return messages

    def _extract_nested_errors(
        self, json_data: dict, error_fields: list[str]
    ) -> list[str]:
        """Extract error messages from nested error objects."""
        messages = []

        if "error" in json_data and isinstance(json_data["error"], dict):
            for field in error_fields:
                if field in json_data["error"]:
                    messages.append(str(json_data["error"][field]))

        return messages

    def _process_error_value(self, value: Any) -> list[str]:
        """Process different types of error values."""
        messages = []

        if isinstance(value, str):
            messages.append(value)
        elif isinstance(value, dict) and "message" in value:
            messages.append(value["message"])
        elif isinstance(value, list):
            messages.extend(self._process_error_list(value))

        return messages

    def _process_error_list(self, error_list: list) -> list[str]:
        """Process list of error items."""
        messages = []

        for item in error_list:
            if isinstance(item, str):
                messages.append(item)
            elif isinstance(item, dict) and "message" in item:
                messages.append(item["message"])

        return messages

    def _text_found_in_messages(
        self, expected_text: str, error_messages: list[str]
    ) -> bool:
        """Check if expected text is found in any error messages."""
        return any(expected_text.lower() in msg.lower() for msg in error_messages)

    def _raise_error_message_not_found(
        self, expected_text: str, error_messages: list[str]
    ) -> None:
        """Raise exception when error message is not found."""
        details = (
            f"Error messages found: {error_messages}"
            if error_messages
            else "No error messages found in common fields"
        )

        raise ResponseValidationError(
            self._format_error_message(
                f"Expected error message containing '{expected_text}'",
                expected=expected_text,
                actual="not found",
                details=details,
            ),
            expected=expected_text,
            actual=error_messages if error_messages else "no error messages",
            assertion_type="error_message",
        )

    # Performance Assertions

    def response_time_less_than(self, max_seconds: float) -> "ResponseAssertion":
        """Assert that response time is less than the specified threshold.

        Args:
        ----
            max_seconds: Maximum acceptable response time in seconds

        Returns:
        -------
            Self for method chaining

        Example:
        -------
            assert_that(response).response_time_less_than(1.0)

        """
        self._add_assertion(f"response_time_less_than({max_seconds})")

        actual_time = self.response.response_time

        if actual_time >= max_seconds:
            raise ResponseValidationError(
                self._format_error_message(
                    f"Response time {actual_time:.3f}s exceeds limit of {max_seconds}s",
                    expected=f"< {max_seconds}s",
                    actual=f"{actual_time:.3f}s",
                    details=f"Response took {actual_time - max_seconds:.3f}s longer than expected",
                ),
                expected=f"< {max_seconds}s",
                actual=f"{actual_time:.3f}s",
                assertion_type="response_time",
            )

        return self

    def response_size_less_than(self, max_bytes: int) -> "ResponseAssertion":
        """Assert that response size is less than the specified threshold.

        Args:
        ----
            max_bytes: Maximum acceptable response size in bytes

        Returns:
        -------
            Self for method chaining

        Example:
        -------
            assert_that(response).response_size_less_than(10000)  # 10KB

        """
        self._add_assertion(f"response_size_less_than({max_bytes})")

        actual_size = len(self.response.content)

        if actual_size >= max_bytes:
            # Format sizes for readability
            def format_size(bytes: int) -> str:
                for unit in ["B", "KB", "MB"]:
                    if bytes < 1024:
                        return f"{bytes}{unit}"
                    bytes //= 1024
                return f"{bytes}GB"

            raise ResponseValidationError(
                self._format_error_message(
                    f"Response size {format_size(actual_size)} exceeds limit of {format_size(max_bytes)}",
                    expected=f"< {format_size(max_bytes)}",
                    actual=format_size(actual_size),
                ),
                expected=f"< {max_bytes} bytes",
                actual=f"{actual_size} bytes",
                assertion_type="response_size",
            )

        return self

    # JSON Schema Validation

    def matches_schema(
        self,
        schema: dict[str, Any] | type[BaseModel] | str | Path,
        schema_type: str = "auto",
    ) -> "ResponseAssertion":
        """Assert that response matches a JSON schema or Pydantic model.

        Supports multiple schema formats:
        - JSON Schema (dict or file path)
        - Pydantic models (BaseModel subclasses)
        - OpenAPI response schemas (with additional context required)

        Args:
        ----
            schema: Schema definition (dict, Pydantic model, or file path)
            schema_type: Schema type hint ("auto", "jsonschema", "pydantic", "openapi")

        Returns:
        -------
            Self for method chaining

        Raises:
        ------
            ResponseValidationError: If validation fails

        Example:
        -------
            # JSON Schema validation
            schema = {"type": "object", "properties": {"id": {"type": "integer"}}}
            assert_that(response).matches_schema(schema)

            # Pydantic model validation
            class User(BaseModel):
                id: int
                name: str
            assert_that(response).matches_schema(User)

        """
        self._add_assertion(f"matches_schema({schema_type})")

        try:
            json_data = self._get_json()

            # Auto-detect schema type if needed
            if schema_type == "auto":
                try:
                    schema_type = self._detect_schema_type(schema)
                except ValueError as e:
                    raise ResponseValidationError(
                        self._format_error_message(
                            f"Schema validation failed: {e}",
                            expected="valid schema type detection",
                            actual="auto-detection error",
                        ),
                        expected="valid schema",
                        actual=str(e),
                        assertion_type="schema_validation",
                    ) from e

            # Validate using appropriate validator
            if schema_type == "pydantic":
                if not isinstance(schema, type) or not issubclass(schema, BaseModel):
                    raise ResponseValidationError(
                        self._format_error_message(
                            "Invalid Pydantic model provided for validation",
                            expected="Pydantic BaseModel subclass",
                            actual=type(schema).__name__,
                        ),
                        expected="Pydantic model",
                        actual=type(schema).__name__,
                        assertion_type="schema_validation",
                    )

                result = self._pydantic_validator.validate(json_data, schema)

            elif schema_type == "jsonschema":
                if isinstance(schema, type) and issubclass(schema, BaseModel):
                    raise ResponseValidationError(
                        self._format_error_message(
                            "Invalid schema type: Pydantic model provided for JSON schema validation",
                            expected="JSON schema (dict, str, or Path)",
                            actual="Pydantic model",
                        ),
                        expected="JSON schema",
                        actual="Pydantic model",
                        assertion_type="schema_validation",
                    )
                result = self._json_schema_validator.validate(json_data, schema)

            elif schema_type == "openapi":
                # For OpenAPI, we need additional context (path, method, status)
                # This is a simplified version - full OpenAPI validation requires more context
                if isinstance(schema, type) and issubclass(schema, BaseModel):
                    raise ResponseValidationError(
                        self._format_error_message(
                            "Invalid schema type: Pydantic model provided for OpenAPI validation",
                            expected="OpenAPI schema (dict, str, or Path)",
                            actual="Pydantic model",
                        ),
                        expected="OpenAPI schema",
                        actual="Pydantic model",
                        assertion_type="schema_validation",
                    )
                result = self._json_schema_validator.validate(json_data, schema)

            else:
                raise ResponseValidationError(
                    self._format_error_message(
                        f"Unsupported schema type: {schema_type}",
                        expected="jsonschema, pydantic, or openapi",
                        actual=schema_type,
                    ),
                    expected="valid schema type",
                    actual=schema_type,
                    assertion_type="schema_validation",
                )

            # Check validation result
            if not result.is_valid:
                error_details = f"Validation time: {result.validation_time_ms:.2f}ms\n"
                error_details += f"Schema type: {result.schema_type}\n"
                error_details += f"Errors: {result.error_summary}"

                raise ResponseValidationError(
                    self._format_error_message(
                        f"Response does not match {schema_type} schema",
                        expected="valid schema match",
                        actual=f"{result.error_count} validation errors",
                        details=error_details,
                    ),
                    expected="valid schema",
                    actual=result.errors,
                    assertion_type="schema_validation",
                )

        except SchemaValidationError as e:
            # Re-raise schema validation errors as response validation errors
            raise ResponseValidationError(
                self._format_error_message(
                    f"Schema validation failed: {e}",
                    expected="valid schema validation",
                    actual="schema validation error",
                ),
                expected="valid schema",
                actual=str(e),
                assertion_type="schema_validation",
            ) from e

        return self

    def matches_openapi_schema(
        self,
        openapi_spec: dict[str, Any],
        path: str,
        method: str,
        status_code: int | None = None,
        content_type: str = "application/json",
    ) -> "ResponseAssertion":
        """Assert that response matches OpenAPI specification schema.

        This method provides full OpenAPI validation with proper context
        including path, method, and status code information.

        Args:
        ----
            openapi_spec: Complete OpenAPI specification dictionary
            path: API path (e.g., "/users/{id}")
            method: HTTP method (e.g., "GET", "POST")
            status_code: Expected status code (uses actual if None)
            content_type: Response content type

        Returns:
        -------
            Self for method chaining

        Example:
        -------
            openapi_spec = load_openapi_spec("api.yaml")
            assert_that(response).matches_openapi_schema(
                openapi_spec, "/users", "GET", 200
            )

        """
        actual_status = status_code or self.response.status_code

        self._add_assertion(f"matches_openapi_schema({path}#{method}#{actual_status})")

        try:
            json_data = self._get_json()

            result = self._openapi_validator.validate_response_schema(
                json_data, openapi_spec, path, method, actual_status, content_type
            )

            if not result.is_valid:
                error_details = f"OpenAPI path: {path}\n"
                error_details += f"Method: {method}\n"
                error_details += f"Status code: {actual_status}\n"
                error_details += f"Content type: {content_type}\n"
                error_details += f"Validation time: {result.validation_time_ms:.2f}ms\n"
                error_details += f"Errors: {result.error_summary}"

                raise ResponseValidationError(
                    self._format_error_message(
                        "Response does not match OpenAPI schema",
                        expected="valid OpenAPI response",
                        actual=f"{result.error_count} validation errors",
                        details=error_details,
                    ),
                    expected="valid OpenAPI schema",
                    actual=result.errors,
                    assertion_type="openapi_validation",
                )

        except Exception as e:
            raise ResponseValidationError(
                self._format_error_message(
                    f"OpenAPI validation failed: {e}",
                    expected="valid OpenAPI validation",
                    actual="validation error",
                ),
                expected="valid OpenAPI schema",
                actual=str(e),
                assertion_type="openapi_validation",
            ) from e

        return self

    def _detect_schema_type(self, schema: Any) -> str:
        """Auto-detect schema type from schema object."""
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            return "pydantic"
        elif isinstance(schema, (dict, str, Path)):
            # Check if it looks like a JSON schema
            if isinstance(schema, dict):
                # Simple heuristic: JSON schemas often have these properties
                if any(
                    key in schema for key in ["type", "properties", "items", "$schema"]
                ):
                    return "jsonschema"
                # Check if it looks like an OpenAPI response schema
                elif any(
                    key in schema for key in ["content", "schema", "application/json"]
                ):
                    return "openapi"
            return "jsonschema"  # Default for dict/string/path
        else:
            raise ValueError(f"Cannot auto-detect schema type for {type(schema)}")

    # Helper Methods

    def _get_json(self) -> dict[str, Any]:
        """Get JSON data from response with caching."""
        if self._json_cache is None:
            self._json_cache = self.response.json_data
        return self._json_cache

    def _extract_json_path(self, path: str) -> Any:
        """Extract value from JSON using dot notation path.

        Handles:
        - Nested objects: "user.profile.name"
        - Array indices: "users[0].email"
        - Mixed: "data.users[0].addresses[1].city"
        """
        current: Any = self._get_json()
        parts = path.split(".")

        for part in parts:
            if "[" in part and part.endswith("]"):
                key, index_part = part.split("[", 1)
                index_part = index_part.rstrip("]")
                if key:
                    if not isinstance(current, dict):
                        raise TypeError(
                            f"Expected dict for key access, got {type(current)}"
                        )
                    current = current[key]
                if index_part.isdigit():
                    idx = int(index_part)
                    if not isinstance(current, list):
                        raise TypeError(
                            f"Expected list for index access, got {type(current)}"
                        )
                    current = current[idx]
                else:
                    current = current[index_part.strip("\"'")]
            else:
                if not isinstance(current, dict):
                    raise TypeError(
                        f"Expected dict for key access, got {type(current)}"
                    )
                current = current[part]

        return current

    def _get_json_preview(self, max_depth: int = 3, max_length: int = 500) -> str:
        """Get a preview of JSON structure for error messages."""
        try:
            data = self._get_json()

            def truncate_data(obj: Any, depth: int = 0) -> Any:
                if depth >= max_depth:
                    return "..."

                if isinstance(obj, dict):
                    return {
                        k: truncate_data(v, depth + 1) for k, v in list(obj.items())[:5]
                    }
                elif isinstance(obj, list):
                    return [truncate_data(item, depth + 1) for item in obj[:3]]
                elif isinstance(obj, str) and len(obj) > 50:
                    return obj[:50] + "..."
                else:
                    return obj

            truncated = truncate_data(data)
            preview = json.dumps(truncated, indent=2)

            if len(preview) > max_length:
                preview = preview[:max_length] + "\n..."

            return preview

        except:
            return "[Unable to generate JSON preview]"


def assert_that(response: EnhancedResponse | Any) -> ResponseAssertion:
    """Create a fluent assertion interface for an API response.

    This is the main entry point for TestAPIX assertions. It creates a
    ResponseAssertion object that provides a fluent interface for making
    assertions about the response.

    Args:
    ----
        response: The response object to make assertions about.
                 Should be an EnhancedResponse from TestAPIX client.

    Returns:
    -------
        ResponseAssertion object for fluent assertion chaining

    Example:
    -------
        response = await client.get("/users")
        assert_that(response) \\
            .has_status(200) \\
            .has_json_path("users[0].email") \\
            .response_time_less_than(1.0)

    The beauty of this approach is that tests read like specifications,
    making them self-documenting and easier to understand.

    """
    if not isinstance(response, EnhancedResponse):
        # Help users who might pass in raw httpx responses
        raise TypeError(
            f"assert_that() expects an EnhancedResponse from TestAPIX client, "
            f"got {type(response).__name__}. "
            f"Make sure you're using TestAPIX's APIClient or SyncAPIClient."
        )

    return ResponseAssertion(response)
