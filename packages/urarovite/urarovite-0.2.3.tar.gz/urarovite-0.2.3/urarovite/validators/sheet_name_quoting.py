"""
Sheet Name Quoting Validator.

This validator ensures that all sheet names in verification_field_ranges are
properly quoted with single quotes when they contain spaces or special characters.

Goal:
Verify that each range segment starts with a sheet name wrapped in single quotes
following the pattern 'SheetName'! to ensure proper A1 notation parsing.

Why:
Sheet names with spaces or special characters must be quoted in A1 notation to
avoid parsing errors and ensure consistent behavior across different systems.

Examples:
- Valid: 'March 2025'!A2:A91
- Invalid: March 2025!A2:A91 (missing quotes)
"""

from __future__ import annotations
import re
from typing import Any, Dict, List, Union
import pandas as pd

from urarovite.validators.base import BaseValidator
from urarovite.core.exceptions import ValidationError
from urarovite.utils.sheets import split_segments


class SheetNameQuotingValidator(BaseValidator):
    """Validator that ensures proper sheet name quoting in verification ranges."""
    
    def __init__(self) -> None:
        super().__init__(
            validator_id="sheet_name_quoting",
            name="Sheet Name Quoting",
            description=(
                "Ensures all sheet names in verification ranges are properly "
                "quoted with single quotes (e.g., 'Sheet Name'!A1:B2)"
            ),
        )
    
    # Regular expression for properly quoted sheet names
    # Matches: 'SheetName'! or 'SheetName'$ (for whole sheet references)
    SHEET_PREFIX_RE = re.compile(r"^'[^']+'(!|$)")
    
    def _segment_is_quoted(self, segment: str) -> bool:
        """Check if a segment has properly quoted sheet name."""
        return bool(self.SHEET_PREFIX_RE.match(segment))
    
    def validate(
        self, sheets_service: Any, sheet_id: str, mode: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Execute sheet name quoting validation.
        
        Args:
            sheets_service: Google Sheets API service instance (not used)
            sheet_id: Not used for this validator
            mode: Either "fix" (not applicable) or "flag" (report only)
            **kwargs: Must contain either 'row' with data or 'ranges_str' directly
            
        Returns:
            Dict with validation results
        """
        # Extract ranges string from parameters
        ranges_str = ""
        
        if "ranges_str" in kwargs:
            # Direct string input
            ranges_str = kwargs["ranges_str"]
        elif "row" in kwargs:
            # Extract from row data
            row = kwargs["row"]
            if row is None:
                raise ValidationError("Row data is required for this validator")
            
            field = kwargs.get("field", "verification_field_ranges")
            ranges_str = str(row.get(field, ""))
        else:
            raise ValidationError(
                "Either 'row' or 'ranges_str' parameter is required"
            )
        
        # Parse segments and check quoting
        segments = split_segments(ranges_str)
        failing_segments = [s for s in segments if not self._segment_is_quoted(s)]
        
        # Determine overall success
        ok = len(failing_segments) == 0
        
        return {
            "validator": self.id,
            "ok": ok,
            "total_segments": len(segments),
            "failing_segments": failing_segments,
            "original": ranges_str,
        }


# Convenience function for backward compatibility
def run(
    row_or_str: Union[str, Dict[str, Any], "pd.Series"], 
    field: str = "verification_field_ranges"
) -> Dict[str, Any]:
    """
    Execute sheet name quoting check.
    This function provides backward compatibility with the original checker1 interface.
    
    Args:
        row_or_str: Either a string with ranges, a dict, or pandas Series with data
        field: Field name to extract ranges from (when row_or_str is not a string)
        
    Returns:
        Dict with validation results
    """
    validator = SheetNameQuotingValidator()
    
    try:
        if isinstance(row_or_str, str):
            # Direct string input
            return validator.validate(
                sheets_service=None,
                sheet_id="",
                mode="flag",
                ranges_str=row_or_str
            )
        else:
            # Row data input (pandas Series or dict)
            return validator.validate(
                sheets_service=None,
                sheet_id="",
                mode="flag",
                row=row_or_str,
                field=field
            )
    except Exception as e:
        # Return error in the expected format
        return {
            "validator": validator.id,
            "ok": False,
            "total_segments": 0,
            "failing_segments": [],
            "original": "",
            "error": f"validation_error: {str(e)}",
        }


# Backwards compatible helper name
run_detailed = run
