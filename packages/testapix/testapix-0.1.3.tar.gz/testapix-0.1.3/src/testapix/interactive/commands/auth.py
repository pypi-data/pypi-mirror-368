"""Authentication Commands for Interactive Shell

Commands for managing authentication in the interactive CLI.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from testapix.interactive.shell import InteractiveShell


class AuthCommands:
    """Authentication command handlers"""

    def __init__(self, shell: "InteractiveShell") -> None:
        self.shell = shell

    async def auth(self, args: list[str]) -> None:
        """Handle authentication commands"""
        if not args:
            await self._show_auth_status()
            return

        subcommand = args[0].lower()
        remaining_args = args[1:]

        if subcommand == "bearer":
            await self._set_bearer_auth(remaining_args)
        elif subcommand == "apikey":
            await self._set_apikey_auth(remaining_args)
        elif subcommand == "basic":
            await self._set_basic_auth(remaining_args)
        elif subcommand == "clear":
            await self._clear_auth()
        elif subcommand == "status":
            await self._show_auth_status()
        else:
            await self._show_auth_help()

    async def _set_bearer_auth(self, args: list[str]) -> None:
        """Set Bearer token authentication"""
        if not args:
            print("❌ Usage: auth bearer <token>")
            print("💡 Example: auth bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
            return

        token = args[0]
        if not token:
            print("❌ Token cannot be empty")
            return

        # Store auth configuration
        auth_config = {"type": "bearer", "token": token}
        self.shell.session_manager.current_session["auth_config"] = auth_config
        self.shell.session_manager.current_session["auth_type"] = "bearer"

        # Recreate HTTPClient with authentication
        await self.shell._recreate_client_with_auth(auth_config)

        print("✅ Bearer token authentication configured")
        print("🔐 All requests will now include: Authorization: Bearer ***")

    async def _set_apikey_auth(self, args: list[str]) -> None:
        """Set API Key authentication"""
        if not args:
            print("❌ Usage: auth apikey <key> [header_name]")
            print("💡 Examples:")
            print("  auth apikey sk_1234567890abcdef")
            print("  auth apikey 1234567890abcdef X-API-Key")
            return

        api_key = args[0]
        header_name = args[1] if len(args) > 1 else "X-API-Key"

        if not api_key:
            print("❌ API key cannot be empty")
            return

        # Store auth configuration
        auth_config = {"type": "apikey", "api_key": api_key, "header_name": header_name}
        self.shell.session_manager.current_session["auth_config"] = auth_config
        self.shell.session_manager.current_session["auth_type"] = "apikey"

        # Recreate HTTPClient with authentication
        await self.shell._recreate_client_with_auth(auth_config)

        print("✅ API Key authentication configured")
        print(f"🔐 All requests will now include: {header_name}: ***")

    async def _set_basic_auth(self, args: list[str]) -> None:
        """Set Basic authentication"""
        if len(args) < 2:
            print("❌ Usage: auth basic <username> <password>")
            print("💡 Example: auth basic myuser mypassword")
            return

        username = args[0]
        password = args[1]

        if not username or not password:
            print("❌ Username and password cannot be empty")
            return

        # Store auth configuration
        auth_config = {"type": "basic", "username": username, "password": password}
        self.shell.session_manager.current_session["auth_config"] = auth_config
        self.shell.session_manager.current_session["auth_type"] = "basic"

        # Recreate HTTPClient with authentication
        await self.shell._recreate_client_with_auth(auth_config)

        print("✅ Basic authentication configured")
        print(
            f"🔐 All requests will now include: Authorization: Basic *** (user: {username})"
        )

    async def _clear_auth(self) -> None:
        """Clear authentication"""
        # Clear auth from session
        self.shell.session_manager.current_session["auth_config"] = None
        self.shell.session_manager.current_session["auth_type"] = None

        # Recreate HTTPClient without authentication
        await self.shell._recreate_client_with_auth(None)

        print("✅ Authentication cleared")
        print("🔓 Requests will no longer include authentication headers")

    async def _show_auth_status(self) -> None:
        """Show current authentication status"""
        print("🔐 **Authentication Status**")
        print()

        auth_config = self.shell.session_manager.current_session.get("auth_config")

        if not auth_config:
            print("🔓 No authentication configured")
            print()
            print("💡 Configure authentication with:")
            print("  • auth bearer <token>")
            print("  • auth apikey <key> [header_name]")
            print("  • auth basic <username> <password>")
            return

        auth_type = auth_config.get("type", "unknown")

        if auth_type == "bearer":
            token = auth_config.get("token", "")
            masked_token = token[:8] + "..." + token[-4:] if len(token) > 12 else "***"
            print("✅ **Bearer Token Authentication**")
            print(f"   Token: {masked_token}")
            print("   Header: Authorization: Bearer ***")

        elif auth_type == "apikey":
            api_key = auth_config.get("api_key", "")
            header_name = auth_config.get("header_name", "X-API-Key")
            masked_key = (
                api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "***"
            )
            print("✅ **API Key Authentication**")
            print(f"   Key: {masked_key}")
            print(f"   Header: {header_name}: ***")

        elif auth_type == "basic":
            username = auth_config.get("username", "")
            print("✅ **Basic Authentication**")
            print(f"   Username: {username}")
            print("   Header: Authorization: Basic ***")

        else:
            print(f"❓ Unknown authentication type: {auth_type}")

        print()
        print("💡 Use 'auth clear' to remove authentication")

    async def _show_auth_help(self) -> None:
        """Show authentication help"""
        print("❌ Unknown auth command")
        print()
        print("🔐 **Authentication Commands**:")
        print()
        print("📖 **Available commands:**")
        print("  auth status              - Show current authentication")
        print("  auth bearer <token>      - Set Bearer token auth")
        print("  auth apikey <key> [hdr]  - Set API key auth")
        print("  auth basic <user> <pass> - Set Basic auth")
        print("  auth clear               - Clear authentication")
        print()
        print("💡 **Examples:**")
        print("  auth bearer eyJhbGciOiJIUzI1NiIs...")
        print("  auth apikey sk_1234567890abcdef")
        print("  auth apikey abcd1234 X-Custom-Key")
        print("  auth basic myuser mypassword")
        print()
