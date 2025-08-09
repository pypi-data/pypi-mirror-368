"""Session Management Commands for Interactive Shell

Commands for saving, loading, and managing interactive sessions.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from testapix.interactive.shell import InteractiveShell


class SessionCommands:
    """Session management command handlers"""

    def __init__(self, shell: "InteractiveShell") -> None:
        self.shell = shell

    async def save(self, args: list[str]) -> None:
        """Save current session with a name"""
        if not args:
            print("❌ Usage: save <session_name>")
            print("💡 Example: save my-api-exploration")
            return

        session_name = args[0]

        # Get current session info
        base_url = self.shell.client.base_url if self.shell.client else None
        auth_type = None
        if (
            self.shell.client
            and hasattr(self.shell.client, "_auth")
            and self.shell.client._auth
        ):
            auth_type = type(self.shell.client._auth).__name__

        # Save the session
        success = self.shell.session_manager.save_session(
            name=session_name, base_url=base_url, auth_type=auth_type
        )

        if success:
            print(f"💾 Session '{session_name}' saved successfully!")

            # Show session stats
            current_session = self.shell.session_manager.current_session
            request_count = len(current_session.get("requests", []))
            if request_count > 0:
                print(f"📊 Saved {request_count} requests from this session")
            if base_url:
                print(f"🌐 Base URL: {base_url}")
        else:
            print(f"❌ Failed to save session '{session_name}'")

    async def load(self, args: list[str]) -> None:
        """Load a previously saved session"""
        if not args:
            # Show available sessions
            sessions = self.shell.session_manager.list_sessions()
            if not sessions:
                print("📂 No saved sessions found")
                print("💡 Use 'save <name>' to save your current session")
                return

            print("📂 Available sessions:")
            for session_name in sessions:
                session_info = self.shell.session_manager.get_session_info(session_name)
                if session_info:
                    request_count = session_info.get("request_count", 0)
                    saved_at = session_info.get("saved_at", "Unknown")
                    base_url = session_info.get("base_url", "No URL")
                    print(f"  📄 {session_name}")
                    print(
                        f"     🗓️  Saved: {saved_at[:19] if saved_at != 'Unknown' else saved_at}"
                    )
                    print(f"     📊 Requests: {request_count}")
                    print(f"     🌐 URL: {base_url}")
                else:
                    print(f"  📄 {session_name}")

            print("\n💡 Use 'load <session_name>' to load a specific session")
            return

        session_name = args[0]

        # Load the session
        success = self.shell.session_manager.load_session(session_name)

        if success:
            # Update shell client if session has base URL
            session_data = self.shell.session_manager.current_session
            if session_data.get("base_url") and not self.shell.client:
                try:
                    from testapix.core.client import HTTPClient

                    self.shell.client = HTTPClient(base_url=session_data["base_url"])
                    print(f"🌐 Connected to: {session_data['base_url']}")
                except Exception as e:
                    print(f"⚠️  Could not connect to API: {e}")

            # Apply authentication if present in loaded session
            auth_config = session_data.get("auth_config")
            if auth_config and self.shell.client:
                await self.shell._recreate_client_with_auth(auth_config)
                print("🔐 Authentication applied from session")

            print(f"✅ Session '{session_name}' loaded successfully!")
        else:
            print(f"❌ Failed to load session '{session_name}'")

    async def sessions(self, args: list[str]) -> None:
        """List all saved sessions with details"""
        sessions = self.shell.session_manager.list_sessions()

        if not sessions:
            print("📂 No saved sessions found")
            print("💡 Use 'save <name>' to save your current session")
            return

        print(f"📂 Found {len(sessions)} saved session(s):\n")

        for session_name in sessions:
            session_info = self.shell.session_manager.get_session_info(session_name)
            if session_info:
                print(f"📄 **{session_name}**")
                print(
                    f"   🗓️  Created: {session_info.get('created_at', 'Unknown')[:19]}"
                )
                print(f"   💾 Saved: {session_info.get('saved_at', 'Unknown')[:19]}")
                print(f"   📊 Requests: {session_info.get('request_count', 0)}")
                print(f"   🌐 Base URL: {session_info.get('base_url', 'None')}")
                if session_info.get("auth_type"):
                    print(f"   🔐 Auth: {session_info['auth_type']}")
                print()

        print("💡 Use 'load <session_name>' to load a session")

    async def delete(self, args: list[str]) -> None:
        """Delete a saved session"""
        if not args:
            print("❌ Usage: remove <session_name>")
            print("💡 Example: remove my-api-exploration")

            # Show available sessions
            sessions = self.shell.session_manager.list_sessions()
            if sessions:
                print("\n📂 Available sessions:")
                for session_name in sessions[:5]:  # Show first 5
                    print(f"  📄 {session_name}")
                if len(sessions) > 5:
                    print(f"  ... and {len(sessions) - 5} more")
                print("\n💡 Use 'sessions' to see all saved sessions")
            return

        session_name = args[0]

        # Delete the session
        success = self.shell.session_manager.delete_session(session_name)

        if success:
            print("⚠️  Session permanently deleted from disk")
            print("💡 Use 'save <name>' to save your current session if needed")
        else:
            print("💡 Use 'sessions' to see available sessions")

    async def clear(self, args: list[str]) -> None:
        """Clear current session data"""
        current_requests = len(
            self.shell.session_manager.current_session.get("requests", [])
        )

        if current_requests == 0:
            print("📋 Session is already empty")
            return

        # Ask for confirmation if session has data
        print(f"⚠️  This will clear {current_requests} requests from current session")
        print("💡 Consider saving with 'save <name>' first")

        # For now, just clear without confirmation in CLI
        # In a real terminal, you'd want to add confirmation
        self.shell.session_manager.clear_current_session()
        print("✅ Current session cleared")

    async def history(self, args: list[str]) -> None:
        """Show request history from current session"""
        limit = 10  # Default limit

        if args:
            try:
                limit = int(args[0])
                if limit <= 0:
                    print("❌ Limit must be a positive number")
                    return
            except ValueError:
                print("❌ Invalid limit. Please provide a number")
                print("💡 Usage: history [limit]")
                return

        history = self.shell.session_manager.get_request_history(limit)

        if not history:
            print("📋 No requests in current session")
            print("💡 Make some API requests to build up history")
            return

        print(f"📋 Last {len(history)} request(s):\n")

        for i, request in enumerate(reversed(history), 1):
            method = request.get("method", "Unknown")
            endpoint = request.get("endpoint", "Unknown")
            response = request.get("response", {})
            status_code = response.get("status_code", "Unknown")
            response_time = response.get("response_time", 0)
            timestamp = request.get("timestamp", "")

            # Format timestamp
            time_str = timestamp[:19] if timestamp else "Unknown"

            # Status emoji
            if isinstance(status_code, int):
                if status_code < 300:
                    status_emoji = "✅"
                elif status_code < 400:
                    status_emoji = "🔄"
                else:
                    status_emoji = "❌"
            else:
                status_emoji = "❓"

            print(f"{i:2d}. {status_emoji} {method} {endpoint}")
            print(f"    📊 {status_code} ({response_time:.0f}ms) at {time_str}")

            # Show request details if available
            kwargs = request.get("kwargs", {})
            if kwargs.get("params"):
                params_str = ", ".join(f"{k}={v}" for k, v in kwargs["params"].items())
                print(f"    🔍 Params: {params_str}")
            if kwargs.get("json"):
                json_preview = str(kwargs["json"])[:50]
                if len(str(kwargs["json"])) > 50:
                    json_preview += "..."
                print(f"    📝 JSON: {json_preview}")
            print()

        if len(history) == limit and limit < 100:  # Max stored is 100
            print(f"💡 Use 'history {limit + 10}' to see more requests")

    async def export(self, args: list[str]) -> None:
        """Export current session to different formats"""
        if not args:
            print("❌ Usage: export <format> [filename]")
            print("📋 Available formats:")
            print("  • json     - Export as JSON file")
            print("  • curl     - Export as curl commands")
            print("  • python   - Export as Python requests code")
            print("💡 Example: export json my-session")
            return

        format_type = args[0].lower()
        filename = args[1] if len(args) > 1 else None

        if format_type not in ["json", "curl", "python"]:
            print(f"❌ Unsupported format: {format_type}")
            print("💡 Supported formats: json, curl, python")
            return

        history = self.shell.session_manager.get_request_history(
            100
        )  # Get all requests

        if not history:
            print("📋 No requests to export")
            return

        # For now, just show what would be exported
        print(f"📤 Would export {len(history)} requests as {format_type}")
        if filename:
            print(f"📁 Filename: {filename}.{format_type}")
        else:
            print(f"📁 Default filename: session-export.{format_type}")

        print("🚧 Export functionality coming soon!")
        print("💡 For now, use 'save <name>' to save your session")
