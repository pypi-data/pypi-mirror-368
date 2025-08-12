"""Tests for the SheetNameQuotingValidator.

This module tests the sheet name quoting validator that was migrated
from checker1. It ensures all sheet names in verification ranges are
properly quoted with single quotes.
"""

import pandas as pd
import pytest
from urarovite.validators import get_validator
from urarovite.validators.sheet_name_quoting import run, run_detailed, SheetNameQuotingValidator


class TestSheetNameQuotingValidator:
    """Test cases for SheetNameQuotingValidator."""
    
    def test_validator_registration(self):
        """Test that the validator is properly registered."""
        validator = get_validator("sheet_name_quoting")
        assert isinstance(validator, SheetNameQuotingValidator)
        assert validator.id == "sheet_name_quoting"
        assert validator.name == "Sheet Name Quoting"
        assert "properly quoted" in validator.description
    
    def test_validator_all_quoted(self):
        """Test validator with all properly quoted sheet names."""
        validator = SheetNameQuotingValidator()
        
        result = validator.validate(
            sheets_service=None,
            sheet_id="",
            mode="flag",
            ranges_str="'Tab One'!A1:B2@@'Another'!C3@@'T'!Z1"
        )
        
        assert result["issues_found"] == 0
        assert result["details"]["total_segments"] == 3
        assert result["details"]["failing_segments"] == []
        assert result["details"]["original"] == "'Tab One'!A1:B2@@'Another'!C3@@'T'!Z1"
    
    def test_validator_unquoted_segments(self):
        """Test validator with unquoted sheet names."""
        validator = SheetNameQuotingValidator()
        
        result = validator.validate(
            sheets_service=None,
            sheet_id="",
            mode="flag",
            ranges_str="Tab One!A1:B2"
        )
        
        assert result["issues_found"] > 0
        assert result["details"]["total_segments"] == 1
        assert result["details"]["failing_segments"] == ["Tab One!A1:B2"]
    
    def test_validator_mixed_segments(self):
        """Test validator with mixed quoted and unquoted segments."""
        validator = SheetNameQuotingValidator()
        
        result = validator.validate(
            sheets_service=None,
            sheet_id="",
            mode="flag",
            ranges_str="'Good'!A1@@Bad!B2:B5@@'Also Good'!C1"
        )
        
        assert result["issues_found"] > 0
        assert result["details"]["total_segments"] == 3
        assert result["details"]["failing_segments"] == ["Bad!B2:B5"]
    
    def test_validator_with_row_data(self):
        """Test validator with pandas Series row data."""
        validator = SheetNameQuotingValidator()
        
        row = pd.Series({
            "verification_field_ranges": "'Sheet1'!A1:B10@@'Sheet2'!C1:D5"
        })
        
        result = validator.validate(
            sheets_service=None,
            sheet_id="",
            mode="flag",
            row=row
        )
        
        assert result["issues_found"] == 0
        assert result["details"]["total_segments"] == 2
        assert result["details"]["failing_segments"] == []
    
    def test_validator_custom_field(self):
        """Test validator with custom field name."""
        validator = SheetNameQuotingValidator()
        
        row = pd.Series({
            "custom_ranges": "'Tab'!A1@@Sheet2!B2"
        })
        
        result = validator.validate(
            sheets_service=None,
            sheet_id="",
            mode="flag",
            row=row,
            field="custom_ranges"
        )
        
        assert result["issues_found"] > 0
        assert result["details"]["total_segments"] == 2
        assert len(result["details"]["failing_segments"]) == 1
        assert "Sheet2!B2" in result["details"]["failing_segments"]
    
    def test_validator_empty_ranges(self):
        """Test validator with empty ranges string."""
        validator = SheetNameQuotingValidator()
        
        result = validator.validate(
            sheets_service=None,
            sheet_id="",
            mode="flag",
            ranges_str=""
        )
        
        assert result["issues_found"] == 0
        assert result["details"]["total_segments"] == 0
        assert result["details"]["failing_segments"] == []
    
    def test_validator_missing_parameters(self):
        """Test validator with missing required parameters."""
        validator = SheetNameQuotingValidator()
        
        # Should return empty result instead of raising exception
        result = validator.validate(
            sheets_service=None,
            sheet_id="",
            mode="flag"
            # Missing both row and ranges_str
        )
        
        assert result["issues_found"] == 0
        assert result["details"]["total_segments"] == 0
        assert result["details"]["failing_segments"] == []
        assert result["details"]["original"] == ""


