"""Tests for the worker module."""

import queue
import threading
from unittest.mock import MagicMock, patch

import pikepdf
import pytest

from pdf_pycrack.worker import worker_process


@pytest.fixture
def mock_pdf_data():
    """Create mock PDF data."""
    return b"mock_pdf_data"


@pytest.fixture
def mock_password_queue():
    """Create a mock password queue."""
    return queue.Queue()


@pytest.fixture
def mock_found_event():
    """Create a mock found event."""
    event = MagicMock()
    event.is_set.return_value = False
    return event


@pytest.fixture
def mock_result_queue():
    """Create a mock result queue."""
    return queue.Queue()


@pytest.fixture
def mock_progress_queue():
    """Create a mock progress queue."""
    return queue.Queue()


def test_worker_process_empty_queue(
    mock_pdf_data,
    mock_password_queue,
    mock_found_event,
    mock_result_queue,
    mock_progress_queue,
):
    """Test worker_process with an empty queue."""
    # Put None in the queue to signal end
    mock_password_queue.put(None)

    # Call the worker process
    worker_process(
        pdf_data=mock_pdf_data,
        password_queue=mock_password_queue,
        found_event=mock_found_event,
        result_queue=mock_result_queue,
        progress_queue=mock_progress_queue,
        report_worker_errors=False,
        batch_size=10,
    )

    # Check that the worker finished without errors
    assert mock_progress_queue.empty()


def test_worker_process_timeout_handling(
    mock_pdf_data,
    mock_password_queue,
    mock_found_event,
    mock_result_queue,
    mock_progress_queue,
):
    """Test worker_process handling of queue timeout."""
    # Don't put anything in the queue, so it will timeout

    # We'll run the worker in a separate thread and stop it after a short time
    mock_found_event.is_set.return_value = True  # Signal to stop immediately

    worker_process(
        pdf_data=mock_pdf_data,
        password_queue=mock_password_queue,
        found_event=mock_found_event,
        result_queue=mock_result_queue,
        progress_queue=mock_progress_queue,
        report_worker_errors=False,
        batch_size=10,
    )

    # Check that the worker finished without errors
    assert mock_progress_queue.empty()


@patch("pikepdf.open")
def test_worker_process_pdf_error(
    mock_pikepdf_open,
    mock_pdf_data,
    mock_password_queue,
    mock_found_event,
    mock_result_queue,
    mock_progress_queue,
):
    """Test worker_process handling of PdfError."""
    # Set up the mock to raise PdfError
    mock_pikepdf_open.side_effect = pikepdf.PdfError("Test PDF error")

    # Add a password to the queue
    mock_password_queue.put("wrong_password")
    mock_password_queue.put(None)  # Signal end

    # Call the worker process
    worker_process(
        pdf_data=mock_pdf_data,
        password_queue=mock_password_queue,
        found_event=mock_found_event,
        result_queue=mock_result_queue,
        progress_queue=mock_progress_queue,
        report_worker_errors=True,
        batch_size=10,
    )

    # Check that progress was reported
    assert not mock_progress_queue.empty()
    progress = mock_progress_queue.get()
    assert progress == 1  # One password was tried


@patch("pikepdf.open")
def test_worker_process_generic_exception(
    mock_pikepdf_open,
    mock_pdf_data,
    mock_password_queue,
    mock_found_event,
    mock_result_queue,
    mock_progress_queue,
):
    """Test worker_process handling of generic exceptions."""
    # Set up the mock to raise a generic exception
    mock_pikepdf_open.side_effect = Exception("Test generic error")

    # Add a password to the queue
    mock_password_queue.put("wrong_password")
    mock_password_queue.put(None)  # Signal end

    # Call the worker process
    worker_process(
        pdf_data=mock_pdf_data,
        password_queue=mock_password_queue,
        found_event=mock_found_event,
        result_queue=mock_result_queue,
        progress_queue=mock_progress_queue,
        report_worker_errors=True,
        batch_size=10,
    )

    # Check that progress was reported
    assert not mock_progress_queue.empty()
    progress = mock_progress_queue.get()
    assert progress == 1  # One password was tried


def test_worker_process_password_found(
    mock_pdf_data,
    mock_password_queue,
    mock_found_event,
    mock_result_queue,
    mock_progress_queue,
):
    """Test worker_process when password is found."""
    # Add the correct password to the queue
    mock_password_queue.put("correct_password")
    mock_password_queue.put(None)  # Signal end

    # Create a real threading event for more realistic testing
    found_event = threading.Event()

    with patch("pikepdf.open") as mock_pikepdf_open:
        # Make the context manager work correctly
        mock_pdf_context = MagicMock()
        mock_pikepdf_open.return_value.__enter__.return_value = mock_pdf_context

        # Call the worker process in a separate thread so we can control the event
        worker_thread = threading.Thread(
            target=worker_process,
            kwargs={
                "pdf_data": mock_pdf_data,
                "password_queue": mock_password_queue,
                "found_event": found_event,
                "result_queue": mock_result_queue,
                "progress_queue": mock_progress_queue,
                "report_worker_errors": False,
                "batch_size": 10,
            },
        )

        worker_thread.start()

        # Wait a bit for the worker to process the password
        worker_thread.join(timeout=1.0)

        # Check that the password was found and put in the result queue
        assert not mock_result_queue.empty()
        found_password = mock_result_queue.get()
        assert found_password == "correct_password"

        # Check that the found event was set
        assert found_event.is_set()
