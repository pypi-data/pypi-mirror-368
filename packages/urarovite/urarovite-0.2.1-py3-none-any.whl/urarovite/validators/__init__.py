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
)
from urarovite.validators.format_validation import (
    EmailValidator,
    PhoneNumberValidator,
    DateValidator,
    URLValidator,
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
    _VALIDATOR_REGISTRY["inconsistent_formatting"] = InconsistentFormattingValidator()
    _VALIDATOR_REGISTRY["missing_required_fields"] = MissingRequiredFieldsValidator()
    
    # Format validation validators
    _VALIDATOR_REGISTRY["invalid_emails"] = EmailValidator()
    _VALIDATOR_REGISTRY["invalid_phone_numbers"] = PhoneNumberValidator()
    _VALIDATOR_REGISTRY["invalid_dates"] = DateValidator()
    _VALIDATOR_REGISTRY["invalid_urls"] = URLValidator()


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
    # Format validation validators
    "EmailValidator",
    "PhoneNumberValidator",
    "DateValidator",
    "URLValidator",
    # Registry functions
    "get_validator_registry",
    "get_validator",
]
