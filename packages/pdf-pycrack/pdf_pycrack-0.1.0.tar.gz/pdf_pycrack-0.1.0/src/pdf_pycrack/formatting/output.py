"""Console output formatting for PDF password cracking results.

This module provides functions for displaying start information,
end results, and progress updates in a formatted and visually
appealing manner using the Rich library.
"""

import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..models.cracking_result import (
    CrackingInterrupted,
    CrackResult,
    PasswordFound,
    PasswordNotFound,
)

console = Console()


def print_start_info(
    pdf_file: str,
    min_length: int,
    max_length: int,
    charset: str,
    batch_size: int,
    cores: int,
    start_time: float,
) -> None:
    """Print the starting information in a formatted panel.

    Args:
        pdf_file: Path to the PDF file being processed.
        min_length: Minimum password length to try.
        max_length: Maximum password length to try.
        charset: Character set used for password generation.
        batch_size: Number of passwords processed per batch.
        cores: Number of CPU cores being used.
        start_time: Unix timestamp when the process started.
    """

    grid = Table.grid(expand=True)
    grid.add_column(justify="left", style="bold")
    grid.add_column(justify="left")

    grid.add_row("PDF File:", f"[cyan]{pdf_file}[/cyan]")
    grid.add_row("Password Length:", f"[cyan]{min_length} to {max_length}[/cyan]")
    grid.add_row("Character Set:", f"[cyan]{charset}[/cyan]")
    grid.add_row("Batch Size:", f"[cyan]{batch_size}[/cyan]")
    grid.add_row("CPU Cores:", f"[cyan]{cores}[/cyan]")
    grid.add_row("Start Time:", f"[cyan]{time.ctime(start_time)}[/cyan]")

    panel = Panel(
        grid,
        title="[bold yellow]PDF PyCrack Initializing[/bold yellow]",
        border_style="green",
        padding=(1, 2),
    )
    console.print(panel)


def print_end_info(result: CrackResult) -> None:
    """Print the final result and duration in a formatted panel.

    Args:
        result: The cracking result containing status, timing, and other details.
    """

    duration = result.elapsed_time

    if isinstance(result, PasswordFound):
        end_message = Text.from_markup(
            f"Password found: [bold green]{repr(result.password)}[/bold green]"
        )
        panel_title = "[bold green]Cracking Successful[/bold green]"
        border_style = "green"
    elif isinstance(result, CrackingInterrupted):
        end_message = Text.from_markup("Cracking process interrupted by user.")
        panel_title = "[bold yellow]Cracking Interrupted[/bold yellow]"
        border_style = "yellow"
    else:  # PasswordNotFound
        end_message = Text.from_markup(
            "Password not found within the specified constraints."
        )
        panel_title = "[bold red]Cracking Failed[/bold red]"
        border_style = "red"

    grid = Table.grid(expand=True)
    grid.add_column(justify="left", style="bold")
    grid.add_column(justify="left")

    grid.add_row("Status:", end_message)
    grid.add_row("Duration:", f"[cyan]{duration:.2f} seconds[/cyan]")

    if isinstance(result, (PasswordFound, PasswordNotFound, CrackingInterrupted)):
        passwords_checked = result.passwords_checked
        if passwords_checked > 0:
            grid.add_row("Passwords Checked:", f"[cyan]{passwords_checked}[/cyan]")
            if isinstance(result, (PasswordFound, PasswordNotFound)):
                passwords_per_second = result.passwords_per_second
                grid.add_row(
                    "Passwords/Second:", f"[cyan]{passwords_per_second:.2f}[/cyan]"
                )

    panel = Panel(grid, title=panel_title, border_style=border_style, padding=(1, 2))
    console.print(panel)
