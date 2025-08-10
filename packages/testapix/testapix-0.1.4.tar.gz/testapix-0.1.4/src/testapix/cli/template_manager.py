"""Template Management System for TestAPIX CLI.

This module provides a comprehensive template management system that handles:
- Template discovery and loading
- Jinja2 template rendering with context validation
- Template caching for performance
- Error handling with detailed context
- Template validation and preprocessing

The template manager supports:
- Multiple template types (configs, tests, docs)
- Template inheritance and includes
- Context validation with helpful error messages
- Template hot-reloading for development
- Custom template filters and functions
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import (
    Environment,
    FileSystemLoader,
    StrictUndefined,
    TemplateSyntaxError,
    UndefinedError,
    select_autoescape,
)
from jinja2 import (
    TemplateError as Jinja2TemplateError,
)
from rich.console import Console

from testapix.core.exceptions import TemplateError, ValidationError

logger = logging.getLogger(__name__)
console = Console()


class TemplateManager:
    """Comprehensive template management system for TestAPIX CLI.

    This class provides a centralized way to manage all template operations,
    ensuring consistency, performance, and proper error handling across
    the CLI commands.
    """

    def __init__(self, templates_dir: Path | None = None):
        """Initialize the template manager.

        Args:
        ----
            templates_dir: Directory containing templates. If None, uses default.

        """
        self._templates_dir = templates_dir or self._get_default_templates_dir()
        self._env: Environment | None = None
        self._template_cache: dict[str, Any] = {}
        self._context_validators: dict[str, set[str]] = {}

        # Ensure templates directory exists
        if not self._templates_dir.exists():
            raise TemplateError(
                f"Templates directory not found: {self._templates_dir}",
                template_path=str(self._templates_dir),
            )

        self._setup_jinja_environment()
        self._discover_templates()

    def _get_default_templates_dir(self) -> Path:
        """Get the default templates directory."""
        # Get the directory containing this file
        current_dir = Path(__file__).parent
        return current_dir / "templates"

    def _setup_jinja_environment(self) -> None:
        """Set up the Jinja2 environment with custom configuration."""
        try:
            self._env = Environment(
                loader=FileSystemLoader(str(self._templates_dir)),
                autoescape=select_autoescape(["html", "xml"]),
                undefined=StrictUndefined,  # Raise errors for undefined variables
                trim_blocks=True,
                lstrip_blocks=True,
            )

            # Add custom filters
            self._env.filters.update(
                {
                    "snake_case": self._to_snake_case,
                    "camel_case": self._to_camel_case,
                    "pascal_case": self._to_pascal_case,
                    "kebab_case": self._to_kebab_case,
                    "safe_filename": self._to_safe_filename,
                    "timestamp": self._format_timestamp,
                }
            )

            # Add custom functions
            self._env.globals.update(
                {
                    "now": datetime.now,
                    "generate_id": self._generate_id,
                    "format_list": self._format_list,
                }
            )

            logger.debug(
                f"Jinja2 environment initialized with templates from {self._templates_dir}"
            )

        except Exception as e:
            raise TemplateError(
                f"Failed to initialize Jinja2 environment: {e}",
                template_path=str(self._templates_dir),
            ) from e

    def _discover_templates(self) -> None:
        """Discover all available templates and cache their metadata."""
        try:
            template_files = list(self._templates_dir.rglob("*.j2"))

            for template_file in template_files:
                # Get relative path from templates directory
                relative_path = template_file.relative_to(self._templates_dir)
                template_name = str(relative_path)

                # Extract template metadata (category, type, etc.)
                parts = relative_path.parts
                category = parts[0] if len(parts) > 1 else "misc"

                self._template_cache[template_name] = {
                    "path": template_file,
                    "category": category,
                    "name": template_name,
                    "last_modified": template_file.stat().st_mtime,
                }

                # Analyze template for required variables
                self._analyze_template_variables(template_name)

            logger.info(f"Discovered {len(template_files)} templates")

        except Exception as e:
            raise TemplateError(f"Failed to discover templates: {e}") from e

    def _analyze_template_variables(self, template_name: str) -> None:
        """Analyze a template to extract required variables."""
        try:
            if not self._env:
                logger.warning(
                    f"Template environment not initialized, skipping analysis for {template_name}"
                )
                self._context_validators[template_name] = set()
                return

            # Get template file path and read source directly
            template_info = self._template_cache.get(template_name)
            if not template_info:
                logger.warning(f"Template {template_name} not found in cache")
                self._context_validators[template_name] = set()
                return

            template_path = template_info["path"]
            template_source = template_path.read_text(encoding="utf-8")

            # Get all undefined variables from the template
            # This is a simplified approach - in practice, this would require
            # more sophisticated AST analysis
            required_vars = set()
            import re

            # Find all {{ variable }} patterns
            variable_pattern = r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*[^}]*\}\}"
            variables = re.findall(variable_pattern, template_source)

            for var in variables:
                # Extract the root variable name (before any dots)
                root_var = var.split(".")[0]
                required_vars.add(root_var)

            # Find all {% if variable %} patterns
            if_pattern = r"\{\%\s*if\s+([a-zA-Z_][a-zA-Z0-9_]*)"
            if_variables = re.findall(if_pattern, template_source)
            required_vars.update(if_variables)

            # Store the required variables
            self._context_validators[template_name] = required_vars

        except Exception as e:
            logger.warning(f"Could not analyze template {template_name}: {e}")
            self._context_validators[template_name] = set()

    def get_available_templates(self, category: str | None = None) -> list[str]:
        """Get list of available templates, optionally filtered by category.

        Args:
        ----
            category: Optional category filter (e.g., 'configs', 'functional')

        Returns:
        -------
            List of template names

        """
        templates = list(self._template_cache.keys())

        if category:
            templates = [
                name
                for name, info in self._template_cache.items()
                if info["category"] == category
            ]

        return sorted(templates)

    def render_template(
        self,
        template_name: str,
        context: dict[str, Any],
        validate_context: bool = False,
    ) -> str:
        """Render a template with the given context.

        Args:
        ----
            template_name: Name of the template to render
            context: Template context variables
            validate_context: Whether to validate context before rendering

        Returns:
        -------
            Rendered template content

        Raises:
        ------
            TemplateError: If template rendering fails
            ValidationError: If context validation fails

        """
        try:
            # Validate context if requested
            if validate_context:
                self._validate_context(template_name, context)

            # Get the template
            if not self._env:
                raise TemplateError("Template environment not initialized")

            template = self._env.get_template(template_name)

            # Add standard context variables
            enhanced_context = {
                **context,
                "timestamp": datetime.now().isoformat(),
                "testapix_version": self._get_testapix_version(),
            }

            # Render the template
            rendered = template.render(enhanced_context)

            logger.debug(f"Successfully rendered template: {template_name}")
            return rendered

        except UndefinedError as e:
            # Extract variable name from error message
            var_name = str(e).split("'")[1] if "'" in str(e) else "unknown"
            raise TemplateError(
                f"Template variable '{var_name}' is not defined",
                template_name=template_name,
                missing_variables=[var_name],
            ) from e

        except TemplateSyntaxError as e:
            raise TemplateError(
                f"Template syntax error: {e.message}",
                template_name=template_name,
                template_path=str(e.filename) if e.filename else None,
            ) from e

        except Jinja2TemplateError as e:
            raise TemplateError(
                f"Template rendering failed: {str(e)}", template_name=template_name
            ) from e

        except Exception as e:
            raise TemplateError(
                f"Unexpected error rendering template: {str(e)}",
                template_name=template_name,
            ) from e

    def render_to_file(
        self,
        template_name: str,
        output_path: Path,
        context: dict[str, Any],
        create_dirs: bool = True,
    ) -> None:
        """Render a template directly to a file.

        Args:
        ----
            template_name: Name of the template to render
            output_path: Path where the rendered content should be written
            context: Template context variables
            create_dirs: Whether to create parent directories if they don't exist

        """
        try:
            # Create parent directories if needed
            if create_dirs and not output_path.parent.exists():
                output_path.parent.mkdir(parents=True, exist_ok=True)

            # Render the template
            content = self.render_template(template_name, context)

            # Write to file
            output_path.write_text(content, encoding="utf-8")

            logger.debug(f"Template {template_name} rendered to {output_path}")

        except Exception as e:
            raise TemplateError(
                f"Failed to render template to file: {str(e)}",
                template_name=template_name,
                template_path=str(output_path),
            ) from e

    def _validate_context(self, template_name: str, context: dict[str, Any]) -> None:
        """Validate that the context contains all required variables.

        Args:
        ----
            template_name: Name of the template
            context: Context to validate

        Raises:
        ------
            ValidationError: If required variables are missing

        """
        required_vars = self._context_validators.get(template_name, set())
        provided_vars = set(context.keys())
        missing_vars = required_vars - provided_vars

        if missing_vars:
            raise ValidationError(
                f"Missing required template variables: {', '.join(sorted(missing_vars))}",
                field="template_context",
                value=f"provided: {', '.join(sorted(provided_vars))}",
                valid_options=sorted(required_vars),
            )

    def _get_testapix_version(self) -> str:
        """Get the current TestAPIX version."""
        try:
            # Try to get version from package metadata
            import importlib.metadata

            return importlib.metadata.version("testapix")
        except Exception:
            # Fallback version
            return "0.1.0"

    # Custom Jinja2 filters
    def _to_snake_case(self, text: str) -> str:
        """Convert text to snake_case."""
        import re

        # Replace spaces and hyphens with underscores
        text = re.sub(r"[-\s]+", "_", text)
        # Insert underscores before uppercase letters
        text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", text)
        return text.lower()

    def _to_camel_case(self, text: str) -> str:
        """Convert text to camelCase."""
        snake = self._to_snake_case(text)
        parts = snake.split("_")
        return parts[0].lower() + "".join(word.capitalize() for word in parts[1:])

    def _to_pascal_case(self, text: str) -> str:
        """Convert text to PascalCase."""
        snake = self._to_snake_case(text)
        return "".join(word.capitalize() for word in snake.split("_"))

    def _to_kebab_case(self, text: str) -> str:
        """Convert text to kebab-case."""
        return self._to_snake_case(text).replace("_", "-")

    def _to_safe_filename(self, text: str) -> str:
        """Convert text to a safe filename."""
        import re

        # Remove or replace unsafe characters
        safe = re.sub(r"[^\w\-_\.]", "_", text)
        # Remove consecutive underscores
        safe = re.sub(r"_+", "_", safe)
        # Remove leading/trailing underscores
        return safe.strip("_")

    def _format_timestamp(
        self, dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S"
    ) -> str:
        """Format a datetime object."""
        return dt.strftime(format_str)

    # Custom Jinja2 functions
    def _generate_id(self, prefix: str = "id") -> str:
        """Generate a unique ID."""
        import uuid

        return f"{prefix}_{uuid.uuid4().hex[:8]}"

    def _format_list(self, items: list[Any], separator: str = ", ") -> str:
        """Format a list as a string."""
        return separator.join(str(item) for item in items)


# Singleton instance for easy importing
template_manager = TemplateManager()
