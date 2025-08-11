"""Cancel command - terminate running GPU tasks.

Allows terminating running or pending tasks with optional confirmation.

Examples:
    # Cancel a specific task
    $ flow cancel my-training-job

    # Cancel last task from status (using index)
    $ flow cancel :1

    # Cancel all dev tasks without confirmation (wildcard)
    $ flow cancel --name-pattern "dev-*" --yes

Command Usage:
    flow cancel TASK_ID_OR_NAME [OPTIONS]

The command will:
- Verify the task exists and is cancellable
- Prompt for confirmation (unless --yes is used)
- Send cancellation request to the provider
- Display cancellation status

Note:
    Only tasks in 'pending' or 'running' state can be cancelled.
    Completed or failed tasks cannot be cancelled.
"""

from __future__ import annotations

import fnmatch
import os
import re

import click

from flow.api.client import Flow
from flow.api.models import Task, TaskStatus
from flow.cli.utils.task_formatter import TaskFormatter
from flow.cli.utils.task_resolver import resolve_task_identifier as _resolve_task_identifier
from flow.cli.utils.task_selector_mixin import TaskFilter, TaskOperationCommand
from flow.errors import AuthenticationError

# Re-export for tests that patch 'flow.cli.commands.cancel.resolve_task_identifier'
resolve_task_identifier = _resolve_task_identifier
from flow.cli.commands.base import BaseCommand, console


def _invalidate_task_prefetch_cache():
    try:
        from flow.cli.utils.prefetch import _CACHE  # type: ignore

        for k in ("tasks_running", "tasks_pending", "tasks_all"):
            if hasattr(_CACHE, "_data"):
                _CACHE._data.pop(k, None)  # noqa: SLF001
    except Exception:
        pass


from flow.cli.utils.task_index_cache import TaskIndexCache


