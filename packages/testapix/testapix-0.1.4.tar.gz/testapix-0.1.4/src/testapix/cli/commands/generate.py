"""Test Generation Command

This module generates comprehensive test files that demonstrate TestAPIX best
practices while providing immediately useful tests. The generated tests are
designed to:

1. Work out of the box with minimal customization
2. Teach testing patterns through working examples
3. Cover common scenarios (success, failure, edge cases)
4. Include helpful comments explaining the why, not just the what
5. Demonstrate proper test organization and cleanup

The generation process uses templates that can be customized based on the
API type, endpoints, and testing requirements.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import DictLoader, Environment, select_autoescape
from rich.console import Console
from rich.syntax import Syntax

from testapix.core.config import TestAPIXConfig
from testapix.core.exceptions import TestAPIXError

console = Console()


# Template cache to avoid recreating templates
_template_cache: dict[str, str] = {}


def generate_tests(
    test_type: str,
    api_name: str,
    output_dir: Path | None = None,
    endpoints: list[str] | None = None,
    schema_file: Path | None = None,
    include_examples: bool = True,
    config: TestAPIXConfig | None = None,
    verbose: bool = False,
) -> bool:
    """Generate comprehensive test files for an API.

    This function creates test files that are both educational and practical.
    Each generated test includes:
    - Working test code for common scenarios
    - Comments explaining testing patterns
    - Proper error handling and assertions
    - Test data generation examples
    - Cleanup patterns

    Args:
    ----
        test_type: Type of tests to generate (functional, contract, security, performance)
        api_name: Name of the API being tested
        output_dir: Output directory for test files
        endpoints: List of API endpoints to test
        schema_file: Schema file for contract testing
        include_examples: Whether to include example tests
        config: TestAPIX configuration (if available)
        verbose: Enable verbose output

    Returns:
    -------
        True if successful

    Raises:
    ------
        TestAPIXError: If generation fails

    """
    # Normalize and validate inputs
    test_type = test_type.lower()
    python_name = _normalize_python_name(api_name)

    # Determine output directory
    if output_dir is None:
        if config:
            # Inside a TestAPIX project
            output_dir = Path.cwd() / "tests" / test_type
        else:
            # Standalone generation
            output_dir = Path.cwd() / "tests"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate default endpoints if not provided
    if not endpoints:
        endpoints = _generate_default_endpoints(api_name)
        if verbose:
            console.print(f"Using default endpoints: {', '.join(endpoints)}")

    # Create generation context
    context = _create_generation_context(
        api_name=api_name,
        python_name=python_name,
        test_type=test_type,
        endpoints=endpoints,
        schema_file=schema_file,
        include_examples=include_examples,
        config=config,
    )

    # Generate based on test type
    if test_type == "functional":
        success = _generate_functional_tests(output_dir, context, verbose)
    elif test_type == "contract":
        success = _generate_contract_tests(output_dir, context, schema_file, verbose)
    elif test_type == "security":
        success = _generate_security_tests(output_dir, context, verbose)
    elif test_type == "performance":
        success = _generate_performance_tests(output_dir, context, verbose)
    else:
        raise TestAPIXError(f"Unknown test type: {test_type}")

    if success and verbose:
        # Show a preview of the generated test
        test_file = output_dir / f"test_{python_name}_{test_type}.py"
        if test_file.exists():
            _show_test_preview(test_file)

    return success


def _normalize_python_name(name: str) -> str:
    """Convert API name to valid Python identifier.

    Examples
    --------
        "user-api" -> "user_api"
        "User API" -> "user_api"
        "123-api" -> "api_123"

    """
    # Replace non-alphanumeric with underscores
    python_name = re.sub(r"[^\w]+", "_", name.lower())

    # Remove leading/trailing underscores
    python_name = python_name.strip("_")

    # Ensure it doesn't start with a number
    if python_name and python_name[0].isdigit():
        python_name = f"api_{python_name}"

    return python_name or "api"


def _generate_default_endpoints(api_name: str) -> list[str]:
    """Generate sensible default endpoints based on API name.

    This helps users get started quickly even if they don't specify endpoints.
    """
    # Extract resource name from API name
    resource = api_name.lower()
    resource = resource.replace("-api", "").replace("_api", "").replace(" api", "")

    # Simple pluralization
    if resource.endswith("y"):
        plural = resource[:-1] + "ies"
    elif resource.endswith("s"):
        plural = resource
    else:
        plural = resource + "s"

    # Common RESTful endpoints
    return [
        f"/{plural}",  # GET list
        f"/{plural}/{{id}}",  # GET/PUT/DELETE single
        f"/{resource}",  # POST create
        f"/{plural}/search",  # Search endpoint
    ]


def _create_generation_context(
    api_name: str,
    python_name: str,
    test_type: str,
    endpoints: list[str],
    schema_file: Path | None,
    include_examples: bool,
    config: TestAPIXConfig | None,
) -> dict[str, Any]:
    """Create context dictionary for template rendering."""
    context = {
        "api_name": api_name,
        "python_name": python_name,
        "test_type": test_type,
        "endpoints": endpoints,
        "schema_file": schema_file,
        "include_examples": include_examples,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "has_auth": bool(config and config.auth),
        "auth_type": config.auth.type if config and config.auth else None,
        "base_url": config.http.base_url if config else "https://api.example.com",
        # Helper functions for templates
        "extract_resource": _extract_resource_from_endpoint,
        "method_for_endpoint": _guess_http_method,
        "generate_test_name": _generate_test_name,
    }

    return context


def _extract_resource_from_endpoint(endpoint: str) -> str:
    """Extract resource name from endpoint path."""
    # Remove leading slash and parameters
    clean_path = endpoint.lstrip("/").split("?")[0]

    # Extract first path segment
    parts = clean_path.split("/")
    if parts:
        return parts[0].rstrip("s")  # Simple de-pluralization

    return "resource"


def _guess_http_method(endpoint: str) -> str:
    """Guess appropriate HTTP method based on endpoint pattern."""
    if "{id}" in endpoint or endpoint.endswith("/search"):
        return "GET"
    elif endpoint.count("/") == 1:
        return "POST"  # Probably a creation endpoint
    else:
        return "GET"  # Default to GET


def _generate_test_name(endpoint: str, scenario: str = "success") -> str:
    """Generate descriptive test method name from endpoint."""
    # Clean endpoint
    clean = endpoint.lstrip("/").replace("/", "_").replace("{", "").replace("}", "")
    clean = re.sub(r"[^\w]+", "_", clean).strip("_")

    return f"test_{clean}_{scenario}"


def _generate_functional_tests(
    output_dir: Path, context: dict[str, Any], verbose: bool
) -> bool:
    """Generate comprehensive functional tests."""
    template = '''"""
