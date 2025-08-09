# TestAPIX - Modern Python API Testing Framework

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

TestAPIX is a modern, comprehensive API testing framework designed to make API testing both powerful and accessible. Built from the ground up with Python async patterns, TestAPIX provides everything from simple functional tests to sophisticated security testing, schema validation, and interactive API exploration.

## Why TestAPIX?

Traditional API testing tools force you to choose between simplicity and power. TestAPIX eliminates this compromise by providing:

**🚀 Instant Productivity**: Get from zero to comprehensive tests in under 5 minutes with our intelligent CLI and generated examples that demonstrate best practices.

**📚 Learning Through Examples**: Every generated test includes detailed comments explaining not just what the code does, but why it's structured that way and how to extend it.

**⚡ Progressive Enhancement**: Start simple with basic functional tests, then seamlessly adopt advanced features like security testing, persona-based authentication, and interactive exploration as your needs evolve.

**🎯 Actionable Insights**: When tests fail, TestAPIX provides clear, contextual error messages with suggestions for resolution, not cryptic stack traces.

**🛠️ Interactive Development**: Explore APIs in real-time with our rich interactive CLI, then generate tests from your exploration sessions.

## ✨ Key Features

### 🌐 Comprehensive Testing Capabilities
- **Async-First Architecture**: Built on modern Python async/await for superior performance and scalability
- **Fluent Assertions**: Write tests that read like specifications with comprehensive assertion chaining
- **Smart HTTP Client**: Automatic retries, intelligent error handling, and response enhancement
- **Realistic Test Data**: Context-aware data generation that uncovers real edge cases and bugs

### 🔒 Security Testing
- **OWASP-Compliant Security Tests**: Comprehensive security vulnerability testing including:
  - SQL injection prevention validation
  - Cross-Site Scripting (XSS) attack detection
  - Authentication and authorization boundary testing
  - Rate limiting and abuse prevention verification
  - Security headers validation
- **Security Test Payloads**: Comprehensive payloads across multiple attack vectors
- **Responsible Testing**: Built-in safeguards and warnings for ethical security testing

### 👥 Persona-Based Authentication Testing
- **Business-Context Authentication**: Test with realistic user personas and roles
- **Multi-Provider Support**: Bearer tokens, API keys, OAuth2, Basic Auth, and custom providers
- **Session Management**: Automatic token refresh, auth failure handling, and session persistence
- **Cross-Authentication Testing**: Validate proper isolation between different user contexts

### 🖥️ Interactive API Exploration
- **Rich Interactive CLI**: Explore APIs in real-time with syntax highlighting and intelligent suggestions
- **Session Management**: Save and restore exploration sessions with secure credential handling
- **Test Generation**: Convert interactive sessions into automated test files
- **Multiple Export Formats**: Generate tests in pytest, curl, Postman collection, or Python requests format

### 🏗️ Developer Experience Excellence
- **Intelligent CLI**: Generate projects, tests, and configurations with helpful guidance and validation
- **Multi-Environment Support**: Seamlessly test across development, staging, and production environments
- **Advanced Error Reporting**: Batch error aggregation, detailed context, and intelligent error suggestions
- **Schema Validation**: JSON Schema validation with detailed mismatch reporting
- **Extensible Architecture**: Plugin-ready design for custom assertions, generators, and authentication providers

## Quick Start

### Installation

Install TestAPIX from PyPI:

```bash
# Basic installation
pip install testapix

# Full installation with interactive CLI support
pip install 'testapix[interactive]'
```

### Option 1: Traditional Project Setup

Create a structured test project:

```bash
# Create a new test project
testapix init my-api-tests

# Navigate to your project
cd my-api-tests

# Generate comprehensive functional tests
testapix generate functional user-api

# Run your tests
pytest tests/ -v
```

### Option 2: Interactive API Exploration

Start exploring APIs immediately:

```bash
# Launch interactive CLI
testapix interactive --api https://api.example.com

# Or with authentication
testapix interactive --api https://api.example.com
```

