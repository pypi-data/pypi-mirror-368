"""Data quality validators for common spreadsheet issues.

This module implements validators for basic data quality issues such as
empty cells, duplicate rows, and inconsistent formatting.
"""

import re
from typing import Any, Dict, List, Set

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.exceptions import ValidationError

ILLEGAL_CHARS = ["\\", "/", "?", "*", "[", "]"]


class TabNameValidator(BaseValidator):
    """Validator for checking and fixing tab names."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="tab_names",
            name="Fix Tab Names",
            description="Validates that tab names contain only allowed characters and fixes illegal characters",
        )

    def validate(
        self,
        sheets_service: Any,
        sheet_id: str,
        mode: str,
        replacement_char: str = "_",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Check for and optionally fix tab name characters.

        Args:
            sheets_service: Google Sheets API service instance
            sheet_id: ID of the spreadsheet to validate
            mode: Either "fix" (fix tab names) or "flag" (report only)
            replacement_char: Character to replace illegal characters with (default: "_")

        Returns:
            Dict with validation results including mapping of changes
        """
        result = ValidationResult()

        try:
            # Get spreadsheet metadata to access tab information
            spreadsheet_data = (
                sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            )

            sheets = spreadsheet_data.get("sheets", [])
            if not sheets:
                result.add_error("No sheets found in spreadsheet")
                return result.to_dict()

            # Collect all existing tab names for collision detection
            all_tab_names = {sheet["properties"]["title"] for sheet in sheets}

            tab_issues = []
            name_mapping = {}
            used_names = set(
                all_tab_names
            )  # Track all names (original + new) to avoid collisions

            # Check each tab for illegal characters
            for sheet in sheets:
                sheet_properties = sheet["properties"]
                tab_name = sheet_properties["title"]
                sheet_id_num = sheet_properties["sheetId"]

                # Check for illegal characters: \ / ? * [ ]
                has_illegal_chars = any(char in tab_name for char in ILLEGAL_CHARS)

                if has_illegal_chars:
                    # Create a cleaned version
                    fixed_name = self._clean_tab_name(tab_name, replacement_char)

                    # Handle collisions by appending numbers
                    final_name = self._resolve_name_collision(fixed_name, used_names)

                    # Add to used names to prevent future collisions
                    used_names.add(final_name)

                    # Create mapping entry
                    name_mapping[tab_name] = final_name

                    # Record detected illegal characters
                    detected_chars = [
                        char for char in ILLEGAL_CHARS if char in tab_name
                    ]

                    tab_issues.append(
                        {
                            "sheet_id": sheet_id_num,
                            "original_name": tab_name,
                            "fixed_name": final_name,
                            "illegal_chars": detected_chars,
                        }
                    )

            # Record results
            if tab_issues:
                if mode == "fix":
                    # Update tab names
                    self._update_tab_names(sheets_service, sheet_id, tab_issues)
                    result.add_fix(len(tab_issues))
                    result.details["fixed_tabs"] = tab_issues
                    result.details["name_mapping"] = name_mapping
                else:
                    result.add_issue(len(tab_issues))
                    result.details["tab_issues"] = tab_issues
                    result.details["proposed_mapping"] = name_mapping

        except ValidationError:
            raise
        except Exception as e:
            result.add_error(f"Unexpected error: {str(e)}")

        return result.to_dict()

    def _clean_tab_name(self, tab_name: str, replacement_char: str) -> str:
        """Clean a tab name by replacing illegal characters.

        Args:
            tab_name: Original tab name
            replacement_char: Character to replace illegal characters with

        Returns:
            Cleaned tab name
        """
        fixed_name = tab_name

        # Replace each illegal character with replacement character
        for char in ILLEGAL_CHARS:
            fixed_name = fixed_name.replace(char, replacement_char)

        # Remove multiple consecutive replacement characters
        fixed_name = re.sub(
            f"{re.escape(replacement_char)}+", replacement_char, fixed_name
        )

        # Remove leading/trailing replacement characters
        fixed_name = fixed_name.strip(replacement_char)

        # Ensure name isn't empty
        if not fixed_name:
            fixed_name = "Sheet"

        return fixed_name

    def _resolve_name_collision(self, proposed_name: str, used_names: Set[str]) -> str:
        """Resolve name collisions by appending numbers.

        Args:
            proposed_name: The proposed cleaned name
            used_names: Set of already used names

        Returns:
            Final name that doesn't collide with existing names
        """
        if proposed_name not in used_names:
            return proposed_name

        # Try appending numbers until we find an unused name
        counter = 1
        while f"{proposed_name}_{counter}" in used_names:
            counter += 1

        return f"{proposed_name}_{counter}"

    def _update_tab_names(
        self, sheets_service: Any, sheet_id: str, tab_issues: List[Dict[str, Any]]
    ) -> None:
        """Update tab names to fix illegal characters.

        Args:
            sheets_service: Google Sheets API service instance
            sheet_id: ID of the spreadsheet
            tab_issues: List of tab issues with original and fixed names

        Raises:
            ValidationError: If unable to update tab names
        """
        try:
            requests = []

            for issue in tab_issues:
                # Create a request to update the sheet properties
                requests.append(
                    {
                        "updateSheetProperties": {
                            "properties": {
                                "sheetId": issue["sheet_id"],
                                "title": issue["fixed_name"],
                            },
                            "fields": "title",
                        }
                    }
                )

            # Execute batch update
            if requests:
                body = {"requests": requests}
                sheets_service.spreadsheets().batchUpdate(
                    spreadsheetId=sheet_id, body=body
                ).execute()

        except Exception as e:
            raise ValidationError(f"Failed to update tab names: {str(e)}")