Functional Tests for {{ api_name }}

Generated by TestAPIX on {{ timestamp }}

This test suite provides comprehensive functional testing for the {{ api_name }} API.
Functional tests verify that the API behaves correctly from a user's perspective,
focusing on:

- Correct response data and status codes
- Proper error handling
- Business logic validation
- Integration between API components

The tests demonstrate TestAPIX best practices including:
- Async test execution for better performance
- Realistic test data generation
- Comprehensive assertions
- Proper test isolation and cleanup
"""

import pytest
from typing import Dict, Any, List
import asyncio

from testapix import APIClient, assert_that
from testapix.core.exceptions import RequestError, ResponseValidationError


class Test{{ python_name.title() }}Functional:
    """Functional tests for {{ api_name }}."""

    @pytest.fixture(autouse=True)
    def setup(self, api_client: APIClient, data_generator):
        """
        Set up test dependencies.

        This fixture automatically runs before each test, providing access
        to the authenticated API client and test data generator.
        """
        self.client = api_client
        self.generator = data_generator
        self.created_resources = []  # Track resources for cleanup

    {% for endpoint in endpoints %}
    {% set resource = extract_resource(endpoint) %}
    {% set method = method_for_endpoint(endpoint) %}

    async def {{ generate_test_name(endpoint, "success") }}(self):
        """Test successful {{ method }} request to {{ endpoint }}."""
        {% if method == "POST" %}
        # Generate realistic test data
        test_data = {
            "name": self.generator.fake.name(),
            "description": self.generator.fake.text(max_nb_chars=200),
            "email": self.generator.fake.email(),
            # Add more fields based on your API requirements
        }

        response = await self.client.post("{{ endpoint }}", json=test_data)

        # Verify successful creation
        assert_that(response) \\
            .has_status(201) \\
            .has_json_path("id") \\
            .has_json_path("name", test_data["name"])

        # Track for cleanup
        resource_id = response.json_path("id")
        self.created_resources.append(("{{ resource }}", resource_id))

        {% elif method == "GET" and "{id}" in endpoint %}
        # First create a resource to retrieve
        create_data = {"name": f"Test {{ resource.title() }}"}
        create_response = await self.client.post("/{{ resource }}", json=create_data)
        resource_id = create_response.json_path("id")
        self.created_resources.append(("{{ resource }}", resource_id))

        # Now test retrieval
        response = await self.client.get("{{ endpoint.replace('{id}', '') }}{resource_id}")

        assert_that(response) \\
            .has_status(200) \\
            .has_json_path("id", resource_id) \\
            .has_json_path("name")

        {% else %}
        # Test GET request
        response = await self.client.get("{{ endpoint }}")

        assert_that(response) \\
            .has_status(200) \\
            .has_json_path("data") \\
            .response_time_less_than(2.0)

        # Verify response structure
        data = response.json_path("data")
        assert isinstance(data, (list, dict)), "Response data should be list or dict"
        {% endif %}

    async def {{ generate_test_name(endpoint, "not_found") }}(self):
        """Test {{ method }} request to {{ endpoint }} with non-existent resource."""
        {% if "{id}" in endpoint %}
        response = await self.client.{{ method.lower() }}("{{ endpoint.replace('{id}', '99999') }}")

        assert_that(response) \\
            .has_status(404) \\
            .has_error_message_containing("not found")
        {% else %}
        # This test may not apply to all endpoints
        pytest.skip("Not applicable for this endpoint")
        {% endif %}

    {% if include_examples %}
    async def {{ generate_test_name(endpoint, "validation_error") }}(self):
        """Test {{ method }} request to {{ endpoint }} with invalid data."""
        {% if method == "POST" %}
        invalid_data = {
            "name": "",  # Empty required field
            "email": "not-an-email",  # Invalid format
            # Add more validation test cases
        }

        response = await self.client.post("{{ endpoint }}", json=invalid_data)

        assert_that(response) \\
            .has_status(400) \\
            .has_error_message_containing("validation")
        {% else %}
        pytest.skip("Validation test not applicable for {{ method }} requests")
        {% endif %}
    {% endif %}
    {% endfor %}

    {% if has_auth %}
    async def test_authentication_required(self, unauthenticated_client: APIClient):
        """Test that endpoints require authentication."""
        # Test a few endpoints without auth
        test_endpoints = [
            {% for endpoint in endpoints[:3] %}
            "{{ endpoint }}",
            {% endfor %}
        ]

        for endpoint in test_endpoints:
            response = await unauthenticated_client.get(endpoint.replace("{id}", "1"))

            assert_that(response) \\
                .has_status(401) \\
                .has_error_message_containing("unauthorized")
    {% endif %}

    {% if include_examples %}
    @pytest.mark.parametrize("page_size", [10, 50, 100])
    async def test_pagination(self, page_size: int):
        """Test pagination functionality across different page sizes."""
        # Test list endpoint with pagination
        response = await self.client.get("{{ endpoints[0] }}", params={
            "page": 1,
            "per_page": page_size
        })

        assert_that(response).has_status(200)

        # Verify pagination metadata
        if response.has_json_path("pagination"):
            assert_that(response) \\
                .has_json_path("pagination.page", 1) \\
                .has_json_path("pagination.per_page", page_size)

            # Verify data count matches requested size (or less for last page)
            data = response.json_path("data", [])
            assert len(data) <= page_size

    async def test_concurrent_operations(self):
        """Test API behavior under concurrent requests."""
        # Create multiple resources concurrently
        tasks = []
        for i in range(5):
            data = {"name": f"Concurrent Test {i}"}
            task = self.client.post("{{ endpoints[2] if len(endpoints) > 2 else endpoints[0] }}", json=data)
            tasks.append(task)

        # Execute concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify most succeeded (allowing for some rate limiting)
        successful = [r for r in responses if not isinstance(r, Exception) and r.status_code < 400]
        assert len(successful) >= 3, "At least 3 concurrent requests should succeed"

        # Cleanup
        for response in successful:
            if hasattr(response, 'json_path'):
                resource_id = response.json_path("id")
                if resource_id:
                    self.created_resources.append(("resource", resource_id))

    async def test_error_handling(self):
        """Test various error scenarios and API error handling."""
        error_scenarios = [
            # (request_kwargs, expected_status, expected_error)
            ({"json": None}, 400, "invalid"),  # Null body
            ({"json": "not-json"}, 400, "invalid"),  # Invalid JSON type
            ({"headers": {"Content-Type": "text/plain"}}, 415, "unsupported"),  # Wrong content type
        ]

        for kwargs, expected_status, expected_error in error_scenarios:
            response = await self.client.post("{{ endpoints[2] if len(endpoints) > 2 else endpoints[0] }}", **kwargs)

            # API should handle errors gracefully
            assert response.status_code >= 400, f"Expected error for {kwargs}"
            assert response.status_code < 500, f"Got server error for {kwargs}: {response.status_code}"
    {% endif %}

    @pytest.fixture(autouse=True)
    async def cleanup(self):
        """Clean up created resources after each test."""
        yield  # Test runs here

        # Cleanup in reverse order
        for resource_type, resource_id in reversed(self.created_resources):
            try:
                # Adjust cleanup based on your API structure
                await self.client.delete(f"/{resource_type}s/{resource_id}")
            except Exception:
                # Don't fail test if cleanup fails
                pass


{% if include_examples %}
class Test{{ python_name.title() }}EdgeCases:
    """Edge case tests for {{ api_name }}."""

    @pytest.fixture(autouse=True)
    def setup(self, api_client: APIClient, data_generator):
        self.client = api_client
        self.generator = data_generator

    async def test_special_characters_handling(self):
        """Test API handling of special characters in data."""
        special_data = {
            "name": "Test™ with émojis 🚀 and symbols @#$%",
            "description": "Line1\\nLine2\\tTabbed\\r\\nWindows",
            "unicode": "你好世界 مرحبا بالعالم",
        }

        response = await self.client.post("{{ endpoints[2] if len(endpoints) > 2 else endpoints[0] }}", json=special_data)

        if response.status_code < 400:
            # If accepted, verify data is preserved correctly
            for key, value in special_data.items():
                if response.has_json_path(key):
                    assert response.json_path(key) == value

            # Cleanup
            resource_id = response.json_path("id")
            if resource_id:
                await self.client.delete(f"/{self.extract_resource('{{ endpoints[0] }}')}s/{resource_id}")

    async def test_boundary_values(self):
        """Test API handling of boundary values."""
        boundary_data = {
            "count": 2147483647,  # Max 32-bit integer
            "price": 999999999.99,  # Large decimal
            "percentage": 100.0,
            "minimum": 0,
            "name": "x" * 255,  # Max length string (adjust based on API)
        }

        response = await self.client.post("{{ endpoints[2] if len(endpoints) > 2 else endpoints[0] }}", json=boundary_data)

        # API should either accept or reject with proper validation error
        assert response.status_code in [201, 400], f"Unexpected status: {response.status_code}"

        if response.status_code == 400:
            assert_that(response).has_error_message_containing("validation")
{% endif %}


# Helper function for resource extraction
def extract_resource(endpoint: str) -> str:
    """Extract resource name from endpoint."""
    return endpoint.lstrip('/').split('/')[0].rstrip('s')
'''

    # Render template
    env = Environment(
        loader=DictLoader({"functional": template}),
        autoescape=select_autoescape(["html", "xml"]),
    )
    # Add built-in Python functions to the environment
    env.globals.update(
        len=len,
        str=str,
        int=int,
        float=float,
        bool=bool,
        range=range,
        enumerate=enumerate,
    )
    rendered = env.get_template("functional").render(**context)

    # Write test file
    test_file = output_dir / f"test_{context['python_name']}_functional.py"
    test_file.write_text(rendered, encoding="utf-8")

    if verbose:
        console.print(f"[OK] Generated functional tests: {test_file}")

    return True


def _generate_security_tests(
    output_dir: Path, context: dict[str, Any], verbose: bool
) -> bool:
    """Generate security-focused tests."""
    template = '''"""
