"""Module for training error detection models."""

import ast
import glob
import os
import pickle
import sys
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from ..utils import tokenize_code


class ModelTrainer:
    """Class for training code error detection models."""

    def __init__(self, output_path: Optional[str] = None):
        """
        Initialize the model trainer.

        Args:
            output_path: Path to save the trained model
        """
        if output_path is None:
            # Default to saving in the models directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            output_path = os.path.join(current_dir, "default_model.pkl")

        self.output_path = output_path
        self.model = None

    def prepare_data(
        self, code_samples: List[str], labels: List[int]
    ) -> Tuple[List[str], List[int]]:
        """
        Prepare code samples for training.

        Args:
            code_samples: List of Python code strings
            labels: List of labels (1 for code with errors, 0 for clean code)

        Returns:
            Processed code samples and labels
        """
        processed_samples = []
        processed_labels = []

        for code, label in zip(code_samples, labels):
            try:
                # Tokenize the code
                tokens = tokenize_code(code)
                processed_code = " ".join(tokens)

                processed_samples.append(processed_code)
                processed_labels.append(label)
            except Exception as e:
                # Skip samples that can't be processed
                print(f"Skipping sample: {e}")

        return processed_samples, processed_labels

    def extract_features(self, code_samples: List[str]) -> List[Dict]:
        """
        Extract additional features from code samples.

        Args:
            code_samples: List of Python code strings

        Returns:
            List of feature dictionaries
        """
        features = []

        for code in code_samples:
            feature_dict = {}

            try:
                # Parse the code with ast
                tree = ast.parse(code)

                # Count various AST nodes as features
                feature_dict["num_functions"] = sum(
                    1 for _ in ast.walk(tree) if isinstance(_, ast.FunctionDef)
                )
                feature_dict["num_classes"] = sum(
                    1 for _ in ast.walk(tree) if isinstance(_, ast.ClassDef)
                )
                feature_dict["num_imports"] = sum(
                    1
                    for _ in ast.walk(tree)
                    if isinstance(_, ast.Import) or isinstance(_, ast.ImportFrom)
                )
                feature_dict["num_loops"] = sum(
                    1
                    for _ in ast.walk(tree)
                    if isinstance(_, ast.For) or isinstance(_, ast.While)
                )
                feature_dict["num_branches"] = sum(
                    1
                    for _ in ast.walk(tree)
                    if isinstance(_, ast.If) or isinstance(_, ast.IfExp)
                )
                feature_dict["num_except"] = sum(
                    1 for _ in ast.walk(tree) if isinstance(_, ast.ExceptHandler)
                )

                # Code complexity: rough approximation based on McCabe complexity
                feature_dict["complexity"] = (
                    feature_dict["num_functions"]
                    + feature_dict["num_classes"]
                    + feature_dict["num_loops"] * 2
                    + feature_dict["num_branches"] * 2
                    + feature_dict["num_except"]
                )

                # Code size features
                feature_dict["code_lines"] = len(code.split("\n"))
                feature_dict["code_chars"] = len(code)

            except SyntaxError:
                # For code with syntax errors, we can't extract AST features
                # Use default values
                feature_dict = {
                    "num_functions": 0,
                    "num_classes": 0,
                    "num_imports": 0,
                    "num_loops": 0,
                    "num_branches": 0,
                    "num_except": 0,
                    "complexity": 0,
                    "code_lines": len(code.split("\n")),
                    "code_chars": len(code),
                }

            features.append(feature_dict)

        return features

    def train(self, code_samples: List[str], labels: List[int]) -> Any:
        """
        Train a model on the provided code samples and labels.

        Args:
            code_samples: List of Python code strings
            labels: List of labels (1 for code with errors, 0 for clean code)

        Returns:
            Trained model
        """
        # Prepare the data
        processed_samples, processed_labels = self.prepare_data(code_samples, labels)

        # Extract additional features (currently not used in the pipeline below)
        # additional_features = self.extract_features(code_samples) # This data is not being used in the current pipeline

        # Create a pipeline with TF-IDF and RandomForest
        pipeline = Pipeline(
            [
                ("vectorizer", TfidfVectorizer(max_features=5000, ngram_range=(1, 3))),
                (
                    "classifier",
                    RandomForestClassifier(n_estimators=100, random_state=42),
                ),
            ]
        )

        # Train the model
        print(f"Training model on {len(processed_samples)} samples...")
        X_train, X_test, y_train, y_test = train_test_split(
            processed_samples, processed_labels, test_size=0.2, random_state=42
        )

        pipeline.fit(X_train, y_train)

        # Evaluate the model
        y_pred = pipeline.predict(X_test)
        print(classification_report(y_test, y_pred))

        self.model = pipeline
        return self.model

    def save_model(self) -> str:
        """
        Save the trained model to disk.

        Returns:
            Path to the saved model
        """
        if self.model is None:
            raise ValueError("No model to save. Train a model first.")

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        # Save the model
        with open(self.output_path, "wb") as f:
            pickle.dump(self.model, f)

        print(f"Model saved to {self.output_path}")
        return self.output_path

    def load_model(self, model_path: Optional[str] = None) -> Any:
        """
        Load a trained model from disk.

        Args:
            model_path: Path to the model file. If None, use the output_path

        Returns:
            Loaded model
        """
        if model_path is None:
            model_path = self.output_path

        with open(model_path, "rb") as f:
            self.model = pickle.load(f)

        return self.model


def load_python_files_from_directory(directory: str) -> List[Dict]:
    """
    Load Python files from a directory structure.

    Args:
        directory: Path to the directory containing Python files

    Returns:
        List of dictionaries with code samples and error labels
    """
    dataset = []

    # Find all .py files recursively
    py_files = glob.glob(os.path.join(directory, "**", "*.py"), recursive=True)

    for file_path in py_files:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read()

            # Determine if the code has errors
            has_error = False
            try:
                ast.parse(code)
            except SyntaxError:
                has_error = True

            # Create a dataset item
            item = {"code": code, "has_error": has_error, "path": file_path}

            dataset.append(item)
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")

    print(f"Loaded {len(dataset)} Python files from {directory}")
    return dataset


def train_from_codenetpy(dataset_path: str, output_path: str) -> str:
    """
    Train a model using Python files from a directory.

    Args:
        dataset_path: Path to the directory containing Python files
        output_path: Path to save the trained model

    Returns:
        Path to the saved model
    """
    # Load the dataset from the directory
    dataset = load_python_files_from_directory(dataset_path)

    # Extract code samples and error labels
    code_samples = []
    labels = []

    for item in dataset:
        code = item.get("code", "")
        has_error = item.get("has_error", False)

        if code:
            code_samples.append(code)
            labels.append(1 if has_error else 0)

    # Train the model
    trainer = ModelTrainer(output_path)
    trainer.train(code_samples, labels)

    # Save the model
    return trainer.save_model()