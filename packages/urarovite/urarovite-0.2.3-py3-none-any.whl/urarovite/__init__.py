"""Urarovite - A Google Sheets validation library.

This library provides two main functions for integrating with batch processing systems:
- get_available_validation_criteria(): Returns all supported validation checks
- execute_validation(): Executes validation checks on Google Sheets

Example usage:
    from urarovite import get_available_validation_criteria, execute_validation
    
    # Get available validation options
    criteria = get_available_validation_criteria()
    
    # Execute validations
    checks = [{"id": "empty_cells", "mode": "fix"}]
    result = execute_validation(checks, sheet_url, auth_secret)
"""

# Main API functions (required by Uvarolite system)
from urarovite.core.api import (
    get_available_validation_criteria,
    execute_validation,
)

# Core modules for advanced usage
from urarovite import core, auth, validators, utils, config

# Legacy modules (for backward compatibility)
from urarovite import checker, resolver

# Version is now managed by hatch-vcs from Git tags
try:
    from urarovite._version import __version__
except ImportError:
    # Fallback for development installs without build
    __version__ = "dev"

__all__ = [
    # Main API functions
    "get_available_validation_criteria", 
    "execute_validation",
    # Core modules
    "core",
    "auth", 
    "validators",
    "utils",
    "config",
    # Legacy modules
    "checker",
    "resolver",
]
