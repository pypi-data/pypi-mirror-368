# PyBugHunt

## Advanced Python Code Error Detection and Analysis

PyBugHunt is a sophisticated Python library designed to detect, analyze, and suggest fixes for both syntactical and logical errors in Python code. Leveraging a combination of static code analysis techniques and machine learning approaches, PyBugHunt offers developers a powerful tool to improve code quality and reduce debugging time.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-0.1.1-orange)

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
  - [Command Line Interface](#command-line-interface)
  - [Python API](#python-api)
- [Error Detection Capabilities](#error-detection-capabilities)
  - [Syntax Error Detection](#syntax-error-detection)
  - [Logical Error Detection](#logical-error-detection)
- [Machine Learning Approach](#machine-learning-approach)
- [Development](#development)
  - [Project Structure](#project-structure)
  - [Testing](#testing)
- [Customization](#customization)
  - [Training Custom Models](#training-custom-models)
  - [Extending Error Patterns](#extending-error-patterns)
- [License](#license)
- [Contributing](#contributing)

## Features

PyBugHunt offers comprehensive error detection capabilities:

- **Robust Syntax Error Detection and Analysis**

  - Identifies and reports syntax errors with precise line and column information
  - Provides detailed descriptions of common syntax errors
  - Suggests potential fixes for various syntax issues

- **Intelligent Logical Error Detection**

  - Identifies common logical error patterns using AST-based analysis
  - Employs machine learning models to detect subtle logical errors
  - Recognizes error patterns that might lead to runtime failures

- **Fix Suggestion System**

  - Provides context-aware suggestions to fix identified errors
  - Offers example code snippets for improved code patterns

- **Flexible Integration Options**

  - Command-line interface for analyzing Python files
  - Python API for seamless integration into other tools and workflows
  - Multiple output formats including text and JSON

- **Customization and Training**
  - Support for training custom error detection models with your codebase
  - Extensible architecture for adding new error patterns and detection strategies

## Technology Stack

PyBugHunt utilizes a wide range of technologies and libraries:

### Core Technologies

- **Python 3.8+**: Modern Python language features for robust implementation
- **Abstract Syntax Tree (AST)**: For parsing and analyzing Python code structure
- **Python Standard Library**:
  - `ast`: For parsing and traversing Python code
  - `tokenize`: For lexical analysis of Python code
  - `re`: For pattern matching in error analysis
  - `pickle`: For model serialization

### Machine Learning

- **NumPy**: For numerical operations and data processing
- **scikit-learn**: For machine learning model implementation
  - Random Forest classifiers for error pattern recognition
  - TF-IDF vectorization for code feature extraction
  - Pipeline API for streamlined model training and inference
- **PyTorch**: For advanced deep learning models (transformer-based error detection)
- **Transformers**: For pre-trained language models adapted to code understanding

### Static Analysis

- **Astroid**: For enhanced AST capabilities and more detailed code analysis
- **PyLint**: For additional pattern recognition and best practice enforcement

### Development and Testing

- **setuptools**: For package building and distribution
- **unittest**: For comprehensive test coverage
- **black & isort**: For consistent code formatting and organization

## Installation

### From PyPI (Recommended)

```bash
pip install pybughunt
```

### From Source

```bash
# Clone the repository
git clone https://github.com/Preksha-7/pybughunt.git
cd pybughunt

# Install in development mode
pip install -e .
```

### Dependencies

All dependencies will be automatically installed when you install PyBugHunt. The main dependencies include:

```
numpy>=1.20.0
scikit-learn>=1.0.0
torch>=1.9.0
transformers>=4.12.0
astroid>=2.8.0
pylint>=2.11.0
```

## Usage

### Command Line Interface

PyBugHunt provides a versatile command-line interface for analyzing Python files:

```bash
# Analyze a single Python file
pybughunt analyze file.py

# Analyze multiple Python files
pybughunt analyze file1.py file2.py file3.py

# Output results in JSON format to a file
pybughunt analyze file.py --format json --output results.json

# Use a custom trained model
pybughunt analyze file.py --model path/to/custom_model.pkl
```

Training a custom model on your codebase:

```bash
# Train a model on a directory containing Python files
pybughunt train --dataset /path/to/python/files --output my_model.pkl
```

### Python API

PyBugHunt can be easily integrated into your Python applications:

```python
from pybughunt import CodeErrorDetector

# Initialize the detector (optionally with a custom model)
detector = CodeErrorDetector()  # or CodeErrorDetector("path/to/model.pkl")

# Analyze code from a string
code = '''
def example():
    print("Hello, world!"  # Missing closing parenthesis

    x = 10  # Unused variable

    while True:
        # Infinite loop without break
        pass
'''

# Get analysis results
results = detector.analyze(code)

# Process syntax errors
if results["syntax_errors"]:
    print(f"Found {len(results['syntax_errors'])} syntax errors:")
    for error in results["syntax_errors"]:
        print(f"  Line {error['line']}: {error['message']}")

# Process logical errors
if results["logic_errors"]:
    print(f"Found {len(results['logic_errors'])} logical errors:")
    for error in results["logic_errors"]:
        print(f"  Line {error['line']}: {error['message']}")

# Get fix suggestions
if results["syntax_errors"] or results["logic_errors"]:
    suggestions = detector.fix_suggestions(code, results)
    for error_key, suggestion in suggestions.items():
        print(f"Suggestion for {error_key}: {suggestion}")
```

For quick analysis, you can also use the shorthand function:

```python
from pybughunt import quick_detect

# Quickly analyze a file
quick_detect(file_path="my_script.py")

# Or analyze code directly
quick_detect(code='''
def hello():
    print("Hello"
''')
```

## Error Detection Capabilities

### Syntax Error Detection

PyBugHunt identifies and provides detailed information about a wide range of syntax errors:

- **Missing Delimiters**

  - Unclosed parentheses, brackets, and braces
  - Unterminated string literals and quotes
  - Missing colons in control flow statements

- **Indentation Issues**

  - Inconsistent indentation
  - Missing indentation after control flow statements
  - Unexpected indentation

- **Invalid Syntax**

  - Invalid tokens and characters
  - Python 2 to Python 3 migration issues (e.g., print statements)
  - Keyword misuse

- **Imports and Module Errors**
  - Invalid import syntax
  - Circular imports (in multi-file analysis)

Each detected syntax error includes:

- Line and column information
- Error type classification
- Descriptive message explaining the issue
- Suggested fixes when possible

### Logical Error Detection

The logical error detection system identifies common patterns that could lead to runtime errors or unexpected behavior:

- **Control Flow Issues**

  - Infinite loops (while True without break)
  - Unreachable code after return/break/continue
  - Empty code blocks with pass statements

- **Variable Usage**

  - Unused variables
  - Variables used before assignment
  - Shadowed variables

- **Algorithm Problems**

  - Potential off-by-one errors in loops (e.g., range(len(x)))
  - Division by zero risks
  - Potential null reference errors

- **Performance Issues**

  - Inefficient list operations
  - Nested loops with redundant computations

- **Bug-Prone Patterns**
  - Mutable default arguments
  - Improper exception handling
  - Improper resource management

## Machine Learning Approach

PyBugHunt employs a sophisticated machine learning approach to detect logical errors that might be missed by traditional static analysis:

### Feature Extraction

- **Code Tokenization**: Conversion of Python code into tokenized sequences
- **TF-IDF Vectorization**: Transformation of code tokens into numerical features
- **AST-Based Features**: Extraction of code structure features from AST
  - Function and class counts
  - Loop and branch counts
  - Exception handling patterns
  - Code complexity metrics

### Model Architecture

The default model uses a pipeline of:

1. **TF-IDF Vectorizer**: Converts tokenized code into numerical features
2. **Random Forest Classifier**: Identifies error patterns based on extracted features

For advanced use cases, PyBugHunt can be configured to use:

- **Transformer-based Models**: Adapted from pre-trained language models for code understanding
- **Custom Neural Networks**: For project-specific error pattern recognition

### Training Process

Models are trained on a diverse corpus of Python code samples with known errors, including:

- Syntax errors
- Runtime errors
- Logical bugs
- Best practice violations

The training process involves:

1. **Data Collection**: Gathering Python code samples with and without errors
2. **Feature Extraction**: Converting code samples into feature vectors
3. **Model Training**: Supervised learning with labeled error examples
4. **Evaluation**: Testing on held-out validation set
5. **Optimization**: Hyperparameter tuning for optimal error detection

## Development

### Project Structure

The PyBugHunt project follows a modular structure:

```
pybughunt/
│
├── src/
│   └── pybughunt/
│       ├── __init__.py           # Package initialization
│       ├── __main__.py           # Entry point for module execution
│       ├── cli.py                # Command line interface
│       ├── detector.py           # Main detector class
│       ├── driver.py             # Quick detection functionality
│       ├── logic_analyzer.py     # Logical error detection
│       ├── syntax_analyzer.py    # Syntax error detection
│       ├── utils.py              # Utility functions
│       ├── sample_buggy.py       # Example buggy code
│       │
│       └── models/               # Machine learning components
│           ├── __init__.py
│           ├── model_loader.py   # Model loading functionality
│           └── model_trainer.py  # Model training functionality
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── test_detector.py
│   ├── test_logic_analyzer.py
│   └── test_syntax_analyzer.py
│
├── .gitignore                    # Git ignore file
├── README.md                     # Project documentation
├── pyproject.toml                # Project metadata and configuration
└── setup.py                      # Package setup script
```

### Testing

PyBugHunt includes a comprehensive test suite to ensure reliability:

```bash
# Run all tests
python -m unittest discover

# Run specific test file
python -m unittest tests/test_detector.py
```

Test coverage includes:

- Unit tests for syntax error detection
- Unit tests for logical error detection
- Integration tests for the full error detection pipeline

## Customization

### Training Custom Models

You can train custom models on your specific codebase to improve error detection:

```python
from pybughunt.models.model_trainer import ModelTrainer

# Create a trainer
trainer = ModelTrainer(output_path="my_custom_model.pkl")

# Prepare your dataset (code samples and error labels)
code_samples = [...]  # List of Python code strings
labels = [...]        # 1 for code with errors, 0 for clean code

# Train the model
model = trainer.train(code_samples, labels)

# Save the model
trainer.save_model()
```

Using the command line:

```bash
# Train on a directory of Python files
pybughunt train --dataset /path/to/python/files --output my_model.pkl
```

### Extending Error Patterns

You can extend PyBugHunt with custom error patterns by subclassing the analyzers:

```python
from pybughunt.logic_analyzer import LogicAnalyzer
import ast

class CustomLogicAnalyzer(LogicAnalyzer):
    def __init__(self, model):
        super().__init__(model)
        # Add your custom pattern check
        self.common_patterns["my_custom_pattern"] = self._check_my_pattern

    def _check_my_pattern(self, tree: ast.AST) -> list:
        # Implement your custom pattern detection
        errors = []
        # ... detection logic
        return errors
```

## License

PyBugHunt is released under the MIT License. See the LICENSE file for details.

## Contributing

Contributions to PyBugHunt are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
