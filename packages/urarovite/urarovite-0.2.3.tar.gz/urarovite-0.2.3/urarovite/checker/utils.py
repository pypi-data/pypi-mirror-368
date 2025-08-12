"""Legacy utilities module - compatibility wrapper.

This module provides backward compatibility for existing code that imports
from urarovite.checker.utils. All functionality is now provided by the
new urarovite.utils.sheets module with enhanced features.

DEPRECATED: Use urarovite.utils.sheets instead for new code.
"""

# Re-export all functions from new utils module for backward compatibility
from urarovite.utils.sheets import (
    # URL and range parsing
    extract_sheet_id,
    split_segments,
    strip_outer_single_quotes,
    extract_sheet_and_range,
    parse_tab_token,
    parse_referenced_tabs,
    # Column conversions
    col_index_to_letter,
    letter_to_col_index,
    # Sheet data access
    get_sheet_values as _new_get_sheet_values,
    update_sheet_values,
    # Constants
    SHEET_ID_RE,
    SEGMENT_SEPARATOR,
    COL_RE,
    ROW_RE,
)

# Special handling for fetch_sheet_tabs to maintain legacy signature
# OAuth functionality removed - using gspread only now
from urarovite.utils.sheets import fetch_sheet_tabs as _new_fetch_sheet_tabs
from typing import Dict, Any


def fetch_sheet_tabs(spreadsheet_id: str | None) -> Dict[str, Any]:
    """Legacy wrapper for fetch_sheet_tabs that uses OAuth service.

    This maintains backward compatibility with the legacy API that doesn't
    require passing a sheets_service parameter.
    """
    try:
        service = get_oauth_sheets_service()
        return _new_fetch_sheet_tabs(service, spreadsheet_id)
    except Exception as e:
        return {
            "accessible": False,
            "tabs": [],
            "error": f"auth_error:{e.__class__.__name__}",
        }


def get_sheet_values(spreadsheet_id: str | None, range_name: str) -> Dict[str, Any]:
    """Legacy wrapper for get_sheet_values that uses OAuth service.

    This maintains backward compatibility with the legacy API that doesn't
    require passing a sheets_service parameter.

    Args:
        spreadsheet_id: The ID of the spreadsheet
        range_name: The A1 notation range (e.g., 'Sheet1!A1:Z1000')

    Returns:
        Dict with keys: success, values, rows, cols, error
    """
    try:
        service = get_oauth_sheets_service()
        return _new_get_sheet_values(service, spreadsheet_id, range_name)
    except Exception as e:
        return {
            "success": False,
            "values": [],
            "rows": 0,
            "cols": 0,
            "error": f"auth_error:{e.__class__.__name__}",
        }


__all__ = [
    # URL and range parsing
    "extract_sheet_id",
    "split_segments",
    "strip_outer_single_quotes",
    "extract_sheet_and_range",
    "parse_tab_token",
    "parse_referenced_tabs",
    # Column conversions
    "col_index_to_letter",
    "letter_to_col_index",
    # Sheet data access
    "fetch_sheet_tabs",
    "get_sheet_values",
    "update_sheet_values",
    # Constants
    "SHEET_ID_RE",
    "SEGMENT_SEPARATOR",
    "COL_RE",
    "ROW_RE",
]
