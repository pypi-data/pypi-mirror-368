"""Tests for the core module."""

from unittest.mock import patch

import pikepdf

from pdf_pycrack.core import crack_pdf_password
from pdf_pycrack.models.cracking_result import (
    FileReadError,
    InitializationError,
    NotEncrypted,
    PDFCorruptedError,
)


def test_crack_pdf_password_empty_charset():
    """Test crack_pdf_password with an empty charset."""
    result = crack_pdf_password(
        pdf_path="test.pdf",
        min_len=1,
        max_len=4,
        charset="",  # Empty charset
        num_processes=1,
        batch_size_arg=10,
        report_worker_errors_arg=False,
    )

    # Check that we got an InitializationError result
    assert isinstance(result, InitializationError)
    assert result.error_message == "Charset cannot be empty."
    assert result.error_type == "EmptyCharset"


@patch("pdf_pycrack.core.validate_pdf")
def test_crack_pdf_password_generic_exception(mock_validate_pdf):
    """Test crack_pdf_password when a generic exception is raised during validation."""
    # Make validate_pdf raise a generic exception
    mock_validate_pdf.side_effect = Exception("Generic error")

    # Call crack_pdf_password
    result = crack_pdf_password(
        pdf_path="test.pdf",
        min_len=1,
        max_len=4,
        charset="0123456789",
        num_processes=1,
        batch_size_arg=10,
        report_worker_errors_arg=False,
    )

    # Check that we got an InitializationError result
    assert isinstance(result, InitializationError)
    assert "Generic error" in result.error_message
    assert result.error_type == "Unknown"


@patch("pdf_pycrack.core.validate_pdf")
def test_crack_pdf_password_memory_error(mock_validate_pdf):
    """Test crack_pdf_password when a MemoryError is raised during validation."""
    # Make validate_pdf raise a MemoryError
    mock_validate_pdf.side_effect = MemoryError("Not enough memory")

    # Call crack_pdf_password
    result = crack_pdf_password(
        pdf_path="test.pdf",
        min_len=1,
        max_len=4,
        charset="0123456789",
        num_processes=1,
        batch_size_arg=10,
        report_worker_errors_arg=False,
    )

    # Check that we got an InitializationError result
    assert isinstance(result, InitializationError)
    assert "Not enough memory" in result.error_message
    assert result.error_type == "MemoryError"


@patch("pdf_pycrack.core.validate_pdf")
def test_crack_pdf_password_not_encrypted(mock_validate_pdf):
    """Test crack_pdf_password with a non-encrypted PDF."""
    # Make validate_pdf return False (not encrypted)
    mock_validate_pdf.return_value = False

    # Call crack_pdf_password
    result = crack_pdf_password(
        pdf_path="test.pdf",
        min_len=1,
        max_len=4,
        charset="0123456789",
        num_processes=1,
        batch_size_arg=10,
        report_worker_errors_arg=False,
    )

    # Check that we got a NotEncrypted result
    assert isinstance(result, NotEncrypted)


@patch("pdf_pycrack.core.validate_pdf")
def test_crack_pdf_password_file_not_found(mock_validate_pdf):
    """Test crack_pdf_password when FileNotFoundError is raised during validation."""
    # Make validate_pdf raise FileNotFoundError
    mock_validate_pdf.side_effect = FileNotFoundError("File not found")

    # Call crack_pdf_password
    result = crack_pdf_password(
        pdf_path="nonexistent.pdf",
        min_len=1,
        max_len=4,
        charset="0123456789",
        num_processes=1,
        batch_size_arg=10,
        report_worker_errors_arg=False,
    )

    # Check that we got a FileReadError result
    assert isinstance(result, FileReadError)
    assert "File not found" in result.error_message
    assert result.error_type == "FileNotFoundError"


@patch("pdf_pycrack.core.validate_pdf")
def test_crack_pdf_password_pdf_error(mock_validate_pdf):
    """Test crack_pdf_password when PdfError is raised during validation."""
    # Make validate_pdf raise PdfError
    mock_validate_pdf.side_effect = pikepdf.PdfError("Corrupted PDF")

    # Call crack_pdf_password
    result = crack_pdf_password(
        pdf_path="corrupted.pdf",
        min_len=1,
        max_len=4,
        charset="0123456789",
        num_processes=1,
        batch_size_arg=10,
        report_worker_errors_arg=False,
    )

    # Check that we got a PDFCorruptedError result
    assert isinstance(result, PDFCorruptedError)
    assert "Corrupted PDF" in result.error_message
    assert result.corruption_type == "pdf_error"
