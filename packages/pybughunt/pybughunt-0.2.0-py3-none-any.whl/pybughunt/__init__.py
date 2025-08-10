"""Code Error Detector - A Python library for detecting logical and syntactical errors in Python code."""

from .detector import CodeErrorDetector
from .driver import main as quick_detect

__version__ = "0.2.0"
__all__ = ["CodeErrorDetector", "quick_detect"]
