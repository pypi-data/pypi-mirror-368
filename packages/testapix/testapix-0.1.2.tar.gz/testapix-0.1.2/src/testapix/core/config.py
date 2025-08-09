"""TestAPIX Configuration Management

This module implements a sophisticated layered configuration system that solves
real-world testing challenges:

1. Environment-Specific Settings: Run the same tests against different environments
2. Secret Management: Never hardcode credentials, use environment variables
3. Configuration Validation: Catch configuration errors early with clear messages
4. Flexible Overrides: Override any setting at runtime for special cases

The configuration precedence (highest to lowest):
1. Runtime overrides (passed to load_config)
2. Environment variables (TESTAPIX_* prefix)
3. Environment-specific YAML files (test.yaml, staging.yaml)
4. Base configuration file (base.yaml)
5. Default values in Pydantic models

This design allows teams to share base configurations while customizing for
their specific needs without modifying code.
"""

import logging
import os
from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .exceptions import ConfigurationError

# Configure logging
logger = logging.getLogger(__name__)


class LogLevel(str, Enum):
    """Supported logging levels for TestAPIX."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AuthConfig(BaseModel):
    """Authentication configuration.

    Supports multiple authentication types with appropriate validation
    for each type. The configuration can be minimal (just type and token)
    or comprehensive (OAuth2 with all parameters).
    """

    model_config = ConfigDict(
        extra="allow"
    )  # Allow additional fields for extensibility

    type: str = Field(description="Authentication type: bearer, api_key, oauth2, basic")

    # Bearer token authentication
    token: str | None = Field(
        default=None, description="Bearer token value (use env var in production)"
    )

    # API key authentication
    api_key: str | None = Field(
        default=None, description="API key value (use env var in production)"
    )
    header_name: str = Field(
        default="X-API-Key", description="Header name for API key authentication"
    )

    # OAuth2 authentication
    client_id: str | None = Field(default=None, description="OAuth2 client ID")
    client_secret: str | None = Field(
        default=None, description="OAuth2 client secret (use env var!)"
    )
    token_url: str | None = Field(default=None, description="OAuth2 token endpoint URL")
    scope: str | None = Field(
        default=None, description="OAuth2 scope(s) space-separated"
    )

    # Basic authentication
    username: str | None = Field(default=None, description="Basic auth username")
    password: str | None = Field(
        default=None, description="Basic auth password (use env var!)"
    )

    @field_validator("type")
    @classmethod
    def validate_auth_type(cls, v: str) -> str:
        """Ensure auth type is supported."""
        supported = {"bearer", "api_key", "oauth2", "basic"}
        if v.lower() not in supported:
            raise ValueError(
                f"Unsupported auth type: {v}. "
                f"Supported types: {', '.join(sorted(supported))}"
            )
        return v.lower()

    @field_validator("token")
    @classmethod
    def validate_token_for_bearer(cls, v: str | None, info: Any) -> str | None:
        """Ensure token is provided for bearer auth."""
        if info.data.get("type") == "bearer" and not v:
            logger.warning(
                "Bearer auth configured without token. "
                "Set TESTAPIX_AUTH__TOKEN environment variable."
            )
        return v

    @field_validator("api_key")
    @classmethod
    def validate_api_key_for_api_key_auth(cls, v: str | None, info: Any) -> str | None:
        """Ensure API key is provided for API key auth."""
        if info.data.get("type") == "api_key" and not v:
            logger.warning(
                "API key auth configured without key. "
                "Set TESTAPIX_AUTH__API_KEY environment variable."
            )
        return v


class HTTPConfig(BaseModel):
    """HTTP client configuration.

    These settings control how TestAPIX makes HTTP requests. The defaults
    are chosen for reliability in testing scenarios.
    """

    model_config = ConfigDict(extra="forbid")  # Strict validation

    base_url: str = Field(
        description="Base URL for API requests (e.g., https://api.example.com)"
    )
    timeout: float = Field(default=30.0, gt=0, description="Request timeout in seconds")
    retries: int = Field(
        default=3, ge=0, description="Number of retry attempts for failed requests"
    )
    retry_delay: float = Field(
        default=1.0, ge=0, description="Initial delay between retries in seconds"
    )
    retry_backoff: float = Field(
        default=2.0,
        ge=1.0,
        description="Backoff multiplier for exponential retry delay",
    )
    follow_redirects: bool = Field(
        default=True, description="Whether to automatically follow HTTP redirects"
    )
    verify_ssl: bool = Field(
        default=True, description="Whether to verify SSL certificates"
    )
    headers: dict[str, str] = Field(
        default_factory=dict, description="Default headers to include in all requests"
    )

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Ensure base URL is properly formatted."""
        if not v:
            raise ValueError("base_url cannot be empty")

        if not v.startswith(("http://", "https://")):
            raise ValueError(f"base_url must start with http:// or https://, got: {v}")

        # Remove trailing slash for consistency
        return v.rstrip("/")

    @field_validator("headers")
    @classmethod
    def validate_headers(cls, v: dict[str, str]) -> dict[str, str]:
        """Set default User-Agent if not provided."""
        if "User-Agent" not in v:
            v["User-Agent"] = "TestAPIX/0.1.0"
        return v

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v: float) -> float:
        """Validate timeout is reasonable."""
        if v <= 0:
            raise ValueError("timeout must be positive")
        if v > 300:  # 5 minutes
            logger.warning(
                f"Timeout of {v}s is very high. "
                "Consider using a smaller timeout for better test performance."
            )
        return v

    @field_validator("retries")
    @classmethod
    def validate_retries(cls, v: int) -> int:
        """Validate retry count is reasonable."""
        if v < 0:
            raise ValueError("retries cannot be negative")
        if v > 10:
            logger.warning(
                f"Retry count of {v} is very high. "
                "This may cause tests to run very slowly on failures."
            )
        return v

    @field_validator("retry_delay")
    @classmethod
    def validate_retry_delay(cls, v: float) -> float:
        """Validate retry delay is reasonable."""
        if v < 0:
            raise ValueError("retry_delay cannot be negative")
        if v > 60:  # 1 minute
            logger.warning(
                f"Retry delay of {v}s is very high. "
                "This may cause tests to run very slowly."
            )
        return v


