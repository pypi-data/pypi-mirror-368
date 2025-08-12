"""Tests for backward compatibility of imports after the refactoring."""

import pytest
from unittest.mock import patch, Mock


class TestCheckerModuleImports:
    """Test that the checker module maintains backward compatibility."""

    def test_checker_init_imports(self):
        """Test that checker/__init__.py exports work correctly."""
        # These imports should work without error
        from urarovite.checker import get_gspread_client, clear_service_cache

        # Verify they are callable
        assert callable(get_gspread_client)
        assert callable(clear_service_cache)

    def test_checker_auth_imports(self):
        """Test that checker/auth.py maintains backward compatibility."""
        # These imports should work without error
        from urarovite.checker.auth import get_gspread_client, clear_service_cache

        # Verify they are callable
        assert callable(get_gspread_client)
        assert callable(clear_service_cache)

    def test_checker_utils_imports(self):
        """Test that checker/utils.py maintains all utility imports."""
        # Test all the utility function imports
        from urarovite.checker.utils import (
            # URL and range parsing
            extract_sheet_id,
            split_segments,
            strip_outer_single_quotes,
            extract_sheet_and_range,
            parse_tab_token,
            parse_referenced_tabs,
            # Sheet data fetching
            fetch_sheet_tabs,
            get_sheet_values,
            # Constants
            SHEET_ID_RE,
            SEGMENT_SEPARATOR,
            COL_RE,
            ROW_RE,
        )

        # Verify all are available
        assert callable(extract_sheet_id)
        assert callable(split_segments)
        assert callable(strip_outer_single_quotes)
        assert callable(extract_sheet_and_range)
        assert callable(parse_tab_token)
        assert callable(parse_referenced_tabs)
        assert callable(fetch_sheet_tabs)
        assert callable(get_sheet_values)

        # Verify constants exist
        assert SHEET_ID_RE is not None
        assert SEGMENT_SEPARATOR is not None
        assert COL_RE is not None
        assert ROW_RE is not None

    def test_utils_module_imports(self):
        """Test that utils/__init__.py maintains all utility imports."""
        from urarovite.utils import (
            extract_sheet_id,
            split_segments,
            strip_outer_single_quotes,
            extract_sheet_and_range,
            parse_tab_token,
            parse_referenced_tabs,
            fetch_sheet_tabs,
            get_sheet_values,
        )

        # Verify all are callable
        assert callable(extract_sheet_id)
        assert callable(split_segments)
        assert callable(strip_outer_single_quotes)
        assert callable(extract_sheet_and_range)
        assert callable(parse_tab_token)
        assert callable(parse_referenced_tabs)
        assert callable(fetch_sheet_tabs)
        assert callable(get_sheet_values)

    def test_auth_module_imports(self):
        """Test that auth/__init__.py exports the new functions."""
        from urarovite.auth import (
            decode_service_account,
            create_gspread_client,
            get_gspread_client,
            create_sheets_service_from_encoded_creds,
            clear_client_cache,
        )

        # Verify all are callable
        assert callable(decode_service_account)
        assert callable(create_gspread_client)
        assert callable(get_gspread_client)
        assert callable(create_sheets_service_from_encoded_creds)
        assert callable(clear_client_cache)


class TestLegacyFunctionWrappers:
    """Test that legacy function wrappers work correctly."""

    def test_fetch_sheet_tabs_legacy_wrapper(self):
        """Test that the legacy fetch_sheet_tabs wrapper handles auth errors gracefully."""
        from urarovite.checker.utils import fetch_sheet_tabs

        # Call the wrapper - should return error since OAuth is removed
        result = fetch_sheet_tabs("test_spreadsheet_id")

        # Should return error structure
        assert result["accessible"] is False
        assert result["tabs"] == []
        assert "auth_error" in result["error"]

    def test_get_sheet_values_legacy_wrapper(self):
        """Test that the legacy get_sheet_values wrapper handles auth errors gracefully."""
        from urarovite.checker.utils import get_sheet_values

        # Call the wrapper - should return error since OAuth is removed
        result = get_sheet_values("test_spreadsheet_id", "Sheet1!A1:B2")

        # Should return error structure
        assert result["success"] is False
        assert result["values"] == []
        assert result["rows"] == 0
        assert result["cols"] == 0
        assert "auth_error" in result["error"]