```bash
# In the interactive shell:
🌐 TestAPIX Interactive Shell
> auth bearer your-token-here
✅ Authentication configured

> get /users
📊 GET /users → 200 OK (234ms)
{
  "users": [{"id": 1, "name": "John", "email": "john@example.com"}]
}

> generate test functional my-users-test.py
✅ Test file generated from session history

> save my-exploration-session
✅ Session saved for later use
```

That's it! You now have either a complete test project or interactive exploration ready to generate tests.

## Core Usage Examples

### Writing Comprehensive Tests

TestAPIX tests are clean, readable, and powerful:

```python
import pytest
from testapix import APIClient, assert_that
from testapix.generators import BaseGenerator

class TestUserAPI:
    def setup_method(self):
        self.generator = BaseGenerator()

    @pytest.fixture(autouse=True)
    def setup(self, api_client: APIClient):
        self.client = api_client

    async def test_create_user_comprehensive(self):
        # Generate realistic test data
        user_data = self.generator.generate_user_data()

        # Create user with comprehensive validation
        response = await self.client.post("/users", json=user_data)

        # Fluent assertions with detailed validation
        assert_that(response) \
            .has_status(201) \
            .has_header("location") \
            .has_json_path("id") \
            .has_json_path("email") \
            .response_time_less_than(2.0)

        # Verify user can be retrieved
        user_id = response.json().get("id")
        get_response = await self.client.get(f"/users/{user_id}")
        assert_that(get_response) \
            .has_status(200) \
            .has_json_path("id")
```

### Persona-Based Authentication Testing

Test with realistic business contexts:

```python
from testapix.auth import PersonaPool, UserPersona, PersonaRole

class TestUserPermissions:
    def setup_method(self):
        # Define business personas
        self.personas = PersonaPool([
            UserPersona(
                name="admin_user",
                role=PersonaRole.ADMIN,
                credentials={"token": "admin-token-here"}
            ),
            UserPersona(
                name="regular_user",
                role=PersonaRole.USER,
                credentials={"token": "user-token-here"}
            )
        ])

    async def test_admin_can_delete_users(self):
        # Test as admin persona
        async with self.personas.get_client("admin_user") as admin_client:
            response = await admin_client.delete("/users/123")
            assert_that(response).has_status(204)

    async def test_user_cannot_delete_users(self):
        # Test as regular user persona
        async with self.personas.get_client("regular_user") as user_client:
            response = await user_client.delete("/users/123")
            assert_that(response).has_status(403)
```

### Security Testing

Comprehensive security validation:

```python
from testapix.generators import BaseGenerator

class TestAPISecurity:
    def setup_method(self):
        self.generator = BaseGenerator()

    @pytest.mark.security
    async def test_sql_injection_protection(self, api_client: APIClient):
        """Verify API protects against SQL injection attacks."""

        # Generate SQL injection payloads
        payloads = self.generator.generate_security_test_data("sql_injection")

        for payload_name, payload in payloads.items():
            response = await api_client.get("/users", params={"search": payload})

            # API should either reject malicious input or handle it safely
            assert response.status_code in [400, 401, 403, 422] or \
                   (response.status_code == 200 and "error" not in response.text.lower()), \
                   f"SQL injection vulnerability detected with payload: {payload_name}"

    @pytest.mark.security
    async def test_xss_protection(self, api_client: APIClient):
        """Verify API protects against XSS attacks."""

        xss_payloads = self.generator.generate_security_test_data("xss")

        for payload_name, payload in xss_payloads.items():
            user_data = {"name": payload, "email": "test@example.com"}
            response = await api_client.post("/users", json=user_data)

            if response.status_code == 201:
                # If user created, ensure XSS payload is properly escaped
                user_id = response.json().get("id")
                get_response = await api_client.get(f"/users/{user_id}")
                assert_that(get_response).has_status(200)
                # Verify no script tags in response
                assert "<script>" not in get_response.text
                assert "javascript:" not in get_response.text
                assert "onerror=" not in get_response.text
```

### Multi-Environment Configuration

Seamless environment management:

