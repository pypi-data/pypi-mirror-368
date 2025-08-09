"""TestAPIX CLI Main Entry Point

This module provides the command-line interface for TestAPIX. The CLI is designed
to be intuitive and helpful, guiding users through the process of setting up
and running API tests.

Design principles:
1. Progressive Disclosure: Simple commands are simple, advanced features are available
2. Helpful Feedback: Clear messages guide users to success
3. Beautiful Output: Uses Rich for colorful, formatted output
4. Error Recovery: Helpful error messages suggest solutions

The CLI serves both as a tool and a teacher, helping users learn TestAPIX
patterns through examples and suggestions.
"""

import logging
import sys
import traceback
from pathlib import Path
from typing import Any

import click
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from testapix import __version__
from testapix.core.config import load_config
from testapix.core.exceptions import ConfigurationError, TestAPIXError

# Lazy imports for commands to improve startup time
# Commands are imported only when needed


# Create Rich console for beautiful output with cross-platform compatibility
console = Console(force_terminal=True, width=120)

# Configure logging format
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.WARNING,  # Default level, overridden by config
)


def print_banner() -> None:
    """Print the TestAPIX welcome banner with ASCII art."""
    # ASCII art for TestAPIX using only standard ASCII characters (no Unicode)
    # Carefully aligned: T-e-s-t-A-P-I-X
    ascii_art = Text()
    ascii_art.append(
        "######   ##  ##   #####  ######  ####  ##     ##\n", style="bold blue"
    )
    ascii_art.append(
        "##   ##  ##  ##  ##   ## ##   ##  ##    ##   ##\n", style="bold blue"
    )
    ascii_art.append(
        "######    ####   ####### ######   ##     #####\n", style="bold blue"
    )
    ascii_art.append(
        "##         ##    ##   ## ##       ##    ##   ##\n", style="bold blue"
    )
    ascii_art.append(
        "##         ##    ##   ## ##      ####  ##     ##\n", style="bold blue"
    )

    # Tagline
    tagline = Text()
    tagline.append("Comprehensive Python API Testing Framework", style="dim cyan")

    # Version info
    version_text = Text()
    version_text.append(f"Version {__version__}", style="dim white")

    # Combine everything
    banner_content = Text()
    banner_content.append(ascii_art)
    banner_content.append("\n")
    banner_content.append(tagline)

    panel = Panel(
        banner_content,
        subtitle=version_text,
        subtitle_align="right",
        border_style="blue",
        box=box.ROUNDED,
        padding=(1, 2),
    )

    console.print(panel)


def print_error(
    message: str, error: Exception | None = None, show_traceback: bool = False
) -> None:
    """Print an error message in a user-friendly format.

    Args:
    ----
        message: Main error message
        error: The exception object (if available)
        show_traceback: Whether to show full traceback

    """
    error_text = Text()
    error_text.append("[ERROR] ", style="bold red")
    error_text.append(message, style="red")

    console.print(error_text)

    if error and hasattr(error, "__dict__"):
        # Show additional context from custom exceptions
        context_items = []
        for attr, value in error.__dict__.items():
            if not attr.startswith("_") and value is not None:
                context_items.append(f"{attr}: {value}")

        if context_items:
            console.print("   Context:", style="dim red")
            for item in context_items:
                console.print(f"   - {item}", style="dim red")

    if show_traceback and error:
        console.print("\n[dim]Full traceback:[/dim]")
        console.print(
            Syntax(traceback.format_exc(), "python", theme="monokai", line_numbers=True)
        )


def print_success(message: str) -> None:
    """Print a success message."""
    success_text = Text()
    success_text.append("[OK] ", style="bold green")
    success_text.append(message, style="green")
    console.print(success_text)


def print_info(message: str) -> None:
    """Print an informational message."""
    info_text = Text()
    info_text.append("[INFO] ", style="bold blue")
    info_text.append(message, style="blue")
    console.print(info_text)


def print_warning(message: str) -> None:
    """Print a warning message."""
    warning_text = Text()
    warning_text.append("[WARN] ", style="bold yellow")
    warning_text.append(message, style="yellow")
    console.print(warning_text)


class TestAPIXContext:
    """Context object passed between CLI commands.

    This stores global state like configuration directory,
    environment, and verbosity settings.
    """

    def __init__(self) -> None:
        self.config_dir: Path | None = None
        self.environment: str | None = None
        self.verbose: bool = False
        self.debug: bool = False
        self.config: Any | None = None  # Loaded configuration