class TestBackwardCompatibility:
    """Test backward compatibility with the original checker1 interface."""
    
    def test_run_function_with_string(self):
        """Test the run() function with direct string input."""
        result = run("'March 2025'!A2:A91@@'Sheet1'!B1")
        
        # Should have same structure as original checker1
        assert result["issues_found"] == 0
        assert result["details"]["total_segments"] == 2
        assert result["details"]["failing_segments"] == []
    
    def test_run_function_with_series(self):
        """Test the run() function with pandas Series."""
        row = pd.Series({
            "verification_field_ranges": "'Tab'!A1@@'B'!B2:B5"
        })
        
        result = run(row)
        
        assert result["issues_found"] == 0
        assert result["details"]["total_segments"] == 2
        assert result["details"]["failing_segments"] == []
    
    def test_run_function_with_failing_segments(self):
        """Test the run() function with unquoted segments."""
        result = run("March 2025'!A2:A91@@'Sheet1'!B1")
        
        assert result["issues_found"] > 0
        assert len(result["details"]["failing_segments"]) == 1
        assert "March 2025'!A2:A91" in result["details"]["failing_segments"]
    
    def test_run_function_custom_field(self):
        """Test the run() function with custom field name."""
        row = pd.Series({
            "custom_field": "'Tab'!A1@@Sheet2!B2"
        })
        
        result = run(row, field="custom_field")
        
        assert result["issues_found"] > 0
        assert len(result["details"]["failing_segments"]) == 1
    
    def test_run_detailed_alias(self):
        """Test the run_detailed alias function."""
        result = run_detailed("'Sheet1'!A1:B10")
        
        assert result["issues_found"] == 0
        assert result["details"]["total_segments"] == 1


class TestValidatorLogic:
    """Test specific validator logic components."""
    
    def test_segment_is_quoted_valid(self):
        """Test segment quoting detection with valid segments."""
        validator = SheetNameQuotingValidator()
        
        valid_segments = [
            "'Sheet1'!A1:B10",
            "'March 2025'!A2:A91",
            "'Tab'!A1",
            "'Complex Name With Spaces'!Z99",
            "'Sheet'!",  # Whole sheet reference
            "'A'!B1:C5"
        ]
        
        for segment in valid_segments:
            assert validator._segment_is_quoted(segment), f"'{segment}' should be valid"
    
    def test_segment_is_quoted_invalid(self):
        """Test segment quoting detection with invalid segments."""
        validator = SheetNameQuotingValidator()
        
        invalid_segments = [
            "Sheet1!A1:B10",  # No quotes
            "March 2025!A2:A91",  # No quotes with spaces
            "'Sheet1!A1:B10",  # Missing closing quote
            "Sheet1'!A1:B10",  # Missing opening quote
            "Sheet1A1:B10",  # Missing exclamation point
            "",  # Empty segment
            "!A1:B10"  # Missing sheet name entirely
        ]
        
        for segment in invalid_segments:
            assert not validator._segment_is_quoted(segment), f"'{segment}' should be invalid"
    
    def test_edge_cases(self):
        """Test edge cases and special characters."""
        validator = SheetNameQuotingValidator()
        
        # Test with various special characters in sheet names
        special_cases = [
            ("'Sheet-1'!A1", True),  # Hyphen
            ("'Sheet_1'!A1", True),  # Underscore
            ("'Sheet 1'!A1", True),  # Space
            ("'Sheet.1'!A1", True),  # Period
            ("'Sheet(1)'!A1", True),  # Parentheses
            ("'Sheet[1]'!A1", True),  # Brackets
        ]
        
        for segment, expected in special_cases:
            result = validator._segment_is_quoted(segment)
            assert result == expected, f"'{segment}' should be {expected}"
