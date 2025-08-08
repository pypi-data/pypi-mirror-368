"""Status command - List and monitor GPU compute tasks.

This module implements the status command for the Flow CLI. It provides a
comprehensive view of submitted tasks, with filtering and display options
for monitoring task execution and resource usage.

Examples:
    # Check your active tasks (running/pending)
    $ flow status

    # Monitor a specific task by name or ID
    $ flow status my-training-job

    # Show only running tasks with costs
    $ flow status --status running

Command Usage:
    flow status [TASK_ID_OR_NAME] [OPTIONS]

Status values:
- pending: Task submitted, waiting for resources
- running: Task actively executing on GPU
- preempting: Task running but will be terminated soon by provider
- completed: Task finished successfully
- failed: Task terminated with error
- cancelled: Task cancelled by user

The command will:
- Query tasks from the configured provider
- Apply status and time filters
- Format output in a readable table
- Show task IDs, status, GPU type, and timing
- Display creation and completion timestamps

Output includes:
- Task ID (shortened for readability)
- Current status with color coding
- GPU type allocated
- Creation timestamp
- Duration or completion time

Note:
    By default, shows only active tasks (running or pending). If no active
    tasks exist, shows recent tasks from the last 24 hours. Use --all to
    see the complete task history.
"""

import sys
import time
from typing import Optional
from datetime import datetime, timedelta, timezone

import click
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

from flow import Flow
from flow.api.models import TaskStatus
from flow.errors import AuthenticationError

from .base import BaseCommand, console
from ..utils.theme_manager import theme_manager
from ..utils.task_presenter import TaskPresenter, DisplayOptions
from ..utils.animated_progress import AnimatedEllipsisProgress


