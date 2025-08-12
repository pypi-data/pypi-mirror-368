"""Google Sheets utilities for data access and manipulation.

This module provides utilities for working with Google Sheets, including
URL parsing, range handling, and data retrieval. Enhanced from the original
checker/utils.py with better error handling and additional functionality.
"""

import re
from typing import Any, Dict, List, Optional, Tuple

from urarovite.core.exceptions import SheetAccessError

# Regular expressions for parsing
SHEET_ID_RE = re.compile(r"/d/([a-zA-Z0-9-_]+)")
SEGMENT_SEPARATOR = "@@"
COL_RE = r"[A-Z]+"
ROW_RE = r"[0-9]+"


def extract_sheet_id(url: str | None) -> Optional[str]:
    """Extract spreadsheet ID from a Google Sheets URL.
    
    Args:
        url: Google Sheets URL
        
    Returns:
        Spreadsheet ID if found, None otherwise
        
    Example:
        >>> extract_sheet_id("https://docs.google.com/spreadsheets/d/1ABC123.../edit")
        "1ABC123..."
    """
    if not url:
        return None
    match = SHEET_ID_RE.search(url)
    return match.group(1) if match else None


def split_segments(ranges_str: str | None, sep: str = SEGMENT_SEPARATOR) -> List[str]:
    """Split the verification_field_ranges string into cleaned segments.
    
    Args:
        ranges_str: String containing range segments separated by separator
        sep: Separator string (default: "@@")
        
    Returns:
        List of cleaned range segments
    """
    if not ranges_str:
        return []
    return [s.strip() for s in ranges_str.split(sep) if s.strip()]


def strip_outer_single_quotes(token: str) -> str:
    """Remove outer single quotes from a token if present.
    
    Args:
        token: Token that may have outer single quotes
        
    Returns:
        Token with outer quotes removed
    """
    token = token.strip()
    start_quote = 1 if token.startswith("'") else 0
    end_quote = 1 if token.endswith("'") else 0
    token = token[start_quote : len(token) - end_quote]
    return token


def extract_sheet_and_range(segment: str) -> Tuple[str, Optional[str]]:
    """Split a segment into sheet token and range part.
    
    Args:
        segment: Range segment (e.g., "Sheet1!A1:B10" or "Sheet1")
        
    Returns:
        Tuple of (sheet_name, range) where range is None if whole sheet
    """
    if "!" not in segment:
        return segment, None
    sheet, rng = segment.split("!", 1)
    return sheet, rng.strip()


def parse_tab_token(segment: str) -> str:
    """Parse tab name from a range segment.
    
    Args:
        segment: Range segment
        
    Returns:
        Clean tab name with quotes removed
    """
    sheet_token, _ = extract_sheet_and_range(segment)
    return strip_outer_single_quotes(sheet_token.strip())


def parse_referenced_tabs(ranges_str: str | None) -> List[str]:
    """Return unique tab names in order of first appearance from ranges string.
    
    Args:
        ranges_str: String containing range segments
        
    Returns:
        List of unique tab names in order of appearance
    """
    seen = set()
    ordered: List[str] = []
    for seg in split_segments(ranges_str):
        tab = parse_tab_token(seg)
        if tab not in seen:
            seen.add(tab)
            ordered.append(tab)
    return ordered


# Column letter/index conversions


def col_index_to_letter(idx: int) -> str:
    """Convert column index (0-based) to Excel-style letter.
    
    Args:
        idx: 0-based column index
        
    Returns:
        Column letter(s) (e.g., 0 -> "A", 25 -> "Z", 26 -> "AA")
    """
    s = ""
    while idx >= 0:
        s = chr(idx % 26 + 65) + s
        idx = idx // 26 - 1
    return s


def letter_to_col_index(letters: str) -> int:
    """Convert Excel-style column letter(s) to 0-based index.
    
    Args:
        letters: Column letter(s) (e.g., "A", "Z", "AA")
        
    Returns:
        0-based column index
    """
    v = 0
    for c in letters:
        v = v * 26 + (ord(c) - 64)
    return v - 1


# Google Sheets data access


