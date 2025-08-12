"""Tests for the updated API functions in core.api module."""

import base64
import json
import pytest
from unittest.mock import patch, Mock, MagicMock

from urarovite.core.api import get_available_validation_criteria, execute_validation
from urarovite.core.exceptions import (
    AuthenticationError,
    ValidationError,
    SheetAccessError,
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


class TestGetAvailableValidationCriteria:
    """Test the get_available_validation_criteria function."""

    def test_returns_list_of_criteria(self):
        """Test that function returns a list of validation criteria."""
        result = get_available_validation_criteria()

        assert isinstance(result, list)
        assert len(result) > 0

        # Check structure of each criterion
        for criterion in result:
            assert isinstance(criterion, dict)
            assert "id" in criterion
            assert "name" in criterion
            assert isinstance(criterion["id"], str)
            assert isinstance(criterion["name"], str)

    def test_criteria_have_required_fields(self):
        """Test that all criteria have required id and name fields."""
        result = get_available_validation_criteria()

        for criterion in result:
            # Should have both id and name
            assert criterion["id"], f"Criterion missing id: {criterion}"
            assert criterion["name"], f"Criterion missing name: {criterion}"

            # ID should be suitable for programmatic use
            assert isinstance(criterion["id"], str)
            assert len(criterion["id"]) > 0

            # Name should be human-readable
            assert isinstance(criterion["name"], str)
            assert len(criterion["name"]) > 0


class TestExecuteValidation:
    """Test the updated execute_validation function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.encoded_creds = base64.b64encode(
            json.dumps(SAMPLE_SERVICE_ACCOUNT).encode()
        ).decode()
        self.valid_sheet_url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit"
        self.valid_check = {"id": "empty_cells", "mode": "fix"}

    def test_missing_check(self):
        """Test error handling when no check is provided."""
        result = execute_validation(
            check=None, sheet_url=self.valid_sheet_url, auth_secret=self.encoded_creds
        )

        assert result["fixes_applied"] == 0
        assert result["issues_flagged"] == 0
        assert len(result["errors"]) == 1
        assert "No validation check specified" in result["errors"][0]
        assert "automated_logs" in result

    def test_empty_check(self):
        """Test error handling when empty check is provided."""
        result = execute_validation(
            check={}, sheet_url=self.valid_sheet_url, auth_secret=self.encoded_creds
        )

        assert result["fixes_applied"] == 0
        assert result["issues_flagged"] == 0
        assert len(result["errors"]) == 1
        assert "No validation check specified" in result["errors"][0]

    @patch("urarovite.core.api.create_sheets_service_from_encoded_creds")
    def test_check_missing_id_field(self, mock_create_service):
        """Test error handling when check is missing 'id' field."""
        # Mock successful authentication to get to ID validation
        mock_service = Mock()
        mock_create_service.return_value = mock_service

        result = execute_validation(
            check={"mode": "fix"},  # Missing 'id' field
            sheet_url=self.valid_sheet_url,
            auth_secret=self.encoded_creds,
        )

        assert result["fixes_applied"] == 0
        assert result["issues_flagged"] == 0
        assert len(result["errors"]) == 1
        assert "Check missing required 'id' field" in result["errors"][0]

    def test_missing_sheet_url(self):
        """Test error handling when sheet URL is missing."""
        result = execute_validation(
            check=self.valid_check, sheet_url="", auth_secret=self.encoded_creds
        )

        assert result["fixes_applied"] == 0
        assert result["issues_flagged"] == 0
        assert len(result["errors"]) == 1
        assert "Sheet URL is required" in result["errors"][0]

    def test_missing_auth_secret(self):
        """Test error handling when auth_secret is missing."""
        result = execute_validation(
            check=self.valid_check, sheet_url=self.valid_sheet_url, auth_secret=None
        )

        assert result["fixes_applied"] == 0
        assert result["issues_flagged"] == 0
        assert len(result["errors"]) == 1
        assert "Authentication credentials are required" in result["errors"][0]
        assert "base64 encoded service account" in result["errors"][0]

    def test_invalid_sheet_url(self):
        """Test error handling for invalid sheet URL."""
        result = execute_validation(
            check=self.valid_check,
            sheet_url="https://invalid-url.com",
            auth_secret=self.encoded_creds,
        )

        assert result["fixes_applied"] == 0
        assert result["issues_flagged"] == 0
        assert len(result["errors"]) == 1
        assert "Invalid Google Sheets URL" in result["errors"][0]

    @patch("urarovite.core.api.create_sheets_service_from_encoded_creds")
    def test_invalid_mode(self, mock_create_service):
        """Test error handling for invalid validation mode."""
        # Mock successful authentication to get to mode validation
        mock_service = Mock()
        mock_create_service.return_value = mock_service

        invalid_check = {"id": "empty_cells", "mode": "invalid_mode"}

        result = execute_validation(
            check=invalid_check,
            sheet_url=self.valid_sheet_url,
            auth_secret=self.encoded_creds,
        )

        assert result["fixes_applied"] == 0
        assert result["issues_flagged"] == 0
        assert len(result["errors"]) == 1
        assert "Invalid mode 'invalid_mode'" in result["errors"][0]
        assert "Must be 'fix' or 'flag'" in result["errors"][0]

    def test_default_mode_is_flag(self):
        """Test that default mode is 'flag' when not specified."""
        check_without_mode = {"id": "empty_cells"}

        with (
            patch(
                "urarovite.core.api.create_sheets_service_from_encoded_creds"
            ) as mock_create_service,
            patch("urarovite.core.api.get_validator_registry") as mock_get_registry,
        ):
            # Mock successful authentication
            mock_service = Mock()
            mock_create_service.return_value = mock_service

            # Mock validator registry
            mock_validator = Mock()
            mock_validator.validate.return_value = {
                "issues_found": 5,
                "fixes_applied": 0,
                "errors": [],
            }
            mock_registry = {"empty_cells": mock_validator}
            mock_get_registry.return_value = mock_registry

            result = execute_validation(
                check=check_without_mode,
                sheet_url=self.valid_sheet_url,
                auth_secret=self.encoded_creds,
            )

            # Should use flag mode by default
            mock_validator.validate.assert_called_once()
            call_args = mock_validator.validate.call_args
            assert call_args[1]["mode"] == "flag"

    @patch("urarovite.core.api.create_sheets_service_from_encoded_creds")
    def test_authentication_failure(self, mock_create_service):
        """Test handling of authentication failures."""
        mock_create_service.side_effect = AuthenticationError("Auth failed")

        result = execute_validation(
            check=self.valid_check,
            sheet_url=self.valid_sheet_url,
            auth_secret=self.encoded_creds,
        )

        assert result["fixes_applied"] == 0
        assert result["issues_flagged"] == 0
        assert len(result["errors"]) == 1
        assert "Authentication failed: Auth failed" in result["errors"][0]

    @patch("urarovite.core.api.create_sheets_service_from_encoded_creds")
    @patch("urarovite.core.api.get_validator_registry")
    def test_unknown_validation_check(self, mock_get_registry, mock_create_service):
        """Test handling of unknown validation check IDs."""
        # Mock successful authentication
        mock_service = Mock()
        mock_create_service.return_value = mock_service

        # Mock empty validator registry
        mock_get_registry.return_value = {}

        unknown_check = {"id": "unknown_check", "mode": "fix"}

        result = execute_validation(
            check=unknown_check,
            sheet_url=self.valid_sheet_url,
            auth_secret=self.encoded_creds,
        )

        assert result["fixes_applied"] == 0
        assert result["issues_flagged"] == 0
        assert len(result["errors"]) == 1
        assert "Unknown validation check: 'unknown_check'" in result["errors"][0]

    @patch("urarovite.core.api.create_sheets_service_from_encoded_creds")
    @patch("urarovite.core.api.get_validator_registry")
    def test_successful_fix_mode(self, mock_get_registry, mock_create_service):
        """Test successful validation in fix mode."""
        # Mock successful authentication
        mock_service = Mock()
        mock_create_service.return_value = mock_service

        # Mock validator registry
        mock_validator = Mock()
        mock_validator.validate.return_value = {
            "fixes_applied": 3,
            "issues_found": 0,
            "errors": [],
            "details": {
                "fixed_cells": [(2, 1), (3, 2), (4, 1)]
            },
            "automated_log": "Fixed empty cells at positions: [(2, 1), (3, 2), (4, 1)]"
        }
        mock_registry = {"empty_cells": mock_validator}
        mock_get_registry.return_value = mock_registry

        result = execute_validation(
            check={"id": "empty_cells", "mode": "fix"},
            sheet_url=self.valid_sheet_url,
            auth_secret=self.encoded_creds,
        )

        assert result["fixes_applied"] == 3
        assert result["issues_flagged"] == 0
        assert result["errors"] == []
        assert "Fixed empty cells at positions" in result["automated_logs"]

    @patch("urarovite.core.api.create_sheets_service_from_encoded_creds")
    @patch("urarovite.core.api.get_validator_registry")
    def test_successful_flag_mode(self, mock_get_registry, mock_create_service):
        """Test successful validation in flag mode."""
        # Mock successful authentication
        mock_service = Mock()
        mock_create_service.return_value = mock_service

        # Mock validator registry
        mock_validator = Mock()
        mock_validator.validate.return_value = {
            "fixes_applied": 0,
            "issues_found": 7,
            "errors": [],
            "details": {
                "duplicate_rows": [3, 5, 7, 9, 11, 13, 15]
            },
            "automated_log": "Duplicate rows found: [3, 5, 7, 9, 11, 13, 15]"
        }
        mock_registry = {"duplicate_rows": mock_validator}
        mock_get_registry.return_value = mock_registry

        result = execute_validation(
            check={"id": "duplicate_rows", "mode": "flag"},
            sheet_url=self.valid_sheet_url,
            auth_secret=self.encoded_creds,
        )

        assert result["fixes_applied"] == 0
        assert result["issues_flagged"] == 7
        assert result["errors"] == []
        assert "Duplicate rows found" in result["automated_logs"]

    @patch("urarovite.core.api.create_sheets_service_from_encoded_creds")
    @patch("urarovite.core.api.get_validator_registry")
    def test_no_issues_found(self, mock_get_registry, mock_create_service):
        """Test when validation finds no issues."""
        # Mock successful authentication
        mock_service = Mock()
        mock_create_service.return_value = mock_service

        # Mock validator registry
        mock_validator = Mock()
        mock_validator.validate.return_value = {
            "fixes_applied": 0,
            "issues_found": 0,
            "errors": [],
        }
        mock_registry = {"empty_cells": mock_validator}
        mock_get_registry.return_value = mock_registry

        result = execute_validation(
            check={"id": "empty_cells", "mode": "flag"},
            sheet_url=self.valid_sheet_url,
            auth_secret=self.encoded_creds,
        )

        assert result["fixes_applied"] == 0
        assert result["issues_flagged"] == 0
        assert result["errors"] == []
        assert "No issues found" in result["automated_logs"]

    @patch("urarovite.core.api.create_sheets_service_from_encoded_creds")
    @patch("urarovite.core.api.get_validator_registry")
    def test_validator_errors_included(self, mock_get_registry, mock_create_service):
        """Test that validator errors are included in results."""
        # Mock successful authentication
        mock_service = Mock()
        mock_create_service.return_value = mock_service

        # Mock validator registry with errors
        mock_validator = Mock()
        mock_validator.validate.return_value = {
            "fixes_applied": 1,
            "issues_found": 0,
            "errors": ["Warning: Could not fix row 5", "Sheet is protected"],
        }
        mock_registry = {"empty_cells": mock_validator}
        mock_get_registry.return_value = mock_registry

        result = execute_validation(
            check={"id": "empty_cells", "mode": "fix"},
            sheet_url=self.valid_sheet_url,
            auth_secret=self.encoded_creds,
        )

        assert result["fixes_applied"] == 1
        assert result["issues_flagged"] == 0
        assert len(result["errors"]) == 2
        assert "Warning: Could not fix row 5" in result["errors"]
        assert "Sheet is protected" in result["errors"]

    @patch("urarovite.core.api.create_sheets_service_from_encoded_creds")
    @patch("urarovite.core.api.get_validator_registry")
    def test_subject_parameter_passed(self, mock_get_registry, mock_create_service):
        """Test that subject parameter is passed to authentication."""
        # Mock successful authentication
        mock_service = Mock()
        mock_create_service.return_value = mock_service

        # Mock validator registry
        mock_validator = Mock()
        mock_validator.validate.return_value = {
            "fixes_applied": 0,
            "issues_found": 0,
            "errors": [],
        }
        mock_registry = {"empty_cells": mock_validator}
        mock_get_registry.return_value = mock_registry

        execute_validation(
            check=self.valid_check,
            sheet_url=self.valid_sheet_url,
            auth_secret=self.encoded_creds,
            subject="user@example.com",
        )

        # Verify subject was passed to authentication
        mock_create_service.assert_called_once_with(
            self.encoded_creds, "user@example.com"
        )

    @patch("urarovite.core.api.create_sheets_service_from_encoded_creds")
    @patch("urarovite.core.api.get_validator_registry")
    def test_validation_error_handling(self, mock_get_registry, mock_create_service):
        """Test handling of ValidationError exceptions."""
        # Mock successful authentication
        mock_service = Mock()
        mock_create_service.return_value = mock_service

        # Mock validator that raises ValidationError
        mock_validator = Mock()
        mock_validator.validate.side_effect = ValidationError("Validation failed")
        mock_registry = {"empty_cells": mock_validator}
        mock_get_registry.return_value = mock_registry

        result = execute_validation(
            check=self.valid_check,
            sheet_url=self.valid_sheet_url,
            auth_secret=self.encoded_creds,
        )

        assert result["fixes_applied"] == 0
        assert result["issues_flagged"] == 0
        assert len(result["errors"]) == 1
        assert (
            "Validation error in check 'empty_cells': Validation failed"
            in result["errors"][0]
        )

    @patch("urarovite.core.api.create_sheets_service_from_encoded_creds")
    @patch("urarovite.core.api.get_validator_registry")
    def test_unexpected_error_handling(self, mock_get_registry, mock_create_service):
        """Test handling of unexpected exceptions."""
        # Mock successful authentication
        mock_service = Mock()
        mock_create_service.return_value = mock_service

        # Mock validator that raises unexpected error
        mock_validator = Mock()
        mock_validator.validate.side_effect = RuntimeError("Unexpected error")
        mock_registry = {"empty_cells": mock_validator}
        mock_get_registry.return_value = mock_registry

        result = execute_validation(
            check=self.valid_check,
            sheet_url=self.valid_sheet_url,
            auth_secret=self.encoded_creds,
        )

        assert result["fixes_applied"] == 0
        assert result["issues_flagged"] == 0
        assert len(result["errors"]) == 1
        assert (
            "Unexpected error in check 'empty_cells': Unexpected error"
            in result["errors"][0]
        )

    def test_result_structure(self):
        """Test that result always has the expected structure."""
        result = execute_validation(check=None, sheet_url="", auth_secret=None)

        # Should always have these keys
        required_keys = ["fixes_applied", "issues_flagged", "errors", "automated_logs"]
        for key in required_keys:
            assert key in result, f"Missing required key: {key}"

        # Check types
        assert isinstance(result["fixes_applied"], int)
        assert isinstance(result["issues_flagged"], int)
        assert isinstance(result["errors"], list)
        assert isinstance(result["automated_logs"], str)