class EmptyCellsValidator(BaseValidator):
    """Validator for identifying and fixing empty cells."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="empty_cells",
            name="Fix Empty Cells",
            description="Identifies and optionally fills empty cells with default values",
        )

    def validate(
        self,
        sheets_service: Any,
        sheet_id: str,
        mode: str,
        fill_value: str = "",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Check for and optionally fix empty cells.

        Args:
            sheets_service: Google Sheets API service instance
            sheet_id: ID of the spreadsheet to validate
            mode: Either "fix" (fill empty cells) or "flag" (report only)
            fill_value: Value to use when filling empty cells (default: "")

        Returns:
            Dict with validation results
        """
        result = ValidationResult()

        try:
            # Get all sheet data
            data = self._get_all_sheet_data(sheets_service, sheet_id)

            if not data:
                result.add_error("Sheet is empty")
                return result.to_dict()

            empty_cells = []
            fixed_data = []

            # Check each row for empty cells
            for row_idx, row in enumerate(data):
                fixed_row = []
                for col_idx, cell in enumerate(row):
                    if cell == "" or cell is None:
                        empty_cells.append(
                            (row_idx + 1, col_idx + 1)
                        )  # 1-based indexing
                        if mode == "fix":
                            fixed_row.append(fill_value)
                        else:
                            fixed_row.append(cell)
                    else:
                        fixed_row.append(cell)
                fixed_data.append(fixed_row)

            # Record results
            if empty_cells:
                if mode == "fix":
                    # Update the sheet with fixed data
                    self._update_sheet_data(sheets_service, sheet_id, None, fixed_data)
                    result.add_fix(len(empty_cells))
                    result.details["fixed_cells"] = empty_cells
                else:
                    result.add_issue(len(empty_cells))
                    result.details["empty_cells"] = empty_cells

        except ValidationError:
            raise
        except Exception as e:
            result.add_error(f"Unexpected error: {str(e)}")

        return result.to_dict()


class DuplicateRowsValidator(BaseValidator):
    """Validator for identifying and removing duplicate rows."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="duplicate_rows",
            name="Remove Duplicate Rows",
            description="Finds and optionally removes duplicate rows based on all columns",
        )

    def validate(
        self,
        sheets_service: Any,
        sheet_id: str,
        mode: str,
        keep_first: bool = True,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Check for and optionally remove duplicate rows.

        Args:
            sheets_service: Google Sheets API service instance
            sheet_id: ID of the spreadsheet to validate
            mode: Either "fix" (remove duplicates) or "flag" (report only)
            keep_first: If True, keep first occurrence of duplicate (default: True)

        Returns:
            Dict with validation results
        """
        result = ValidationResult()

        try:
            # Get all sheet data
            data = self._get_all_sheet_data(sheets_service, sheet_id)

            if not data:
                result.add_error("Sheet is empty")
                return result.to_dict()

            # Find duplicates
            seen_rows: Set[str] = set()
            duplicate_indices: List[int] = []
            unique_data: List[List[Any]] = []

            for row_idx, row in enumerate(data):
                # Convert row to string for comparison (handle None values)
                row_str = str([cell if cell is not None else "" for cell in row])

                if row_str in seen_rows:
                    duplicate_indices.append(row_idx + 1)  # 1-based indexing
                    if mode == "fix":
                        # Skip duplicate row (keep_first=True means skip duplicates)
                        continue
                else:
                    seen_rows.add(row_str)

                if mode == "fix":
                    unique_data.append(row)

            # Record results
            if duplicate_indices:
                if mode == "fix":
                    # Update the sheet with deduplicated data
                    self._update_sheet_data(sheets_service, sheet_id, None, unique_data)
                    result.add_fix(len(duplicate_indices))
                    result.details["removed_rows"] = duplicate_indices
                else:
                    result.add_issue(len(duplicate_indices))
                    result.details["duplicate_rows"] = duplicate_indices

        except ValidationError:
            raise
        except Exception as e:
            result.add_error(f"Unexpected error: {str(e)}")

        return result.to_dict()


