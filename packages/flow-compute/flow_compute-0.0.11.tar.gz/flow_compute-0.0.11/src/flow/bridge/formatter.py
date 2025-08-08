"""Formatter bridge adapter for table rendering."""

import io
from typing import Any, Dict, List

from rich.console import Console
from rich.table import Table

from flow.cli.utils.task_formatter import TaskFormatter
from flow.cli.utils.task_renderer import TaskTableRenderer

from .base import BridgeAdapter


class FormatterBridge(BridgeAdapter):
    """Bridge adapter for Flow SDK's Rich-based formatting."""

    def __init__(self):
        """Initialize the formatter bridge."""
        self.task_formatter = TaskFormatter()
        # Create console that renders to string
        self._string_buffer = io.StringIO()
        self._console = Console(file=self._string_buffer, force_terminal=True, width=120)
        self.task_renderer = TaskTableRenderer(console=self._console)

    def get_capabilities(self) -> Dict[str, Any]:
        """Return capabilities of the formatter adapter."""
        return {
            "description": "Table formatting and rendering",
            "methods": {
                "format_table": {
                    "description": "Format data as a table (like mithril's formatTable)",
                    "args": {
                        "data": "List of row dictionaries",
                        "columns": "List of column names to display",
                    },
                    "returns": "Formatted table as string",
                },
                "format_status": {
                    "description": "Format status with color codes",
                    "args": {"status": "Status string"},
                    "returns": "ANSI color codes for terminal",
                },
                "get_status_color": {
                    "description": "Get color name for status",
                    "args": {"status": "Status string"},
                    "returns": "Color name (e.g., 'green', 'yellow')",
                },
            },
        }

    def format_table(self, data: List[Dict[str, Any]], columns: List[str]) -> str:
        """Format data as a table.

        Args:
            data: List of row dictionaries
            columns: List of column names to display

        Returns:
            Formatted table as string with ANSI codes
        """
        if not data:
            return "No results"

        # Clear buffer
        self._string_buffer.truncate(0)
        self._string_buffer.seek(0)

        # Create Rich table
        table = Table(box=None, show_header=True)

        # Add columns with styling based on mithril's format.js
        for col in columns:
            col_upper = col.upper()
            if col == "status":
                table.add_column(col_upper, style="bold")
            elif col == "type":
                table.add_column(col_upper, style="cyan")
            elif col == "ip":
                table.add_column(col_upper, style="yellow")
            elif col == "price":
                table.add_column(col_upper, style="yellow")
            else:
                table.add_column(col_upper)

        # Add rows
        for row in data:
            values = []
            for col in columns:
                value = str(row.get(col, "N/A"))

                # Apply semantic coloring like mithril
                if col == "status":
                    value = self._format_status_value(value)
                elif col == "available":
                    if value == "0":
                        value = f"[dim]{value}[/dim]"
                    elif int(value) > 10:
                        value = f"[green]{value}[/green]"
                elif col == "type":
                    if "a100" in value:
                        value = f"[magenta]{value}[/magenta]"
                    elif "h100" in value:
                        value = f"[blue]{value}[/blue]"
                elif col == "price":
                    value = f"[yellow]{value}[/yellow]"
                elif col == "ip":
                    if value == "N/A":
                        value = f"[dim]{value}[/dim]"
                    else:
                        value = f"[green]{value}[/green]"

                values.append(value)

            table.add_row(*values)

        # Render to string
        self._console.print(table)
        result = self._string_buffer.getvalue()

        # Clear buffer for next use
        self._string_buffer.truncate(0)
        self._string_buffer.seek(0)

        return result

    def format_status(self, status: str) -> str:
        """Format status with ANSI color codes.

        Args:
            status: Status string

        Returns:
            ANSI-formatted status string
        """
        return self._format_status_value(status)

    def get_status_color(self, status: str) -> str:
        """Get color name for status.

        Args:
            status: Status string

        Returns:
            Color name
        """
        status_upper = status.upper()

        if status_upper == "RUNNING":
            return "green"
        elif status_upper == "PENDING":
            return "yellow"
        elif status_upper == "TERMINATED":
            return "red"
        elif status_upper == "PROVISIONING":
            return "yellow"
        elif status_upper == "FAILED":
            return "red"
        else:
            return "white"

    def _format_status_value(self, status: str) -> str:
        """Format status value with Rich markup.

        Args:
            status: Status string

        Returns:
            Rich-formatted status
        """
        color = self.get_status_color(status)
        return f"[{color}]{status}[/{color}]"
