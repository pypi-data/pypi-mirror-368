"""Health status rendering utilities for CLI output."""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from rich import box
from rich.align import Align
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

from .gpu_formatter import GPUFormatter
from .terminal_adapter import TerminalAdapter, TerminalBreakpoints
from .time_formatter import TimeFormatter


class HealthRenderer:
    """Renders health status information for Flow tasks."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize renderer with optional console override."""
        self.console = console or Console()
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
            title="[bold cyan]Fleet Health Summary[/bold cyan]",
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
        nodes: List[NodeHealthSnapshot],
        title: Optional[str] = None,
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
            table = Table(
                box=None,
                show_header=True,
                header_style="bold",
                expand=False,
            )
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
            panel = Panel(
                table,
                title=f"[bold cyan]{title}[/bold cyan]",
                title_align="center",
                border_style="cyan",
                padding=(1, 2),
            )
            self.console.print(panel)
        else:
            self.console.print(table)

    def render_node_details(self, node: NodeHealthSnapshot) -> None:
        """Render detailed health information for a single node.

        Args:
            node: Node health snapshot
        """
        # Header panel
        header = self._create_node_header(node)
        self.console.print(header)

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

    def render_checking_health(self, task_names: List[str]) -> Progress:
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
        health_color = self._get_percentage_color(health_pct)

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
        nodes: List[NodeHealthSnapshot],
        layout: Dict[str, Any],
        show_details: bool,
    ) -> Table:
        """Create health status table with responsive columns."""
        table = Table(
            box=box.ROUNDED,
            show_header=True,
            header_style="bold",
            border_style="cyan",
            title_style="bold cyan",
            expand=False,
        )

        # Base columns
        table.add_column(
            "Task", style="white", no_wrap=True, header_style="bold white", justify="center"
        )
        table.add_column("Status", justify="center", header_style="bold white")
        table.add_column("Health", justify="center", header_style="bold white")

        # Responsive columns based on width
        width = self.terminal.get_terminal_width()

        if width >= TerminalBreakpoints.COMPACT:
            table.add_column("GPUs", justify="center", header_style="bold white")
            table.add_column("GPU Temp", justify="center", header_style="bold white")
            table.add_column("GPU Usage", justify="center", header_style="bold white")

        if width >= TerminalBreakpoints.NORMAL:
            table.add_column("Memory", justify="center", header_style="bold white")
            table.add_column("Issues", justify="center", header_style="bold white")

        if width >= TerminalBreakpoints.WIDE:
            table.add_column(
                "Last Check", justify="center", header_style="bold white", style="dim white"
            )

        # Add rows
        for node in sorted(nodes, key=lambda n: n.task_name):
            self._add_health_row(table, node, width, show_details)

        return table

    def _add_health_columns(self, table: Table, width: int) -> None:
        """Add columns to health table based on terminal width."""
        # Base columns
        table.add_column(
            "Task", style="white", no_wrap=True, header_style="bold white", justify="center"
        )
        table.add_column("Status", justify="center", header_style="bold white")
        table.add_column("Health", justify="center", header_style="bold white")

        # Responsive columns based on width
        if width >= TerminalBreakpoints.COMPACT:
            table.add_column("GPUs", justify="center", header_style="bold white")
            table.add_column("GPU Temp", justify="center", header_style="bold white")
            table.add_column("GPU Usage", justify="center", header_style="bold white")

        if width >= TerminalBreakpoints.NORMAL:
            table.add_column("Memory", justify="center", header_style="bold white")
            table.add_column("Issues", justify="center", header_style="bold white")

        if width >= TerminalBreakpoints.WIDE:
            table.add_column(
                "Last Check", justify="center", header_style="bold white", style="dim white"
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

        # Health score
        score_color = self._get_percentage_color(node.health_score * 100)
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
                util_color = self._get_percentage_color(avg_util)
                row.append(Text(f"{avg_util:.0f}%", style=util_color))
            else:
                row.append("-")

        if width >= TerminalBreakpoints.NORMAL:
            # Memory usage
            if node.gpu_metrics:
                avg_mem = sum(g.memory_utilization_pct for g in node.gpu_metrics) / len(
                    node.gpu_metrics
                )
                mem_color = self._get_percentage_color(avg_mem)
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
        table = Table(
            title="[bold cyan]GPU Metrics[/bold cyan]",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold",
            border_style="cyan",
            title_style="bold cyan",
        )

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
            util_color = self._get_percentage_color(gpu.gpu_utilization_pct)
            usage = Text(f"{gpu.gpu_utilization_pct:.0f}%", style=util_color)

            # Memory usage
            mem_pct = gpu.memory_utilization_pct
            mem_color = self._get_percentage_color(mem_pct)
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
        cpu_color = self._get_percentage_color(metrics.cpu_usage_pct)
        table.add_row(
            "[bold]CPU Usage[/bold]", f"[{cpu_color}]{metrics.cpu_usage_pct:.1f}%[/{cpu_color}]"
        )

        # Memory usage
        mem_pct = metrics.memory_utilization_pct
        mem_color = self._get_percentage_color(mem_pct)
        table.add_row(
            "[bold]Memory[/bold]",
            f"[{mem_color}]{metrics.memory_used_gb:.1f}/{metrics.memory_total_gb:.1f}GB ({mem_pct:.0f}%)[/{mem_color}]",
        )

        # Disk usage
        disk_color = self._get_percentage_color(metrics.disk_usage_pct)
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
            title="[bold cyan]System Metrics[/bold cyan]",
            title_align="center",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )

        self.console.print(panel)

    def _render_health_states(self, node: NodeHealthSnapshot) -> None:
        """Render health states table."""
        if not node.health_states:
            return

        table = Table(
            title="[bold cyan]Component Health States[/bold cyan]",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold",
            border_style="cyan",
            title_style="bold cyan",
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

        table = Table(
            title="[bold cyan]Recent Events[/bold cyan]",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold",
            border_style="cyan",
            title_style="bold cyan",
        )

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

        table = Table(
            box=None,
            show_header=True,
            header_style="bold",
            expand=False,
        )

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
            title="[bold red]Critical Issues[/bold red]",
            title_align="center",
            border_style="red",
            box=box.ROUNDED,
            padding=(0, 1),
        )

        self.console.print(panel)

    def _create_node_header(self, node: NodeHealthSnapshot) -> Panel:
        """Create header panel for node details."""
        # Build header content
        lines = []

        # Task info
        lines.append(f"[bold cyan]Task:[/bold cyan] {node.task_name} ({node.task_id})")
        lines.append(f"[bold]Instance:[/bold] {node.instance_id} ({node.instance_type})")

        # Health status
        status_text, status_style = self._format_health_status(node.health_status)
        score_color = self._get_percentage_color(node.health_score * 100)
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
            title="[bold cyan]Node Health Details[/bold cyan]",
            title_align="center",
            border_style=border_style,
            box=box.ROUNDED,
            padding=(1, 2),
        )

    def _format_health_status(self, status: HealthStatus) -> Tuple[str, str]:
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

    def _get_percentage_color(self, percentage: float) -> str:
        """Get color based on percentage value."""
        if percentage >= 90:
            return "red"
        elif percentage >= 75:
            return "yellow"
        elif percentage >= 50:
            return "white"
        else:
            return "green"

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
