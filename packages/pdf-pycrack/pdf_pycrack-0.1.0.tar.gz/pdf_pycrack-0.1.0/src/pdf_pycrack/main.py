"""Main entry point for the PDF password cracking application.

This module provides the main function that handles command-line arguments,
executes the password cracking process, and displays results.
"""

import multiprocessing
import sys
import time

from .cli import setup_arg_parser
from .core import crack_pdf_password
from .formatting.errors import print_error, print_warning
from .formatting.output import print_end_info, print_start_info
from .models.cracking_result import CrackingInterrupted, CrackResult, PasswordNotFound


def main() -> None:
    """Main entry point for the PDF password cracking application.

    Parses command-line arguments, sets up the character set for password
    generation, and initiates the PDF password cracking process. Handles
    user interruptions and displays appropriate results.

    Raises:
        SystemExit: When invalid password length parameters are provided.
    """
    parser = setup_arg_parser()
    args = parser.parse_args()

    # Construct character set
    charset: str = args.charset_custom
    if args.charset_numbers:
        charset += "0123456789"
    if args.charset_letters:
        charset += "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if args.charset_special:
        charset += "!@#$%^&*() "

    # Default to numbers if no charset is specified
    if not charset:
        charset = "0123456789"
        print("No charset specified, defaulting to numbers (0-9).")

    # Remove duplicates and sort for consistency
    charset = "".join(sorted(list(set(charset))))

    pdf_document_path: str = args.file
    requested_cores: int = args.cores
    min_pw_len: int = args.min_len
    max_pw_len: int = args.max_len

    # Validate and limit cores to available CPU cores
    max_cores = multiprocessing.cpu_count()
    if requested_cores > max_cores:
        print_warning(
            title="Core Count Warning",
            message=f"Requested {requested_cores} cores, but only {max_cores} cores are available.\n"
            f"The application will automatically use {max_cores} cores instead.",
            suggested_actions=[
                f"Use --cores {max_cores} or fewer to avoid this warning",
                "Check available cores with: nproc (Linux) or sysctl -n hw.ncpu (macOS)",
            ],
        )
        num_cores_to_use = max_cores
    else:
        num_cores_to_use = requested_cores

    if min_pw_len <= 0 or max_pw_len <= 0 or min_pw_len > max_pw_len:
        print_error(
            title="Invalid Password Length Configuration",
            message="The password length parameters provided are invalid.",
            details=f"Minimum length: {min_pw_len}, Maximum length: {max_pw_len}",
            suggested_actions=[
                "Ensure both minimum and maximum lengths are positive numbers",
                "Ensure minimum length is less than or equal to maximum length",
                "Example: --min_len 4 --max_len 8",
            ],
        )
        sys.exit(1)

    start_time: float = time.time()
    print_start_info(
        pdf_document_path,
        min_pw_len,
        max_pw_len,
        charset,
        args.batch_size,
        num_cores_to_use,
        start_time,
    )

    try:
        result: CrackResult = crack_pdf_password(
            pdf_document_path,
            min_len=min_pw_len,
            max_len=max_pw_len,
            charset=charset,
            num_processes=num_cores_to_use,
            batch_size_arg=args.batch_size,
            report_worker_errors_arg=args.worker_errors,
        )
    except KeyboardInterrupt:
        result = CrackingInterrupted(
            passwords_checked=0,  # This will be unknown
            elapsed_time=time.time() - start_time,
        )

    if result:
        # Only print end info if cracking started
        # All concrete CrackResult implementations have a status field
        if getattr(result, "status", "") != "not_encrypted":
            print_end_info(result)
    else:
        # Fallback for unexpected cases where result is None (e.g. file not found)
        end_time: float = time.time()
        print_end_info(
            PasswordNotFound(
                elapsed_time=end_time - start_time,
                passwords_checked=0,
                passwords_per_second=0,
            )
        )


if __name__ == "__main__":
    main()