class DatabaseConfig(BaseModel):
    """Database configuration for test data management.

    This configuration controls how TestAPIX handles test data cleanup
    and database interactions during testing.
    """

    model_config = ConfigDict(extra="allow")

    enabled: bool = Field(
        default=False, description="Whether database integration is enabled"
    )
    url: str | None = Field(
        default=None,
        description="Database connection URL (use env var for credentials)",
    )
    cleanup_strategy: str = Field(
        default="immediate", description="Test data cleanup strategy"
    )
    cleanup_batch_size: int = Field(
        default=100, gt=0, description="Number of records to clean up in each batch"
    )

    @field_validator("cleanup_strategy")
    @classmethod
    def validate_cleanup_strategy(cls, v: str) -> str:
        """Validate cleanup strategy."""
        valid_strategies = {
            "immediate",  # Clean up immediately after each test
            "batch",  # Clean up in batches after test suite
            "manual",  # No automatic cleanup
            "environment",  # Clean up based on environment (e.g., not in prod)
        }
        if v not in valid_strategies:
            raise ValueError(
                f"Invalid cleanup strategy: {v}. "
                f"Valid strategies: {', '.join(sorted(valid_strategies))}"
            )
        return v

    @field_validator("url")
    @classmethod
    def validate_url_when_enabled(cls, v: str | None, info: Any) -> str | None:
        """Ensure URL is provided when database is enabled and properly formatted."""
        if info.data.get("enabled"):
            if not v:
                raise ValueError(
                    "Database URL required when database.enabled=true. "
                    "Set database.url in config or TESTAPIX_DATABASE__URL env var."
                )

            # Validate database URL format
            supported_schemes = {
                "postgresql",
                "postgres",
                "mysql",
                "sqlite",
                "mongodb",
                "redis",
                "oracle",
                "mssql",
                "cockroachdb",
            }

            if "://" not in v:
                raise ValueError(
                    f"Invalid database URL format: {v}. "
                    "URL must include scheme (e.g., postgresql://user:pass@host/db)"
                )

            scheme = v.split("://")[0].lower()
            if scheme not in supported_schemes:
                logger.warning(
                    f"Unsupported database scheme '{scheme}'. "
                    f"Supported schemes: {', '.join(sorted(supported_schemes))}"
                )

            # Validate sqlite special case
            if scheme == "sqlite":
                path_part = v.split("://", 1)[1]
                if not path_part or path_part.startswith("//"):
                    raise ValueError(
                        f"Invalid SQLite URL: {v}. "
                        "Use format: sqlite:///path/to/database.db"
                    )

        return v


