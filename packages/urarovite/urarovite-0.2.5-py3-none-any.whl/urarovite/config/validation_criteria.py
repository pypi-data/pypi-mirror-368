"""Validation criteria definitions for the Urarovite library.

This module defines all available validation criteria that can be applied
to Google Sheets data. Each criterion has an ID, name, and description.
"""

from typing import TypedDict


class ValidationCriterion(TypedDict):
    """Type definition for a validation criterion."""

    id: str
    name: str
    description: str
    supports_fix: bool
    supports_flag: bool


# All available validation criteria
VALIDATION_CRITERIA: list[ValidationCriterion] = [
    # Data Quality Validators
    {
        "id": "empty_cells",
        "name": "Fix Empty Cells",
        "description": "Identifies and optionally fills empty cells with default values",
        "supports_fix": True,
        "supports_flag": True,
    },
    {
        "id": "duplicate_rows",
        "name": "Remove Duplicate Rows",
        "description": "Finds and optionally removes duplicate rows based on all columns",
        "supports_fix": True,
        "supports_flag": True,
    },
    {
        "id": "inconsistent_formatting",
        "name": "Fix Inconsistent Formatting",
        "description": "Standardizes text formatting (case, whitespace, etc.)",
        "supports_fix": True,
        "supports_flag": True,
    },
    {
        "id": "missing_required_fields",
        "name": "Check Required Fields",
        "description": "Validates that required fields are not empty",
        "supports_fix": False,
        "supports_flag": True,
    },
    {
        "id": "tab_names",
        "name": "Fix Tab Names",
        "description": "Validates that tab names contain only allowed characters and fixes illegal characters",
        "supports_fix": True,
        "supports_flag": True,
    },

    # Format Validation
    {
        "id": "invalid_emails",
        "name": "Validate Email Addresses",
        "description": "Checks email format and flags invalid emails",
        "supports_fix": False,
        "supports_flag": True,
    },
    {
        "id": "invalid_phone_numbers",
        "name": "Validate Phone Numbers",
        "description": "Validates phone number formats and consistency",
        "supports_fix": True,
        "supports_flag": True,
    },
    {
        "id": "invalid_dates",
        "name": "Validate Date Formats",
        "description": "Checks and standardizes date formats",
        "supports_fix": True,
        "supports_flag": True,
    },
    {
        "id": "invalid_urls",
        "name": "Validate URLs",
        "description": "Validates URL format and accessibility",
        "supports_fix": False,
        "supports_flag": True,
    },
    {
        "id": "invalid_verification_ranges",
        "name": "Fix Verification Ranges",
        "description": "Validates and fixes malformed A1 notation ranges",
        "supports_fix": True,
        "supports_flag": True,
    },
    # Spreadsheet Range Validators
    {
        "id": "sheet_name_quoting",
        "name": "Sheet Name Quoting",
        "description": (
            "Ensures all sheet names in verification ranges are properly "
            "quoted with single quotes (e.g., 'Sheet Name'!A1:B2)"
        ),
        "supports_fix": False,
        "supports_flag": True,
    },
    # Spreadsheet Comparison Validators
    {
        "id": "tab_name_consistency",
        "name": "Tab Name Consistency",
        "description": (
            "Ensures tab names referenced in verification ranges exist "
            "with exact casing in both input and output spreadsheets"
        ),
        "supports_fix": False,
        "supports_flag": True,
    },
    {
        "id": "open_ended_ranges",
        "name": "Open-Ended Ranges Detection",
        "description": (
            "Detects unbounded A1 notations in verification ranges that "
            "can cause flaky verification (whole columns, rows, half-bounded ranges)"
        ),
        "supports_fix": False,
        "supports_flag": True,
    },
    {
        "id": "sheet_accessibility",
        "name": "Check Sheet Accessibility",
        "description": "Validates that Google Sheets URLs are accessible",
        "supports_fix": False,
        "supports_flag": True,
    },
    {
        "id": "identical_outside_ranges",
        "name": "Identical Outside Ranges",
        "description": (
            "Ensures input and output spreadsheets are identical except "
            "in specified verification ranges"
        ),
        "supports_fix": False,
        "supports_flag": True,
    },
]
