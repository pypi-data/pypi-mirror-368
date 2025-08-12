"""Validation modules for the Urarovite library.

This module provides all available validators and a registry system
for managing and accessing them.
"""

from typing import Dict

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.validators.data_quality import (
    EmptyCellsValidator,
    DuplicateRowsValidator,
    InconsistentFormattingValidator,
    MissingRequiredFieldsValidator,
    TabNameValidator,
)
from urarovite.validators.format_validation import (
    EmailValidator,
    PhoneNumberValidator,
    DateValidator,
    URLValidator,
    VerificationRangesValidator,
)
from urarovite.validators.tab_name_consistency import TabNameConsistencyValidator
from urarovite.validators.open_ended_ranges import OpenEndedRangesValidator
from urarovite.validators.sheet_name_quoting import SheetNameQuotingValidator
from urarovite.validators.sheet_accessibility import SheetAccessibilityValidator
from urarovite.validators.identical_outside_ranges import (
    IdenticalOutsideRangesValidator
)

# Registry of all available validators
_VALIDATOR_REGISTRY: Dict[str, BaseValidator] = {}


def _initialize_registry() -> None:
    """Initialize the validator registry with all available validators."""
    global _VALIDATOR_REGISTRY

    if _VALIDATOR_REGISTRY:
        return  # Already initialized

    # Data quality validators
    _VALIDATOR_REGISTRY["empty_cells"] = EmptyCellsValidator()
    _VALIDATOR_REGISTRY["duplicate_rows"] = DuplicateRowsValidator()
    _VALIDATOR_REGISTRY["inconsistent_formatting"] = (
        InconsistentFormattingValidator()
    )
    _VALIDATOR_REGISTRY["missing_required_fields"] = (
        MissingRequiredFieldsValidator()
    )
    _VALIDATOR_REGISTRY["tab_names"] = TabNameValidator()

    # Format validation validators
    _VALIDATOR_REGISTRY["invalid_emails"] = EmailValidator()
    _VALIDATOR_REGISTRY["invalid_phone_numbers"] = PhoneNumberValidator()
    _VALIDATOR_REGISTRY["invalid_dates"] = DateValidator()
    _VALIDATOR_REGISTRY["invalid_urls"] = URLValidator()

    # Spreadsheet comparison validators
    _VALIDATOR_REGISTRY["tab_name_consistency"] = TabNameConsistencyValidator()
    _VALIDATOR_REGISTRY["open_ended_ranges"] = OpenEndedRangesValidator()
    _VALIDATOR_REGISTRY["invalid_verification_ranges"] = VerificationRangesValidator()

    # Spreadsheet range validators
    _VALIDATOR_REGISTRY["sheet_name_quoting"] = SheetNameQuotingValidator()

    # Sheet accessibility validator
    _VALIDATOR_REGISTRY["sheet_accessibility"] = SheetAccessibilityValidator()
    _VALIDATOR_REGISTRY["identical_outside_ranges"] = (
        IdenticalOutsideRangesValidator()
    )


def get_validator_registry() -> Dict[str, BaseValidator]:
    """Get the registry of all available validators.

    Returns:
        Dictionary mapping validator IDs to validator instances
    """
    _initialize_registry()
    return _VALIDATOR_REGISTRY.copy()


def get_validator(validator_id: str) -> BaseValidator:
    """Get a specific validator by ID.

    Args:
        validator_id: The ID of the validator to retrieve

    Returns:
        The validator instance

    Raises:
        KeyError: If validator ID is not found
    """
    _initialize_registry()
    return _VALIDATOR_REGISTRY[validator_id]


# Initialize registry on import
_initialize_registry()

__all__ = [
    # Base classes
    "BaseValidator",
    "ValidationResult",
    # Data quality validators
    "EmptyCellsValidator",
    "DuplicateRowsValidator",
    "InconsistentFormattingValidator",
    "MissingRequiredFieldsValidator",
    "TabNameValidator",
    # Format validation validators
    "EmailValidator",
    "PhoneNumberValidator",
    "DateValidator",
    "URLValidator",
    # Spreadsheet comparison validators
    "TabNameConsistencyValidator",
    "OpenEndedRangesValidator",
    "VerificationRangesValidator",
    # Spreadsheet range validators
    "SheetNameQuotingValidator",
    # Sheet accessibility validator
    "SheetAccessibilityValidator",
    "IdenticalOutsideRangesValidator",
    # Registry functions
    "get_validator_registry",
    "get_validator",
]
