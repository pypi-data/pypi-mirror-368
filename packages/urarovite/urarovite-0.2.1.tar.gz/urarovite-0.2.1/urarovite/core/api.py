"""Main API functions for the Urarovite validation library.

This module provides the two required functions that integrate with the
Uvarolite batch processing system:
1. get_available_validation_criteria() - Returns all supported validation criteria
2. execute_validation() - Executes validation checks on Google Sheets
"""

from __future__ import annotations

import logging
from typing import Any

from urarovite.config import VALIDATION_CRITERIA
from urarovite.validators import get_validator_registry
from urarovite.auth.google_sheets import create_sheets_service_from_encoded_creds
from urarovite.utils.sheets import extract_sheet_id
from urarovite.core.exceptions import (
    ValidationError,
    AuthenticationError,
    SheetAccessError,
)

# Set up logging
logger = logging.getLogger(__name__)


def get_available_validation_criteria() -> list[dict[str, str]]:
    """Return list of all validation criteria this library supports.

    Returns:
        List of criteria dictionaries with 'id' and 'name' fields

    Example:
        [
            {"id": "empty_cells", "name": "Fix Empty Cells"},
            {"id": "duplicate_rows", "name": "Remove Duplicate Rows"},
            {"id": "invalid_emails", "name": "Validate Email Addresses"},
            ...
        ]
    """
    try:
        # Convert from our internal format to the required API format
        return [
            {
                "id": criterion["id"],
                "name": criterion["name"],
                "description": criterion["description"],
                "supports_fix": criterion["supports_fix"],
                "supports_flag": criterion["supports_flag"],
            }
            for criterion in VALIDATION_CRITERIA
        ]
    except Exception as e:
        logger.error(f"Error getting validation criteria: {e}")
        # Even if there's an error, return an empty list rather than raising
        return []


def execute_validation(
    check: dict[str, str],
    sheet_url: str,
    auth_secret: str | None = None,
    subject: str | None = None,
) -> dict[str, Any]:
    """Execute a validation check on a Google Sheets document.

    Args:
        check: Single validation check to apply, containing:
            - id: Must match an ID from get_available_validation_criteria()
            - mode: Either "fix" (auto-correct) or "flag" (report only)
        sheet_url: Google Sheets URL to validate
        auth_secret: Base64 encoded service account credentials
        subject: Optional email subject for delegation (for domain-wide delegation)

    Returns:
        Dict with validation results:
        {
            "fixes_applied": int,      # Count of issues fixed
            "issues_flagged": int,     # Count of issues found but not fixed
            "errors": list[str],       # Error messages (empty list if no errors)
            "automated_logs": str      # Log messages from the validation process
        }

    Example:
        result = execute_validation(
            check={"id": "empty_cells", "mode": "fix"},
            sheet_url=sheet_url,
            auth_secret="eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsIC4uLn0="
        )
    """
    result = {
        "fixes_applied": 0,
        "issues_flagged": 0,
        "errors": [],
        "automated_logs": "",
    }

    try:
        # Validate inputs
        if not check:
            result["errors"].append("No validation check specified")
            return result

        if not sheet_url:
            result["errors"].append("Sheet URL is required")
            return result

        if not auth_secret:
            result["errors"].append(
                "Authentication credentials are required (provide auth_secret with base64 encoded service account)"
            )
            return result

        # Extract sheet ID from URL
        sheet_id = extract_sheet_id(sheet_url)
        if not sheet_id:
            result["errors"].append(f"Invalid Google Sheets URL: {sheet_url}")
            return result

        # Create Google Sheets service from base64 encoded credentials
        try:
            sheets_service = create_sheets_service_from_encoded_creds(
                auth_secret, subject
            )
        except Exception as e:
            result["errors"].append(f"Authentication failed: {str(e)}")
            return result

        # Get validator registry
        validator_registry = get_validator_registry()

        # Process the validation check
        try:
            check_id = check.get("id")
            mode = check.get("mode", "flag")  # Default to flag mode

            if not check_id:
                result["errors"].append("Check missing required 'id' field")
                return result

            if mode not in ["fix", "flag"]:
                result["errors"].append(
                    f"Invalid mode '{mode}' for check '{check_id}'. Must be 'fix' or 'flag'"
                )
                return result

            # Get the validator for this check
            validator = validator_registry.get(check_id)
            if not validator:
                result["errors"].append(f"Unknown validation check: '{check_id}'")
                return result

            logger.info(f"Running validation check: {check_id} in {mode} mode")

            # Execute the validation
            validation_result = validator.validate(
                sheets_service=sheets_service, sheet_id=sheet_id, mode=mode
            )

            # Aggregate results
            if mode == "fix":
                result["fixes_applied"] += validation_result.get("fixes_applied", 0)
            else:
                result["issues_flagged"] += validation_result.get("issues_found", 0)

            # Add any validator-specific errors
            validator_errors = validation_result.get("errors", [])
            result["errors"].extend(validator_errors)

            # Add automated logs
            logs = []
            if mode == "fix" and result["fixes_applied"] > 0:
                logs.append(f"Applied {result['fixes_applied']} fixes")
            elif mode == "flag" and result["issues_flagged"] > 0:
                logs.append(f"Flagged {result['issues_flagged']} issues")
            else:
                logs.append("No issues found")

            # Add any additional details from the validation result
            if "details" in validation_result:
                details = validation_result["details"]
                if isinstance(details, dict):
                    for key, value in details.items():
                        if value:
                            logs.append(f"{key}: {value}")

            result["automated_logs"] = "; ".join(logs)

        except ValidationError as e:
            result["errors"].append(f"Validation error in check '{check_id}': {str(e)}")
        except Exception as e:
            result["errors"].append(f"Unexpected error in check '{check_id}': {str(e)}")
            logger.exception(f"Unexpected error in validation check {check_id}")

    except AuthenticationError as e:
        result["errors"].append(f"Authentication error: {str(e)}")
    except SheetAccessError as e:
        result["errors"].append(f"Sheet access error: {str(e)}")
    except Exception as e:
        result["errors"].append(f"Unexpected error: {str(e)}")
        logger.exception("Unexpected error in execute_validation")

    return result
