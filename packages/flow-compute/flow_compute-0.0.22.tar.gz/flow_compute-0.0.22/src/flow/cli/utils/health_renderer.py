"""Health status rendering utilities for CLI output."""

from typing import Any

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

from flow.api.health_models import (
    FleetHealthSummary,
    HealthStatus,
    NodeHealthSnapshot,
)
from flow.cli.utils.gpu_formatter import GPUFormatter
from flow.cli.utils.table_styles import create_flow_table, wrap_table_in_panel
from flow.cli.utils.terminal_adapter import TerminalAdapter, TerminalBreakpoints
from flow.cli.utils.theme_manager import theme_manager
from flow.cli.utils.time_formatter import TimeFormatter


class HealthRenderer:
    """Renders health status information for Flow tasks."""

    def __init__(self, console: Console | None = None):
        """Initialize renderer with optional console override."""
        self.console = console or theme_manager.create_console()
        self.terminal = TerminalAdapter()
        self.time_fmt = TimeFormatter()
        self.gpu_fmt = GPUFormatter()

    def render_fleet_summary(self, summary: FleetHealthSummary) -> None:
        """Render fleet-wide health summary with professional styling.

        Args:
            summary: Fleet health summary data
        """
        # Create summary panel
        panel_content = self._create_summary_content(summary)

        # Determine panel style based on health
        border_style = self._get_health_style(summary)

        panel = Panel(
            panel_content,
            title=f"[bold {theme_manager.get_color('accent')}]Fleet Health Summary[/bold {theme_manager.get_color('accent')}]",
            title_align="center",
            border_style=border_style,
            box=box.ROUNDED,
            padding=(1, 2),
        )

        self.console.print(panel)

        # Show critical issues if any
        if summary.has_critical_issues:
            self._render_critical_issues(summary)

    def render_node_health_table(
        self,
        nodes: list[NodeHealthSnapshot],
        title: str | None = None,
        show_details: bool = False,
    ) -> None:
        """Render health status for multiple nodes.

        Args:
            nodes: List of node health snapshots
            title: Optional table title
            show_details: Whether to show detailed metrics
        """
        if not nodes:
            return

        # Get responsive layout
        width = self.terminal.get_terminal_width()
        layout = self.terminal.get_responsive_layout(width)

        # Create table (no borders when wrapped in panel)
        if title:
            # Simpler table for panel wrapping
            table = create_flow_table(show_borders=False, padding=1, expand=False)
        else:
            table = self._create_health_table(nodes, layout, show_details)

        # Add columns if creating simple table
        if title:
            self._add_health_columns(table, width)

        # Add rows
        for node in sorted(nodes, key=lambda n: n.task_name):
            self._add_health_row(table, node, width, show_details)

        # Wrap in panel with centered title (matches task renderer style)
        if title:
            wrap_table_in_panel(table, title, self.console)
        else:
            self.console.print(table)

    def render_live_table(self, tasks: list[Any], snapshots: list[NodeHealthSnapshot]) -> Table:
        """Create a live-updating table for health display.

        This replicates the inline table previously built in the command layer,
        but uses shared theming and proportions.
        """
        table = create_flow_table(
            title="Node GPU Monitoring & Health Status",
            show_borders=True,
            padding=1,
            expand=False,
        )

        # Columns: compact, set explicit widths and prevent stretching
        from flow.cli.utils.table_styles import add_centered_column

        table.add_column(
            "Node",
            style=theme_manager.get_color("task.name"),
            no_wrap=True,
            min_width=18,
            max_width=24,
            overflow="ellipsis",
        )
        add_centered_column(table, "Monitor", width=7)
        add_centered_column(table, "GPUs", width=8)
        add_centered_column(table, "Temp", width=6)
        add_centered_column(table, "Usage", width=7)
        add_centered_column(table, "Memory", width=7)
        table.add_column(
            "Status",
            style=theme_manager.get_color("table.row.dim"),
            no_wrap=True,
            min_width=10,
            max_width=14,
            overflow="fold",
        )

        # Add rows for completed checks
        checked_ids = {s.task_id for s in snapshots}
        for snapshot in snapshots:
            self._add_live_table_row(table, snapshot)

        # Spinner for pending rows
        import time

        spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        frame_idx = int(time.time() * 10) % len(spinner_frames)
        spinner = spinner_frames[frame_idx]

        for task in tasks:
            if task.task_id not in checked_ids:
                node_label = getattr(task, "name", None) or task.task_id[:12]
                table.add_row(
                    node_label,
                    f"[yellow]{spinner}[/yellow]",
                    "[dim]—[/dim]",
                    "[dim]—[/dim]",
                    "[dim]—[/dim]",
                    "[dim]—[/dim]",
                    "[dim italic]Checking...[/dim italic]",
                )

        return table

    # Public wrapper to add a completed health row to a live table
    def add_live_table_row(self, table: Table, snapshot: NodeHealthSnapshot) -> None:
        self._add_live_table_row(table, snapshot)

    def _add_live_table_row(self, table: Table, snapshot: NodeHealthSnapshot) -> None:
        """Add a completed health check row to the live table (shared)."""
        # Monitoring
        if snapshot.gpud_healthy:
            monitoring = "[green]✓[/green]"
        elif snapshot.health_status == HealthStatus.UNKNOWN:
            note = str((snapshot.machine_info or {}).get("note", "")).lower()
            monitoring = "[dim]Legacy[/dim]" if "legacy" in note else "[yellow]None[/yellow]"
        else:
            monitoring = "[red]✗[/red]"

        # GPU count: show cluster total GPUs when multi-node info is available
        try:
            nodes = int((snapshot.machine_info or {}).get("nodes", 1) or 1)
        except Exception:
            nodes = 1
        gpn = len(snapshot.gpu_metrics) if snapshot.gpu_metrics else 0
        if gpn == 0:
            try:
                gpn = int((snapshot.machine_info or {}).get("gpus_per_node", 0) or 0)
            except Exception:
                gpn = 0
        total_gpus = nodes * gpn
        if total_gpus > 0:
            gpu_count = f"[accent]{total_gpus}[/accent]"
        elif snapshot.gpud_healthy:
            gpu_count = "[accent]0[/accent]"
        else:
            gpu_count = "[dim]—[/dim]"

        # Temp
        if snapshot.gpu_metrics:
            avg_temp = sum(g.temperature_c for g in snapshot.gpu_metrics) / len(
                snapshot.gpu_metrics
            )
            temp_color = self._get_temperature_color(avg_temp)
            temp = f"[{temp_color}]{avg_temp:.0f}°C[/{temp_color}]"
        else:
            temp = "[dim]—[/dim]"

        # Usage
        if snapshot.gpu_metrics:
            avg_usage = sum(g.gpu_utilization_pct for g in snapshot.gpu_metrics) / len(
                snapshot.gpu_metrics
            )
            usage_color = self._get_utilization_color(avg_usage)
            usage = f"[{usage_color}]{avg_usage:.0f}%[/{usage_color}]"
        else:
            usage = "[dim]—[/dim]"

        # Memory
        if snapshot.gpu_metrics:
            avg_mem = sum(g.memory_utilization_pct for g in snapshot.gpu_metrics) / len(
                snapshot.gpu_metrics
            )
            mem_color = self._get_utilization_color(avg_mem)
            memory = f"[{mem_color}]{avg_mem:.0f}%[/{mem_color}]"
        else:
            memory = "[dim]—[/dim]"

        # Status
        if not snapshot.gpud_healthy:
            note = str((snapshot.machine_info or {}).get("note", "")).lower()
            if "legacy" in note:
                status = "[dim]Legacy node[/dim]"
            elif "not installed" in note:
                from flow.cli.utils.hyperlink_support import (
                    hyperlink_support,  # local import to avoid cycles
                )

                install_url = "https://pkg.gpud.dev/install.sh"
                link = hyperlink_support.create_link("Install GPUd →", install_url)
                status = f"[yellow]{link}[/yellow]"
            else:
                status = "[red]Connection failed[/red]"
        elif snapshot.health_status == HealthStatus.HEALTHY:
            status = "[green]● Healthy[/green]"
        elif snapshot.health_status == HealthStatus.DEGRADED:
            issues = []
            for gpu in snapshot.gpu_metrics:
                if gpu.temperature_c >= 75:
                    issues.append("Hot")
                if gpu.memory_utilization_pct >= 90:
                    issues.append("Mem full")
            status = f"[yellow]⚠ {' & '.join(issues[:1]) if issues else 'Degraded'}[/yellow]"
        else:
            status = "[red]● Critical[/red]"

        table.add_row(
            snapshot.task_name or snapshot.task_id[:12],
            monitoring,
            gpu_count,
            temp,
            usage,
            memory,
            status,
        )

    def render_node_details(self, node: NodeHealthSnapshot) -> None:
        """Render detailed health information for a single node.

        Args:
            node: Node health snapshot
        """
        # Header panel
        header = self._create_node_header(node)
        self.console.print(header)

        # Health score breakdown (if available)
        try:
            breakdown = (node.machine_info or {}).get("health_score_breakdown")
            if breakdown:
                self._render_health_breakdown(node)
        except Exception:
            pass

        # GPU metrics table
        if node.gpu_metrics:
            self._render_gpu_metrics(node)

        # System metrics
        if node.system_metrics:
            self._render_system_metrics(node)

        # Health states
        if node.health_states:
            self._render_health_states(node)

        # Recent events
        if node.events:
            self._render_recent_events(node)

    def render_checking_health(self, task_names: list[str]) -> Progress:
        """Render progress indicator for health checking operation.

        Args:
            task_names: List of task names being checked

        Returns:
            Progress object for updating
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        )

        # Add task for each node
        for name in task_names:
            progress.add_task(f"Checking health: {name}", total=None)

        return progress

    def _create_summary_content(self, summary: FleetHealthSummary) -> Table:
        """Create summary content table."""
        table = Table(show_header=False, box=None, padding=0)
        table.add_column(justify="left", no_wrap=True)
        table.add_column(justify="right")

        # Health percentage with color
        health_pct = summary.health_percentage
        # Health percentage is higher-is-better
        health_color = self._get_score_color(health_pct)

        table.add_row(
            "[bold]Overall Health[/bold]", f"[{health_color}]{health_pct:.1f}%[/{health_color}]"
        )

        # Node status
        table.add_row(
            "[bold]Nodes[/bold]", f"{summary.healthy_nodes}/{summary.total_nodes} healthy"
        )

        if summary.degraded_nodes > 0:
            table.add_row("", f"[yellow]{summary.degraded_nodes} degraded[/yellow]")

        if summary.critical_nodes > 0:
            table.add_row("", f"[red]{summary.critical_nodes} critical[/red]")

        # GPU status
        table.add_row("[bold]GPUs[/bold]", f"{summary.healthy_gpus}/{summary.total_gpus} healthy")

        # Average metrics
        table.add_row("[bold]Avg GPU Temp[/bold]", f"{summary.avg_gpu_temperature:.1f}°C")

        table.add_row("[bold]Avg GPU Usage[/bold]", f"{summary.avg_gpu_utilization:.1f}%")

        table.add_row("[bold]Avg Memory Usage[/bold]", f"{summary.avg_gpu_memory_utilization:.1f}%")

        return table

    def _create_health_table(
        self,
        nodes: list[NodeHealthSnapshot],
        layout: dict[str, Any],
        show_details: bool,
    ) -> Table:
        """Create health status table with responsive columns."""
        table = create_flow_table(show_borders=True, padding=1, expand=False)

        # Base columns
        table.add_column(
            "Task",
            style=theme_manager.get_color("task.name"),
            no_wrap=True,
            header_style=theme_manager.get_color("table.header"),
            justify="left",
            min_width=20,
            max_width=48,
            overflow="ellipsis",
        )
        table.add_column(
            "Status", justify="center", header_style=theme_manager.get_color("table.header")
        )
        table.add_column(
            "Health", justify="center", header_style=theme_manager.get_color("table.header")
        )

        # Responsive columns based on width
        width = self.terminal.get_terminal_width()

        if width >= TerminalBreakpoints.COMPACT:
            table.add_column(
                "GPUs",
                justify="center",
                header_style=theme_manager.get_color("table.header"),
                width=6,
                no_wrap=True,
            )
            table.add_column(
                "GPU Temp",
                justify="center",
                header_style=theme_manager.get_color("table.header"),
                width=7,
                no_wrap=True,
            )
            table.add_column(
                "GPU Usage",
                justify="center",
                header_style=theme_manager.get_color("table.header"),
                width=7,
                no_wrap=True,
            )

        if width >= TerminalBreakpoints.NORMAL:
            table.add_column(
                "Memory",
                justify="center",
                header_style=theme_manager.get_color("table.header"),
                width=7,
                no_wrap=True,
            )
            table.add_column(
                "Issues",
                justify="center",
                header_style=theme_manager.get_color("table.header"),
                width=6,
                no_wrap=True,
            )

        if width >= TerminalBreakpoints.WIDE:
            table.add_column(
                "Last Check",
                justify="center",
                header_style=theme_manager.get_color("table.header"),
                style=theme_manager.get_color("task.time"),
                width=12,
                no_wrap=True,
            )

        # Add rows
        for node in sorted(nodes, key=lambda n: n.task_name):
            self._add_health_row(table, node, width, show_details)

        return table

    def _add_health_columns(self, table: Table, width: int) -> None:
        """Add columns to health table based on terminal width."""
        # Base columns
        table.add_column(
            "Task",
            style=theme_manager.get_color("task.name"),
            no_wrap=True,
            header_style=theme_manager.get_color("table.header"),
            justify="left",
            min_width=20,
            max_width=48,
            overflow="ellipsis",
        )
        table.add_column(
            "Status", justify="center", header_style=theme_manager.get_color("table.header")
        )
        table.add_column(
            "Health", justify="center", header_style=theme_manager.get_color("table.header")
        )

        # Responsive columns based on width
        if width >= TerminalBreakpoints.COMPACT:
            table.add_column(
                "GPUs",
                justify="center",
                header_style=theme_manager.get_color("table.header"),
                width=6,
                no_wrap=True,
            )
            table.add_column(
                "GPU Temp",
                justify="center",
                header_style=theme_manager.get_color("table.header"),
                width=7,
                no_wrap=True,
            )
            table.add_column(
                "GPU Usage",
                justify="center",
                header_style=theme_manager.get_color("table.header"),
                width=7,
                no_wrap=True,
            )

        if width >= TerminalBreakpoints.NORMAL:
            table.add_column(
                "Memory",
                justify="center",
                header_style=theme_manager.get_color("table.header"),
                width=7,
                no_wrap=True,
            )
            table.add_column(
                "Issues",
                justify="center",
                header_style=theme_manager.get_color("table.header"),
                width=6,
                no_wrap=True,
            )

        if width >= TerminalBreakpoints.WIDE:
            table.add_column(
                "Last Check",
                justify="center",
                header_style=theme_manager.get_color("table.header"),
                style=theme_manager.get_color("task.time"),
                width=12,
                no_wrap=True,
            )

    def _add_health_row(
        self,
        table: Table,
        node: NodeHealthSnapshot,
        width: int,
        show_details: bool,
    ) -> None:
        """Add a health status row to the table."""
        # Base columns
        task_name = Text(node.task_name)

        # Status with color
        status_text, status_style = self._format_health_status(node.health_status)
        status = Text(status_text, style=status_style)

        # Health score (higher is better => green)
        score_color = self._get_score_color(node.health_score * 100)
        health = Text(f"{node.health_score * 100:.0f}%", style=score_color)

        row = [task_name, status, health]

        # Responsive columns
        if width >= TerminalBreakpoints.COMPACT:
            # GPU count
            gpu_count = str(node.gpu_count) if node.gpu_count > 0 else "-"
            row.append(gpu_count)

            # Average GPU temperature
            if node.gpu_metrics:
                avg_temp = sum(g.temperature_c for g in node.gpu_metrics) / len(node.gpu_metrics)
                temp_color = self._get_temperature_color(avg_temp)
                row.append(Text(f"{avg_temp:.0f}°C", style=temp_color))
            else:
                row.append("-")

            # Average GPU utilization
            if node.gpu_metrics:
                avg_util = sum(g.gpu_utilization_pct for g in node.gpu_metrics) / len(
                    node.gpu_metrics
                )
                util_color = self._get_utilization_color(avg_util)
                row.append(Text(f"{avg_util:.0f}%", style=util_color))
            else:
                row.append("-")

        if width >= TerminalBreakpoints.NORMAL:
            # Memory usage
            if node.gpu_metrics:
                avg_mem = sum(g.memory_utilization_pct for g in node.gpu_metrics) / len(
                    node.gpu_metrics
                )
                mem_color = self._get_utilization_color(avg_mem)
                row.append(Text(f"{avg_mem:.0f}%", style=mem_color))
            else:
                row.append("-")

            # Issue count
            issue_count = len(node.unhealthy_components)
            if issue_count > 0:
                row.append(Text(str(issue_count), style="yellow"))
            else:
                row.append(Text("0", style="green"))

        if width >= TerminalBreakpoints.WIDE:
            # Last check time
            time_str = self.time_fmt.format_time_ago(node.timestamp)
            row.append(time_str)

        table.add_row(*row)

    def _render_gpu_metrics(self, node: NodeHealthSnapshot) -> None:
        """Render GPU metrics table."""
        table = create_flow_table(title="GPU Metrics", show_borders=True, padding=1, expand=False)

        table.add_column("GPU", style="white", header_style="bold white", justify="center")
        table.add_column("Model", style="dim white", header_style="bold white", justify="center")
        table.add_column("Temp", justify="center", header_style="bold white")
        table.add_column("Power", justify="center", header_style="bold white")
        table.add_column("Usage", justify="center", header_style="bold white")
        table.add_column("Memory", justify="center", header_style="bold white")
        table.add_column("Clock", justify="center", header_style="bold white")

        for gpu in node.gpu_metrics:
            # Temperature with color
            temp_color = self._get_temperature_color(gpu.temperature_c)
            temp = Text(f"{gpu.temperature_c:.0f}°C", style=temp_color)

            # Power usage
            power = f"{gpu.power_draw_w:.0f}W/{gpu.power_limit_w:.0f}W"

            # GPU utilization
            util_color = self._get_utilization_color(gpu.gpu_utilization_pct)
            usage = Text(f"{gpu.gpu_utilization_pct:.0f}%", style=util_color)

            # Memory usage
            mem_pct = gpu.memory_utilization_pct
            mem_color = self._get_utilization_color(mem_pct)
            memory = Text(
                f"{gpu.memory_used_mb}/{gpu.memory_total_mb}MB ({mem_pct:.0f}%)", style=mem_color
            )

            # Clock speed
            clock = f"{gpu.clock_mhz}MHz"
            if gpu.is_throttling:
                clock = Text(clock + " (throttled)", style="yellow")

            table.add_row(
                f"GPU {gpu.gpu_index}",
                gpu.name,
                temp,
                power,
                usage,
                memory,
                clock,
            )

        self.console.print(table)

    def _render_system_metrics(self, node: NodeHealthSnapshot) -> None:
        """Render system metrics panel."""
        if not node.system_metrics:
            return

        metrics = node.system_metrics

        table = Table(show_header=False, box=None, padding=0)

        # CPU usage
        cpu_color = self._get_utilization_color(metrics.cpu_usage_pct)
        table.add_row(
            "[bold]CPU Usage[/bold]", f"[{cpu_color}]{metrics.cpu_usage_pct:.1f}%[/{cpu_color}]"
        )

        # Memory usage
        mem_pct = metrics.memory_utilization_pct
        mem_color = self._get_utilization_color(mem_pct)
        table.add_row(
            "[bold]Memory[/bold]",
            f"[{mem_color}]{metrics.memory_used_gb:.1f}/{metrics.memory_total_gb:.1f}GB ({mem_pct:.0f}%)[/{mem_color}]",
        )

        # Disk usage
        disk_color = self._get_utilization_color(metrics.disk_usage_pct)
        table.add_row(
            "[bold]Disk Usage[/bold]", f"[{disk_color}]{metrics.disk_usage_pct:.1f}%[/{disk_color}]"
        )

        # Load average
        if metrics.load_average:
            table.add_row(
                "[bold]Load Average[/bold]",
                f"{metrics.load_average[0]:.2f}, {metrics.load_average[1]:.2f}, {metrics.load_average[2]:.2f}",
            )

        panel = Panel(
            table,
            title=f"[bold {theme_manager.get_color('accent')}]System Metrics[/bold {theme_manager.get_color('accent')}]",
            title_align="center",
            border_style=theme_manager.get_color("table.border"),
            box=box.ROUNDED,
            padding=(1, 2),
        )

        self.console.print(panel)

    def _render_health_breakdown(self, node: NodeHealthSnapshot) -> None:
        """Render per-component health score breakdown if provided."""
        breakdown = (node.machine_info or {}).get("health_score_breakdown")
        if not breakdown:
            return

        def style_for_score(value: float) -> str:
            if value >= 0.8:
                return "green"
            if value >= 0.6:
                return "yellow"
            return "red"

        table = Table(show_header=False, box=None, padding=0)
        table.add_column("Component", style="white")
        table.add_column("Score", justify="right")

        order = ["gpu", "memory", "interconnect", "host", "software", "confidence"]
        labels = {
            "gpu": "GPU",
            "memory": "Memory",
            "interconnect": "Interconnect",
            "host": "Host",
            "software": "Software",
            "confidence": "Confidence",
        }

        for key in order:
            if key in breakdown:
                val = breakdown.get(key, 0)
                try:
                    val_f = float(val)
                except Exception:
                    continue
                color = style_for_score(val_f)
                pct = f"{val_f * 100:.0f}%"
                table.add_row(labels.get(key, key.title()), f"[{color}]{pct}[/{color}]")

        panel = Panel(
            table,
            title=f"[bold {theme_manager.get_color('accent')}]Health Breakdown[/bold {theme_manager.get_color('accent')}]",
            title_align="center",
            border_style=theme_manager.get_color("table.border"),
            box=box.ROUNDED,
            padding=(1, 2),
        )

        self.console.print(panel)

    def _render_health_states(self, node: NodeHealthSnapshot) -> None:
        """Render health states table."""
        if not node.health_states:
            return

        table = create_flow_table(
            title="Component Health States", show_borders=True, padding=1, expand=False
        )

        table.add_column("Component", style="white", header_style="bold white", justify="center")
        table.add_column("Health", justify="center", header_style="bold white")
        table.add_column("Message", header_style="bold white")

        for state in node.health_states:
            health_icon = self._get_health_icon(state.health)
            table.add_row(
                state.component,
                health_icon,
                state.message,
            )

        self.console.print(table)

    def _render_recent_events(self, node: NodeHealthSnapshot) -> None:
        """Render recent events table."""
        if not node.events:
            return

        # Only show last 10 events
        recent_events = sorted(node.events, key=lambda e: e.timestamp, reverse=True)[:10]

        table = create_flow_table(title="Recent Events", show_borders=True, padding=1, expand=False)

        table.add_column("Time", style="dim white", header_style="bold white", justify="center")
        table.add_column("Level", justify="center", header_style="bold white")
        table.add_column("Component", style="white", header_style="bold white", justify="center")
        table.add_column("Message", header_style="bold white")

        for event in recent_events:
            # Level with color
            level_style = {
                "error": "red",
                "warning": "yellow",
                "info": "blue",
            }.get(event.level, "white")

            level = Text(event.level.upper(), style=level_style)

            # Relative time
            time_str = self.time_fmt.format_time_ago(event.timestamp)

            table.add_row(
                time_str,
                level,
                event.component,
                event.message,
            )

        self.console.print(table)

    def _render_critical_issues(self, summary: FleetHealthSummary) -> None:
        """Render critical issues panel."""
        if not summary.critical_issues:
            return

        table = create_flow_table(show_borders=False, padding=1, expand=False)

        table.add_column("Node", style="cyan")
        table.add_column("Component", style="yellow")
        table.add_column("Issue")

        for issue in summary.critical_issues[:10]:  # Limit to 10
            table.add_row(
                issue.get("task_name", "Unknown"),
                issue.get("component", "Unknown"),
                issue.get("message", "Unknown issue"),
            )

        # Wrap in panel with centered title
        panel = Panel(
            table,
            title=f"[bold {theme_manager.get_color('error')}]Critical Issues[/bold {theme_manager.get_color('error')}]",
            title_align="center",
            border_style=theme_manager.get_color("error"),
            box=box.ROUNDED,
            padding=(0, 1),
        )

        self.console.print(panel)

    def _create_node_header(self, node: NodeHealthSnapshot) -> Panel:
        """Create header panel for node details."""
        # Build header content
        lines = []

        # Task info
        lines.append(f"[bold accent]Task:[/bold accent] {node.task_name} ({node.task_id})")
        lines.append(f"[bold]Instance:[/bold] {node.instance_id} ({node.instance_type})")

        # Health status
        status_text, status_style = self._format_health_status(node.health_status)
        score_color = self._get_score_color(node.health_score * 100)
        lines.append(
            f"[bold]Health:[/bold] [{status_style}]{status_text}[/{status_style}] "
            f"[{score_color}]{node.health_score * 100:.0f}%[/{score_color}]"
        )

        # GPUd status
        gpud_status = "✓ Running" if node.gpud_healthy else "✗ Not Running"
        gpud_style = "green" if node.gpud_healthy else "red"
        lines.append(f"[bold]GPUd:[/bold] [{gpud_style}]{gpud_status}[/{gpud_style}]")

        if node.gpud_version:
            lines.append(f"[bold]GPUd Version:[/bold] {node.gpud_version}")

        # Last updated
        lines.append(f"[bold]Last Updated:[/bold] {self.time_fmt.format_time_ago(node.timestamp)}")

        content = "\n".join(lines)

        # Determine border style
        border_style = self._get_health_style_for_status(node.health_status)

        return Panel(
            content,
            title=f"[bold {theme_manager.get_color('accent')}]Node Health Details[/bold {theme_manager.get_color('accent')}]",
            title_align="center",
            border_style=border_style,
            box=box.ROUNDED,
            padding=(1, 2),
        )

    def _format_health_status(self, status: HealthStatus) -> tuple[str, str]:
        """Format health status with appropriate icon and color."""
        status_map = {
            HealthStatus.HEALTHY: ("● Healthy", "green"),
            HealthStatus.DEGRADED: ("● Degraded", "yellow"),
            HealthStatus.CRITICAL: ("● Critical", "red"),
            HealthStatus.UNKNOWN: ("● Unknown", "dim"),
        }
        return status_map.get(status, ("● Unknown", "dim"))

    def _get_health_icon(self, health: str) -> Text:
        """Get health icon with color."""
        icon_map = {
            "healthy": Text("✓", style="green"),
            "unhealthy": Text("✗", style="red"),
            "degraded": Text("!", style="yellow"),
            "unknown": Text("?", style="dim"),
        }
        return icon_map.get(health.lower(), Text("?", style="dim"))

    def _get_utilization_color(self, percentage: float) -> str:
        """Color for higher-is-worse utilization metrics (e.g., temp, usage)."""
        if percentage >= 90:
            return "red"
        elif percentage >= 75:
            return "yellow"
        elif percentage >= 50:
            return "white"
        else:
            return "green"

    def _get_score_color(self, percentage: float) -> str:
        """Color for higher-is-better scores (e.g., health score)."""
        if percentage >= 90:
            return "green"
        elif percentage >= 75:
            return "white"
        elif percentage >= 50:
            return "yellow"
        else:
            return "red"

    def _get_temperature_color(self, temp_c: float) -> str:
        """Get color based on temperature."""
        if temp_c >= 85:
            return "red"
        elif temp_c >= 75:
            return "yellow"
        elif temp_c >= 65:
            return "white"
        else:
            return "green"

    def _get_health_style(self, summary: FleetHealthSummary) -> str:
        """Get border style based on fleet health."""
        if summary.critical_nodes > 0:
            return "red"
        elif summary.degraded_nodes > 0:
            return "yellow"
        else:
            return "green"

    def _get_health_style_for_status(self, status: HealthStatus) -> str:
        """Get border style based on health status."""
        return {
            HealthStatus.HEALTHY: "green",
            HealthStatus.DEGRADED: "yellow",
            HealthStatus.CRITICAL: "red",
            HealthStatus.UNKNOWN: "dim",
        }.get(status, "dim")
