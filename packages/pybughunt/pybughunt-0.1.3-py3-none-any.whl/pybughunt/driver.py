"""Driver script for quick code error detection."""

import argparse
import sys

from .detector import CodeErrorDetector


def main():
    """Run code error detection from command line arguments."""
    parser = argparse.ArgumentParser(description="Detect errors in Python code quickly")
    parser.add_argument("--file", "-f", help="Python file to analyze")
    parser.add_argument("--code", "-c", help="Python code string to analyze")

    args = parser.parse_args()

    if not args.file and not args.code:
        print("Please provide either a file or a code string to analyze")
        parser.print_help()
        return 1

    detector = CodeErrorDetector()

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                code = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return 1
    else:
        code = args.code

    results = detector.analyze(code)

    # Format and print results
    if results["syntax_errors"]:
        print("\nSyntax Errors:")
        for error in results["syntax_errors"]:
            print(f"  Line {error['line']}: {error['message']}")
            if error.get("description"):
                print(f"    {error['description']}")

    if results["logic_errors"]:
        print("\nLogic Errors:")
        for error in results["logic_errors"]:
            print(f"  Line {error['line']}: {error['message']}")
            if error.get("description"):
                print(f"    {error['description']}")

    if not results["syntax_errors"] and not results["logic_errors"]:
        print("\nNo errors detected.")

    # Generate fix suggestions
    suggestions = detector.fix_suggestions(code, results)
    if suggestions:
        print("\nSuggested fixes:")
        for error_key, suggestion in suggestions.items():
            print(f"  {error_key}: {suggestion}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
