"""Logs command for viewing task output.

Provides both historical log retrieval and real-time streaming.
Supports stdout/stderr selection and tail functionality.

Examples:
    View recent logs:
        $ flow logs task-abc123

    Stream logs in real-time:
        $ flow logs task-abc123 -f

    Show last 50 lines of stderr:
        $ flow logs task-abc123 --stderr -n 50
"""

import sys
import os
import re
import time
from datetime import datetime, timedelta
from typing import Optional, List

import click

from flow import Flow
from flow.api.models import TaskStatus
from flow.errors import FlowError
from flow.api.models import Task

from .base import BaseCommand, console
from ..utils.task_resolver import resolve_task_identifier
from ..utils.task_formatter import TaskFormatter
from ..utils.interactive_selector import select_task
from ..utils.task_selector_mixin import TaskOperationCommand, TaskFilter
from ..utils.task_index_cache import TaskIndexCache
from ..utils.task_resolver import resolve_task_identifier
from flow.cli.utils.selection import Selection, SelectionParseError


class LogsCommand(BaseCommand, TaskOperationCommand):
    """Logs command implementation.

    Handles both batch retrieval and streaming modes with automatic
    reconnection for long-running tasks.
    """

    def __init__(self):
        """Initialize command with formatter."""
        super().__init__()
        self.task_formatter = TaskFormatter()

    def _parse_since(self, since_str: str) -> Optional[datetime]:
        """Parse since string to datetime."""
        if not since_str:
            return None

        # Try relative time formats (5m, 1h, 2d)
        match = re.match(r"^(\d+)([mhd])$", since_str)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)

            if unit == "m":
                delta = timedelta(minutes=amount)
            elif unit == "h":
                delta = timedelta(hours=amount)
            elif unit == "d":
                delta = timedelta(days=amount)

            return datetime.now() - delta

        # Try ISO format
        try:
            return datetime.fromisoformat(since_str.replace("Z", "+00:00"))
        except Exception:
            return None

    def _format_log_line(self, line: str, node_idx: int, no_prefix: bool, full_prefix: bool) -> str:
        """Format a log line with node prefix."""
        if no_prefix:
            return line

        if full_prefix:
            prefix = f"[node-{node_idx}] "
        else:
            prefix = f"[{node_idx}] "

        return prefix + line

    def _filter_logs(self, logs: str, grep: Optional[str], since: Optional[datetime]) -> List[str]:
        """Filter logs based on grep pattern and time."""
        lines = logs.splitlines(keepends=True)

        if grep:
            pattern = re.compile(grep)
            lines = [line for line in lines if pattern.search(line)]

        # Note: since filtering would require timestamp parsing from logs
        # This is a simplified implementation

        return lines

    @property
    def name(self) -> str:
        return "logs"

    @property
    def help(self) -> str:
        return "View task output logs - stdout, stderr, real-time streaming"

    # TaskSelectorMixin implementation
    def get_task_filter(self):
        """Prefer running tasks but allow all."""
        return TaskFilter.with_logs

    def get_selection_title(self) -> str:
        return "Select a task to view logs"

    def get_no_tasks_message(self) -> str:
        return "No running or completed tasks found"

    # Command execution
    def execute_on_task(self, task: Task, client: Flow, **kwargs) -> None:
        """Execute log viewing on the selected task."""
        follow = kwargs.get("follow", False)
        tail = kwargs.get("tail", 100)
        stderr = kwargs.get("stderr", False)
        node = kwargs.get("node")
        since = kwargs.get("since")
        grep = kwargs.get("grep")
        no_prefix = kwargs.get("no_prefix", False)
        full_prefix = kwargs.get("full_prefix", False)
        output_json = kwargs.get("output_json", False)

        # Validate node parameter for multi-instance tasks
        is_multi_instance = hasattr(task, "num_instances") and task.num_instances > 1

        if node is not None:
            if is_multi_instance:
                if node < 0 or node >= task.num_instances:
                    console.print(
                        f"[red]Error: Node index {node} out of bounds (task has {task.num_instances} nodes)[/red]"
                    )
                    console.print(f"Valid nodes: 0-{task.num_instances - 1}")
                    raise SystemExit(1)
            else:
                console.print(
                    f"[red]Error: Task '{task.name or task.task_id}' is single-instance[/red]"
                )
                console.print("Remove --node flag for single-instance tasks")
                raise SystemExit(1)

        # JSON output mode
        if output_json:
            import json

            result = {
                "task_id": task.task_id,
                "task_name": task.name,
                "status": task.status.value,
                "num_instances": getattr(task, "num_instances", 1),
            }

            # For now, just return basic info - actual log fetching would need provider support
            if follow:
                result["error"] = "JSON output not supported for follow mode"
            else:
                # This would need to be implemented in the provider
                result["logs"] = "Log retrieval with new options requires provider implementation"

            console.print(json.dumps(result))
            return

        task_display = self.task_formatter.format_task_display(task)

        if follow:
            # Enhanced log streaming with status indicator
            from rich.panel import Panel
            from rich.layout import Layout
            from rich.text import Text

            # Create header with task info
            from ..utils.gpu_formatter import GPUFormatter

            gpu_display = (
                GPUFormatter.format_ultra_compact(
                    task.instance_type, getattr(task, "num_instances", 1)
                )
                if task.instance_type
                else "N/A"
            )
            header = Panel(
                f"[bold]Task:[/bold] {task.name or task.task_id}\n"
                f"[bold]Status:[/bold] {self.task_formatter.format_status_with_color(task.status.value)}\n"
                f"[bold]Instance:[/bold] {gpu_display}",
                title="[bold cyan]Log Stream[/bold cyan]",
                border_style="cyan",
                padding=(0, 1),
                height=5,
            )

            console.print(header)
            console.print(f"[dim]Following logs... (Ctrl+C to stop)[/dim]\n")

            try:
                # TODO: Multi-instance support requires provider implementation
                # Would need to:
                # 1. If node specified, get logs from that specific node
                # 2. If no node specified and multi-instance, interleave logs from all nodes with prefixes
                # 3. Apply grep filtering if specified
                # 4. Apply since filtering if specified

                for line in client.logs(task.task_id, follow=True, stderr=stderr):
                    # For multi-instance, would format with node prefix here
                    if is_multi_instance and not no_prefix:
                        # This would need node index from the log source
                        node_idx = 0  # Placeholder - would come from provider
                        line = self._format_log_line(line, node_idx, no_prefix, full_prefix)

                    # Apply grep filter
                    if grep and not re.search(grep, line):
                        continue

                    # Print each line directly for real-time display
                    console.print(line, end="", markup=False, highlight=False)
            except KeyboardInterrupt:
                console.print("\n[dim]Stopped following logs[/dim]")
        else:
            # Retry loop for instances that are still starting
            max_retries = 30  # 30 * 2 = 60 seconds max wait
            retry_delay = 2
            logs = None
            provisioning_message_shown = False

            for attempt in range(max_retries):
                try:
                    # TODO: Multi-instance support requires provider implementation
                    # For now, fetch logs normally
                    logs = client.logs(task.task_id, tail=tail, stderr=stderr)

                    # Check if we got a "waiting" message instead of actual logs
                    # Note: This is a temporary check until providers consistently raise InstanceNotReadyError
                    if logs and (
                        "waiting for instance" in logs.lower()
                        or "instance is still starting" in logs.lower()
                        or "ssh is not ready" in logs.lower()
                        or "task pending" in logs.lower()
                    ):
                        # Show provisioning message once
                        if not provisioning_message_shown:
                            # Import constant for provisioning time
                            from flow import DEFAULT_PROVISION_MINUTES as EXPECTED_PROVISION_MINUTES

                            console.print(
                                f"\n[dim]Instance is provisioning (Mithril instances take up to {EXPECTED_PROVISION_MINUTES} minutes)...[/dim]"
                            )
                            provisioning_message_shown = True

                        time.sleep(retry_delay)
                        continue

                    # Got real logs or empty logs - break out
                    break

                except FlowError as e:
                    # Handle common errors with helpful messages
                    error_msg = str(e)
                    if "not ready" in error_msg.lower() or "starting up" in error_msg.lower():
                        # Show provisioning message once
                        if not provisioning_message_shown:
                            from flow import DEFAULT_PROVISION_MINUTES as EXPECTED_PROVISION_MINUTES

                            console.print(
                                f"\n[dim]Instance is provisioning (Mithril instances take up to {EXPECTED_PROVISION_MINUTES} minutes)...[/dim]"
                            )
                            provisioning_message_shown = True

                        time.sleep(retry_delay)
                        continue
                    else:
                        raise
            else:
                # Max retries exceeded - show helpful message
                console.print(
                    f"[yellow]Instance is taking longer than expected to start[/yellow]\n"
                )
                console.print("The instance needs a few minutes to be ready for SSH connections.")
                console.print(
                    f"\nTry: [cyan]flow ssh {task.name or task.task_id}[/cyan] (automatically waits for readiness)"
                )
                return

            # Display logs (outside of progress context)
            if logs and logs.strip():
                # Apply filtering
                lines = self._filter_logs(logs, grep, self._parse_since(since) if since else None)

                # Format lines with node prefix for multi-instance
                if is_multi_instance and not no_prefix:
                    # This would need node index from the log source
                    node_idx = 0  # Placeholder - would come from provider
                    lines = [
                        self._format_log_line(line, node_idx, no_prefix, full_prefix)
                        for line in lines
                    ]

                # Join and print
                output = "".join(lines)
                if output.strip():
                    console.print(output, markup=False, highlight=False, end="")
                else:
                    console.print(f"[dim]No logs match the specified filters[/dim]")
            else:
                console.print(f"[dim]No logs available for {task_display}[/dim]")

        # Show next actions based on task status
        task_ref = task.name or task.task_id
        if task.status == TaskStatus.RUNNING:
            self.show_next_actions(
                [
                    f"SSH into instance: [cyan]flow ssh {task_ref}[/cyan]",
                    f"Check task status: [cyan]flow status {task_ref}[/cyan]",
                    f"Cancel task: [cyan]flow cancel {task_ref}[/cyan]",
                ]
            )
        elif task.status == TaskStatus.COMPLETED:
            self.show_next_actions(
                [
                    "Submit a new task: [cyan]flow run task.yaml[/cyan]",
                    "View all tasks: [cyan]flow status[/cyan]",
                ]
            )
        elif task.status == TaskStatus.FAILED:
            self.show_next_actions(
                [
                    f"View error details: [cyan]flow logs {task_ref} --stderr[/cyan]",
                    f"Check task details: [cyan]flow status {task_ref}[/cyan]",
                    "Retry with different parameters: [cyan]flow run <config.yaml>[/cyan]",
                ]
            )
        elif task.status == TaskStatus.PENDING:
            self.show_next_actions(
                [
                    f"Check task status: [cyan]flow status {task_ref}[/cyan]",
                    f"Cancel if needed: [cyan]flow cancel {task_ref}[/cyan]",
                    "View resource availability: [cyan]flow status --all[/cyan]",
                ]
            )

    def get_command(self) -> click.Command:
        # Import completion function
        from ..utils.shell_completion import complete_task_ids

        @click.command(name=self.name, help=self.help)
        @click.argument("task_identifier", required=False, shell_complete=complete_task_ids)
        @click.option("--follow", "-f", is_flag=True, help="Follow log output")
        @click.option("--tail", "-n", type=int, default=100, help="Number of lines to show")
        @click.option("--stderr", is_flag=True, help="Show stderr instead of stdout")
        @click.option("--node", type=int, help="Specific node (0-indexed) for multi-instance tasks")
        @click.option(
            "--since", help="Show logs since timestamp (e.g., '5m', '1h', '2024-01-15T10:00:00')"
        )
        @click.option("--grep", help="Filter lines matching pattern")
        @click.option(
            "--no-prefix", is_flag=True, help="Remove node prefix for single-node or piping"
        )
        @click.option(
            "--full-prefix",
            is_flag=True,
            help="Use full node prefix (e.g., [node-0] instead of [0])",
        )
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        @click.option(
            "--verbose", "-v", is_flag=True, help="Show detailed examples and usage patterns"
        )
        def logs(
            task_identifier: Optional[str],
            follow: bool,
            tail: int,
            stderr: bool,
            node: Optional[int],
            since: Optional[str],
            grep: Optional[str],
            no_prefix: bool,
            full_prefix: bool,
            output_json: bool,
            verbose: bool,
        ):
            """Get logs from a running task.

            TASK_IDENTIFIER: Task ID or name (optional - interactive selector if omitted)

            \b
            Examples:
                flow logs                    # Interactive task selector
                flow logs my-training        # View recent logs
                flow logs task-abc123 -f     # Stream logs in real-time
                flow logs task --stderr -n 50  # Last 50 stderr lines

            Use 'flow logs --verbose' for advanced filtering and multi-node examples.
            """
            if verbose:
                console.print("\n[bold]Advanced Log Viewing:[/bold]\n")
                console.print("Real-time streaming:")
                console.print("  flow logs task -f                # Follow stdout")
                console.print("  flow logs task -f --stderr        # Follow stderr")
                console.print("  flow logs task -f --grep ERROR   # Stream only errors\n")

                console.print("Time-based filtering:")
                console.print("  flow logs task --since 5m        # Last 5 minutes")
                console.print("  flow logs task --since 1h        # Last hour")
                console.print("  flow logs task --since 2024-01-15T10:00:00  # Since timestamp\n")

                console.print("Multi-node tasks:")
                console.print("  flow logs distributed --node 0    # Head node logs")
                console.print("  flow logs distributed --node 1    # Worker node logs")
                console.print(
                    "  flow logs task --no-prefix        # Remove [0] prefix for piping\n"
                )

                console.print("Advanced filtering:")
                console.print("  flow logs task --grep 'loss.*0\\.[0-9]+'     # Regex patterns")
                console.print("  flow logs task -n 1000 | grep -v DEBUG      # Unix pipelines")
                console.print(
                    "  flow logs task --json > logs.json            # Export for analysis\n"
                )

                console.print("Common patterns:")
                console.print("  • Training progress: flow logs task -f --grep 'epoch\\|loss'")
                console.print("  • Error debugging: flow logs task --stderr --grep ERROR")
                console.print("  • Save full logs: flow logs task -n 999999 > task.log")
                console.print("  • Monitor GPU: flow ssh task -c 'tail -f /var/log/gpud.log'\n")
                return

            # Selection grammar: attempt if looks like indices (works after 'flow status')
            if task_identifier:
                import re
                expr = task_identifier.strip()
                # Accept optional leading colon for index selections (e.g., ":1-3,5" or ":2")
                if re.fullmatch(r":?[0-9,\-\s]+", expr):
                    try:
                        if expr.startswith(":"):
                            expr = expr[1:]
                        sel = Selection.parse(expr)
                        idx_map = TaskIndexCache().get_indices_map()
                        if idx_map:
                            task_ids, errors = sel.to_task_ids(idx_map)
                            if errors:
                                console.print(f"[red]Selection error:[/red] {errors[0]}")
                                return
                            if len(task_ids) != 1:
                                console.print("[red]Selection must resolve to exactly one task for logs[/red]")
                                return
                            task_identifier = task_ids[0]
                    except SelectionParseError:
                        # Fall through to normal resolution
                        pass

            self._execute(
                task_identifier,
                follow,
                tail,
                stderr,
                node,
                since,
                grep,
                no_prefix,
                full_prefix,
                output_json,
            )

        return logs

    def _execute(
        self,
        task_identifier: Optional[str],
        follow: bool,
        tail: int,
        stderr: bool,
        node: Optional[int],
        since: Optional[str],
        grep: Optional[str],
        no_prefix: bool,
        full_prefix: bool,
        output_json: bool,
    ) -> None:
        """Execute log retrieval or streaming."""
        self.execute_with_selection(
            task_identifier,
            follow=follow,
            tail=tail,
            stderr=stderr,
            node=node,
            since=since,
            grep=grep,
            no_prefix=no_prefix,
            full_prefix=full_prefix,
            output_json=output_json,
        )


# Export command instance
command = LogsCommand()
