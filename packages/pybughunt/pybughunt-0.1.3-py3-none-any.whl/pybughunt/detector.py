"""Main module for detecting errors in Python code."""

import ast
import os
from typing import Dict, List, Optional, Tuple, Union

from .logic_analyzer import LogicAnalyzer
from .models.model_loader import load_model
from .syntax_analyzer import SyntaxAnalyzer


class CodeErrorDetector:
    """Main class for detecting errors in Python code."""

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the error detector.

        Args:
            model_path: Path to the trained model. If None, use the default model.
        """
        self.syntax_analyzer = SyntaxAnalyzer()

        # Load the trained model
        if model_path is None:
            # Use the default model path relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(current_dir, "models", "default_model.pkl")

        self.model = load_model(model_path)
        self.logic_analyzer = LogicAnalyzer(self.model)

    def analyze(self, code: str) -> Dict[str, List[Dict]]:
        """
        Analyze Python code for errors.

        Args:
            code: Python code string to analyze

        Returns:
            Dictionary with syntax and logic errors
        """
        result = {"syntax_errors": [], "logic_errors": []}

        # First check for syntax errors
        syntax_errors = self.syntax_analyzer.analyze(code)
        if syntax_errors:
            result["syntax_errors"] = syntax_errors
            # If there are syntax errors, we can't reliably check for logic errors
            return result

        # If no syntax errors, check for logic errors
        try:
            logic_errors = self.logic_analyzer.analyze(code)
            result["logic_errors"] = logic_errors
        except Exception as e:
            result["logic_errors"] = [
                {"line": 0, "message": f"Error analyzing logic: {str(e)}"}
            ]

        return result

    def fix_suggestions(
        self, code: str, errors: Dict[str, List[Dict]]
    ) -> Dict[str, str]:
        """
        Generate fix suggestions for detected errors.

        Args:
            code: Original Python code string
            errors: Dictionary of errors as returned by analyze()

        Returns:
            Dictionary mapping error locations to suggested fixes
        """
        suggestions = {}

        # Generate suggestions for syntax errors
        for error in errors["syntax_errors"]:
            suggestion = self.syntax_analyzer.suggest_fix(code, error)
            if suggestion:
                suggestions[f"syntax_{error['line']}"] = suggestion

        # Generate suggestions for logic errors
        for error in errors["logic_errors"]:
            suggestion = self.logic_analyzer.suggest_fix(code, error)
            if suggestion:
                suggestions[f"logic_{error['line']}"] = suggestion

        return suggestions
