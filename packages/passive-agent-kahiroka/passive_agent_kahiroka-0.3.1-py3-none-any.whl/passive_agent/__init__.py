"""
Passive Agent - A tool for prompt engineering experiments with instruction-based context building.

This package provides a flexible system for processing instructions that combine
file content and AI completions to build complex contexts for prompt engineering.
"""

__version__ = "0.1.0"

from .core import (
    read_file,
    read_directory,
    process_instructions,
    perform_completion,
    main
)

__all__ = [
    'read_file',
    'read_directory',
    'process_instructions',
    'perform_completion',
    'main',
]