@click.group(invoke_without_command=True)
@click.option("--version", "-v", is_flag=True, help="Show version information")
@click.option(
    "--config-dir",
    "-c",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=Path),
    help="Configuration directory path (default: ./configs)",
)
@click.option(
    "--environment", "-e", help="Environment to use (local, dev, test, staging, prod)"
)
@click.option("--verbose", is_flag=True, help="Enable verbose output")
@click.option("--debug", is_flag=True, help="Enable debug output (very verbose)")
@click.pass_context
def cli(
    ctx: click.Context,
    version: bool,
    config_dir: Path | None,
    environment: str | None,
    verbose: bool,
    debug: bool,
) -> None:
    """TestAPIX - A comprehensive Python API testing framework.

    TestAPIX provides everything you need to build robust, maintainable API tests.
    From simple functional tests to complex security and performance testing,
    TestAPIX guides you through best practices while remaining flexible for
    advanced use cases.

    Get started with a new project:

        \b
        testapix init my-api-tests
        cd my-api-tests
        testapix generate functional user-api
        pytest tests/

    For more information, visit: https://testapix.readthedocs.io
    """
    # Create context object
    ctx.ensure_object(TestAPIXContext)
    ctx.obj.config_dir = config_dir
    ctx.obj.environment = environment
    ctx.obj.verbose = verbose
    ctx.obj.debug = debug

    # Configure logging based on verbosity
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        console.print("[DEBUG] Debug mode enabled", style="dim yellow")
    elif verbose:
        logging.getLogger().setLevel(logging.INFO)
        console.print("[VERBOSE] Verbose mode enabled", style="dim blue")

    # Show version if requested
    if version:
        console.print(f"TestAPIX version {__version__}", style="bold green")
        return

    # Show help if no command provided
    if ctx.invoked_subcommand is None:
        print_banner()
        console.print("\n[TIP] Use --help to see available commands\n", style="dim")
        console.print(ctx.get_help())


@cli.command()
@click.argument("project_name")
@click.option(
    "--template",
    "-t",
    default="basic",
    type=click.Choice(
        ["basic", "advanced", "microservices", "demo"], case_sensitive=False
    ),
    help="Project template to use",
)
@click.option(
    "--api-type",
    default="rest",
    type=click.Choice(["rest", "graphql", "grpc"], case_sensitive=False),
    help="Type of API to test",
)
@click.option(
    "--auth-type",
    type=click.Choice(["bearer", "api_key", "oauth2", "basic"], case_sensitive=False),
    help="Authentication type (optional)",
)
@click.option("--base-url", help="Base URL for the API (e.g., https://api.example.com)")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing directory")
@click.pass_context
def init(
    ctx: click.Context,
    project_name: str,
    template: str,
    api_type: str,
    auth_type: str | None,
    base_url: str | None,
    force: bool,
) -> None:
    """Initialize a new TestAPIX testing project.

    This command creates a new directory with all the necessary files and
    structure for API testing. The generated project includes:

    \b
    - Configuration files for different environments
    - Example tests demonstrating best practices
    - Test data generators
    - Documentation to get started quickly

    PROJECT_NAME: Name of the project directory to create

    Examples
    --------
        \b
        # Basic REST API project
        testapix init my-api-tests

        # API with bearer token authentication
        testapix init my-api --auth-type bearer --base-url https://api.example.com

        # Advanced microservices project
        testapix init my-services --template microservices --auth-type oauth2

        # Demo project with Practice Software Testing API
        testapix init demo-project --template demo

    """
    try:
        print_info(f"Initializing TestAPIX project: {project_name}")

        # Import command implementation
        from testapix.cli.commands.init import init_project

        # Show configuration being used
        if ctx.obj.verbose:
            config_table = Table(title="Project Configuration", box=box.SIMPLE)
            config_table.add_column("Setting", style="cyan")
            config_table.add_column("Value", style="white")

            config_table.add_row("Template", template)
            config_table.add_row("API Type", api_type)
            config_table.add_row("Auth Type", auth_type or "None")
            config_table.add_row("Base URL", base_url or "http://localhost:8000")

            console.print(config_table)

        # Execute initialization
        success = init_project(
            project_name=project_name,
            template=template,
            api_type=api_type,
            auth_type=auth_type,
            base_url=base_url,
            force=force,
            verbose=ctx.obj.verbose,
        )

        if success:
            print_success(f"Project '{project_name}' created successfully!")

            # Show next steps
            console.print("\n>>> [bold]Next steps:[/bold]")
            console.print(f"   1. cd {project_name}")
            console.print("   2. pip install -r requirements.txt")
            console.print("   3. cp .env.example .env  # Add your credentials")
            console.print("   4. testapix generate functional your-api")
            console.print("   5. pytest tests/ -v")

            if auth_type:
                print_warning(
                    f"\nRemember to set your {auth_type} credentials in the .env file!"
                )

    except TestAPIXError as e:
        print_error(str(e), e, show_traceback=ctx.obj.debug)
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}", e, show_traceback=ctx.obj.debug)
        sys.exit(1)


