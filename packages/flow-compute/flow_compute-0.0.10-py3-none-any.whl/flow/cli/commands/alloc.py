"""Streamlined allocation view - abbreviated version of `flow status`.

Focused GPU resource display for rapid allocation assessment.
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
import time
import sys
import termios
import tty

import click
from rich.console import Console, Group, RenderableType
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from rich.align import Align
from rich.layout import Layout
from rich.columns import Columns

from flow import Flow
from flow.api.models import Task, TaskStatus
from flow.errors import AuthenticationError

from .base import BaseCommand, console
from ..utils.animated_progress import AnimatedEllipsisProgress


class BeautifulTaskRenderer:
    """Renders GPU task allocations with hierarchical organization.

    Implements a state-based rendering system that groups tasks by execution
    status and provides progressive detail levels. Optimized for terminal
    display with ANSI color support and box-drawing characters.

    Attributes:
        STATUS_SYMBOLS: Unicode symbols mapped to task states
        STATUS_COLORS: ANSI color codes for visual state differentiation
    """

    # Unicode symbols for task state representation
    STATUS_SYMBOLS = {
        "running": "●",  # Active execution
        "starting": "◐",  # Initialization phase
        "pending": "○",  # Queued for execution
        "completed": "✓",  # Successful completion
        "failed": "✗",  # Execution failure
        "paused": "⏸",  # Suspended execution
        "cancelled": "⊘",  # User-initiated termination
    }

    # ANSI color mapping for visual state differentiation
    STATUS_COLORS = {
        "running": "green",
        "starting": "bright_blue",
        "pending": "dim white",
        "completed": "dim green",
        "failed": "red",
        "paused": "dim yellow",
        "cancelled": "dim red",
    }

    def __init__(self, console: Console):
        self.console = console
        self._animation_frame = 0
        self.selected_index = 0
        self.show_details = False
        self.selected_task = None

    def render_interactive_view(self, tasks: List[Task]) -> RenderableType:
        """Render task list with keyboard navigation support.

        Args:
            tasks: List of Task objects to display.

        Returns:
            RenderableType: Panel or Columns layout with task list and optional details.
        """
        # Store tasks for selection
        self.tasks = tasks

        # Main list panel
        main_panel = self._render_task_list_interactive(tasks)

        # Detail panel if task selected
        if self.show_details and self.selected_task:
            detail_panel = self._render_task_detail_panel(self.selected_task)

            # Use Columns instead of Layout for simpler side-by-side display
            from rich.columns import Columns

            return Columns([main_panel, detail_panel], padding=1, expand=True)
        else:
            return main_panel

    def render_allocation_view(self, tasks: List[Task]) -> Panel:
        """Render hierarchical task display grouped by execution state.

        Tasks are organized into three primary groups: active (running/starting),
        pending, and completed. Display is limited to 20 tasks for performance.

        Args:
            tasks: List of Task objects to display.

        Returns:
            Panel: Formatted panel with grouped task display.
        """

        # Store tasks for potential selection
        self.tasks = tasks

        # Organize tasks by execution state
        active_tasks = []
        pending_tasks = []
        completed_tasks = []

        for task in tasks[:20]:  # Performance optimization: limit display count
            status = task.status.value
            if status in ["running", "starting"]:
                active_tasks.append(task)
            elif status == "pending":
                pending_tasks.append(task)
            else:
                completed_tasks.append(task)

        # Construct hierarchical display groups
        groups = []
        task_index = 0

        # Active tasks section
        if active_tasks:
            active_group = self._render_task_group(
                active_tasks, "Active", show_details=True, start_index=task_index
            )
            groups.append(active_group)
            groups.append(Text(""))  # Visual separator
            task_index += len(active_tasks)

        # Pending tasks section
        if pending_tasks:
            pending_group = self._render_task_group(
                pending_tasks, "Waiting", show_details=False, start_index=task_index
            )
            groups.append(pending_group)
            groups.append(Text(""))
            task_index += len(pending_tasks)

        # Recent completions (limited to 5 for display efficiency)
        if completed_tasks:
            recent_completed = completed_tasks[:5]
            completed_group = self._render_task_group(
                recent_completed, "Recent", show_details=False, dim=True, start_index=task_index
            )
            groups.append(completed_group)

        # No-data state display
        if not tasks:
            empty_state = self._render_empty_state()
            groups.append(empty_state)

        # Combine all groups
        content = Group(*groups) if groups else Text("Initializing...", style="dim")

        # Construct final panel with rounded borders
        return Panel(
            Align.center(content, vertical="middle"),
            title="[bold]GPU Resources[/bold]",
            title_align="center",
            border_style="bright_black",
            box=box.ROUNDED,
            padding=(1, 3),
            expand=True,
        )

    def _render_task_list_interactive(self, tasks: List[Task]) -> Panel:
        """Render interactive task list with selection indicator.

        Args:
            tasks: List of Task objects to display.

        Returns:
            Panel: Formatted panel with selectable task rows.
        """
        table = Table(show_header=False, show_edge=False, box=None, padding=(0, 2), expand=True)

        table.add_column("selector", width=3)
        table.add_column("status", width=3)
        table.add_column("name", min_width=20)
        table.add_column("gpu", width=12)
        table.add_column("time", width=8)

        for idx, task in enumerate(tasks[:15]):  # Display limit for terminal height
            status = self._get_display_status(task)
            symbol = self.STATUS_SYMBOLS.get(status, "?")
            color = self.STATUS_COLORS.get(status, "white")

            # Row selection state
            if idx == self.selected_index:
                selector = "▶"
                row_style = "bold cyan"
            else:
                selector = " "
                row_style = None

            # Task metadata extraction
            name = task.name or task.task_id[:8]
            if len(name) > 20:
                name = name[:17] + "..."

            gpu_info = self._format_gpu_elegant(
                task.instance_type, getattr(task, "num_instances", 1)
            )
            time_info = self._format_time_elegant(task)

            table.add_row(
                selector, f"[{color}]{symbol}[/{color}]", name, gpu_info, time_info, style=row_style
            )

        # Keyboard navigation guide
        help_text = Text(
            "\n↑↓/jk: navigate  Enter: details  q: quit  r: refresh", style="dim", justify="center"
        )

        content = Group(table, help_text)

        return Panel(
            content,
            title="[bold]GPU Resources[/bold] - Interactive Mode",
            title_align="center",
            border_style="cyan" if self.selected_index >= 0 else "bright_black",
            box=box.ROUNDED,
            padding=(1, 2),
        )

    def _render_task_detail_panel(self, task: Task) -> Panel:
        """Render comprehensive task details in side panel.

        Args:
            task: Task object to display details for.

        Returns:
            Panel: Formatted panel with task metadata and connection info.
        """
        lines = []

        # Task identification and status
        status = self._get_display_status(task)
        symbol = self.STATUS_SYMBOLS.get(status, "?")
        color = self.STATUS_COLORS.get(status, "white")

        lines.append(f"[bold]{task.name or task.task_id}[/bold]")
        lines.append(f"[{color}]{symbol} {status.upper()}[/{color}]\n")

        # Hardware resource allocation
        if task.instance_type:
            from ..utils.gpu_formatter import GPUFormatter

            gpu_display = GPUFormatter.format_ultra_compact(
                task.instance_type, getattr(task, "num_instances", 1)
            )
            lines.append(f"[bold]GPU:[/bold] {gpu_display}")
        if task.num_instances and task.num_instances > 1:
            lines.append(f"[bold]Nodes:[/bold] {task.num_instances}")
        if task.region:
            lines.append(f"[bold]Region:[/bold] {task.region}")

        lines.append("")  # Section separator

        # SSH connection parameters for active tasks
        if task.status.value == "running" and task.ssh_host:
            lines.append("[bold cyan]Connection:[/bold cyan]")
            lines.append(f"  IP: {task.ssh_host}")
            if task.ssh_port:
                lines.append(f"  Port: {task.ssh_port}")
            lines.append(f"\n  [dim]flow ssh {task.name}[/dim]")

        # Temporal metadata
        lines.append("")
        if task.created_at:
            lines.append(f"[bold]Created:[/bold] {self._format_time_detailed(task.created_at)}")

        duration = self._format_duration_detailed(task)
        if duration:
            lines.append(f"[bold]Duration:[/bold] {duration}")

        # Resource cost projection
        if hasattr(task, "estimated_cost"):
            lines.append(f"\n[bold]Est. Cost:[/bold] ${task.estimated_cost:.2f}/hr")

        content = "\n".join(lines)

        return Panel(
            content,
            title="[bold]Task Details[/bold]",
            title_align="left",
            border_style="blue",
            box=box.ROUNDED,
            padding=(1, 2),
        )

    def _render_task_group(
        self,
        tasks: List[Task],
        title: str,
        show_details: bool = True,
        dim: bool = False,
        start_index: int = 0,
    ) -> Table:
        """Render grouped tasks with configurable detail level.

        Args:
            tasks: List of Task objects to render.
            title: Section header text.
            show_details: Include GPU and timing columns.
            dim: Apply dimmed styling for de-emphasis.
            start_index: Starting index for task numbering.

        Returns:
            Table: Formatted table with task rows.
        """

        # Initialize borderless table layout
        table = Table(show_header=False, show_edge=False, box=None, padding=(0, 2), expand=False)

        # Configure column structure
        table.add_column("status", width=3)
        table.add_column("name", min_width=20)

        if show_details:
            table.add_column("gpu", width=12)
            table.add_column("time", width=8)

        # Insert section header
        title_style = "dim white" if dim else "bold white"
        table.add_row(
            "", f"[{title_style}]── {title} ──[/{title_style}]", *[""] * (2 if show_details else 0)
        )

        # Populate task rows
        for task in tasks:
            status = self._get_display_status(task)
            symbol = self.STATUS_SYMBOLS.get(status, "?")
            color = self.STATUS_COLORS.get(status, "white")

            # Apply animation to active tasks
            if status == "running" and not dim:
                # Brightness modulation for visual feedback
                if self._animation_frame % 4 < 2:
                    color = f"bright_{color}"

            # Task name truncation
            name = task.name or task.task_id[:8]
            if len(name) > 20:
                name = name[:17] + "..."

            row = [
                f"[{color}]{symbol}[/{color}]",
                f"[{'dim ' if dim else ''}white]{name}[/{'dim ' if dim else ''}white]",
            ]

            if show_details:
                # Hardware specification formatting
                gpu_info = self._format_gpu_elegant(
                    task.instance_type, getattr(task, "num_instances", 1)
                )
                row.append(f"[dim cyan]{gpu_info}[/dim cyan]")

                # Duration formatting
                time_info = self._format_time_elegant(task)
                row.append(f"[dim white]{time_info}[/dim white]")

            table.add_row(*row)

        return table

    def _render_empty_state(self) -> Panel:
        """Render informative message when no tasks are present.

        Returns:
            Panel: Formatted panel with usage instructions.
        """

        # Animation sequence for visual interest
        gradient_chars = [".", "·", "•", "●", "•", "·", "."]
        frame = self._animation_frame % len(gradient_chars)

        # Construct informational display
        lines = [
            "",
            "[dim]No active allocations[/dim]",
            "",
            f"[dim cyan]{gradient_chars[frame]}  {gradient_chars[frame]}  {gradient_chars[frame]}[/dim cyan]",
            "",
            "[white]flow run task.yaml[/white]",
            "[dim]or[/dim]",
            "[white]flow dev[/white]",
            "",
        ]

        content = "\n".join(lines)
        return Panel(content, border_style="dim", box=box.ROUNDED, padding=(2, 4))

    def _get_display_status(self, task: Task) -> str:
        """Determine effective task status for display.

        Maps internal states to user-facing status values. Tasks in 'running'
        state without SSH connectivity are displayed as 'starting'.

        Args:
            task: Task object to evaluate.

        Returns:
            str: Display status string.
        """
        if task.status.value == "running" and not task.ssh_host:
            return "starting"
        return task.status.value

    def _format_gpu_elegant(self, instance_type: Optional[str], num_instances: int = 1) -> str:
        """Format GPU instance type for compact display.

        For multi-node clusters, shows total GPU count (e.g., '16×H100' for
        2 nodes with 8xH100 each). This provides immediate clarity on total
        compute resources available.

        Args:
            instance_type: Raw instance type string.
            num_instances: Number of nodes/instances.

        Returns:
            str: Formatted instance specification showing total GPUs.
        """
        from ..utils.gpu_formatter import GPUFormatter

        return GPUFormatter.format_ultra_compact(instance_type, num_instances)

    def _format_time_elegant(self, task: Task) -> str:
        """Format task duration with appropriate time unit.

        Uses progressive units: minutes (<1h), hours (<24h), days (>=24h).

        Args:
            task: Task object with created_at timestamp.

        Returns:
            str: Formatted duration string.
        """
        if not task.created_at:
            return "-"

        now = datetime.now(timezone.utc)
        if task.created_at.tzinfo is None:
            created = task.created_at.replace(tzinfo=timezone.utc)
        else:
            created = task.created_at

        delta = now - created
        hours = delta.total_seconds() / 3600

        if hours < 1:
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes}m"
        elif hours < 24:
            return f"{int(hours)}h"
        else:
            days = int(hours / 24)
            return f"{days}d"

    def _format_time_detailed(self, dt: datetime) -> str:
        """Format datetime as ISO-like string with UTC timezone.

        Args:
            dt: Datetime object to format.

        Returns:
            str: Formatted datetime string.
        """
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

    def _format_duration_detailed(self, task: Task) -> Optional[str]:
        """Calculate and format task execution duration.

        Computes duration from creation to completion (or current time if running).
        Uses appropriate units based on duration magnitude.

        Args:
            task: Task object with temporal metadata.

        Returns:
            Optional[str]: Formatted duration or None if created_at is missing.
        """
        if not task.created_at:
            return None

        now = datetime.now(timezone.utc)
        if task.created_at.tzinfo is None:
            created = task.created_at.replace(tzinfo=timezone.utc)
        else:
            created = task.created_at

        if task.completed_at:
            if task.completed_at.tzinfo is None:
                end = task.completed_at.replace(tzinfo=timezone.utc)
            else:
                end = task.completed_at
        else:
            end = now

        delta = end - created
        hours = delta.total_seconds() / 3600

        if hours < 1:
            minutes = int(delta.total_seconds() / 60)
            seconds = int(delta.total_seconds() % 60)
            return f"{minutes}m {seconds}s"
        elif hours < 24:
            h = int(hours)
            m = int((hours * 60) % 60)
            return f"{h}h {m}m"
        else:
            days = int(hours / 24)
            h = int(hours % 24)
            return f"{days}d {h}h"

    def advance_animation(self):
        """Increment animation frame counter.

        Used for cyclic animations like pulsing status indicators.
        """
        self._animation_frame += 1

    def move_selection(self, direction: int):
        """Update selected task index with bounds checking.

        Args:
            direction: Movement delta (-1 for up, 1 for down).
        """
        if not self.tasks:
            return

        self.selected_index = max(0, min(len(self.tasks) - 1, self.selected_index + direction))
        if 0 <= self.selected_index < len(self.tasks):
            self.selected_task = self.tasks[self.selected_index]

    def toggle_details(self):
        """Toggle visibility of task detail panel.

        Updates show_details flag and selected_task reference.
        """
        if self.tasks and 0 <= self.selected_index < len(self.tasks):
            self.show_details = not self.show_details
            self.selected_task = self.tasks[self.selected_index] if self.show_details else None


class AllocCommand(BaseCommand):
    """GPU resource allocation and monitoring command.

    Provides multiple execution modes for resource visualization:
    - Standard: Single snapshot of current allocations
    - Watch: Continuous monitoring with periodic refresh
    - Interactive: Keyboard-driven navigation (future)
    """

    def __init__(self):
        super().__init__()
        self.renderer = BeautifulTaskRenderer(console)

    @property
    def name(self) -> str:
        return "alloc"

    @property
    def help(self) -> str:
        return "Streamlined GPU allocations (abbreviated `flow status`)"

    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        # @click.option("--interactive", "-i", is_flag=True, help="Interactive mode with keyboard navigation")  # Reserved for future implementation
        @click.option("--watch", "-w", is_flag=True, help="Continuous monitoring with auto-refresh")
        @click.option("--gpus", type=int, help="Request specific GPU count (future)")
        @click.option("--type", "gpu_type", help="Specify GPU model (e.g., h100, a100)")
        @click.option(
            "--refresh-rate",
            default=2.0,
            type=float,
            help="Update interval in seconds (default: 2.0)",
        )
        def alloc(watch: bool, gpus: Optional[int], gpu_type: Optional[str], refresh_rate: float):
            """Streamlined GPU allocation view - abbreviated version of `flow status`.

            Focused display optimized for rapid resource assessment.
            Use `flow status` for comprehensive task details and metrics.

            \b
            Examples:
                flow alloc              # Quick allocation snapshot
                flow alloc --watch      # Live GPU monitoring
                flow alloc --refresh-rate 5  # Custom refresh interval
            """
            self._execute(False, watch, gpus, gpu_type, refresh_rate)  # Interactive mode reserved

        return alloc

    def _execute(
        self,
        interactive: bool,
        watch: bool,
        gpus: Optional[int],
        gpu_type: Optional[str],
        refresh_rate: float,
    ) -> None:
        """Execute allocation command in specified mode.

        Args:
            interactive: Enable keyboard navigation mode.
            watch: Enable continuous monitoring.
            gpus: Requested GPU count (future feature).
            gpu_type: Requested GPU model (future feature).
            refresh_rate: Update interval for watch mode.
        """

        # Allocation features pending implementation
        if gpus or gpu_type:
            console.print("[dim]Allocation request noted. Displaying current resources...[/dim]\n")
            time.sleep(1)

        try:
            flow_client = Flow()

            if interactive:
                self._run_interactive_mode(flow_client)
            elif watch:
                self._run_watch_mode(flow_client, refresh_rate)
            else:
                # Standard mode: single snapshot with progress indicator
                progress = AnimatedEllipsisProgress(
                    console,
                    "Fetching GPU allocations",
                    start_immediately=True,
                )

                with progress:
                    from ..utils.task_fetcher import TaskFetcher

                    fetcher = TaskFetcher(flow_client)
                    tasks = fetcher.fetch_for_display(show_all=False, limit=30)

                    panel = self.renderer.render_allocation_view(tasks)

                console.print(panel)

        except AuthenticationError:
            self.handle_auth_error()
        except Exception as e:
            self.handle_error(str(e))

    def _run_interactive_mode(self, flow_client: Flow) -> None:
        """Execute interactive mode with keyboard-driven navigation.

        Provides vim-style navigation (j/k) and arrow key support for
        task selection and detail viewing.

        Args:
            flow_client: Authenticated Flow API client.
        """

        if not sys.stdin.isatty():
            console.print("[red]Error:[/red] Interactive mode requires a terminal")
            return

        from ..utils.task_fetcher import TaskFetcher

        fetcher = TaskFetcher(flow_client)

        # Get initial tasks
        tasks = fetcher.fetch_for_display(show_all=False, limit=30)

        def get_display():
            """Generate current display state.

            Returns:
                RenderableType: Current task view with selection.
            """
            nonlocal tasks
            return self.renderer.render_interactive_view(tasks)

        def get_key():
            """Read single keystroke from terminal.

            Handles multi-byte sequences for arrow keys.

            Returns:
                str: Key identifier or character.
            """
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)

                # Parse ANSI escape sequences for arrow keys
                if ch == "\x1b":
                    ch2 = sys.stdin.read(1)
                    if ch2 == "[":
                        ch3 = sys.stdin.read(1)
                        if ch3 == "A":
                            return "up"
                        elif ch3 == "B":
                            return "down"
                return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        try:
            with Live(
                get_display(),
                console=console,
                refresh_per_second=10,  # Smooth for keyboard nav
                screen=True,
                transient=True,
            ) as live:
                while True:
                    key = get_key()

                    if key in ["q", "\x03"]:  # Quit on 'q' or Ctrl+C
                        break
                    elif key in ["up", "k"]:
                        self.renderer.move_selection(-1)
                        live.update(get_display())
                    elif key in ["down", "j"]:
                        self.renderer.move_selection(1)
                        live.update(get_display())
                    elif key in ["\r", "\n"]:  # Toggle details on Enter
                        self.renderer.toggle_details()
                        live.update(get_display())
                    elif key == "r":  # Manual refresh
                        tasks = fetcher.fetch_for_display(show_all=False, limit=30)
                        self.renderer.tasks = tasks
                        live.update(get_display())

            console.clear()
            console.print("[dim]Interactive mode ended[/dim]")

        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted[/dim]")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")

    def _run_watch_mode(self, flow_client: Flow, refresh_rate: float) -> None:
        """Execute continuous monitoring mode with periodic updates.

        Refreshes task display at specified intervals with animated
        status indicators for active tasks.

        Args:
            flow_client: Authenticated Flow API client.
            refresh_rate: Seconds between display updates.
        """

        if not sys.stdin.isatty():
            console.print("[red]Error:[/red] Watch mode requires an interactive terminal")
            return

        from ..utils.task_fetcher import TaskFetcher

        fetcher = TaskFetcher(flow_client)

        def get_display():
            """Generate display with incremented animation frame.

            Returns:
                Panel: Current task allocation view or error panel.
            """
            try:
                tasks = fetcher.fetch_for_display(show_all=False, limit=30)
                self.renderer.advance_animation()
                return self.renderer.render_allocation_view(tasks)
            except Exception as e:
                return Panel(f"[red]Error: {e}[/red]", border_style="red")

        try:
            # Initial data fetch with progress indicator
            with AnimatedEllipsisProgress(
                console,
                "Starting allocation monitor",
                start_immediately=True,
            ) as progress:
                initial_display = get_display()

            with Live(
                initial_display,
                console=console,
                refresh_per_second=2,  # Animation frame rate
                screen=True,
                transient=True,
            ) as live:
                while True:
                    try:
                        live.update(get_display())
                        time.sleep(refresh_rate)
                    except KeyboardInterrupt:
                        break

            console.clear()
            console.print("[dim]Allocation monitor stopped[/dim]")

        except KeyboardInterrupt:
            console.print("\n[dim]Stopped[/dim]")


# Module-level command instance for CLI registration
command = AllocCommand()
