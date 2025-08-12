"""Data quality validators for common spreadsheet issues.

This module implements validators for basic data quality issues such as
empty cells, duplicate rows, and inconsistent formatting.
"""

import re
from typing import Any, Dict, List, Set, Tuple

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.exceptions import ValidationError


class EmptyCellsValidator(BaseValidator):
    """Validator for identifying and fixing empty cells."""
    
    def __init__(self) -> None:
        super().__init__(
            validator_id="empty_cells",
            name="Fix Empty Cells",
            description="Identifies and optionally fills empty cells with default values"
        )
    
    def validate(
        self, 
        sheets_service: Any, 
        sheet_id: str, 
        mode: str,
        fill_value: str = "",
        **kwargs: Any
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
                        empty_cells.append((row_idx + 1, col_idx + 1))  # 1-based indexing
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
            description="Finds and optionally removes duplicate rows based on all columns"
        )
    
    def validate(
        self, 
        sheets_service: Any, 
        sheet_id: str, 
        mode: str,
        keep_first: bool = True,
        **kwargs: Any
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
                    if not keep_first and mode == "fix":
                        continue  # Skip this duplicate row
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
            description="Standardizes text formatting (case, whitespace, etc.)"
        )
    
    def validate(
        self, 
        sheets_service: Any, 
        sheet_id: str, 
        mode: str,
        trim_whitespace: bool = True,
        standardize_case: str = None,  # "upper", "lower", "title", or None
        **kwargs: Any
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
                        fixed_cell = re.sub(r'\s+', ' ', fixed_cell)
                        
                        # Record if changes were made
                        if original_cell != fixed_cell:
                            formatting_issues.append({
                                "row": row_idx + 1,
                                "col": col_idx + 1,
                                "original": original_cell,
                                "fixed": fixed_cell
                            })
                    
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
            description="Validates that required fields are not empty"
        )
    
    def validate(
        self, 
        sheets_service: Any, 
        sheet_id: str, 
        mode: str,
        required_columns: List[int] = None,
        **kwargs: Any
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
                    if (col_zero_based >= len(row) or 
                        row[col_zero_based] == "" or 
                        row[col_zero_based] is None):
                        missing_fields.append({
                            "row": row_idx + 1,
                            "col": col_idx,
                            "field": f"Column {col_idx}"
                        })
            
            # Record results (this validator only flags, doesn't fix)
            if missing_fields:
                result.add_issue(len(missing_fields))
                result.details["missing_fields"] = missing_fields
                
                if mode == "fix":
                    result.add_error("Cannot auto-fix missing required fields - manual review needed")
            
        except ValidationError:
            raise
        except Exception as e:
            result.add_error(f"Unexpected error: {str(e)}")
        
        return result.to_dict()
