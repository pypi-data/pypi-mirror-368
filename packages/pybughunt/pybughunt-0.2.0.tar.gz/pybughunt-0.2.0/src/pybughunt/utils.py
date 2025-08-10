"""Utility functions for the code error detector."""

import ast
import os
import re
from typing import List, Optional, Tuple


def extract_function_from_code(code: str, function_name: str) -> Optional[str]:
    """
    Extract a specific function from a code string.

    Args:
        code: Python code string
        function_name: Name of the function to extract

    Returns:
        Function code as string or None if not found
    """
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                start_line = node.lineno
                end_line = 0

                # Find the end line of the function
                for child in ast.iter_child_nodes(node):
                    if hasattr(child, "lineno"):
                        end_line = max(end_line, child.lineno)

                # If we couldn't find the end, estimate it
                if end_line == 0:
                    end_line = start_line + len(node.body)

                # Extract the function from the code
                lines = code.split("\n")
                function_code = "\n".join(lines[start_line - 1 : end_line])

                return function_code
    except:
        pass

    return None


def get_line_from_code(code: str, line_number: int) -> str:
    """
    Get a specific line from code.

    Args:
        code: Python code string
        line_number: Line number to get (1-indexed)

    Returns:
        The line of code or empty string if line doesn't exist
    """
    lines = code.split("\n")
    if 1 <= line_number <= len(lines):
        return lines[line_number - 1]
    return ""


def tokenize_code(code: str) -> List[str]:
    """
    Simple tokenization of Python code for model input.

    Args:
        code: Python code string

    Returns:
        List of tokens
    """
    # Replace common patterns with spaces
    code = re.sub(r"([^\w\s])", r" \1 ", code)

    # Split by whitespace
    tokens = code.split()

    return tokens


def create_directory_if_not_exists(directory: str) -> None:
    """
    Create a directory if it doesn't exist.

    Args:
        directory: Directory path
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
