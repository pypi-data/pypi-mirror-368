"""Interactive Shell for TestAPIX

Main interactive shell implementation using prompt_toolkit for rich CLI experience.
"""

import asyncio
import sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.history import FileHistory

    from testapix.core.client import EnhancedResponse, HTTPClient
else:
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.completion import WordCompleter
        from prompt_toolkit.formatted_text import HTML
        from prompt_toolkit.history import FileHistory
    except ImportError:
        PromptSession = None
        WordCompleter = None
        FileHistory = None
        HTML = None

from testapix.auth.legacy import APIKeyAuth, AuthProvider, BasicAuth, BearerTokenAuth
from testapix.core.client import HTTPClient
from testapix.core.config import load_config

from .commands import CommandRegistry
from .session import SessionManager


class InteractiveShell:
    """Main interactive shell for TestAPIX API exploration"""

    client: "HTTPClient | None"
    last_response: "EnhancedResponse | None"

    def __init__(
        self,
        base_url: str | None = None,
        config_path: str | None = None,
        allow_non_tty: bool = False,
    ):
        # Check if prompt_toolkit is available
        if PromptSession is None:
            raise ImportError(
                "prompt_toolkit is required for interactive shell. "
                "Install with: pip install prompt_toolkit"
            )

        # Check if we're in an interactive terminal (unless bypassed for testing)
        if not allow_non_tty and not sys.stdin.isatty():
            raise RuntimeError(
                "Interactive shell requires a terminal (TTY). "
                "Cannot run in non-interactive environments."
            )

        self.client = None
        self.last_response = None
        self.session_manager = SessionManager()
        self.command_registry = CommandRegistry(self)
        self._config: Any = None

        # Setup prompt toolkit
        self.session: Any = PromptSession(
            history=FileHistory(".testapix_history"),
            completer=self._create_completer(),
            complete_while_typing=True,
        )

        # Initialize HTTP client if base_url provided
        if base_url:
            self.client = HTTPClient(base_url=base_url)
            self.session_manager.current_session["base_url"] = base_url

        # Load configuration if provided
        self._config_path = config_path

    def _create_completer(self) -> Any:
        """Create tab completer with available commands"""
        commands = self.command_registry.get_command_names()
        return WordCompleter(commands, ignore_case=True)

    async def _load_config(self, config_path: str) -> None:
        """Load configuration from file"""
        try:
            config = load_config(config_path)
            self._config = config

            # Extract base URL
            base_url = config.http.base_url if config.http.base_url else None

            # Create auth provider from config
            auth_provider = None
            if hasattr(config, "auth") and config.auth:
                auth_provider = self._create_auth_from_config(config.auth)

            # Create or recreate client with auth
            if base_url:
                self.client = HTTPClient(base_url=base_url, auth_provider=auth_provider)
                self.session_manager.current_session["base_url"] = base_url

                # Store auth config in session if present
                if auth_provider:
                    auth_config = self._auth_provider_to_config(auth_provider)
                    self.session_manager.current_session["auth_config"] = auth_config
                    self.session_manager.current_session["auth_type"] = (
                        auth_config.get("type") if auth_config else None
                    )

        except Exception as e:
            print(f"⚠️  Warning: Could not load config: {e}")

    async def run(self) -> None:
        """Main shell loop"""
        # Load config if provided
        if self._config_path:
            await self._load_config(self._config_path)

        self._print_banner()

        while True:
            try:
                # Get user input with tab completion
                text = await self.session.prompt_async(
                    HTML("<ansicyan>testapix> </ansicyan>")
                )

                if text.strip().lower() in ("exit", "quit", "q"):
                    break

                # Parse and execute command
                await self._execute_command(text)

            except KeyboardInterrupt:
                print("\n💡 Use 'exit' or Ctrl+D to quit")
                continue
            except EOFError:
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                continue

        print("👋 Goodbye!")

    async def _execute_command(self, text: str) -> None:
        """Parse and execute a command"""
        text = text.strip()
        if not text:
            return

        parts = text.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        try:
            await self.command_registry.execute(command, args)
        except Exception as e:
            print(f"❌ Error executing command: {e}")
            print("💡 Type 'help' for available commands")

    def _print_banner(self) -> None:
        """Print startup banner"""
        print("🚀 TestAPIX Interactive Shell v2.0.0")
        if self.client:
            print(f"🌐 Connected to: {self.client.base_url}")

            # Show auth status
            auth_config = self.session_manager.current_session.get("auth_config")
            if auth_config:
                auth_type = auth_config.get("type", "unknown")
                print(f"🔐 Authentication: {auth_type.title()}")
            else:
                print("🔓 Authentication: None")
        else:
            print("⚠️  No API configured. Use commands to set up connection.")
        print("📖 Type 'help' for commands, 'exit' to quit")
        print()

    def _create_auth_from_config(self, auth_config: Any) -> AuthProvider | None:
        """Create auth provider from configuration"""
        try:
            if hasattr(auth_config, "bearer_token") and auth_config.bearer_token:
                return BearerTokenAuth(auth_config.bearer_token)
            elif hasattr(auth_config, "api_key") and auth_config.api_key:
                header_name = getattr(auth_config, "api_key_header", "X-API-Key")
                return APIKeyAuth(auth_config.api_key, header_name)
            elif hasattr(auth_config, "basic_auth") and auth_config.basic_auth:
                basic = auth_config.basic_auth
                if hasattr(basic, "username") and hasattr(basic, "password"):
                    return BasicAuth(basic.username, basic.password)
        except Exception as e:
            print(f"⚠️  Warning: Could not create auth from config: {e}")
        return None

    def _auth_provider_to_config(
        self, auth_provider: AuthProvider
    ) -> dict[str, Any] | None:
        """Convert auth provider to config dict for session storage"""
        if isinstance(auth_provider, BearerTokenAuth):
            return {"type": "bearer", "token": auth_provider.token}
        elif isinstance(auth_provider, APIKeyAuth):
            return {
                "type": "apikey",
                "api_key": auth_provider.api_key,
                "header_name": auth_provider.header_name,
            }
        elif isinstance(auth_provider, BasicAuth):
            return {
                "type": "basic",
                "username": auth_provider.username,
                "password": auth_provider.password,
            }
        return None

    def _config_to_auth_provider(
        self, auth_config: dict[str, Any]
    ) -> AuthProvider | None:
        """Create auth provider from config dict"""
        if not auth_config or "type" not in auth_config:
            return None

        # Check if this is sanitized data from a saved session
        if auth_config.get("_sanitized"):
            print("⚠️  Warning: Cannot load sanitized authentication from saved session")
            print(
                "💡 Please reconfigure authentication with: auth <type> <credentials>"
            )
            return None

        auth_type = auth_config["type"]
        try:
            if auth_type == "bearer":
                return BearerTokenAuth(auth_config["token"])
            elif auth_type == "apikey":
                return APIKeyAuth(
                    auth_config["api_key"], auth_config.get("header_name", "X-API-Key")
                )
            elif auth_type == "basic":
                return BasicAuth(auth_config["username"], auth_config["password"])
        except Exception as e:
            print(f"⚠️  Warning: Could not create auth provider: {e}")
        return None

    async def _recreate_client_with_auth(
        self, auth_config: dict[str, Any] | None
    ) -> None:
        """Recreate HTTPClient with authentication"""
        if not self.client:
            print("⚠️  No HTTP client to update")
            return

        base_url = self.client.base_url
        auth_provider = None

        if auth_config:
            auth_provider = self._config_to_auth_provider(auth_config)

        # Close existing client
        if hasattr(self.client, "close"):
            await self.client.close()

        # Create new client with auth
        self.client = HTTPClient(base_url=base_url, auth_provider=auth_provider)

        print("🔄 HTTP client updated with authentication")


def main() -> None:
    """Entry point for interactive shell"""
    try:
        shell = InteractiveShell()
        asyncio.run(shell.run())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Failed to start interactive shell: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
