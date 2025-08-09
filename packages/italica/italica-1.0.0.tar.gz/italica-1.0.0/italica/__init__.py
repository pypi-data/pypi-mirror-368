"""
Italica - A simple library for adding markdown-style formatting to print and input functions.

This library provides easy-to-use functions for formatting text in the terminal
with markdown-style syntax like **bold**, *italic*, and more.

Author: 7vntii
GitHub: https://github.com/7vntii
PyPI: https://pypi.org/user/7vntii
"""

__version__ = "1.0.0"
__author__ = "7vntii"
__email__ = "jj9dptr57@mozmail.com"
__url__ = "https://github.com/7vntii/italica"

from .core import print_fmt, input_fmt, format_text
from .formatters import (
    bold, italic, underline, strikethrough, 
    red, green, blue, yellow, magenta, cyan,
    bright_red, bright_green, bright_blue, bright_yellow, bright_magenta, bright_cyan
)

__all__ = [
    # Main functions
    'print_fmt', 'input_fmt', 'format_text',
    
    # Text formatting
    'bold', 'italic', 'underline', 'strikethrough',
    
    # Colors
    'red', 'green', 'blue', 'yellow', 'magenta', 'cyan',
    'bright_red', 'bright_green', 'bright_blue', 'bright_yellow', 'bright_magenta', 'bright_cyan',
    
    # Version info
    '__version__', '__author__', '__email__', '__url__'
]
