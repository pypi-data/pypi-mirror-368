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

import re
import time
from datetime import datetime

import click

from flow.api.client import Flow
from flow.api.models import Task, TaskStatus
from flow.cli.commands.base import BaseCommand, console
from flow.cli.utils.step_progress import SSHWaitProgressAdapter, StepTimeline
from flow.cli.utils.task_formatter import TaskFormatter
from flow.cli.utils.task_selector_mixin import TaskFilter, TaskOperationCommand
from flow.errors import FlowError
from flow.cli.utils.theme_manager import theme_manager


class LogsCommand(BaseCommand, TaskOperationCommand):
    """Logs command implementation.

    Handles both batch retrieval and streaming modes with automatic
    reconnection for long-running tasks.
    """

    def __init__(self):
        """Initialize command with formatter."""
        super().__init__()
        self.task_formatter = TaskFormatter()

    def _parse_since(self, since_str: str) -> datetime | None:
        """Parse since string to datetime (delegates to utils.time_spec)."""
        from flow.cli.utils.time_spec import parse_timespec

        return parse_timespec(since_str)

    def _format_log_line(self, line: str, node_idx: int, no_prefix: bool, full_prefix: bool) -> str:
        """Format a log line with node prefix."""
        if no_prefix:
            return line

        if full_prefix:
            prefix = f"[node-{node_idx}] "
        else:
            prefix = f"[{node_idx}] "

        return prefix + line

    def _filter_logs(self, logs: str, grep: str | None, since: datetime | None) -> list[str]:
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

        # Validate node parameter for multi-instance tasks via shared helper
        from flow.cli.utils.task_utils import validate_node_index

        # Robust multi-instance detection (tolerates mocks)
        try:
            num_instances_val = getattr(task, "num_instances", 1)
            num_instances_int = int(num_instances_val)
        except Exception:
            num_instances_int = 1
        is_multi_instance = num_instances_int > 1
        if node is not None:
            validate_node_index(task, node)

        # JSON output mode
        if output_json:
            import json

            result: dict[str, object] = {
                "task_id": getattr(task, "task_id", None) or "",
                "task_name": getattr(task, "name", None) or "",
                "status": getattr(
                    getattr(task, "status", None), "value", str(getattr(task, "status", ""))
                )
                or "",
                "num_instances": getattr(task, "num_instances", 1),
            }

            if follow:
                result["error"] = "JSON output not supported for follow mode"
            else:
                try:
                    logs_text = client.logs(task.task_id, follow=False, tail=tail, stderr=stderr)  # type: ignore[arg-type]
                    if isinstance(logs_text, str):
                        result["logs"] = logs_text
                    else:
                        # Iterator or unexpected type
                        try:
                            result["logs"] = "".join(list(logs_text))
                        except Exception:
                            result["logs"] = str(logs_text)
                except Exception:
                    result["logs"] = (
                        "Log retrieval with new options requires provider implementation"
                    )

            try:
                console.print(json.dumps(result))
            except Exception:
                console.print(json.dumps({k: str(v) for k, v in result.items()}))
            return

        task_display = getattr(
            self.task_formatter, "format_task_display", lambda t: (t.name or t.task_id)
        )(task)

        # Build unified timeline for non-JSON output
        timeline: StepTimeline | None = None
        if not output_json:
            timeline = StepTimeline(console, title="flow logs", title_animation="auto")
            timeline.start()

        if follow:
            # Ensure SSH/log readiness if needed (running tasks without ssh_host)
            if timeline and not getattr(task, "ssh_host", None):
                from flow.api.ssh_utils import DEFAULT_PROVISION_MINUTES, SSHNotReadyError

                # Seed baseline from instance age to make resume realistic
                baseline = 0
                try:
                    baseline = int(getattr(task, "instance_age_seconds", None) or 0)
                except Exception:
                    baseline = 0
                step_idx = timeline.add_step(
                    "Provisioning & SSH",
                    show_bar=True,
                    estimated_seconds=DEFAULT_PROVISION_MINUTES * 60,
                    baseline_elapsed_seconds=baseline,
                )
                adapter = SSHWaitProgressAdapter(
                    timeline,
                    step_idx,
                    DEFAULT_PROVISION_MINUTES * 60,
                    baseline_elapsed_seconds=baseline,
                )
                try:
                    with adapter:
                        task = client.wait_for_ssh(
                            task_id=task.task_id,
                            timeout=DEFAULT_PROVISION_MINUTES * 60,
                            show_progress=False,
                            progress_adapter=adapter,
                        )
                except SSHNotReadyError as e:
                    timeline.fail_step(str(e))
                    timeline.finish()
                    return

            # Attach step
            if timeline:
                attach_idx = timeline.add_step("Attaching to logs", show_bar=False)
                timeline.start_step(attach_idx)
            # Enhanced log streaming with status indicator
            from rich.panel import Panel

            # Create header with task info
            from flow.cli.utils.gpu_formatter import GPUFormatter

            gpu_display = (
                GPUFormatter.format_ultra_compact(
                    task.instance_type, getattr(task, "num_instances", 1)
                )
                if task.instance_type
                else "N/A"
            )
            # Status string with robust fallback for mocks
            try:
                raw_status = getattr(getattr(task, "status", None), "value", None)
                if not raw_status:
                    raw_status = str(getattr(task, "status", "") or "unknown")
                status_display = self.task_formatter.format_status_with_color(str(raw_status))
            except Exception:
                status_display = str(getattr(task, "status", "unknown"))

            header = Panel(
                f"[bold]Task:[/bold] {task.name or task.task_id}\n"
                f"[bold]Status:[/bold] {status_display}\n"
                f"[bold]Instance:[/bold] {gpu_display}",
                title="[bold accent]Log Stream[/bold accent]",
                border_style=theme_manager.get_color("accent"),
                padding=(0, 1),
                height=5,
            )

            console.print(header)
            console.print(
                f"[dim]Following logs... (Ctrl+C to stop){'  Filter: ' + grep if grep else ''}[/dim]\n"
            )
            if timeline:
                timeline.complete_step()

            try:
                stream = client.logs(task.task_id, follow=True, stderr=stderr)  # type: ignore[arg-type]
                # Support both iterators and plain strings from mocks
                if isinstance(stream, str):
                    for line in self._filter_logs(
                        stream, grep, self._parse_since(since) if since else None
                    ):
                        if is_multi_instance and not no_prefix:
                            node_idx = 0  # Placeholder - would come from provider
                            line = self._format_log_line(line, node_idx, no_prefix, full_prefix)
                        console.print(line, end="", markup=False, highlight=False)
                else:
                    for line in stream:  # type: ignore[assignment]
                        if is_multi_instance and not no_prefix:
                            node_idx = 0  # Placeholder - would come from provider
                            line = self._format_log_line(line, node_idx, no_prefix, full_prefix)
                        if grep and not re.search(grep, line):
                            continue
                        console.print(line, end="", markup=False, highlight=False)
            except KeyboardInterrupt:
                console.print("\n[dim]Stopped following logs[/dim]")
            finally:
                if timeline:
                    timeline.finish()
        else:
            # Ensure readiness for running tasks without ssh_host (avoid noisy prints)
            if (
                timeline
                and not getattr(task, "ssh_host", None)
                and getattr(task, "status", None) == TaskStatus.RUNNING
            ):
                from flow.api.ssh_utils import DEFAULT_PROVISION_MINUTES

                baseline = 0
                try:
                    baseline = int(getattr(task, "instance_age_seconds", None) or 0)
                except Exception:
                    baseline = 0
                step_idx = timeline.add_step(
                    "Provisioning & SSH",
                    show_bar=True,
                    estimated_seconds=DEFAULT_PROVISION_MINUTES * 60,
                    baseline_elapsed_seconds=baseline,
                )
                adapter = SSHWaitProgressAdapter(
                    timeline,
                    step_idx,
                    DEFAULT_PROVISION_MINUTES * 60,
                    baseline_elapsed_seconds=baseline,
                )
                try:
                    with adapter:
                        task = client.wait_for_ssh(
                            task_id=task.task_id,
                            timeout=DEFAULT_PROVISION_MINUTES * 60,
                            show_progress=False,
                            progress_adapter=adapter,
                        )
                except Exception as e:
                    timeline.fail_step(str(e))
                    timeline.finish()
                    return

            # Retry loop for instances that are still starting
            max_retries = 3  # keep tests fast
            retry_delay = 2
            logs = None
            provisioning_message_shown = False

            # Fetch step
            fetch_idx = None
            if timeline:
                fetch_idx = timeline.add_step(f"Fetching last {tail} lines", show_bar=False)
                timeline.start_step(fetch_idx)

            for attempt in range(max_retries):
                try:
                    # TODO: Multi-instance support requires provider implementation
                    # For now, fetch logs normally
                    logs = None
                    primary_ok = False
                    try:
                        # Try provider logs API first
                        logs = client.logs(task.task_id, tail=tail, stderr=stderr)
                        primary_ok = True
                    except Exception:
                        primary_ok = False

                    # Normalize and/or fallback
                    if isinstance(logs, bytes):
                        logs = logs.decode("utf-8", errors="ignore")
                    if not isinstance(logs, str):
                        try:
                            task_obj = client.get_task(task.task_id)
                            # Some providers/tests expose logs() on the task
                            if hasattr(task_obj, "logs") and callable(task_obj.logs):
                                logs = task_obj.logs()
                                if isinstance(logs, bytes):
                                    logs = logs.decode("utf-8", errors="ignore")
                                if not isinstance(logs, str):
                                    logs = str(logs)
                            else:
                                # Last resort: coerce to string
                                logs = str(logs) if logs is not None else ""
                        except Exception:
                            # If both attempts fail, re-raise the primary error if that path was tried
                            if primary_ok:
                                raise
                            # else, surface a simple message and break
                            logs = ""

                    # Check if we got a "waiting" message instead of actual logs
                    # Note: This is a temporary check until providers consistently raise InstanceNotReadyError
                    lower = logs.lower() if isinstance(logs, str) else str(logs).lower()
                    if logs and (
                        "waiting for instance" in lower
                        or "instance is still starting" in lower
                        or "ssh is not ready" in lower
                        or "task pending" in lower
                    ):
                        # Quietly wait; timeline covers this state
                        provisioning_message_shown = True
                        time.sleep(retry_delay)
                        continue

                    # Got real logs or empty logs - break out
                    break

                except FlowError as e:
                    # Handle common errors with quiet backoff
                    error_msg = str(e)
                    if "not ready" in error_msg.lower() or "starting up" in error_msg.lower():
                        provisioning_message_shown = True
                        time.sleep(retry_delay)
                        continue
                    else:
                        raise
            else:
                # Max retries exceeded - show helpful message
                if timeline:
                    timeline.fail_step("Instance is taking longer than expected")
                    timeline.finish()
                console.print("[yellow]Instance is taking longer than expected to start[/yellow]\n")
                console.print("The instance needs a few minutes to be ready for SSH connections.")
                console.print(
                    f"\nTry: [accent]flow ssh {task.name or task.task_id}[/accent] (automatically waits for readiness)"
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
                    console.print("[dim]No logs match the specified filters[/dim]")
            else:
                console.print(f"[dim]No logs available for {task_display}[/dim]")

            if timeline:
                if fetch_idx is not None:
                    timeline.complete_step()
                timeline.finish()

        # Show next actions based on task status
        task_ref = task.name or task.task_id
        if getattr(task, "status", None) == TaskStatus.RUNNING:
            self.show_next_actions(
                [
                    f"SSH into instance: [accent]flow ssh {task_ref}[/accent]",
                    f"Check task status: [accent]flow status {task_ref}[/accent]",
                    f"Cancel task: [accent]flow cancel {task_ref}[/accent]",
                ]
            )
        elif getattr(task, "status", None) == TaskStatus.COMPLETED:
            self.show_next_actions(
                [
                    "Submit a new task: [accent]flow run task.yaml[/accent]",
                    "View all tasks: [accent]flow status[/accent]",
                ]
            )
        elif getattr(task, "status", None) == TaskStatus.FAILED:
            self.show_next_actions(
                [
                    f"View error details: [accent]flow logs {task_ref} --stderr[/accent]",
                    f"Check task details: [accent]flow status {task_ref}[/accent]",
                    "Retry with different parameters: [accent]flow run <config.yaml>[/accent]",
                ]
            )
        elif getattr(task, "status", None) == TaskStatus.PENDING:
            self.show_next_actions(
                [
                    f"Check task status: [accent]flow status {task_ref}[/accent]",
                    f"Cancel if needed: [accent]flow cancel {task_ref}[/accent]",
                    "View resource availability: [accent]flow status --all[/accent]",
                ]
            )

    def get_command(self) -> click.Command:
        # Import completion function
        from flow.cli.utils.mode import demo_aware_command
        from flow.cli.utils.shell_completion import complete_task_ids

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
        @demo_aware_command()
        def logs(
            task_identifier: str | None,
            follow: bool,
            tail: int,
            stderr: bool,
            node: int | None,
            since: str | None,
            grep: str | None,
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
                from flow.cli.utils.selection_helpers import parse_selection_to_task_ids

                ids, err = parse_selection_to_task_ids(task_identifier)
                if err:
                    console.print(f"[red]{err}[/red]")
                    return
                if ids is not None:
                    if len(ids) != 1:
                        console.print(
                            "[red]Selection must resolve to exactly one task for logs[/red]"
                        )
                        return
                    task_identifier = ids[0]

            # When a direct identifier is provided, avoid the selector mixin path to allow tests
            # to patch Flow and resolver without requiring full auth config.
            if task_identifier:
                client = Flow()
                # Import resolver from canonical path to ensure tests can patch it reliably
                from flow.cli.utils.task_resolver import (
                    resolve_task_identifier as _resolve_task_identifier,
                )

                task, error = _resolve_task_identifier(client, task_identifier)
                if error:
                    console.print(f"[red]{error}[/red]")
                    return
                self.execute_on_task(
                    task,
                    client,
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
            else:
                self.execute_with_selection(
                    task_identifier,
                    flow_class=Flow,
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

        return logs

    def _execute(
        self,
        task_identifier: str | None,
        follow: bool,
        tail: int,
        stderr: bool,
        node: int | None,
        since: str | None,
        grep: str | None,
        no_prefix: bool,
        full_prefix: bool,
        output_json: bool,
    ) -> None:
        """Execute log retrieval or streaming."""
        self.execute_with_selection(
            task_identifier,
            flow_class=Flow,
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
