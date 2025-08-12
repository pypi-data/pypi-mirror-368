"""Simple test runner for TabNameValidator using built-in unittest.

This script runs TabNameValidator tests without requiring external dependencies.
"""

import sys
import unittest
from unittest.mock import Mock
import os

# Add the project root to the path so we can import urarovite modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from urarovite.validators.data_quality import TabNameValidator, ILLEGAL_CHARS
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

class TestTabNameValidator(unittest.TestCase):
    """Test suite for TabNameValidator using unittest."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.validator = TabNameValidator()
    
    def test_validator_initialization(self):
        """Test that the validator is properly initialized."""
        self.assertEqual(self.validator.id, "tab_names")
        self.assertEqual(self.validator.name, "Fix Tab Names")
        self.assertIn("allowed characters", self.validator.description)
    
    def test_illegal_chars_constant(self):
        """Test that the illegal characters constant is properly defined."""
        expected_chars = ["\\", "/", "?", "*", "[", "]"]
        self.assertEqual(ILLEGAL_CHARS, expected_chars)
    
    def test_clean_tab_name_basic_replacement(self):
        """Test basic character replacement functionality."""
        test_cases = [
            ("Sheet\\with\\backslashes", "Sheet_with_backslashes"),
            ("Sheet/with/slashes", "Sheet_with_slashes"),
            ("Sheet?with?questions", "Sheet_with_questions"),
            ("Sheet*with*asterisks", "Sheet_with_asterisks"),
            ("Sheet[with[brackets]", "Sheet_with_brackets"),
            ("Sheet]with]brackets", "Sheet_with_brackets"),
        ]
        
        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = self.validator._clean_tab_name(input_name, "_")
                self.assertEqual(result, expected)
    
    def test_clean_tab_name_complex_cases(self):
        """Test complex character replacement scenarios."""
        test_cases = [
            ("Mix\\ed/Ch?ar*s[Test]", "Mix_ed_Ch_ar_s_Test"),
            ("___trimming___", "trimming"),
            ("Multiple___underscores", "Multiple_underscores"),
            ("", "Sheet"),  # empty case
            ("Normal_Sheet_Name", "Normal_Sheet_Name"),  # no illegal chars
            ("///", "Sheet"),  # all illegal chars
            ("_[]*_", "Sheet"),  # becomes empty after cleaning
        ]
        
        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = self.validator._clean_tab_name(input_name, "_")
                self.assertEqual(result, expected)
    
    def test_clean_tab_name_custom_replacement(self):
        """Test character replacement with custom replacement character."""
        input_name = "Sheet\\with/illegal*chars"
        result = self.validator._clean_tab_name(input_name, "-")
        self.assertEqual(result, "Sheet-with-illegal-chars")
        
        # Test with multiple consecutive custom chars
        input_name = "Test///Multiple"
        result = self.validator._clean_tab_name(input_name, "-")
        self.assertEqual(result, "Test-Multiple")
    
    def test_resolve_name_collision_no_conflict(self):
        """Test collision resolution when no conflict exists."""
        used_names = {"Sheet", "Data", "Summary"}
        result = self.validator._resolve_name_collision("NewSheet", used_names)
        self.assertEqual(result, "NewSheet")
    
    def test_resolve_name_collision_with_conflict(self):
        """Test collision resolution when conflicts exist."""
        used_names = {"Sheet", "Sheet_1", "Data", "Summary"}
        
        # Test first collision
        result = self.validator._resolve_name_collision("Data", used_names)
        self.assertEqual(result, "Data_1")
        
        # Test multiple collisions
        result = self.validator._resolve_name_collision("Sheet", used_names)
        self.assertEqual(result, "Sheet_2")
    
    def test_resolve_name_collision_progressive_numbering(self):
        """Test progressive numbering for multiple collisions."""
        used_names = {"Sheet", "Sheet_1", "Data", "Summary"}
        
        collision_tests = ["Sheet", "Data", "NewSheet", "Sheet", "Sheet"]
        expected_results = ["Sheet_2", "Data_1", "NewSheet", "Sheet_3", "Sheet_4"]
        
        for name, expected in zip(collision_tests, expected_results):
            with self.subTest(name=name):
                result = self.validator._resolve_name_collision(name, used_names)
                used_names.add(result)  # Add to used names for next iteration
                self.assertEqual(result, expected)
    
    def test_validate_no_sheets_error(self):
        """Test validation when spreadsheet has no sheets."""
        # Mock sheets service
        mock_service = Mock()
        mock_service.spreadsheets.return_value.get.return_value.execute.return_value = {
            "sheets": []
        }
        
        result = self.validator.validate(mock_service, "test_sheet_id", "flag")
        
        self.assertEqual(result["fixes_applied"], 0)
        self.assertEqual(result["issues_found"], 0)
        self.assertEqual(len(result["errors"]), 1)
        self.assertIn("No sheets found", result["errors"][0])
    
    def test_validate_no_illegal_characters(self):
        """Test validation when no illegal characters are found."""
        # Mock sheets service with clean tab names
        mock_service = Mock()
        mock_service.spreadsheets.return_value.get.return_value.execute.return_value = {
            "sheets": [
                {"properties": {"title": "Clean_Sheet_1", "sheetId": 0}},
                {"properties": {"title": "Clean_Sheet_2", "sheetId": 1}},
            ]
        }
        
        result = self.validator.validate(mock_service, "test_sheet_id", "flag")
        
        self.assertEqual(result["fixes_applied"], 0)
        self.assertEqual(result["issues_found"], 0)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["details"], {})
    
    def test_edge_cases(self):
        """Test various edge cases."""
        # Test empty sheet name
        result = self.validator._clean_tab_name("", "_")
        self.assertEqual(result, "Sheet")
        
        # Test name with only illegal characters
        result = self.validator._clean_tab_name("\\/*[]", "_")
        self.assertEqual(result, "Sheet")
        
        # Test name with only replacement characters
        result = self.validator._clean_tab_name("___", "_")
        self.assertEqual(result, "Sheet")
        
        # Test very long name with illegal characters
        long_name = "Very" + "\\" * 50 + "Long" + "/" * 50 + "Name"
        result = self.validator._clean_tab_name(long_name, "_")
        self.assertEqual(result, "Very_Long_Name")
        self.assertFalse(any(char in result for char in ILLEGAL_CHARS))

def run_tests():
    """Run all the tests and provide a summary."""
    print("Running TabNameValidator Tests")
    print("=" * 50)
    
    # Create a test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestTabNameValidator)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print(f"✅ All {result.testsRun} tests passed!")
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors out of {result.testsRun} tests")
        
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 