class TestModuleStructureConsistency:
    """Test that the module structure is consistent."""

    def test_all_auth_functions_available_in_init(self):
        """Test that all auth functions are properly exported."""
        from urarovite.auth import __all__ as auth_all
        from urarovite.auth.google_sheets import (
            decode_service_account,
            create_gspread_client,
            get_gspread_client,
            create_sheets_service_from_encoded_creds,
            clear_client_cache,
        )

        # All functions should be in __all__
        expected_functions = [
            "decode_service_account",
            "create_gspread_client",
            "get_gspread_client",
            "create_sheets_service_from_encoded_creds",
            "clear_client_cache",
        ]

        for func_name in expected_functions:
            assert func_name in auth_all, f"{func_name} not in auth.__all__"

    def test_checker_module_exports_consistency(self):
        """Test that checker module exports are consistent."""
        from urarovite.checker import __all__ as checker_all

        # Should have the new gspread function
        assert "get_gspread_client" in checker_all
        assert "clear_service_cache" in checker_all

        # Should have all the utility functions
        utility_functions = [
            "extract_sheet_id",
            "split_segments",
            "strip_outer_single_quotes",
            "extract_sheet_and_range",
            "parse_tab_token",
            "parse_referenced_tabs",
            "fetch_sheet_tabs",
            "get_sheet_values",
        ]

        for func_name in utility_functions:
            assert func_name in checker_all, f"{func_name} not in checker.__all__"

    def test_utils_module_exports_consistency(self):
        """Test that utils module exports are consistent."""
        from urarovite.utils import __all__ as utils_all

        utility_functions = [
            "extract_sheet_id",
            "split_segments",
            "strip_outer_single_quotes",
            "extract_sheet_and_range",
            "parse_tab_token",
            "parse_referenced_tabs",
            "fetch_sheet_tabs",
            "get_sheet_values",
        ]

        for func_name in utility_functions:
            assert func_name in utils_all, f"{func_name} not in utils.__all__"


class TestImportPathsStillWork:
    """Test that common import paths from before the refactoring still work."""

    def test_old_style_checker_imports(self):
        """Test that old-style imports from checker modules still work."""
        # These should all work without ImportError
        try:
            from urarovite.checker import extract_sheet_id
            from urarovite.checker import get_gspread_client
            from urarovite.checker import fetch_sheet_tabs
            from urarovite.checker.utils import split_segments
            from urarovite.checker.auth import clear_service_cache
        except ImportError as e:
            pytest.fail(f"Backward compatibility import failed: {e}")

    def test_new_style_direct_imports(self):
        """Test that new-style direct imports work."""
        try:
            from urarovite.auth.google_sheets import decode_service_account
            from urarovite.utils.sheets import extract_sheet_id
            from urarovite.core.api import execute_validation
        except ImportError as e:
            pytest.fail(f"New-style import failed: {e}")

    def test_mixed_import_styles(self):
        """Test that mixing old and new import styles works."""
        try:
            # Old style
            from urarovite.checker import get_gspread_client

            # New style
            from urarovite.auth import create_gspread_client

            # Mixed
            from urarovite.utils import extract_sheet_id
            from urarovite.checker.utils import get_sheet_values

            # All should be available
            assert callable(get_gspread_client)
            assert callable(create_gspread_client)
            assert callable(extract_sheet_id)
            assert callable(get_sheet_values)

        except ImportError as e:
            pytest.fail(f"Mixed import styles failed: {e}")
