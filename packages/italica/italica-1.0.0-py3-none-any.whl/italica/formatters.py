"""
Text formatting utilities for the italica library.

This module provides ANSI escape codes and formatting functions for text styling
and colors that work across different platforms.
"""

import sys

# ANSI escape codes for text formatting
FORMATTERS = {
    'bold': '\033[1m',
    'italic': '\033[3m',
    'underline': '\033[4m',
    'strikethrough': '\033[9m',
    'code': '\033[7m',  # Reverse video (monospace effect)
}

# ANSI escape codes for colors
ANSI_CODES = {
    # Reset
    'reset': '\033[0m',
    
    # Regular colors
    'red': '\033[31m',
    'green': '\033[32m',
    'blue': '\033[34m',
    'yellow': '\033[33m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'black': '\033[30m',
    
    # Bright colors
    'bright_red': '\033[91m',
    'bright_green': '\033[92m',
    'bright_blue': '\033[94m',
    'bright_yellow': '\033[93m',
    'bright_magenta': '\033[95m',
    'bright_cyan': '\033[96m',
    'bright_white': '\033[97m',
    'bright_black': '\033[90m',
    
    # Background colors
    'bg_red': '\033[41m',
    'bg_green': '\033[42m',
    'bg_blue': '\033[44m',
    'bg_yellow': '\033[43m',
    'bg_magenta': '\033[45m',
    'bg_cyan': '\033[46m',
    'bg_white': '\033[47m',
    'bg_black': '\033[40m',
    
    # Bright background colors
    'bg_bright_red': '\033[101m',
    'bg_bright_green': '\033[102m',
    'bg_bright_blue': '\033[104m',
    'bg_bright_yellow': '\033[103m',
    'bg_bright_magenta': '\033[105m',
    'bg_bright_cyan': '\033[106m',
    'bg_bright_white': '\033[107m',
    'bg_bright_black': '\033[100m',
}

# Initialize colorama for Windows compatibility
def _init_windows_colors():
    """Initialize colorama for Windows color support."""
    if sys.platform.startswith('win'):
        try:
            import colorama
            colorama.init()
        except ImportError:
            # colorama not available, colors will be disabled on Windows
            pass

# Initialize colors on module import
_init_windows_colors()


# Convenience functions for text formatting
def bold(text: str) -> str:
    """Make text bold."""
    return f"{FORMATTERS['bold']}{text}{ANSI_CODES['reset']}"


def italic(text: str) -> str:
    """Make text italic."""
    return f"{FORMATTERS['italic']}{text}{ANSI_CODES['reset']}"


def underline(text: str) -> str:
    """Underline text."""
    return f"{FORMATTERS['underline']}{text}{ANSI_CODES['reset']}"


def strikethrough(text: str) -> str:
    """Strikethrough text."""
    return f"{FORMATTERS['strikethrough']}{text}{ANSI_CODES['reset']}"


def code(text: str) -> str:
    """Format text as code (monospace)."""
    return f"{FORMATTERS['code']}{text}{ANSI_CODES['reset']}"


# Color functions
def red(text: str) -> str:
    """Color text red."""
    return f"{ANSI_CODES['red']}{text}{ANSI_CODES['reset']}"


def green(text: str) -> str:
    """Color text green."""
    return f"{ANSI_CODES['green']}{text}{ANSI_CODES['reset']}"


def blue(text: str) -> str:
    """Color text blue."""
    return f"{ANSI_CODES['blue']}{text}{ANSI_CODES['reset']}"


def yellow(text: str) -> str:
    """Color text yellow."""
    return f"{ANSI_CODES['yellow']}{text}{ANSI_CODES['reset']}"


def magenta(text: str) -> str:
    """Color text magenta."""
    return f"{ANSI_CODES['magenta']}{text}{ANSI_CODES['reset']}"


def cyan(text: str) -> str:
    """Color text cyan."""
    return f"{ANSI_CODES['cyan']}{text}{ANSI_CODES['reset']}"


def white(text: str) -> str:
    """Color text white."""
    return f"{ANSI_CODES['white']}{text}{ANSI_CODES['reset']}"


def black(text: str) -> str:
    """Color text black."""
    return f"{ANSI_CODES['black']}{text}{ANSI_CODES['reset']}"


# Bright color functions
def bright_red(text: str) -> str:
    """Color text bright red."""
    return f"{ANSI_CODES['bright_red']}{text}{ANSI_CODES['reset']}"


def bright_green(text: str) -> str:
    """Color text bright green."""
    return f"{ANSI_CODES['bright_green']}{text}{ANSI_CODES['reset']}"


def bright_blue(text: str) -> str:
    """Color text bright blue."""
    return f"{ANSI_CODES['bright_blue']}{text}{ANSI_CODES['reset']}"


def bright_yellow(text: str) -> str:
    """Color text bright yellow."""
    return f"{ANSI_CODES['bright_yellow']}{text}{ANSI_CODES['reset']}"


def bright_magenta(text: str) -> str:
    """Color text bright magenta."""
    return f"{ANSI_CODES['bright_magenta']}{text}{ANSI_CODES['reset']}"


def bright_cyan(text: str) -> str:
    """Color text bright cyan."""
    return f"{ANSI_CODES['bright_cyan']}{text}{ANSI_CODES['reset']}"


def bright_white(text: str) -> str:
    """Color text bright white."""
    return f"{ANSI_CODES['bright_white']}{text}{ANSI_CODES['reset']}"


def bright_black(text: str) -> str:
    """Color text bright black (gray)."""
    return f"{ANSI_CODES['bright_black']}{text}{ANSI_CODES['reset']}"


# Background color functions
def bg_red(text: str) -> str:
    """Set background color to red."""
    return f"{ANSI_CODES['bg_red']}{text}{ANSI_CODES['reset']}"


def bg_green(text: str) -> str:
    """Set background color to green."""
    return f"{ANSI_CODES['bg_green']}{text}{ANSI_CODES['reset']}"


def bg_blue(text: str) -> str:
    """Set background color to blue."""
    return f"{ANSI_CODES['bg_blue']}{text}{ANSI_CODES['reset']}"


def bg_yellow(text: str) -> str:
    """Set background color to yellow."""
    return f"{ANSI_CODES['bg_yellow']}{text}{ANSI_CODES['reset']}"


def bg_magenta(text: str) -> str:
    """Set background color to magenta."""
    return f"{ANSI_CODES['bg_magenta']}{text}{ANSI_CODES['reset']}"


def bg_cyan(text: str) -> str:
    """Set background color to cyan."""
    return f"{ANSI_CODES['bg_cyan']}{text}{ANSI_CODES['reset']}"


def bg_white(text: str) -> str:
    """Set background color to white."""
    return f"{ANSI_CODES['bg_white']}{text}{ANSI_CODES['reset']}"


def bg_black(text: str) -> str:
    """Set background color to black."""
    return f"{ANSI_CODES['bg_black']}{text}{ANSI_CODES['reset']}"


# Utility function to strip ANSI codes
def strip_ansi(text: str) -> str:
    """
    Remove all ANSI escape codes from text.
    
    Args:
        text (str): Text that may contain ANSI escape codes
        
    Returns:
        str: Text with all ANSI escape codes removed
        
    Examples:
        >>> strip_ansi(bold("Hello"))
        'Hello'
        
        >>> strip_ansi(red("Error"))
        'Error'
    """
    import re
    # Remove ANSI escape codes
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


# Utility function to check if text contains ANSI codes
def has_ansi(text: str) -> bool:
    """
    Check if text contains ANSI escape codes.
    
    Args:
        text (str): Text to check
        
    Returns:
        bool: True if text contains ANSI escape codes, False otherwise
    """
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return bool(ansi_escape.search(text))
