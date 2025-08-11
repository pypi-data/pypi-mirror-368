"""PDF validation utilities for determining encryption status.

This module provides functions to validate PDF files and check
whether they are encrypted and require password cracking.
"""

import pikepdf


def validate_pdf(pdf_path: str) -> bool:
    """
    Checks if the PDF is encrypted and ready for cracking.

    Args:
        pdf_path: The path to the PDF file.

    Returns:
        True if the PDF is encrypted, False otherwise.
    """
    try:
        with pikepdf.open(pdf_path):
            return False  # PDF is not encrypted
    except pikepdf.PasswordError:
        return True  # PDF is encrypted
    except pikepdf.PdfError as e:
        raise pikepdf.PdfError(f"PDF file appears to be corrupted: {e}")
    except (FileNotFoundError, PermissionError, IsADirectoryError, OSError) as e:
        raise e  # Re-raise to be caught by the caller
    except RuntimeError as e:
        if "Is a directory" in str(e):
            raise IsADirectoryError(str(e))
        else:
            raise
    except Exception as e:
        raise RuntimeError(
            f"Error during initial check with pikepdf on '{pdf_path}': {e}"
        )
