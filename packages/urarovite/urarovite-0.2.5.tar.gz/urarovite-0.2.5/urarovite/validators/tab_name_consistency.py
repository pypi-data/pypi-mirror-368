"""
Tab Name Consistency Validator.

This validator checks that tab names referenced in verification_field_ranges
exist (with exact casing) in BOTH input and output Google Sheets.

Goal:
Ensure that all tabs referenced in verification ranges are present and
correctly named in both input and output spreadsheets.

Why:
If verification ranges reference tabs that don't exist or have incorrect
casing, the validation process will fail. This validator catches such
issues early.
"""

from __future__ import annotations
import re
from typing import Any, Dict, List, Union
import pandas as pd

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.exceptions import ValidationError
from urarovite.utils.sheets import fetch_sheet_tabs


class TabNameConsistencyValidator(BaseValidator):
    """Validator that checks tab name consistency between input and output spreadsheets."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="tab_name_consistency",
            name="Tab Name Consistency",
            description=(
                "Ensures tab names referenced in verification ranges exist "
                "with exact casing in both input and output spreadsheets"
            ),
        )

    # Regular expressions for parsing
    _ID_RE = re.compile(r"/d/([a-zA-Z0-9-_]+)")
    _DEF_SPLIT_RE = re.compile(r"@@")

    def _extract_sheet_id(self, url: str | None) -> str | None:
        """Extract sheet ID from Google Sheets URL."""
        if not url:
            return None
        m = self._ID_RE.search(url)
        return m.group(1) if m else None

    def _parse_referenced_tabs(self, ranges_str: str | None) -> List[str]:
        """Parse tab names from verification_field_ranges string."""
        if not ranges_str:
            return []

        segments = [
            s.strip() for s in self._DEF_SPLIT_RE.split(ranges_str) if s.strip()
        ]
        referenced: List[str] = []
        seen = set()

        for seg in segments:
            before_bang = seg.split("!", 1)[0].strip()
            # Remove quotes if present (e.g. 'Sheet1' -> Sheet1)
            tab_name = before_bang.strip("'")
            if tab_name not in seen:
                seen.add(tab_name)
                referenced.append(tab_name)

        return referenced

    def _create_case_map(self, tabs: List[str]) -> Dict[str, str]:
        """Create lowercase to actual case mapping for tab names."""
        cmap: Dict[str, str] = {}
        for tab in tabs:
            lc = tab.lower()
            if lc not in cmap:
                cmap[lc] = tab
        return cmap

    def validate(
        self, sheets_service: Any, sheet_id: str, mode: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Execute tab name consistency validation.

        Args:
            sheets_service: Google Sheets API service instance
            sheet_id: Not used for this validator (uses URLs from row data)
            mode: Either "fix" (not applicable) or "flag" (report only)
            **kwargs: Must contain 'row' with pandas Series or dict containing the data

        Returns:
            Dict with validation results
        """
        # Extract parameters
        row = kwargs.get("row")
        if row is None:
            # Return empty result if no row data provided
            result = ValidationResult()
            result.details["missing_in_input"] = []
            result.details["missing_in_output"] = []
            result.details["case_mismatches_input"] = []
            result.details["case_mismatches_output"] = []
            result.set_automated_log("No issues found")
            return result.to_dict()

        input_col = kwargs.get("input_col", "input_sheet_url")
        output_col = kwargs.get("output_col", "example_output_sheet_url")
        ranges_col = kwargs.get("ranges_col", "verification_field_ranges")

        # Extract data from row
        input_url = row.get(input_col, None)
        output_url = row.get(output_col, None)
        ranges_str = row.get(ranges_col, "")

        # Parse referenced tabs and extract sheet IDs
        referenced_tabs = self._parse_referenced_tabs(ranges_str)
        input_id = self._extract_sheet_id(input_url)
        output_id = self._extract_sheet_id(output_url)

        # Fetch sheet metadata
        input_meta = fetch_sheet_tabs(sheets_service, input_id)
        output_meta = fetch_sheet_tabs(sheets_service, output_id)

        # Check for basic errors
        errors: List[str] = []
        if not referenced_tabs:
            errors.append("no_verification_ranges")
        if not input_meta["accessible"]:
            errors.append("input_inaccessible")
        if not output_meta["accessible"]:
            errors.append("output_inaccessible")

        # Initialize result lists
        missing_in_input: List[str] = []
        missing_in_output: List[str] = []
        case_mismatch_input: List[Dict[str, str]] = []
        case_mismatch_output: List[Dict[str, str]] = []

        # Perform consistency checks if both sheets are accessible
        if input_meta["accessible"] and output_meta["accessible"] and referenced_tabs:
            input_tabs = input_meta["tabs"]
            output_tabs = output_meta["tabs"]

            # Create case-insensitive lookups
            input_lower = set(t.lower() for t in input_tabs)
            output_lower = set(t.lower() for t in output_tabs)
            input_case_map = self._create_case_map(input_tabs)
            output_case_map = self._create_case_map(output_tabs)

            # Create exact case lookups
            input_set = set(input_tabs)
            output_set = set(output_tabs)

            # Check each referenced tab
            for tab in referenced_tabs:
                # Check input sheet
                if tab in input_set:
                    # Exact match - good
                    pass
                elif tab.lower() in input_lower:
                    # Case mismatch
                    actual = input_case_map[tab.lower()]
                    case_mismatch_input.append({"requested": tab, "actual": actual})
                else:
                    # Missing entirely
                    missing_in_input.append(tab)

                # Check output sheet
                if tab in output_set:
                    # Exact match - good
                    pass
                elif tab.lower() in output_lower:
                    # Case mismatch
                    actual = output_case_map[tab.lower()]
                    case_mismatch_output.append({"requested": tab, "actual": actual})
                else:
                    # Missing entirely
                    missing_in_output.append(tab)

        # Determine overall success
        ok = (
            len(errors) == 0
            and not missing_in_input
            and not missing_in_output
            and not case_mismatch_input
            and not case_mismatch_output
        )

        result = ValidationResult()
        
        # Add errors if any
        for error in errors:
            result.add_error(error)
            result.add_issue()  # Each error counts as an issue
        
        # Store detailed information
        result.details["sheets"] = {
            "input": {
                "id": input_id,
                "accessible": input_meta["accessible"],
                "tabs": input_meta["tabs"],
                "error": input_meta["error"],
            },
            "output": {
                "id": output_id,
                "accessible": output_meta["accessible"],
                "tabs": output_meta["tabs"],
                "error": output_meta["error"],
            },
        }
        result.details["referenced_tabs"] = referenced_tabs
        result.details["missing_in_input"] = missing_in_input
        result.details["missing_in_output"] = missing_in_output
        result.details["case_mismatches_input"] = case_mismatch_input
        result.details["case_mismatches_output"] = case_mismatch_output
        
        # Generate automated log
        issues = []
        if missing_in_input or missing_in_output:
            all_missing = missing_in_input + missing_in_output
            issues.append(f"Missing tabs: {all_missing}")
        if case_mismatch_input or case_mismatch_output:
            all_mismatches = case_mismatch_input + case_mismatch_output
            issues.append(f"Tab name case mismatches: {all_mismatches}")
        
        if issues:
            total_issues = len(missing_in_input) + len(missing_in_output) + len(case_mismatch_input) + len(case_mismatch_output)
            result.add_issue(total_issues)
            result.set_automated_log("; ".join(issues))
        else:
            result.set_automated_log("No issues found")
        
        return result.to_dict()