Security Tests for {{ api_name }}

Generated by TestAPIX on {{ timestamp }}

This test suite focuses on API security testing, including:
- Authentication and authorization verification
- Input validation and injection prevention
- Security headers validation
- Rate limiting and abuse prevention
- Data exposure and information leakage

[WARN] WARNING: These tests generate potentially malicious payloads.
   Only run against APIs you own and have permission to test.
   Never run security tests against production APIs without approval.
"""

import pytest
from typing import List, Dict, Any
import asyncio
import time

from testapix import APIClient, assert_that
from testapix.core.exceptions import RequestError


class Test{{ python_name.title() }}SecurityAuth:
    """Authentication and authorization security tests."""

    {% if has_auth %}
    async def test_missing_authentication(self, unauthenticated_client: APIClient):
        """Test that API properly rejects unauthenticated requests."""
        protected_endpoints = [
            {% for endpoint in endpoints %}
            "{{ endpoint }}",
            {% endfor %}
        ]

        for endpoint in protected_endpoints:
            # Replace path parameters with test values
            test_endpoint = endpoint.replace("{id}", "1")

            response = await unauthenticated_client.get(test_endpoint)

            assert_that(response) \\
                .has_status(401) \\
                .has_header("www-authenticate")  # Should indicate auth method

    async def test_invalid_authentication_tokens(self, api_client: APIClient):
        """Test various invalid authentication attempts."""
        invalid_auth_headers = [
            ("Authorization", "Bearer "),  # Empty token
            ("Authorization", "Bearer null"),  # Null token
            ("Authorization", "Bearer undefined"),  # JS undefined
            ("Authorization", "Bearer <script>alert('xss')</script>"),  # XSS attempt
            ("Authorization", "Basic YWRtaW46YWRtaW4="),  # Wrong auth type
            ("X-API-Key", ""),  # Empty API key
            ("X-API-Key", "' OR '1'='1"),  # SQL injection in API key
        ]

        for header_name, header_value in invalid_auth_headers:
            headers = {header_name: header_value}
            response = await api_client.get("{{ endpoints[0] }}", headers=headers)

            # Should reject invalid auth
            assert response.status_code in [401, 403], \\
                f"Failed to reject invalid auth: {header_name}: {header_value}"
    {% endif %}

    async def test_authorization_boundaries(self, api_client: APIClient):
        """Test authorization boundaries and access control."""
        # This test would need to be customized based on your API's auth model
        # Example: User A shouldn't access User B's resources

        # Create a resource
        response = await api_client.post("{{ endpoints[2] if len(endpoints) > 2 else endpoints[0] }}", json={
            "name": "Private Resource",
            "visibility": "private"
        })

        if response.status_code == 201:
            resource_id = response.json_path("id")

            # In a real test, you'd switch to a different user here
            # and verify they can't access this resource

            # Cleanup
            await api_client.delete(f"/{extract_resource('{{ endpoints[0] }}')}s/{resource_id}")


class Test{{ python_name.title() }}SecurityInjection:
    """Input validation and injection prevention tests."""

    @pytest.fixture(autouse=True)
    def setup(self, api_client: APIClient):
        self.client = api_client
        self.payloads = self._get_injection_payloads()

    def _get_injection_payloads(self) -> Dict[str, List[str]]:
        """Get various injection test payloads."""
        return {
            "sql_injection": [
                "'; DROP TABLE users; --",
                "1' OR '1'='1",
                "admin'--",
                "1; SELECT * FROM users WHERE 't' = 't",
                "' UNION SELECT NULL, NULL, NULL--",
            ],
            "xss": [
                "<script>alert('XSS')</script>",
                "javascript:alert('XSS')",
                "<img src=x onerror=alert('XSS')>",
                "<svg onload=alert('XSS')>",
                "';alert(String.fromCharCode(88,83,83))//",
            ],
            "command_injection": [
                "; cat /etc/passwd",
                "| ls -la",
                "&& whoami",
                "`id`",
                "$(cat /etc/passwd)",
            ],
            "path_traversal": [
                "../../../etc/passwd",
                "..\\\\..\\\\..\\\\windows\\\\system32\\\\config\\\\sam",
                "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
                "....//....//....//etc/passwd",
            ],
            "ldap_injection": [
                "*)(uid=*))(|(uid=*",
                "admin)(&(password=*))",
                "*)(mail=*))",
            ],
            "xml_injection": [
                "<?xml version=\\"1.0\\"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM \\"file:///etc/passwd\\">]><foo>&xxe;</foo>",
                "<![CDATA[<script>alert('XSS')</script>]]>",
            ],
        }

    @pytest.mark.security
    async def test_sql_injection_prevention(self):
        """Test that API prevents SQL injection attacks."""
        for payload in self.payloads["sql_injection"]:
            # Test in various fields
            test_data = {
                "name": payload,
                "search": payload,
                "filter": f"status={payload}",
            }

            response = await self.client.post("{{ endpoints[2] if len(endpoints) > 2 else endpoints[0] }}", json=test_data)

            # Should either reject or safely handle
            if response.status_code < 400:
                # If accepted, verify no SQL error exposed
                response_text = response.text.lower()
                sql_error_indicators = ["sql", "syntax", "mysql", "postgresql", "sqlite", "oracle"]

                for indicator in sql_error_indicators:
                    assert indicator not in response_text, \\
                        f"Possible SQL error exposed with payload: {payload}"

                # Cleanup if created
                if response.status_code == 201:
                    resource_id = response.json_path("id")
                    if resource_id:
                        await self.client.delete(f"/{extract_resource('{{ endpoints[0] }}')}s/{resource_id}")

    @pytest.mark.security
    async def test_xss_prevention(self):
        """Test that API prevents XSS attacks."""
        for payload in self.payloads["xss"]:
            test_data = {
                "name": payload,
                "description": payload,
                "comment": payload,
            }

            response = await self.client.post("{{ endpoints[2] if len(endpoints) > 2 else endpoints[0] }}", json=test_data)

            if response.status_code < 400:
                # If accepted, verify payload is properly escaped/sanitized
                for field in ["name", "description", "comment"]:
                    if response.has_json_path(field):
                        value = response.json_path(field)

                        # Check that dangerous patterns are escaped
                        assert "<script>" not in value, f"Unescaped script tag in {field}"
                        assert "javascript:" not in value, f"Unescaped javascript: in {field}"

                # Cleanup
                if response.status_code == 201:
                    resource_id = response.json_path("id")
                    if resource_id:
                        await self.client.delete(f"/{extract_resource('{{ endpoints[0] }}')}s/{resource_id}")

    @pytest.mark.security
    async def test_command_injection_prevention(self):
        """Test that API prevents command injection attacks."""
        for payload in self.payloads["command_injection"]:
            # Test in fields that might interact with system commands
            test_data = {
                "filename": payload,
                "command": payload,
                "action": payload,
            }

            response = await self.client.post("{{ endpoints[2] if len(endpoints) > 2 else endpoints[0] }}", json=test_data)

            # Should reject or safely handle
            assert response.status_code != 500, \\
                f"Server error with command injection payload: {payload}"


class Test{{ python_name.title() }}SecurityHeaders:
    """Security headers and HTTP security tests."""

    async def test_security_headers_present(self, api_client: APIClient):
        """Test that appropriate security headers are present."""
        response = await api_client.get("{{ endpoints[0] }}")

        # Check for important security headers
        security_headers = {
            "x-content-type-options": "nosniff",
            "x-frame-options": ["deny", "sameorigin"],
            "x-xss-protection": "1; mode=block",
            "strict-transport-security": None,  # Should be present for HTTPS
            "content-security-policy": None,  # Should have some CSP
        }

        missing_headers = []

        for header, expected_values in security_headers.items():
            if header not in response.headers:
                missing_headers.append(header)
            elif expected_values:
                actual_value = response.headers[header].lower()
                if isinstance(expected_values, list):
                    assert any(val in actual_value for val in expected_values), \\
                        f"{header} has unexpected value: {actual_value}"
                else:
                    assert actual_value == expected_values, \\
                        f"{header} has unexpected value: {actual_value}"

        # Warn about missing headers (don't fail test)
        if missing_headers:
            pytest.skip(f"Missing security headers: {', '.join(missing_headers)}")

    async def test_cors_configuration(self, api_client: APIClient):
        """Test CORS configuration for security."""
        # Send OPTIONS request
        response = await api_client.options("{{ endpoints[0] }}")

        if "access-control-allow-origin" in response.headers:
            origin = response.headers["access-control-allow-origin"]

            # Check for overly permissive CORS
            assert origin != "*", "CORS allows all origins - potential security risk"

            # If credentials are allowed, origin must be specific
            if response.headers.get("access-control-allow-credentials") == "true":
                assert origin != "*", "CORS allows credentials with wildcard origin!"

    async def test_http_methods_restrictions(self, api_client: APIClient):
        """Test that only appropriate HTTP methods are allowed."""
        # Methods that should typically be disabled
        dangerous_methods = ["TRACE", "TRACK", "CONNECT"]

        for method in dangerous_methods:
            response = await api_client.request(method, "{{ endpoints[0] }}")

            # Should be rejected
            assert response.status_code in [405, 501], \\
                f"Dangerous method {method} not properly restricted"


class Test{{ python_name.title() }}SecurityRateLimiting:
    """Rate limiting and abuse prevention tests."""

    @pytest.mark.security
    @pytest.mark.slow
    async def test_rate_limiting_enforcement(self, api_client: APIClient):
        """Test that rate limiting is properly enforced."""
        # Send many requests quickly
        request_count = 50
        start_time = time.time()

        tasks = []
        for i in range(request_count):
            task = api_client.get("{{ endpoints[0] }}")
            tasks.append(task)

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Count rate limited responses
        rate_limited = sum(1 for r in responses
                          if hasattr(r, 'status_code') and r.status_code == 429)

        elapsed_time = time.time() - start_time

        if rate_limited > 0:
            console.print(f"✓ Rate limiting active: {rate_limited}/{request_count} requests limited", style="green")
        else:
            console.print(f"[WARN] No rate limiting detected in {elapsed_time:.1f}s", style="yellow")
            pytest.skip("Rate limiting not detected - consider implementing")

    async def test_request_size_limits(self, api_client: APIClient):
        """Test request size limitations."""
        # Generate large payloads
        size_tests = [
            (1024, "1KB"),         # Should be fine
            (10 * 1024, "10KB"),   # Should be fine
            (1024 * 1024, "1MB"),  # Might hit limits
            (10 * 1024 * 1024, "10MB"),  # Should hit limits
        ]

        for size, description in size_tests:
            large_data = {
                "data": "x" * size,
                "description": f"Testing {description} payload"
            }

            response = await api_client.post("{{ endpoints[2] if len(endpoints) > 2 else endpoints[0] }}", json=large_data)

            # Large payloads should be rejected
            if size > 1024 * 1024:  # Over 1MB
                assert response.status_code in [400, 413, 422], \\
                    f"{description} payload not properly limited"


# Helper function
def extract_resource(endpoint: str) -> str:
    """Extract resource name from endpoint."""
    return endpoint.lstrip('/').split('/')[0].rstrip('s')
'''

    # Render and write template
    env = Environment(
        loader=DictLoader({"security": template}),
        autoescape=select_autoescape(["html", "xml"]),
    )
    # Add built-in Python functions to the environment
    env.globals.update(
        len=len,
        str=str,
        int=int,
        float=float,
        bool=bool,
        range=range,
        enumerate=enumerate,
    )
    rendered = env.get_template("security").render(**context)

    test_file = output_dir / f"test_{context['python_name']}_security.py"
    test_file.write_text(rendered, encoding="utf-8")

    if verbose:
        console.print(f"[OK] Generated security tests: {test_file}")

    return True


def _generate_contract_tests(
    output_dir: Path,
    context: dict[str, Any],
    schema_file: Path | None,
    verbose: bool,
) -> bool:
    """Generate contract tests (basic implementation for Phase 1)."""
    template = '''"""
