#!/usr/bin/env python3
"""TestAPIX CLI module entry point.

This module allows TestAPIX to be executed with:
    python -m testapix

This is useful for testing and environments where the testapix script
is not installed or available in PATH.
"""

from testapix.cli.main import cli

if __name__ == "__main__":
    cli()
