"""Project Initialization Command

This module handles creating new TestAPIX projects with appropriate templates,
configuration files, and example tests. The philosophy is to create projects
that work immediately while teaching best practices through examples.

The initialization process creates:
1. A well-organized directory structure
2. Configuration files for different environments
3. Working example tests that demonstrate patterns
4. Comprehensive documentation
5. All necessary support files (requirements, .env template, etc.)

Every generated file includes helpful comments and serves as both a working
example and a learning resource.
"""

from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from testapix.cli.template_manager import template_manager
from testapix.core.exceptions import (
    ProjectInitializationError,
    TemplateError,
    ValidationError,
)

console = Console()


def init_project(
    project_name: str,
    template: str = "basic",
    api_type: str = "rest",
    auth_type: str | None = None,
    base_url: str | None = None,
    force: bool = False,
    verbose: bool = False,
) -> bool:
    """Initialize a new TestAPIX project with the specified configuration.

    This function creates a complete project structure including:
    - Directory hierarchy for tests, configs, and data
    - Configuration files with sensible defaults
    - Example tests that work out of the box
    - Documentation to get users started

    Args:
    ----
        project_name: Name of the project directory to create
        template: Project template (basic, advanced, microservices)
        api_type: Type of API (rest, graphql, grpc)
        auth_type: Authentication type (bearer, api_key, oauth2, basic)
        base_url: Base URL for the API
        force: Whether to overwrite existing directory
        verbose: Enable verbose output

    Returns:
    -------
        True if successful

    Raises:
    ------
        ProjectInitializationError: If project creation fails
        ValidationError: If input validation fails

    """
    try:
        # Validate all inputs
        _validate_inputs(project_name, template, api_type, auth_type)

        project_path = Path.cwd() / project_name

        # Check if directory exists
        if project_path.exists() and not force:
            if any(project_path.iterdir()):
                suggestions = [
                    "Use --force to overwrite the existing directory",
                    "Choose a different project name",
                    "Remove the existing directory manually",
                ]
                raise ProjectInitializationError(
                    f"Directory '{project_name}' already exists and is not empty",
                    project_path=str(project_path),
                    step="directory_check",
                    suggestions=suggestions,
                )

        # Create project directory
        try:
            project_path.mkdir(exist_ok=True)
        except PermissionError:
            suggestions = [
                "Check that you have write permissions to the current directory",
                "Try running with appropriate permissions",
                "Choose a different location for the project",
            ]
            raise ProjectInitializationError(
                f"Permission denied creating directory '{project_name}'",
                project_path=str(project_path),
                step="directory_creation",
                suggestions=suggestions,
            )
        except OSError as e:
            raise ProjectInitializationError(
                f"Failed to create directory '{project_name}': {e}",
                project_path=str(project_path),
                step="directory_creation",
            )

        if verbose:
            console.print(f"📁 Created project directory: {project_path}")

        # Prepare template context
        context = _prepare_template_context(
            project_name=project_name,
            template=template,
            api_type=api_type,
            auth_type=auth_type,
            base_url=base_url,
        )

        # Create project structure with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Add tasks
            structure_task = progress.add_task(
                "Creating directory structure...", total=1
            )
            config_task = progress.add_task(
                "Generating configuration files...", total=1
            )
            test_task = progress.add_task("Creating example tests...", total=1)
            doc_task = progress.add_task("Writing documentation...", total=1)

            try:
                # Create directory structure
                _create_directory_structure(project_path, verbose)
                progress.update(structure_task, completed=1)

                # Generate configuration files
                _create_configuration_files_from_templates(
                    project_path, context, verbose
                )
                progress.update(config_task, completed=1)

                # Create example tests and fixtures
                _create_example_tests_from_templates(project_path, context, verbose)
                progress.update(test_task, completed=1)

                # Create documentation and support files
                _create_documentation_from_templates(project_path, context, verbose)
                progress.update(doc_task, completed=1)

            except TemplateError as e:
                raise ProjectInitializationError(
                    f"Template processing failed: {e}",
                    project_path=str(project_path),
                    step="template_rendering",
                    suggestions=[
                        "Check that all required template variables are provided",
                        "Verify template files are not corrupted",
                        "Try with a different template type",
                    ],
                ) from e
            except Exception as e:
                raise ProjectInitializationError(
                    f"Project creation failed: {e}",
                    project_path=str(project_path),
                    step="project_creation",
                ) from e

        # Create .testapix metadata directory
        try:
            _create_metadata(project_path, context)
        except Exception as e:
            # Metadata creation failure is not critical
            if verbose:
                console.print(
                    f"[yellow]Warning: Failed to create metadata: {e}[/yellow]"
                )

        if verbose:
            console.print(
                f"[green][OK] Successfully created project '{project_name}'[/green]"
            )

        return True

    except (ValidationError, ProjectInitializationError, TemplateError):
        raise  # Re-raise our custom exceptions
    except Exception as e:
        raise ProjectInitializationError(
            f"Unexpected error during project initialization: {e}",
            project_path=str(project_path) if "project_path" in locals() else None,
            step="unknown",
            recoverable=False,
        ) from e


