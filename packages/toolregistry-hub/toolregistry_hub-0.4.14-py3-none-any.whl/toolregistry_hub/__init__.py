"""ToolRegistry Hub module providing commonly used tools.

This module serves as a central hub for various utility tools including:
- Calculator: Basic arithmetic operations
- FileSystem: File system operations
- FileOps: File manipulation functions
- UnitConverter: Unit conversion functions

Example:
    >>> from toolregistry.hub import Calculator, FileSystem, FileOps
    >>> calc = Calculator()
    >>> result = calc.add(1, 2)
    >>> fs = FileSystem()
    >>> exists = fs.exists('/path/to/file')
    >>> ops = FileOps()
    >>> ops.replace_lines('file.txt', 5, 'new content')
"""

from .calculator import BaseCalculator, Calculator
from .file_ops import FileOps
from .filesystem import FileSystem
from .unit_converter import UnitConverter
from .websearch import (
    Fetch,
    WebSearchBing,
    WebSearchGeneral,
    WebSearchGoogle,
    WebSearchSearXNG,
)

__all__ = [
    "BaseCalculator",
    "Calculator",
    "FileSystem",
    "FileOps",
    "UnitConverter",
    # WebSearch related tools
    "Fetch",
    "WebSearchGeneral",
    "WebSearchBing",
    "WebSearchGoogle",
    "WebSearchSearXNG",
]

version = "0.4.14"  # standalone version
