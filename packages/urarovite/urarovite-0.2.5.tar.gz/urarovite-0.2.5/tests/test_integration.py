"""Integration tests for the complete Urarovite workflow."""

import base64
import json
import pytest
from unittest.mock import patch, Mock, MagicMock

from urarovite.core.api import get_available_validation_criteria, execute_validation
from urarovite.auth.google_sheets import (
    get_gspread_client,
    create_sheets_service_from_encoded_creds,
)


# Sample service account for testing
SAMPLE_SERVICE_ACCOUNT = {
    "type": "service_account",
    "project_id": "test-project",
    "private_key_id": "key123",
    "private_key": "-----BEGIN PRIVATE KEY-----\ntest-key\n-----END PRIVATE KEY-----\n",
    "client_email": "test@test-project.iam.gserviceaccount.com",
    "client_id": "123456789",
}


class TestFullWorkflow:
    """Test the complete validation workflow from start to finish."""

    def setup_method(self):
        """Set up test fixtures."""
        self.encoded_creds = base64.b64encode(
            json.dumps(SAMPLE_SERVICE_ACCOUNT).encode()
        ).decode()
        self.valid_sheet_url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit"

    @patch("urarovite.auth.google_sheets.build")
    @patch("urarovite.auth.google_sheets.ServiceAccountCredentials")
    @patch("urarovite.core.api.get_validator_registry")
    def test_complete_validation_workflow_fix_mode(
        self, mock_get_registry, mock_creds_class, mock_build
    ):
        """Test complete workflow in fix mode."""
        # Mock authentication
        mock_creds = Mock()
        mock_creds_class.from_service_account_info.return_value = mock_creds
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock validator
        mock_validator = Mock()
        mock_validator.validate.return_value = {
            "fixes_applied": 5,
            "issues_found": 0,
            "errors": [],
            "details": {"fixed_cells": [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]},
            "automated_log": "Fixed empty cells at positions: [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]"
        }
        mock_registry = {"empty_cells": mock_validator}
        mock_get_registry.return_value = mock_registry

        # Execute validation
        result = execute_validation(
            check={"id": "empty_cells", "mode": "fix"},
            sheet_url=self.valid_sheet_url,
            auth_secret=self.encoded_creds,
        )

        # Verify results
        assert result["fixes_applied"] == 5
        assert result["issues_flagged"] == 0
        assert result["errors"] == []
        assert "Fixed empty cells at positions" in result["automated_logs"]

        # Verify authentication was called correctly
        mock_creds_class.from_service_account_info.assert_called_once()
        mock_build.assert_called_once_with("sheets", "v4", credentials=mock_creds)

        # Verify validator was called
        mock_validator.validate.assert_called_once_with(
            sheets_service=mock_service,
            sheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
            mode="fix",
            auth_secret=self.encoded_creds,
            subject=None,
        )

    @patch("urarovite.auth.google_sheets.build")
    @patch("urarovite.auth.google_sheets.ServiceAccountCredentials")
    @patch("urarovite.core.api.get_validator_registry")
    def test_complete_validation_workflow_flag_mode(
        self, mock_get_registry, mock_creds_class, mock_build
    ):
        """Test complete workflow in flag mode."""
        # Mock authentication
        mock_creds = Mock()
        mock_creds_class.from_service_account_info.return_value = mock_creds
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock validator
        mock_validator = Mock()
        mock_validator.validate.return_value = {
            "fixes_applied": 0,
            "issues_found": 8,
            "errors": ["Warning: Row 5 has duplicate data"],
            "details": {"duplicate_rows": [3, 5, 7]},
            "automated_log": "Duplicate rows found: [3, 5, 7]"
        }
        mock_registry = {"duplicate_rows": mock_validator}
        mock_get_registry.return_value = mock_registry

        # Execute validation
        result = execute_validation(
            check={"id": "duplicate_rows", "mode": "flag"},
            sheet_url=self.valid_sheet_url,
            auth_secret=self.encoded_creds,
        )

        # Verify results
        assert result["fixes_applied"] == 0
        assert result["issues_flagged"] == 8
        assert len(result["errors"]) == 1
        assert "Warning: Row 5 has duplicate data" in result["errors"]
        assert "Duplicate rows found" in result["automated_logs"]

    @patch("urarovite.auth.google_sheets.build")
    @patch("urarovite.auth.google_sheets.ServiceAccountCredentials")
    @patch("urarovite.core.api.get_validator_registry")
    def test_workflow_with_subject_delegation(
        self, mock_get_registry, mock_creds_class, mock_build
    ):
        """Test workflow with subject delegation."""
        # Mock authentication with delegation
        mock_creds = Mock()
        mock_delegated_creds = Mock()
        mock_creds.with_subject.return_value = mock_delegated_creds
        mock_creds_class.from_service_account_info.return_value = mock_creds
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock validator
        mock_validator = Mock()
        mock_validator.validate.return_value = {
            "fixes_applied": 2,
            "issues_found": 0,
            "errors": [],
        }
        mock_registry = {"format_validation": mock_validator}
        mock_get_registry.return_value = mock_registry

        # Execute validation with subject
        result = execute_validation(
            check={"id": "format_validation", "mode": "fix"},
            sheet_url=self.valid_sheet_url,
            auth_secret=self.encoded_creds,
            subject="user@example.com",
        )

        # Verify delegation was attempted
        mock_creds.with_subject.assert_called_once_with("user@example.com")
        mock_build.assert_called_once_with(
            "sheets", "v4", credentials=mock_delegated_creds
        )

        # Verify results
        assert result["fixes_applied"] == 2
        assert result["errors"] == []

    def test_validation_criteria_consistency(self):
        """Test that validation criteria are consistent across calls."""
        criteria1 = get_available_validation_criteria()
        criteria2 = get_available_validation_criteria()

        # Should return consistent results
        assert criteria1 == criteria2

        # Should have expected structure
        assert isinstance(criteria1, list)
        assert len(criteria1) > 0

        for criterion in criteria1:
            assert "id" in criterion
            assert "name" in criterion


