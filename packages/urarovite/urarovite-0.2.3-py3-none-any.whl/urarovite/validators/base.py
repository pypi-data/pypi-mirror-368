"""Base validator class for all validation implementations.

This module defines the abstract base class that all validators must inherit from,
ensuring consistent interface and behavior across all validation checks.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from urarovite.core.exceptions import ValidationError


class ValidationResult:
    """Container for validation results."""
    
    def __init__(self) -> None:
        self.fixes_applied: int = 0
        self.issues_found: int = 0
        self.errors: List[str] = []
        self.details: Dict[str, Any] = {}
        
    def add_fix(self, count: int = 1) -> None:
        """Add to the count of fixes applied."""
        self.fixes_applied += count
        
    def add_issue(self, count: int = 1) -> None:
        """Add to the count of issues found."""
        self.issues_found += count
        
    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for API response."""
        return {
            "fixes_applied": self.fixes_applied,
            "issues_found": self.issues_found,
            "errors": self.errors,
            "details": self.details
        }


class BaseValidator(ABC):
    """Abstract base class for all validators.
    
    All validation implementations must inherit from this class and implement
    the required methods. This ensures consistent behavior and error handling.
    """
    
    def __init__(self, validator_id: str, name: str, description: str) -> None:
        """Initialize the validator.
        
        Args:
            validator_id: Unique identifier for this validator
            name: Human-readable name
            description: Description of what this validator does
        """
        self.id = validator_id
        self.name = name
        self.description = description
    
    @abstractmethod
    def validate(
        self, 
        sheets_service: Any, 
        sheet_id: str, 
        mode: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Execute the validation check.
        
        Args:
            sheets_service: Google Sheets API service instance
            sheet_id: ID of the spreadsheet to validate
            mode: Either "fix" (auto-correct) or "flag" (report only)
            **kwargs: Additional validator-specific parameters
            
        Returns:
            Dict with validation results
            
        Raises:
            ValidationError: If validation fails
        """
        pass
    
    def _get_all_sheet_data(
        self, 
        sheets_service: Any, 
        sheet_id: str,
        sheet_name: str = None
    ) -> List[List[Any]]:
        """Helper method to get all data from a sheet.
        
        Args:
            sheets_service: Google Sheets API service instance
            sheet_id: ID of the spreadsheet
            sheet_name: Name of the specific sheet (optional)
            
        Returns:
            2D list of cell values
            
        Raises:
            ValidationError: If unable to read sheet data
        """
        try:
            from urarovite.utils.sheets import get_sheet_values
            
            # If no sheet name specified, get the first sheet
            if not sheet_name:
                from urarovite.utils.sheets import fetch_sheet_tabs
                tabs_result = fetch_sheet_tabs(sheets_service, sheet_id)
                if not tabs_result["accessible"] or not tabs_result["tabs"]:
                    raise ValidationError("Unable to access sheet tabs")
                sheet_name = tabs_result["tabs"][0]
            
            # Get all data from the sheet
            range_name = f"'{sheet_name}'"
            result = get_sheet_values(sheets_service, sheet_id, range_name)
            
            if not result["success"]:
                raise ValidationError(f"Failed to read sheet data: {result['error']}")
                
            return result["values"]
            
        except Exception as e:
            raise ValidationError(f"Failed to get sheet data: {str(e)}")
    
    def _update_sheet_data(
        self,
        sheets_service: Any,
        sheet_id: str,
        sheet_name: str,
        values: List[List[Any]],
        start_row: int = 1,
        start_col: int = 1
    ) -> None:
        """Helper method to update sheet data.
        
        Args:
            sheets_service: Google Sheets API service instance
            sheet_id: ID of the spreadsheet
            sheet_name: Name of the sheet to update
            values: 2D list of values to write
            start_row: Starting row (1-based)
            start_col: Starting column (1-based)
            
        Raises:
            ValidationError: If unable to update sheet
        """
        try:
            from urarovite.utils.sheets import update_sheet_values, col_index_to_letter
            
            # Convert to A1 notation
            start_col_letter = col_index_to_letter(start_col - 1)
            end_row = start_row + len(values) - 1
            end_col_letter = col_index_to_letter(start_col + len(values[0]) - 2) if values and values[0] else start_col_letter
            
            range_name = f"'{sheet_name}'!{start_col_letter}{start_row}:{end_col_letter}{end_row}"
            
            result = update_sheet_values(sheets_service, sheet_id, range_name, values)
            
            if not result["success"]:
                raise ValidationError(f"Failed to update sheet: {result['error']}")
                
        except Exception as e:
            raise ValidationError(f"Failed to update sheet data: {str(e)}")
    
    def __str__(self) -> str:
        return f"{self.name} ({self.id})"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id='{self.id}', name='{self.name}')>"
