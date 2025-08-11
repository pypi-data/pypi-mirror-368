"""Worker process implementation for PDF password cracking.

This module contains the worker process function that attempts to crack
PDF passwords by trying different password combinations.
"""

import queue
from io import BytesIO

import pikepdf

from .formatting.errors import print_error


def worker_process(
    pdf_data: bytes,
    password_queue,
    found_event,
    result_queue,
    progress_queue,
    report_worker_errors: bool,
    batch_size: int,
) -> None:
    """
    Worker process for cracking PDF passwords.

    Args:
        pdf_data: The in-memory PDF file data.
        password_queue: Queue to get passwords from.
        found_event: Event to signal when a password is found.
        result_queue: Queue to put the found password in.
        progress_queue: Queue to report progress.
        report_worker_errors: Whether to report worker errors.
        batch_size: The number of passwords to process in a batch.
    """
    passwords = []
    try:
        while not found_event.is_set():
            # Fill the batch
            while len(passwords) < batch_size:
                try:
                    password = password_queue.get(timeout=1.0)
                    if password is None:  # End of queue
                        if not passwords:
                            return
                        break
                    passwords.append(password)
                except queue.Empty:
                    if not passwords:
                        return
                    break

            if not passwords:
                continue

            tried_count = 0
            for password in passwords:
                if found_event.is_set():
                    break
                tried_count += 1
                try:
                    with pikepdf.open(BytesIO(pdf_data), password=password):
                        if not found_event.is_set():
                            found_event.set()
                            result_queue.put(password)
                        break
                except pikepdf.PasswordError:
                    continue
                except pikepdf.PdfError as e:
                    if report_worker_errors:
                        print_error(
                            "PDF Processing Error",
                            f"Error processing PDF with password '{password}': {e}",
                            details="This might indicate PDF corruption or format issues",
                        )
                    continue
                except Exception as e:
                    if report_worker_errors:
                        print_error(
                            "Worker Error",
                            f"Unexpected error during PDF processing: {e}",
                            details="Consider reporting this issue with the PDF file details",
                        )

            progress_queue.put(tried_count)
            passwords = []

    except KeyboardInterrupt:
        pass
    finally:
        if passwords:
            progress_queue.put(len(passwords))
