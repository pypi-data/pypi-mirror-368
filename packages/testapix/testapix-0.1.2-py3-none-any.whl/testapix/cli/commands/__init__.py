"""TestAPIX CLI Commands Module

This module contains the implementation of individual CLI commands. Each command
is designed to be self-contained while sharing common utilities and patterns.

The commands follow these design principles:

1. Helpful by Default: Commands provide sensible defaults and helpful output
   that guides users toward success rather than just reporting failures.

2. Progressive Complexity: Simple use cases work with minimal configuration,
   while advanced features are available through options and flags.

3. Educational Output: Generated files include comprehensive comments and
   examples that teach best practices through working code.

4. Graceful Error Handling: When things go wrong, error messages explain
   what happened and suggest how to fix it, rather than showing stack traces.

Commands in this module:
- init: Create new TestAPIX projects with appropriate structure and examples
- generate: Create test files that demonstrate testing patterns
- validate_config: Check configuration files for errors and inconsistencies

Each command module exports functions that can be called programmatically,
making it easy to integrate TestAPIX functionality into other tools.
"""

# Version for the commands module
__version__ = "0.1.0"