```yaml
# configs/base.yaml
http:
  timeout: 30.0
  retries: 3
  verify_ssl: true

auth:
  type: "bearer"
  token: "${TESTAPIX_AUTH_TOKEN}"

security_testing:
  enable_sql_injection: true
  enable_xss_tests: true
  max_payload_size: 10000

reporting:
  formats: ["console", "html", "junit"]
  output_dir: "reports"
```

```yaml
# configs/staging.yaml
http:
  base_url: "https://staging-api.example.com"
  timeout: 60.0  # Longer timeout for staging

security_testing:
  enable_sql_injection: false  # Skip in staging
```

```bash
# Run tests across environments
TESTAPIX_ENVIRONMENT=local pytest tests/
TESTAPIX_ENVIRONMENT=staging pytest tests/ -m "not destructive"
TESTAPIX_ENVIRONMENT=production pytest tests/ -m "smoke"
```

## Interactive CLI Features

The TestAPIX Interactive CLI provides a rich, terminal-based environment for real-time API exploration:

### Key Interactive Features

- **🔐 Authentication Management**: Configure and switch between multiple authentication methods
- **📊 Rich Response Display**: JSON syntax highlighting with intelligent data analysis
- **💾 Session Persistence**: Save exploration sessions and reload them later
- **⚡ Test Generation**: Convert interactive sessions into automated test files
- **🔍 Advanced Response Analysis**: Extract data with JSON paths, validate schemas, analyze performance

### Interactive CLI Example Session

```bash
$ testapix interactive --api https://api.github.com

🌐 TestAPIX Interactive Shell - API Exploration Environment
Connected to: https://api.github.com

# Configure authentication
> auth bearer ghp_your_token_here
✅ Bearer token authentication configured

# Explore endpoints with rich output
> get /user
📊 GET /user → 200 OK (156ms)
{
  "login": "octocat",
  "id": 1,
  "name": "The Octocat",
  "email": "octocat@github.com"
}

# Extract specific data
> extract login
🎯 Extracted: "octocat"

# Save session for later
> save github-exploration
✅ Session saved: github-exploration

# Generate test file from session
> generate test testapix github_tests.py
✅ Generated test file: github_tests.py
  - 5 test methods created from session history
  - Includes authentication setup
  - Comprehensive assertions included

# Export in different formats
> export curl github_commands.sh
✅ Exported 5 curl commands to github_commands.sh

> export postman github_collection.json
✅ Exported Postman collection to github_collection.json
```

## Project Structure

TestAPIX projects follow a comprehensive, scalable structure:

```
my-api-tests/
├── configs/                    # Environment configurations
│   ├── base.yaml              # Shared settings
│   ├── local.yaml             # Local development overrides
│   ├── staging.yaml           # Staging environment settings
│   └── production.yaml        # Production settings (smoke tests only)
├── tests/                     # Test suites organized by paradigm
│   ├── functional/            # API functionality tests
│   ├── security/              # Security vulnerability tests
│   ├── contract/              # Basic response structure validation
│   ├── performance/           # Response time and basic load tests
│   └── integration/           # End-to-end integration tests
├── personas/                  # User personas and authentication configs
│   ├── admin_personas.yaml    # Admin user configurations
│   └── user_personas.yaml     # Regular user configurations
├── data_generators/           # Custom test data generators
│   ├── user_generator.py      # User-specific data generation
│   └── product_generator.py   # Product/business domain data
├── schemas/                   # API schemas and validation rules
│   ├── openapi.yaml          # OpenAPI/Swagger specifications
│   └── json_schemas/         # JSON schema validation files
├── reports/                   # Test execution reports
│   ├── coverage/             # Test coverage reports
│   ├── security/             # Security scan results
│   └── performance/          # Performance test results
├── sessions/                  # Saved interactive CLI sessions
└── .testapix/                # Framework configuration and cache
```

## Advanced Features

### Security Testing

TestAPIX includes production-ready security testing capabilities:

```bash
# Generate comprehensive security test suite
testapix generate security payment-api --endpoints "/charge,/refund,/admin"
```

**Generated Security Test Categories:**

1. **Authentication & Authorization**
   - Missing authentication detection
   - Invalid token/credential testing
   - Cross-user authorization boundary validation
   - Privilege escalation attempt detection

