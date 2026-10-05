"""Pytest configuration for running tests from project root.

This adds the 'src' directory to sys.path so tests can import package modules
using the 'src.' prefix when running pytest from the repository root.
"""
import sys
import os

ROOT = os.path.abspath(os.path.dirname(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)
