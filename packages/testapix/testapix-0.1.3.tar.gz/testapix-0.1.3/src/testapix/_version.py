"""Version information for TestAPIX package.

This module provides version information that can be imported safely
from any part of the package without causing circular imports.
"""

import tomllib
from pathlib import Path


def get_version() -> str:
    """Get version from pyproject.toml file.

    Returns:
        str: The version string from pyproject.toml

    """
    try:
        # Find pyproject.toml in the package root
        package_root = Path(__file__).parent.parent.parent
        pyproject_path = package_root / "pyproject.toml"

        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                version = data["tool"]["poetry"]["version"]
                return str(version)
    except (FileNotFoundError, KeyError, OSError):
        # Fallback version if reading from pyproject.toml fails
        pass

    # Fallback version
    return "0.1.2"


# Export the version at module level
__version__ = get_version()