class StatusCommand(BaseCommand):
    """List tasks with optional filtering."""

    def __init__(self):
        """Initialize command with task presenter."""
        super().__init__()
        self.task_presenter = TaskPresenter(console)

    @property
    def name(self) -> str:
        return "status"

    @property
    def help(self) -> str:
        return "List and monitor GPU compute tasks - filter by status, name, or time"

    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        @click.argument("task_identifier", required=False)
        @click.option(
            "--all", "show_all", is_flag=True, help="Show all tasks (default: active tasks only)"
        )
        @click.option(
            "--state",
            "-s",
            type=click.Choice(
                ["pending", "running", "paused", "preempting", "completed", "failed", "cancelled"]
            ),
            help="Filter by state",
        )
        @click.option(
            "--status",
            "state",
            type=click.Choice(
                ["pending", "running", "paused", "preempting", "completed", "failed", "cancelled"]
            ),
            help="Filter by status (alias)",
            hidden=True,
        )
        @click.option("--limit", default=20, help="Maximum number of tasks to show")
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        @click.option(
            "--since",
            type=str,
            help="Only tasks created since time (e.g., '2h', '2025-08-07T10:00:00Z')",
        )
        @click.option(
            "--until", type=str, help="Only tasks created until time (same formats as --since)"
        )
        @click.option(
            "--verbose",
            "-v",
            is_flag=True,
            help="Show detailed status information and filtering examples",
        )
        @click.option("--watch", "-w", is_flag=True, help="Live update the status display")
        @click.option("--compact", is_flag=True, help="Compact allocation view (was `flow alloc`)")
        @click.option(
            "--refresh-rate",
            default=3.0,
            type=float,
            help="Refresh rate in seconds for watch mode (default: 3)",
        )
        @click.option("--wide", is_flag=True, help="Use wide table (experimental)", hidden=True)
        def status(
            task_identifier: Optional[str],
            show_all: bool,
            state: Optional[str],
            limit: int,
            output_json: bool,
            since: Optional[str],
            until: Optional[str],
            verbose: bool,
            watch: bool,
            compact: bool,
            wide: bool,
            refresh_rate: float,
        ):
            """List active tasks or show details for a specific task.

            \b
            Examples:
                flow status                  # Active tasks (running/pending)
                flow status my-training      # Find task by name
                flow status --status running # Only running tasks
                flow status --all            # Show all tasks
                flow status --watch          # Live updating display
                flow status -w --refresh-rate 1  # Update every second

            Use 'flow status --verbose' for advanced filtering and monitoring patterns.
            """
            if verbose and not task_identifier:
                accent = theme_manager.get_color("accent")
                border = theme_manager.get_color("table.border")

                sections = []
                sections.append("[bold]Filtering options:[/bold]")
                sections.extend([
                    "  flow status                       # Show active tasks (running/pending)",
                    "  flow status --all                 # Show all tasks (not just active)",
                    "  flow status --status running      # Filter by specific status",
                    "  flow status --status pending      # Tasks waiting for resources",
                    "  flow status --limit 50            # Show more results",
                    "",
                ])

                sections.append("[bold]Task details:[/bold]")
                sections.extend([
                    "  flow status task-abc123           # View specific task",
                    "  flow status my-training           # Find by name",
                    "  flow status training-v2           # Partial name match",
                    "",
                ])

                sections.append("[bold]Status values:[/bold]")
                sections.extend([
                    "  • pending     - Waiting for resources",
                    "  • running     - Actively executing",
                    "  • paused      - Temporarily stopped (no billing)",
                    "  • preempting  - Will be terminated soon",
                    "  • completed   - Finished successfully",
                    "  • failed      - Terminated with error",
                    "  • cancelled   - Cancelled by user",
                    "",
                ])

                sections.append("[bold]Monitoring workflows:[/bold]")
                sections.extend([
                    "  # Live updating status display",
                    "  flow status --watch",
                    "  flow status -w --refresh-rate 1    # Update every second",
                    "",
                    "  # Using system watch command",
                    "  watch -n 5 'flow status --status running'",
                    "",
                    "  # Export for analysis",
                    "  flow status --all --json > tasks.json",
                    "",
                    "  # Check failed tasks",
                    "  flow status --status failed --limit 10",
                    "",
                ])

                sections.append("[bold]Next actions:[/bold]")
                sections.extend([
                    "  • View logs: flow logs <task-name>",
                    "  • Connect: flow ssh <task-name>",
                    "  • Cancel: flow cancel <task-name>",
                    "  • Check health: flow health --task <task-name>",
                ])

                content = "\n".join(sections)
                panel = Panel(
                    content,
                    title=f"[bold {accent}]Task Status and Monitoring[/bold {accent}]",
                    border_style=border,
                    padding=(1, 2),
                )
                console.print(panel)
                return

            # Default to next-gen UI for snapshot list (no JSON, no specific task, no watch)
            if (not output_json) and (not task_identifier) and (not watch):
                try:
                    # Fetch tasks under progress to preserve existing UX
                    from ..utils.task_fetcher import TaskFetcher

                    with AnimatedEllipsisProgress(console, "Fetching tasks", start_immediately=True):
                        fetcher = TaskFetcher(Flow())
                        tasks = fetcher.fetch_for_display(
                            show_all=show_all, status_filter=state, limit=limit
                        )

                    # Apply optional time filtering
                    since_dt = self._parse_timespec(since)
                    until_dt = self._parse_timespec(until)
                    if since_dt or until_dt:
                        def _in_range(t):
                            ts = t.created_at
                            if not ts:
                                return False
                            if ts.tzinfo is None:
                                ts = ts.replace(tzinfo=timezone.utc)
                            if since_dt and ts < since_dt:
                                return False
                            if until_dt and ts > until_dt:
                                return False
                            return True
                        tasks = [t for t in tasks if _in_range(t)]

                    if compact:
                        # Compact allocation view (integrated alloc)
                        from .alloc import BeautifulTaskRenderer
                        renderer = BeautifulTaskRenderer(console)
                        panel = renderer.render_allocation_view(tasks)
                        console.print(panel)
                        return
                    else:
                        # Core table view
                        from flow.cli.utils.status_presenter import StatusPresenter as CoreStatusPresenter
                        from flow.cli.utils.status_presenter import StatusDisplayOptions

                        presenter = CoreStatusPresenter(console)
                        options = StatusDisplayOptions(
                            show_all=(show_all or since or until),
                            limit=limit,
                            wide=wide,
                        )
                        presenter.present(options, tasks=tasks)
                        return
                except Exception as e:
                    # Fallback to stable path on any error
                    try:
                        from rich.markup import escape
                        err = escape(str(e))
                    except Exception:
                        err = str(e)
                    console.print(f"[yellow]New UI failed: {err}[/yellow]\nFalling back...", markup=True)

            self._execute(
                task_identifier,
                show_all,
                state,
                limit,
                output_json,
                since,
                until,
                watch,
                refresh_rate,
            )

        return status

    def _parse_timespec(self, value: Optional[str]) -> Optional[datetime]:
        """Parse timespec like '5m', '2h', '7d' or ISO8601."""
        if not value:
            return None
        s = value.strip()
        try:
            if s.endswith("m") and s[:-1].isdigit():
                return datetime.now(timezone.utc) - timedelta(minutes=int(s[:-1]))
            if s.endswith("h") and s[:-1].isdigit():
                return datetime.now(timezone.utc) - timedelta(hours=int(s[:-1]))
            if s.endswith("d") and s[:-1].isdigit():
                return datetime.now(timezone.utc) - timedelta(days=int(s[:-1]))
            # ISO8601 with optional Z
            if s.endswith("Z"):
                s = s[:-1] + "+00:00"
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            return None

    def _execute(
        self,
        task_identifier: Optional[str],
        show_all: bool,
        status: Optional[str],
        limit: int,
        output_json: bool,
        since: Optional[str],
        until: Optional[str],
        watch: bool = False,
        refresh_rate: float = 3.0,
    ) -> None:
        """Execute the status command."""
        # Cannot use watch mode with JSON output or specific task identifier
        if watch and (output_json or task_identifier):
            if output_json:
                console.print("[red]Error:[/red] Cannot use --watch with --json")
            else:
                console.print("[red]Error:[/red] Cannot use --watch when viewing a specific task")
            return

        # JSON output mode - no animation
        if output_json:
            import json

            flow_client = Flow()

            if task_identifier:
                # Single task lookup
                from ..utils.task_resolver import resolve_task_identifier

                task, error = resolve_task_identifier(flow_client, task_identifier)

                if error:
                    result = {"error": error}
                else:
                    result = {
                        "schema_version": "1.0",
                        "task": {
                            "task_id": task.task_id,
                            "name": task.name,
                            "status": task.status.value,
                            "instance_type": task.instance_type,
                            "num_instances": getattr(task, "num_instances", 1),
                            "region": task.region,
                            "created_at": task.created_at.isoformat() if task.created_at else None,
                            "started_at": task.started_at.isoformat()
                            if getattr(task, "started_at", None)
                            else None,
                            "completed_at": task.completed_at.isoformat()
                            if getattr(task, "completed_at", None)
                            else None,
                            "ssh_host": task.ssh_host,
                        },
                    }

                console.print(json.dumps(result))
                return
            else:
                # Task list
                from ..utils.task_fetcher import TaskFetcher

                fetcher = TaskFetcher(flow_client)
                tasks = fetcher.fetch_for_display(
                    show_all=show_all, status_filter=status, limit=limit
                )

                # Apply time filters if provided
                since_dt = self._parse_timespec(since)
                until_dt = self._parse_timespec(until)
                if since_dt or until_dt:

                    def _in_range(t):
                        ts = t.created_at
                        if not ts:
                            return False
                        if ts.tzinfo is None:
                            ts = ts.replace(tzinfo=timezone.utc)
                        if since_dt and ts < since_dt:
                            return False
                        if until_dt and ts > until_dt:
                            return False
                        return True

                    tasks = [t for t in tasks if _in_range(t)]

                result = {
                    "schema_version": "1.0",
                    "tasks": [
                        {
                            "task_id": task.task_id,
                            "name": task.name,
                            "status": task.status.value,
                            "instance_type": task.instance_type,
                            "num_instances": getattr(task, "num_instances", 1),
                            "region": getattr(task, "region", None),
                            "created_at": task.created_at.isoformat() if task.created_at else None,
                            "started_at": task.started_at.isoformat()
                            if getattr(task, "started_at", None)
                            else None,
                            "completed_at": task.completed_at.isoformat()
                            if getattr(task, "completed_at", None)
                            else None,
                        }
                        for task in tasks
                    ],
                }

                console.print(json.dumps(result))
                return

        # Check if we're in watch mode
        if watch:
            # If compact is requested, use alloc-like live view; else keep existing live table
            if compact:
                self._execute_live_mode_compact(show_all, status, limit, refresh_rate)
            else:
                self._execute_live_mode(show_all, status, limit, refresh_rate)
            return

        # Start animation immediately for instant feedback
        progress = AnimatedEllipsisProgress(
            console,
            "Fetching tasks" if not task_identifier else "Looking up task",
            start_immediately=True,
        )

        try:
            # Handle specific task request
            if task_identifier:
                with progress:
                    if not self.task_presenter.present_single_task(task_identifier):
                        return
            else:
                # Present task list with options
                display_options = DisplayOptions(
                    show_all=(show_all or since or until),
                    status_filter=status,
                    limit=limit,
                    show_details=True,
                )

                with progress:
                    # Optionally apply time-range filtering post-fetch
                    tasks = None
                    if since or until:
                        from ..utils.task_fetcher import TaskFetcher

                        fetcher = TaskFetcher(Flow())
                        tasks = fetcher.fetch_for_display(
                            show_all=True, status_filter=status, limit=limit
                        )
                        since_dt = self._parse_timespec(since)
                        until_dt = self._parse_timespec(until)
                        if since_dt or until_dt:

                            def _in_range(t):
                                ts = t.created_at
                                if not ts:
                                    return False
                                if ts.tzinfo is None:
                                    ts = ts.replace(tzinfo=timezone.utc)
                                if since_dt and ts < since_dt:
                                    return False
                                if until_dt and ts > until_dt:
                                    return False
                                return True

                            tasks = [t for t in tasks if _in_range(t)]
                    summary = self.task_presenter.present_task_list(display_options, tasks=tasks)

                # Show context-aware recommendations based on task states
                if summary:
                    recommendations = []

                    # Dynamic help based on number of tasks shown
                    task_count = min(summary.total_shown, limit)
                    index_help = f":1-{task_count}" if task_count > 1 else ":1"

                    # Check task states for context-aware recommendations
                    has_running = summary.running_tasks > 0
                    has_pending = summary.pending_tasks > 0
                    has_paused = summary.paused_tasks > 0
                    has_failed = summary.failed_tasks > 0

                    if has_running:
                        recommendations.append(
                            f"SSH into running task: [cyan]flow ssh <task-name>[/cyan] or [cyan]flow ssh {index_help}[/cyan]"
                        )
                        recommendations.append(
                            f"View logs for a task: [cyan]flow logs <task-name>[/cyan] or [cyan]flow logs {index_help}[/cyan]"
                        )

                    if has_pending:
                        recommendations.append(
                            f"Check pending task details: [cyan]flow status <task-name>[/cyan]"
                        )
                        if has_pending and not has_running:
                            recommendations.append(
                                "View all available resources: [cyan]flow status --all[/cyan]"
                            )

                    if has_paused:
                        recommendations.append(
                            f"Resume paused task: [cyan]flow grab <task-name>[/cyan]"
                        )

                    if has_failed:
                        recommendations.append(
                            f"Debug failed task: [cyan]flow logs <failed-task-name>[/cyan]"
                        )

                    # Always include new task submission
                    if len(recommendations) < 3:
                        recommendations.append("Submit a new task: [cyan]flow run task.yaml[/cyan]")

                    # If no active tasks, show getting started options
                    if summary.active_tasks == 0:
                        recommendations = [
                            "Submit a new task: [cyan]flow run task.yaml[/cyan]",
                            "Start development environment: [cyan]flow dev[/cyan]",
                            "View examples: [cyan]flow example[/cyan]",
                        ]

                    if recommendations:
                        self.show_next_actions(recommendations[:3])  # Show top 3 recommendations

        except AuthenticationError:
            self.handle_auth_error()
        except Exception as e:
            self.handle_error(str(e))

    def _execute_live_mode(
        self, show_all: bool, status_filter: Optional[str], limit: int, refresh_rate: float
    ) -> None:
        """Execute status command in live update mode."""
        if not sys.stdin.isatty():
            console.print("[red]Error:[/red] Live mode requires an interactive terminal")
            return

        from rich.console import Group
        from rich.text import Text
        from rich.panel import Panel
        from ..utils.animated_progress import AnimatedEllipsisProgress

        try:
            flow_client = Flow(auto_init=True)

            # Define get_display first so we can use it during initialization
            def get_display():
                """Get the current display as a renderable."""
                # Fetch and filter tasks
                from ..utils.task_fetcher import TaskFetcher
                from ..utils.task_renderer import TaskTableRenderer

                try:
                    fetcher = TaskFetcher(flow_client)
                    tasks = fetcher.fetch_for_display(
                        show_all=show_all, status_filter=status_filter, limit=limit
                    )
                except Exception as e:
                    return Text(f"Error fetching tasks: {e}", style="red")

                if not tasks:
                    return Text("No tasks found", style="dim")

                # Calculate summary
                running = sum(1 for t in tasks if t.status.value == "running")
                pending = sum(1 for t in tasks if t.status.value == "pending")

                # Calculate GPU hours
                total_gpu_hours = 0.0
                for task in tasks:
                    if task.status.value in ["running", "completed", "failed"] and task.created_at:
                        from datetime import datetime, timezone

                        end_time = (
                            task.completed_at if task.completed_at else datetime.now(timezone.utc)
                        )
                        created_at = (
                            task.created_at.replace(tzinfo=timezone.utc)
                            if task.created_at.tzinfo is None
                            else task.created_at
                        )
                        duration_hours = (end_time - created_at).total_seconds() / 3600.0

                        import re

                        gpu_count = 1
                        if task.instance_type:
                            match = re.match(r"(\d+)x", task.instance_type)
                            if match:
                                gpu_count = int(match.group(1))
                        total_gpu_hours += duration_hours * gpu_count

                # Build summary line
                parts = []
                if running > 0:
                    parts.append(f"{running} running")
                if pending > 0:
                    parts.append(f"{pending} pending")
                if total_gpu_hours > 0:
                    gpu_hrs_str = (
                        f"{total_gpu_hours:.1f}"
                        if total_gpu_hours >= 1
                        else f"{total_gpu_hours:.2f}"
                    )
                    parts.append(f"GPU-hrs: {gpu_hrs_str}")

                summary_line = " · ".join(parts) if parts else ""

                # Get the table/panel from renderer
                renderer = TaskTableRenderer(console)
                title = f"Tasks (showing up to {limit}"
                if not show_all:
                    title += ", last 24 hours"
                title += ")"

                panel = renderer.render_task_list(
                    tasks, title=title, show_all=show_all, limit=limit, return_renderable=True
                )

                # If panel is None, something went wrong
                if panel is None:
                    return Text("Error: Could not render tasks", style="red")

                # Combine summary and panel
                if summary_line:
                    return Group(
                        Text(summary_line, style="dim"),
                        Text(""),  # Empty line
                        panel,
                    )
                return panel

            # Start animation and keep it running while we prepare the first display
            with AnimatedEllipsisProgress(
                console,
                "Starting live status monitor",
                start_immediately=True,
            ) as progress:
                # Create flow client once
                flow_client = Flow()

                # Get the initial display while animation is still running
                initial_display = get_display()

            # Fallback if display is None
            if initial_display is None:
                initial_display = Panel("Initializing...", title="Status", border_style="cyan")

            with Live(
                initial_display, console=console, refresh_per_second=1 / refresh_rate, screen=True
            ) as live:
                while True:
                    try:
                        display = get_display()
                        if display:
                            live.update(display)
                        time.sleep(refresh_rate)
                    except KeyboardInterrupt:
                        break

            console.print("\n[green]Live monitor stopped.[/green]")

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")

    def _execute_live_mode_compact(
        self, show_all: bool, status_filter: Optional[str], limit: int, refresh_rate: float
    ) -> None:
        """Execute alloc-like live update mode (compact grouped view)."""
        if not sys.stdin.isatty():
            console.print("[red]Error:[/red] Live mode requires an interactive terminal")
            return

        from rich.panel import Panel
        from ..utils.animated_progress import AnimatedEllipsisProgress
        from .alloc import BeautifulTaskRenderer
        from ..utils.task_fetcher import TaskFetcher

        renderer = BeautifulTaskRenderer(console)
        flow_client = Flow()
        fetcher = TaskFetcher(flow_client)

        def get_display():
            try:
                tasks = fetcher.fetch_for_display(show_all=show_all, status_filter=status_filter, limit=limit)
                renderer.advance_animation()
                return renderer.render_allocation_view(tasks)
            except Exception as e:
                return Panel(f"[red]Error: {e}[/red]", border_style="red")

        try:
            with AnimatedEllipsisProgress(console, "Starting compact monitor", start_immediately=True):
                initial_display = get_display()

            from rich.live import Live
            with Live(initial_display, console=console, refresh_per_second=2, screen=True, transient=True) as live:
                while True:
                    try:
                        live.update(get_display())
                        time.sleep(refresh_rate)
                    except KeyboardInterrupt:
                        break

            console.print("\n[green]Live monitor stopped.[/green]")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")


# Export command instance
command = StatusCommand()