class ReportingConfig(BaseModel):
    """Test reporting configuration.

    Controls how test results are formatted and where they're saved.
    Different formats serve different purposes:
    - console: Human-readable output during development
    - html: Detailed reports for debugging
    - json: Machine-readable for CI/CD integration
    - junit: Standard format for test tools
    """

    model_config = ConfigDict(extra="allow")

    enabled: bool = Field(default=True, description="Whether reporting is enabled")
    formats: list[str] = Field(
        default=["console"], description="Output formats for test reports"
    )
    output_dir: str = Field(
        default="reports", description="Directory for saving report files"
    )
    include_request_data: bool = Field(
        default=True, description="Include full request/response data in reports"
    )
    include_timing: bool = Field(
        default=True, description="Include performance timing information"
    )
    max_response_size: int = Field(
        default=10000,
        gt=0,
        description="Maximum response size to include in reports (bytes)",
    )

    @field_validator("formats")
    @classmethod
    def validate_formats(cls, v: list[str]) -> list[str]:
        """Validate report formats."""
        valid_formats = {"console", "html", "json", "junit", "xml"}
        invalid = set(v) - valid_formats

        if invalid:
            raise ValueError(
                f"Invalid report formats: {', '.join(invalid)}. "
                f"Valid formats: {', '.join(sorted(valid_formats))}"
            )

        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for fmt in v:
            if fmt not in seen:
                seen.add(fmt)
                unique.append(fmt)

        return unique


