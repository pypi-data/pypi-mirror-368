"""Module for analyzing and detecting syntax errors in Python code."""

import ast
import re
import tokenize
from io import BytesIO, StringIO
from typing import Dict, List, Optional


class SyntaxAnalyzer:
    """Class for analyzing Python code for syntax errors."""

    def __init__(self):
        """Initialize the syntax analyzer."""
        # Common syntax error patterns and their descriptions
        self.error_patterns = {
            r"invalid syntax": "Invalid syntax",
            r"unexpected EOF": "Unexpected end of file - check for missing parentheses or brackets",
            r"expected an indented block": "Expected an indented block after this line",
            r"unindent does not match any outer indentation level": "Inconsistent indentation",
            r"Missing parentheses in call to \'print\'": "Missing parentheses in print statement - use print() instead",
            r"unexpected indent": "Unexpected indentation - check your spacing",
            r"invalid token": "Invalid token - check for special characters",
            r"EOF while scanning": "Unclosed string literal",
            r"unterminated string literal": "Unterminated string literal - check for missing quotes",
        }

    def analyze(self, code: str) -> List[Dict]:
        """
        Analyze Python code for syntax errors.

        Args:
            code: Python code string to analyze

        Returns:
            List of dictionaries with error information
        """
        errors = []

        # Try to parse the code with ast
        try:
            ast.parse(code)
        except SyntaxError as e:
            # Extract line number and error message
            line_num = e.lineno if hasattr(e, "lineno") else 0
            col_num = e.offset if hasattr(e, "offset") else 0
            error_msg = str(e)

            # Try to match with known error patterns for better descriptions
            description = error_msg
            for pattern, better_desc in self.error_patterns.items():
                if re.search(pattern, error_msg, re.IGNORECASE):
                    description = better_desc
                    break

            errors.append(
                {
                    "line": line_num,
                    "column": col_num,
                    "type": "SyntaxError",
                    "message": error_msg,
                    "description": description,
                }
            )

        # Check for indentation and whitespace issues
        if not errors:
            try:
                tokens = list(tokenize.tokenize(BytesIO(code.encode("utf-8")).readline))
                # Additional token-based checks could be implemented here
            except tokenize.TokenError as e:
                errors.append(
                    {
                        "line": (
                            e.args[1][0]
                            if len(e.args) > 1 and len(e.args[1]) > 0
                            else 0
                        ),
                        "column": 0,
                        "type": "TokenError",
                        "message": str(e),
                        "description": "Tokenization error - check for unclosed parentheses, brackets, or strings",
                    }
                )

        return errors

    def suggest_fix(self, code: str, error: Dict) -> Optional[str]:
        """
        Suggest a fix for a syntax error.

        Args:
            code: Original Python code string
            error: Error dictionary from analyze()

        Returns:
            Suggested fix or None if no suggestion available
        """
        if error["type"] != "SyntaxError" and error["type"] != "TokenError":
            return None

        message = error["message"].lower()

        # Common fixes for specific syntax errors
        if "missing parentheses in call to 'print'" in message:
            # Find the line with the print statement
            lines = code.split("\n")
            if 0 <= error["line"] - 1 < len(lines):
                line = lines[error["line"] - 1]
                # Simple replacement of print statements without parentheses
                fixed_line = re.sub(r"print\s+([^(].*)", r"print(\1)", line)
                return fixed_line

        elif "unexpected EOF" in message or "unexpected end of file" in message:
            # Check for unclosed parentheses, brackets or braces
            stack = []
            for char in code:
                if char in "([{":
                    stack.append(char)
                elif char in ")]}":
                    if stack and (
                        (stack[-1] == "(" and char == ")")
                        or (stack[-1] == "[" and char == "]")
                        or (stack[-1] == "{" and char == "}")
                    ):
                        stack.pop()
                    else:
                        # Mismatched closing bracket
                        return None

            # Suggest adding the missing closing brackets
            if stack:
                closing = "".join(
                    ")" if c == "(" else "]" if c == "[" else "}"
                    for c in reversed(stack)
                )
                return f"Add missing closing characters: {closing}"

        # Generic suggestion
        return None