class TestWorkflowErrorHandling:
    """Test error handling throughout the workflow."""

    def setup_method(self):
        """Set up test fixtures."""
        self.encoded_creds = base64.b64encode(
            json.dumps(SAMPLE_SERVICE_ACCOUNT).encode()
        ).decode()
        self.valid_sheet_url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit"

    def test_invalid_credentials_error_propagation(self):
        """Test that invalid credentials errors are properly handled."""
        result = execute_validation(
            check={"id": "empty_cells", "mode": "fix"},
            sheet_url=self.valid_sheet_url,
            auth_secret="invalid-base64!",
        )

        assert result["fixes_applied"] == 0
        assert result["issues_flagged"] == 0
        assert len(result["errors"]) == 1
        assert "Authentication failed" in result["errors"][0]

    @patch("urarovite.auth.google_sheets.build")
    @patch("urarovite.auth.google_sheets.ServiceAccountCredentials")
    def test_service_creation_failure(self, mock_creds_class, mock_build):
        """Test handling of service creation failures."""
        # Mock credential creation to succeed but service creation to fail
        mock_creds = Mock()
        mock_creds_class.from_service_account_info.return_value = mock_creds
        mock_build.side_effect = Exception("Service creation failed")

        result = execute_validation(
            check={"id": "empty_cells", "mode": "fix"},
            sheet_url=self.valid_sheet_url,
            auth_secret=self.encoded_creds,
        )

        assert result["fixes_applied"] == 0
        assert result["issues_flagged"] == 0
        assert len(result["errors"]) == 1
        assert "Authentication failed" in result["errors"][0]

    @patch("urarovite.auth.google_sheets.build")
    @patch("urarovite.auth.google_sheets.ServiceAccountCredentials")
    @patch("urarovite.core.api.get_validator_registry")
    def test_validator_exception_handling(
        self, mock_get_registry, mock_creds_class, mock_build
    ):
        """Test handling of validator exceptions."""
        # Mock authentication
        mock_creds = Mock()
        mock_creds_class.from_service_account_info.return_value = mock_creds
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock validator that throws exception
        mock_validator = Mock()
        mock_validator.validate.side_effect = RuntimeError("Validator crashed")
        mock_registry = {"empty_cells": mock_validator}
        mock_get_registry.return_value = mock_registry

        result = execute_validation(
            check={"id": "empty_cells", "mode": "fix"},
            sheet_url=self.valid_sheet_url,
            auth_secret=self.encoded_creds,
        )

        assert result["fixes_applied"] == 0
        assert result["issues_flagged"] == 0
        assert len(result["errors"]) == 1
        assert (
            "Unexpected error in check 'empty_cells': Validator crashed"
            in result["errors"][0]
        )


class TestBackwardCompatibilityIntegration:
    """Test that backward compatibility works in integration scenarios."""

    def test_legacy_imports_in_workflow(self):
        """Test that legacy imports work in a realistic workflow."""
        # These imports should work without error
        from urarovite.checker import get_gspread_client, clear_service_cache
        from urarovite.checker import extract_sheet_id, fetch_sheet_tabs
        from urarovite.utils import get_sheet_values, parse_referenced_tabs

        # All functions should be callable
        assert callable(get_gspread_client)
        assert callable(clear_service_cache)
        assert callable(extract_sheet_id)
        assert callable(fetch_sheet_tabs)
        assert callable(get_sheet_values)
        assert callable(parse_referenced_tabs)

    def test_mixed_import_styles_work_together(self):
        """Test that mixing old and new import styles works in practice."""
        # Import using different styles
        from urarovite.checker import extract_sheet_id as legacy_extract
        from urarovite.utils.sheets import extract_sheet_id as new_extract
        from urarovite.auth import get_gspread_client as new_auth
        from urarovite.checker.auth import get_gspread_client as legacy_auth

        # They should be the same functions
        assert legacy_extract == new_extract
        assert legacy_auth == new_auth

        # Test with a real URL
        test_url = "https://docs.google.com/spreadsheets/d/1ABC123/edit"
        result1 = legacy_extract(test_url)
        result2 = new_extract(test_url)
        assert result1 == result2 == "1ABC123"


