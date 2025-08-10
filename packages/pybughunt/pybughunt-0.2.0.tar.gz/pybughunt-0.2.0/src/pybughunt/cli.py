"""Command-line interface for the code error detector."""

import argparse
import json
import os
import sys
from typing import Dict, List, Optional

from .detector import CodeErrorDetector
from .models.model_trainer import ModelTrainer


def analyze_file(file_path: str, model_type: str, model_path: Optional[str] = None, output_format: str = "text") -> Dict:
    """Analyze a Python file for errors."""
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    detector = CodeErrorDetector(model_type, model_path)
    results = detector.analyze(code)

    if output_format == "json":
        return results
    else:
        formatted = format_results(results, file_path)
        return {"formatted": formatted, "results": results}


def format_results(results: Dict[str, List[Dict]], file_path: str) -> str:
    """Format analysis results for text output."""
    output = [f"Analysis results for {os.path.basename(file_path)}:"]
    if results["syntax_errors"]:
        output.append("\nSyntax Errors:")
        for error in results["syntax_errors"]:
            output.append(f"  Line {error['line']}: {error['message']}")
    if results["logic_errors"]:
        output.append("\nLogic Errors:")
        for error in results["logic_errors"]:
            output.append(f"  Line {error['line']}: {error['message']}")
    if not results["syntax_errors"] and not results["logic_errors"]:
        output.append("\nNo errors detected.")
    return "\n".join(output)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Detect errors in Python code")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    analyze_parser = subparsers.add_parser("analyze", help="Analyze Python files for errors")
    analyze_parser.add_argument("files", nargs="+", help="Python files to analyze")
    analyze_parser.add_argument("--model_type", default="static", choices=["static", "codebert", "t5"], help="Model to use for analysis")
    analyze_parser.add_argument("--model_path", help="Path to the trained model")
    analyze_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    analyze_parser.add_argument("--output", "-o", help="Output file")

    train_parser = subparsers.add_parser("train", help="Train a new error detection model")
    train_parser.add_argument("--dataset", required=True, help="Path to the dataset directory")
    train_parser.add_argument("--output", required=True, help="Path to save the trained model")
    train_parser.add_argument("--model_type", default="codebert", choices=["codebert", "t5"], help="Model to train")

    args = parser.parse_args()

    if args.command == "analyze":
        all_results = {}
        for file_path in args.files:
            if not os.path.exists(file_path):
                print(f"Error: File '{file_path}' does not exist", file=sys.stderr)
                continue
            result = analyze_file(file_path, args.model_type, args.model_path, args.format)
            if args.format == "json":
                all_results[file_path] = result
            else:
                print(result["formatted"])

    elif args.command == "train":
        # Simplified training from a directory of files.
        # You'll need to create a dataset in the format of [{"code": "...", "label": 0/1}, ...]
        print("Training functionality needs a properly formatted dataset.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()