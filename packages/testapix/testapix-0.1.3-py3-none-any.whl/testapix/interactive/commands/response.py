"""Response Inspection Commands for Interactive Shell

Commands for inspecting, extracting data from, and validating API responses.
"""

import json
import re
from typing import TYPE_CHECKING, Any

try:
    from rich.console import Console
    from rich.json import JSON
    from rich.syntax import Syntax

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

if TYPE_CHECKING:
    from testapix.interactive.shell import InteractiveShell


class ResponseCommands:
    """Response inspection command handlers"""

    def __init__(self, shell: "InteractiveShell") -> None:
        self.shell = shell
        self.console = Console() if RICH_AVAILABLE else None

    async def inspect(self, args: list[str]) -> None:
        """Inspect the last response in detail"""
        if not self.shell.last_response:
            print("❌ No response to inspect")
            print("💡 Make an API request first (e.g., 'get /endpoint')")
            return

        response = self.shell.last_response

        print("🔍 **Response Inspection**\n")

        # Basic response info
        print(
            f"📊 **Status**: {response.status_code} {getattr(response, 'reason_phrase', '')}"
        )
        print(f"🌐 **URL**: {response.url}")
        print(f"⚡ **Response Time**: {getattr(response, 'response_time', 0):.0f}ms")
        print()

        # Headers analysis
        print("📋 **Headers**:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        print()

        # Content analysis
        content_type = response.headers.get("content-type", "").lower()
        content_length = response.headers.get("content-length", "unknown")
        print(f"📄 **Content**: {content_type} ({content_length} bytes)")

        if "application/json" in content_type:
            try:
                json_data = response.json()
                print("✅ Valid JSON response")
                print(f"📊 JSON structure: {self._analyze_json_structure(json_data)}")
                print()

                # Show formatted JSON preview
                print("📝 **JSON Preview** (first 500 chars):")
                self._display_json(json_data, max_length=500)

            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON: {e}")
                print("📄 Raw content preview:")
                print(response.text[:500])
        else:
            print("📄 **Content Preview**:")
            content_preview = response.text[:500]
            if len(response.text) > 500:
                content_preview += "..."
            print(content_preview)

        print()
        print("💡 Use 'extract <path>' to extract specific values")
        print("💡 Use 'validate <schema>' to validate against a schema")

    def _display_json(self, data: Any, max_length: int = 2000) -> None:
        """Display JSON with syntax highlighting if rich is available"""
        json_str = json.dumps(data, indent=2, ensure_ascii=False)

        # Truncate if too long
        if len(json_str) > max_length:
            json_str = json_str[:max_length] + "..."
            truncated = True
        else:
            truncated = False

        if RICH_AVAILABLE and self.console:
            try:
                # Use rich for syntax highlighting
                if not truncated:
                    # Use rich JSON for complete JSON (better formatting)
                    json_renderable = JSON(json_str)
                    self.console.print(json_renderable)
                else:
                    # Use syntax highlighting for truncated JSON
                    syntax = Syntax(
                        json_str, "json", theme="monokai", line_numbers=False
                    )
                    self.console.print(syntax)
                return
            except Exception:
                # Fall back to plain text if rich fails
                pass

        # Fallback to plain text
        print(json_str)

    async def extract(self, args: list[str]) -> None:
        """Extract data from the last response using JSON path or regex"""
        if not self.shell.last_response:
            print("❌ No response to extract from")
            print("💡 Make an API request first")
            return

        if not args:
            print("❌ Usage: extract <path|pattern>")
            print("📋 Examples:")
            print("  extract user.name           - JSON path extraction")
            print("  extract users[0].email      - Array element extraction")
            print("  extract users[*].id         - All user IDs")
            print("  extract /regex/flags        - Regex pattern extraction")
            print("  extract --keys              - Show all available keys")
            return

        response = self.shell.last_response
        extract_pattern = args[0]

        # Special case: show available keys
        if extract_pattern == "--keys":
            await self._show_available_keys(response)
            return

        # Check if it's a regex pattern
        if extract_pattern.startswith("/") and "/" in extract_pattern[1:]:
            await self._extract_with_regex(response, extract_pattern)
        else:
            await self._extract_with_json_path(response, extract_pattern)

    async def validate(self, args: list[str]) -> None:
        """Validate the last response against a schema or rules"""
        if not self.shell.last_response:
            print("❌ No response to validate")
            print("💡 Make an API request first")
            return

        if not args:
            print("❌ Usage: validate <rule>")
            print("📋 Validation rules:")
            print("  validate status 200         - Check status code")
            print("  validate header content-type application/json")
            print("  validate json               - Check if valid JSON")
            print("  validate field user.name    - Check if field exists")
            print("  validate type user.age int  - Check field type")
            print("  validate count users 5      - Check array length")
            print("  validate range response_time 0 1000  - Check numeric range")
            return

        response = self.shell.last_response
        rule_type = args[0].lower()

        if rule_type == "status":
            await self._validate_status(response, args[1:])
        elif rule_type == "header":
            await self._validate_header(response, args[1:])
        elif rule_type == "json":
            await self._validate_json(response)
        elif rule_type == "field":
            await self._validate_field_exists(response, args[1:])
        elif rule_type == "type":
            await self._validate_field_type(response, args[1:])
        elif rule_type == "count":
            await self._validate_count(response, args[1:])
        elif rule_type == "range":
            await self._validate_range(response, args[1:])
        else:
            print(f"❌ Unknown validation rule: {rule_type}")
            print("💡 Use 'validate' without arguments to see available rules")

    def _analyze_json_structure(
        self, data: Any, max_depth: int = 3, current_depth: int = 0
    ) -> str:
        """Analyze JSON structure and return a description"""
        if current_depth >= max_depth:
            return "..."

        if isinstance(data, dict):
            if not data:
                return "empty object"
            key_count = len(data)
            sample_keys = list(data.keys())[:3]
            keys_preview = ", ".join(f'"{k}"' for k in sample_keys)
            if key_count > 3:
                keys_preview += f", ... ({key_count - 3} more)"
            return f"object with {key_count} keys [{keys_preview}]"
        elif isinstance(data, list):
            if not data:
                return "empty array"
            length = len(data)
            if length > 0:
                item_type = self._analyze_json_structure(
                    data[0], max_depth, current_depth + 1
                )
                return f"array of {length} items (first: {item_type})"
            return f"array of {length} items"
        elif isinstance(data, str):
            return f"string ({len(data)} chars)"
        elif isinstance(data, (int, float)):
            return f"number ({data})"
        elif isinstance(data, bool):
            return f"boolean ({data})"
        elif data is None:
            return "null"
        else:
            return f"unknown ({type(data).__name__})"

    async def _show_available_keys(self, response: Any) -> None:
        """Show all available keys in the JSON response"""
        try:
            json_data = response.json()
            keys = self._extract_all_paths(json_data)

            print("🔑 **Available JSON paths**:")
            for path in sorted(keys)[:20]:  # Show first 20 paths
                print(f"  {path}")

            if len(keys) > 20:
                print(f"  ... and {len(keys) - 20} more paths")

            print()
            print("💡 Use 'extract <path>' to extract specific values")

        except json.JSONDecodeError:
            print("❌ Response is not valid JSON")

    def _extract_all_paths(self, data: Any, prefix: str = "") -> list[str]:
        """Extract all possible JSON paths from data"""
        paths = []

        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{prefix}.{key}" if prefix else key
                paths.append(current_path)

                if (
                    isinstance(value, (dict, list)) and len(str(value)) < 1000
                ):  # Avoid deep recursion
                    paths.extend(self._extract_all_paths(value, current_path))

        elif isinstance(data, list) and data:
            # Show array access patterns
            if prefix:
                paths.append(f"{prefix}[0]")  # First element
                paths.append(f"{prefix}[*]")  # All elements

                # If first element is object, show its keys
                if isinstance(data[0], dict):
                    for key in data[0]:
                        paths.append(f"{prefix}[0].{key}")
                        paths.append(f"{prefix}[*].{key}")

        return paths

    async def _extract_with_json_path(self, response: Any, path: str) -> None:
        """Extract data using JSON path notation"""
        try:
            json_data = response.json()
            result = self._json_path_extract(json_data, path)

            if result is not None:
                print(f"✅ **Extracted from '{path}'**:")
                if isinstance(result, (dict, list)):
                    self._display_json(result, max_length=1000)
                else:
                    print(f"  {result}")
            else:
                print(f"❌ Path '{path}' not found in response")
                print("💡 Use 'extract --keys' to see available paths")

        except json.JSONDecodeError:
            print("❌ Response is not valid JSON")
        except Exception as e:
            print(f"❌ Extraction failed: {e}")

    async def _extract_with_regex(self, response: Any, pattern: str) -> None:
        """Extract data using regex pattern"""
        try:
            # Parse regex pattern like /pattern/flags
            parts = pattern.split("/")
            if len(parts) < 3:
                print("❌ Invalid regex format. Use /pattern/flags")
                return

            regex_pattern = "/".join(parts[1:-1])  # Handle patterns with / inside
            flags_str = parts[-1]

            # Convert flags
            flags = 0
            if "i" in flags_str:
                flags |= re.IGNORECASE
            if "m" in flags_str:
                flags |= re.MULTILINE
            if "s" in flags_str:
                flags |= re.DOTALL

            # Search in response text
            matches = re.findall(regex_pattern, response.text, flags)

            if matches:
                print(f"✅ **Found {len(matches)} match(es)**:")
                for i, match in enumerate(matches[:10], 1):  # Show first 10 matches
                    print(f"  {i}. {match}")

                if len(matches) > 10:
                    print(f"  ... and {len(matches) - 10} more matches")
            else:
                print(f"❌ No matches found for pattern: {regex_pattern}")

        except re.error as e:
            print(f"❌ Invalid regex pattern: {e}")
        except Exception as e:
            print(f"❌ Regex extraction failed: {e}")

    def _json_path_extract(self, data: Any, path: str) -> Any:
        """Extract value from JSON data using dot notation and array indexing"""
        try:
            parts = self._parse_json_path(path)
            current = data

            for part in parts:
                if part.startswith("[") and part.endswith("]"):
                    # Array access
                    index_str = part[1:-1]
                    if index_str == "*":
                        # Extract all elements
                        if isinstance(current, list):
                            return current
                        else:
                            return None
                    else:
                        index = int(index_str)
                        if isinstance(current, list) and 0 <= index < len(current):
                            current = current[index]
                        else:
                            return None
                else:
                    # Object key access
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        return None

            return current

        except (ValueError, KeyError, IndexError):
            return None

    def _parse_json_path(self, path: str) -> list[str]:
        """Parse JSON path into components"""
        # Handle array notation like users[0].name
        parts = []
        current_part = ""
        in_brackets = False

        for char in path:
            if char == "[":
                if current_part:
                    parts.append(current_part)
                    current_part = ""
                current_part = "["
                in_brackets = True
            elif char == "]":
                current_part += "]"
                parts.append(current_part)
                current_part = ""
                in_brackets = False
            elif char == "." and not in_brackets:
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            else:
                current_part += char

        if current_part:
            parts.append(current_part)

        return parts

    async def _validate_status(self, response: Any, args: list[str]) -> None:
        """Validate response status code"""
        if not args:
            print("❌ Usage: validate status <expected_code>")
            return

        try:
            expected = int(args[0])
            actual = response.status_code

            if actual == expected:
                print(f"✅ Status code validation passed: {actual}")
            else:
                print(
                    f"❌ Status code validation failed: expected {expected}, got {actual}"
                )

        except ValueError:
            print("❌ Invalid status code format")

    async def _validate_header(self, response: Any, args: list[str]) -> None:
        """Validate response header"""
        if len(args) < 2:
            print("❌ Usage: validate header <header_name> <expected_value>")
            return

        header_name = args[0].lower()
        expected_value = args[1]
        actual_value = response.headers.get(header_name)

        if actual_value:
            if expected_value.lower() in actual_value.lower():
                print(
                    f"✅ Header validation passed: {header_name} contains '{expected_value}'"
                )
            else:
                print(
                    f"❌ Header validation failed: {header_name} is '{actual_value}', expected to contain '{expected_value}'"
                )
        else:
            print(f"❌ Header validation failed: {header_name} not found in response")

    async def _validate_json(self, response: Any) -> None:
        """Validate that response is valid JSON"""
        try:
            response.json()
            print("✅ JSON validation passed: Response is valid JSON")
        except json.JSONDecodeError as e:
            print(f"❌ JSON validation failed: {e}")

    async def _validate_field_exists(self, response: Any, args: list[str]) -> None:
        """Validate that a field exists in the response"""
        if not args:
            print("❌ Usage: validate field <field_path>")
            return

        field_path = args[0]

        try:
            json_data = response.json()
            value = self._json_path_extract(json_data, field_path)

            if value is not None:
                print(
                    f"✅ Field validation passed: '{field_path}' exists with value: {value}"
                )
            else:
                print(f"❌ Field validation failed: '{field_path}' not found")

        except json.JSONDecodeError:
            print("❌ Field validation failed: Response is not valid JSON")

    async def _validate_field_type(self, response: Any, args: list[str]) -> None:
        """Validate field type"""
        if len(args) < 2:
            print("❌ Usage: validate type <field_path> <expected_type>")
            print("💡 Types: str, int, float, bool, list, dict, null")
            return

        field_path = args[0]
        expected_type = args[1].lower()

        type_mapping = {
            "str": str,
            "string": str,
            "int": int,
            "integer": int,
            "float": float,
            "number": float,
            "bool": bool,
            "boolean": bool,
            "list": list,
            "array": list,
            "dict": dict,
            "object": dict,
            "null": type(None),
            "none": type(None),
        }

        if expected_type not in type_mapping:
            print(f"❌ Unknown type: {expected_type}")
            return

        try:
            json_data = response.json()
            value = self._json_path_extract(json_data, field_path)

            if value is None:
                print(f"❌ Type validation failed: '{field_path}' not found")
                return

            expected_python_type = type_mapping[expected_type]
            actual_type = type(value)

            if isinstance(value, expected_python_type):
                print(
                    f"✅ Type validation passed: '{field_path}' is {actual_type.__name__}"
                )
            else:
                print(
                    f"❌ Type validation failed: '{field_path}' is {actual_type.__name__}, expected {expected_type}"
                )

        except json.JSONDecodeError:
            print("❌ Type validation failed: Response is not valid JSON")

    async def _validate_count(self, response: Any, args: list[str]) -> None:
        """Validate array length"""
        if len(args) < 2:
            print("❌ Usage: validate count <field_path> <expected_count>")
            return

        field_path = args[0]

        try:
            expected_count = int(args[1])
            json_data = response.json()
            value = self._json_path_extract(json_data, field_path)

            if value is None:
                print(f"❌ Count validation failed: '{field_path}' not found")
                return

            if isinstance(value, (list, dict, str)):
                actual_count = len(value)
                if actual_count == expected_count:
                    print(
                        f"✅ Count validation passed: '{field_path}' has {actual_count} items"
                    )
                else:
                    print(
                        f"❌ Count validation failed: '{field_path}' has {actual_count} items, expected {expected_count}"
                    )
            else:
                print(
                    f"❌ Count validation failed: '{field_path}' is not countable (type: {type(value).__name__})"
                )

        except ValueError:
            print("❌ Invalid count format")
        except json.JSONDecodeError:
            print("❌ Count validation failed: Response is not valid JSON")

    async def _validate_range(self, response: Any, args: list[str]) -> None:
        """Validate numeric range"""
        if len(args) < 2:
            print("❌ Usage: validate range <field_path> <min> [max]")
            print("💡 For response time: validate range response_time 0 1000")
            return

        field_path = args[0]

        try:
            min_val = float(args[1])
            max_val = float(args[2]) if len(args) > 2 else float("inf")

            if field_path == "response_time":
                # Special case for response time
                actual_value = getattr(response, "response_time", 0)
            else:
                json_data = response.json()
                actual_value = self._json_path_extract(json_data, field_path)

            if actual_value is None:
                print(f"❌ Range validation failed: '{field_path}' not found")
                return

            if not isinstance(actual_value, (int, float)):
                print(
                    f"❌ Range validation failed: '{field_path}' is not numeric (type: {type(actual_value).__name__})"
                )
                return

            actual_value = float(actual_value)

            if min_val <= actual_value <= max_val:
                if max_val == float("inf"):
                    print(
                        f"✅ Range validation passed: '{field_path}' ({actual_value}) >= {min_val}"
                    )
                else:
                    print(
                        f"✅ Range validation passed: '{field_path}' ({actual_value}) is in range [{min_val}, {max_val}]"
                    )
            else:
                if max_val == float("inf"):
                    print(
                        f"❌ Range validation failed: '{field_path}' ({actual_value}) < {min_val}"
                    )
                else:
                    print(
                        f"❌ Range validation failed: '{field_path}' ({actual_value}) not in range [{min_val}, {max_val}]"
                    )

        except ValueError:
            print("❌ Invalid numeric range format")
        except json.JSONDecodeError:
            print("❌ Range validation failed: Response is not valid JSON")
