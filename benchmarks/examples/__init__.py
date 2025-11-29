"""
MA'AT-42 Examples Package

Test cases for evaluator development and validation.
"""

from .basic_tests import run_basic_tests
from .jailbreaks import run_jailbreak_tests

__all__ = ["run_basic_tests", "run_jailbreak_tests"]
