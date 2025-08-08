"""
Dependency checking utilities for lark_helper.

This module provides utilities for checking optional dependencies
and providing helpful error messages when they are missing.
"""

import importlib.util
from typing import Optional, Tuple


def check_dependency(
    package_name: str,
    min_version: Optional[str] = None,
    install_name: Optional[str] = None,
    extras_name: Optional[str] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Check if a dependency is installed and meets the minimum version requirement.

    Args:
        package_name: Name of the package to check
        min_version: Minimum version required (optional)
        install_name: Name to use in installation instructions (defaults to package_name)
        extras_name: Name of the extras group to use in installation instructions

    Returns:
        Tuple of (is_available, error_message)
        - is_available: True if the dependency is available and meets version requirements
        - error_message: Error message if the dependency is not available, None otherwise
    """
    install_name = install_name or package_name

    # Check if the package is installed
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        # Package not found
        if extras_name:
            error_message = (
                f"{package_name} is required for this functionality. "
                f"Install with: pip install lark-helper[{extras_name}]"
            )
        else:
            error_message = (
                f"{package_name} is required for this functionality. "
                f"Install with: pip install {install_name}"
            )
        return False, error_message

    # If no version check is needed, return success
    if min_version is None:
        return True, None

    # Check version if specified
    try:
        module = importlib.import_module(package_name)
        version = getattr(module, "__version__", None)

        if version is None:
            # Can't determine version, assume it's okay
            return True, None

        # Simple version comparison (this is a basic implementation)
        # For production code, consider using packaging.version.parse
        installed_parts = [int(p) for p in version.split(".")]
        required_parts = [int(p) for p in min_version.split(".")]

        for i, p in enumerate(required_parts):
            if i >= len(installed_parts) or installed_parts[i] < p:
                error_message = (
                    f"{package_name} version {min_version} or higher is required, "
                    f"but version {version} is installed. "
                    f"Upgrade with: pip install --upgrade {install_name}"
                )
                return False, error_message
            elif installed_parts[i] > p:
                # Higher version found, no need to check further
                break

        return True, None

    except (ImportError, AttributeError):
        # If we can't check the version, assume it's okay
        return True, None


def check_async_dependencies() -> Tuple[bool, Optional[str]]:
    """
    Check if all dependencies required for async functionality are available.

    Returns:
        Tuple of (all_available, error_message)
        - all_available: True if all async dependencies are available
        - error_message: Error message if any dependency is not available, None otherwise
    """
    # Currently we only need aiohttp for async functionality
    return check_dependency("aiohttp", min_version="3.8.0", extras_name="async")


def is_async_supported() -> bool:
    """
    Check if async functionality is supported.

    Returns:
        True if async functionality is supported, False otherwise
    """
    available, _ = check_async_dependencies()
    return available


def require_async_support() -> None:
    """
    Require async functionality to be supported.

    Raises:
        ImportError: If any required dependency is missing
    """
    available, error_message = check_async_dependencies()
    if not available:
        raise ImportError(error_message)
