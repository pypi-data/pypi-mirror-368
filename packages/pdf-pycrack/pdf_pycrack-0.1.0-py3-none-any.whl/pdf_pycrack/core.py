"""Core PDF password cracking functionality.

This module provides the main crack_pdf_password function that orchestrates
the PDF password cracking process using multiprocessing.
"""

import multiprocessing
import time
from typing import Optional

import pikepdf

from .formatting.errors import format_error_context, print_error
from .models.cracking_result import (
    CrackResult,
    FileReadError,
    InitializationError,
    NotEncrypted,
    PDFCorruptedError,
)
from .supervisor import manage_workers
from .validator import validate_pdf


def crack_pdf_password(
    pdf_path: str,
    min_len: int = 4,
    max_len: int = 5,
    charset: str = "0123456789",
    num_processes: Optional[int] = None,
    batch_size_arg: int = 5000,
    report_worker_errors_arg: bool = True,
) -> CrackResult:
    """
    Crack a PDF password using multiple processes.

    Args:
        pdf_path: The path to the PDF file.
        min_len: Minimum password length.
        max_len: Maximum password length.
        charset: Character set for passwords.
        num_processes: Number of CPU cores to use (default: all available).
        batch_size_arg: Password batch size for workers.
        report_worker_errors_arg: Whether to report worker errors.

    Returns:
        A dataclass with the cracking result.
    """
    start_time = time.time()

    # Set default for num_processes if not provided
    if num_processes is None:
        num_processes = multiprocessing.cpu_count()

    # Validate input parameters
    if not charset:
        return InitializationError(
            error_message="Charset cannot be empty.",
            elapsed_time=time.time() - start_time,
            error_type="EmptyCharset",
            suggested_actions=[
                "Provide a non-empty charset for password generation",
                "Check the charset parameter and ensure it contains at least one character",
            ],
        )

    # Validate PDF file
    try:
        if not validate_pdf(pdf_path):
            return NotEncrypted(elapsed_time=time.time() - start_time)
    except FileNotFoundError as e:
        error_context = format_error_context("FileNotFoundError", pdf_path, e)
        print_error(**error_context)
        return FileReadError(
            error_message=str(e),
            file_path=pdf_path,
            error_type="FileNotFoundError",
            suggested_actions=error_context.get("suggested_actions", []),
            elapsed_time=time.time() - start_time,
        )
    except PermissionError as e:
        error_context = format_error_context("PermissionError", pdf_path, e)
        print_error(**error_context)
        return FileReadError(
            error_message=str(e),
            file_path=pdf_path,
            error_type="PermissionError",
            suggested_actions=error_context.get("suggested_actions", []),
            elapsed_time=time.time() - start_time,
        )
    except IsADirectoryError as e:
        error_context = format_error_context("IsADirectoryError", pdf_path, e)
        print_error(**error_context)
        return FileReadError(
            error_message=str(e),
            file_path=pdf_path,
            error_type="IsADirectoryError",
            suggested_actions=error_context.get("suggested_actions", []),
            elapsed_time=time.time() - start_time,
        )
    except pikepdf.PdfError as e:
        error_context = format_error_context("pikepdf.PdfError", pdf_path, e)
        print_error(**error_context)
        return PDFCorruptedError(
            error_message=str(e),
            file_path=pdf_path,
            corruption_type="pdf_error",
            suggested_actions=error_context.get("suggested_actions", []),
            elapsed_time=time.time() - start_time,
        )
    except MemoryError as e:
        error_context = format_error_context("MemoryError", pdf_path, e)
        print_error(**error_context)
        return InitializationError(
            error_message=str(e),
            error_type="MemoryError",
            suggested_actions=error_context.get("suggested_actions", []),
            elapsed_time=time.time() - start_time,
        )
    except Exception as e:
        error_context = format_error_context("Exception", pdf_path, e)
        print_error(**error_context)
        return InitializationError(
            error_message=str(e),
            error_type="Unknown",
            suggested_actions=error_context.get("suggested_actions", []),
            elapsed_time=time.time() - start_time,
        )

    # Use supervisor to manage the cracking process
    return manage_workers(
        pdf_path=pdf_path,
        min_len=min_len,
        max_len=max_len,
        charset=charset,
        num_processes=num_processes,
        batch_size=batch_size_arg,
        report_worker_errors=report_worker_errors_arg,
    )