class InconsistentFormattingValidator(BaseValidator):
    """Validator for fixing inconsistent text formatting."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="inconsistent_formatting",
            name="Fix Inconsistent Formatting",
            description="Standardizes text formatting (case, whitespace, etc.)",
        )

    def validate(
        self,
        sheets_service: Any,
        sheet_id: str,
        mode: str,
        trim_whitespace: bool = True,
        standardize_case: str = None,  # "upper", "lower", "title", or None
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Check for and optionally fix inconsistent formatting.

        Args:
            sheets_service: Google Sheets API service instance
            sheet_id: ID of the spreadsheet to validate
            mode: Either "fix" (standardize formatting) or "flag" (report only)
            trim_whitespace: Whether to trim leading/trailing whitespace
            standardize_case: Case standardization ("upper", "lower", "title", or None)

        Returns:
            Dict with validation results
        """
        result = ValidationResult()

        try:
            # Get all sheet data
            data = self._get_all_sheet_data(sheets_service, sheet_id)

            if not data:
                result.add_error("Sheet is empty")
                return result.to_dict()

            formatting_issues = []
            fixed_data = []

            # Check and fix formatting issues
            for row_idx, row in enumerate(data):
                fixed_row = []
                for col_idx, cell in enumerate(row):
                    original_cell = cell
                    fixed_cell = cell

                    # Only process string values
                    if isinstance(cell, str):
                        # Trim whitespace
                        if trim_whitespace:
                            fixed_cell = fixed_cell.strip()

                        # Standardize case
                        if standardize_case == "upper":
                            fixed_cell = fixed_cell.upper()
                        elif standardize_case == "lower":
                            fixed_cell = fixed_cell.lower()
                        elif standardize_case == "title":
                            fixed_cell = fixed_cell.title()

                        # Remove extra whitespace between words
                        fixed_cell = re.sub(r"\s+", " ", fixed_cell)

                        # Record if changes were made
                        if original_cell != fixed_cell:
                            formatting_issues.append(
                                {
                                    "row": row_idx + 1,
                                    "col": col_idx + 1,
                                    "original": original_cell,
                                    "fixed": fixed_cell,
                                }
                            )

                    fixed_row.append(fixed_cell)
                fixed_data.append(fixed_row)

            # Record results
            if formatting_issues:
                if mode == "fix":
                    # Update the sheet with fixed data
                    self._update_sheet_data(sheets_service, sheet_id, None, fixed_data)
                    result.add_fix(len(formatting_issues))
                    result.details["fixed_formatting"] = formatting_issues
                else:
                    result.add_issue(len(formatting_issues))
                    result.details["formatting_issues"] = formatting_issues

        except ValidationError:
            raise
        except Exception as e:
            result.add_error(f"Unexpected error: {str(e)}")

        return result.to_dict()


class MissingRequiredFieldsValidator(BaseValidator):
    """Validator for checking required fields."""

    def __init__(self) -> None:
        super().__init__(
            validator_id="missing_required_fields",
            name="Check Required Fields",
            description="Validates that required fields are not empty",
        )

    def validate(
        self,
        sheets_service: Any,
        sheet_id: str,
        mode: str,
        required_columns: List[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Check for missing required fields.

        Args:
            sheets_service: Google Sheets API service instance
            sheet_id: ID of the spreadsheet to validate
            mode: Either "fix" (not applicable) or "flag" (report only)
            required_columns: List of 1-based column indices that are required

        Returns:
            Dict with validation results
        """
        result = ValidationResult()

        try:
            # Get all sheet data
            data = self._get_all_sheet_data(sheets_service, sheet_id)

            if not data:
                result.add_error("Sheet is empty")
                return result.to_dict()

            # Default to checking all columns if none specified
            if required_columns is None:
                required_columns = list(range(1, len(data[0]) + 1)) if data else []

            missing_fields = []

            # Check each row for missing required fields
            for row_idx, row in enumerate(data):
                for col_idx in required_columns:
                    # Convert to 0-based index
                    col_zero_based = col_idx - 1

                    # Check if column exists and has value
                    if (
                        col_zero_based >= len(row)
                        or row[col_zero_based] == ""
                        or row[col_zero_based] is None
                    ):
                        missing_fields.append(
                            {
                                "row": row_idx + 1,
                                "col": col_idx,
                                "field": f"Column {col_idx}",
                            }
                        )

            # Record results (this validator only flags, doesn't fix)
            if missing_fields:
                result.add_issue(len(missing_fields))
                result.details["missing_fields"] = missing_fields

                if mode == "fix":
                    result.add_error(
                        "Cannot auto-fix missing required fields - manual review needed"
                    )

        except ValidationError:
            raise
        except Exception as e:
            result.add_error(f"Unexpected error: {str(e)}")

        return result.to_dict()
