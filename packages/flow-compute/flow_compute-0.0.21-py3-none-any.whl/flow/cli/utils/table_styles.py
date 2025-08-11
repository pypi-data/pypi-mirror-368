"""Shared table styling utilities for consistent CLI output.

Provides helpers to create tables and panels with Flow's default styles.
"""

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from flow.cli.utils.theme_manager import theme_manager


def create_flow_table(
    title: str | None = None,
    show_borders: bool = True,
    padding: int = 1,
    *,
    expand: bool = False,
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
        expand=expand,  # Do not expand by default; most tables render better compact
    )

    return table


def wrap_table_in_panel(table: Table, title: str, console: Console) -> None:
    """Wrap table in a panel with centered title, matching flow status style.

    Args:
        table: The table to wrap
        title: Panel title
        console: Rich console for output
    """
    accent = theme_manager.get_color("accent")
    border = theme_manager.get_color("table.border")
    panel = Panel(
        table,
        title=f"[bold {accent}]{title}[/bold {accent}]",
        title_align="center",
        border_style=border,
        padding=(1, 2),  # Match wizard panel padding
        expand=False,  # Don't expand panel beyond table content
    )
    console.print(panel)


def add_centered_column(
    table: Table,
    name: str,
    style: str | None = None,
    width: int | None = None,
    min_width: int | None = None,
    max_width: int | None = None,
    ratio: float | None = None,
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