2. **Injection Attack Prevention**
   - SQL injection with 13+ attack vectors
   - XSS prevention with 14+ payload variations
   - Command injection detection
   - Path traversal attack testing
   - LDAP and XML injection testing

3. **HTTP Security Standards**
   - Security headers validation (CSP, HSTS, X-Frame-Options)
   - Basic CORS configuration testing
   - Content-type validation

4. **Rate Limiting & Basic Abuse Prevention**
   - Basic rate limiting detection
   - Request validation testing

### Basic Contract Testing & Schema Validation

Ensure API compatibility and data integrity:

```bash
# Generate basic contract tests from OpenAPI specification
testapix generate contract user-api --schema-file openapi.yaml
```

**Note**: TestAPIX provides basic response structure validation and schema compliance checking. For full consumer-driven contract testing and API evolution management, consider complementing with specialized contract testing tools.

### Advanced Error Reporting & Debugging

TestAPIX provides sophisticated error analysis:

```python
from testapix import batch_operation, get_batch_aggregator

# Batch operations with comprehensive error aggregation
async def test_bulk_user_operations(api_client):
    user_ids = [1, 2, 3, 4, 5]

    async with batch_operation("bulk_user_deletion"):
        for user_id in user_ids:
            response = await api_client.delete(f"/users/{user_id}")
            assert_that(response).has_status(204)

    # Get detailed error report if any operations failed
    error_report = get_batch_aggregator().get_detailed_report()
    if error_report.has_errors():
        print(error_report.format_with_suggestions())
```

### Performance Testing

Basic performance validation capabilities:

```python
@pytest.mark.performance
async def test_api_performance_requirements(api_client):
    """Validate API meets basic performance requirements."""

    # Test response time requirements
    response = await api_client.get("/users", params={"limit": 100})
    assert_that(response) \
        .has_status(200) \
        .response_time_less_than(2.0)

    # Test basic concurrent request handling
    import asyncio
    async def make_request():
        return await api_client.get("/users")

    # Execute 5 concurrent requests
    responses = await asyncio.gather(*[make_request() for _ in range(5)])

    assert all(r.status_code == 200 for r in responses)
```

**Note**: TestAPIX provides basic performance testing for response times and simple concurrent requests. For comprehensive load testing, consider integrating with specialized tools like Locust or Artillery.

## CLI Command Reference

### Project Management
```bash
# Initialize new testing project
testapix init my-project --template advanced

# Validate configuration files
testapix validate-config --environment staging
```

### Test Generation
```bash
# Functional tests
testapix generate functional user-api --endpoints "/users,/profiles"

# Security tests (with safety warnings)
testapix generate security api --endpoints "/admin,/payment"

# Basic contract tests from OpenAPI spec
testapix generate contract api --schema-file swagger.yaml

# Basic performance tests
testapix generate performance api --endpoints "/search,/reports"
```

### Interactive Exploration
```bash
# Basic interactive session
testapix interactive

# With API URL and authentication
testapix interactive --api https://api.example.com --auth-file auth.yaml

# Load previous session
testapix interactive --session my-saved-session
```

## Learning Resources

TestAPIX is designed as a teaching tool that promotes best practices:

### Generated Code Quality
- **Comprehensive Documentation**: Every generated test includes detailed comments explaining patterns and best practices
- **Real-World Examples**: Generated tests demonstrate actual edge cases and error scenarios you'll encounter
- **Progressive Complexity**: Start with basic patterns and learn advanced techniques through example
- **Best Practice Patterns**: Authentication handling, error management, and test organization following industry standards

### Educational Features
- **Error Context**: When tests fail, get explanations of what went wrong and how to fix it
- **Pattern Recognition**: Learn to recognize anti-patterns and security vulnerabilities through hands-on testing
- **Interactive Learning**: Use the CLI to explore APIs and understand their behavior before writing tests

## Enterprise Deployment

### CI/CD Integration

TestAPIX integrates seamlessly with modern CI/CD pipelines:

