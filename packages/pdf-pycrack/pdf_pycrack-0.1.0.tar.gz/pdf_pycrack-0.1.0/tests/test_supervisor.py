"""Tests for the supervisor module."""

from unittest.mock import patch

import pytest

from pdf_pycrack.models.cracking_result import FileReadError
from pdf_pycrack.supervisor import manage_workers


@pytest.fixture
def mock_pdf_data():
    """Create mock PDF data."""
    return b"mock_pdf_data"


@patch("pdf_pycrack.supervisor.open")
def test_manage_workers_file_read_error(mock_open, mock_pdf_data):
    """Test manage_workers when there's a file read error."""
    # Set up the mock to raise an IOError
    mock_open.side_effect = IOError("File not found")

    # Call manage_workers
    result = manage_workers(
        pdf_path="nonexistent.pdf",
        min_len=1,
        max_len=4,
        charset="0123456789",
        num_processes=1,
        batch_size=10,
        report_worker_errors=False,
    )

    # Check that we got a FileReadError result
    assert isinstance(result, FileReadError)
    assert result.error_message == "File not found"
    assert result.file_path == "nonexistent.pdf"
    # In Python 3, IOError is an alias for OSError
    assert result.error_type in ("IOError", "OSError")
