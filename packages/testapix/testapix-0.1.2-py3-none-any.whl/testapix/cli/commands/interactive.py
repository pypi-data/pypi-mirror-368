"""Interactive CLI Command

Command to start the TestAPIX interactive shell for API exploration.
"""

import asyncio
import sys
from pathlib import Path

import click

from testapix.core.client import HTTPClient
from testapix.interactive import InteractiveShell


@click.command()
@click.option("--api", help="API base URL to connect to", metavar="URL")
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to TestAPIX configuration file",
)
@click.option(
    "--auth",
    help='Authentication in format "type:credentials" (e.g., "bearer:token123")',
    metavar="TYPE:CREDS",
)
@click.option("--env", help="Environment to load from configuration", metavar="ENV")
def interactive(api: str, config: Path, auth: str, env: str) -> None:
    """Start interactive TestAPIX shell for API exploration and testing.

    The interactive shell provides a REPL environment for exploring APIs,
    making requests, and building test scenarios interactively.

    Examples:
        # Start with specific API
        testapix interactive --api https://api.example.com

        # Start with configuration file
        testapix interactive --config ./configs/staging.yaml

        # Start with authentication
        testapix interactive --api https://api.example.com --auth bearer:your-token

        # Start with specific environment
        testapix interactive --config ./configs/base.yaml --env staging

    """
    # Check if prompt_toolkit is available
    try:
        import prompt_toolkit  # noqa: F401
    except ImportError:
        click.echo("❌ Interactive shell requires prompt_toolkit", err=True)
        click.echo("💡 Install with: pip install prompt_toolkit", err=True)
        sys.exit(1)

    try:
        # Create shell instance
        shell = InteractiveShell(
            base_url=api, config_path=str(config) if config else None
        )

        # Configure authentication if provided
        if auth and ":" in auth:
            auth_type, credentials = auth.split(":", 1)
            if shell.client:
                _configure_authentication(shell.client, auth_type, credentials)
            else:
                click.echo(
                    "⚠️  Cannot configure authentication without API URL", err=True
                )
                click.echo("💡 Use --api option to specify base URL", err=True)

        # Set environment if provided
        if env:
            # Environment handling would be implemented with config system
            click.echo(f"🌍 Environment: {env}")

        # Run the interactive shell
        asyncio.run(shell.run())

    except KeyboardInterrupt:
        click.echo("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        click.echo(f"❌ Failed to start interactive shell: {e}", err=True)
        sys.exit(1)


def _configure_authentication(
    client: HTTPClient, auth_type: str, credentials: str
) -> None:
    """Configure authentication for the API client"""
    auth_type = auth_type.lower()

    try:
        if auth_type == "bearer":
            from testapix.auth import BearerTokenAuth

            client.set_auth(BearerTokenAuth(credentials))
            click.echo("🔐 Configured Bearer authentication")

        elif auth_type == "apikey" or auth_type == "api-key":
            from testapix.auth import APIKeyAuth

            client.set_auth(APIKeyAuth(credentials))
            click.echo("🔐 Configured API Key authentication")

        elif auth_type == "basic":
            if ":" in credentials:
                username, password = credentials.split(":", 1)
                # Basic auth would need to be implemented
                click.echo(
                    "❌ Basic auth not yet implemented in current auth system", err=True
                )
            else:
                click.echo(
                    "❌ Basic auth requires format 'username:password'", err=True
                )

        else:
            click.echo(f"❌ Unsupported authentication type: {auth_type}", err=True)
            click.echo("💡 Supported types: bearer, apikey", err=True)

    except ImportError as e:
        click.echo(f"❌ Authentication module not available: {e}", err=True)
    except Exception as e:
        click.echo(f"❌ Failed to configure authentication: {e}", err=True)
