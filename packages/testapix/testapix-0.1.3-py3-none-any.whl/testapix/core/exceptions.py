"""TestAPIX Exception Hierarchy

This module defines the exception types used throughout TestAPIX. Good exception
design is crucial for a testing framework because:

1. Clear errors help users debug test failures quickly
2. Specific exception types allow for precise error handling
3. Rich error context reduces debugging time

The hierarchy follows these principles:
- Each exception type represents a specific category of error
- Exceptions carry relevant context (not just messages)
- Error messages guide users toward solutions
"""

from typing import Any


class TestAPIXError(Exception):
    """Base exception for all TestAPIX errors.

    This allows users to catch all TestAPIX-specific errors with a single
    except clause while still being able to handle specific error types
    when needed.
    """

    def __init__(self, message: str, *args: object, **kwargs: object) -> None:
        """Initialize the exception with an informative message.

        Args:
        ----
            message: Human-readable error description
            *args: Additional positional arguments for Exception
            **kwargs: Additional context stored as instance attributes

        """
        super().__init__(message, *args)
        # Store any additional context as attributes
        for key, value in kwargs.items():
            setattr(self, key, value)


class ConfigurationError(TestAPIXError):
    """Raised when there's an issue with configuration.

    This includes:
    - Missing required configuration
    - Invalid configuration values
    - Configuration file parsing errors
    - Environment variable issues

    The error message should guide users to the specific configuration
    problem and suggest how to fix it.
    """

    def __init__(
        self,
        message: str,
        config_file: str | None = None,
        field: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize configuration error with context.

        Args:
        ----
            message: Description of the configuration problem
            config_file: Path to the problematic config file (if applicable)
            field: Specific configuration field that caused the error
            **kwargs: Additional context

        """
        super().__init__(message, **kwargs)
        self.config_file = config_file
        self.field = field

    def __str__(self) -> str:
        """Provide detailed error message with context."""
        base_msg = super().__str__()
        details = []

        if self.config_file:
            details.append(f"Config file: {self.config_file}")
        if self.field:
            details.append(f"Field: {self.field}")

        if details:
            return f"{base_msg} ({', '.join(details)})"
        return base_msg


class AuthenticationError(TestAPIXError):
    """Raised when authentication fails.

    This helps distinguish authentication issues from other request failures,
    allowing tests to handle auth problems specifically (e.g., refresh tokens,
    retry with different credentials).
    """

    def __init__(
        self,
        message: str,
        auth_type: str | None = None,
        status_code: int | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize authentication error.

        Args:
        ----
            message: Description of the authentication failure
            auth_type: Type of authentication that failed (bearer, api_key, etc.)
            status_code: HTTP status code if available (401, 403, etc.)
            **kwargs: Additional context

        """
        super().__init__(message, **kwargs)
        self.auth_type = auth_type
        self.status_code = status_code


class RequestError(TestAPIXError):
    """Raised when a request fails due to client-side issues.

    This includes:
    - Network connectivity problems
    - Timeout errors
    - Invalid request construction
    - Client-side validation failures

    The error includes request details to aid debugging.
    """

    def __init__(
        self,
        message: str,
        request_data: dict[str, Any] | None = None,
        response_data: dict[str, Any] | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize request error with full context.

        Args:
        ----
            message: Description of what went wrong
            request_data: Details about the failed request (method, url, headers)
            response_data: Details about the response if available
            **kwargs: Additional context

        """
        super().__init__(message, **kwargs)
        self.request_data = request_data or {}
        self.response_data = response_data or {}

    def __str__(self) -> str:
        """Provide detailed error message with request context."""
        base_msg = super().__str__()

        # Add request details if available
        if self.request_data:
            method = self.request_data.get("method", "Unknown")
            url = self.request_data.get("url", "Unknown")
            base_msg += f"\nRequest: {method} {url}"

        # Add response details if available
        if self.response_data:
            status = self.response_data.get("status_code")
            if status:
                base_msg += f"\nResponse Status: {status}"

        return base_msg


class ResponseValidationError(TestAPIXError):
    """Raised when response validation fails in assertions.

    This is the most common error users will see, raised when an assertion
    like assert_that(response).has_status(200) fails. The error includes
    both expected and actual values to make debugging easier.
    """

    def __init__(
        self,
        message: str,
        expected: Any | None = None,
        actual: Any | None = None,
        assertion_type: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize validation error with comparison context.

        Args:
        ----
            message: Description of the validation failure
            expected: What was expected
            actual: What was actually found
            assertion_type: Type of assertion that failed (status, json_path, etc.)
            **kwargs: Additional context

        """
        super().__init__(message, **kwargs)
        self.expected = expected
        self.actual = actual
        self.assertion_type = assertion_type

    def __str__(self) -> str:
        """Provide clear error message showing the mismatch."""
        # The base message should already be descriptive
        # This method exists for future enhancement if needed
        return super().__str__()


class TimeoutError(RequestError):
    """Raised when a request times out.

    This is separated from general RequestError to allow specific handling
    of timeout scenarios, which might need different retry strategies.
    """

    def __init__(
        self, message: str, timeout_seconds: float | None = None, **kwargs: Any
    ) -> None:
        """Initialize timeout error.

        Args:
        ----
            message: Description of the timeout
            timeout_seconds: The timeout value that was exceeded
            **kwargs: Additional context including request_data

        """
        super().__init__(message, **kwargs)
        self.timeout_seconds = timeout_seconds


class DataGenerationError(TestAPIXError):
    """Raised when test data generation fails.

    This helps identify issues with test data generators, which might be due to:
    - Invalid generation parameters
    - Constraint conflicts
    - Resource exhaustion (e.g., can't generate unique values)
    """

    def __init__(
        self,
        message: str,
        generator_type: str | None = None,
        field: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize data generation error.

        Args:
        ----
            message: Description of the generation failure
            generator_type: Type of data being generated (user, product, etc.)
            field: Specific field that failed to generate
            **kwargs: Additional context

        """
        super().__init__(message, **kwargs)
        self.generator_type = generator_type
        self.field = field


class TemplateError(TestAPIXError):
    """Raised when template processing fails.

    This includes:
    - Template file not found
    - Template syntax errors
    - Missing template variables
    - Template rendering failures
    """

    def __init__(
        self,
        message: str,
        template_name: str | None = None,
        template_path: str | None = None,
        missing_variables: list[str] | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize template error with context.

        Args:
        ----
            message: Description of the template problem
            template_name: Name of the template that failed
            template_path: Full path to the template file
            missing_variables: List of missing template variables
            **kwargs: Additional context

        """
        super().__init__(message, **kwargs)
        self.template_name = template_name
        self.template_path = template_path
        self.missing_variables = missing_variables or []

    def __str__(self) -> str:
        """Provide detailed error message with template context."""
        base_msg = super().__str__()
        details = []

        if self.template_name:
            details.append(f"Template: {self.template_name}")
        if self.template_path:
            details.append(f"Path: {self.template_path}")
        if self.missing_variables:
            details.append(f"Missing variables: {', '.join(self.missing_variables)}")

        if details:
            return f"{base_msg} ({', '.join(details)})"
        return base_msg


class ProjectInitializationError(TestAPIXError):
    """Raised when project initialization fails.

    This includes:
    - Directory creation failures
    - File permission issues
    - Template processing errors
    - Configuration validation failures
    """

    def __init__(
        self,
        message: str,
        project_path: str | None = None,
        step: str | None = None,
        recoverable: bool = True,
        suggestions: list[str] | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize project initialization error.

        Args:
        ----
            message: Description of the initialization failure
            project_path: Path where initialization failed
            step: Which initialization step failed
            recoverable: Whether the error can be recovered from
            suggestions: List of suggested solutions
            **kwargs: Additional context

        """
        super().__init__(message, **kwargs)
        self.project_path = project_path
        self.step = step
        self.recoverable = recoverable
        self.suggestions = suggestions or []

    def __str__(self) -> str:
        """Provide detailed error message with recovery suggestions."""
        base_msg = super().__str__()
        details = []

        if self.project_path:
            details.append(f"Project path: {self.project_path}")
        if self.step:
            details.append(f"Failed at step: {self.step}")

        if details:
            base_msg += f" ({', '.join(details)})"

        if self.suggestions:
            suggestions_text = "\n".join(
                f"  • {suggestion}" for suggestion in self.suggestions
            )
            base_msg += f"\n\nSuggestions:\n{suggestions_text}"

        return base_msg


class ValidationError(TestAPIXError):
    """Raised when validation fails.

    This includes:
    - Input parameter validation
    - Configuration validation
    - Data format validation
    - Business rule validation
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: str | None = None,
        valid_options: list[str] | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize validation error.

        Args:
        ----
            message: Description of the validation failure
            field: Field that failed validation
            value: Invalid value that was provided
            valid_options: List of valid options (if applicable)
            **kwargs: Additional context

        """
        super().__init__(message, **kwargs)
        self.field = field
        self.value = value
        self.valid_options = valid_options or []

    def __str__(self) -> str:
        """Provide detailed error message with validation context."""
        base_msg = super().__str__()
        details = []

        if self.field:
            details.append(f"Field: {self.field}")
        if self.value is not None:
            details.append(f"Value: {self.value}")

        if details:
            base_msg += f" ({', '.join(details)})"

        if self.valid_options:
            options_text = ", ".join(self.valid_options)
            base_msg += f"\nValid options: {options_text}"

        return base_msg