def _is_valid_project_name(name: str) -> bool:
    """Check if project name is valid.

    Valid names contain only letters, numbers, hyphens, and underscores.
    They should not start with a number or special character.
    """
    if not name:
        return False

    # Check first character
    if not (name[0].isalpha() or name[0] == "_"):
        return False

    # Check all characters
    for char in name:
        if not (char.isalnum() or char in "-_"):
            return False

    return True


def _validate_inputs(
    project_name: str,
    template: str,
    api_type: str,
    auth_type: str | None,
) -> None:
    """Validate all input parameters and raise detailed errors.

    Args:
    ----
        project_name: Name of the project
        template: Project template type
        api_type: API type
        auth_type: Authentication type

    Raises:
    ------
        ValidationError: If any parameter is invalid

    """
    # Validate project name
    if not _is_valid_project_name(project_name):
        suggestions = [
            "Use only letters, numbers, hyphens, and underscores",
            "Start with a letter or underscore (not a number)",
            "Examples: my-api-tests, user_service_tests, APITests",
        ]
        raise ValidationError(
            f"Invalid project name '{project_name}'",
            field="project_name",
            value=project_name,
            suggestions=suggestions,
        )

    # Validate template
    valid_templates = ["basic", "advanced", "microservices", "demo"]
    if template not in valid_templates:
        raise ValidationError(
            f"Invalid template '{template}'",
            field="template",
            value=template,
            valid_options=valid_templates,
        )

    # Validate API type
    valid_api_types = ["rest", "graphql", "grpc"]
    if api_type not in valid_api_types:
        raise ValidationError(
            f"Invalid API type '{api_type}'",
            field="api_type",
            value=api_type,
            valid_options=valid_api_types,
        )

    # Validate auth type
    if auth_type is not None:
        valid_auth_types = ["bearer", "api_key", "oauth2", "basic"]
        if auth_type not in valid_auth_types:
            raise ValidationError(
                f"Invalid authentication type '{auth_type}'",
                field="auth_type",
                value=auth_type,
                valid_options=valid_auth_types,
            )


def _prepare_template_context(
    project_name: str,
    template: str,
    api_type: str,
    auth_type: str | None,
    base_url: str | None,
) -> dict[str, Any]:
    """Prepare the context dictionary for template rendering.

    This context is used by Jinja2 templates to customize generated files
    based on user choices.
    """
    # Normalize project name for Python package naming
    python_package_name = project_name.lower().replace("-", "_").replace(" ", "_")

    # Default base URL if not provided
    if not base_url:
        if template == "demo":
            base_url = "https://api.practicesoftwaretesting.com"
        elif template != "basic":
            base_url = "https://api.example.com"
        else:
            base_url = "http://localhost:8000"

    context = {
        # Project information
        "project_name": project_name,
        "python_package_name": python_package_name,
        "template": template,
        "api_type": api_type,
        # API configuration
        "base_url": base_url,
        "auth_type": auth_type,
        # Metadata
        "created_date": datetime.now().strftime("%Y-%m-%d"),
        "testapix_version": "0.1.0",
        # Feature flags based on template
        "include_security_tests": template in ["advanced", "microservices"],
        "include_performance_tests": template in ["advanced", "microservices"],
        "include_contract_tests": template == "microservices",
        "include_docker": template == "microservices",
        "database_enabled": template in ["advanced", "microservices"],
        "is_demo_template": template == "demo",
        # Helper functions for templates
        "capitalize": str.capitalize,
        "title": str.title,
    }

    return context


def _create_directory_structure(project_path: Path, verbose: bool) -> None:
    """Create the standard TestAPIX project directory structure.

    The structure is designed to:
    - Separate different types of tests
    - Organize configuration by environment
    - Provide clear locations for data and utilities
    """
    directories = [
        # Configuration directory
        "configs",
        # Test directories
        "tests/functional",
        "tests/contract",
        "tests/security",
        "tests/performance",
        "tests/fixtures",
        # Data and utilities
        "schemas",
        "data_generators",
        "reports",
        # Hidden TestAPIX metadata
        ".testapix",
    ]

    for directory in directories:
        dir_path = project_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)

        # Create __init__.py for Python packages
        if directory.startswith("tests") or directory in ["schemas", "data_generators"]:
            init_file = dir_path / "__init__.py"
            init_file.touch()

            # Add docstring to test __init__.py files
            if directory.startswith("tests"):
                init_file.write_text(
                    f'"""\n{directory.replace("/", " ").title()}\n"""\n'
                )

        if verbose:
            console.print(f"   📁 Created {directory}/")


