"""Format validation validators for common data formats.

This module implements validators for checking and fixing common data formats
such as email addresses, phone numbers, dates, and URLs.
"""

import re
from datetime import datetime
from typing import Any, Dict, List
from urllib.parse import urlparse

from urarovite.validators.base import BaseValidator, ValidationResult
from urarovite.core.exceptions import ValidationError


class EmailValidator(BaseValidator):
    """Validator for email address formats."""
    
    # Basic email regex pattern
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    def __init__(self) -> None:
        super().__init__(
            validator_id="invalid_emails",
            name="Validate Email Addresses",
            description="Checks email format and optionally flags invalid emails"
        )
    
    def validate(
        self, 
        sheets_service: Any, 
        sheet_id: str, 
        mode: str,
        email_columns: List[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Validate email addresses in specified columns.
        
        Args:
            sheets_service: Google Sheets API service instance
            sheet_id: ID of the spreadsheet to validate
            mode: Either "fix" (not applicable) or "flag" (report only)
            email_columns: List of 1-based column indices containing emails
            
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
            
            # Auto-detect email columns if not specified
            if email_columns is None:
                email_columns = self._detect_email_columns(data)
            
            invalid_emails = []
            
            # Check each specified column for invalid emails
            for row_idx, row in enumerate(data):
                for col_idx in email_columns:
                    col_zero_based = col_idx - 1
                    
                    if col_zero_based < len(row) and row[col_zero_based]:
                        email = str(row[col_zero_based]).strip()
                        
                        if email and not self._is_valid_email(email):
                            invalid_emails.append({
                                "row": row_idx + 1,
                                "col": col_idx,
                                "email": email,
                                "issue": "Invalid format"
                            })
            
            # Record results
            if invalid_emails:
                result.add_issue(len(invalid_emails))
                result.details["invalid_emails"] = invalid_emails
                
                if mode == "fix":
                    result.add_error("Cannot auto-fix invalid emails - manual review needed")
            
        except ValidationError:
            raise
        except Exception as e:
            result.add_error(f"Unexpected error: {str(e)}")
        
        return result.to_dict()
    
    def _is_valid_email(self, email: str) -> bool:
        """Check if an email address is valid."""
        return bool(self.EMAIL_PATTERN.match(email))
    
    def _detect_email_columns(self, data: List[List[Any]]) -> List[int]:
        """Auto-detect columns that likely contain email addresses."""
        email_columns = []
        
        if not data:
            return email_columns
        
        # Check first few rows for email-like content
        sample_rows = data[:min(10, len(data))]
        
        for col_idx in range(len(data[0]) if data else 0):
            email_count = 0
            total_non_empty = 0
            
            for row in sample_rows:
                if col_idx < len(row) and row[col_idx]:
                    total_non_empty += 1
                    if self._is_valid_email(str(row[col_idx]).strip()):
                        email_count += 1
            
            # If more than 50% of non-empty cells look like emails, include this column
            if total_non_empty > 0 and email_count / total_non_empty > 0.5:
                email_columns.append(col_idx + 1)  # Convert to 1-based
        
        return email_columns


class PhoneNumberValidator(BaseValidator):
    """Validator for phone number formats."""
    
    # Basic phone number patterns
    PHONE_PATTERNS = [
        re.compile(r'^\+?1?[-.\s]?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})$'),  # US format
        re.compile(r'^\+?(\d{1,3})[-.\s]?(\d{3,4})[-.\s]?(\d{3,4})[-.\s]?(\d{3,4})$'),  # International
    ]
    
    def __init__(self) -> None:
        super().__init__(
            validator_id="invalid_phone_numbers",
            name="Validate Phone Numbers", 
            description="Validates phone number formats and consistency"
        )
    
    def validate(
        self, 
        sheets_service: Any, 
        sheet_id: str, 
        mode: str,
        phone_columns: List[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Validate phone numbers in specified columns.
        
        Args:
            sheets_service: Google Sheets API service instance
            sheet_id: ID of the spreadsheet to validate
            mode: Either "fix" (standardize format) or "flag" (report only)
            phone_columns: List of 1-based column indices containing phone numbers
            
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
            
            # Auto-detect phone columns if not specified
            if phone_columns is None:
                phone_columns = self._detect_phone_columns(data)
            
            invalid_phones = []
            fixed_data = []
            
            # Check and optionally fix phone numbers
            for row_idx, row in enumerate(data):
                fixed_row = list(row)
                
                for col_idx in phone_columns:
                    col_zero_based = col_idx - 1
                    
                    if col_zero_based < len(row) and row[col_zero_based]:
                        phone = str(row[col_zero_based]).strip()
                        
                        if phone:
                            standardized = self._standardize_phone(phone)
                            
                            if not standardized:
                                invalid_phones.append({
                                    "row": row_idx + 1,
                                    "col": col_idx,
                                    "phone": phone,
                                    "issue": "Invalid format"
                                })
                            elif mode == "fix" and standardized != phone:
                                fixed_row[col_zero_based] = standardized
                
                fixed_data.append(fixed_row)
            
            # Record results
            if invalid_phones:
                if mode == "fix":
                    # Update the sheet with fixed data
                    self._update_sheet_data(sheets_service, sheet_id, None, fixed_data)
                    result.add_fix(len([p for p in invalid_phones if self._standardize_phone(p["phone"])]))
                    result.details["standardized_phones"] = invalid_phones
                else:
                    result.add_issue(len(invalid_phones))
                    result.details["invalid_phones"] = invalid_phones
            
        except ValidationError:
            raise
        except Exception as e:
            result.add_error(f"Unexpected error: {str(e)}")
        
        return result.to_dict()
    
    def _standardize_phone(self, phone: str) -> str:
        """Standardize phone number format."""
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Try to match against patterns and standardize
        for pattern in self.PHONE_PATTERNS:
            if pattern.match(phone):
                # For US numbers, standardize to (XXX) XXX-XXXX
                digits = re.sub(r'[^\d]', '', phone)
                if len(digits) == 10:
                    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
                elif len(digits) == 11 and digits[0] == '1':
                    return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        
        return ""  # Invalid phone number
    
    def _detect_phone_columns(self, data: List[List[Any]]) -> List[int]:
        """Auto-detect columns that likely contain phone numbers."""
        phone_columns = []
        
        if not data:
            return phone_columns
        
        # Check first few rows for phone-like content
        sample_rows = data[:min(10, len(data))]
        
        for col_idx in range(len(data[0]) if data else 0):
            phone_count = 0
            total_non_empty = 0
            
            for row in sample_rows:
                if col_idx < len(row) and row[col_idx]:
                    total_non_empty += 1
                    phone_str = str(row[col_idx]).strip()
                    if any(pattern.match(phone_str) for pattern in self.PHONE_PATTERNS):
                        phone_count += 1
            
            # If more than 50% of non-empty cells look like phone numbers, include this column
            if total_non_empty > 0 and phone_count / total_non_empty > 0.5:
                phone_columns.append(col_idx + 1)  # Convert to 1-based
        
        return phone_columns


class DateValidator(BaseValidator):
    """Validator for date formats."""
    
    # Common date formats to try
    DATE_FORMATS = [
        "%Y-%m-%d",      # 2023-12-25
        "%m/%d/%Y",      # 12/25/2023
        "%d/%m/%Y",      # 25/12/2023
        "%Y/%m/%d",      # 2023/12/25
        "%m-%d-%Y",      # 12-25-2023
        "%d-%m-%Y",      # 25-12-2023
        "%B %d, %Y",     # December 25, 2023
        "%d %B %Y",      # 25 December 2023
        "%m/%d/%y",      # 12/25/23
        "%d/%m/%y",      # 25/12/23
    ]
    
    def __init__(self) -> None:
        super().__init__(
            validator_id="invalid_dates",
            name="Validate Date Formats",
            description="Checks and standardizes date formats"
        )
    
    def validate(
        self, 
        sheets_service: Any, 
        sheet_id: str, 
        mode: str,
        date_columns: List[int] = None,
        target_format: str = "%Y-%m-%d",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Validate and optionally standardize date formats.
        
        Args:
            sheets_service: Google Sheets API service instance
            sheet_id: ID of the spreadsheet to validate
            mode: Either "fix" (standardize format) or "flag" (report only)
            date_columns: List of 1-based column indices containing dates
            target_format: Target date format for standardization
            
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
            
            # Auto-detect date columns if not specified
            if date_columns is None:
                date_columns = self._detect_date_columns(data)
            
            date_issues = []
            fixed_data = []
            
            # Check and optionally fix dates
            for row_idx, row in enumerate(data):
                fixed_row = list(row)
                
                for col_idx in date_columns:
                    col_zero_based = col_idx - 1
                    
                    if col_zero_based < len(row) and row[col_zero_based]:
                        date_str = str(row[col_zero_based]).strip()
                        
                        if date_str:
                            parsed_date, original_format = self._parse_date(date_str)
                            
                            if not parsed_date:
                                date_issues.append({
                                    "row": row_idx + 1,
                                    "col": col_idx,
                                    "date": date_str,
                                    "issue": "Invalid date format"
                                })
                            elif mode == "fix" and original_format != target_format:
                                standardized = parsed_date.strftime(target_format)
                                fixed_row[col_zero_based] = standardized
                                date_issues.append({
                                    "row": row_idx + 1,
                                    "col": col_idx,
                                    "original": date_str,
                                    "standardized": standardized
                                })
                
                fixed_data.append(fixed_row)
            
            # Record results
            if date_issues:
                if mode == "fix":
                    # Update the sheet with fixed data
                    self._update_sheet_data(sheets_service, sheet_id, None, fixed_data)
                    valid_fixes = [d for d in date_issues if "standardized" in d]
                    result.add_fix(len(valid_fixes))
                    result.details["standardized_dates"] = valid_fixes
                    
                    invalid_dates = [d for d in date_issues if "issue" in d]
                    if invalid_dates:
                        result.add_issue(len(invalid_dates))
                        result.details["invalid_dates"] = invalid_dates
                else:
                    result.add_issue(len(date_issues))
                    result.details["date_issues"] = date_issues
            
        except ValidationError:
            raise
        except Exception as e:
            result.add_error(f"Unexpected error: {str(e)}")
        
        return result.to_dict()
    
    def _parse_date(self, date_str: str) -> tuple[datetime, str]:
        """Try to parse a date string using various formats."""
        for fmt in self.DATE_FORMATS:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed, fmt
            except ValueError:
                continue
        return None, None
    
    def _detect_date_columns(self, data: List[List[Any]]) -> List[int]:
        """Auto-detect columns that likely contain dates."""
        date_columns = []
        
        if not data:
            return date_columns
        
        # Check first few rows for date-like content
        sample_rows = data[:min(10, len(data))]
        
        for col_idx in range(len(data[0]) if data else 0):
            date_count = 0
            total_non_empty = 0
            
            for row in sample_rows:
                if col_idx < len(row) and row[col_idx]:
                    total_non_empty += 1
                    date_str = str(row[col_idx]).strip()
                    if self._parse_date(date_str)[0]:
                        date_count += 1
            
            # If more than 50% of non-empty cells look like dates, include this column
            if total_non_empty > 0 and date_count / total_non_empty > 0.5:
                date_columns.append(col_idx + 1)  # Convert to 1-based
        
        return date_columns


class URLValidator(BaseValidator):
    """Validator for URL formats."""
    
    def __init__(self) -> None:
        super().__init__(
            validator_id="invalid_urls",
            name="Validate URLs",
            description="Validates URL format and accessibility"
        )
    
    def validate(
        self, 
        sheets_service: Any, 
        sheet_id: str, 
        mode: str,
        url_columns: List[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Validate URLs in specified columns.
        
        Args:
            sheets_service: Google Sheets API service instance
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
            
            invalid_urls = []
            
            # Check URLs
            for row_idx, row in enumerate(data):
                for col_idx in url_columns:
                    col_zero_based = col_idx - 1
                    
                    if col_zero_based < len(row) and row[col_zero_based]:
                        url = str(row[col_zero_based]).strip()
                        
                        if url and not self._is_valid_url(url):
                            invalid_urls.append({
                                "row": row_idx + 1,
                                "col": col_idx,
                                "url": url,
                                "issue": "Invalid URL format"
                            })
            
            # Record results
            if invalid_urls:
                result.add_issue(len(invalid_urls))
                result.details["invalid_urls"] = invalid_urls
                
                if mode == "fix":
                    result.add_error("Cannot auto-fix invalid URLs - manual review needed")
            
        except ValidationError:
            raise
        except Exception as e:
            result.add_error(f"Unexpected error: {str(e)}")
        
        return result.to_dict()
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if a URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _detect_url_columns(self, data: List[List[Any]]) -> List[int]:
        """Auto-detect columns that likely contain URLs."""
        url_columns = []
        
        if not data:
            return url_columns
        
        # Check first few rows for URL-like content
        sample_rows = data[:min(10, len(data))]
        
        for col_idx in range(len(data[0]) if data else 0):
            url_count = 0
            total_non_empty = 0
            
            for row in sample_rows:
                if col_idx < len(row) and row[col_idx]:
                    total_non_empty += 1
                    url_str = str(row[col_idx]).strip()
                    if self._is_valid_url(url_str):
                        url_count += 1
            
            # If more than 50% of non-empty cells look like URLs, include this column
            if total_non_empty > 0 and url_count / total_non_empty > 0.5:
                url_columns.append(col_idx + 1)  # Convert to 1-based
        
        return url_columns