Contract Tests for {{ api_name }}

Generated by TestAPIX on {{ timestamp }}

Contract tests ensure API compatibility by validating:
- Response structure matches expected schema
- Required fields are present
- Data types are correct
- No breaking changes in API evolution

These tests help prevent integration issues between API providers and consumers.
"""

import pytest
from typing import Dict, Any
import json

from testapix import APIClient, assert_that
{% if schema_file %}
from pathlib import Path
{% endif %}


class Test{{ python_name.title() }}Contract:
    """Contract validation tests for {{ api_name }}."""

    @pytest.fixture(autouse=True)
    def setup(self, api_client: APIClient):
        self.client = api_client
        {% if schema_file %}
        # Load schema file
        schema_path = Path("{{ schema_file }}")
        if schema_path.exists():
            with open(schema_path) as f:
                self.schema = json.load(f)
        else:
            self.schema = None
        {% endif %}

    {% for endpoint in endpoints %}
    async def test_{{ generate_test_name(endpoint, "contract") }}(self):
        """Test response contract for {{ endpoint }}."""
        response = await self.client.get("{{ endpoint }}".replace("{id}", "1"))

        # Basic contract validation
        assert_that(response).has_status_in([200, 404])

        if response.status_code == 200:
            # Verify response structure
            assert_that(response).has_json()

            # Check required fields exist
            # Customize these based on your API contract
            required_fields = ["id", "created_at", "updated_at"]

            for field in required_fields:
                assert_that(response).has_json_path(field), \\
                    f"Required field '{field}' missing from response"

            # Verify data types
            if response.has_json_path("id"):
                assert isinstance(response.json_path("id"), (str, int)), \\
                    "ID should be string or integer"

            if response.has_json_path("created_at"):
                # Should be ISO format timestamp
                timestamp = response.json_path("created_at")
                assert isinstance(timestamp, str), "Timestamp should be string"
                # Add more specific timestamp validation as needed

    {% endfor %}

    async def test_response_headers_contract(self):
        """Test that API returns expected headers."""
        response = await self.client.get("{{ endpoints[0] }}")

        # Expected headers that should always be present
        required_headers = [
            "content-type",
            "x-request-id",  # For request tracking
        ]

        for header in required_headers:
            assert_that(response).has_header(header), \\
                f"Required header '{header}' not present"

        # Verify content-type for JSON APIs
        if response.headers.get("content-type"):
            assert "application/json" in response.headers["content-type"], \\
                "API should return JSON content type"

    async def test_error_response_contract(self):
        """Test that error responses follow consistent structure."""
        # Trigger a 404 error
        response = await self.client.get("/nonexistent-endpoint-12345")

        assert_that(response).has_status(404)

        # Verify error response structure
        assert_that(response).has_json()

        # Common error response fields
        error_fields = ["error", "message", "status_code", "timestamp"]

        for field in error_fields:
            if response.has_json_path(field):
                # At least some error fields should be present
                break
        else:
            pytest.fail("Error response doesn't follow expected structure")

    {% if include_examples %}
    async def test_pagination_contract(self):
        """Test pagination response contract."""
        response = await self.client.get("{{ endpoints[0] }}", params={
            "page": 1,
            "per_page": 10
        })

        if response.status_code == 200:
            # Check pagination structure
            if response.has_json_path("pagination"):
                pagination = response.json_path("pagination")

                # Verify pagination fields
                pagination_fields = ["page", "per_page", "total", "total_pages"]

                for field in pagination_fields:
                    assert field in pagination, \\
                        f"Pagination missing required field: {field}"

                # Verify data types
                assert isinstance(pagination.get("page"), int)
                assert isinstance(pagination.get("per_page"), int)
                assert isinstance(pagination.get("total"), int)
    {% endif %}
'''

    # Render and write template
    env = Environment(
        loader=DictLoader({"contract": template}),
        autoescape=select_autoescape(["html", "xml"]),
    )
    # Add built-in Python functions to the environment
    env.globals.update(
        len=len,
        str=str,
        int=int,
        float=float,
        bool=bool,
        range=range,
        enumerate=enumerate,
    )
    rendered = env.get_template("contract").render(**context)

    test_file = output_dir / f"test_{context['python_name']}_contract.py"
    test_file.write_text(rendered, encoding="utf-8")

    if verbose:
        console.print(f"[OK] Generated contract tests: {test_file}")

    return True


def _generate_performance_tests(
    output_dir: Path, context: dict[str, Any], verbose: bool
) -> bool:
    """Generate performance tests (basic implementation for Phase 1)."""
    template = '''"""
