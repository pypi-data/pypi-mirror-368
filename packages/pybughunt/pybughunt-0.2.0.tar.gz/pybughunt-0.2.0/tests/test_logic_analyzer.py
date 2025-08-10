"""Tests for the LogicAnalyzer class."""

import ast
import unittest

from pybughunt.logic_analyzer import LogicAnalyzer
from pybughunt.models.model_loader import DummyModel


class TestLogicAnalyzer(unittest.TestCase):
    """Test cases for the LogicAnalyzer class."""

    def setUp(self):
        """Set up test cases."""
        self.analyzer = LogicAnalyzer(DummyModel())

    def test_infinite_loop_detection(self):
        """Test detection of infinite loops."""
        code = """
def process_data():
    while True:
        # This loop has no break statement
        print("Processing...")
"""
        tree = ast.parse(code)
        errors = self.analyzer._check_infinite_loop(tree)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["type"], "InfiniteLoop")

    def test_unused_variable_detection(self):
        """Test detection of unused variables."""
        code = """
def calculate():
    x = 10  # This variable is unused
    return 42
"""
        tree = ast.parse(code)
        errors = self.analyzer._check_unused_variables(tree)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["type"], "UnusedVariable")

    def test_off_by_one_detection(self):
        """Test detection of potential off-by-one errors."""
        code = """
def process_list(items):
    for i in range(len(items)):
        print(items[i])
"""
        tree = ast.parse(code)
        errors = self.analyzer._check_off_by_one(tree)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["type"], "PotentialOffByOne")

    def test_division_by_zero_detection(self):
        """Test detection of division by zero."""
        code = """
def calculate(x):
    return 10 / 0
"""
        tree = ast.parse(code)
        errors = self.analyzer._check_division_by_zero(tree)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["type"], "DivisionByZero")

    def test_unreachable_code_detection(self):
        """Test detection of unreachable code."""
        code = """
def calculate():
    return 42
    print("This will never be executed")
"""
        tree = ast.parse(code)
        errors = self.analyzer._check_unreachable_code(tree)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["type"], "UnreachableCode")

    def test_fix_suggestion(self):
        """Test fix suggestions for logical errors."""
        # Test infinite loop suggestion
        error = {
            "type": "InfiniteLoop",
            "line": 2,
            "message": "Potential infinite loop: while True without break",
        }
        suggestion = self.analyzer.suggest_fix("", error)
        self.assertIsNotNone(suggestion)
        self.assertIn("break", suggestion)

        # Test unused variable suggestion
        error = {"type": "UnusedVariable", "line": 2, "message": "Unused variable: 'x'"}
        suggestion = self.analyzer.suggest_fix("", error)
        self.assertIsNotNone(suggestion)
        self.assertIn("_x", suggestion)


if __name__ == "__main__":
    unittest.main()