# Convenience function for backward compatibility
def run(
    row: Union[Dict[str, Any], "pd.Series"],
    input_col: str = "input_sheet_url",
    output_col: str = "example_output_sheet_url",
    ranges_col: str = "verification_field_ranges",
) -> Dict[str, Any]:
    """
    Execute tab name consistency check.
    This function provides backward compatibility with the original checker3 interface.
    """
    # Import here to avoid circular imports
    from urarovite.auth.google_sheets import get_gspread_client

    # Create a mock sheets service (we use fetch_sheet_tabs directly)
    # which handles its own service creation
    validator = TabNameConsistencyValidator()

    try:
        # Get a service for the validator (though fetch_sheet_tabs creates its own)
        service = get_gspread_client()

        return validator.validate(
            sheets_service=service,
            sheet_id="",  # Not used by this validator
            mode="flag",
            row=row,
            input_col=input_col,
            output_col=output_col,
            ranges_col=ranges_col,
        )
    except Exception as e:
        # Return error in ValidationResult format
        result = ValidationResult()
        result.add_error(f"validation_error: {str(e)}")
        result.details["sheets"] = {
            "input": {"id": None, "accessible": False, "tabs": [], "error": str(e)},
            "output": {
                "id": None,
                "accessible": False,
                "tabs": [],
                "error": str(e),
            },
        }
        result.details["referenced_tabs"] = []
        result.details["missing_in_input"] = []
        result.details["missing_in_output"] = []
        result.details["case_mismatches_input"] = []
        result.details["case_mismatches_output"] = []
        result.set_automated_log("No issues found")
        return result.to_dict()
