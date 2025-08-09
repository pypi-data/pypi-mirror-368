"""Simplified live dashboard for real-time task monitoring."""

import sys
import time
from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich import box

from flow import Flow
from flow.api.models import TaskStatus
from .task_presenter import TaskPresenter, DisplayOptions
from .theme_manager import theme_manager


class SimpleLiveDashboard:
    """Simplified interactive live monitoring dashboard for Flow tasks."""

    def __init__(
        self, flow_client: Flow, refresh_rate: float = 2.0, console: Optional[Console] = None
    ):
        """Initialize live dashboard.

        Args:
            flow_client: Flow client instance
            refresh_rate: Refresh interval in seconds
            console: Console instance (optional)
        """
        self.flow_client = flow_client
        self.refresh_rate = refresh_rate
        self.console = console or theme_manager.create_console()
        self.task_presenter = TaskPresenter(self.console, flow_client)
        self.last_update = datetime.now()
        self.tasks = []

    def fetch_tasks(self):
        """Fetch current tasks."""
        try:
            display_options = DisplayOptions(show_all=False, status_filter=None, limit=20)
            self.tasks = self.task_presenter._fetch_tasks(display_options)
            self.last_update = datetime.now()
        except Exception:
            # Keep existing tasks on error
            pass

    def create_display(self) -> Panel:
        """Create the display panel."""
        # Create main table
        table = Table(
            title=f"Flow Task Monitor - {len(self.tasks)} tasks",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan",
        )

        # Add columns
        table.add_column("Task ID", style="dim", width=12)
        table.add_column("Name", style="cyan", width=20)
        table.add_column("Status", justify="center", width=12)
        table.add_column("GPU", style="green", width=15)
        table.add_column("Created", style="blue", width=12)

        # Add rows
        for task in self.tasks[:20]:  # Limit display
            status_color = {
                TaskStatus.PENDING: "yellow",
                TaskStatus.RUNNING: "green",
                TaskStatus.COMPLETED: "blue",
                TaskStatus.FAILED: "red",
                TaskStatus.CANCELLED: "dim",
            }.get(task.status, "white")

            from .gpu_formatter import GPUFormatter

            gpu_display = (
                GPUFormatter.format_ultra_compact(
                    task.instance_type, getattr(task, "num_instances", 1)
                )
                if task.instance_type
                else "-"
            )
            table.add_row(
                task.task_id[:8] + "...",
                task.name or "-",
                f"[{status_color}]{task.status.value}[/{status_color}]",
                gpu_display,
                task.created_at.strftime("%H:%M:%S") if task.created_at else "-",
            )

        # Add footer info
        footer = f"Last updated: {self.last_update.strftime('%H:%M:%S')} | Press Ctrl+C to exit"

        return Panel(
            table, title="[bold]Flow Status Monitor[/bold]", subtitle=footer, border_style="cyan"
        )

    def run(self):
        """Run the live dashboard."""
        # Check if running in a TTY
        if not sys.stdin.isatty():
            self.console.print("[red]Error:[/red] Live mode requires an interactive terminal")
            return

        self.console.print("[cyan]Starting live dashboard...[/cyan]")
        self.console.print("Press [bold]Ctrl+C[/bold] to exit\n")

        # Initial fetch
        self.fetch_tasks()

        try:
            with Live(
                self.create_display(),
                console=self.console,
                refresh_per_second=2,
                screen=False,  # Don't clear screen, just update in place
            ) as live:
                while True:
                    # Update data
                    self.fetch_tasks()

                    # Update display
                    live.update(self.create_display())

                    # Wait before next update
                    time.sleep(self.refresh_rate)

        except KeyboardInterrupt:
            self.console.print("\n[green]Dashboard stopped.[/green]")
