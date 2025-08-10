"""Module for analyzing and detecting logical errors in Python code."""

import ast
from typing import Any, Dict, List, Optional, Set

from .utils import tokenize_code # Added import


class LogicAnalyzer:
    """Class for analyzing Python code for logical errors."""

    def __init__(self, model: Any):
        """
        Initialize the logic analyzer.

        Args:
            model: Trained model for detecting logical errors
        """
        self.model = model

        # Common logical error patterns
        self.common_patterns = {
            # Infinite loops
            "while_true_no_break": self._check_infinite_loop,
            # Unused variables
            "unused_variables": self._check_unused_variables,
            # Off-by-one errors
            "off_by_one": self._check_off_by_one,
            # Division by zero
            "division_by_zero": self._check_division_by_zero,
            # Unreachable code
            "unreachable_code": self._check_unreachable_code,
        }

    def analyze(self, code: str) -> List[Dict]:
        """
        Analyze Python code for logical errors.

        Args:
            code: Python code string to analyze

        Returns:
            List of dictionaries with error information
        """
        errors = []

        try:
            # Parse the code into an AST
            tree = ast.parse(code)

            # Run static checks for common patterns
            for pattern_name, check_func in self.common_patterns.items():
                pattern_errors = check_func(tree)
                errors.extend(pattern_errors)

            # Use the trained model to detect additional logical errors
            model_errors = self._analyze_with_model(code) # Now this method is functional
            errors.extend(model_errors)

        except Exception as e:
            errors.append(
                {
                    "line": 0,
                    "column": 0,
                    "type": "AnalysisError",
                    "message": f"Error analyzing code: {str(e)}",
                    "description": "An error occurred during the logical analysis",
                }
            )

        return errors

    def _analyze_with_model(self, code: str) -> List[Dict]:
        """
        Use the trained model to detect logical errors.

        Args:
            code: Python code string to analyze

        Returns:
            List of dictionaries with error information
        """
        errors = []
        if self.model:
            try:
                # Preprocess code for the model
                tokens = tokenize_code(code)
                processed_code = [" ".join(tokens)] # Model expects a list of strings

                # Predict probability of error (assuming 0 is clean, 1 is error)
                probabilities = self.model.predict_proba(processed_code)

                # Assuming the model outputs probabilities for [class_0, class_1]
                # where class_1 is the error class
                error_probability = probabilities[0][1] # Probability of being buggy

                # Define a threshold for detection
                if error_probability > 0.5: # Adjustable threshold
                    errors.append({
                        "line": 0, # ML detection might not be line-specific
                        "column": 0,
                        "type": "PotentialLogicalError",
                        "message": f"Potential logical error detected by ML model (confidence: {error_probability:.2f})",
                        "description": "The machine learning model suggests a logical issue in this code section.",
                    })
            except Exception as e:
                # Handle cases where model prediction fails
                errors.append(
                    {
                        "line": 0,
                        "column": 0,
                        "type": "ModelPredictionError",
                        "message": f"Error during ML model prediction: {str(e)}",
                        "description": "Failed to run the logical error detection model. Ensure the model is correctly trained and loaded.",
                    }
                )
        return errors

    def _check_infinite_loop(self, tree: ast.AST) -> List[Dict]:
        """Check for potential infinite loops."""
        errors = []

        class InfiniteLoopVisitor(ast.NodeVisitor):
            def __init__(self):
                self.errors = []

            def visit_While(self, node):
                # Check for while True without break
                if isinstance(node.test, ast.Constant) and node.test.value is True:
                    # Check if there's a break statement in the loop body
                    has_break = False

                    class BreakFinder(ast.NodeVisitor):
                        def __init__(self):
                            self.found_break = False

                        def visit_Break(self, node):
                            self.found_break = True

                    break_finder = BreakFinder()
                    break_finder.visit(node)

                    if not break_finder.found_break:
                        self.errors.append(
                            {
                                "line": node.lineno,
                                "column": node.col_offset,
                                "type": "InfiniteLoop",
                                "message": "Potential infinite loop: while True without break",
                                "description": "This while loop might run indefinitely as it has no break statement",
                            }
                        )

                self.generic_visit(node)

        visitor = InfiniteLoopVisitor()
        visitor.visit(tree)
        errors.extend(visitor.errors)

        return errors

    def _check_unused_variables(self, tree: ast.AST) -> List[Dict]:
        """Check for unused variables."""

        class VariableTracker(ast.NodeVisitor):
            def __init__(self):
                self.defined = {}  # Maps variable names to line numbers
                self.used = set()  # Set of used variable names
                self.errors = []

            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Store):
                    self.defined[node.id] = node.lineno
                elif isinstance(node.ctx, ast.Load):
                    self.used.add(node.id)
                self.generic_visit(node)

            def get_unused(self):
                for var, line in self.defined.items():
                    if var not in self.used and not var.startswith("_"):
                        self.errors.append(
                            {
                                "line": line,
                                "column": 0,
                                "type": "UnusedVariable",
                                "message": f"Unused variable: '{var}'",
                                "description": f"The variable '{var}' is defined but never used",
                            }
                        )
                return self.errors

        tracker = VariableTracker()
        tracker.visit(tree)
        return tracker.get_unused()

    def _check_off_by_one(self, tree: ast.AST) -> List[Dict]:
        """Check for potential off-by-one errors."""
        errors = []

        class OffByOneVisitor(ast.NodeVisitor):
            def __init__(self):
                self.errors = []

            def visit_For(self, node):
                # Check for common off-by-one patterns in range() calls
                if (
                    isinstance(node.iter, ast.Call)
                    and isinstance(node.iter.func, ast.Name)
                    and node.iter.func.id == "range"
                ):

                    # Check for range(len(x)) which might be an off-by-one if accessing indices
                    if (
                        len(node.iter.args) == 1
                        and isinstance(node.iter.args[0], ast.Call)
                        and isinstance(node.iter.args[0].func, ast.Name)
                        and node.iter.args[0].func.id == "len"
                    ):

                        self.errors.append(
                            {
                                "line": node.lineno,
                                "column": node.col_offset,
                                "type": "PotentialOffByOne",
                                "message": "Potential off-by-one error in range(len(...))",
                                "description": "Using range(len(x)) might lead to off-by-one errors if accessing indices",
                            }
                        )

                self.generic_visit(node)

        visitor = OffByOneVisitor()
        visitor.visit(tree)
        errors.extend(visitor.errors)

        return errors

    def _check_division_by_zero(self, tree: ast.AST) -> List[Dict]:
        """Check for potential division by zero errors."""
        errors = []

        class DivisionByZeroVisitor(ast.NodeVisitor):
            def __init__(self):
                self.errors = []

            def visit_BinOp(self, node):
                # Check for division operations
                if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
                    # Check if the divisor is a constant 0
                    if isinstance(node.right, ast.Constant) and node.right.value == 0:
                        self.errors.append(
                            {
                                "line": node.lineno,
                                "column": node.col_offset,
                                "type": "DivisionByZero",
                                "message": "Division by zero",
                                "description": "This operation will cause a division by zero error",
                            }
                        )

                    # Check for potential division by zero with variables
                    if isinstance(node.right, ast.Name):
                        self.errors.append(
                            {
                                "line": node.lineno,
                                "column": node.col_offset,
                                "type": "PotentialDivisionByZero",
                                "message": f"Potential division by zero with variable '{node.right.id}'",
                                "description": f"Consider adding a check to ensure '{node.right.id}' is not zero before division",
                            }
                        )

                self.generic_visit(node)

        visitor = DivisionByZeroVisitor()
        visitor.visit(tree)
        errors.extend(visitor.errors)

        return errors

    def _check_unreachable_code(self, tree: ast.AST) -> List[Dict]:
        """Check for unreachable code."""
        errors = []

        class UnreachableCodeVisitor(ast.NodeVisitor):
            def __init__(self):
                self.errors = []
                self.current_function = None

            def visit_FunctionDef(self, node):
                old_function = self.current_function
                self.current_function = node

                # Check for code after return/break/continue
                has_unreachable = False
                for i, stmt in enumerate(node.body):
                    if isinstance(stmt, ast.Return) and i < len(node.body) - 1:
                        has_unreachable = True
                        unreachable_line = node.body[i + 1].lineno
                        break

                if has_unreachable:
                    self.errors.append(
                        {
                            "line": unreachable_line,
                            "column": 0,
                            "type": "UnreachableCode",
                            "message": "Unreachable code after return statement",
                            "description": "This code will never be executed as it follows a return statement",
                        }
                    )

                self.generic_visit(node)
                self.current_function = old_function

        visitor = UnreachableCodeVisitor()
        visitor.visit(tree)
        errors.extend(visitor.errors)

        return errors

    def suggest_fix(self, code: str, error: Dict) -> Optional[str]:
        """
        Suggest a fix for a logical error.

        Args:
            code: Original Python code string
            error: Error dictionary from analyze()

        Returns:
            Suggested fix or None if no suggestion available
        """
        # Handle specific error types
        if error["type"] == "InfiniteLoop":
            return "Add a break condition to prevent infinite execution, e.g.:\n```python\nwhile True:\n    # Your code\n    if some_condition:\n        break\n```"

        elif error["type"] == "UnusedVariable":
            var_name = error["message"].split("'")[1]
            return f"Either use the variable '{var_name}' or remove it. If it's intentionally unused, prefix it with an underscore: '_{var_name}'"

        elif error["type"] == "PotentialOffByOne":
            return "Use explicit indices or consider using enumeration:\n```python\nfor i, item in enumerate(my_list):\n    # Use i as index, item as value\n```"

        elif (
            error["type"] == "DivisionByZero"
            or error["type"] == "PotentialDivisionByZero"
        ):
            if "variable" in error["message"]:
                var_name = error["message"].split("'")[1]
                return f"Add a check before the division:\n```python\nif {var_name} != 0:\n    result = value / {var_name}\nelse:\n    # Handle the zero case\n```"
            else:
                return "Fix the division operation to avoid dividing by zero"

        elif error["type"] == "UnreachableCode":
            return "Remove or relocate the unreachable code, or fix the control flow to make it reachable"
        
        elif error["type"] == "PotentialLogicalError": # Suggestion for ML-detected errors
            return "Review the logic in this section of code. Consider refactoring or adding more tests to identify the underlying issue."


        # Generic suggestion
        return None