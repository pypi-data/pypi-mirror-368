"""
Tests for the core functionality of the italica library.
"""

import sys
import io
import pytest
from italica.core import format_text, print_fmt, input_fmt, _supports_color
from italica.formatters import strip_ansi, has_ansi


class TestFormatText:
    """Test the format_text function."""
    
    def test_bold_formatting(self):
        """Test bold text formatting."""
        result = format_text("Hello **world**!")
        assert "**world**" not in result
        assert has_ansi(result)
    
    def test_italic_formatting(self):
        """Test italic text formatting."""
        result = format_text("This is *italic* text")
        assert "*italic*" not in result
        assert has_ansi(result)
    
    def test_strikethrough_formatting(self):
        """Test strikethrough text formatting."""
        result = format_text("This is ~~crossed out~~ text")
        assert "~~crossed out~~" not in result
        assert has_ansi(result)
    
    def test_code_formatting(self):
        """Test code text formatting."""
        result = format_text("This is `code` text")
        assert "`code`" not in result
        assert has_ansi(result)
    
    def test_color_formatting(self):
        """Test color text formatting."""
        result = format_text("[red]Red text[/red]")
        assert "[red]Red text[/red]" not in result
        assert has_ansi(result)
    
    def test_bright_color_formatting(self):
        """Test bright color text formatting."""
        result = format_text("[bright_red]Bright red text[/bright_red]")
        assert "[bright_red]Bright red text[/bright_red]" not in result
        assert has_ansi(result)
    
    def test_combined_formatting(self):
        """Test combined formatting."""
        result = format_text("This is **bold** and *italic* and ~~strikethrough~~")
        assert "**bold**" not in result
        assert "*italic*" not in result
        assert "~~strikethrough~~" not in result
        assert has_ansi(result)
    
    def test_no_formatting(self):
        """Test text with no formatting."""
        text = "Plain text without formatting"
        result = format_text(text)
        assert result == text
        assert not has_ansi(result)
    
    def test_empty_string(self):
        """Test empty string formatting."""
        result = format_text("")
        assert result == ""
    
    def test_none_string(self):
        """Test None string formatting."""
        result = format_text(None)
        assert result == ""
    
    def test_disable_colors(self):
        """Test formatting with colors disabled."""
        result = format_text("**bold** [red]red[/red]", enable_colors=False)
        assert result == "**bold** [red]red[/red]"
        assert not has_ansi(result)


class TestPrintFmt:
    """Test the print_fmt function."""
    
    def test_basic_print(self, capsys):
        """Test basic print functionality."""
        print_fmt("Hello world")
        captured = capsys.readouterr()
        assert "Hello world" in captured.out
    
    def test_formatted_print(self, capsys):
        """Test formatted print functionality."""
        print_fmt("Hello **world**!")
        captured = capsys.readouterr()
        assert "Hello" in captured.out
        assert "world" in captured.out
        assert "**world**" not in captured.out
    
    def test_multiple_args(self, capsys):
        """Test print with multiple arguments."""
        print_fmt("Hello", "**world**", "!")
        captured = capsys.readouterr()
        assert "Hello" in captured.out
        assert "world" in captured.out
        assert "!" in captured.out
    
    def test_custom_sep(self, capsys):
        """Test print with custom separator."""
        print_fmt("Hello", "world", sep="|")
        captured = capsys.readouterr()
        assert "Hello|world" in captured.out
    
    def test_custom_end(self, capsys):
        """Test print with custom end."""
        print_fmt("Hello", end="!")
        captured = capsys.readouterr()
        assert captured.out == "Hello!"
    
    def test_disable_colors(self, capsys):
        """Test print with colors disabled."""
        print_fmt("**bold** [red]red[/red]", enable_colors=False)
        captured = capsys.readouterr()
        assert "**bold** [red]red[/red]" in captured.out
    
    def test_file_output(self):
        """Test print to file."""
        output = io.StringIO()
        print_fmt("Hello world", file=output)
        assert "Hello world" in output.getvalue()


