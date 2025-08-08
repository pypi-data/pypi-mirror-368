"""Release command - Release grabbed GPU resources.

This module implements the release command for the Flow CLI. It provides
a clean way to release resources acquired with 'flow grab'.

Examples:
    # Interactive selection of grabbed resources
    $ flow release

    # Release by name
    $ flow release grab-abc123

    # Release by index from status
    $ flow release :1

    # Release all grabbed resources
    $ flow release --all

    # Force release without confirmation
    $ flow release grab-abc123 --force

Command Usage:
    flow release [NAME] [OPTIONS]
    flow release --all [OPTIONS]
"""

import click

from flow import Flow
from flow.api.models import Task, TaskStatus
from flow.errors import AuthenticationError

from ..utils.task_formatter import TaskFormatter
from ..utils.task_selector_mixin import TaskFilter, TaskOperationCommand
from .base import BaseCommand, console


class ReleaseCommand(BaseCommand, TaskOperationCommand):
    """Release grabbed GPU resources."""

    def __init__(self):
        """Initialize command with formatter."""
        super().__init__()
        self.task_formatter = TaskFormatter()

    @property
    def name(self) -> str:
        return "release"

    @property
    def help(self) -> str:
        return "Release grabbed GPU resources - clean up and show costs"

    def get_command(self) -> click.Command:
        # Import completion function
        from ..utils.shell_completion import complete_task_ids

        @click.command(name=self.name, help=self.help)
        @click.argument("task_identifier", required=False, shell_complete=complete_task_ids)
        @click.option(
            "--all",
            "-a",
            is_flag=True,
            help="Release all grabbed resources",
        )
        @click.option(
            "--force",
            "-f",
            is_flag=True,
            help="Skip confirmation prompt",
        )
        @click.option(
            "--verbose",
            "-v",
            is_flag=True,
            help="Show detailed release information and workflows",
        )
        def release(
            task_identifier: str | None,
            all: bool,
            force: bool,
            verbose: bool,
        ):
            """Release grabbed GPU resources.

            TASK_IDENTIFIER: Name, ID, or index of grabbed resources to release (optional - will show interactive selector if omitted)

            \b
            Examples:
                flow release                 # Interactive selection
                flow release grab-abc123     # Release by name
                flow release --all           # Release all grabbed
                flow release --all --force   # Skip confirmation

            Use 'flow release --verbose' for cost tracking details and workflows.
            """
            if verbose:
                console.print("\n[bold]Resource Release Guide:[/bold]\n")
                console.print("Selection methods:")
                console.print("  flow release                      # Interactive with cost info")
                console.print("  flow release train-v2             # By custom name")
                console.print("  flow release grab-abc123          # By auto-generated name")
                console.print("  flow release :1                   # By index from status\n")

                console.print("Batch operations:")
                console.print("  flow release --all                # Release all grabbed")
                console.print("  flow release --all --force        # No confirmation")
                console.print("  flow status | grep grab | xargs flow release --force\n")

                console.print("Cost information shown:")
                console.print("  • Total runtime duration")
                console.print("  • Hourly cost rate")
                console.print("  • Total cost incurred")
                console.print("  • Instance configuration\n")

                console.print("Common workflows:")
                console.print("  # End of work session")
                console.print("  flow status                       # Check what's running")
                console.print("  flow release                      # Interactive cleanup")
                console.print("  ")
                console.print("  # Automated cleanup")
                console.print("  NAME=$(flow grab 8 --json | jq -r .name)")
                console.print("  # ... do work ...")
                console.print("  flow release $NAME --force\n")

                console.print("Important notes:")
                console.print("  • Only releases 'grabbed' resources")
                console.print("  • Use 'flow cancel' for regular tasks")
                console.print("  • Shows final cost before termination")
                console.print("  • Resources stop billing immediately\n")
                return

            self._execute(task_identifier, all, force)

        return release

    # TaskSelectorMixin implementation
    def get_task_filter(self):
        """Only show grabbed resources (tasks starting with 'grab-')."""

        def grab_filter(tasks):
            return [
                t
                for t in tasks
                if t.name and t.name.startswith("grab-") and t.status == TaskStatus.RUNNING
            ]

        return grab_filter

    def get_selection_title(self) -> str:
        return "Select grabbed resources to release"

    def get_no_tasks_message(self) -> str:
        return "No grabbed resources found. Use 'flow grab' to allocate GPU resources."

    # Command execution
    def execute_on_task(self, task: Task, client: Flow, **kwargs) -> None:
        """Execute release on the selected task."""
        force = kwargs.get("force", False)

        # Verify this is a grabbed resource
        if not task.name or not task.name.startswith("grab-"):
            console.print(
                f"[yellow]'{task.name or task.task_id}' is not a grabbed resource. Use 'flow cancel' for regular tasks.[/yellow]"
            )

            # Show helpful next steps
            self.show_next_actions(
                [
                    f"Cancel this task: [cyan]flow cancel {task.name or task.task_id}[/cyan]",
                    "View all tasks: [cyan]flow status[/cyan]",
                    "Release grabbed resources: [cyan]flow release[/cyan]",
                ]
            )
            return

        # Double-check task is still running
        if task.status != TaskStatus.RUNNING:
            status_str = str(task.status).replace("TaskStatus.", "").lower()
            console.print(
                f"[yellow]Resource '{task.name or task.task_id}' is already {status_str}[/yellow]"
            )
            return

        # Show confirmation with resource details
        if not force:
            self._show_release_confirmation(task)

            if not click.confirm("\nRelease this resource?"):
                console.print("Cancelled.")
                return

        # Show progress
        from ..utils.animated_progress import AnimatedEllipsisProgress

        with AnimatedEllipsisProgress(
            console, "Releasing resource", start_immediately=True
        ) as progress:
            client.cancel(task.task_id)

        console.print(f"\n[green]✓[/green] Released {task.name}")

        # Show next actions
        self.show_next_actions(
            [
                "View all tasks: [cyan]flow status[/cyan]",
                "Grab new resources: [cyan]flow grab[/cyan]",
            ]
        )

    def _show_release_confirmation(self, task: Task) -> None:
        """Show a confirmation panel with resource details."""
        from datetime import datetime, timezone

        from rich.panel import Panel
        from rich.table import Table

        from ..utils.time_formatter import TimeFormatter

        time_fmt = TimeFormatter()

        # Create a clean table for resource details
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column(style="bold")
        table.add_column()

        # Resource name
        table.add_row("Resource", task.name or "Unnamed resource")

        # GPU type and count - use proper formatter
        from ..utils.gpu_formatter import GPUFormatter

        gpu_display = GPUFormatter.format_ultra_compact(
            task.instance_type, getattr(task, "num_instances", 1)
        )
        table.add_row("Configuration", gpu_display)

        # Duration
        duration = time_fmt.calculate_duration(task)
        table.add_row("Duration", duration)

        # Calculate cost if available
        if hasattr(task, "price_per_hour") and task.price_per_hour and task.started_at:
            start = task.started_at
            if hasattr(start, "tzinfo") and start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)

            now = datetime.now(timezone.utc)
            hours_run = (now - start).total_seconds() / 3600
            cost_so_far = hours_run * task.price_per_hour

            table.add_row("Cost so far", f"${cost_so_far:.2f}")
            table.add_row("Hourly rate", f"${task.price_per_hour:.2f}/hr")

        # Create panel
        panel = Panel(
            table,
            title="[bold cyan]Release Grabbed Resource[/bold cyan]",
            title_align="center",
            border_style="cyan",
            padding=(1, 2),
        )

        console.print()
        console.print(panel)

    def _execute(
        self,
        task_identifier: str | None,
        release_all: bool,
        force: bool,
    ) -> None:
        """Execute the release command."""
        if release_all:
            self._execute_release_all(force)
        else:
            # Use the TaskOperationCommand's execute_with_selection
            self.execute_with_selection(task_identifier, force=force)

    def _execute_release_all(self, force: bool) -> None:
        """Release all grabbed resources."""
        from ..utils.animated_progress import AnimatedEllipsisProgress

        try:
            with AnimatedEllipsisProgress(
                console, "Finding grabbed resources", start_immediately=True
            ) as progress:
                client = Flow()

                # Get all tasks
                from ..utils.task_fetcher import TaskFetcher

                fetcher = TaskFetcher(client)
                all_tasks = fetcher.fetch_all_tasks(limit=1000, prioritize_active=True)

                # Filter for grabbed resources
                grabbed_tasks = [
                    t
                    for t in all_tasks
                    if t.name and t.name.startswith("grab-") and t.status == TaskStatus.RUNNING
                ]

            if not grabbed_tasks:
                console.print("No grabbed resources found.")
                return

            # Show what will be released
            from ..utils.gpu_formatter import GPUFormatter

            console.print(
                f"\nFound {len(grabbed_tasks)} grabbed resource{'s' if len(grabbed_tasks) != 1 else ''}:"
            )
            for task in grabbed_tasks:
                gpu_info = GPUFormatter.format_ultra_compact(
                    task.instance_type, getattr(task, "num_instances", 1)
                )
                console.print(f"  - {task.name} ({gpu_info})")

            if not force:
                if not click.confirm("\nRelease all these resources?"):
                    console.print("Cancelled.")
                    return

            # Release all
            released_count = 0
            failed_count = 0

            with AnimatedEllipsisProgress(
                console, f"Releasing {len(grabbed_tasks)} resources", start_immediately=True
            ) as progress:
                for i, task in enumerate(grabbed_tasks):
                    progress.base_message = f"Releasing {task.name} ({i + 1}/{len(grabbed_tasks)})"

                    try:
                        client.cancel(task.task_id)
                        released_count += 1
                    except Exception as e:
                        console.print(f"[red]✗[/red] Failed to release {task.name}: {e}")
                        failed_count += 1

            # Summary
            console.print()
            if released_count > 0:
                console.print(
                    f"[green]✓[/green] Released {released_count} resource{'s' if released_count != 1 else ''}."
                )
            if failed_count > 0:
                console.print(
                    f"[red]✗[/red] Failed to release {failed_count} resource{'s' if failed_count != 1 else ''}."
                )

            # Show next actions
            self.show_next_actions(
                [
                    "View all tasks: [cyan]flow status[/cyan]",
                    "Grab new resources: [cyan]flow grab[/cyan]",
                ]
            )

        except AuthenticationError:
            self.handle_auth_error()
        except Exception as e:
            self.handle_error(str(e))


# Export command instance
command = ReleaseCommand()
