"""Comprehensive JSON Schema Validation Implementation.

This module provides a complete implementation of JSON schema validation
supporting multiple validation backends and schema formats.
"""

import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import ValidationError
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

from testapix.core.exceptions import ValidationError as TestAPIXValidationError

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of schema validation with detailed error information."""

    is_valid: bool
    errors: list[str]
    schema_type: str
    validation_time_ms: float
    schema_path: str | None = None

    @property
    def error_count(self) -> int:
        """Number of validation errors."""
        return len(self.errors)

    @property
    def error_summary(self) -> str:
        """Human-readable summary of validation errors."""
        if self.is_valid:
            return "No validation errors"

        if self.error_count == 1:
            return f"1 validation error: {self.errors[0]}"

        return f"{self.error_count} validation errors: {'; '.join(self.errors[:3])}"


class SchemaValidationError(TestAPIXValidationError):
    """Raised when schema validation fails."""

    def __init__(
        self,
        message: str,
        validation_result: ValidationResult | None = None,
        schema_path: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.validation_result = validation_result
        self.schema_path = schema_path


class SchemaValidator(ABC):
    """Abstract base class for all schema validators."""

    @abstractmethod
    def validate(self, data: Any, schema: Any) -> ValidationResult:
        """Validate data against schema and return detailed result."""
        pass

    @abstractmethod
    def compile_schema(self, schema: Any) -> Any:
        """Compile schema for efficient reuse."""
        pass

    @property
    @abstractmethod
    def validator_type(self) -> str:
        """Type identifier for this validator."""
        pass


class JSONSchemaValidator(SchemaValidator):
    """JSON Schema validator using jsonschema library.

    Supports JSON Schema Draft 7, 2019-09, and 2020-12.
    Provides schema compilation, custom format validation,
    and detailed error reporting.
    """

    def __init__(
        self,
        draft_version: str = "draft7",
        format_checker: jsonschema.FormatChecker | None = None,
        custom_formats: dict[str, Callable[[str], bool]] | None = None,
    ):
        """Initialize JSON Schema validator.

        Args:
            draft_version: JSON Schema draft version ("draft7", "draft201909", "draft202012")
            format_checker: Custom format checker instance
            custom_formats: Dictionary of custom format validators

        """
        self.draft_version = draft_version
        self.format_checker = format_checker or jsonschema.FormatChecker()
        self.custom_formats = custom_formats or {}
        self._compiled_schemas: dict[str, jsonschema.protocols.Validator] = {}

        # Register custom formats
        for format_name, format_func in self.custom_formats.items():
            self.format_checker.checks(format_name)(format_func)  # type: ignore

        # Get validator class based on draft version
        self._validator_class = self._get_validator_class(draft_version)

    def _get_validator_class(self, draft_version: str) -> Any:
        """Get appropriate validator class for draft version."""
        validators = {
            "draft7": jsonschema.Draft7Validator,
            "draft201909": jsonschema.Draft201909Validator,
            "draft202012": jsonschema.Draft202012Validator,
        }

        if draft_version not in validators:
            raise ValueError(f"Unsupported draft version: {draft_version}")

        return validators[draft_version]

    @property
    def validator_type(self) -> str:
        """Type identifier for this validator."""
        return f"jsonschema_{self.draft_version}"

    def compile_schema(self, schema: dict[str, Any] | str | Path) -> Any:
        """Compile JSON schema for efficient validation.

        Args:
            schema: JSON schema as dict, JSON string, or file path

        Returns:
            Compiled validator instance

        """
        # Convert schema to dict if needed
        if isinstance(schema, (str, Path)):
            schema_dict = self._load_schema_from_source(schema)
        else:
            schema_dict = schema

        # Create schema key for caching
        schema_key = json.dumps(schema_dict, sort_keys=True)

        if schema_key not in self._compiled_schemas:
            try:
                validator = self._validator_class(
                    schema_dict, format_checker=self.format_checker
                )
                self._compiled_schemas[schema_key] = validator
                logger.debug(f"Compiled {self.validator_type} schema")
            except Exception as e:
                raise SchemaValidationError(
                    f"Failed to compile JSON schema: {e}",
                    schema_path=str(schema) if isinstance(schema, Path) else None,
                ) from e

        return self._compiled_schemas[schema_key]

    def validate(
        self, data: Any, schema: dict[str, Any] | str | Path
    ) -> ValidationResult:
        """Validate data against JSON schema.

        Args:
            data: Data to validate
            schema: JSON schema as dict, JSON string, or file path

        Returns:
            ValidationResult with detailed validation information

        """
        import time

        start_time = time.perf_counter()

        try:
            # Compile schema
            validator = self.compile_schema(schema)

            # Perform validation
            errors = []
            for error in validator.iter_errors(data):
                error_msg = self._format_validation_error(error)
                errors.append(error_msg)

            validation_time = (time.perf_counter() - start_time) * 1000

            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                schema_type=self.validator_type,
                validation_time_ms=validation_time,
                schema_path=str(schema) if isinstance(schema, Path) else None,
            )

        except Exception as e:
            validation_time = (time.perf_counter() - start_time) * 1000
            return ValidationResult(
                is_valid=False,
                errors=[f"Schema validation failed: {e}"],
                schema_type=self.validator_type,
                validation_time_ms=validation_time,
                schema_path=str(schema) if isinstance(schema, Path) else None,
            )

    def _load_schema_from_source(self, source: str | Path) -> dict[str, Any]:
        """Load schema from string or file path."""
        if isinstance(source, Path):
            try:
                schema_text = source.read_text(encoding="utf-8")
            except Exception as e:
                raise SchemaValidationError(
                    f"Failed to read schema file {source}: {e}"
                ) from e
        else:
            schema_text = source

        try:
            result = json.loads(schema_text)
            if not isinstance(result, dict):
                raise SchemaValidationError("Schema must be a JSON object")
            return result
        except json.JSONDecodeError as e:
            raise SchemaValidationError(f"Invalid JSON in schema: {e}") from e

    def _format_validation_error(self, error: ValidationError) -> str:
        """Format jsonschema ValidationError into readable message."""
        path = (
            " -> ".join(str(p) for p in error.absolute_path)
            if error.absolute_path
            else "root"
        )

        # Handle different types of validation errors
        if error.validator == "required":  # type: ignore
            missing_props = error.validator_value
            if isinstance(missing_props, list):
                missing = ", ".join(f"'{prop}'" for prop in missing_props)
                return f"Missing required properties at '{path}': {missing}"
            else:
                return f"Missing required property at '{path}': '{missing_props}'"

        elif error.validator == "type":  # type: ignore
            expected_type = error.validator_value
            actual_type = type(error.instance).__name__
            return (
                f"Type error at '{path}': expected {expected_type}, got {actual_type}"
            )

        elif error.validator == "enum":  # type: ignore
            valid_values = error.validator_value
            return f"Invalid value at '{path}': must be one of {valid_values}"

        elif error.validator == "format":  # type: ignore
            format_name = error.validator_value
            return (
                f"Format error at '{path}': value does not match format '{format_name}'"
            )

        elif error.validator in ["minimum", "maximum"]:  # type: ignore
            limit = error.validator_value
            operator = ">=" if error.validator == "minimum" else "<="  # type: ignore
            return f"Range error at '{path}': value must be {operator} {limit}"

        elif error.validator in ["minLength", "maxLength"]:  # type: ignore
            limit = error.validator_value
            operator = "at least" if error.validator == "minLength" else "at most"  # type: ignore
            return f"Length error at '{path}': string must be {operator} {limit} characters"

        else:
            # Generic error format
            return f"Validation error at '{path}': {error.message}"


class OpenAPIValidator(JSONSchemaValidator):
    """OpenAPI 3.0/3.1 schema validator.

    Extends JSON Schema validation with OpenAPI-specific features:
    - Response schema validation
    - Request body validation
    - Parameter validation
    - Security scheme validation
    """

    def __init__(self, openapi_version: str = "3.0"):
        """Initialize OpenAPI validator.

        Args:
            openapi_version: OpenAPI version ("3.0" or "3.1")

        """
        self.openapi_version = openapi_version

        # OpenAPI 3.1 uses JSON Schema Draft 2020-12
        # OpenAPI 3.0 uses JSON Schema Draft 7
        draft_version = "draft202012" if openapi_version == "3.1" else "draft7"

        # Add OpenAPI-specific format validators
        custom_formats: dict[str, Callable[[str], bool]] = {
            "byte": self._validate_byte_format,
            "binary": self._validate_binary_format,
            "password": self._validate_password_format,
        }

        super().__init__(draft_version=draft_version, custom_formats=custom_formats)

    @property
    def validator_type(self) -> str:
        """Type identifier for this validator."""
        return f"openapi_{self.openapi_version}"

    def validate_response_schema(
        self,
        response_data: Any,
        openapi_spec: dict[str, Any],
        path: str,
        method: str,
        status_code: int,
        content_type: str = "application/json",
    ) -> ValidationResult:
        """Validate response data against OpenAPI specification.

        Args:
            response_data: Response data to validate
            openapi_spec: Complete OpenAPI specification
            path: API path (e.g., "/users/{id}")
            method: HTTP method (e.g., "get")
            status_code: HTTP status code
            content_type: Response content type

        Returns:
            ValidationResult with validation details

        """
        try:
            # Extract response schema from OpenAPI spec
            schema = self._extract_response_schema(
                openapi_spec, path, method, status_code, content_type
            )

            if not schema:
                return ValidationResult(
                    is_valid=True,
                    errors=[],
                    schema_type=self.validator_type,
                    validation_time_ms=0.0,
                    schema_path=f"{path}#{method}#{status_code}",
                )

            # Validate using extracted schema
            return self.validate(response_data, schema)

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"OpenAPI validation failed: {e}"],
                schema_type=self.validator_type,
                validation_time_ms=0.0,
                schema_path=f"{path}#{method}#{status_code}",
            )

    def _extract_response_schema(
        self,
        openapi_spec: dict[str, Any],
        path: str,
        method: str,
        status_code: int,
        content_type: str,
    ) -> dict[str, Any] | None:
        """Extract response schema from OpenAPI specification."""
        try:
            # Navigate to the response schema
            paths = openapi_spec.get("paths", {})
            path_item = paths.get(path, {})
            operation = path_item.get(method.lower(), {})
            responses = operation.get("responses", {})

            # Try exact status code first, then default
            response = responses.get(str(status_code)) or responses.get("default")
            if not response:
                return None

            content = response.get("content", {})
            media_type = content.get(content_type, {})
            schema = media_type.get("schema", {})

            # Resolve $ref if present
            if "$ref" in schema:
                schema = self._resolve_schema_ref(openapi_spec, schema["$ref"])

            return schema if schema else None

        except (KeyError, TypeError):
            return None

    def _resolve_schema_ref(
        self, openapi_spec: dict[str, Any], ref: str
    ) -> dict[str, Any]:
        """Resolve $ref to actual schema definition."""
        if ref.startswith("#/"):
            # Internal reference
            ref_path = ref[2:].split("/")
            schema = openapi_spec
            for part in ref_path:
                schema = schema[part]
            return schema
        else:
            # External reference - not implemented yet
            raise NotImplementedError("External schema references not supported")

    def _validate_byte_format(self, instance: str) -> bool:
        """Validate base64-encoded byte string."""
        import base64

        try:
            base64.b64decode(instance)
            return True
        except Exception:
            return False

    def _validate_binary_format(self, instance: str) -> bool:
        """Validate binary format (any string)."""
        return isinstance(instance, str)

    def _validate_password_format(self, instance: str) -> bool:
        """Validate password format (any non-empty string)."""
        return isinstance(instance, str) and len(instance) > 0


class PydanticValidator(SchemaValidator):
    """Pydantic model validator for response validation.

    Uses Pydantic models for validation with excellent error messages
    and type coercion capabilities.
    """

    def __init__(self) -> None:
        """Initialize Pydantic validator."""
        self._compiled_models: dict[str, type[BaseModel]] = {}

    @property
    def validator_type(self) -> str:
        """Type identifier for this validator."""
        return "pydantic"

    def compile_schema(self, model_class: type[BaseModel]) -> type[BaseModel]:
        """Compile Pydantic model for validation.

        Args:
            model_class: Pydantic model class

        Returns:
            The model class (no actual compilation needed)

        """
        if not issubclass(model_class, BaseModel):
            raise SchemaValidationError(
                f"Expected Pydantic BaseModel subclass, got {type(model_class)}"
            )

        model_key = f"{model_class.__module__}.{model_class.__name__}"
        self._compiled_models[model_key] = model_class

        return model_class

    def validate(self, data: Any, model_class: type[BaseModel]) -> ValidationResult:
        """Validate data against Pydantic model.

        Args:
            data: Data to validate
            model_class: Pydantic model class

        Returns:
            ValidationResult with validation details

        """
        import time

        start_time = time.perf_counter()

        try:
            # Compile model if needed
            self.compile_schema(model_class)

            # Validate data
            model_class(**data if isinstance(data, dict) else {"value": data})

            validation_time = (time.perf_counter() - start_time) * 1000

            return ValidationResult(
                is_valid=True,
                errors=[],
                schema_type=self.validator_type,
                validation_time_ms=validation_time,
                schema_path=f"{model_class.__module__}.{model_class.__name__}",
            )

        except PydanticValidationError as e:
            validation_time = (time.perf_counter() - start_time) * 1000

            errors = []
            for error in e.errors():
                error_dict = dict(error)
                error_msg = self._format_pydantic_error(error_dict)
                errors.append(error_msg)

            return ValidationResult(
                is_valid=False,
                errors=errors,
                schema_type=self.validator_type,
                validation_time_ms=validation_time,
                schema_path=f"{model_class.__module__}.{model_class.__name__}",
            )

        except Exception as e:
            validation_time = (time.perf_counter() - start_time) * 1000

            return ValidationResult(
                is_valid=False,
                errors=[f"Pydantic validation failed: {e}"],
                schema_type=self.validator_type,
                validation_time_ms=validation_time,
            )

    def _format_pydantic_error(self, error: dict[str, Any]) -> str:
        """Format Pydantic validation error into readable message."""
        location = " -> ".join(str(loc) for loc in error.get("loc", []))
        error_type = error.get("type", "unknown")
        message = error.get("msg", "Validation failed")

        if location:
            return f"Validation error at '{location}': {message} (type: {error_type})"
        else:
            return f"Validation error: {message} (type: {error_type})"
