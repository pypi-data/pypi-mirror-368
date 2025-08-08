"""Task rendering utilities for CLI output."""

import os
from typing import Any, Dict, List, Optional, Union

from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from flow.api.models import Task, TaskStatus

from .gpu_formatter import GPUFormatter
from .task_formatter import TaskFormatter
from .terminal_adapter import TerminalAdapter
from .time_formatter import TimeFormatter
from .theme_manager import theme_manager


class TaskTableRenderer:
    """Renders task lists as formatted tables with responsive column handling."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize renderer with optional console override."""
        self.console = console or Console()
        self.terminal = TerminalAdapter()
        self.time_fmt = TimeFormatter()
        self.gpu_fmt = GPUFormatter()
        self.task_fmt = TaskFormatter()

    def render_task_list(
        self,
        tasks: List[Task],
        title: Optional[str] = None,
        show_all: bool = False,
        limit: int = 20,
        return_renderable: bool = False,
    ):
        """Render a list of tasks using the new core table columns.

        This method now delegates to the unified StatusTableRenderer to keep
        the column definitions and styling DRY across the codebase.
        """
        from flow.cli.utils.status_table_renderer import StatusTableRenderer as CoreStatusTable

        renderer = CoreStatusTable(self.console)
        panel = renderer.render(
            tasks,
            me=None,
            title=(title or f"Tasks (showing up to {limit}{', last 24 hours' if not show_all else ''})"),
            wide=False,
            return_renderable=True,
        )
        if return_renderable:
            return panel
        self.console.print(panel)

    def _create_professional_table(
        self, title: Optional[str], layout: Dict[str, Any], density_config: Dict[str, Any]
    ) -> Table:
        """Create a professionally styled table.

        Args:
            title: Table title
            layout: Responsive layout configuration
            density_config: Density-specific configuration

        Returns:
            Configured Rich Table instance
        """
        # Determine box style - match flow init wizard style
        box_style = box.ROUNDED if density_config["show_borders"] else None

        # Create table with wizard-consistent styling
        table = Table(
            title=title,
            box=box_style,
            header_style="bold",
            border_style=(
                theme_manager.get_color("table.border")
                if density_config["show_borders"]
                else theme_manager.get_color("muted")
            ),
            title_style=(f"bold {theme_manager.get_color('accent')}" if title else None),
            caption_style=theme_manager.get_color("muted"),
            show_lines=False,  # Clean look without horizontal lines
            padding=(0, density_config["column_padding"]),
            collapse_padding=True,  # Reduce unnecessary padding
        )

        return table

    def _add_responsive_columns(self, table: Table, layout: Dict[str, Any]) -> None:
        """Add columns to table based on responsive layout.

        Args:
            table: Rich Table instance
            layout: Responsive layout configuration
        """
        columns = layout["columns"]

        if "name" in columns:
            width = layout.get("name_width")
            table.add_column(
                "Name",
                style=theme_manager.get_color("task.name"),
                width=width,
                header_style=theme_manager.get_color("table.header"),
                justify="left",
            )

        if "status" in columns:
            width = layout.get("status_width", 12)
            table.add_column(
                "Status",
                width=width,
                header_style=theme_manager.get_color("table.header"),
                justify="center",
            )

        if "gpu" in columns:
            width = layout.get("gpu_width", 12)
            table.add_column(
                "GPU",
                style=theme_manager.get_color("task.gpu"),
                width=width,
                header_style=theme_manager.get_color("table.header"),
                justify="center",
            )

        if "nodes" in columns:
            width = layout.get("nodes_width", 8)
            table.add_column(
                "Nodes",
                style=theme_manager.get_color("table.row"),
                width=width,
                header_style=theme_manager.get_color("table.header"),
                justify="right",
            )

        if "ip" in columns:
            width = layout.get("ip_width", 15)
            table.add_column(
                "IP",
                style=theme_manager.get_color("task.ip"),
                width=width,
                header_style=theme_manager.get_color("table.header"),
                justify="left",
            )

        if "created" in columns:
            width = layout.get("created_width", 12)
            table.add_column(
                "Created",
                style=theme_manager.get_color("task.time"),
                width=width,
                header_style=theme_manager.get_color("table.header"),
                justify="right",
            )

        if "duration" in columns:
            width = layout.get("duration_width", 8)
            table.add_column(
                "Duration",
                style=theme_manager.get_color("task.duration"),
                width=width,
                header_style=theme_manager.get_color("table.header"),
                justify="right",
            )

    def _center_text_in_width(self, text: str, width: int) -> str:
        """Manually center text within a given width using space padding.

        Args:
            text: Text to center (may contain Rich markup)
            width: Target width for centering

        Returns:
            Text padded with spaces to center within width
        """
        from rich.console import Console
        from rich.text import Text

        # Create a temporary console to measure text properly
        temp_console = Console(file=None, width=1000)  # Wide console for accurate measurement

        try:
            # Measure the display width of the text (excluding markup)
            if "[" in text and "]" in text:  # Likely contains Rich markup
                rich_text = Text.from_markup(text)
                display_width = len(rich_text.plain)
            else:
                display_width = len(text)
        except Exception:
            # Fallback to plain text length if markup parsing fails
            display_width = len(text)

        # If text is already as wide or wider than target, return as-is
        if display_width >= width:
            return text

        # Calculate padding needed
        total_padding = width - display_width
        left_padding = total_padding // 2
        right_padding = total_padding - left_padding

        # Create centered text with padding
        centered = " " * left_padding + text + " " * right_padding

        return centered

    def _build_row_data(self, task: Task, layout: Dict[str, Any]) -> List[Union[str, Align]]:
        """Build row data based on responsive layout configuration.

        Args:
            task: Task to format
            layout: Responsive layout configuration

        Returns:
            List of formatted cell values
        """
        row = []
        columns = layout["columns"]

        # Build row data based on configured columns
        if "name" in columns:
            name = self.task_fmt.format_task_summary(task)
            max_width = layout.get("name_width")
            if max_width and len(name) > max_width:
                name = self.terminal.intelligent_truncate(name, max_width, "start")
            row.append(name)

        if "status" in columns:
            # Check if we have a more specific instance status to show
            instance_status = getattr(task, "instance_status", None)

            # Determine display status using instance metadata when available
            if instance_status in ["STATUS_STARTING", "STATUS_INITIALIZING"]:
                display_status = "starting"
            elif instance_status == "STATUS_SCHEDULED":
                display_status = "pending"
            elif task.status.value == "pending":
                display_status = "pending"
            elif task.status.value == "running" and not task.ssh_host:
                # Only show starting if running but no IP yet
                display_status = "starting"
            else:
                # Default to the task's actual status
                display_status = task.status.value

            # Decide compact vs full word based on BOTH layout preference and width budget
            status_col_width = layout.get("status_width", 12)
            # Visible width is one symbol + space + word length
            required_width = 2 + len(display_status)
            should_use_compact = layout.get("use_compact_status", False) or (
                required_width > status_col_width
            )

            if should_use_compact:
                status = self.task_fmt.format_compact_status(display_status)
            else:
                status = self.task_fmt.format_status_with_color(display_status)

            row.append(status)

        if "gpu" in columns:
            # Get number of instances for multi-node display
            num_instances = getattr(task, "num_instances", 1)

            # Use ultra-compact format with width awareness
            max_gpu_width = layout.get("gpu_width")

            # Always use the new format which handles both single and multi-node elegantly
            gpu_type = self.gpu_fmt.format_ultra_compact_width_aware(
                task.instance_type, num_instances, max_gpu_width
            )
            row.append(gpu_type)

        if "nodes" in columns:
            # Show node count in X/Y format (running/total)
            num_instances = getattr(task, "num_instances", 1)

            if num_instances > 1:
                # Multi-instance: count running instances
                if hasattr(task, "instances") and task.instances:
                    # We have instance list - could potentially query each instance status
                    # For now, use simple heuristic based on task status
                    if task.status == TaskStatus.RUNNING:
                        # If task is running and has SSH, assume all instances are up
                        if task.ssh_host:
                            running_count = num_instances
                        else:
                            # Still provisioning
                            running_count = 0
                    elif task.status == TaskStatus.PENDING:
                        running_count = 0
                    else:
                        # For other states, assume all were running
                        running_count = num_instances

                    nodes_text = f"{running_count}/{num_instances}"
                else:
                    # No instance info, use task status
                    if task.status == TaskStatus.RUNNING:
                        nodes_text = f"{num_instances}/{num_instances}"
                    else:
                        nodes_text = f"0/{num_instances}"
            else:
                # Single instance - show based on status
                if task.status == TaskStatus.RUNNING:
                    nodes_text = "1/1"
                elif task.status == TaskStatus.PENDING:
                    nodes_text = "0/1"
                else:
                    nodes_text = "1/1"

            row.append(nodes_text)

        if "ip" in columns:
            # Show IP for running tasks, provisioning message for others
            if task.status == TaskStatus.RUNNING and task.ssh_host:
                ip_text = task.ssh_host
            elif task.is_provisioning():
                ip_text = "[dim]provisioning[/dim]"
            else:
                ip_text = "[dim]-[/dim]"
            row.append(ip_text)

        if "created" in columns:
            created = self.time_fmt.format_time_ago(task.created_at)
            row.append(created)

        if "duration" in columns:
            duration = self.time_fmt.calculate_duration(task)
            row.append(duration)

        return row


