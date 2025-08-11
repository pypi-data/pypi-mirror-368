import time
from unittest.mock import MagicMock, patch

import pytest
from pikepdf import PdfError
from rich.console import Console

from pdf_pycrack.formatting.errors import (
    format_error_context,
    print_error,
    print_info,
    print_warning,
)
from pdf_pycrack.formatting.output import print_end_info, print_start_info
from pdf_pycrack.models.cracking_result import (
    CrackingInterrupted,
    PasswordFound,
    PasswordNotFound,
)


@patch("pdf_pycrack.formatting.errors.console")
def test_print_error(mock_console):
    """Test that print_error calls console.print with the correct structure."""
    print_error(
        "Test Error",
        "This is a test.",
        details="Some details.",
        suggested_actions=["Do this.", "Do that."],
    )
    mock_console.print.assert_called_once()
    call_args = mock_console.print.call_args[0]
    assert "Test Error" in str(call_args[0].title)
    assert "This is a test." in str(call_args[0].renderable)
    assert "Some details." in str(call_args[0].renderable)
    assert "Do this." in str(call_args[0].renderable)


@patch("pdf_pycrack.formatting.errors.console")
def test_print_warning(mock_console):
    """Test that print_warning calls console.print with a warning panel."""
    print_warning("Test Warning", "This is a warning.", suggested_actions=["Check it."])
    mock_console.print.assert_called_once()
    call_args = mock_console.print.call_args[0]
    assert "Test Warning" in str(call_args[0].title)
    assert "orange3" in str(call_args[0].border_style)
    assert "Check it." in str(call_args[0].renderable)


@patch("pdf_pycrack.formatting.errors.console")
def test_print_info(mock_console):
    """Test that print_info calls console.print with an info panel."""
    print_info("Test Info", "This is for your information.")
    mock_console.print.assert_called_once()
    call_args = mock_console.print.call_args[0]
    assert "Test Info" in str(call_args[0].title)
    assert "blue" in str(call_args[0].border_style)
    assert "your information" in str(call_args[0].renderable)


@pytest.mark.parametrize(
    "error_type, exception, expected_title, check_filename",
    [
        ("FileNotFoundError", FileNotFoundError(), "File Not Found", True),
        ("PermissionError", PermissionError(), "Permission Denied", True),
        ("IsADirectoryError", IsADirectoryError(), "Path is a Directory", True),
        ("pikepdf.PdfError", PdfError(), "PDF Processing Error", True),
        ("MemoryError", MemoryError(), "Memory Error", False),
        ("UnknownError", ValueError("Generic"), "PDF Error", True),
    ],
)
def test_format_error_context(error_type, exception, expected_title, check_filename):
    """Test that error contexts are formatted correctly for different error types."""
    context = format_error_context(error_type, "/path/to/file.pdf", exception)
    assert context["title"] == expected_title
    if check_filename:
        assert "file.pdf" in context["message"]
    assert isinstance(context["suggested_actions"], list)


@patch("pdf_pycrack.formatting.output.console", new_callable=MagicMock)
def test_print_start_info(mock_console):
    """Test that print_start_info displays the correct initial setup."""
    # Use a real console with capturing to inspect the output
    console = Console(record=True)
    with patch("pdf_pycrack.formatting.output.console", console):
        print_start_info(
            pdf_file="test.pdf",
            min_length=1,
            max_length=4,
            charset="abc",
            batch_size=100,
            cores=4,
            start_time=time.time(),
        )

    output = console.export_text()
    assert "test.pdf" in output
    assert "1 to 4" in output
    assert "abc" in output
    assert "100" in output
    assert "4" in output


@patch("pdf_pycrack.formatting.output.console")
def test_print_end_info_password_found(mock_console):
    """Test end info for a successful password recovery."""
    result = PasswordFound(
        password="123",
        passwords_checked=1000,
        elapsed_time=10.0,
        passwords_per_second=100.0,
    )
    print_end_info(result)
    mock_console.print.assert_called_once()
    call_args = mock_console.print.call_args[0]

    # Capture rendered output to check content
    console = Console(record=True)
    console.print(call_args[0])
    output = console.export_text()

    assert "Cracking Successful" in output
    assert "Password found" in output
    assert "123" in output
    assert "100.00" in output  # Passwords/sec


@patch("pdf_pycrack.formatting.output.console")
def test_print_end_info_password_not_found(mock_console):
    """Test end info for a failed password recovery."""
    result = PasswordNotFound(
        passwords_checked=5000, elapsed_time=20.0, passwords_per_second=250.0
    )
    print_end_info(result)
    mock_console.print.assert_called_once()
    call_args = mock_console.print.call_args[0]

    console = Console(record=True)
    console.print(call_args[0])
    output = console.export_text()

    assert "Cracking Failed" in output
    assert "Password not found" in output
    assert "250.00" in output  # Passwords/sec


@patch("pdf_pycrack.formatting.output.console")
def test_print_end_info_interrupted(mock_console):
    """Test end info for an interrupted process."""
    result = CrackingInterrupted(passwords_checked=100, elapsed_time=5.0)
    print_end_info(result)
    mock_console.print.assert_called_once()
    call_args = mock_console.print.call_args[0]

    console = Console(record=True)
    console.print(call_args[0])
    output = console.export_text()

    assert "Cracking Interrupted" in output
    assert "interrupted by user" in output
