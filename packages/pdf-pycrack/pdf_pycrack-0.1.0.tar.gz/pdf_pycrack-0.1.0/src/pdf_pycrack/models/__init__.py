"""Data models for PDF PyCrack."""

from .cracking_result import (
    CrackingInterrupted,
    CrackResult,
    FileReadError,
    InitializationError,
    NotEncrypted,
    PasswordFound,
    PasswordNotFound,
)

__all__ = [
    "CrackResult",
    "PasswordFound",
    "PasswordNotFound",
    "CrackingInterrupted",
    "NotEncrypted",
    "FileReadError",
    "InitializationError",
]
