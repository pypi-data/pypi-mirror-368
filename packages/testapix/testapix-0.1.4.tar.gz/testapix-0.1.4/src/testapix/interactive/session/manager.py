"""Session Manager for Interactive Shell

Handles session persistence and management for the interactive CLI.
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class SessionManager:
    """Manages interactive session persistence and history"""

    def __init__(self, sessions_dir: str | None = None) -> None:
        if sessions_dir is None:
            # Use .testapix directory in user's home
            home_dir = Path.home()
            sessions_dir_path = home_dir / ".testapix" / "sessions"
        else:
            sessions_dir_path = Path(sessions_dir)

        self.sessions_dir = sessions_dir_path
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        # Current session data
        self.current_session: dict[str, Any] = {
            "name": None,
            "created_at": datetime.now(UTC).isoformat(),
            "requests": [],
            "base_url": None,
            "auth_type": None,
            "auth_config": None,
        }

    def add_request(self, request_data: dict[str, Any]) -> None:
        """Add request to current session history"""
        request_data["timestamp"] = datetime.now(UTC).isoformat()
        requests_list = self.current_session.get("requests", [])
        if isinstance(requests_list, list):
            requests_list.append(request_data)
            self.current_session["requests"] = requests_list

        # Keep only last 100 requests to prevent memory issues
        requests_list = self.current_session.get("requests", [])
        if isinstance(requests_list, list) and len(requests_list) > 100:
            self.current_session["requests"] = requests_list[-100:]

    def save_session(
        self, name: str, base_url: str | None = None, auth_type: str | None = None
    ) -> bool:
        """Save current session to file"""
        try:
            session_data = {
                **self.current_session,
                "name": name,
                "base_url": base_url or self.current_session.get("base_url"),
                "auth_type": auth_type or self.current_session.get("auth_type"),
                "saved_at": datetime.now(UTC).isoformat(),
            }

            # Sanitize sensitive auth data for storage
            if session_data.get("auth_config"):
                session_data["auth_config"] = self._sanitize_auth_config(
                    session_data["auth_config"]
                )

            # Sanitize filename
            safe_name = "".join(
                c for c in name if c.isalnum() or c in ("-", "_")
            ).strip()
            if not safe_name:
                safe_name = "session"

            session_file = self.sessions_dir / f"{safe_name}.json"

            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)

            print(f"✅ Session saved: {name}")
            print(f"   📁 File: {session_file}")
            requests_list = session_data.get("requests", [])
            if isinstance(requests_list, list):
                print(f"   📊 Requests: {len(requests_list)}")
            if session_data.get("base_url"):
                print(f"   🌐 Base URL: {session_data['base_url']}")

            return True

        except Exception as e:
            print(f"❌ Failed to save session: {e}")
            return False

    def load_session(self, name: str) -> bool:
        """Load session from file"""
        try:
            # Try exact name first
            session_file = self.sessions_dir / f"{name}.json"

            # If not found, try to find a match
            if not session_file.exists():
                matching_files = list(self.sessions_dir.glob(f"*{name}*.json"))
                if matching_files:
                    session_file = matching_files[0]
                else:
                    print(f"❌ Session not found: {name}")
                    available_sessions = self.list_sessions()
                    if available_sessions:
                        print(f"💡 Available sessions: {', '.join(available_sessions)}")
                    return False

            with open(session_file, encoding="utf-8") as f:
                session_data = json.load(f)

            self.current_session = session_data

            print(f"✅ Session loaded: {session_data.get('name', name)}")

            # Show auth info if present
            auth_config = session_data.get("auth_config")
            if auth_config:
                auth_type = auth_config.get("type", "unknown")
                print(f"🔐 Authentication: {auth_type.title()}")
            else:
                print("🔓 Authentication: None")

            print("📊 Session contains:")

            for i, req in enumerate(session_data.get("requests", []), 1):
                status = req.get("response", {}).get("status_code", "Unknown")
                method = req.get("method", "Unknown")
                endpoint = req.get("endpoint", "Unknown")
                print(f"   {i}. {method} {endpoint} ({status})")

                # Limit display to first 10 requests
                if i >= 10 and len(session_data.get("requests", [])) > 10:
                    remaining = len(session_data.get("requests", [])) - 10
                    print(f"   ... and {remaining} more requests")
                    break

            return True

        except Exception as e:
            print(f"❌ Failed to load session: {e}")
            return False

    def list_sessions(self) -> list[str]:
        """List all saved sessions"""
        sessions = []
        try:
            for session_file in self.sessions_dir.glob("*.json"):
                sessions.append(session_file.stem)
        except Exception:
            pass  # Directory might not exist yet

        return sorted(sessions)

    def get_session_info(self, name: str) -> dict[str, Any] | None:
        """Get session information without fully loading it"""
        try:
            session_file = self.sessions_dir / f"{name}.json"
            if not session_file.exists():
                return None

            with open(session_file, encoding="utf-8") as f:
                session_data = json.load(f)

            # Return summary info
            return {
                "name": session_data.get("name", name),
                "created_at": session_data.get("created_at"),
                "saved_at": session_data.get("saved_at"),
                "request_count": len(session_data.get("requests", [])),
                "base_url": session_data.get("base_url"),
                "auth_type": session_data.get("auth_type"),
            }
        except Exception:
            return None

    def delete_session(self, name: str) -> bool:
        """Delete a saved session"""
        try:
            # Try exact name first
            session_file = self.sessions_dir / f"{name}.json"

            # If not found, try to find a match
            if not session_file.exists():
                matching_files = list(self.sessions_dir.glob(f"*{name}*.json"))
                if matching_files:
                    session_file = matching_files[0]
                else:
                    print(f"❌ Session not found: {name}")
                    available_sessions = self.list_sessions()
                    if available_sessions:
                        print(f"💡 Available sessions: {', '.join(available_sessions)}")
                    return False

            # Get session info before deleting for confirmation message
            actual_name = session_file.stem
            session_info = self.get_session_info(actual_name)

            # Delete the file
            session_file.unlink()

            print(f"✅ Session deleted: {actual_name}")
            if session_info:
                print(f"   📊 Had {session_info.get('request_count', 0)} requests")
                if session_info.get("base_url"):
                    print(f"   🌐 Base URL: {session_info['base_url']}")

            return True

        except Exception as e:
            print(f"❌ Failed to delete session: {e}")
            return False

    def clear_current_session(self) -> None:
        """Clear current session data"""
        self.current_session = {
            "name": None,
            "created_at": datetime.now(UTC).isoformat(),
            "requests": [],
            "base_url": self.current_session.get("base_url"),  # Keep base_url
            "auth_type": self.current_session.get("auth_type"),  # Keep auth_type
            "auth_config": self.current_session.get("auth_config"),  # Keep auth_config
        }
        print("✅ Current session cleared")

    def _sanitize_auth_config(self, auth_config: dict[str, Any]) -> dict[str, Any]:
        """Sanitize auth config for secure storage by masking sensitive data"""
        if not auth_config:
            return auth_config

        sanitized = auth_config.copy()

        # Mask sensitive values but preserve structure for loading
        if "token" in sanitized:
            token = sanitized["token"]
            if len(token) > 8:
                sanitized["token"] = token[:4] + "*" * (len(token) - 8) + token[-4:]
            else:
                sanitized["token"] = "*" * len(token)

        if "api_key" in sanitized:
            key = sanitized["api_key"]
            if len(key) > 8:
                sanitized["api_key"] = key[:4] + "*" * (len(key) - 8) + key[-4:]
            else:
                sanitized["api_key"] = "*" * len(key)

        if "password" in sanitized:
            sanitized["password"] = "*" * len(sanitized["password"])

        # Add warning that this is sanitized data
        sanitized["_sanitized"] = True

        return sanitized

    def get_request_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent request history"""
        requests = self.current_session.get("requests", [])
        if isinstance(requests, list):
            return requests[-limit:] if requests else []
        return []