class TestInputFmt:
    """Test the input_fmt function."""
    
    def test_basic_input(self, monkeypatch):
        """Test basic input functionality."""
        monkeypatch.setattr('builtins.input', lambda x: "test")
        result = input_fmt("Enter name: ")
        assert result == "test"
    
    def test_formatted_input(self, monkeypatch):
        """Test formatted input functionality."""
        monkeypatch.setattr('builtins.input', lambda x: "test")
        result = input_fmt("Enter your **name**: ")
        assert result == "test"
    
    def test_colored_input(self, monkeypatch):
        """Test colored input functionality."""
        monkeypatch.setattr('builtins.input', lambda x: "test")
        result = input_fmt("[green]Enter name:[/green] ")
        assert result == "test"
    
    def test_disable_colors(self, monkeypatch):
        """Test input with colors disabled."""
        monkeypatch.setattr('builtins.input', lambda x: "test")
        result = input_fmt("**bold** [red]red[/red]", enable_colors=False)
        assert result == "test"


class TestSupportsColor:
    """Test the _supports_color function."""
    
    def test_windows_platform(self, monkeypatch):
        """Test color support detection on Windows."""
        monkeypatch.setattr(sys, 'platform', 'win32')
        
        # Test with colorama available
        try:
            import colorama
            assert _supports_color(sys.stdout) == True
        except ImportError:
            # Without colorama, should return False on Windows
            assert _supports_color(sys.stdout) == False
    
    def test_unix_platform(self, monkeypatch):
        """Test color support detection on Unix."""
        monkeypatch.setattr(sys, 'platform', 'linux')
        
        # Mock isatty to return True
        class MockStream:
            def isatty(self):
                return True
        
        assert _supports_color(MockStream()) == True
    
    def test_non_terminal_stream(self, monkeypatch):
        """Test color support detection for non-terminal streams."""
        monkeypatch.setattr(sys, 'platform', 'linux')
        
        # Mock isatty to return False
        class MockStream:
            def isatty(self):
                return False
        
        assert _supports_color(MockStream()) == False


class TestStripAnsi:
    """Test the strip_ansi function."""
    
    def test_strip_ansi_codes(self):
        """Test stripping ANSI escape codes."""
        from italica.formatters import bold, red
        
        bold_text = bold("Hello")
        red_text = red("World")
        
        assert strip_ansi(bold_text) == "Hello"
        assert strip_ansi(red_text) == "World"
    
    def test_no_ansi_codes(self):
        """Test stripping from text without ANSI codes."""
        text = "Plain text"
        assert strip_ansi(text) == text
    
    def test_empty_string(self):
        """Test stripping from empty string."""
        assert strip_ansi("") == ""


class TestHasAnsi:
    """Test the has_ansi function."""
    
    def test_has_ansi_codes(self):
        """Test detection of ANSI codes."""
        from italica.formatters import bold, red
        
        bold_text = bold("Hello")
        red_text = red("World")
        
        assert has_ansi(bold_text) == True
        assert has_ansi(red_text) == True
    
    def test_no_ansi_codes(self):
        """Test detection of text without ANSI codes."""
        text = "Plain text"
        assert has_ansi(text) == False
    
    def test_empty_string(self):
        """Test detection in empty string."""
        assert has_ansi("") == False


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_print_bold(self, capsys):
        """Test print_bold function."""
        from italica.core import print_bold
        print_bold("Hello")
        captured = capsys.readouterr()
        assert "Hello" in captured.out
        assert has_ansi(captured.out)
    
    def test_print_italic(self, capsys):
        """Test print_italic function."""
        from italica.core import print_italic
        print_italic("Hello")
        captured = capsys.readouterr()
        assert "Hello" in captured.out
        assert has_ansi(captured.out)
    
    def test_print_error(self, capsys):
        """Test print_error function."""
        from italica.core import print_error
        print_error("Error message")
        captured = capsys.readouterr()
        assert "Error message" in captured.out
        assert has_ansi(captured.out)
    
    def test_print_success(self, capsys):
        """Test print_success function."""
        from italica.core import print_success
        print_success("Success message")
        captured = capsys.readouterr()
        assert "Success message" in captured.out
        assert has_ansi(captured.out)
    
    def test_print_warning(self, capsys):
        """Test print_warning function."""
        from italica.core import print_warning
        print_warning("Warning message")
        captured = capsys.readouterr()
        assert "Warning message" in captured.out
        assert has_ansi(captured.out)


if __name__ == "__main__":
    pytest.main([__file__])
