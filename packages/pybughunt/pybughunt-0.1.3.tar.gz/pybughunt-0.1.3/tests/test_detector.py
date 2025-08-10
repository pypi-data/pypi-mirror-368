"""Tests for the CodeErrorDetector class."""

import os
import unittest

from pybughunt import CodeErrorDetector


class TestCodeErrorDetector(unittest.TestCase):
    """Test cases for the CodeErrorDetector class."""

    def setUp(self):
        """Set up test cases."""
        self.detector = CodeErrorDetector()

    def test_syntax_error_detection(self):
        """Test detection of syntax errors."""
        # Code with a syntax error (missing closing parenthesis)
        code_with_syntax_error = """
def hello():
    print("Hello, world!"
"""
        result = self.detector.analyze(code_with_syntax_error)
        self.assertTrue(result["syntax_errors"])
        self.assertEqual(len(result["syntax_errors"]), 1)
        self.assertIn("line", result["syntax_errors"][0])
        self.assertIn("message", result["syntax_errors"][0])

    def test_clean_code(self):
        """Test analysis of clean code with no errors."""
        clean_code = """
def hello():
    print("Hello, world!")
    return True
"""
        result = self.detector.analyze(clean_code)
        self.assertFalse(result["syntax_errors"])
        # Note: Logic error detection depends on the model, which may not be available in tests

    def test_infinite_loop_detection(self):
        """Test detection of potential infinite loops."""
        code_with_infinite_loop = """
def process_data():
    while True:
        # This loop has no break statement
        print("Processing...")
"""
        result = self.detector.analyze(code_with_infinite_loop)
        self.assertFalse(result["syntax_errors"])

        # Check if logic errors contain infinite loop warning
        has_infinite_loop_warning = False
        for error in result["logic_errors"]:
            if "InfiniteLoop" in error.get("type", ""):
                has_infinite_loop_warning = True
                break

        self.assertTrue(has_infinite_loop_warning)

    def test_unused_variable_detection(self):
        """Test detection of unused variables."""
        code_with_unused_var = """
def calculate():
    x = 10  # This variable is unused
    return 42
"""
        result = self.detector.analyze(code_with_unused_var)
        self.assertFalse(result["syntax_errors"])

        # Check if logic errors contain unused variable warning
        has_unused_var_warning = False
        for error in result["logic_errors"]:
            if "UnusedVariable" in error.get("type", ""):
                has_unused_var_warning = True
                break

        self.assertTrue(has_unused_var_warning)


if __name__ == "__main__":
    unittest.main()