def _create_configuration_files_from_templates(
    project_path: Path, context: dict[str, Any], verbose: bool
) -> None:
    """Create configuration files using templates.

    Creates configuration files for different environments using the
    template system for consistency and maintainability.
    """
    configs_dir = project_path / "configs"

    try:
        # Base configuration
        template_manager.render_to_file(
            "configs/base.yaml.j2", Path(configs_dir / "base.yaml"), context
        )

        # Local development configuration
        template_manager.render_to_file(
            "configs/local.yaml.j2", Path(configs_dir / "local.yaml"), context
        )

        # Test environment configuration
        template_manager.render_to_file(
            "configs/test.yaml.j2", Path(configs_dir / "test.yaml"), context
        )

        # Create staging config for advanced templates
        if context["template"] in ["advanced", "microservices"]:
            # For now, use test config as base for staging
            # Could create a separate staging.yaml.j2 template later
            staging_context = {**context, "environment": "staging"}
            template_manager.render_to_file(
                "configs/test.yaml.j2",
                Path(configs_dir / "staging.yaml"),
                staging_context,
            )

        # Create .env.example file
        template_manager.render_to_file(
            "configs/env.example.j2", Path(project_path / ".env.example"), context
        )

        # Create pytest.ini
        template_manager.render_to_file(
            "configs/pytest.ini.j2", Path(project_path / "pytest.ini"), context
        )

        if verbose:
            console.print("   [INFO] Created configuration files")

    except TemplateError as e:
        raise ProjectInitializationError(
            f"Failed to create configuration files: {e}",
            project_path=str(project_path),
            step="configuration_files",
        ) from e


def _create_example_tests_from_templates(
    project_path: Path, context: dict[str, Any], verbose: bool
) -> None:
    """Create example test files using templates.

    Creates test files using the template system for consistency and
    maintainability, replacing the old string concatenation approach.
    """
    try:
        # Create fixtures file
        template_manager.render_to_file(
            "fixtures/fixtures.py.j2",
            Path(project_path / "tests" / "fixtures" / "__init__.py"),
            context,
        )

        # Create example functional test
        test_name = context["python_package_name"]
        functional_test_context = {
            **context,
            "python_name": test_name,
            "api_name": context["project_name"],
            "has_auth": context["auth_type"] is not None,
        }

        # Use demo-specific template if demo template is selected
        if context["is_demo_template"]:
            template_manager.render_to_file(
                "demo/test_practice_software_testing_api.py.j2",
                Path(
                    project_path
                    / "tests"
                    / "functional"
                    / "test_practice_software_testing_api.py"
                ),
                functional_test_context,
            )
        else:
            template_manager.render_to_file(
                "functional/test_template.py.j2",
                Path(project_path / "tests" / "functional" / f"test_{test_name}.py"),
                functional_test_context,
            )

        # Create conftest.py for pytest configuration
        template_manager.render_to_file(
            "fixtures/conftest.py.j2",
            Path(project_path / "tests" / "conftest.py"),
            context,
        )

        # Create data generator
        if context["is_demo_template"]:
            template_manager.render_to_file(
                "demo/data_generator.py.j2",
                Path(project_path / "data_generators" / f"{test_name}_generator.py"),
                context,
            )
        else:
            template_manager.render_to_file(
                "generators/data_generator.py.j2",
                Path(project_path / "data_generators" / f"{test_name}_generator.py"),
                context,
            )

        if verbose:
            console.print("   [INFO] Created example tests and generators")

    except TemplateError as e:
        raise ProjectInitializationError(
            f"Failed to create test files: {e}",
            project_path=str(project_path),
            step="test_creation",
        ) from e


def _create_documentation_from_templates(
    project_path: Path, context: dict[str, Any], verbose: bool
) -> None:
    """Create documentation files using templates.

    Creates documentation and support files using the template system.
    """
    try:
        # Create README.md
        if context["is_demo_template"]:
            template_manager.render_to_file(
                "demo/README.md.j2", Path(project_path / "README.md"), context
            )
        else:
            template_manager.render_to_file(
                "docs/README.md.j2", Path(project_path / "README.md"), context
            )

        # Create requirements.txt
        template_manager.render_to_file(
            "docs/requirements.txt.j2", Path(project_path / "requirements.txt"), context
        )

        # Create .gitignore
        gitignore_content = """# Environment files
.env
.env.*
!.env.example

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Testing
.coverage
.pytest_cache/
htmlcov/
reports/
*.log

# IDE
.idea/
.vscode/
*.swp
*.swo
.DS_Store

# TestAPIX
.testapix/
"""
        (project_path / ".gitignore").write_text(gitignore_content)

        if verbose:
            console.print("   📚 Created documentation and support files")

    except TemplateError as e:
        raise ProjectInitializationError(
            f"Failed to create documentation files: {e}",
            project_path=str(project_path),
            step="documentation_creation",
        ) from e


def _create_metadata(project_path: Path, context: dict[str, Any]) -> None:
    """Create TestAPIX metadata directory for framework use.

    This hidden directory stores framework-specific information that
    shouldn't be edited by users but helps TestAPIX provide better features.
    """
    metadata_dir = project_path / ".testapix"
    metadata_dir.mkdir(exist_ok=True)

    # Store project metadata
    metadata = {
        "version": "1.0",
        "created_with": context["testapix_version"],
        "created_date": context["created_date"],
        "template": context["template"],
        "api_type": context["api_type"],
        "auth_type": context["auth_type"],
    }

    import json

    (metadata_dir / "project.json").write_text(json.dumps(metadata, indent=2))

    # Create .gitkeep to ensure directory is tracked
    (metadata_dir / ".gitkeep").touch()
