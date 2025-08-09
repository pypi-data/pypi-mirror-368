"""
Core functionality for the italica library.

This module provides the main functions for formatting text with markdown-style syntax
and handling print and input operations with formatting.
"""

import sys
import re
from typing import Optional, Any
from .formatters import FORMATTERS, ANSI_CODES


def format_text(text: str, enable_colors: bool = True) -> str:
    """
    Format text with markdown-style syntax.
    
    Supported formats:
    - **text** or __text__ -> bold
    - *text* or _text_ -> italic
    - ~~text~~ -> strikethrough
    - `text` -> code (monospace)
    - [color]text[/color] -> colored text (where color is red, green, blue, etc.)
    
    Args:
        text (str): The text to format
        enable_colors (bool): Whether to enable color formatting (default: True)
        
    Returns:
        str: The formatted text with ANSI escape codes
        
    Examples:
        >>> format_text("Hello **world**!")
        'Hello \x1b[1mworld\x1b[0m!'
        
        >>> format_text("This is *italic* and **bold**")
        'This is \x1b[3mitalic\x1b[0m and \x1b[1mbold\x1b[0m'
    """
    if not text:
        return text
    
    # Define markdown patterns
    patterns = [
        # Bold: **text** or __text__
        (r'\*\*(.*?)\*\*', 'bold'),
        (r'__(.*?)__', 'bold'),
        
        # Italic: *text* or _text_
        (r'\*(.*?)\*', 'italic'),
        (r'_(.*?)_', 'italic'),
        
        # Strikethrough: ~~text~~
        (r'~~(.*?)~~', 'strikethrough'),
        
        # Code: `text`
        (r'`(.*?)`', 'code'),
        
        # Colors: [color]text[/color]
        (r'\[(red|green|blue|yellow|magenta|cyan|bright_red|bright_green|bright_blue|bright_yellow|bright_magenta|bright_cyan)\](.*?)\[/\1\]', 'color'),
    ]
    
    formatted_text = text
    
    for pattern, format_type in patterns:
        if format_type == 'color':
            # Handle color formatting
            def color_replace(match):
                color_name = match.group(1)
                content = match.group(2)
                if enable_colors and color_name in ANSI_CODES:
                    return f"{ANSI_CODES[color_name]}{content}{ANSI_CODES['reset']}"
                return content
            
            formatted_text = re.sub(pattern, color_replace, formatted_text)
        else:
            # Handle other formatting
            def format_replace(match):
                content = match.group(1)
                if enable_colors and format_type in FORMATTERS:
                    return f"{FORMATTERS[format_type]}{content}{ANSI_CODES['reset']}"
                return content
            
            formatted_text = re.sub(pattern, format_replace, formatted_text)
    
    return formatted_text


def print_fmt(*args, sep: str = " ", end: str = "\n", file=None, flush: bool = False, 
              enable_colors: bool = None) -> None:
    """
    Print formatted text with markdown-style syntax.
    
    This function works like the built-in print() function but supports markdown formatting.
    
    Args:
        *args: Objects to print
        sep (str): Separator between objects (default: " ")
        end (str): String appended after the last value (default: "\n")
        file: A file-like object to write to (default: sys.stdout)
        flush (bool): Whether to forcibly flush the stream (default: False)
        enable_colors (bool): Whether to enable color formatting. If None, auto-detects terminal support
        
    Examples:
        >>> print_fmt("Hello **world**!")
        Hello world! (with bold formatting)
        
        >>> print_fmt("This is *italic* and **bold**")
        This is italic and bold (with formatting)
        
        >>> print_fmt("[red]Error message[/red]")
        Error message (in red)
    """
    if enable_colors is None:
        enable_colors = _supports_color(file or sys.stdout)
    
    # Format each argument
    formatted_args = []
    for arg in args:
        if isinstance(arg, str):
            formatted_args.append(format_text(arg, enable_colors))
        else:
            formatted_args.append(str(arg))
    
    # Join and print
    text = sep.join(formatted_args)
    print(text, end=end, file=file, flush=flush)


def input_fmt(prompt: str = "", enable_colors: bool = None) -> str:
    """
    Get user input with formatted prompt.
    
    This function works like the built-in input() function but supports markdown formatting in the prompt.
    
    Args:
        prompt (str): The prompt to display (supports markdown formatting)
        enable_colors (bool): Whether to enable color formatting. If None, auto-detects terminal support
        
    Returns:
        str: The user's input
        
    Examples:
        >>> name = input_fmt("Enter your **name**: ")
        Enter your name: (with bold formatting)
        
        >>> age = input_fmt("[green]How old are you?[/green] ")
        How old are you? (in green)
    """
    if enable_colors is None:
        enable_colors = _supports_color(sys.stdout)
    
    formatted_prompt = format_text(prompt, enable_colors)
    return input(formatted_prompt)


def _supports_color(stream) -> bool:
    """
    Check if the given stream supports color output.
    
    Args:
        stream: The stream to check
        
    Returns:
        bool: True if the stream supports colors, False otherwise
    """
    # Check if we're on Windows
    if sys.platform.startswith('win'):
        # On Windows, check if we're in a terminal that supports colors
        try:
            import colorama
            return True
        except ImportError:
            # Without colorama, Windows console doesn't support ANSI colors well
            return False
    
    # On Unix-like systems, check if we're in a terminal
    if hasattr(stream, 'isatty') and stream.isatty():
        return True
    
    return False


# Convenience functions for common use cases
def print_bold(text: str, **kwargs) -> None:
    """Print text in bold."""
    print_fmt(f"**{text}**", **kwargs)


def print_italic(text: str, **kwargs) -> None:
    """Print text in italic."""
    print_fmt(f"*{text}*", **kwargs)


def print_error(text: str, **kwargs) -> None:
    """Print text in red (for error messages)."""
    print_fmt(f"[red]{text}[/red]", **kwargs)


def print_success(text: str, **kwargs) -> None:
    """Print text in green (for success messages)."""
    print_fmt(f"[green]{text}[/green]", **kwargs)


def print_warning(text: str, **kwargs) -> None:
    """Print text in yellow (for warning messages)."""
    print_fmt(f"[yellow]{text}[/yellow]", **kwargs)