@cli.command()
@click.argument(
    "test_type",
    type=click.Choice(
        ["functional", "contract", "security", "performance"], case_sensitive=False
    ),
)
@click.argument("api_name")
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    help="Output directory for generated tests (default: tests/{test_type})",
)
@click.option(
    "--endpoints",
    help="Comma-separated list of endpoints to test (e.g., /users,/posts)",
)
@click.option(
    "--schema-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="OpenAPI/JSON schema file for contract testing",
)
@click.option(
    "--include-examples/--no-examples",
    default=True,
    help="Include example tests and documentation",
)
@click.pass_context
def generate(
    ctx: click.Context,
    test_type: str,
    api_name: str,
    output_dir: Path | None,
    endpoints: str | None,
    schema_file: Path | None,
    include_examples: bool,
) -> None:
    """Generate test files for an API.

    This command creates comprehensive test files based on the specified test type.
    The generated tests include:

    \b
    - Realistic test scenarios
    - Proper error handling
    - Test data generation
    - Clear documentation

    TEST_TYPE: Type of tests to generate
    API_NAME: Name of the API being tested

    Examples
    --------
        \b
        # Generate functional tests for user API
        testapix generate functional user-api

        # Generate security tests for specific endpoints
        testapix generate security payment-api --endpoints "/charge,/refund"

        # Generate contract tests from OpenAPI spec
        testapix generate contract api --schema-file openapi.yaml

    """
    try:
        print_info(f"Generating {test_type} tests for {api_name}")

        # Import command implementation
        from testapix.cli.commands.generate import generate_tests

        # Try to load configuration to understand project structure
        try:
            config = load_config(
                environment=ctx.obj.environment, config_dir=ctx.obj.config_dir
            )
            ctx.obj.config = config
        except ConfigurationError:
            # Not in a TestAPIX project or no config found
            if ctx.obj.verbose:
                print_warning(
                    "No TestAPIX configuration found. "
                    "Generating tests with default settings."
                )
            config = None

        # Parse endpoints if provided
        endpoint_list = None
        if endpoints:
            endpoint_list = [e.strip() for e in endpoints.split(",")]
            if ctx.obj.verbose:
                console.print(f"Targeting endpoints: {', '.join(endpoint_list)}")

        # Execute generation
        success = generate_tests(
            test_type=test_type,
            api_name=api_name,
            output_dir=output_dir,
            endpoints=endpoint_list,
            schema_file=schema_file,
            include_examples=include_examples,
            config=config,
            verbose=ctx.obj.verbose,
        )

        if success:
            print_success(f"{test_type.title()} tests generated successfully!")

            # Show helpful next steps
            console.print("\n[TEST] [bold]Run your tests:[/bold]")
            console.print("   pytest tests/ -v")

            if test_type == "functional":
                console.print("\n[TIP] [bold]Tips:[/bold]")
                console.print(
                    "   - Review the generated tests and customize for your API"
                )
                console.print("   - Update test data generators for realistic values")
                console.print("   - Add edge cases specific to your business logic")
            elif test_type == "security":
                print_warning(
                    "\n[WARN] Security tests generate potentially dangerous payloads. "
                    "Only run against APIs you own!"
                )

    except TestAPIXError as e:
        print_error(str(e), e, show_traceback=ctx.obj.debug)
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}", e, show_traceback=ctx.obj.debug)
        sys.exit(1)


@cli.command()
@click.option(
    "--config-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Specific configuration file to validate",
)
@click.pass_context
def validate_config(ctx: click.Context, config_file: Path | None) -> None:
    """Validate TestAPIX configuration files.

    This command checks your configuration for:

    \b
    - Syntax errors in YAML files
    - Missing required fields
    - Invalid configuration values
    - Environment variable references

    Examples
    --------
        \b
        # Validate all configuration files
        testapix validate-config

        # Validate specific file
        testapix validate-config --config-file configs/staging.yaml

    """
    try:
        print_info("Validating configuration...")

        if config_file:
            # Validate specific file
            import yaml

            console.print(f"Checking {config_file}")

            try:
                with open(config_file) as f:
                    data = yaml.safe_load(f)

                print_success(f"{config_file} is valid YAML")

                if ctx.obj.verbose and isinstance(data, dict):
                    # Show configuration structure
                    from rich.tree import Tree

                    tree = Tree("Configuration Structure")
                    _build_config_tree(tree, data)
                    console.print(tree)

            except yaml.YAMLError as e:
                print_error(f"Invalid YAML: {e}")
                sys.exit(1)

        else:
            # Validate complete configuration
            try:
                config = load_config(
                    environment=ctx.obj.environment, config_dir=ctx.obj.config_dir
                )

                print_success("Configuration is valid!")

                # Show configuration summary
                summary_table = Table(title="Configuration Summary", box=box.SIMPLE)
                summary_table.add_column("Setting", style="cyan")
                summary_table.add_column("Value", style="white")

                summary_table.add_row("Environment", config.environment)
                summary_table.add_row("Base URL", config.http.base_url)
                summary_table.add_row(
                    "Auth Type", config.auth.type if config.auth else "None"
                )
                summary_table.add_row("Log Level", config.log_level.value)
                summary_table.add_row("Parallel Workers", str(config.parallel_workers))

                console.print(summary_table)

                # Check for potential issues
                warnings = []

                if not config.http.verify_ssl:
                    warnings.append("SSL verification is disabled")

                if (
                    config.auth
                    and config.auth.type == "bearer"
                    and not config.auth.token
                ):
                    warnings.append(
                        "Bearer auth configured but no token set. "
                        "Set TESTAPIX_AUTH__TOKEN environment variable."
                    )

                if config.database.enabled and not config.database.url:
                    warnings.append(
                        "Database enabled but no URL set. "
                        "Set TESTAPIX_DATABASE__URL environment variable."
                    )

                if warnings:
                    console.print("\n[WARN] [bold yellow]Warnings:[/bold yellow]")
                    for warning in warnings:
                        console.print(f"   - {warning}", style="yellow")

            except ConfigurationError as e:
                print_error(f"Configuration error: {e}", e)
                sys.exit(1)

    except Exception as e:
        print_error(f"Unexpected error: {e}", e, show_traceback=ctx.obj.debug)
        sys.exit(1)