```yaml
# .github/workflows/api-tests.yml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        test-type: [functional, security, contract]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install TestAPIX
      run: pip install 'testapix[interactive]'

    - name: Run API Tests
      run: |
        testapix validate-config
        pytest tests/${{ matrix.test-type }}/ -v --junit-xml=reports/results.xml

    - name: Upload Test Results
      uses: actions/upload-artifact@v3
      with:
        name: test-results-${{ matrix.test-type }}
        path: reports/
```

### Security & Compliance

- **Responsible Testing**: Built-in warnings and safeguards for security testing
- **Credential Management**: Secure handling of authentication tokens and sensitive data
- **Audit Trails**: Comprehensive logging of all test activities for compliance
- **Data Privacy**: Automatic sanitization of sensitive data in logs and reports

## Contributing

TestAPIX is designed for extensibility. Common contribution areas:

- **Custom Assertions**: Domain-specific validation logic
- **Authentication Providers**: Enterprise authentication systems
- **Data Generators**: Industry-specific test data patterns
- **Security Tests**: Additional vulnerability detection patterns
- **Report Formats**: Integration with monitoring and alerting systems

See our [Contributing Guide](CONTRIBUTING.md) for development setup and guidelines.

## 🗺️ Development Roadmap

### ✅ Phase 1 - Core Foundation (Complete)
- Modern async HTTP client with intelligent retry logic
- Fluent assertion library with comprehensive validation
- Multi-environment configuration system
- Intelligent CLI with project scaffolding
- Advanced test generation with best practices

### ✅ Phase 2 - Enhanced Features (Complete)
- Persona-based authentication system
- Interactive CLI with session management
- Advanced error reporting and batch operations
- JSON Schema validation system
- Comprehensive security testing framework

### 🚧 Phase 3 - Advanced Integration (In Progress)
- Plugin system for custom extensions
- Enhanced contract testing with API evolution tracking
- Comprehensive performance testing and load generation
- Extended GraphQL support and testing

### 📋 Phase 4 - Ecosystem & Tooling (Planned)
- IDE plugins (VS Code, PyCharm) with intelligent test generation
- Cloud service integrations (AWS, Azure, GCP)
- Advanced CI/CD integrations and pipeline templates
- Real-time collaboration features for team testing

### 📋 Phase 5 - AI-Powered Testing (Future)
- Intelligent test case generation from API usage patterns
- Automated vulnerability discovery and test creation
- Natural language test specification and generation
- Predictive API reliability and performance analysis

## 📄 License

TestAPIX is released under the MIT License. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

TestAPIX stands on the shoulders of giants in the Python ecosystem:

- **[httpx](https://www.python-httpx.org/)** - Modern, async HTTP client foundation
- **[pytest](https://pytest.org/)** - Powerful, flexible testing framework
- **[Click](https://click.palletsprojects.com/)** - Beautiful command-line interface creation
- **[Rich](https://rich.readthedocs.io/)** - Rich terminal output and interactive interfaces
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** - Data validation and settings management
- **[Mimesis](https://mimesis.name/)** - Realistic test data generation
- **[Prompt Toolkit](https://python-prompt-toolkit.readthedocs.io/)** - Interactive CLI foundation
- **[Jinja2](https://jinja.palletsprojects.com/)** - Flexible template engine for code generation

## 🚀 Get Started Now!

Ready to transform your API testing workflow?

### Quick Start (2 minutes)
```bash
pip install 'testapix[interactive]'
testapix init my-first-project
cd my-first-project
testapix generate functional my-api
pytest tests/ -v
```

### Interactive Exploration (30 seconds)
```bash
pip install 'testapix[interactive]'
testapix interactive --api https://jsonplaceholder.typicode.com
```

### Security Testing
```bash
pip install 'testapix[interactive]'
testapix init secure-api-tests --template microservices
testapix generate security payment-api --endpoints "/charge,/refund"
pytest tests/security/ -v
```

---

<p align="center">
  <strong>Built by API testing professionals who believe comprehensive testing should be intuitive, powerful, and enjoyable.</strong>
</p>

<p align="center">
  Join the TestAPIX community and help shape the future of intelligent API testing.
</p>