class TestAPIXConfig(BaseSettings):
    """Main TestAPIX configuration model.

    This is the root configuration that combines all sub-configurations.
    It uses Pydantic Settings to automatically load from environment variables
    with the TESTAPIX_ prefix.

    Environment variable examples:
    - TESTAPIX_ENVIRONMENT=staging
    - TESTAPIX_LOG_LEVEL=DEBUG
    - TESTAPIX_HTTP__BASE_URL=https://staging-api.example.com
    - TESTAPIX_AUTH__TOKEN=secret-token-value
    """

    model_config = SettingsConfigDict(
        # Environment variable settings
        env_prefix="TESTAPIX_",
        env_nested_delimiter="__",  # Allows TESTAPIX_HTTP__TIMEOUT=60
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Allow extra fields for extensibility
        extra="allow",
        # Validate default values
        validate_default=True,
    )

    # Basic settings
    project_name: str = Field(
        default="api-tests", description="Name of the testing project"
    )
    environment: str = Field(
        default="local",
        description="Current environment (local, dev, test, staging, prod)",
    )
    log_level: LogLevel = Field(
        default=LogLevel.INFO, description="Logging level for TestAPIX"
    )

    # Sub-configurations
    http: HTTPConfig = Field(description="HTTP client configuration")
    auth: AuthConfig | None = Field(
        default=None, description="Authentication configuration (optional)"
    )
    database: DatabaseConfig = Field(
        default_factory=DatabaseConfig,
        description="Database configuration for test data",
    )
    reporting: ReportingConfig = Field(
        default_factory=ReportingConfig, description="Test reporting configuration"
    )

    # Test execution settings
    parallel_workers: int = Field(
        default=1, ge=1, description="Number of parallel test workers"
    )
    test_data_cleanup: bool = Field(
        default=True, description="Whether to automatically clean up test data"
    )
    fail_fast: bool = Field(
        default=False, description="Stop test execution on first failure"
    )
    random_seed: int | None = Field(
        default=None, description="Random seed for reproducible test data generation"
    )

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate and normalize environment name."""
        if not v or not v.strip():
            raise ValueError("environment cannot be empty")

        # Common environment aliases
        aliases = {
            "dev": "development",
            "prod": "production",
            "local": "local",
            "test": "test",
            "testing": "test",
            "staging": "staging",
            "stage": "staging",
            "qa": "test",
        }

        normalized = aliases.get(v.lower().strip(), v.lower().strip())

        # Warn about production environment
        if normalized in ("production", "prod"):
            logger.warning(
                "Running tests against PRODUCTION environment. "
                "Ensure this is intentional and test data cleanup is configured."
            )

        logger.info(f"Running in {normalized} environment")
        return normalized

    @field_validator("parallel_workers")
    @classmethod
    def validate_parallel_workers(cls, v: int) -> int:
        """Validate parallel worker count is reasonable."""
        if v <= 0:
            raise ValueError("parallel_workers must be positive")
        if v > 50:
            logger.warning(
                f"Very high parallel worker count ({v}). "
                "This may overwhelm the target API or cause rate limiting."
            )
        return v

    @field_validator("random_seed")
    @classmethod
    def validate_random_seed(cls, v: int | None) -> int | None:
        """Validate random seed if provided."""
        if v is not None and v < 0:
            logger.warning(
                f"Negative random seed ({v}) may cause unexpected behavior. "
                "Consider using a positive integer."
            )
        return v


class ConfigManager:
    """Configuration manager that implements the layered loading strategy.

    This class handles:
    1. Loading YAML configuration files
    2. Merging configurations according to precedence rules
    3. Validating the final configuration
    4. Caching loaded configurations

    The manager is designed to be used as a singleton through the
    module-level functions (load_config, get_current_config).
    """

    def __init__(self, config_dir: Path | None = None):
        """Initialize configuration manager.

        Args:
        ----
            config_dir: Directory containing configuration files
                       (defaults to ./configs)

        """
        self.config_dir = config_dir or Path.cwd() / "configs"
        self._config_cache: TestAPIXConfig | None = None

        logger.debug(f"ConfigManager initialized with directory: {self.config_dir}")

    def load_config(
        self,
        environment: str | None = None,
        config_overrides: dict[str, Any] | None = None,
    ) -> TestAPIXConfig:
        """Load configuration with layered approach.

        Loading order (each layer overrides previous):
        1. Default values from Pydantic models
        2. base.yaml (if exists)
        3. {environment}.yaml (if exists)
        4. Environment variables (TESTAPIX_*)
        5. Runtime overrides (config_overrides parameter)

        Args:
        ----
            environment: Target environment name
            config_overrides: Runtime configuration overrides

        Returns:
        -------
            Validated configuration object

        Raises:
        ------
            ConfigurationError: If configuration is invalid

        """
        # Determine environment
        env = environment or os.getenv("TESTAPIX_ENVIRONMENT", "local")
        logger.info(f"Loading configuration for environment: {env}")

        try:
            # Start with base configuration
            config_data = self._load_base_config()

            # Apply environment-specific overrides
            env_config = self._load_environment_config(env if env is not None else "")
            if env_config:
                logger.debug(f"Applying {env} environment configuration")
                config_data = self._merge_configs(config_data, env_config)

            # Apply runtime overrides
            if config_overrides:
                logger.debug("Applying runtime configuration overrides")
                config_data = self._merge_configs(config_data, config_overrides)

            # Set the environment in config
            config_data["environment"] = env

            # Apply environment variables manually
            env_overrides = self._load_env_overrides()
            if env_overrides:
                logger.debug("Applying environment variable overrides")
                config_data = self._merge_configs(config_data, env_overrides)

            # Create and validate configuration
            config = TestAPIXConfig(**config_data)

            # Cache the configuration
            self._config_cache = config

            logger.info(
                f"Configuration loaded successfully for {config.environment} "
                f"environment with base URL: {config.http.base_url}"
            )

            return config

        except yaml.YAMLError as e:
            config_file = None
            if hasattr(e, "problem_mark") and e.problem_mark and e.problem_mark.name:
                config_file = str(e.problem_mark.name)
            raise ConfigurationError(
                f"Failed to parse YAML configuration: {e}",
                config_file=config_file,
            )
        except ValueError as e:
            # Pydantic validation errors
            raise ConfigurationError(
                f"Configuration validation failed: {e}",
                details={"validation_error": str(e), "environment": env},
            ) from e
        except Exception as e:
            # Wrap any other errors in ConfigurationError
            raise ConfigurationError(
                f"Unexpected error loading configuration: {e}",
                details={"error_type": type(e).__name__, "environment": env},
            ) from e

    def _load_base_config(self) -> dict[str, Any]:
        """Load base configuration file."""
        base_file = self.config_dir / "base.yaml"

        if not base_file.exists():
            logger.warning(
                f"Base configuration not found at {base_file}. Using minimal defaults."
            )
            # Return minimal required configuration
            return {"http": {"base_url": "http://localhost:8000"}}

        logger.debug(f"Loading base configuration from {base_file}")
        return self._load_yaml_file(base_file)

    def _load_environment_config(self, environment: str) -> dict[str, Any] | None:
        """Load environment-specific configuration if it exists."""
        env_file = self.config_dir / f"{environment}.yaml"

        if not env_file.exists():
            logger.debug(
                f"No environment-specific config found for {environment} at {env_file}"
            )
            return None

        logger.debug(f"Loading {environment} configuration from {env_file}")
        return self._load_yaml_file(env_file)

    def _load_yaml_file(self, file_path: Path) -> dict[str, Any]:
        """Load and parse a YAML configuration file.

        Args:
        ----
            file_path: Path to YAML file

        Returns:
        -------
            Parsed configuration data

        Raises:
        ------
            ConfigurationError: If file cannot be read or parsed

        """
        try:
            # Check file exists and is readable
            if not file_path.exists():
                raise ConfigurationError(
                    f"Configuration file not found: {file_path}",
                    config_file=str(file_path),
                )

            if not file_path.is_file():
                raise ConfigurationError(
                    f"Configuration path is not a file: {file_path}",
                    config_file=str(file_path),
                )

            # Check file permissions
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
            except PermissionError:
                raise ConfigurationError(
                    f"Permission denied reading configuration file: {file_path}",
                    config_file=str(file_path),
                )
            except UnicodeDecodeError as e:
                raise ConfigurationError(
                    f"Invalid UTF-8 encoding in configuration file {file_path}: {e}",
                    config_file=str(file_path),
                )

            # Handle empty files
            if not content.strip():
                logger.debug(f"Empty configuration file: {file_path}")
                return {}

            # Parse YAML with additional safety checks
            try:
                data = yaml.safe_load(content)
            except yaml.constructor.ConstructorError as e:
                raise ConfigurationError(
                    f"Invalid YAML structure in {file_path}: {e}. "
                    "Ensure all values use supported YAML types.",
                    config_file=str(file_path),
                )
            except yaml.scanner.ScannerError as e:
                raise ConfigurationError(
                    f"YAML syntax error in {file_path}: {e}. "
                    "Check indentation and special characters.",
                    config_file=str(file_path),
                )

            # Validate that root is a dictionary
            if data is None:
                logger.debug(
                    f"Configuration file contains only comments/whitespace: {file_path}"
                )
                return {}
            elif not isinstance(data, dict):
                raise ConfigurationError(
                    f"Configuration root must be a dictionary/object, got {type(data).__name__} in {file_path}",
                    config_file=str(file_path),
                )

            # Validate no null keys
            self._validate_config_structure(data, file_path)

            return data

        except ConfigurationError:
            # Re-raise our own errors
            raise
        except yaml.YAMLError as e:
            raise ConfigurationError(
                f"Invalid YAML in {file_path}: {e}", config_file=str(file_path)
            )
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load {file_path}: {e}", config_file=str(file_path)
            )

    def _validate_config_structure(self, data: dict[str, Any], file_path: Path) -> None:
        """Validate configuration structure for common issues.

        Args:
        ----
            data: Configuration data to validate
            file_path: Path to the configuration file (for error reporting)

        Raises:
        ------
            ConfigurationError: If structure is invalid

        """

        def check_recursive(obj: Any, path: str = "") -> None:
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key is None:
                        raise ConfigurationError(
                            f"Null key found in configuration at {path or 'root'} in {file_path}",
                            config_file=str(file_path),
                        )
                    if not isinstance(key, str):
                        raise ConfigurationError(
                            f"Non-string key '{key}' found at {path or 'root'} in {file_path}. "
                            "All keys must be strings.",
                            config_file=str(file_path),
                        )

                    current_path = f"{path}.{key}" if path else key

                    # Check for reserved key names that might cause issues
                    reserved_keys = {"__class__", "__module__", "__dict__", "__doc__"}
                    if key in reserved_keys:
                        logger.warning(
                            f"Reserved key name '{key}' found at {current_path} in {file_path}. "
                            "This may cause unexpected behavior."
                        )

                    check_recursive(value, current_path)

            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_recursive(item, f"{path}[{i}]")

        check_recursive(data)

    def _merge_configs(
        self, base: dict[str, Any], override: dict[str, Any]
    ) -> dict[str, Any]:
        """Recursively merge configuration dictionaries.

        This performs a deep merge where:
        - Scalar values in override replace base values
        - Lists in override replace base lists entirely
        - Dictionaries are merged recursively

        This allows for partial overrides of nested configuration.

        Args:
        ----
            base: Base configuration
            override: Configuration to merge on top

        Returns:
        -------
            Merged configuration

        """
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                # Recursively merge nested dictionaries
                result[key] = self._merge_configs(result[key], value)
            else:
                # Override scalar values and lists
                result[key] = value

        return result

    def _load_env_overrides(self) -> dict[str, Any]:
        """Load environment variable overrides with TESTAPIX_ prefix.

        Converts TESTAPIX_HTTP__BASE_URL to {"http": {"base_url": "..."}}

        Returns
        -------
            Dictionary of environment variable overrides

        """
        env_overrides: dict[str, Any] = {}
        prefix = "TESTAPIX_"

        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Remove prefix and convert to lowercase
                config_key = key[len(prefix) :].lower()

                # Handle nested keys (e.g., HTTP__BASE_URL -> http.base_url)
                parts = config_key.split("__")

                # Convert string values to appropriate types
                converted_value = self._convert_env_value(value)

                # Build nested dictionary
                current = env_overrides
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = converted_value

        return env_overrides

    def _convert_env_value(self, value: str) -> Any:
        """Convert environment variable string to appropriate type."""
        # Handle boolean values
        if value.lower() in ("true", "false"):
            return value.lower() == "true"

        # Handle numeric values
        try:
            if "." in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass

        # Return as string
        return value

    def get_config(self) -> TestAPIXConfig | None:
        """Get the currently loaded configuration.

        Returns
        -------
            Cached configuration or None if not loaded

        """
        return self._config_cache

    def reload_config(
        self,
        environment: str | None = None,
        config_overrides: dict[str, Any] | None = None,
    ) -> TestAPIXConfig:
        """Force reload configuration, clearing the cache.

        This is useful when configuration files have changed or
        when switching environments.

        Args:
        ----
            environment: Target environment
            config_overrides: Runtime overrides

        Returns:
        -------
            Newly loaded configuration

        """
        logger.info("Reloading configuration")
        self._config_cache = None
        return self.load_config(environment, config_overrides)


# Global configuration manager instance
_config_manager = ConfigManager()


def load_config(
    environment: str | None = None,
    config_dir: Path | None = None,
    config_overrides: dict[str, Any] | None = None,
) -> TestAPIXConfig:
    """Load TestAPIX configuration.

    This is the main entry point for loading configuration in TestAPIX.
    It handles the complexity of layered configuration loading while
    providing a simple interface for users.

    Args:
    ----
        environment: Target environment name (defaults to TESTAPIX_ENVIRONMENT or "local")
        config_dir: Directory containing config files (defaults to ./configs)
        config_overrides: Runtime configuration overrides

    Returns:
    -------
        Loaded and validated configuration

    Examples:
    --------
        # Load default configuration
        config = load_config()

        # Load staging configuration
        config = load_config(environment="staging")

        # Load with custom base URL
        config = load_config(
            environment="test",
            config_overrides={"http": {"base_url": "https://test-api.example.com"}}
        )

    """
    global _config_manager

    # Create new manager if config_dir is specified
    if config_dir:
        _config_manager = ConfigManager(config_dir)

    return _config_manager.load_config(environment, config_overrides)


def get_current_config() -> TestAPIXConfig | None:
    """Get the currently loaded configuration.

    Returns:
    -------
        Current configuration or None if not loaded

    Example:
    -------
        config = get_current_config()
        if config:
            print(f"Running against: {config.http.base_url}")

    """
    return _config_manager.get_config()


def reload_config(
    environment: str | None = None, config_overrides: dict[str, Any] | None = None
) -> TestAPIXConfig:
    """Reload configuration, clearing any cached values.

    This is useful when configuration files have changed during
    test execution or when switching between environments.

    Args:
    ----
        environment: Target environment
        config_overrides: Runtime overrides

    Returns:
    -------
        Newly loaded configuration

    """
    return _config_manager.reload_config(environment, config_overrides)
