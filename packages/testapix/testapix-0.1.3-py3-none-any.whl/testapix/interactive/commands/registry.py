"""Command Registry for Interactive Shell

Central registry for all interactive shell commands.
"""

import os
from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from testapix.interactive.shell import InteractiveShell

from .auth import AuthCommands
from .generate import GenerateCommands
from .http import HTTPCommands
from .response import ResponseCommands
from .session import SessionCommands


class CommandRegistry:
    """Registry for interactive shell commands"""

    def __init__(self, shell: "InteractiveShell"):
        self.shell = shell
        self.commands: dict[str, Callable] = {}
        self._register_commands()

    def _register_commands(self) -> None:
        """Register all command handlers"""
        # HTTP commands
        http_commands = HTTPCommands(self.shell)
        self.commands.update(
            {
                "get": http_commands.get,
                "post": http_commands.post,
                "put": http_commands.put,
                "patch": http_commands.patch,
                "delete": http_commands.delete,
                "show": http_commands.show,
            }
        )

        # Authentication commands
        auth_commands = AuthCommands(self.shell)
        self.commands.update({"auth": auth_commands.auth})

        # Session commands
        session_commands = SessionCommands(self.shell)
        self.commands.update(
            {
                "save": session_commands.save,
                "load": session_commands.load,
                "sessions": session_commands.sessions,
                "remove": session_commands.delete,
                "history": session_commands.history,
                "export": session_commands.export,
            }
        )

        # Response inspection commands
        response_commands = ResponseCommands(self.shell)
        self.commands.update(
            {
                "inspect": response_commands.inspect,
                "extract": response_commands.extract,
                "validate": response_commands.validate,
            }
        )

        # Test generation commands
        generate_commands = GenerateCommands(self.shell)
        self.commands.update(
            {
                "generate": generate_commands.test,
            }
        )

        # Utility commands (built-in)
        self.commands.update(
            {
                "config": self._show_config,
                "clear": self._clear_screen,
                "help": self._show_help,
            }
        )

    async def execute(self, command: str, args: list[str]) -> None:
        """Execute a command with arguments"""
        if command in self.commands:
            await self.commands[command](args)
        else:
            print(f"❌ Unknown command: {command}")
            print("💡 Type 'help' to see available commands")

            # Suggest similar commands
            suggestions = self._get_similar_commands(command)
            if suggestions:
                print(f"📝 Did you mean: {', '.join(suggestions)}")

    def get_command_names(self) -> list[str]:
        """Get list of all command names for tab completion"""
        return sorted(self.commands.keys())

    def _get_similar_commands(
        self, command: str, max_suggestions: int = 3
    ) -> list[str]:
        """Get similar command suggestions using simple string distance"""
        suggestions = []

        for cmd_name in self.commands:
            # Simple similarity check
            if command.lower() in cmd_name.lower() or cmd_name.lower().startswith(
                command.lower()[:2]
            ):
                suggestions.append(cmd_name)

        return suggestions[:max_suggestions]

    async def _show_config(self, args: list[str]) -> None:
        """Show current configuration"""
        print("🔧 Current Configuration:")

        if self.shell.client:
            print(f"  📡 Base URL: {self.shell.client.base_url}")

            # Show auth info (without sensitive details)
            if hasattr(self.shell.client, "_auth") and self.shell.client._auth:
                auth_type = type(self.shell.client._auth).__name__
                print(f"  🔐 Authentication: {auth_type}")
            else:
                print("  🔐 Authentication: None")

            # Show timeout and other config
            if hasattr(self.shell.client, "_timeout"):
                print(f"  ⏱️  Timeout: {self.shell.client._timeout}s")
        else:
            print("  ⚠️  No API client configured")
            print("  💡 Use: get <endpoint> to configure automatically")
            print("  💡 Or start with: testapix interactive --api <url>")

        # Show session info
        session = self.shell.session_manager.current_session
        if session["requests"]:
            print(f"  📊 Session: {len(session['requests'])} requests made")
        else:
            print("  📊 Session: No requests yet")

        print()

    async def _clear_screen(self, args: list[str]) -> None:
        """Clear the screen"""
        # Use safer approach to clear screen
        if os.name == "nt":
            # Windows
            print("\033[H\033[J", end="")
        else:
            # Unix/Linux/macOS
            print("\033[2J\033[H", end="")

        # Reprint banner after clear
        self.shell._print_banner()

    async def _show_help(self, args: list[str]) -> None:
        """Show help information"""
        if args and args[0] in self.commands:
            # Show specific command help
            command_name = args[0]
            print(f"📖 Help for '{command_name}':")

            # Basic help for each command type
            help_text = {
                "get": "Send GET request to endpoint\nUsage: get <endpoint> [--params key=value] [--headers key:value]",
                "post": "Send POST request to endpoint\nUsage: post <endpoint> [--json {...}] [--headers key:value]",
                "put": "Send PUT request to endpoint\nUsage: put <endpoint> [--json {...}] [--headers key:value]",
                "patch": "Send PATCH request to endpoint\nUsage: patch <endpoint> [--json {...}] [--headers key:value]",
                "delete": "Send DELETE request to endpoint\nUsage: delete <endpoint> [--headers key:value]",
                "show": "Show detailed response information\nUsage: show <option>\nOptions: full, headers, body, status, json, raw",
                "save": "Save current session with a name\nUsage: save <session_name>",
                "load": "Load a previously saved session\nUsage: load [session_name]",
                "sessions": "List all saved sessions with details",
                "remove": "Delete a saved session permanently\nUsage: remove <session_name>",
                "history": "Show request history from current session\nUsage: history [limit]",
                "export": "Export current session to different formats\nUsage: export <format> [filename]",
                "inspect": "Inspect the last response in detail",
                "extract": "Extract data from last response\nUsage: extract <path|pattern>",
                "validate": "Validate last response against rules\nUsage: validate <rule>",
                "generate": "Generate test files from session\nUsage: generate test <type> [filename]",
                "auth": "Manage authentication\nUsage: auth <subcommand>\nSubcommands: bearer, apikey, basic, clear, status",
                "config": "Show current configuration and session status",
                "clear": "Clear the screen and show banner",
                "help": "Show this help message or help for specific command\nUsage: help [command]",
            }

            print(f"  {help_text.get(command_name, 'No detailed help available')}")
            print()
        else:
            # Show general help
            print("📖 TestAPIX Interactive Shell Commands:")
            print()
            print("🌐 HTTP Requests:")
            print("  get <endpoint>     - Send GET request")
            print("  post <endpoint>    - Send POST request")
            print("  put <endpoint>     - Send PUT request")
            print("  patch <endpoint>   - Send PATCH request")
            print("  delete <endpoint>  - Send DELETE request")
            print()
            print("💾 Session Management:")
            print("  save <name>        - Save current session")
            print("  load [name]        - Load saved session")
            print("  sessions           - List all sessions")
            print("  remove <name>      - Delete saved session")
            print("  history [limit]    - Show request history")
            print("  export <format>    - Export session")
            print()
            print("🔍 Response Analysis:")
            print(
                "  show <option>      - Show response details (full, headers, body, etc)"
            )
            print("  inspect            - Inspect last response")
            print("  extract <path>     - Extract data from response")
            print("  validate <rule>    - Validate response")
            print()
            print("⚡ Test Generation:")
            print("  generate test <type> - Generate test files")
            print()
            print("🔐 Authentication:")
            print("  auth status        - Show auth status")
            print("  auth bearer <token> - Set bearer token")
            print("  auth apikey <key>  - Set API key")
            print("  auth basic <u> <p> - Set basic auth")
            print("  auth clear         - Clear authentication")
            print()
            print("🛠️  Utility:")
            print("  config             - Show configuration")
            print("  clear              - Clear screen")
            print("  help [command]     - Show help")
            print("  exit               - Exit shell")
            print()
            print("💡 Tips:")
            print("  - Use Tab for command completion")
            print("  - Commands support --params and --headers options")
            print("  - POST/PUT/PATCH support --json for request body")
            print("  - Use 'help <command>' for detailed command help")
            print()
