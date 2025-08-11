"""Comprehensive error handling tests for PDF password cracking.

This module contains tests that verify proper error handling for various
failure scenarios including file system errors, PDF corruption, and
invalid parameters.
"""

import os
import tempfile
from unittest.mock import patch

import pikepdf

from pdf_pycrack.core import crack_pdf_password
from pdf_pycrack.models.cracking_result import (
    FileReadError,
    InitializationError,
    NotEncrypted,
    PasswordNotFound,
    PDFCorruptedError,
)


class TestErrorHandling:
    """Test suite for comprehensive error handling in PDF cracking."""

    def test_file_not_found_error(self):
        """Test handling of non-existent PDF files."""
        result = crack_pdf_password(
            "non_existent_file.pdf", min_len=1, max_len=1, charset="a"
        )
        assert isinstance(result, FileReadError)
        assert result.error_type == "FileNotFoundError"
        assert result.file_path is not None
        assert "non_existent_file.pdf" in str(result.file_path)

    def test_permission_denied_error(self):
        """Test handling of permission denied errors."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"dummy content")
            tmp_path = tmp.name

        try:
            # Mock permission error
            with patch(
                "builtins.open", side_effect=PermissionError("Permission denied")
            ):
                result = crack_pdf_password(tmp_path, min_len=1, max_len=1, charset="a")
            assert isinstance(result, FileReadError)
            assert result.error_type == "PermissionError"
            assert result.file_path is not None
            assert tmp_path in str(result.file_path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_is_a_directory_error(self):
        """Test handling when path is a directory instead of file."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = crack_pdf_password(tmp_dir, min_len=1, max_len=1, charset="a")
            assert isinstance(result, FileReadError)
            assert result.error_type == "IsADirectoryError"
            assert result.file_path is not None
            assert tmp_dir in str(result.file_path)

    def test_empty_charset_error(self):
        """Test handling of empty charset."""
        result = crack_pdf_password(
            "tests/test_pdfs/numbers/100.pdf", min_len=1, max_len=1, charset=""
        )
        assert isinstance(result, InitializationError)
        assert "empty" in result.error_message.lower()

    def test_pdf_corruption_error(self):
        """Test handling of corrupted PDF files."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"corrupted pdf content")
            tmp_path = tmp.name

        try:
            result = crack_pdf_password(tmp_path, min_len=1, max_len=1, charset="a")
            # Should handle corrupted PDF gracefully
            assert isinstance(
                result, (PDFCorruptedError, FileReadError, InitializationError)
            )
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_memory_error_handling(self):
        """Test handling of memory errors during file reading."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"dummy content")
            tmp_path = tmp.name

        try:
            # Mock memory error
            with patch("builtins.open", side_effect=MemoryError("Out of memory")):
                result = crack_pdf_password(tmp_path, min_len=1, max_len=1, charset="a")
            assert isinstance(result, (FileReadError, InitializationError))
            assert result.error_type is not None
            assert (
                "MemoryError" in str(result.error_type)
                or "memory" in result.error_message.lower()
            )
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_not_encrypted_pdf(self):
        """Test handling of unencrypted PDF files."""
        result = crack_pdf_password(
            "tests/test_pdfs/unencrypted.pdf", min_len=1, max_len=1, charset="a"
        )
        assert isinstance(result, NotEncrypted)

    def test_error_context_in_file_read_error(self):
        """Test that FileReadError contains proper context."""
        result = crack_pdf_password(
            "non_existent_file.pdf", min_len=1, max_len=1, charset="a"
        )
        assert isinstance(result, FileReadError)
        assert result.file_path is not None
        assert result.error_type is not None
        assert isinstance(result.suggested_actions, list)

    def test_error_context_in_initialization_error(self):
        """Test that InitializationError contains proper context."""
        result = crack_pdf_password(
            "tests/test_pdfs/numbers/100.pdf", min_len=1, max_len=1, charset=""
        )
        assert isinstance(result, InitializationError)
        assert result.error_type is not None
        assert isinstance(result.suggested_actions, list)

    @patch("pikepdf.open")
    def test_pikepdf_error_handling(self, mock_pikepdf_open):
        """Test handling of pikepdf-specific errors."""
        mock_pikepdf_open.side_effect = pikepdf.PdfError("PDF is corrupted")

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"dummy pdf content")
            tmp_path = tmp.name

        try:
            result = crack_pdf_password(tmp_path, min_len=1, max_len=1, charset="a")
            # Should handle pikepdf errors gracefully
            assert isinstance(
                result, (PDFCorruptedError, FileReadError, InitializationError)
            )
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_suggested_actions_in_errors(self):
        """Test that error results include suggested actions."""
        # Test file not found
        result = crack_pdf_password(
            "non_existent_file.pdf", min_len=1, max_len=1, charset="a"
        )
        assert isinstance(result, FileReadError)
        assert len(result.suggested_actions) > 0
        assert any(
            "check the file path" in action.lower()
            for action in result.suggested_actions
        )

        # Test empty charset
        result = crack_pdf_password(
            "tests/test_pdfs/numbers/100.pdf", min_len=1, max_len=1, charset=""
        )
        assert isinstance(result, InitializationError)
        assert len(result.suggested_actions) > 0
        assert any("charset" in action.lower() for action in result.suggested_actions)

    def test_error_message_clarity(self):
        """Test that error messages are informative and clear."""
        # Test file not found
        result = crack_pdf_password(
            "non_existent_file.pdf", min_len=1, max_len=1, charset="a"
        )
        assert isinstance(result, FileReadError)
        assert "non_existent_file.pdf" in str(
            result.error_message
        ) or "non_existent_file.pdf" in str(result.file_path)

        # Test empty charset
        result = crack_pdf_password(
            "tests/test_pdfs/numbers/100.pdf", min_len=1, max_len=1, charset=""
        )
        assert isinstance(result, InitializationError)
        assert "empty" in result.error_message.lower()

    def test_worker_error_handling(self):
        """Test that worker processes handle errors gracefully."""
        # This test ensures worker errors don't crash the entire process
        result = crack_pdf_password(
            "tests/test_pdfs/numbers/100.pdf", min_len=1, max_len=1, charset="xyz"
        )
        assert isinstance(result, PasswordNotFound)
