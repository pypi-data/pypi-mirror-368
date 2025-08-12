"""Legacy checker module with backward compatibility.

This module maintains backward compatibility for existing code while internally
using the new modular structure. All functions are re-exported from their
new locations to ensure existing imports continue to work.
"""

# Import from new gspread-focused auth module
from urarovite.auth.google_sheets import (
    get_gspread_client,
    clear_client_cache as clear_service_cache,
)
from urarovite.utils.sheets import (
    # Extracting sheet IDs and segments
    extract_sheet_id,
    split_segments,
    strip_outer_single_quotes,
    extract_sheet_and_range,
    parse_tab_token,
    parse_referenced_tabs,
    # Column letter/index conversions
    col_index_to_letter,
    letter_to_col_index,
    # Sheet data access (updated to use new auth)
    fetch_sheet_tabs,
    get_sheet_values,
    update_sheet_values,
)

# Legacy auth and utils modules are still available for direct import
from urarovite.checker import auth, utils

__all__ = [
    # auth.py functions (mapped to new gspread-focused auth module)
    "get_gspread_client",
    "clear_service_cache",
    # utils.py functions (mapped to new utils module)
    # Extracting sheet IDs and segments
    "extract_sheet_id",
    "split_segments",
    "strip_outer_single_quotes",
    "extract_sheet_and_range",
    "parse_tab_token",
    "parse_referenced_tabs",
    # Column letter/index conversions
    "col_index_to_letter",
    "letter_to_col_index",
    # Sheet data access
    "fetch_sheet_tabs",
    "get_sheet_values",
    "update_sheet_values",
    # Legacy modules for direct access
    "auth",
    "utils",
]
