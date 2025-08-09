"""Shared table styling utilities for consistent CLI output.

Following DRY principles, this module provides reusable table creation
functions that maintain consistent styling across all Flow CLI commands.
"""

from typing import Optional
from rich import box
from rich.table import Table
from rich.panel import Panel
from rich.console import Console

from .theme_manager import theme_manager


def create_flow_table(
    title: Optional[str] = None, show_borders: bool = True, padding: int = 1
) -> Table:
    """Create a table with Flow's standard styling.

    Args:
        title: Optional table title
        show_borders: Whether to show table borders
        padding: Column padding (0-2)

    Returns:
        Configured Rich Table instance with Flow styling
    """
    # Use rounded box style like task tables
    box_style = box.ROUNDED if show_borders else None

    table = Table(
        title=title,
        box=box_style,
        header_style="bold",
        border_style=(
            theme_manager.get_color("table.border")
            if show_borders
            else theme_manager.get_color("muted")
        ),
        title_style=f"bold {theme_manager.get_color('accent')}" if title else None,
        show_lines=False,  # Clean look without horizontal lines
        padding=(0, padding),
        collapse_padding=True,
        expand=True,  # Allow table to expand to fill available space
    )

    return table


def wrap_table_in_panel(table: Table, title: str, console: Console) -> None:
    """Wrap table in a panel with centered title, matching flow status style.

    Args:
        table: The table to wrap
        title: Panel title
        console: Rich console for output
    """
    panel = Panel(
        table,
        title=f"[bold cyan]{title}[/bold cyan]",
        title_align="center",
        border_style="cyan",
        padding=(1, 2),  # Match wizard panel padding
        expand=False,  # Don't expand panel beyond table content
    )
    console.print(panel)


def add_centered_column(
    table: Table,
    name: str,
    style: Optional[str] = None,
    width: Optional[int] = None,
    min_width: Optional[int] = None,
    max_width: Optional[int] = None,
    ratio: Optional[float] = None,
    overflow: str = "fold",
) -> None:
    """Add a column with centered alignment and consistent header style.

    Args:
        table: Table to add column to
        name: Column name
        style: Optional column style
        width: Optional fixed column width
        min_width: Optional minimum column width
        max_width: Optional maximum column width
        ratio: Optional width ratio for proportional sizing
        overflow: How to handle overflow text (fold, crop, ellipsis)
    """
    table.add_column(
        name,
        style=style or theme_manager.get_color("default"),
        width=width,
        min_width=min_width,
        max_width=max_width,
        ratio=ratio,
        header_style=theme_manager.get_color("table.header"),
        justify="center",
        overflow=overflow,
    )
