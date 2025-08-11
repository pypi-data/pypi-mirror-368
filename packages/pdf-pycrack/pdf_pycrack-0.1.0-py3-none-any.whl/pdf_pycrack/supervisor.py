"""Worker process management and coordination for PDF password cracking.

This module contains the supervisor function that manages multiple worker processes
and coordinates the password cracking workflow with progress tracking.
"""

import multiprocessing
import queue
import time

from tqdm import tqdm

from .models.cracking_result import (
    CrackingInterrupted,
    FileReadError,
    PasswordFound,
    PasswordNotFound,
)
from .password_generator import generate_passwords
from .worker import worker_process


def manage_workers(
    pdf_path: str,
    min_len: int,
    max_len: int,
    charset: str,
    num_processes: int,
    batch_size: int,
    report_worker_errors: bool,
) -> PasswordFound | PasswordNotFound | CrackingInterrupted | FileReadError:
    """
    Manages worker processes for password cracking.

    Args:
        pdf_path: Path to the PDF file.
        min_len: Minimum password length.
        max_len: Maximum password length.
        charset: Character set for passwords.
        num_processes: Number of CPU cores to use.
        batch_size: Password batch size for workers.
        report_worker_errors: Whether to report worker errors.

    Returns:
        The result of the cracking process.
    """
    start_time = time.time()
    total_passwords_to_check = sum(
        len(charset) ** length for length in range(min_len, max_len + 1)
    )

    try:
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()
    except (IOError, MemoryError) as e:
        return FileReadError(
            error_message=str(e),
            file_path=pdf_path,
            error_type=type(e).__name__,
            suggested_actions=[
                "Check file permissions",
                "Ensure file exists at the specified path",
                "Verify sufficient memory is available",
            ],
            elapsed_time=time.time() - start_time,
        )

    manager = multiprocessing.Manager()
    found_event = manager.Event()
    result_queue = manager.Queue()
    password_queue = manager.Queue(maxsize=num_processes * 2)
    progress_queue = manager.Queue()
    stop_generating_event = manager.Event()

    pbar = tqdm(total=total_passwords_to_check, desc="Cracking PDF", unit="pw")

    # Create and start generator process
    generator_process = multiprocessing.Process(
        target=_generator_process,
        args=(
            password_queue,
            min_len,
            max_len,
            charset,
            stop_generating_event,
            num_processes,
        ),
    )
    generator_process.start()

    # Create and start worker processes
    processes = []
    for _ in range(num_processes):
        p = multiprocessing.Process(
            target=worker_process,
            args=(
                pdf_data,
                password_queue,
                found_event,
                result_queue,
                progress_queue,
                report_worker_errors,
                batch_size,
            ),
        )
        processes.append(p)
        p.start()

    # Main processing loop
    found_password = None
    interrupted = False
    passwords_processed = 0

    try:
        while (
            passwords_processed < total_passwords_to_check and not found_event.is_set()
        ):
            try:
                progress = progress_queue.get(timeout=0.1)
                pbar.update(progress)
                passwords_processed += progress
            except queue.Empty:
                # Check if the generator is done and the queue is empty
                if (
                    not generator_process.is_alive()
                    and password_queue.empty()
                    and not any(p.is_alive() for p in processes)
                ):
                    break
                continue

            if not result_queue.empty():
                found_password = result_queue.get_nowait()
                if found_password:
                    found_event.set()
                    stop_generating_event.set()

    except KeyboardInterrupt:
        interrupted = True
        print("\nCracking interrupted by user.")
        stop_generating_event.set()

    # Wait for all worker processes to finish
    for p in processes:
        p.join()

    generator_process.join()

    # Final progress update
    while not progress_queue.empty():
        passwords_processed += progress_queue.get_nowait()
    pbar.update(total_passwords_to_check - pbar.n)

    # Collect the final result if found
    if not found_password:
        while not result_queue.empty():
            found_password = result_queue.get_nowait()

    pbar.close()

    end_time = time.time()
    elapsed_time = end_time - start_time
    passwords_per_second = passwords_processed / elapsed_time if elapsed_time > 0 else 0

    if interrupted:
        return CrackingInterrupted(
            passwords_checked=passwords_processed,
            elapsed_time=elapsed_time,
        )

    if found_password:
        return PasswordFound(
            password=found_password,
            passwords_checked=passwords_processed,
            elapsed_time=elapsed_time,
            passwords_per_second=passwords_per_second,
        )

    return PasswordNotFound(
        passwords_checked=passwords_processed,
        elapsed_time=elapsed_time,
        passwords_per_second=passwords_per_second,
    )


def _generator_process(
    password_queue,
    min_len: int,
    max_len: int,
    charset: str,
    stop_generating_event,
    num_processes: int,
) -> None:
    """
    A separate process to generate and queue passwords.

    Args:
        password_queue: Queue to put passwords into.
        min_len: Minimum password length.
        max_len: Maximum password length.
        charset: Character set for passwords.
        stop_generating_event: Event to signal when to stop.
        num_processes: Number of worker processes.
    """
    password_generator = generate_passwords(min_len, max_len, charset)

    while not stop_generating_event.is_set():
        try:
            password = next(password_generator)
            password_queue.put(password)
        except StopIteration:
            break

    # Signal workers to exit
    for _ in range(num_processes):
        password_queue.put(None)
