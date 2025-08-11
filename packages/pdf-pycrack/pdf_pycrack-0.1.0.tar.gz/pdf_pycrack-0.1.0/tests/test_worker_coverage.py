"""Additional tests for worker module to improve coverage."""

import queue
import threading
from unittest.mock import MagicMock, patch

import pytest

from pdf_pycrack.worker import worker_process


@pytest.fixture
def mock_pdf_data():
    """Create mock PDF data."""
    return b"mock_pdf_data"


def test_worker_process_finally_block_with_passwords():
    """Test worker_process finally block when there are passwords to report."""
    # Create queues
    password_queue = queue.Queue()
    result_queue = queue.Queue()
    progress_queue = queue.Queue()

    # Add one password to the queue
    password_queue.put("test_password")
    # Add None to signal end
    password_queue.put(None)

    # Create a mock found event that will be set to exit the loop
    found_event = MagicMock()
    found_event.is_set.return_value = False

    with patch("pikepdf.open") as mock_pikepdf_open:
        # Make the context manager work correctly
        mock_pdf_context = MagicMock()
        mock_pikepdf_open.return_value.__enter__.return_value = mock_pdf_context

        # Create a threading event for more realistic testing
        threading_event = threading.Event()

        # Call the worker process in a separate thread
        worker_thread = threading.Thread(
            target=worker_process,
            kwargs={
                "pdf_data": b"mock_pdf_data",
                "password_queue": password_queue,
                "found_event": threading_event,
                "result_queue": result_queue,
                "progress_queue": progress_queue,
                "report_worker_errors": False,
                "batch_size": 10,
            },
        )

        worker_thread.start()

        # Wait a bit for the worker to process
        worker_thread.join(timeout=1.0)

        # Check that progress was reported
        assert not progress_queue.empty()
        progress = progress_queue.get()
        # We added one password, so progress should be 1
        assert progress == 1


def test_worker_process_continue_when_no_passwords():
    """Test worker_process continue statement when no passwords are available."""
    # Create queues
    password_queue = queue.Queue()
    result_queue = queue.Queue()
    progress_queue = queue.Queue()

    # Create a mock found event
    found_event = MagicMock()
    # First call returns False, second call returns True to exit loop
    found_event.is_set.side_effect = [False, True]

    with patch("pikepdf.open") as mock_pikepdf_open:
        # Make the context manager work correctly
        mock_pdf_context = MagicMock()
        mock_pikepdf_open.return_value.__enter__.return_value = mock_pdf_context

        # Call the worker process
        worker_process(
            pdf_data=b"mock_pdf_data",
            password_queue=password_queue,
            found_event=found_event,
            result_queue=result_queue,
            progress_queue=progress_queue,
            report_worker_errors=False,
            batch_size=10,
        )

        # Check that no progress was reported
        assert progress_queue.empty()
