"""Legacy authentication module - compatibility wrapper.

This module provides backward compatibility for existing code that imports
from urarovite.checker.auth. All functionality is now provided by the
new urarovite.auth.google_sheets module.

DEPRECATED: Use urarovite.auth.google_sheets instead for new code.
"""

# Re-export functions from new gspread-focused auth module for backward compatibility
from urarovite.auth.google_sheets import (
    get_gspread_client,
    clear_client_cache as clear_service_cache,
)

# Note: OAuth functionality removed in favor of gspread with base64 credentials
# Legacy functions are no longer available

__all__ = [
    "get_gspread_client",
    "clear_service_cache",
]
