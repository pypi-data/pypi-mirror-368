"""Sheet accessibility validator for Google Sheets URLs.

This validator checks whether Google Sheets URLs are accessible using
gspread with base64-encoded service account credentials.
"""

import re
from typing import Any, Dict, List

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.exceptions import ValidationError
from urarovite.auth.google_sheets import get_gspread_client


class SheetAccessibilityValidator(BaseValidator):
    """Validator for checking Google Sheets URL accessibility."""

    # Regex to extract spreadsheet ID from Google Sheets URLs
    _ID_RE = re.compile(r"/d/([a-zA-Z0-9-_]+)")

    def __init__(self) -> None:
        super().__init__(
            validator_id="sheet_accessibility",
            name="Check Sheet Accessibility",
            description="Validates that Google Sheets URLs are accessible",
        )

    def validate(
        self,
        sheets_service: Any,
        sheet_id: str,
        mode: str,
        url_columns: List[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Validate Google Sheets URL accessibility.

        Args:
            sheets_service: Google Sheets API service instance (not used,
                           we use gspread directly)
            sheet_id: ID of the spreadsheet to validate
            mode: Either "fix" (not applicable) or "flag" (report only)
            url_columns: List of 1-based column indices containing URLs

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

            # Auto-detect URL columns if not specified
            if url_columns is None:
                url_columns = self._detect_url_columns(data)
                if not url_columns:
                    # Return empty result instead of error
                    result.details["message"] = "No Google Sheets URLs found in data"
                    result.details["accessible_count"] = 0
                    result.details["inaccessible_urls"] = []
                    return result.to_dict()

            # Get auth credentials from sheets_service context
            # Note: This is a workaround since we need gspread client
            auth_secret = kwargs.get("auth_secret")
            subject = kwargs.get("subject")

            if not auth_secret:
                # Return empty result instead of error
                result.details["message"] = "Authentication credentials not provided"
                result.details["accessible_count"] = 0
                result.details["inaccessible_urls"] = []
                return result.to_dict()

            inaccessible_urls = []
            accessible_count = 0

            # Check each URL in the specified columns
            for row_idx, row in enumerate(data):
                if row_idx == 0:  # Skip header row
                    continue

                for col_idx in url_columns:
                    if col_idx <= len(row):
                        url = row[col_idx - 1]  # Convert to 0-based index
                        if url and isinstance(url, str):
                            accessibility_result = self._check_url_accessibility(
                                url, auth_secret, subject
                            )

                            if not accessibility_result["accessible"]:
                                inaccessible_urls.append(
                                    {
                                        "row": row_idx + 1,
                                        "column": col_idx,
                                        "url": url,
                                        "error": accessibility_result["error"],
                                    }
                                )
                                result.add_issue()
                            else:
                                accessible_count += 1

            # Record results
            if inaccessible_urls:
                result.details["inaccessible_urls"] = inaccessible_urls
                result.details["accessible_count"] = accessible_count
                result.set_automated_log(f"Inaccessible URLs: {len(inaccessible_urls)} sheets")

                # Note: Fix mode does nothing for this validator since we cannot
                # automatically fix inaccessible URLs
            else:
                result.details["accessible_count"] = accessible_count
                result.details["message"] = "All URLs are accessible"
                result.set_automated_log("No issues found")

        except ValidationError:
            raise
        except Exception as e:
            result.add_error(f"Unexpected error: {str(e)}")

        return result.to_dict()

    def _detect_url_columns(self, data: List[List[Any]]) -> List[int]:
        """Auto-detect columns containing Google Sheets URLs."""
        url_columns = []

        if not data:
            return url_columns

        # Check first few rows for URLs
        sample_rows = data[: min(5, len(data))]

        for col_idx in range(len(data[0]) if data[0] else 0):
            contains_urls = False

            for row in sample_rows:
                if col_idx < len(row) and row[col_idx]:
                    cell_value = str(row[col_idx])
                    if "docs.google.com/spreadsheets" in cell_value:
                        contains_urls = True
                        break

            if contains_urls:
                url_columns.append(col_idx + 1)  # Convert to 1-based

        return url_columns

    def _extract_sheet_id(self, url: str) -> str | None:
        """Extract spreadsheet ID from Google Sheets URL."""
        if not url:
            return None
        match = self._ID_RE.search(url)
        return match.group(1) if match else None

    def _check_url_accessibility(
        self, url: str, auth_secret: str, subject: str | None = None
    ) -> Dict[str, Any]:
        """Check if a Google Sheets URL is accessible."""
        spreadsheet_id = self._extract_sheet_id(url)

        if not spreadsheet_id:
            return {"accessible": False, "error": "invalid_url_format"}

        try:
            client = get_gspread_client(auth_secret, subject=subject)

            # Try to access the spreadsheet
            spreadsheet = client.open_by_key(spreadsheet_id)

            # Access a basic property to verify accessibility
            _ = spreadsheet.title

            return {"accessible": True, "error": None}

        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg or "Forbidden" in error_msg:
                error_type = "forbidden"
            elif "404" in error_msg or "not found" in error_msg.lower():
                error_type = "not_found"
            else:
                error_type = f"request_exception:{e.__class__.__name__}"

            return {"accessible": False, "error": error_type}