class CancelCommand(BaseCommand, TaskOperationCommand):
    """Cancel a running task."""

    def __init__(self):
        """Initialize command with formatter."""
        super().__init__()
        self.task_formatter = TaskFormatter()

    @property
    def name(self) -> str:
        return "cancel"

    @property
    def help(self) -> str:
        return """Cancel GPU tasks - pattern matching uses wildcards by default
        
        Example: flow cancel -n 'dev-*'"""

    def get_command(self) -> click.Command:
        # Import completion function
        from flow.cli.utils.mode import demo_aware_command
        from flow.cli.utils.shell_completion import complete_task_ids

        @click.command(name=self.name, help=self.help)
        @click.argument("task_identifier", required=False, shell_complete=complete_task_ids)
        @click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
        @click.option("--all", is_flag=True, help="Cancel all running tasks")
        @click.option(
            "--name-pattern",
            "-n",
            help="Cancel tasks matching wildcard pattern (e.g., 'dev-*', '*-gpu-8x*', 'train-v?'). Use --regex for regex.",
        )
        @click.option("--regex", is_flag=True, help="Treat pattern as regex instead of wildcard")
        @click.option("--verbose", "-v", is_flag=True, help="Show detailed examples and patterns")
        @click.option(
            "--interactive/--no-interactive",
            default=None,
            help="Force interactive selector on/off regardless of terminal autodetect",
        )
        @demo_aware_command()
        def cancel(
            task_identifier: str,  # Optional at runtime, Click passes ''/None if omitted
            yes: bool,
            all: bool,
            name_pattern: str,  # Optional at runtime
            regex: bool,
            verbose: bool,
            interactive: bool | None,
        ):
            """Cancel a running task.

            TASK_IDENTIFIER: Task ID or name (optional - interactive selector if omitted)

            \b
            Examples:
                flow cancel                       # Interactive task selector
                flow cancel my-training           # Cancel by name
                flow cancel task-abc123           # Cancel by ID
                flow cancel -n 'dev-*' --yes      # Cancel tasks starting with 'dev-'
                flow cancel --all --yes           # Cancel all running tasks

            Pattern matching uses wildcards by default:
                flow cancel -n 'dev-*'           # Matches: dev-1, dev-test, dev-experiment
                flow cancel -n '*-gpu-8x*'       # Matches tasks mentioning 8x GPU
                flow cancel -n 'train-v?'        # Single character wildcard
            Use --regex for advanced regex patterns:
                flow cancel -n '^gpu-test-' --regex     # Start anchor
                flow cancel -n '.*-v[0-9]+' --regex     # Version pattern

            Use 'flow cancel --verbose' for advanced pattern matching examples.
            """
            if verbose:
                console.print("\n[bold]Pattern Matching Examples[/bold]\n")

                console.print("[bold]Wildcard patterns (default):[/bold]")
                console.print(
                    "  flow cancel -n 'dev-*'                # Cancel all starting with dev-"
                )
                console.print("  flow cancel -n '*-gpu-8x*'            # Match GPU type")
                console.print(
                    "  flow cancel -n 'train-v?'             # Single character wildcard\n"
                )

                console.print("[bold]Regex patterns (with --regex flag):[/bold]")
                console.print(
                    "  flow cancel -n '^dev-' --regex        # Matches tasks starting with 'dev-'"
                )
                console.print(
                    "  flow cancel -n 'dev-$' --regex        # Matches tasks ending with 'dev-'"
                )
                console.print(
                    "  flow cancel -n '.*-v[0-9]+' --regex  # Version pattern (e.g., app-v1, test-v23)"
                )
                console.print("  flow cancel -n '^test-.*-2024' --regex   # Complex matching")
                console.print(
                    "  flow cancel -n 'gpu-(test|prod)' --regex # Match gpu-test OR gpu-prod\n"
                )

                console.print(
                    "[yellow]Note: When using wildcards (default), quote them to prevent shell expansion:[/yellow]"
                )
                console.print("  [green]✓ CORRECT:[/green]  flow cancel -n 'gpu-test-*'")
                console.print(
                    "  [red]✗ WRONG:[/red]    flow cancel -n gpu-test-*   # Shell expands *\n"
                )

                console.print("[bold]Batch operations:[/bold]")
                console.print(
                    "  flow cancel --all                       # Cancel all (with confirmation)"
                )
                console.print("  flow cancel --all --yes                 # Force cancel all\n")

                console.print("[bold]Common workflows:[/bold]")
                console.print("  • Cancel all dev tasks: flow cancel -n 'dev-*' --yes")
                console.print("  • Clean up test tasks: flow cancel -n '*test*' --yes")
                console.print("  • Cancel specific prefix: flow cancel -n 'training-v2-*' --yes")
                console.print("  • Cancel by suffix: flow cancel -n '*-temp' --yes\n")
                return

            # Interactive toggle via flag overrides autodetect
            if interactive is True:
                os.environ["FLOW_FORCE_INTERACTIVE"] = "true"
            elif interactive is False:
                os.environ["FLOW_NONINTERACTIVE"] = "1"

            # Selection grammar: allow batch cancel via indices (works after 'flow status')
            if task_identifier:
                from flow.cli.utils.selection_helpers import parse_selection_to_task_ids

                ids, err = parse_selection_to_task_ids(task_identifier)
                if err:
                    from flow.cli.utils.theme_manager import theme_manager as _tm_err

                    error_color = _tm_err.get_color("error")
                    console.print(f"[{error_color}]{err}[/{error_color}]")
                    return
                if ids is not None:
                    # Echo expansion
                    cache = TaskIndexCache()
                    display_names: list[str] = []
                    for tid in ids:
                        cached = cache.get_cached_task(tid)
                        name = (cached or {}).get("name") if cached else None
                        display_names.append(name or (tid[:12] + "…"))
                    console.print(
                        f"[dim]Selection {task_identifier} → {', '.join(display_names)}[/dim]"
                    )
                    # Confirm unless --yes
                    if not yes:
                        if not click.confirm(f"Cancel {len(ids)} task(s)?"):
                            console.print("[dim]Cancellation aborted[/dim]")
                            return
                    # Execute cancellations one by one
                    # Reuse one Flow client instance (patchable in tests)
                    _client = Flow()
                    for tid in ids:
                        try:
                            self.execute_on_task(
                                task=_client.get_task(tid),
                                client=_client,
                                yes=True,
                                suppress_next_steps=True,
                            )
                        except Exception as e:
                            from rich.markup import escape

                            from flow.cli.utils.theme_manager import theme_manager as _tm_fail

                            error_color = _tm_fail.get_color("error")
                            console.print(
                                f"[{error_color}]✗[/{error_color}] Failed to cancel {tid[:12]}…: {escape(str(e))}"
                            )
                    # Show next steps once after batch
                    self.show_next_actions(
                        [
                            "View all tasks: [accent]flow status[/accent]",
                            "Submit a new task: [accent]flow run task.yaml[/accent]",
                        ]
                    )
                    return

            self._execute(task_identifier, yes, all, name_pattern, regex)

        return cancel

    # TaskSelectorMixin implementation
    def get_task_filter(self):
        """Only show cancellable tasks."""
        return TaskFilter.cancellable

    def get_selection_title(self) -> str:
        return "Select a task to cancel"

    def get_no_tasks_message(self) -> str:
        return "No running tasks to cancel"

    # Command execution
    def execute_on_task(self, task: Task, client: Flow, **kwargs) -> None:
        """Execute cancellation on the selected task."""
        yes = kwargs.get("yes", False)
        suppress_next_steps = kwargs.get("suppress_next_steps", False)

        # Double-check task is still cancellable
        if task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            status_str = str(task.status).replace("TaskStatus.", "").lower()
            console.print(
                f"[yellow]Task '{task.name or task.task_id}' is already {status_str}[/yellow]"
            )
            return

        # Show confirmation with task details
        if not yes:
            self._show_cancel_confirmation(task)

            # Simple, focused confirmation prompt
            if not click.confirm("\nProceed with cancellation?", default=False):
                console.print("[dim]Cancellation aborted[/dim]")
                return

        # Show progress
        from flow.cli.utils.animated_progress import AnimatedEllipsisProgress

        with AnimatedEllipsisProgress(
            console, "Cancelling task", start_immediately=True
        ) as progress:
            client.cancel(task.task_id)
            # Reflect cancellation in the local task object for immediate UX/tests
            try:
                task.status = TaskStatus.CANCELLED
            except Exception:
                pass

        # Success message
        from flow.cli.utils.theme_manager import theme_manager as _tm

        success_color = _tm.get_color("success")
        console.print(
            f"\n[{success_color}]✓[/{success_color}] Successfully cancelled [bold]{task.name or task.task_id}[/bold]"
        )

        # Show next actions (suppress in batch mode)
        if not suppress_next_steps:
            self.show_next_actions(
                [
                    "View all tasks: [accent]flow status[/accent]",
                    "Submit a new task: [accent]flow run task.yaml[/accent]",
                ]
            )

        # Invalidate stale task lists and trigger a refresh after cancellation
        try:
            from flow.cli.utils.prefetch import (
                invalidate_cache_for_current_context,
                refresh_active_task_caches,
                refresh_all_tasks_cache,
            )

            invalidate_cache_for_current_context(["tasks_running", "tasks_pending", "tasks_all"])
            import threading

            def _refresh():
                try:
                    refresh_active_task_caches()
                    refresh_all_tasks_cache()
                except Exception:
                    pass

            threading.Thread(target=_refresh, daemon=True).start()
        except Exception:
            pass

    def _show_cancel_confirmation(self, task: Task) -> None:
        """Show a confirmation panel with task details."""
        from datetime import datetime, timezone

        from rich.panel import Panel
        from rich.table import Table

        from flow.cli.utils.time_formatter import TimeFormatter

        time_fmt = TimeFormatter()

        # Create a clean table for task details
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column(style="bold")
        table.add_column()

        # Task name
        table.add_row("Task", task.name or "Unnamed task")

        # GPU type - show total GPUs if multiple instances
        from flow.cli.utils.gpu_formatter import GPUFormatter

        gpu_display = GPUFormatter.format_ultra_compact(
            task.instance_type, getattr(task, "num_instances", 1)
        )
        table.add_row("GPU", gpu_display)

        # Status
        status_display = self.task_formatter.format_status_with_color(task.status.value)
        table.add_row("Status", status_display)

        # Duration and cost
        duration = time_fmt.calculate_duration(task)
        table.add_row("Duration", duration)

        # Calculate approximate cost if available
        if (
            hasattr(task, "price_per_hour")
            and task.price_per_hour
            and task.status == TaskStatus.RUNNING
        ):
            if task.started_at:
                start = task.started_at
                if hasattr(start, "tzinfo") and start.tzinfo is None:
                    start = start.replace(tzinfo=timezone.utc)

                now = datetime.now(timezone.utc)
                hours_run = (now - start).total_seconds() / 3600
                cost_so_far = hours_run * task.price_per_hour

                table.add_row("Cost so far", f"${cost_so_far:.2f}")
                table.add_row("Hourly rate", f"${task.price_per_hour:.2f}/hr")

        # Create panel with calmer themed colors
        from flow.cli.utils.theme_manager import theme_manager as _tm

        warning_color = _tm.get_color("warning")
        border_color = _tm.get_color("table.border")
        panel = Panel(
            table,
            title=f"[bold {warning_color}]⚠  Cancel Task[/bold {warning_color}]",
            title_align="center",
            border_style=border_color,
            padding=(1, 2),
        )

        console.print()
        console.print(panel)

    def _execute(
        self,
        task_identifier: str,
        yes: bool,
        all: bool,
        name_pattern: str,
        regex: bool,
    ) -> None:
        """Execute the cancel command."""
        if all:
            self._execute_cancel_all(yes)
        elif name_pattern:
            self._execute_cancel_pattern(name_pattern, yes, regex)
        else:
            # Prefer direct path to allow tests to patch Flow and resolver cleanly
            if task_identifier:
                try:
                    client = Flow()
                    task = self.resolve_task(task_identifier, client)
                    self.execute_on_task(task, client, yes=yes)
                except AuthenticationError:
                    self.handle_auth_error()
                except Exception as e:
                    self.handle_error(str(e))
            else:
                # Fallback to interactive selection via mixin
                self.execute_with_selection(task_identifier, yes=yes, flow_class=Flow)

    # Override resolve_task to import resolver from its canonical module so tests can patch it there
    def resolve_task(self, task_identifier: str | None, client: Flow, allow_multiple: bool = False):  # type: ignore[override]
        if task_identifier:
            from flow.cli.utils.task_resolver import (
                resolve_task_identifier as resolver,  # type: ignore
            )

            task, error = resolver(client, task_identifier)
            if error:
                from flow.cli.commands.base import console as _console

                _console.print(f"[red]✗ Error:[/red] {error}")
                raise SystemExit(1)
            return task
        # Fallback to base mixin behavior for interactive selection
        return super().resolve_task(task_identifier, client, allow_multiple)

    def _execute_cancel_all(self, yes: bool) -> None:
        """Handle --all flag separately as it's a special case."""
        from flow.cli.utils.animated_progress import AnimatedEllipsisProgress

        try:
            # Start animation immediately
            with AnimatedEllipsisProgress(
                console, "Finding all cancellable tasks", start_immediately=True
            ) as progress:
                client = Flow()

                # Get cancellable tasks using TaskFetcher for consistent behavior
                from flow.cli.utils.task_fetcher import TaskFetcher

                fetcher = TaskFetcher(client)
                all_tasks = fetcher.fetch_all_tasks(limit=1000, prioritize_active=True)
                cancellable = TaskFilter.cancellable(all_tasks)

            if not cancellable:
                from flow.cli.utils.theme_manager import theme_manager as _tm_warn

                warn = _tm_warn.get_color("warning")
                console.print(f"[{warn}]No running tasks to cancel[/{warn}]")
                return

            # Confirm
            if not yes:
                if not click.confirm(f"Cancel {len(cancellable)} running tasks?"):
                    console.print("Cancelled")
                    return

            # Cancel each task with progress
            from flow.cli.utils.animated_progress import AnimatedEllipsisProgress

            cancelled_count = 0
            failed_count = 0

            with AnimatedEllipsisProgress(
                console, f"Cancelling {len(cancellable)} tasks", start_immediately=True
            ) as progress:
                for i, task in enumerate(cancellable):
                    task_name = task.name or task.task_id
                    progress.base_message = f"Cancelling {task_name} ({i + 1}/{len(cancellable)})"

                    try:
                        client.cancel(task.task_id)
                        cancelled_count += 1
                    except Exception as e:
                        from rich.markup import escape

                        from flow.cli.utils.theme_manager import theme_manager as _tm_fail2

                        err = _tm_fail2.get_color("error")
                        console.print(
                            f"[{err}]✗[/{err}] Failed to cancel {task_name}: {escape(str(e))}"
                        )
                        failed_count += 1

            # Summary
            console.print()
            if cancelled_count > 0:
                from flow.cli.utils.theme_manager import theme_manager as _tm2

                success_color = _tm2.get_color("success")
                console.print(
                    f"[{success_color}]✓[/{success_color}] Successfully cancelled {cancelled_count} task(s)"
                )
            if failed_count > 0:
                from flow.cli.utils.theme_manager import theme_manager as _tm_fail3

                err = _tm_fail3.get_color("error")
                console.print(f"[{err}]✗[/{err}] Failed to cancel {failed_count} task(s)")

            # Show next actions
            self.show_next_actions(
                [
                    "View all tasks: [accent]flow status[/accent]",
                    "Submit a new task: [accent]flow run task.yaml[/accent]",
                ]
            )

        except AuthenticationError:
            self.handle_auth_error()
        except Exception as e:
            self.handle_error(str(e))

    def _execute_cancel_pattern(self, pattern: str, yes: bool, use_regex: bool) -> None:
        """Cancel tasks matching a name pattern."""
        from flow.cli.utils.animated_progress import AnimatedEllipsisProgress

        try:
            # Start animation immediately
            with AnimatedEllipsisProgress(
                console, f"Finding tasks matching: {pattern}", start_immediately=True
            ) as progress:
                client = Flow()

                # Get cancellable tasks
                from flow.cli.utils.task_fetcher import TaskFetcher

                fetcher = TaskFetcher(client)
                all_tasks = fetcher.fetch_all_tasks(limit=1000, prioritize_active=True)
                cancellable = TaskFilter.cancellable(all_tasks)

            if not cancellable:
                from flow.cli.utils.theme_manager import theme_manager as _tm_warn2

                warn = _tm_warn2.get_color("warning")
                console.print(f"[{warn}]No running tasks to cancel[/{warn}]")
                return

            # Filter by pattern
            matching_tasks = []
            for task in cancellable:
                if task.name:
                    if use_regex:
                        # Use regex matching when requested
                        try:
                            if re.search(pattern, task.name):
                                matching_tasks.append(task)
                        except re.error as e:
                            from rich.markup import escape

                            from flow.cli.utils.theme_manager import theme_manager as _tm_err2

                            err = _tm_err2.get_color("error")
                            console.print(f"[{err}]Invalid regex pattern: {escape(str(e))}[/{err}]")
                            return
                    else:
                        # Default to wildcard matching
                        if fnmatch.fnmatch(task.name, pattern):
                            matching_tasks.append(task)

            if not matching_tasks:
                from flow.cli.utils.theme_manager import theme_manager as _tm_warn3

                warn = _tm_warn3.get_color("warning")
                console.print(f"[{warn}]No running tasks match pattern '{pattern}'[/{warn}]")

                # Help users debug common issues
                if "*" in pattern or "?" in pattern:
                    console.print("\n[dim]Tip: If you're seeing this after shell expansion failed,")
                    console.print(
                        "     make sure to quote your pattern: flow cancel -n 'pattern*'[/dim]"
                    )

                # Show what tasks ARE available
                sample_names = [t.name for t in cancellable[:5] if t.name]
                if sample_names:
                    console.print(
                        f"\n[dim]Available task names: {', '.join(sample_names)}"
                        f"{' ...' if len(cancellable) > 5 else ''}[/dim]"
                    )
                return

            # Show matching tasks
            console.print(
                f"\n[bold]Found {len(matching_tasks)} task(s) matching pattern '[accent]{pattern}[/accent]':[/bold]\n"
            )
            from rich.table import Table

            table = Table(show_header=True, box=None)
            table.add_column("Task Name", style="cyan")
            table.add_column("Task ID", style="dim")
            table.add_column("Status")
            table.add_column("GPU Type")

            for task in matching_tasks:
                from flow.cli.utils.gpu_formatter import GPUFormatter

                status_display = self.task_formatter.format_status_with_color(task.status.value)
                gpu_display = GPUFormatter.format_ultra_compact(
                    task.instance_type, getattr(task, "num_instances", 1)
                )
                table.add_row(
                    task.name or "Unnamed",
                    task.task_id[:12] + "...",
                    status_display,
                    gpu_display,
                )

            console.print(table)
            console.print()

            # Confirm
            if not yes:
                if not click.confirm(f"Cancel {len(matching_tasks)} matching task(s)?"):
                    console.print("[dim]Cancellation aborted[/dim]")
                    return

            # Cancel each task with progress
            from flow.cli.utils.animated_progress import AnimatedEllipsisProgress

            cancelled_count = 0
            failed_count = 0

            with AnimatedEllipsisProgress(
                console, f"Cancelling {len(matching_tasks)} matching tasks", start_immediately=True
            ) as progress:
                for i, task in enumerate(matching_tasks):
                    task_name = task.name or task.task_id
                    progress.base_message = (
                        f"Cancelling {task_name} ({i + 1}/{len(matching_tasks)})"
                    )

                    try:
                        client.cancel(task.task_id)
                        cancelled_count += 1
                    except Exception as e:
                        from rich.markup import escape

                        from flow.cli.utils.theme_manager import theme_manager as _tm_err3

                        err = _tm_err3.get_color("error")
                        console.print(
                            f"[{err}]✗[/{err}] Failed to cancel {task_name}: {escape(str(e))}"
                        )
                        failed_count += 1

            # Summary
            console.print()
            if cancelled_count > 0:
                from flow.cli.utils.theme_manager import theme_manager as _tm3

                success_color = _tm3.get_color("success")
                console.print(
                    f"[{success_color}]✓[/{success_color}] Successfully cancelled {cancelled_count} task(s)"
                )
            if failed_count > 0:
                from flow.cli.utils.theme_manager import theme_manager as _tm_err4

                err = _tm_err4.get_color("error")
                console.print(f"[{err}]✗[/{err}] Failed to cancel {failed_count} task(s)")

            # Show next actions
            self.show_next_actions(
                [
                    "View all tasks: [accent]flow status[/accent]",
                    "Submit a new task: [accent]flow run task.yaml[/accent]",
                ]
            )

        except AuthenticationError:
            self.handle_auth_error()
        except Exception as e:
            self.handle_error(str(e))


# Export command instance
command = CancelCommand()
