"""TestAPIX Assertions Module

This module provides the fluent assertion interface that makes TestAPIX tests
readable and expressive. Instead of writing:

    assert response.status_code == 200
    data = response.json()
    assert 'user' in data
    assert data['user']['email'] == 'test@example.com'

You can write:

    assert_that(response)
        .has_status(200)
        .has_json_path('user.email', 'test@example.com')

This approach has several benefits:
1. Tests read like natural language specifications
2. Error messages are more helpful and specific
3. Common patterns are built-in (like JSON path extraction)
4. Assertions can be chained for complex validations

The assertion system is designed to fail fast with clear error messages
that help developers quickly understand what went wrong.
"""

from testapix.assertions.response import ResponseAssertion, assert_that

# Export the main assertion interface
__all__ = ["ResponseAssertion", "assert_that"]

# Module version
__version__ = "0.1.0"
