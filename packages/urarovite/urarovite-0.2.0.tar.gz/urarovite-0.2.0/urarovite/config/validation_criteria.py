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
        "description": (
            "Identifies and optionally fills empty cells with default values"
        ),
        "supports_fix": True,
        "supports_flag": True,
    },
    {
        "id": "duplicate_rows",
        "name": "Remove Duplicate Rows",
        "description": (
            "Finds and optionally removes duplicate rows based on all columns"
        ),
        "supports_fix": True,
        "supports_flag": True,
    },
    {
        "id": "inconsistent_formatting",
        "name": "Fix Inconsistent Formatting",
        "description": ("Standardizes text formatting (case, whitespace, etc.)"),
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
    # Format Validation
    {
        "id": "invalid_emails",
        "name": "Validate Email Addresses",
        "description": ("Checks email format and optionally flags invalid emails"),
        "supports_fix": False,
        "supports_flag": True,
    },
    {
        "id": "invalid_phone_numbers",
        "name": "Validate Phone Numbers",
        "description": ("Validates phone number formats and consistency"),
        "supports_fix": False,
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
    # Data Type Validation
    {
        "id": "numeric_validation",
        "name": "Validate Numeric Data",
        "description": (
            "Ensures numeric fields contain valid numbers within expected ranges"
        ),
        "supports_fix": False,
        "supports_flag": True,
    },
    {
        "id": "text_length_validation",
        "name": "Validate Text Length",
        "description": (
            "Checks text fields against minimum/maximum length requirements"
        ),
        "supports_fix": False,
        "supports_flag": True,
    },
    # Business Rules
    {
        "id": "data_consistency",
        "name": "Check Data Consistency",
        "description": "Validates relationships between related fields",
        "supports_fix": False,
        "supports_flag": True,
    },
    {
        "id": "reference_validation",
        "name": "Validate References",
        "description": "Checks that referenced IDs exist in related sheets/ranges",
        "supports_fix": False,
        "supports_flag": True,
    },
]
