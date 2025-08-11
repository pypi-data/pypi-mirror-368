"""Tests for the validator module."""

from unittest.mock import patch

import pikepdf
import pytest

from pdf_pycrack.validator import validate_pdf


def test_validate_pdf_not_encrypted():
    """Test validate_pdf with a non-encrypted PDF."""
    with patch("pikepdf.open") as mock_open:
        # Mock the context manager - PDF opens successfully (not encrypted)
        mock_open.return_value.__enter__.return_value
        # validate_pdf should return False for non-encrypted PDFs
        result = validate_pdf("test.pdf")
        assert result is False


def test_validate_pdf_encrypted():
    """Test validate_pdf with an encrypted PDF."""
    with patch("pikepdf.open") as mock_open:
        # Make the open function raise PasswordError
        mock_open.side_effect = pikepdf.PasswordError("Password required")
        # validate_pdf should return True for encrypted PDFs
        result = validate_pdf("test.pdf")
        assert result is True


def test_validate_pdf_corrupted():
    """Test validate_pdf with a corrupted PDF."""
    with patch("pikepdf.open") as mock_open:
        # Make the open function raise PdfError
        mock_open.side_effect = pikepdf.PdfError("Corrupted PDF")
        # validate_pdf should re-raise PdfError
        with pytest.raises(pikepdf.PdfError):
            validate_pdf("test.pdf")


def test_validate_pdf_file_not_found():
    """Test validate_pdf with a non-existent file."""
    # validate_pdf should re-raise FileNotFoundError
    with pytest.raises(FileNotFoundError):
        validate_pdf("nonexistent.pdf")


@patch("pikepdf.open")
def test_validate_pdf_runtime_error_directory(mock_open):
    """Test validate_pdf when a RuntimeError with 'Is a directory' is raised."""
    # Make the open function raise RuntimeError with "Is a directory"
    mock_open.side_effect = RuntimeError("Is a directory")
    # validate_pdf should convert this to IsADirectoryError
    with pytest.raises(IsADirectoryError):
        validate_pdf("test.pdf")


@patch("pikepdf.open")
def test_validate_pdf_runtime_error_other(mock_open):
    """Test validate_pdf when a RuntimeError with other message is raised."""
    # Make the open function raise RuntimeError with other message
    mock_open.side_effect = RuntimeError("Other error")
    # validate_pdf should re-raise the RuntimeError
    with pytest.raises(RuntimeError):
        validate_pdf("test.pdf")


@patch("pikepdf.open")
def test_validate_pdf_generic_exception(mock_open):
    """Test validate_pdf when a generic exception is raised."""
    # Make the open function raise a generic exception
    mock_open.side_effect = Exception("Generic error")
    # validate_pdf should convert this to RuntimeError
    with pytest.raises(RuntimeError) as exc_info:
        validate_pdf("test.pdf")

    # Check that the error message contains the expected text
    assert "Error during initial check with pikepdf" in str(exc_info.value)
