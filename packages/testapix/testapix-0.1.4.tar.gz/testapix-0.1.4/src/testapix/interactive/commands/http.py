"""HTTP Commands for Interactive Shell

Handlers for HTTP request commands (GET, POST, PUT, PATCH, DELETE).
"""

import json
from typing import TYPE_CHECKING, Any

try:
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.table import Table

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None  # type: ignore
    Syntax = None  # type: ignore
    Table = None  # type: ignore

if TYPE_CHECKING:
    from testapix.interactive.shell import InteractiveShell


class HTTPCommands:
    """HTTP request command handlers"""

    def __init__(self, shell: "InteractiveShell"):
        self.shell = shell
        self.console = Console() if RICH_AVAILABLE else None

    async def get(self, args: list[str]) -> None:
        """Handle GET request command"""
        if not args:
            print("❌ Usage: get <endpoint> [--params key=value] [--headers key:value]")
            print("💡 Example: get /users --params page=1 limit=10")
            return

        endpoint = args[0]
        params, headers = self._parse_request_options(args[1:])

        await self._execute_request("GET", endpoint, params=params, headers=headers)

    async def post(self, args: list[str]) -> None:
        """Handle POST request command"""
        if not args:
            print("❌ Usage: post <endpoint> [--json {...}] [--headers key:value]")
            print(
                '💡 Example: post /users --json \'{"name":"John","email":"john@example.com"}\''
            )
            return

        endpoint = args[0]
        params, headers, json_data = self._parse_request_options_with_json(args[1:])

        # If no JSON provided, prompt user
        if json_data is None:
            json_data = await self._prompt_for_json()
            if json_data is None:
                print("⚠️  Request cancelled")
                return

        await self._execute_request("POST", endpoint, json=json_data, headers=headers)

    async def put(self, args: list[str]) -> None:
        """Handle PUT request command"""
        if not args:
            print("❌ Usage: put <endpoint> [--json {...}] [--headers key:value]")
            return

        endpoint = args[0]
        params, headers, json_data = self._parse_request_options_with_json(args[1:])

        if json_data is None:
            json_data = await self._prompt_for_json()
            if json_data is None:
                print("⚠️  Request cancelled")
                return

        await self._execute_request("PUT", endpoint, json=json_data, headers=headers)

    async def patch(self, args: list[str]) -> None:
        """Handle PATCH request command"""
        if not args:
            print("❌ Usage: patch <endpoint> [--json {...}] [--headers key:value]")
            return

        endpoint = args[0]
        params, headers, json_data = self._parse_request_options_with_json(args[1:])

        if json_data is None:
            json_data = await self._prompt_for_json()
            if json_data is None:
                print("⚠️  Request cancelled")
                return

        await self._execute_request("PATCH", endpoint, json=json_data, headers=headers)

    async def delete(self, args: list[str]) -> None:
        """Handle DELETE request command"""
        if not args:
            print("❌ Usage: delete <endpoint> [--headers key:value]")
            return

        endpoint = args[0]
        params, headers = self._parse_request_options(args[1:])

        await self._execute_request("DELETE", endpoint, headers=headers)

    async def show(self, args: list[str]) -> None:
        """Show detailed response information"""
        if not self.shell.last_response:
            print("❌ No response available. Make a request first.")
            return

        if not args:
            print("❌ Usage: show <option>")
            print("💡 Options: full, headers, body, status, json, raw")
            return

        option = args[0].lower()
        response = self.shell.last_response

        if option == "full":
            await self._show_full_response()
        elif option == "headers":
            await self._show_headers()
        elif option == "body":
            await self._show_body()
        elif option == "status":
            await self._show_status()
        elif option == "json":
            await self._show_json()
        elif option == "raw":
            await self._show_raw()
        else:
            print(f"❌ Unknown option: {option}")
            print("💡 Options: full, headers, body, status, json, raw")

    async def inspect(self, args: list[str]) -> None:
        """Inspect last response with detailed analysis"""
        if not self.shell.last_response:
            print("❌ No response available. Make a request first.")
            return

        response = self.shell.last_response
        print("🔍 **Response Inspector**")
        print()

        # Request details
        print("📤 **Request:**")
        print(f"   Method: {response.request.method}")
        print(f"   URL: {response.request.url}")
        if hasattr(response, "request") and response.request.content:
            print(f"   Body size: {len(response.request.content)} bytes")
        print()

        # Response summary
        response_time = getattr(response, "response_time", 0)
        status_emoji = (
            "✅"
            if response.status_code < 300
            else "❌"
            if response.status_code >= 400
            else "🔄"
        )
        print("📥 **Response:**")
        print(
            f"   {status_emoji} Status: {response.status_code} {response.reason_phrase}"
        )
        print(f"   ⏱️  Time: {response_time:.0f}ms")
        print(f"   📄 Size: {len(response.content)} bytes")
        print()

        # Content type analysis
        content_type = response.headers.get("content-type", "unknown")
        print(f"📋 **Content Type:** {content_type}")

        # JSON path suggestions if applicable
        if "application/json" in content_type.lower():
            try:
                data = response.json()
                print("🔍 **JSON Structure:**")
                self._analyze_json_structure(data, "", max_depth=2)
            except:
                pass

        print()
        print("💡 **Quick commands:**")
        print("   show full    - Show complete response")
        print("   show json    - Show formatted JSON")
        print("   show headers - Show all headers")
        print("   show body    - Show response body")

    def _parse_request_options(
        self, args: list[str]
    ) -> tuple[dict[str, str], dict[str, str]]:
        """Parse request options (params and headers)"""
        params = {}
        headers = {}

        i = 0
        while i < len(args):
            if args[i] == "--params" and i + 1 < len(args):
                param = args[i + 1]
                if "=" in param:
                    key, value = param.split("=", 1)
                    params[key.strip()] = value.strip()
                i += 2
            elif args[i] == "--headers" and i + 1 < len(args):
                header = args[i + 1]
                if ":" in header:
                    key, value = header.split(":", 1)
                    headers[key.strip()] = value.strip()
                i += 2
            else:
                i += 1

        return params, headers

    def _parse_request_options_with_json(
        self, args: list[str]
    ) -> tuple[dict[str, str], dict[str, str], Any]:
        """Parse request options including JSON body"""
        params = {}
        headers = {}
        json_data = None

        i = 0
        while i < len(args):
            if args[i] == "--params" and i + 1 < len(args):
                param = args[i + 1]
                if "=" in param:
                    key, value = param.split("=", 1)
                    params[key.strip()] = value.strip()
                i += 2
            elif args[i] == "--headers" and i + 1 < len(args):
                header = args[i + 1]
                if ":" in header:
                    key, value = header.split(":", 1)
                    headers[key.strip()] = value.strip()
                i += 2
            elif args[i] == "--json" and i + 1 < len(args):
                try:
                    json_data = json.loads(args[i + 1])
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON: {e}")
                    return params, headers, None
                i += 2
            else:
                i += 1

        return params, headers, json_data

    async def _prompt_for_json(self) -> Any:
        """Prompt user for JSON input"""
        print("📝 Enter JSON body for request:")
        print('💡 Example: {"name": "John", "email": "john@example.com"}')
        print("💡 Press Enter on empty line to skip, or type 'cancel' to abort")

        try:
            json_input = input("JSON: ").strip()

            if not json_input or json_input.lower() == "cancel":
                return None

            return json.loads(json_input)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            return None
        except (KeyboardInterrupt, EOFError):
            return None

    async def _execute_request(self, method: str, endpoint: str, **kwargs: Any) -> None:
        """Execute HTTP request and display results"""
        # Ensure we have an API client
        if not self.shell.client:
            print("❌ No API client configured.")
            print("💡 Start shell with: testapix interactive --api <base-url>")
            print("💡 Or set up client first")
            return

        try:
            # Clean up endpoint
            if not endpoint.startswith("/"):
                endpoint = "/" + endpoint

            full_url = f"{self.shell.client.base_url.rstrip('/')}{endpoint}"
            print(f"🔄 {method} {full_url}")

            # Execute request based on method
            client_method = getattr(self.shell.client, method.lower())
            response = await client_method(endpoint, **kwargs)

            # Store response for inspection
            self.shell.last_response = response

            # Display results
            self._display_response(response)

            # Add to session history
            self.shell.session_manager.add_request(
                {
                    "method": method,
                    "endpoint": endpoint,
                    "kwargs": self._sanitize_kwargs(kwargs),
                    "response": {
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "body": response.text[:1000],  # Truncate large responses
                        "response_time": getattr(response, "response_time", 0),
                    },
                }
            )

            # Show suggestions for next actions
            self._show_suggestions(response, endpoint)

        except Exception as e:
            print(f"❌ Request failed: {e}")
            print("💡 Check your endpoint URL and authentication")

    def _sanitize_kwargs(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Sanitize kwargs for storage (remove sensitive data)"""
        sanitized = kwargs.copy()

        # Remove or mask sensitive headers
        if "headers" in sanitized:
            headers = sanitized["headers"].copy()
            for key in headers:
                if key.lower() in ["authorization", "x-api-key", "cookie"]:
                    headers[key] = "***"
            sanitized["headers"] = headers

        return sanitized

    def _display_response(
        self, response: Any, full: bool = False, limit: int = 300
    ) -> None:
        """Display formatted response"""
        # Status line with color coding
        if response.status_code < 300:
            status_emoji = "✅"
        elif response.status_code < 400:
            status_emoji = "🔄"
        else:
            status_emoji = "❌"

        response_time = getattr(response, "response_time", 0)
        print(
            f"{status_emoji} {response.status_code} {response.reason_phrase} ({response_time:.0f}ms)"
        )

        # Important headers
        self._display_important_headers(response.headers)

        # Body preview
        self._display_response_body(response, full=full, limit=limit)

        print()  # Empty line for spacing

    def _display_important_headers(self, headers: dict[str, str]) -> None:
        """Display important response headers"""
        important_headers = [
            "content-type",
            "content-length",
            "location",
            "x-rate-limit",
            "x-rate-remaining",
            "x-rate-reset",
            "cache-control",
            "etag",
            "last-modified",
        ]

        displayed_headers = []
        for header in important_headers:
            if header in headers:
                displayed_headers.append(f"{header}: {headers[header]}")

        if displayed_headers:
            print("📋 Headers:")
            for header_line in displayed_headers[:5]:  # Limit to 5 headers
                print(f"  {header_line}")

        if len(displayed_headers) > 5:
            print(f"  ... and {len(displayed_headers) - 5} more headers")

    def _display_response_body(
        self, response: Any, full: bool = False, limit: int = 300
    ) -> None:
        """Display response body with intelligent formatting"""
        content_type = response.headers.get("content-type", "").lower()

        if "application/json" in content_type:
            try:
                json_data = response.json()
                if full:
                    self._display_json_full(json_data)
                else:
                    self._display_json_preview(json_data)
            except json.JSONDecodeError:
                body_text = response.text
                if full or len(body_text) <= limit:
                    print(f"📄 Full Response Body: {body_text}")
                else:
                    print(f"📄 Body: {body_text[:limit]}...")
        elif "text/" in content_type:
            body_text = response.text
            if full or len(body_text) <= limit:
                print(f"📄 Full Response Body: {body_text}")
            else:
                print(f"📄 Body: {body_text[:limit]}...")
        else:
            content_length = len(response.content)
            if full:
                print(f"📄 Full Binary Response: ({content_length} bytes)")
                if content_length > 0:
                    print(f"📄 Binary content: {response.content[:200]}...")
            else:
                print(f"📄 Body: Binary content ({content_length} bytes)")
                if content_length > 0:
                    print(f"📄 Binary preview: {response.content[:100]}...")

    def _display_json_preview(self, data: Any) -> None:
        """Display JSON data with smart preview"""
        if isinstance(data, dict):
            # Check for common collection patterns
            collection_keys = [
                "users",
                "items",
                "products",
                "orders",
                "data",
                "results",
            ]
            collection_key = None

            for key in collection_keys:
                if key in data and isinstance(data[key], list):
                    collection_key = key
                    break

            if collection_key:
                items = data[collection_key]
                print(f"📊 Response: {len(items)} {collection_key} found")

                if items:
                    # Show sample item
                    sample_item = items[0]
                    print("📋 Sample item:")
                    if isinstance(sample_item, dict):
                        # Show first few fields of sample item
                        sample_fields = dict(list(sample_item.items())[:3])
                        for key, value in sample_fields.items():
                            print(f"  {key}: {value}")
                        if len(sample_item) > 3:
                            print(f"  ... and {len(sample_item) - 3} more fields")
                    else:
                        print(f"  {sample_item}")
            else:
                # Regular object - show first few fields
                print("📄 Response object:")
                if isinstance(data, dict):
                    items = list(data.items())[:5]
                    for key, value in items:
                        if isinstance(value, (str, int, float, bool)):
                            print(f"  {key}: {value}")
                        else:
                            print(f"  {key}: {type(value).__name__}")

                    if len(data) > 5:
                        print(f"  ... and {len(data) - 5} more fields")
        elif isinstance(data, list):
            print(f"📊 Response: Array with {len(data)} items")
            if data:
                print(f"📋 Sample item: {data[0]}")
        else:
            print(f"📄 Response: {data}")

    def _display_json_full(self, data: Any) -> None:
        """Display full JSON data with pretty formatting"""
        try:
            if self.console and RICH_AVAILABLE:
                formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
                print("📄 Full JSON Response:")
                syntax = Syntax(
                    formatted_json, "json", theme="monokai", line_numbers=False
                )
                self.console.print(syntax)
            else:
                formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
                print("📄 Full JSON Response:")
                print(formatted_json)
        except Exception as e:
            print(f"📄 JSON Response (raw): {data}")
            print(f"💥 JSON formatting error: {e}")

    def _show_suggestions(self, response: Any, endpoint: str) -> None:
        """Show suggestions for next actions based on response"""
        suggestions = []

        # Suggest related endpoints based on current endpoint
        if endpoint == "/users" and response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict) and "users" in data and data["users"]:
                    first_user_id = data["users"][0].get("id")
                    if first_user_id:
                        suggestions.append(f"get /users/{first_user_id}")
            except:
                pass

        # Suggest pagination for collection endpoints
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict) and any(
                    key in data for key in ["pagination", "paging", "meta"]
                ):
                    suggestions.append(f"get {endpoint}?page=2")
            except:
                pass

        # Show suggestions if any
        if suggestions:
            print("💡 Suggested next actions:")
            for i, suggestion in enumerate(suggestions[:3], 1):
                print(f"  {i}. {suggestion}")
            print()

    async def _show_full_response(self) -> None:
        """Show complete response details"""
        response = self.shell.last_response
        if not response:
            print("❌ No response available")
            return
        print("📋 **Complete Response Details**")
        print()

        # Status and timing
        response_time = getattr(response, "response_time", 0)
        status_emoji = (
            "✅"
            if response.status_code < 300
            else "❌"
            if response.status_code >= 400
            else "🔄"
        )
        print(
            f"{status_emoji} **Status:** {response.status_code} {response.reason_phrase}"
        )
        print(f"⏱️  **Response Time:** {response_time:.0f}ms")
        print()

        # All headers
        print("📋 **All Headers:**")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        print()

        # Full body
        self._display_response_body(response, full=True)

    async def _show_headers(self) -> None:
        """Show all response headers"""
        response = self.shell.last_response
        if not response:
            print("❌ No response available")
            return
        print("📋 **Response Headers**")
        print()

        if self.console and RICH_AVAILABLE:
            table = Table(show_header=True, header_style="bold blue")
            table.add_column("Header", style="cyan")
            table.add_column("Value", style="white")

            for key, value in response.headers.items():
                table.add_row(key, value)

            self.console.print(table)
        else:
            for key, value in response.headers.items():
                print(f"  {key}: {value}")

    async def _show_body(self) -> None:
        """Show full response body"""
        response = self.shell.last_response
        if not response:
            print("❌ No response available")
            return
        print("📄 **Response Body**")
        print()

        content_type = response.headers.get("content-type", "").lower()

        if "application/json" in content_type:
            try:
                data = response.json()
                if self.console and RICH_AVAILABLE:
                    json_text = json.dumps(data, indent=2, ensure_ascii=False)
                    syntax = Syntax(
                        json_text, "json", theme="monokai", line_numbers=True
                    )
                    self.console.print(syntax)
                else:
                    formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
                    print(formatted_json)
            except json.JSONDecodeError:
                print(response.text)
        else:
            print(response.text)

    async def _show_status(self) -> None:
        """Show response status details"""
        response = self.shell.last_response
        if not response:
            print("❌ No response available")
            return
        response_time = getattr(response, "response_time", 0)

        status_emoji = (
            "✅"
            if response.status_code < 300
            else "❌"
            if response.status_code >= 400
            else "🔄"
        )

        print("📊 **Response Status**")
        print()
        print(f"{status_emoji} **Status Code:** {response.status_code}")
        print(f"📝 **Reason:** {response.reason_phrase}")
        print(f"⏱️  **Response Time:** {response_time:.0f}ms")
        print(f"📄 **Content Length:** {len(response.content)} bytes")
        print(f"🌐 **URL:** {response.url}")

    async def _show_json(self) -> None:
        """Show formatted JSON response"""
        response = self.shell.last_response
        if not response:
            print("❌ No response available")
            return
        content_type = response.headers.get("content-type", "").lower()

        if "application/json" not in content_type:
            print("⚠️  Response is not JSON format")
            print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
            return

        try:
            data = response.json()
            print("🔍 **JSON Response (Formatted)**")
            print()

            if self.console and RICH_AVAILABLE:
                json_text = json.dumps(data, indent=2, ensure_ascii=False)
                syntax = Syntax(json_text, "json", theme="monokai", line_numbers=True)
                self.console.print(syntax)
            else:
                formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
                print(formatted_json)

        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            print("Raw response:")
            print(response.text)

    async def _show_raw(self) -> None:
        """Show raw response data"""
        response = self.shell.last_response
        if not response:
            print("❌ No response available")
            return
        print("📄 **Raw Response**")
        print()

        print("📤 **Request Line:**")
        print(f"{response.request.method} {response.request.url} HTTP/1.1")
        print()

        print("📥 **Response Line:**")
        print(f"HTTP/1.1 {response.status_code} {response.reason_phrase}")
        print()

        print("📋 **Headers:**")
        for key, value in response.headers.items():
            print(f"{key}: {value}")
        print()

        print("📄 **Body:**")
        print(response.text)

    def _analyze_json_structure(
        self, data: Any, path: str, max_depth: int = 3, current_depth: int = 0
    ) -> None:
        """Analyze JSON structure and suggest paths"""
        if current_depth >= max_depth:
            return

        if isinstance(data, dict):
            for key, value in list(data.items())[:5]:  # Limit to 5 items per level
                current_path = f"{path}.{key}" if path else key
                value_type = type(value).__name__

                if isinstance(value, (dict, list)):
                    item_count = len(value)
                    print(f"   {current_path}: {value_type}({item_count})")
                    if current_depth < max_depth - 1:
                        self._analyze_json_structure(
                            value, current_path, max_depth, current_depth + 1
                        )
                else:
                    print(f"   {current_path}: {value_type} = {value}")

        elif isinstance(data, list) and data:
            print(f"   {path}[0]: {type(data[0]).__name__}")
            if isinstance(data[0], dict):
                self._analyze_json_structure(
                    data[0], f"{path}[0]", max_depth, current_depth + 1
                )
