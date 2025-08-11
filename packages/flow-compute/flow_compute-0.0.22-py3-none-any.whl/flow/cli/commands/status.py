"""Status command - list and monitor GPU compute tasks.

Provides task listings with filtering and display options for monitoring
execution and resource usage.

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
from datetime import datetime, timezone

import click
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from flow.api.client import Flow
from flow.cli.commands.base import BaseCommand, console
from flow.cli.utils.animated_progress import AnimatedEllipsisProgress
from flow.cli.utils.task_presenter import DisplayOptions, TaskPresenter
from flow.cli.utils.theme_manager import theme_manager
from flow.errors import AuthenticationError


class StatusCommand(BaseCommand):
    """List tasks with optional filtering."""

    def __init__(self):
        """Initialize command with task presenter.

        Avoid creating Flow() at import time to prevent environment-dependent
        side effects during module import (e.g., smoke import or docs build).
        The presenter will lazily create a Flow client on first use.
        """
        super().__init__()
        self.task_presenter = TaskPresenter(console)

    @property
    def name(self) -> str:
        return "status"

    @property
    def help(self) -> str:
        return "List and monitor GPU compute tasks - filter by status, name, or time"

    def get_command(self) -> click.Command:
        from flow.cli.utils.mode import demo_aware_command

        @click.command(name=self.name, help=self.help)
        @click.argument("task_identifier", required=False)
        @click.option(
            "--all", "show_all", is_flag=True, help="Show all tasks (default: active tasks only)"
        )
        @click.option(
            "--demo/--no-demo",
            default=None,
            help="Override demo mode for this command (mock provider, no real provisioning)",
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
        @click.option(
            "--force-refresh",
            is_flag=True,
            help="Bypass local caches and fetch fresh task data from provider",
        )
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
        @click.option(
            "--project",
            type=str,
            required=False,
            help="Filter to a specific project/workspace (provider dependent)",
        )
        @click.option(
            "--no-origin-group", is_flag=True, help="Disable Flow/Other grouping in main view"
        )
        @click.option(
            "--show-reservations",
            is_flag=True,
            help="Show an additional Reservations panel (upcoming and active)",
        )
        @demo_aware_command(flag_param="demo")
        def status(
            task_identifier: str | None,
            show_all: bool,
            state: str | None,
            limit: int,
            output_json: bool,
            since: str | None,
            until: str | None,
            verbose: bool,
            watch: bool,
            compact: bool,
            wide: bool,
            refresh_rate: float,
            project: str | None,
            no_origin_group: bool,
            show_reservations: bool,
            demo: bool | None,
            force_refresh: bool,
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
            if force_refresh:
                # Clear prefetch caches before proceeding
                try:
                    from flow.cli.utils.prefetch import (
                        refresh_active_task_caches as _refresh_active,
                        refresh_all_tasks_cache as _refresh_all,
                    )

                    _refresh_active()
                    _refresh_all()
                except Exception:
                    pass

            if verbose and not task_identifier:
                accent = theme_manager.get_color("accent")
                border = theme_manager.get_color("table.border")

                sections = []
                sections.append("[bold]Filtering options:[/bold]")
                sections.extend(
                    [
                        "  flow status                       # Show active tasks (running/pending)",
                        "  flow status --all                 # Show all tasks (not just active)",
                        "  flow status --status running      # Filter by specific status",
                        "  flow status --status pending      # Tasks waiting for resources",
                        "  flow status --limit 50            # Show more results",
                        "",
                    ]
                )

                sections.append("[bold]Task details:[/bold]")
                sections.extend(
                    [
                        "  flow status task-abc123           # View specific task",
                        "  flow status my-training           # Find by name",
                        "  flow status training-v2           # Partial name match",
                        "",
                    ]
                )

                sections.append("[bold]Status values:[/bold]")
                sections.extend(
                    [
                        "  • pending     - Waiting for resources",
                        "  • running     - Actively executing",
                        "  • paused      - Temporarily stopped (no billing)",
                        "  • preempting  - Will be terminated soon",
                        "  • completed   - Finished successfully",
                        "  • failed      - Terminated with error",
                        "  • cancelled   - Cancelled by user",
                        "",
                    ]
                )

                sections.append("[bold]Monitoring workflows:[/bold]")
                sections.extend(
                    [
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
                    ]
                )

                sections.append("[bold]Next actions:[/bold]")
                sections.extend(
                    [
                        "  • View logs: flow logs <task-name>",
                        "  • Connect: flow ssh <task-name>",
                        "  • Cancel: flow cancel <task-name>",
                        "  • Check health: flow health --task <task-name>",
                    ]
                )

                content = "\n".join(sections)
                panel = Panel(
                    content,
                    title=f"[bold {accent}]Task Status and Monitoring[/bold {accent}]",
                    border_style=border,
                    padding=(1, 2),
                )
                console.print(panel)
                return

            # Demo mode already applied by decorator

            # Default to next-gen UI for snapshot list (no JSON, no specific task, no watch)
            if (not output_json) and (not task_identifier) and (not watch):
                try:
                    from flow.api.models import TaskStatus
                    from flow.cli.utils.time_spec import parse_timespec

                    with AnimatedEllipsisProgress(
                        console, "Fetching tasks", start_immediately=True
                    ):
                        flow_client = Flow()
                        # Optional project scoping (provider dependent)
                        if project:
                            try:
                                import os as _os

                                _os.environ.setdefault("FLOW_PROJECT", project)
                            except Exception:
                                pass
                        status_enum = TaskStatus(state) if state else None
                        # Use display-optimized fetcher to prevent duplicates and
                        # prioritize active tasks. This also unifies pagination behavior.
                        from flow.cli.utils.task_fetcher import TaskFetcher as _Fetcher

                        _fetcher = _Fetcher(flow_client)
                        if status_enum is None and not show_all and not (since or until):
                            tasks = _fetcher.fetch_for_display(show_all=False, status_filter=None, limit=limit)
                        else:
                            # Respect explicit filters
                            if status_enum is not None:
                                tasks = _fetcher.fetch_all_tasks(limit=limit, prioritize_active=False, status_filter=status_enum)
                            else:
                                tasks = _fetcher.fetch_all_tasks(limit=limit, prioritize_active=False, status_filter=None)

                    # Apply optional time filtering (delegated helper)
                    since_dt = parse_timespec(since)
                    until_dt = parse_timespec(until)
                    if since_dt or until_dt:

                        def _in_range(t):
                            ts = getattr(t, "created_at", None)
                            if not ts:
                                return False
                            if getattr(ts, "tzinfo", None) is None:
                                ts = ts.replace(tzinfo=timezone.utc)
                            if since_dt and ts < since_dt:
                                return False
                            if until_dt and ts > until_dt:
                                return False
                            return True

                        tasks = [t for t in tasks if _in_range(t)]

                    if compact:
                        # Compact allocation view (integrated alloc)
                        from flow.cli.commands.alloc import BeautifulTaskRenderer

                        renderer = BeautifulTaskRenderer(console)
                        panel = renderer.render_allocation_view(tasks)
                        console.print(panel)
                        return
                    else:
                        # Core table view
                        from flow.cli.utils.status_presenter import StatusDisplayOptions
                        from flow.cli.utils.status_presenter import (
                            StatusPresenter as CoreStatusPresenter,
                        )

                        # Inject the Flow client directly to avoid implicit creation paths
                        presenter = CoreStatusPresenter(console, flow_client=flow_client)
                        options = StatusDisplayOptions(
                            show_all=(show_all or since or until),
                            limit=limit,
                            wide=wide,
                            group_by_origin=(not no_origin_group),
                        )
                        try:
                            presenter.present(options, tasks=tasks)
                        except Exception:
                            # Ultra-safe fallback: render table directly
                            from flow.cli.utils.status_table_renderer import (
                                StatusTableRenderer as _Tbl,
                            )

                            _r = _Tbl(console)
                            panel = _r.render(
                                tasks,
                                me=None,
                                title=(
                                    f"Tasks (showing up to {limit}{', last 24 hours' if not (show_all or since or until) else ''})"
                                ),
                                wide=wide,
                                start_index=1,
                                return_renderable=True,
                            )
                            console.print(panel)
                            return

                        # Optional Reservations panel
                        if show_reservations:
                            try:
                                provider = flow_client.provider
                                caps = provider.get_capabilities()
                                # Only proceed when capability is explicitly True (avoid Mock truthiness)
                                if hasattr(caps, "supports_reservations") and (
                                    caps.supports_reservations is True
                                ):
                                    from datetime import datetime, timezone

                                    from rich.panel import Panel
                                    from rich.table import Table

                                    reservations = provider.list_reservations()

                                    # Sort by start time; keep top 5
                                    def _start(r):
                                        return getattr(r, "start_time_utc", None) or datetime.now(
                                            timezone.utc
                                        )

                                    try:
                                        if isinstance(reservations, list):
                                            reservations.sort(key=_start)
                                            reservations = reservations[:5]
                                        else:
                                            reservations = []
                                    except Exception:
                                        reservations = []

                                    if reservations:
                                        table = Table(
                                            show_header=True, header_style="bold", expand=False
                                        )
                                        table.add_column("Name", no_wrap=True)
                                        table.add_column("Type", no_wrap=True)
                                        table.add_column("Qty", justify="right")
                                        table.add_column("Region", no_wrap=True)
                                        table.add_column("Start (UTC)")
                                        table.add_column("Start In", justify="right")
                                        table.add_column("Window", justify="right")

                                        now = datetime.now(timezone.utc)
                                        for r in reservations:
                                            name = getattr(r, "name", None) or getattr(
                                                r, "reservation_id", "-"
                                            )
                                            it = getattr(r, "instance_type", "-")
                                            qty = str(getattr(r, "quantity", 1))
                                            region = getattr(r, "region", "-")
                                            st = getattr(r, "start_time_utc", None)
                                            et = getattr(r, "end_time_utc", None)
                                            start_str = (
                                                st.isoformat().replace("+00:00", "Z") if st else "-"
                                            )
                                            start_in = "-"
                                            if st:
                                                try:
                                                    delta_min = max(
                                                        0, int((st - now).total_seconds() // 60)
                                                    )
                                                    start_in = (
                                                        f"{delta_min}m"
                                                        if delta_min < 120
                                                        else f"{delta_min//60}h"
                                                    )
                                                except Exception:
                                                    pass
                                            window = "-"
                                            if st and et:
                                                try:
                                                    dur_h = int(
                                                        round((et - st).total_seconds() / 3600)
                                                    )
                                                    window = f"{dur_h}h"
                                                except Exception:
                                                    pass
                                            table.add_row(
                                                name, it, qty, region, start_str, start_in, window
                                            )

                                        panel = Panel(
                                            table, title="Reservations", border_style="bright_black"
                                        )
                                        console.print("")
                                        console.print(panel)
                            except Exception:
                                pass
                        return
                except Exception as e:
                    # If auth is not configured: in demo mode only, use mock fallback; else show auth help
                    msg = str(e)
                    if (
                        isinstance(e, ValueError)
                        and (("Authentication not configured" in msg) or ("MITHRIL_API_KEY" in msg))
                    ) or isinstance(e, AuthenticationError):
                        try:
                            from flow.cli.utils.mode import is_demo_active as _is_demo

                            if _is_demo():
                                with AnimatedEllipsisProgress(
                                    console, "Using demo provider", start_immediately=True
                                ):
                                    flow_client = Flow()
                                    status_enum = TaskStatus(state) if state else None
                                    tasks = flow_client.list_tasks(status=status_enum, limit=limit)

                                from flow.cli.utils.status_presenter import StatusDisplayOptions
                                from flow.cli.utils.status_presenter import (
                                    StatusPresenter as CoreStatusPresenter,
                                )

                                presenter = CoreStatusPresenter(console, flow_client=flow_client)
                                options = StatusDisplayOptions(
                                    show_all=(show_all or since or until),
                                    limit=limit,
                                    wide=wide,
                                    group_by_origin=(not no_origin_group),
                                )
                                presenter.present(options, tasks=tasks)
                                return
                            else:
                                self.handle_auth_error()
                                return
                        except Exception:
                            self.handle_auth_error()
                            return
                    # Hard error path: surface error clearly and exit non-zero
                    from rich.markup import escape as _escape

                    console.print(f"[red]Error:[/red] {_escape(str(e))}")
                    raise click.exceptions.Exit(2)

            self._execute(
                task_identifier,
                show_all,
                state,
                limit,
                output_json,
                since,
                until,
                watch,
                compact,
                refresh_rate,
            )

        return status

    def _parse_timespec(self, value: str | None) -> datetime | None:
        from flow.cli.utils.time_spec import parse_timespec

        return parse_timespec(value)

    def _execute(
        self,
        task_identifier: str | None,
        show_all: bool,
        status: str | None,
        limit: int,
        output_json: bool,
        since: str | None,
        until: str | None,
        watch: bool = False,
        compact: bool = False,
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
                from flow.cli.utils.task_resolver import resolve_task_identifier

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
                            "started_at": (
                                task.started_at.isoformat()
                                if getattr(task, "started_at", None)
                                else None
                            ),
                            "completed_at": (
                                task.completed_at.isoformat()
                                if getattr(task, "completed_at", None)
                                else None
                            ),
                            "ssh_host": task.ssh_host,
                        },
                    }

                console.print(json.dumps(result))
                return
            else:
                # Task list
                from flow.cli.utils.task_fetcher import TaskFetcher
                from flow.cli.utils.time_spec import parse_timespec

                fetcher = TaskFetcher(flow_client)
                tasks = fetcher.fetch_for_display(
                    show_all=show_all, status_filter=status, limit=limit
                )

                # Apply time filters if provided
                since_dt = parse_timespec(since)
                until_dt = parse_timespec(until)
                if since_dt or until_dt:

                    def _in_range(t):
                        ts = getattr(t, "created_at", None)
                        if not ts:
                            return False
                        if getattr(ts, "tzinfo", None) is None:
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
                            "started_at": (
                                task.started_at.isoformat()
                                if getattr(task, "started_at", None)
                                else None
                            ),
                            "completed_at": (
                                task.completed_at.isoformat()
                                if getattr(task, "completed_at", None)
                                else None
                            ),
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
                    # Ensure presenter uses this module's Flow (patched in tests)
                    try:
                        if not getattr(self.task_presenter, "flow_client", None):
                            self.task_presenter.flow_client = Flow()
                    except Exception:
                        pass
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
                    # Ensure presenter uses this module's Flow (patched in tests)
                    try:
                        if not getattr(self.task_presenter, "flow_client", None):
                            self.task_presenter.flow_client = Flow()
                    except Exception:
                        pass
                    # Optionally apply time-range filtering post-fetch
                    tasks = None
                    if since or until:
                        from flow.cli.utils.task_fetcher import TaskFetcher
                        from flow.cli.utils.time_spec import parse_timespec

                        fetcher = TaskFetcher(Flow())
                        tasks = fetcher.fetch_for_display(
                            show_all=True, status_filter=status, limit=limit
                        )
                        since_dt = parse_timespec(since)
                        until_dt = parse_timespec(until)
                        if since_dt or until_dt:

                            def _in_range(t):
                                ts = getattr(t, "created_at", None)
                                if not ts:
                                    return False
                                if getattr(ts, "tzinfo", None) is None:
                                    ts = ts.replace(tzinfo=timezone.utc)
                                if since_dt and ts < since_dt:
                                    return False
                                if until_dt and ts > until_dt:
                                    return False
                                return True

                            tasks = [t for t in tasks if _in_range(t)]
                        # Ensure presenter uses this module's Flow symbol (patched by tests)
                        try:
                            if not getattr(self.task_presenter, "flow_client", None):
                                self.task_presenter.flow_client = Flow()
                        except Exception:
                            pass
                        summary = self.task_presenter.present_task_list(
                            display_options, tasks=tasks
                        )
                    else:
                        # No time filtering path: present using whatever Flow is patched to
                        summary = self.task_presenter.present_task_list(display_options, tasks=None)

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
                            f"SSH into running task: [accent]flow ssh <task-name>[/accent] or [accent]flow ssh {index_help}[/accent]"
                        )
                        recommendations.append(
                            f"View logs for a task: [accent]flow logs <task-name>[/accent] or [accent]flow logs {index_help}[/accent]"
                        )

                    if has_pending:
                        recommendations.append(
                            "Check pending task details: [accent]flow status <task-name>[/accent]"
                        )
                        if has_pending and not has_running:
                            recommendations.append(
                                "View all available resources: [accent]flow status --all[/accent]"
                            )

                    if has_paused:
                        recommendations.append(
                            "Resume paused task: [accent]flow grab <task-name>[/accent]"
                        )

                    if has_failed:
                        recommendations.append(
                            "Debug failed task: [accent]flow logs <failed-task-name>[/accent]"
                        )

                    # Always include new task submission
                    if len(recommendations) < 3:
                        recommendations.append(
                            "Submit a new task: [accent]flow run task.yaml[/accent]"
                        )

                    # If no active tasks, show getting started options
                    if summary.active_tasks == 0:
                        recommendations = [
                            "Submit a new task: [accent]flow run task.yaml[/accent]",
                            "Start development environment: [accent]flow dev[/accent]",
                            "View examples: [accent]flow example[/accent]",
                        ]

                    if recommendations:
                        self.show_next_actions(recommendations[:3])  # Show top 3 recommendations

        except AuthenticationError:
            self.handle_auth_error()
        except click.exceptions.Exit:
            # Ensure we don't print error messages twice
            raise
        except Exception as e:
            self.handle_error(e)

    def _execute_live_mode(
        self, show_all: bool, status_filter: str | None, limit: int, refresh_rate: float
    ) -> None:
        """Execute status command in live update mode."""
        if not sys.stdin.isatty():
            console.print("[red]Error:[/red] Live mode requires an interactive terminal")
            return

        from rich.console import Group
        from rich.panel import Panel

        from flow.cli.utils.animated_progress import AnimatedEllipsisProgress

        try:
            flow_client = Flow(auto_init=True)

            # Define get_display first so we can use it during initialization
            def get_display():
                """Get the current display as a renderable."""
                # Fetch and filter tasks
                from flow.cli.utils.task_fetcher import TaskFetcher
                from flow.cli.utils.task_renderer import TaskTableRenderer

                try:
                    fetcher = TaskFetcher(flow_client)
                    tasks = fetcher.fetch_for_display(
                        show_all=show_all, status_filter=status_filter, limit=limit
                    )
                except Exception as e:
                    from rich.markup import escape

                    return Text(f"Error fetching tasks: {escape(str(e))}", style="red")

                if not tasks:
                    return Text("No tasks found", style="dim")

                # Calculate summary
                running = sum(1 for t in tasks if t.status.value == "running")
                pending = sum(1 for t in tasks if t.status.value == "pending")

                # Calculate GPU hours (resilient to mocks/missing fields)
                total_gpu_hours = 0.0
                for task in tasks:
                    try:
                        from datetime import datetime, timezone

                        status_val = getattr(getattr(task, "status", None), "value", None)
                        created_at = getattr(task, "created_at", None)
                        if (
                            status_val in ["running", "completed", "failed"]
                            and created_at is not None
                        ):
                            end_time = getattr(task, "completed_at", None) or datetime.now(
                                timezone.utc
                            )
                            created_at = (
                                created_at.replace(tzinfo=timezone.utc)
                                if getattr(created_at, "tzinfo", None) is None
                                else created_at
                            )
                            duration_hours = (end_time - created_at).total_seconds() / 3600.0
                            import re

                            it = getattr(task, "instance_type", "") or ""
                            m = re.match(r"(\d+)x", str(it))
                            gpu_count = int(m.group(1)) if m else 1
                            total_gpu_hours += float(duration_hours) * float(gpu_count)
                    except Exception:
                        continue

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
                from flow.cli.utils.theme_manager import theme_manager as _tm
                initial_display = Panel(
                    "Initializing...",
                    title="[bold accent]Status[/bold accent]",
                    border_style=_tm.get_color("accent"),
                )

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

            from flow.cli.utils.theme_manager import theme_manager as _tm

            success_color = _tm.get_color("success")
            console.print(f"\n[{success_color}]Live monitor stopped.[/{success_color}]")

        except Exception as e:
            from rich.markup import escape

            console.print(f"[red]Error:[/red] {escape(str(e))}")

    def _execute_live_mode_compact(
        self, show_all: bool, status_filter: str | None, limit: int, refresh_rate: float
    ) -> None:
        """Execute alloc-like live update mode (compact grouped view)."""
        if not sys.stdin.isatty():
            console.print("[red]Error:[/red] Live mode requires an interactive terminal")
            return

        from rich.panel import Panel

        from flow.cli.commands.alloc import BeautifulTaskRenderer
        from flow.cli.utils.animated_progress import AnimatedEllipsisProgress
        from flow.cli.utils.task_fetcher import TaskFetcher

        renderer = BeautifulTaskRenderer(console)
        flow_client = Flow()
        fetcher = TaskFetcher(flow_client)

        def get_display():
            try:
                tasks = fetcher.fetch_for_display(
                    show_all=show_all, status_filter=status_filter, limit=limit
                )
                renderer.advance_animation()
                return renderer.render_allocation_view(tasks)
            except Exception as e:
                from rich.markup import escape

                return Panel(f"[red]Error: {escape(str(e))}[/red]", border_style="red")

        try:
            with AnimatedEllipsisProgress(
                console, "Starting compact monitor", start_immediately=True
            ):
                initial_display = get_display()

            from rich.live import Live

            with Live(
                initial_display, console=console, refresh_per_second=2, screen=True, transient=True
            ) as live:
                while True:
                    try:
                        live.update(get_display())
                        time.sleep(refresh_rate)
                    except KeyboardInterrupt:
                        break

            from flow.cli.utils.theme_manager import theme_manager as _tm2

            success_color = _tm2.get_color("success")
            console.print(f"\n[{success_color}]Live monitor stopped.[/{success_color}]")
        except Exception as e:
            from rich.markup import escape

            console.print(f"[red]Error:[/red] {escape(str(e))}")


# Export command instance
command = StatusCommand()
