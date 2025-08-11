"""Data models and result types for PDF password cracking operations.

This module defines dataclasses that represent different outcomes
of the PDF password cracking process, including success, failure,
and error conditions.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CrackResult:
    """Base class for all PDF password cracking results.

    Attributes:
        elapsed_time: Total time taken for the cracking process in seconds.
    """

    elapsed_time: float


@dataclass
class PasswordFound(CrackResult):
    """Result when the password is successfully found.

    Attributes:
        password: The discovered password string.
        passwords_checked: Number of passwords tested before finding the correct one.
        passwords_per_second: Rate of password testing achieved.
        status: Fixed status string indicating successful password discovery.
    """

    password: str
    passwords_checked: int
    passwords_per_second: float
    status: str = field(default="found", init=False)


@dataclass
class PasswordNotFound(CrackResult):
    """Result when the password is not found within the given constraints.

    Attributes:
        passwords_checked: Total number of passwords tested.
        passwords_per_second: Rate of password testing achieved.
        status: Fixed status string indicating password was not found.
    """

    passwords_checked: int
    passwords_per_second: float
    status: str = field(default="not_found", init=False)


@dataclass
class CrackingInterrupted(CrackResult):
    """Result when the cracking process is interrupted by user input.

    Attributes:
        passwords_checked: Number of passwords tested before interruption.
        status: Fixed status string indicating process was interrupted.
    """

    passwords_checked: int
    status: str = field(default="interrupted", init=False)


@dataclass
class NotEncrypted(CrackResult):
    """Result when the PDF is not encrypted."""

    status: str = field(default="not_encrypted", init=False)


@dataclass
class FileReadError(CrackResult):
    """Result when the PDF file cannot be read."""

    error_message: str
    file_path: Optional[str] = None
    error_type: Optional[str] = None
    suggested_actions: List[str] = field(default_factory=list)
    status: str = field(default="file_read_error", init=False)


@dataclass
class InitializationError(CrackResult):
    """Result for initialization errors."""

    error_message: str
    error_type: Optional[str] = None
    suggested_actions: List[str] = field(default_factory=list)
    status: str = field(default="initialization_error", init=False)


@dataclass
class PDFCorruptedError(CrackResult):
    """Result when the PDF file is corrupted or malformed."""

    error_message: str
    file_path: Optional[str] = None
    corruption_type: Optional[str] = None
    suggested_actions: List[str] = field(default_factory=list)
    status: str = field(default="pdf_corrupted", init=False)


@dataclass
class PDFUnsupportedError(CrackResult):
    """Result when the PDF uses unsupported encryption or features."""

    error_message: str
    encryption_type: Optional[str] = None
    pdf_version: Optional[str] = None
    suggested_actions: List[str] = field(default_factory=list)
    status: str = field(default="pdf_unsupported", init=False)
