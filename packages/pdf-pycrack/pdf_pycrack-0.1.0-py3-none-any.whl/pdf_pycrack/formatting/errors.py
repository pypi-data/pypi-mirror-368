"""Error message formatting and display utilities.

This module provides functions for displaying error messages, warnings,
and informational messages in a consistent and user-friendly format
using the Rich library.
"""

from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel

console = Console()


def print_error(
    title: str,
    message: str,
    details: Optional[str] = None,
    suggested_actions: Optional[List[str]] = None,
) -> None:
    """Print an error message in a formatted panel with optional details and suggestions.

    Args:
        title: The error title/heading.
        message: The main error message.
        details: Optional additional details about the error.
        suggested_actions: Optional list of suggested actions to resolve the error.
    """

    # Create the main error content
    content_parts = [f"[white]{message}[/white]"]

    if details:
        content_parts.append(f"\n[dim]{details}[/dim]")

    if suggested_actions:
        content_parts.append("\n[bold yellow]Suggested actions:[/bold yellow]")
        for i, action in enumerate(suggested_actions, 1):
            content_parts.append(f"  [yellow]{i}.[/yellow] {action}")

    content = "\n".join(content_parts)

    panel = Panel(
        content,
        title=f"[bold red]{title}[/bold red]",
        border_style="red",
        padding=(1, 2),
    )
    console.print(panel)


def print_warning(
    title: str, message: str, suggested_actions: Optional[List[str]] = None
) -> None:
    """Print a warning message in a formatted panel.

    Args:
        title: The warning title/heading.
        message: The main warning message.
        suggested_actions: Optional list of suggested actions to address the warning.
    """

    content_parts = [f"[white]{message}[/white]"]

    if suggested_actions:
        content_parts.append("\n[bold yellow]Suggested actions:[/bold yellow]")
        for i, action in enumerate(suggested_actions, 1):
            content_parts.append(f"  [yellow]{i}.[/yellow] {action}")

    content = "\n".join(content_parts)

    panel = Panel(
        content,
        title=f"[bold orange3]{title}[/bold orange3]",
        border_style="orange3",
        padding=(1, 2),
    )
    console.print(panel)


def print_info(title: str, message: str) -> None:
    """Print an info message in a formatted panel.

    Args:
        title: The info title/heading.
        message: The main info message.
    """

    panel = Panel(
        f"[white]{message}[/white]",
        title=f"[bold blue]{title}[/bold blue]",
        border_style="blue",
        padding=(1, 2),
    )
    console.print(panel)


def format_error_context(
    error_type: str, file_path: str, exception: Exception
) -> Dict[str, Any]:
    """Format error context for different types of PDF errors.

    Args:
        error_type: The type of error encountered.
        file_path: Path to the file that caused the error.
        exception: The exception that was raised.

    Returns:
        Dict containing formatted error context with title, message, and suggested actions.
    """

    error_mapping = {
        "FileNotFoundError": {
            "title": "File Not Found",
            "message": f"The file '{file_path}' does not exist.",
            "suggested_actions": [
                "Check the file path and ensure it is correct",
                "Verify the file exists in the specified location",
                "Use absolute path if relative path is ambiguous",
            ],
        },
        "PermissionError": {
            "title": "Permission Denied",
            "message": f"Cannot read the file '{file_path}' due to permission restrictions.",
            "suggested_actions": [
                "Check file permissions with `ls -la` (Unix) or file properties (Windows)",
                "Ensure you have read access to the file",
                "Try running with appropriate user permissions",
            ],
        },
        "IsADirectoryError": {
            "title": "Path is a Directory",
            "message": f"The path '{file_path}' is a directory, not a file.",
            "suggested_actions": [
                "Specify the full path to the PDF file including filename",
                "Check if the file extension is .pdf",
            ],
        },
        "pikepdf.PdfError": {
            "title": "PDF Processing Error",
            "message": f"The PDF file '{file_path}' appears to be corrupted or malformed.",
            "suggested_actions": [
                "Try opening the PDF in a PDF reader to verify it's not corrupted",
                "Use a PDF repair tool to fix the file",
                "Re-download or re-create the PDF if possible",
            ],
        },
        "MemoryError": {
            "title": "Memory Error",
            "message": "Insufficient memory to process the PDF file.",
            "suggested_actions": [
                "Close other applications to free up memory",
                "Try processing a smaller PDF file",
                "Increase system RAM or use a machine with more memory",
            ],
        },
    }

    # Default fallback
    default_error = {
        "title": "PDF Error",
        "message": f"An error occurred while processing '{file_path}': {str(exception)}",
        "suggested_actions": [
            "Check if the file is a valid PDF",
            "Verify the file is not corrupted",
            "Try opening the file in a PDF reader",
        ],
    }

    return error_mapping.get(error_type, default_error)