class TaskDetailRenderer:
    """Renders detailed task information in a formatted panel."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize renderer with optional console override."""
        self.console = console or Console()
        self.time_fmt = TimeFormatter()
        self.gpu_fmt = GPUFormatter()
        self.task_fmt = TaskFormatter()

    def render_task_details(self, task: Task) -> None:
        """Render detailed task information.

        Args:
            task: Task to display details for
        """
        lines = []

        # Basic info
        lines.append(f"[bold]Task:[/bold] {task.name}")

        # Only show the internal ID in debug mode or if it's different from name
        if os.environ.get("FLOW_DEBUG") or (task.task_id and not task.task_id.startswith("bid_")):
            lines.append(f"[bold]ID:[/bold] {task.task_id}")

        # Status with color - check if we should show "starting" status
        instance_status = getattr(task, "instance_status", None)

        # Determine display status based on instance state and task state
        if instance_status in ["STATUS_STARTING", "STATUS_INITIALIZING"]:
            display_status = "starting"
        elif instance_status == "STATUS_SCHEDULED":
            display_status = "pending"
        elif task.status.value == "pending":
            display_status = "pending"
        elif task.status.value == "running" and not task.ssh_host:
            # Only show starting if running but no IP yet
            display_status = "starting"
        else:
            # Default to the task's actual status
            display_status = task.status.value

        status_text = self.task_fmt.format_status_with_color(display_status)
        lines.append(f"[bold]Status:[/bold] {status_text}")

        # Show provisioning message if applicable
        provisioning_msg = task.get_provisioning_message()
        if provisioning_msg:
            lines.append(f"[yellow]⚠ {provisioning_msg}[/yellow]")

        # Resource info
        if task.instance_type:
            gpu_details = self.gpu_fmt.format_gpu_details(
                task.instance_type, task.num_instances or 1
            )
            lines.append(f"[bold]GPU:[/bold] {gpu_details}")

        if task.region:
            lines.append(f"[bold]Region:[/bold] {task.region}")

        # Connection info (show IP/port when available)
        if getattr(task, "ssh_host", None):
            if getattr(task, "ssh_port", None):
                lines.append(f"[bold]IP:[/bold] {task.ssh_host}:{task.ssh_port}")
            else:
                lines.append(f"[bold]IP:[/bold] {task.ssh_host}")

        # Timing info
        if task.created_at:
            lines.append(f"[bold]Created:[/bold] {self.time_fmt.format_time_ago(task.created_at)}")

        if task.started_at:
            lines.append(f"[bold]Started:[/bold] {self.time_fmt.format_time_ago(task.started_at)}")

        duration = self.time_fmt.calculate_duration(task)
        if duration != "-":
            if task.status == TaskStatus.RUNNING:
                lines.append(f"[bold]Running for:[/bold] {duration}")
            else:
                lines.append(f"[bold]Duration:[/bold] {duration}")

        if task.completed_at and task.status in [
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
        ]:
            lines.append(
                f"[bold]Completed:[/bold] {self.time_fmt.format_time_ago(task.completed_at)}"
            )

        # Add provider-specific details if available
        if task.provider_metadata:
            metadata = task.provider_metadata

            # Show detailed state information for pending or preempting tasks
            if metadata.get("state_detail"):
                lines.append("")  # Add separator
                if metadata.get("is_preempting"):
                    lines.append(
                        f"[bold red]Provider Status:[/bold red] {metadata['state_detail']}"
                    )
                else:
                    lines.append(f"[bold]Provider Status:[/bold] {metadata['state_detail']}")

                if metadata.get("state_help"):
                    lines.append(f"[dim]{metadata['state_help']}[/dim]")

            # Show pricing information for pending tasks
            if task.status == TaskStatus.PENDING and metadata.get("limit_price"):
                lines.append("")  # Add separator for pricing section
                bid_price = str(metadata["limit_price"])
                # Remove any existing dollar sign to avoid duplication
                if bid_price.startswith("$"):
                    bid_price = bid_price[1:]
                lines.append(f"[bold]Bid Price:[/bold] ${bid_price}/hour")

                # Show market price if available
                if metadata.get("market_price"):
                    market_price = metadata["market_price"]
                    lines.append(f"[bold]Market Price:[/bold] ${market_price:.2f}/hour")

                    # Show competitiveness message from provider
                    if metadata.get("price_message"):
                        competitiveness = metadata.get("price_competitiveness", "")
                        if competitiveness == "below_market":
                            lines.append(f"[yellow]⚠ {metadata['price_message']}[/yellow]")
                        elif competitiveness == "above_market":
                            lines.append(f"[green]✓ {metadata['price_message']}[/green]")
                        else:
                            lines.append(f"[dim]{metadata['price_message']}[/dim]")

            # Show provider console link
            if metadata.get("web_console_url") and metadata.get("provider") == "mithril":
                lines.append("")  # Add separator
                lines.append(
                    f"[bold]Mithril Console:[/bold] [cyan]{metadata['web_console_url']}[/cyan]"
                )

        # Create panel
        panel_content = "\n".join(lines)
        title = f"Task: {task.name or task.task_id}"

        panel = Panel(
            panel_content,
            title=title,
            title_align="left",
            border_style=theme_manager.get_color("table.border"),
        )

        self.console.print(panel)

        # Show helpful commands
        self._show_task_commands(task)

    def _show_task_commands(self, task: Task) -> None:
        """Show relevant commands for the task state.

        Args:
            task: Task to show commands for
        """
        if task.status == TaskStatus.RUNNING:
            self.console.print("\n[dim]Commands:[/dim]")
            self.console.print(f"  flow logs {task.name}     # View logs")
            self.console.print(f"  flow ssh {task.name}      # SSH into instance")
            self.console.print(f"  flow cancel {task.name}   # Cancel task")
        elif task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            self.console.print("\n[dim]Commands:[/dim]")
            self.console.print(f"  flow logs {task.name}     # View logs")