def fetch_sheet_tabs(sheets_service: Any, spreadsheet_id: str | None) -> Dict[str, Any]:
    """Fetch tab (sheet) titles using Google Sheets API.
    
    Args:
        sheets_service: Google Sheets API service instance
        spreadsheet_id: ID of the spreadsheet
        
    Returns:
        Dict with keys: accessible, tabs, error
    """
    if not spreadsheet_id:
        return {"accessible": False, "tabs": [], "error": "missing_or_malformed_url"}
    
    try:
        # Get sheet metadata (list of tabs)
        sheet_metadata = (
            sheets_service.spreadsheets()
            .get(spreadsheetId=spreadsheet_id, fields="sheets.properties.title")
            .execute()
        )
        
        tabs = [
            sheet["properties"]["title"] for sheet in sheet_metadata.get("sheets", [])
        ]
        return {"accessible": True, "tabs": tabs, "error": None}
        
    except Exception as e:
        error_msg = str(e)
        if "HttpError 403" in error_msg or "HttpError 404" in error_msg:
            return {"accessible": False, "tabs": [], "error": "forbidden_or_not_found"}
        return {
            "accessible": False,
            "tabs": [],
            "error": f"request_exception:{e.__class__.__name__}",
        }


def get_sheet_values(
    sheets_service: Any, 
    spreadsheet_id: str | None, 
    range_name: str
) -> Dict[str, Any]:
    """Get values from a sheet range using Google Sheets API.
    
    Args:
        sheets_service: Google Sheets API service instance
        spreadsheet_id: The ID of the spreadsheet
        range_name: The A1 notation range (e.g., 'Sheet1!A1:Z1000')
        
    Returns:
        Dict with keys: success, values, rows, cols, error
        - rows: number of rows that contain at least one non-empty cell
        - cols: number of columns that contain at least one non-empty cell
        
    Raises:
        SheetAccessError: If unable to access the sheet
    """
    if not spreadsheet_id:
        return {
            "success": False,
            "values": [],
            "rows": 0,
            "cols": 0,
            "error": "missing_spreadsheet_id",
        }
    
    try:
        result = (
            sheets_service.spreadsheets()
            .values()
            .get(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueRenderOption="UNFORMATTED_VALUE",
            )
            .execute()
        )
        
        values = result.get("values", [])
        
        if not values:
            return {"success": True, "values": [], "rows": 0, "cols": 0, "error": None}
        
        # Find the actual used bounds (last row and column with data)
        used_rows = 0
        used_cols = 0
        
        for row_idx, row in enumerate(values):
            # Check if this row has any non-empty cells
            has_data = any(cell != "" and cell is not None for cell in row)
            if has_data:
                used_rows = row_idx + 1  # 1-based
                # Update max columns seen
                used_cols = max(used_cols, len(row))
        
        # Also check for trailing columns in any row that might extend beyond
        if values:
            max_col_in_any_row = max(len(row) for row in values)
            # Find the rightmost column with actual data
            for col_idx in range(max_col_in_any_row - 1, -1, -1):
                has_data_in_col = any(
                    col_idx < len(row)
                    and row[col_idx] != ""
                    and row[col_idx] is not None
                    for row in values
                )
                if has_data_in_col:
                    used_cols = max(used_cols, col_idx + 1)  # 1-based
                    break
        
        return {
            "success": True,
            "values": values,
            "rows": used_rows,
            "cols": used_cols,
            "error": None,
        }
        
    except Exception as e:
        error_msg = str(e)
        if "HttpError 403" in error_msg or "HttpError 404" in error_msg:
            return {
                "success": False,
                "values": [],
                "rows": 0,
                "cols": 0,
                "error": "forbidden_or_not_found",
            }
        return {
            "success": False,
            "values": [],
            "rows": 0,
            "cols": 0,
            "error": f"request_exception:{e.__class__.__name__}",
        }


def update_sheet_values(
    sheets_service: Any,
    spreadsheet_id: str,
    range_name: str,
    values: List[List[Any]],
    value_input_option: str = "RAW"
) -> Dict[str, Any]:
    """Update values in a sheet range.
    
    Args:
        sheets_service: Google Sheets API service instance
        spreadsheet_id: The ID of the spreadsheet
        range_name: The A1 notation range to update
        values: 2D array of values to write
        value_input_option: How to interpret input data ("RAW" or "USER_ENTERED")
        
    Returns:
        Dict with update results or error information
        
    Raises:
        SheetAccessError: If unable to update the sheet
    """
    try:
        body = {
            "values": values
        }
        
        result = (
            sheets_service.spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption=value_input_option,
                body=body
            )
            .execute()
        )
        
        return {
            "success": True,
            "updated_cells": result.get("updatedCells", 0),
            "updated_rows": result.get("updatedRows", 0),
            "updated_columns": result.get("updatedColumns", 0),
            "error": None
        }
        
    except Exception as e:
        error_msg = str(e)
        if "HttpError 403" in error_msg:
            raise SheetAccessError(f"Permission denied: {error_msg}")
        elif "HttpError 404" in error_msg:
            raise SheetAccessError(f"Sheet not found: {error_msg}")
        else:
            raise SheetAccessError(f"Failed to update sheet: {error_msg}")
