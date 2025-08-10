"""Tests for the SyntaxAnalyzer class."""

import unittest

from pybughunt.syntax_analyzer import SyntaxAnalyzer


class TestSyntaxAnalyzer(unittest.TestCase):
    """Test cases for the SyntaxAnalyzer class."""

    def setUp(self):
        """Set up test cases."""
        self.analyzer = SyntaxAnalyzer()

    def test_missing_parenthesis(self):
        """Test detection of missing parenthesis."""
        code = """
def hello():
    print("Hello, world!"
"""
        errors = self.analyzer.analyze(code)
        self.assertEqual(len(errors), 1)
        self.assertIn("was never closed", errors[0]["description"].lower())

    def test_indentation_error(self):
        """Test detection of indentation errors."""
        code = """
def hello():
print("Hello, world!")
"""
        errors = self.analyzer.analyze(code)
        self.assertEqual(len(errors), 1)
        self.assertIn("indent", errors[0]["description"].lower())

    def test_valid_code(self):
        """Test analysis of valid code."""
        code = """
def hello():
    print("Hello, world!")
    return True
"""
        errors = self.analyzer.analyze(code)
        self.assertEqual(len(errors), 0)

    def test_unterminated_string(self):
        """Test detection of unterminated strings."""
        code = """
def hello():
    message = "Hello, world!
    print(message)
"""
        errors = self.analyzer.analyze(code)
        self.assertEqual(len(errors), 1)
        self.assertIn("string", errors[0]["description"].lower())

    def test_fix_suggestion_print(self):
        """Test fix suggestion for print statements."""
        code = """
def hello():
    print "Hello, world!"
"""
        errors = self.analyzer.analyze(code)
        suggestion = self.analyzer.suggest_fix(code, errors[0])
        self.assertIsNotNone(suggestion)
        self.assertIn("print(", suggestion)


if __name__ == "__main__":
    unittest.main()
