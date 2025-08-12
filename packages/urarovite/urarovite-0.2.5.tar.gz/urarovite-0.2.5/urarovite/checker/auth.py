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
    create_sheets_service_from_encoded_creds,
)

# Note: OAuth functionality removed in favor of gspread with base64 credentials
# Legacy functions are no longer available

def get_sheets_service():
    """Legacy compatibility function for get_sheets_service().
    
    DEPRECATED: This function is deprecated and will be removed in a future version.
    Validators should use the sheets_service parameter passed to their validate() method.
    
    This function exists only for backward compatibility with old code that
    calls get_sheets_service() without parameters. It cannot work without
    credentials being set up elsewhere.
    
    Raises:
        NotImplementedError: Always, as this function requires refactoring
    """
    raise NotImplementedError(
        "get_sheets_service() is deprecated. "
        "Use the sheets_service parameter passed to your validator's validate() method instead."
    )

__all__ = [
    "get_gspread_client",
    "clear_service_cache",
    "get_sheets_service",
]