Performance Tests for {{ api_name }}

Generated by TestAPIX on {{ timestamp }}

Performance tests ensure your API meets performance requirements:
- Response time SLAs
- Throughput capabilities
- Resource efficiency
- Behavior under load

These basic tests check individual endpoint performance.
Full load testing will be available in TestAPIX Phase 3.
"""

import pytest
import asyncio
import time
from typing import List
from statistics import mean, median, stdev

from testapix import APIClient, assert_that


class Test{{ python_name.title() }}Performance:
    """Performance tests for {{ api_name }}."""

    @pytest.fixture(autouse=True)
    def setup(self, api_client: APIClient):
        self.client = api_client

    {% for endpoint in endpoints[:3] %}  # Test first 3 endpoints
    @pytest.mark.performance
    async def test_{{ generate_test_name(endpoint, "response_time") }}(self):
        """Test response time for {{ endpoint }}."""
        # Make multiple requests to get average
        response_times = []

        for _ in range(10):
            start_time = time.time()
            response = await self.client.get("{{ endpoint }}".replace("{id}", "1"))
            response_time = time.time() - start_time

            if response.status_code < 500:  # Only count successful requests
                response_times.append(response_time)

        # Calculate statistics
        avg_time = mean(response_times)
        median_time = median(response_times)

        # Performance assertions
        assert avg_time < 2.0, f"Average response time {avg_time:.2f}s exceeds 2s limit"
        assert median_time < 1.5, f"Median response time {median_time:.2f}s exceeds 1.5s limit"

        # Log performance metrics
        console.print(f"{{ endpoint }} - Avg: {avg_time:.3f}s, Median: {median_time:.3f}s")

    {% endfor %}

    @pytest.mark.performance
    async def test_concurrent_request_performance(self):
        """Test API performance under concurrent requests."""
        concurrent_requests = 10

        async def make_request():
            start = time.time()
            response = await self.client.get("{{ endpoints[0] }}")
            return time.time() - start, response.status_code

        # Execute requests concurrently
        start_time = time.time()
        results = await asyncio.gather(*[make_request() for _ in range(concurrent_requests)])
        total_time = time.time() - start_time

        # Extract times and status codes
        times = [r[0] for r in results]
        statuses = [r[1] for r in results]

        # Performance analysis
        successful_requests = sum(1 for s in statuses if s < 400)
        avg_response_time = mean(times)

        # Assertions
        assert successful_requests >= concurrent_requests * 0.8, \\
            f"Only {successful_requests}/{concurrent_requests} requests succeeded"

        assert avg_response_time < 3.0, \\
            f"Average response time {avg_response_time:.2f}s too high under load"

        # Log results
        console.print(f"Concurrent test - Total: {total_time:.2f}s, Avg: {avg_response_time:.2f}s")

    @pytest.mark.performance
    @pytest.mark.slow
    async def test_sustained_load_performance(self):
        """Test API performance under sustained load."""
        duration = 10  # seconds
        request_interval = 0.1  # seconds between requests

        response_times = []
        errors = 0
        start_time = time.time()

        while time.time() - start_time < duration:
            request_start = time.time()

            try:
                response = await self.client.get("{{ endpoints[0] }}")
                response_time = time.time() - request_start

                if response.status_code < 500:
                    response_times.append(response_time)
                else:
                    errors += 1

            except Exception:
                errors += 1

            # Wait before next request
            await asyncio.sleep(request_interval)

        # Calculate statistics
        total_requests = len(response_times) + errors
        success_rate = len(response_times) / total_requests if total_requests > 0 else 0

        # Performance assertions
        assert success_rate > 0.95, f"Success rate {success_rate:.2%} below 95%"

        if response_times:
            avg_time = mean(response_times)
            assert avg_time < 2.0, f"Average response time {avg_time:.2f}s exceeds limit"

            # Check for performance degradation
            first_half = response_times[:len(response_times)//2]
            second_half = response_times[len(response_times)//2:]

            if len(first_half) > 5 and len(second_half) > 5:
                degradation = mean(second_half) / mean(first_half)
                assert degradation < 1.5, f"Performance degraded by {degradation:.1f}x"

    @pytest.mark.performance
    async def test_response_size_impact(self):
        """Test how response size affects performance."""
        # Test with different page sizes
        page_sizes = [1, 10, 50, 100]
        results = {}

        for size in page_sizes:
            response = await self.client.get("{{ endpoints[0] }}", params={
                "per_page": size
            })

            if response.status_code == 200:
                results[size] = {
                    "time": response.response_time,
                    "size": len(response.content)
                }

        # Verify reasonable scaling
        if len(results) > 1:
            sizes = sorted(results.keys())

            # Response time shouldn't scale linearly with size
            for i in range(1, len(sizes)):
                size_ratio = sizes[i] / sizes[i-1]
                time_ratio = results[sizes[i]]["time"] / results[sizes[i-1]]["time"]

                # Time should scale sub-linearly with size
                assert time_ratio < size_ratio * 0.8, \\
                    f"Response time scaling poorly: {time_ratio:.1f}x for {size_ratio}x size increase"
'''

    # Render and write template
    env = Environment(
        loader=DictLoader({"performance": template}),
        autoescape=select_autoescape(["html", "xml"]),
    )
    # Add built-in Python functions to the environment
    env.globals.update(
        len=len,
        str=str,
        int=int,
        float=float,
        bool=bool,
        range=range,
        enumerate=enumerate,
    )
    rendered = env.get_template("performance").render(**context)

    test_file = output_dir / f"test_{context['python_name']}_performance.py"
    test_file.write_text(rendered, encoding="utf-8")

    if verbose:
        console.print(f"[OK] Generated performance tests: {test_file}")

    return True


def _show_test_preview(test_file: Path) -> None:
    """Show a preview of the generated test file."""
    content = test_file.read_text()

    # Show first 50 lines as preview
    lines = content.split("\n")
    preview_lines = lines[:50]

    if len(lines) > 50:
        preview_lines.append("... (truncated)")

    preview = "\n".join(preview_lines)

    console.print("\n📄 Test Preview:", style="bold")
    console.print(Syntax(preview, "python", theme="monokai"))
