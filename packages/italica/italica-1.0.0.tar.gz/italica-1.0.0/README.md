# Italica

A simple and elegant Python library for adding markdown-style formatting to print and input functions. Make your terminal output beautiful with bold, italic, colors, and more!

[![PyPI version](https://badge.fury.io/py/italica.svg)](https://badge.fury.io/py/italica)
[![Python versions](https://img.shields.io/pypi/pyversions/italica.svg)](https://pypi.org/project/italica/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🎨 **Markdown-style formatting** - Use familiar syntax like `**bold**`, `*italic*`, `~~strikethrough~~`
- 🌈 **Rich color support** - 16 colors including bright variants
- 🖥️ **Cross-platform** - Works on Windows, macOS, and Linux
- ⚡ **Zero dependencies** - Uses only Python standard library
- 🔧 **Easy to use** - Drop-in replacement for `print()` and `input()`
- 🎯 **Auto-detection** - Automatically detects terminal color support

## Installation

```bash
pip install italica
```

## Quick Start

```python
from italica import print_fmt, input_fmt

# Print formatted text
print_fmt("Hello **world**!")  # Bold text
print_fmt("This is *italic*")  # Italic text
print_fmt("[red]Error message[/red]")  # Red text

# Get input with formatted prompt
name = input_fmt("Enter your **name**: ")
age = input_fmt("[green]How old are you?[/green] ")
```

## Usage

### Basic Formatting

```python
from italica import print_fmt

# Bold text
print_fmt("This is **bold** text")

# Italic text  
print_fmt("This is *italic* text")

# Strikethrough
print_fmt("This is ~~crossed out~~ text")

# Code/monospace
print_fmt("This is `code` text")

# Combined formatting
print_fmt("This is **bold** and *italic* and ~~strikethrough~~")
```

### Colors

```python
from italica import print_fmt

# Basic colors
print_fmt("[red]Red text[/red]")
print_fmt("[green]Green text[/green]")
print_fmt("[blue]Blue text[/blue]")
print_fmt("[yellow]Yellow text[/yellow]")
print_fmt("[magenta]Magenta text[/magenta]")
print_fmt("[cyan]Cyan text[/cyan]")

# Bright colors
print_fmt("[bright_red]Bright red text[/bright_red]")
print_fmt("[bright_green]Bright green text[/bright_green]")
print_fmt("[bright_blue]Bright blue text[/bright_blue]")
print_fmt("[bright_yellow]Bright yellow text[/bright_yellow]")
print_fmt("[bright_magenta]Bright magenta text[/bright_magenta]")
print_fmt("[bright_cyan]Bright cyan text[/bright_cyan]")
```

### Input with Formatting

```python
from italica import input_fmt

# Simple formatted input
name = input_fmt("Enter your **name**: ")

# Colored input prompts
age = input_fmt("[green]How old are you?[/green] ")
email = input_fmt("[blue]Enter your email:[/blue] ")

# Complex formatting
password = input_fmt("[red]Enter your **password**:[/red] ")
```

### Convenience Functions

```python
from italica import print_bold, print_italic, print_error, print_success, print_warning

# Quick formatting functions
print_bold("This is bold!")
print_italic("This is italic!")

# Predefined message types
print_error("Something went wrong!")
print_success("Operation completed successfully!")
print_warning("Please be careful!")
```

### Direct Formatting Functions

```python
from italica import bold, italic, red, green, blue

# Format text directly
text = bold("This is bold")
colored_text = red("This is red")

# Combine formatting
formatted = bold(red("Bold red text"))
```

## API Reference

### Main Functions

#### `print_fmt(*args, sep=" ", end="\n", file=None, flush=False, enable_colors=None)`

Print formatted text with markdown-style syntax.

**Parameters:**
- `*args`: Objects to print
- `sep` (str): Separator between objects (default: " ")
- `end` (str): String appended after the last value (default: "\n")
- `file`: A file-like object to write to (default: sys.stdout)
- `flush` (bool): Whether to forcibly flush the stream (default: False)
- `enable_colors` (bool): Whether to enable color formatting. If None, auto-detects terminal support

#### `input_fmt(prompt="", enable_colors=None)`

Get user input with formatted prompt.

**Parameters:**
- `prompt` (str): The prompt to display (supports markdown formatting)
- `enable_colors` (bool): Whether to enable color formatting. If None, auto-detects terminal support

**Returns:**
- `str`: The user's input

#### `format_text(text, enable_colors=True)`

Format text with markdown-style syntax.

**Parameters:**
- `text` (str): The text to format
- `enable_colors` (bool): Whether to enable color formatting (default: True)

**Returns:**
- `str`: The formatted text with ANSI escape codes

### Convenience Functions

#### Text Formatting
- `print_bold(text, **kwargs)` - Print text in bold
- `print_italic(text, **kwargs)` - Print text in italic
- `print_error(text, **kwargs)` - Print text in red (for error messages)
- `print_success(text, **kwargs)` - Print text in green (for success messages)
- `print_warning(text, **kwargs)` - Print text in yellow (for warning messages)

#### Direct Formatting
- `bold(text)` - Make text bold
- `italic(text)` - Make text italic
- `underline(text)` - Underline text
- `strikethrough(text)` - Strikethrough text
- `code(text)` - Format text as code (monospace)

#### Colors
- `red(text)`, `green(text)`, `blue(text)`, `yellow(text)`, `magenta(text)`, `cyan(text)`
- `bright_red(text)`, `bright_green(text)`, `bright_blue(text)`, `bright_yellow(text)`, `bright_magenta(text)`, `bright_cyan(text)`

## Supported Markdown Syntax

| Syntax | Description | Example |
|--------|-------------|---------|
| `**text**` or `__text__` | Bold | `**Hello**` |
| `*text*` or `_text_` | Italic | `*World*` |
| `~~text~~` | Strikethrough | `~~Old text~~` |
| `` `text` `` | Code/monospace | `` `code` `` |
| `[color]text[/color]` | Colored text | `[red]Error[/red]` |

## Supported Colors

### Basic Colors
- `red`, `green`, `blue`, `yellow`, `magenta`, `cyan`, `white`, `black`

### Bright Colors
- `bright_red`, `bright_green`, `bright_blue`, `bright_yellow`, `bright_magenta`, `bright_cyan`, `bright_white`, `bright_black`

## Examples

### Simple Chat Application

```python
from italica import print_fmt, input_fmt

print_fmt("[cyan]=== Welcome to Chat App ===[/cyan]")
print_fmt("")

name = input_fmt("Enter your **name**: ")
print_fmt(f"Hello **{name}**! Welcome to the chat.")

while True:
    message = input_fmt(f"[green]{name}[/green]: ")
    if message.lower() == 'quit':
        print_fmt("[yellow]Goodbye![/yellow]")
        break
    print_fmt(f"[blue]You said:[/blue] {message}")
```

### Error Handling

```python
from italica import print_fmt, print_error, print_success, print_warning

def process_data(data):
    try:
        # Process data
        result = data * 2
        print_success(f"Data processed successfully: {result}")
        return result
    except ValueError:
        print_error("Invalid data format!")
    except Exception as e:
        print_warning(f"Unexpected error: {e}")

# Usage
process_data(5)  # Success
process_data("invalid")  # Error
```

### Progress Indicator

```python
from italica import print_fmt
import time

def show_progress():
    steps = ["Loading...", "Processing...", "Saving...", "Complete!"]
    colors = ["yellow", "blue", "green", "bright_green"]
    
    for step, color in zip(steps, colors):
        print_fmt(f"[{color}]{step}[/{color}]")
        time.sleep(1)

show_progress()
```

## Platform Support

### Windows
- ✅ Full support with colorama (optional dependency)
- ✅ ANSI colors work in modern terminals (Windows 10+)
- ✅ Fallback to plain text if colors not supported

### macOS
- ✅ Full support
- ✅ Native ANSI color support
- ✅ Works in Terminal.app, iTerm2, and other terminals

### Linux
- ✅ Full support
- ✅ Native ANSI color support
- ✅ Works in all major terminals

## Installation for Development

```bash
# Clone the repository
git clone https://github.com/7vntii/italica.git
cd italica

# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**7vntii**
- GitHub: [https://github.com/7vntii](https://github.com/7vntii)
- PyPI: [https://pypi.org/user/7vntii](https://pypi.org/user/7vntii)
- Email: jj9dptr57@mozmail.com
- YouTube: [https://www.youtube.com/@7vntii](https://www.youtube.com/@7vntii)

## Changelog

### Version 1.0.0
- Initial release
- Markdown-style formatting support
- Color support with 16 colors
- Cross-platform compatibility
- Auto-detection of terminal color support
- Convenience functions for common use cases

## Acknowledgments

- Inspired by the need for simple, beautiful terminal output
- Built with cross-platform compatibility in mind
- Uses ANSI escape codes for maximum compatibility