class TestEndToEndScenarios:
    """Test realistic end-to-end scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.encoded_creds = base64.b64encode(
            json.dumps(SAMPLE_SERVICE_ACCOUNT).encode()
        ).decode()

    @patch("urarovite.auth.google_sheets.build")
    @patch("urarovite.auth.google_sheets.ServiceAccountCredentials")
    @patch("urarovite.core.api.get_validator_registry")
    def test_multiple_validations_different_modes(
        self, mock_get_registry, mock_creds_class, mock_build
    ):
        """Test running multiple validations on the same sheet."""
        # Mock authentication (reused across calls)
        mock_creds = Mock()
        mock_creds_class.from_service_account_info.return_value = mock_creds
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock different validators
        mock_empty_cells_validator = Mock()
        mock_empty_cells_validator.validate.return_value = {
            "fixes_applied": 3,
            "issues_found": 0,
            "errors": [],
        }

        mock_duplicate_validator = Mock()
        mock_duplicate_validator.validate.return_value = {
            "fixes_applied": 0,
            "issues_found": 2,
            "errors": [],
        }

        mock_registry = {
            "empty_cells": mock_empty_cells_validator,
            "duplicate_rows": mock_duplicate_validator,
        }
        mock_get_registry.return_value = mock_registry

        sheet_url = "https://docs.google.com/spreadsheets/d/1ABC123/edit"

        # Run first validation (fix mode)
        result1 = execute_validation(
            check={"id": "empty_cells", "mode": "fix"},
            sheet_url=sheet_url,
            auth_secret=self.encoded_creds,
        )

        # Run second validation (flag mode)
        result2 = execute_validation(
            check={"id": "duplicate_rows", "mode": "flag"},
            sheet_url=sheet_url,
            auth_secret=self.encoded_creds,
        )

        # Verify results
        assert result1["fixes_applied"] == 3
        assert result1["issues_flagged"] == 0

        assert result2["fixes_applied"] == 0
        assert result2["issues_flagged"] == 2

        # Verify both validators were called
        mock_empty_cells_validator.validate.assert_called_once()
        mock_duplicate_validator.validate.assert_called_once()

    @patch("urarovite.auth.google_sheets.build")
    @patch("urarovite.auth.google_sheets.ServiceAccountCredentials")
    @patch("urarovite.core.api.get_validator_registry")
    def test_validation_with_warnings_and_fixes(
        self, mock_get_registry, mock_creds_class, mock_build
    ):
        """Test validation that both fixes issues and reports warnings."""
        # Mock authentication
        mock_creds = Mock()
        mock_creds_class.from_service_account_info.return_value = mock_creds
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Mock validator that fixes some issues but warns about others
        mock_validator = Mock()
        mock_validator.validate.return_value = {
            "fixes_applied": 4,
            "issues_found": 0,  # In fix mode, this should be 0
            "errors": [
                "Warning: Could not fix protected cell at A5",
                "Info: Skipped empty row 10",
            ],
            "details": {"fixed_formatting": [(1, 1), (2, 2), (3, 3), (4, 4)]},
            "automated_log": "Fixed formatting issues: 4 cells"
        }
        mock_registry = {"data_quality": mock_validator}
        mock_get_registry.return_value = mock_registry

        result = execute_validation(
            check={"id": "data_quality", "mode": "fix"},
            sheet_url="https://docs.google.com/spreadsheets/d/1TEST123/edit",
            auth_secret=self.encoded_creds,
        )

        # Verify results include both fixes and warnings
        assert result["fixes_applied"] == 4
        assert result["issues_flagged"] == 0
        assert len(result["errors"]) == 2
        assert "Could not fix protected cell" in result["errors"][0]
        assert "Skipped empty row" in result["errors"][1]
        assert "Fixed formatting issues" in result["automated_logs"]

    def test_criteria_and_execution_consistency(self):
        """Test that criteria IDs match what execute_validation accepts."""
        criteria = get_available_validation_criteria()

        # Extract all criterion IDs
        criterion_ids = [c["id"] for c in criteria]

        # Verify we have some criteria
        assert len(criterion_ids) > 0

        # Each ID should be a valid string
        for criterion_id in criterion_ids:
            assert isinstance(criterion_id, str)
            assert len(criterion_id) > 0
            assert criterion_id.replace("_", "").replace("-", "").isalnum()

        # Test that execute_validation recognizes these IDs
        # (This would fail with unknown validator in a real scenario, but tests the ID validation)
        for criterion_id in criterion_ids:
            result = execute_validation(
                check={"id": criterion_id, "mode": "flag"},
                sheet_url="https://docs.google.com/spreadsheets/d/1TEST/edit",
                auth_secret=self.encoded_creds,
            )

            # Should fail on auth, not on unknown criterion
            if result["errors"]:
                # Should be auth error, not unknown criterion error
                assert not any(
                    "Unknown validation check" in error for error in result["errors"]
                )
