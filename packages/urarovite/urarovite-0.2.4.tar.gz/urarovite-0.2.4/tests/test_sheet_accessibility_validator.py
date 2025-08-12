"""Tests for the SheetAccessibilityValidator."""

import pytest
from unittest.mock import patch, MagicMock
from urarovite.validators.sheet_accessibility import SheetAccessibilityValidator


class TestSheetAccessibilityValidator:
    """Test the SheetAccessibilityValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = SheetAccessibilityValidator()
        self.mock_sheets_service = MagicMock()
        self.test_sheet_id = "test_sheet_123"
        self.test_auth_secret = "fake_auth_secret"

    @patch("urarovite.validators.sheet_accessibility.get_gspread_client")
    def test_validate_accessible_urls(self, mock_get_client):
        """Test validation of accessible Google Sheets URLs."""
        # Mock data with Google Sheets URLs
        test_data = [
            ["Header1", "Sheet URL", "Header3"],
            [
                "Data1",
                "https://docs.google.com/spreadsheets/d/accessible123/edit",
                "Data3",
            ],
            [
                "Data2",
                "https://docs.google.com/spreadsheets/d/accessible456/edit",
                "Data4",
            ],
        ]

        # Mock gspread client
        mock_client = MagicMock()
        mock_spreadsheet = MagicMock()
        mock_spreadsheet.title = "Test Sheet"
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_get_client.return_value = mock_client

        # Mock the _get_all_sheet_data method
        with patch.object(
            self.validator, "_get_all_sheet_data", return_value=test_data
        ):
            result = self.validator.validate(
                sheets_service=self.mock_sheets_service,
                sheet_id=self.test_sheet_id,
                mode="flag",
                auth_secret=self.test_auth_secret,
            )

        # Verify results
        assert result["issues_found"] == 0
        assert result["fixes_applied"] == 0
        assert len(result["errors"]) == 0
        assert "accessible_count" in result["details"]
        assert result["details"]["accessible_count"] == 2

    @patch("urarovite.validators.sheet_accessibility.get_gspread_client")
    def test_validate_inaccessible_urls(self, mock_get_client):
        """Test validation of inaccessible Google Sheets URLs."""
        # Mock data with mix of accessible and inaccessible URLs
        test_data = [
            ["Header1", "Sheet URL", "Header3"],
            [
                "Data1",
                "https://docs.google.com/spreadsheets/d/accessible123/edit",
                "Data3",
            ],
            [
                "Data2",
                "https://docs.google.com/spreadsheets/d/inaccessible456/edit",
                "Data4",
            ],
        ]

        # Mock gspread client with selective access
        mock_client = MagicMock()

        def mock_open_by_key(sheet_id):
            if "inaccessible" in sheet_id:
                raise Exception("403 Forbidden")
            mock_spreadsheet = MagicMock()
            mock_spreadsheet.title = "Test Sheet"
            return mock_spreadsheet

        mock_client.open_by_key.side_effect = mock_open_by_key
        mock_get_client.return_value = mock_client

        # Mock the _get_all_sheet_data method
        with patch.object(
            self.validator, "_get_all_sheet_data", return_value=test_data
        ):
            result = self.validator.validate(
                sheets_service=self.mock_sheets_service,
                sheet_id=self.test_sheet_id,
                mode="flag",
                auth_secret=self.test_auth_secret,
            )

        # Verify results
        assert result["issues_found"] == 1
        assert result["fixes_applied"] == 0
        assert len(result["errors"]) == 0
        assert "inaccessible_urls" in result["details"]
        assert len(result["details"]["inaccessible_urls"]) == 1
        assert result["details"]["accessible_count"] == 1

    def test_validate_no_urls_found(self):
        """Test validation when no Google Sheets URLs are found."""
        # Mock data without Google Sheets URLs
        test_data = [
            ["Header1", "Header2", "Header3"],
            ["Data1", "https://example.com", "Data3"],
            ["Data2", "Not a URL", "Data4"],
        ]

        # Mock the _get_all_sheet_data method
        with patch.object(
            self.validator, "_get_all_sheet_data", return_value=test_data
        ):
            result = self.validator.validate(
                sheets_service=self.mock_sheets_service,
                sheet_id=self.test_sheet_id,
                mode="flag",
                auth_secret=self.test_auth_secret,
            )

        # Verify results
        assert result["issues_found"] == 0
        assert result["fixes_applied"] == 0
        assert len(result["errors"]) == 1
        assert "No Google Sheets URLs found" in result["errors"][0]

    def test_validate_empty_sheet(self):
        """Test validation of empty sheet."""
        # Mock the _get_all_sheet_data method to return empty data
        with patch.object(self.validator, "_get_all_sheet_data", return_value=[]):
            result = self.validator.validate(
                sheets_service=self.mock_sheets_service,
                sheet_id=self.test_sheet_id,
                mode="flag",
                auth_secret=self.test_auth_secret,
            )

        # Verify results
        assert result["issues_found"] == 0
        assert result["fixes_applied"] == 0
        assert len(result["errors"]) == 1
        assert "Sheet is empty" in result["errors"][0]

    def test_validate_missing_auth_secret(self):
        """Test validation when auth_secret is missing."""
        test_data = [
            ["Header1", "Sheet URL", "Header3"],
            ["Data1", "https://docs.google.com/spreadsheets/d/test123/edit", "Data3"],
        ]

        # Mock the _get_all_sheet_data method
        with patch.object(
            self.validator, "_get_all_sheet_data", return_value=test_data
        ):
            result = self.validator.validate(
                sheets_service=self.mock_sheets_service,
                sheet_id=self.test_sheet_id,
                mode="flag",
                # No auth_secret provided
            )

        # Verify results
        assert result["issues_found"] == 0
        assert result["fixes_applied"] == 0
        assert len(result["errors"]) == 1
        assert "Authentication credentials required" in result["errors"][0]

    def test_detect_url_columns(self):
        """Test URL column detection."""
        test_data = [
            ["Name", "Sheet URL", "Description", "Another URL"],
            [
                "Test1",
                "https://docs.google.com/spreadsheets/d/abc123/edit",
                "Desc1",
                "https://example.com",
            ],
            [
                "Test2",
                "https://docs.google.com/spreadsheets/d/def456/edit",
                "Desc2",
                "https://docs.google.com/spreadsheets/d/ghi789/edit",
            ],
        ]

        url_columns = self.validator._detect_url_columns(test_data)

        # Should detect columns 2 and 4 (1-based indexing)
        assert 2 in url_columns  # "Sheet URL" column
        assert 4 in url_columns  # "Another URL" column
        assert len(url_columns) == 2

    def test_extract_sheet_id(self):
        """Test spreadsheet ID extraction from URLs."""
        # Valid URLs
        assert (
            self.validator._extract_sheet_id(
                "https://docs.google.com/spreadsheets/d/1ABC123def456/edit"
            )
            == "1ABC123def456"
        )

        assert (
            self.validator._extract_sheet_id(
                "https://docs.google.com/spreadsheets/d/test-sheet_123/edit?usp=sharing"
            )
            == "test-sheet_123"
        )

        # Invalid URLs
        assert self.validator._extract_sheet_id("https://example.com") is None
        assert self.validator._extract_sheet_id("") is None
        assert self.validator._extract_sheet_id(None) is None

    def test_fix_mode_error(self):
        """Test that fix mode returns appropriate error."""
        test_data = [
            ["Header1", "Sheet URL"],
            ["Data1", "https://docs.google.com/spreadsheets/d/inaccessible123/edit"],
        ]

        with patch.object(
            self.validator, "_get_all_sheet_data", return_value=test_data
        ):
            with patch.object(self.validator, "_check_url_accessibility") as mock_check:
                mock_check.return_value = {"accessible": False, "error": "forbidden"}

                result = self.validator.validate(
                    sheets_service=self.mock_sheets_service,
                    sheet_id=self.test_sheet_id,
                    mode="fix",
                    auth_secret=self.test_auth_secret,
                )

        # Verify that fix mode produces an error
        assert result["issues_found"] == 1
        assert result["fixes_applied"] == 0
        assert len(result["errors"]) == 1
        assert "Cannot auto-fix inaccessible URLs" in result["errors"][0]