# Import and register interactive command
try:
    from testapix.cli.commands.interactive import interactive

    cli.add_command(interactive)
except ImportError:
    # prompt_toolkit not available - interactive command won't be available
    pass


@cli.command()
@click.option(
    "--list-commands",
    is_flag=True,
    help="List all available commands with descriptions",
)
def help(list_commands: bool) -> None:
    """Show detailed help and usage examples.

    This command provides comprehensive help including:

    \b
    - Available commands and options
    - Common usage patterns
    - Configuration examples
    - Troubleshooting tips
    """
    print_banner()

    if list_commands:
        # Show all commands with descriptions
        commands_table = Table(title="Available Commands", box=box.ROUNDED)
        commands_table.add_column("Command", style="cyan", no_wrap=True)
        commands_table.add_column("Description", style="white")

        commands = [
            ("init", "Initialize a new TestAPIX project"),
            ("generate", "Generate test files for an API"),
            ("interactive", "Start interactive shell for API exploration"),
            ("validate-config", "Validate configuration files"),
            ("help", "Show help and usage examples"),
        ]

        for cmd, desc in commands:
            commands_table.add_row(cmd, desc)

        console.print(commands_table)

    else:
        # Show general help
        console.print("\n[bold]Quick Start:[/bold]")
        console.print(
            """
    1. Initialize a new project:
       [cyan]testapix init my-api-tests[/cyan]

    2. Generate functional tests:
       [cyan]testapix generate functional user-api[/cyan]

    3. Run your tests:
       [cyan]pytest tests/ -v[/cyan]
"""
        )

        console.print("\n[bold]Common Usage Patterns:[/bold]")
        console.print(
            """
    # REST API with Bearer token auth
    [cyan]testapix init my-api --auth-type bearer --base-url https://api.example.com[/cyan]

    # Generate tests for specific endpoints
    [cyan]testapix generate functional users --endpoints "/users,/users/{id}"[/cyan]

    # Run tests against staging environment
    [cyan]TESTAPIX_ENVIRONMENT=staging pytest tests/[/cyan]
"""
        )

        console.print("\n[bold]For more help:[/bold]")
        console.print(
            "   - Use [cyan]testapix COMMAND --help[/cyan] for command-specific help"
        )
        console.print(
            "   - Visit [cyan]https://testapix.readthedocs.io[/cyan] for full documentation"
        )
        console.print(
            "   - Report issues at [cyan]https://github.com/testapix/testapix/issues[/cyan]"
        )


def _build_config_tree(tree: Any, data: Any, prefix: str = "") -> None:
    """Helper to build configuration tree for display."""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                branch = tree.add(f"{prefix}{key}")
                _build_config_tree(branch, value)
            elif isinstance(value, list):
                tree.add(f"{prefix}{key}: [{len(value)} items]")
            else:
                tree.add(f"{prefix}{key}: {value}")
    else:
        tree.add(str(data))


# Entry point for console script
def main() -> None:
    """Main entry point for the CLI."""
    try:
        cli(obj=TestAPIXContext())
    except KeyboardInterrupt:
        console.print("\n[EXIT] Operation cancelled by user", style="yellow")
        sys.exit(130)  # Standard exit code for Ctrl+C
    except Exception as e:
        # Catch any unhandled exceptions
        print_error(f"Unhandled error: {e}", e, show_traceback=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
