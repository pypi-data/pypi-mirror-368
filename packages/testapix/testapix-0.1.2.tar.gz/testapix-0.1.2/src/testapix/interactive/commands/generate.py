"""Test Generation Commands for Interactive Shell

Commands for generating test files from interactive session history.
"""

import json
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from testapix.interactive.shell import InteractiveShell


class GenerateCommands:
    """Test generation command handlers"""

    def __init__(self, shell: "InteractiveShell") -> None:
        self.shell = shell

    async def test(self, args: list[str]) -> None:
        """Generate test file from session history"""
        if not args:
            print("❌ Usage: generate test <test_type> [filename]")
            print("📋 Test types:")
            print("  • testapix     - Generate TestAPIX test file")
            print("  • functional - Generate TestAPIX functional tests")
            print("  • curl       - Generate curl commands")
            print("  • postman    - Generate Postman collection")
            print("💡 Example: generate test testapix my_api_tests.py")
            return

        test_type = args[0].lower()
        filename = args[1] if len(args) > 1 else None

        # Get session history
        history = self.shell.session_manager.get_request_history(100)
        if not history:
            print("❌ No requests in session history")
            print("💡 Make some API requests first to build up history")
            return

        # Generate based on type
        if test_type in ["testapix", "functional"]:
            await self._generate_testapix_tests(history, filename, test_type)
        elif test_type == "curl":
            await self._generate_curl_commands(history, filename)
        elif test_type == "postman":
            await self._generate_postman_collection(history, filename)
        else:
            print(f"❌ Unsupported test type: {test_type}")
            print("💡 Supported types: testapix, functional, curl, postman")

    async def _generate_testapix_tests(
        self, history: list[dict[str, Any]], filename: str | None, test_type: str
    ) -> None:
        """Generate TestAPIX test file"""
        if filename is None:
            filename = f"test_api_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"

        if not filename.endswith(".py"):
            filename += ".py"

        # Get base URL from session or first request
        base_url = self.shell.session_manager.current_session.get("base_url")
        if not base_url:
            base_url = "https://api.example.com"  # Default fallback

        # Generate TestAPIX code
        test_code = self._build_testapix_code(history, base_url, test_type)

        # Write to file
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(test_code)

            test_type_display = (
                "TestAPIX functional tests"
                if test_type == "functional"
                else "TestAPIX tests"
            )
            print(f"✅ **{test_type_display} generated**: {filename}")
            print(f"📊 Generated {len(history)} test cases")
            print(f"🚀 Run with: pytest {filename} -v")
            print()
            print("💡 Next steps:")
            print("  1. Review and customize the generated tests")
            print("  2. Add TestAPIX assertions for your specific use case")
            print("  3. Configure authentication and test data")
            print("  4. Run with: pytest -v --cov to see coverage")

        except Exception as e:
            print(f"❌ Failed to write test file: {e}")

    async def _generate_curl_commands(
        self, history: list[dict[str, Any]], filename: str | None
    ) -> None:
        """Generate curl commands"""
        if filename is None:
            filename = f"api_commands_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sh"

        if not filename.endswith(".sh"):
            filename += ".sh"

        base_url = self.shell.session_manager.current_session.get(
            "base_url", "https://api.example.com"
        )

        # Generate curl commands
        commands = self._build_curl_commands(history, base_url)

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(commands)

            print(f"✅ **Curl commands generated**: {filename}")
            print(f"📊 Generated {len(history)} curl commands")
            print(f"🚀 Run with: chmod +x {filename} && ./{filename}")

        except Exception as e:
            print(f"❌ Failed to write commands file: {e}")

    async def _generate_postman_collection(
        self, history: list[dict[str, Any]], filename: str | None
    ) -> None:
        """Generate Postman collection"""
        if filename is None:
            filename = f"api_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        if not filename.endswith(".json"):
            filename += ".json"

        base_url = self.shell.session_manager.current_session.get(
            "base_url", "https://api.example.com"
        )

        # Generate Postman collection
        collection = self._build_postman_collection(history, base_url)

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(collection, f, indent=2, ensure_ascii=False)

            print(f"✅ **Postman collection generated**: {filename}")
            print(f"📊 Generated collection with {len(history)} requests")
            print("📥 Import into Postman to use")

        except Exception as e:
            print(f"❌ Failed to write collection file: {e}")

    def _build_testapix_code(
        self, history: list[dict[str, Any]], base_url: str, test_type: str
    ) -> str:
        """Build TestAPIX test code from history"""
        lines = []

        # Header
        lines.extend(
            [
                '"""Generated API tests from TestAPIX interactive session"""',
                "",
                "import pytest",
                "from testapix import APIClient, assert_that",
                "from testapix.core.config import load_config",
                "",
                f'BASE_URL = "{base_url}"',
                "",
                "",
            ]
        )

        # Add fixtures
        if test_type == "functional":
            lines.extend(
                [
                    "@pytest.fixture",
                    "async def api_client():",
                    '    """Create configured API client for functional tests"""',
                    "    # TODO: Configure authentication if needed",
                    "    # from testapix.auth import BearerTokenAuth, APIKeyAuth",
                    "    # auth = BearerTokenAuth(token='your-token')",
                    "    # auth = APIKeyAuth(api_key='your-key', header_name='X-API-Key')",
                    "    ",
                    "    async with APIClient(base_url=BASE_URL) as client:",
                    "        yield client",
                    "",
                    "",
                    "class TestAPIFunctional:",
                    '    """Functional test cases generated from interactive session"""',
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "@pytest.fixture",
                    "async def api_client():",
                    '    """Create configured API client"""',
                    "    # TODO: Add authentication, configuration loading, etc.",
                    "    # config = load_config('./configs/base.yaml')",
                    "    async with APIClient(base_url=BASE_URL) as client:",
                    "        yield client",
                    "",
                    "",
                    "class TestAPISession:",
                    '    """Test cases generated from interactive session"""',
                    "",
                ]
            )

        # Generate test methods
        for i, request in enumerate(history, 1):
            method = request.get("method", "GET").upper()
            endpoint = request.get("endpoint", "/")
            kwargs = request.get("kwargs", {})
            response = request.get("response", {})

            # Create test method name
            test_name = f"test_{method.lower()}_{self._sanitize_endpoint_for_method_name(endpoint)}_{i}"

            lines.extend(
                [
                    f"    async def {test_name}(self, api_client):",
                    f'        """Test {method} {endpoint}"""',
                ]
            )

            # Build request parameters
            request_params = []
            param_lines = []

            if kwargs.get("params"):
                params_str = self._format_dict_for_code(kwargs["params"])
                param_lines.append(f"        params = {params_str}")
                request_params.append("params=params")

            if kwargs.get("headers"):
                headers_str = self._format_dict_for_code(kwargs["headers"])
                param_lines.append(f"        headers = {headers_str}")
                request_params.append("headers=headers")

            if kwargs.get("json"):
                json_str = self._format_json_for_code(kwargs["json"])
                param_lines.append(f"        json_data = {json_str}")
                request_params.append("json=json_data")

            # Add parameter setup
            lines.extend(param_lines)
            if param_lines:
                lines.append("")

            # Build request call
            params_str = ", ".join(request_params)
            if params_str:
                lines.append(
                    f'        response = await api_client.{method.lower()}("{endpoint}", {params_str})'
                )
            else:
                lines.append(
                    f'        response = await api_client.{method.lower()}("{endpoint}")'
                )

            lines.append("")

            # Add TestAPIX fluent assertions
            expected_status = response.get("status_code", 200)
            lines.append("        # TestAPIX fluent assertions")

            # Build assertion chain
            assertion_parts = [f"has_status({expected_status})"]

            # Add content type assertion if available
            if "content-type" in response.get("headers", {}):
                content_type = response["headers"]["content-type"]
                if "application/json" in content_type:
                    assertion_parts.append('has_header("content-type")')
                    assertion_parts.append("is_json()")

            # Chain assertions
            assertion_chain = " \\\n            .".join(assertion_parts)
            lines.append(f"        assert_that(response).{assertion_chain}")

            lines.extend(
                [
                    "",
                    "        # TODO: Add specific TestAPIX assertions for your use case",
                    "        # Examples:",
                    "        # .has_json_path('user.id')",
                    "        # .has_json_path_value('user.name', 'Expected Name')",
                    "        # .has_json_path_matching('user.email', r'^[\\w\\.-]+@[\\w\\.-]+\\.[a-zA-Z]{2,}$')",
                    "        # .has_response_time_under(1000)",
                    "",
                ]
            )

        # Add configuration and fixture suggestions
        lines.extend(
            [
                "",
                "# TODO: Configuration suggestions:",
                "# 1. Create configs/base.yaml with your API settings",
                "# 2. Add authentication configuration:",
                "#    auth:",
                "#      bearer_token: ${API_TOKEN}",
                "#      # OR",
                "#      api_key: ${API_KEY}",
                "#      api_key_header: X-API-Key",
                "# 3. Use load_config() in fixtures for environment-specific settings",
                "# 4. Add test data generators for complex scenarios",
                "",
            ]
        )

        return "\n".join(lines)

    def _build_curl_commands(self, history: list[dict[str, Any]], base_url: str) -> str:
        """Build curl commands from history"""
        lines = []

        # Header
        lines.extend(
            [
                "#!/bin/bash",
                "# Generated curl commands from TestAPIX interactive session",
                "",
                f'BASE_URL="{base_url}"',
                "",
                'echo "🚀 Executing curl commands from TestAPIX session..."',
                "echo",
                "",
            ]
        )

        # Generate curl commands
        for i, request in enumerate(history, 1):
            method = request.get("method", "GET").upper()
            endpoint = request.get("endpoint", "/")
            kwargs = request.get("kwargs", {})

            lines.extend(
                [
                    f"# Request {i}: {method} {endpoint}",
                    f'echo "📡 {method} {endpoint}"',
                ]
            )

            # Build curl command
            curl_parts = ["curl", "-X", method]

            # Add headers
            if kwargs.get("headers"):
                for key, value in kwargs["headers"].items():
                    curl_parts.extend(["-H", f'"{key}: {value}"'])

            # Add JSON data
            if kwargs.get("json"):
                json_str = json.dumps(kwargs["json"], separators=(",", ":"))
                curl_parts.extend(["-H", '"Content-Type: application/json"'])
                curl_parts.extend(["-d", f"'{json_str}'"])

            # Add query parameters to URL
            url = f'"$BASE_URL{endpoint}"'
            if kwargs.get("params"):
                param_parts = []
                for key, value in kwargs["params"].items():
                    param_parts.append(f"{key}={value}")
                if param_parts:
                    url = f'"$BASE_URL{endpoint}?{"&".join(param_parts)}"'

            curl_parts.append(url)

            # Build command line
            curl_command = " ".join(curl_parts)
            lines.extend(
                [
                    curl_command,
                    'echo "Status: $?"',
                    "echo",
                    "",
                ]
            )

        return "\n".join(lines)

    def _build_postman_collection(
        self, history: list[dict[str, Any]], base_url: str
    ) -> dict[str, Any]:
        """Build Postman collection from history"""
        collection = {
            "info": {
                "name": f"TestAPIX Session - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "description": "Generated from TestAPIX interactive session",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            },
            "item": [],
            "variable": [{"key": "base_url", "value": base_url, "type": "string"}],
        }

        # Generate request items
        for i, request in enumerate(history, 1):
            method = request.get("method", "GET").upper()
            endpoint = request.get("endpoint", "/")
            kwargs = request.get("kwargs", {})

            # Build Postman request item
            request_headers: list[dict[str, str]] = []
            url_path: list[str] = (
                endpoint.strip("/").split("/") if endpoint.strip("/") else []
            )

            item = {
                "name": f"{method} {endpoint}",
                "request": {
                    "method": method,
                    "header": request_headers,
                    "url": {
                        "raw": f"{{{{base_url}}}}{endpoint}",
                        "host": ["{{base_url}}"],
                        "path": url_path,
                    },
                },
            }

            # Add headers
            if kwargs.get("headers"):
                for key, value in kwargs["headers"].items():
                    request_headers.append({"key": key, "value": value, "type": "text"})

            # Add query parameters
            query_params: list[dict[str, str]] = []
            if kwargs.get("params"):
                for key, value in kwargs["params"].items():
                    query_params.append({"key": key, "value": str(value)})
                item["request"]["url"]["query"] = query_params  # type: ignore[index]

            # Add JSON body
            if kwargs.get("json"):
                item["request"]["body"] = {  # type: ignore[index]
                    "mode": "raw",
                    "raw": json.dumps(kwargs["json"], indent=2),
                    "options": {"raw": {"language": "json"}},
                }

            collection["item"].append(item)  # type: ignore[attr-defined]

        return collection

    def _sanitize_endpoint_for_method_name(self, endpoint: str) -> str:
        """Convert endpoint to valid Python method name"""
        # Remove leading slash and replace special chars
        name = endpoint.lstrip("/")
        name = name.replace("/", "_").replace("-", "_").replace(".", "_")

        # Remove non-alphanumeric characters
        name = "".join(c if c.isalnum() or c == "_" else "_" for c in name)

        # Ensure it doesn't start with a number
        if name and name[0].isdigit():
            name = "endpoint_" + name

        # Handle empty or invalid names
        if not name or name == "_":
            name = "endpoint"

        return name

    def _format_dict_for_code(self, data: dict[str, Any]) -> str:
        """Format dictionary for code generation"""
        if not data:
            return "{}"

        items = []
        for key, value in data.items():
            if isinstance(value, str):
                items.append(f'"{key}": "{value}"')
            else:
                items.append(f'"{key}": {repr(value)}')

        return "{" + ", ".join(items) + "}"

    def _format_json_for_code(self, data: Any) -> str:
        """Format JSON data for code generation"""
        return json.dumps(data, indent=None, separators=(",", ":"))
