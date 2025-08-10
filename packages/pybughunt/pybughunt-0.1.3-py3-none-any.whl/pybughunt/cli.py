"""Command-line interface for the code error detector."""

import argparse
import json
import os
import sys
from typing import Dict, List, Optional

from .detector import CodeErrorDetector
from .models.model_trainer import ModelTrainer, train_from_codenetpy


def analyze_file(
    file_path: str, model_path: Optional[str] = None, output_format: str = "text"
) -> Dict:
    """
    Analyze a Python file for errors.

    Args:
        file_path: Path to the Python file
        model_path: Path to the trained model
        output_format: Output format (text or json)

    Returns:
        Analysis results
    """
    # Read the file
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Analyze the code
    detector = CodeErrorDetector(model_path)
    results = detector.analyze(code)

    if output_format == "json":
        return results
    else:
        # Format results for text output
        formatted = format_results(results, file_path)
        return {"formatted": formatted, "results": results}


def format_results(results: Dict[str, List[Dict]], file_path: str) -> str:
    """
    Format analysis results for text output.

    Args:
        results: Analysis results
        file_path: Path to the analyzed file

    Returns:
        Formatted results string
    """
    output = [f"Analysis results for {os.path.basename(file_path)}:"]

    # Display syntax errors
    if results["syntax_errors"]:
        output.append("\nSyntax Errors:")
        for error in results["syntax_errors"]:
            output.append(f"  Line {error['line']}: {error['message']}")
            if error.get("description"):
                output.append(f"    {error['description']}")

    # Display logic errors
    if results["logic_errors"]:
        output.append("\nLogic Errors:")
        for error in results["logic_errors"]:
            output.append(f"  Line {error['line']}: {error['message']}")
            if error.get("description"):
                output.append(f"    {error['description']}")

    # If no errors found
    if not results["syntax_errors"] and not results["logic_errors"]:
        output.append("\nNo errors detected.")

    return "\n".join(output)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Detect errors in Python code")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Parser for analyzing files
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze Python files for errors"
    )
    analyze_parser.add_argument("files", nargs="+", help="Python files to analyze")
    analyze_parser.add_argument("--model", help="Path to the trained model")
    analyze_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    analyze_parser.add_argument("--output", "-o", help="Output file (default: stdout)")

    # Parser for training a model
    train_parser = subparsers.add_parser(
        "train", help="Train a new error detection model"
    )
    train_parser.add_argument(
        "--dataset", required=True, help="Path to the CodeNetPy dataset"
    )
    train_parser.add_argument(
        "--output", required=True, help="Path to save the trained model"
    )

    args = parser.parse_args()

    if args.command == "analyze":
        all_results = {}
        for file_path in args.files:
            if not os.path.exists(file_path):
                print(f"Error: File '{file_path}' does not exist", file=sys.stderr)
                continue

            if not file_path.endswith(".py"):
                print(
                    f"Warning: '{file_path}' does not have a .py extension",
                    file=sys.stderr,
                )

            result = analyze_file(file_path, args.model, args.format)

            if args.format == "json":
                all_results[file_path] = result
            else:
                if args.output:
                    with open(args.output, "a", encoding="utf-8") as f:
                        f.write(result["formatted"])
                        f.write("\n\n")
                else:
                    print(result["formatted"])
                    print()

        if args.format == "json" and args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(all_results, f, indent=2)

    elif args.command == "train":
        try:
            output_path = train_from_codenetpy(args.dataset, args.output)
            print(f"Model trained and saved to: {output_path}")
        except Exception as e:
            print(f"Error training model: {str(e)}", file=sys.stderr)
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
