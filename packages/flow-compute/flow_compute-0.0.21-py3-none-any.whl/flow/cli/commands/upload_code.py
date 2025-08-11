"""Upload code command for transferring local code to running tasks.

This command provides manual code upload functionality using SCP/rsync,
useful for updating code on long-running instances without restarting.
"""

from pathlib import Path

import click

from flow.api.client import Flow
from flow.cli.commands.base import BaseCommand, console
from flow.cli.utils.step_progress import StepTimeline, UploadProgressReporter
from flow.cli.utils.task_selector_mixin import TaskOperationCommand
from flow.errors import FlowError


class UploadCodeCommand(BaseCommand, TaskOperationCommand):
    """Upload code to a running task.

    Transfers local code to a running GPU instance using efficient
    rsync-based transfer with progress reporting.
    """

    @property
    def name(self) -> str:
        return "upload-code"

    @property
    def help(self) -> str:
        return "Upload local code to running tasks - incremental sync via rsync"

    @property
    def manages_own_progress(self) -> bool:
        """Upload-code manages its own progress display for smooth transitions."""
        return True

    # TaskSelectorMixin implementation
    def get_task_filter(self):
        """Only show running tasks with SSH access."""
        from flow.cli.utils.task_selector_mixin import TaskFilter

        return TaskFilter.RUNNING

    def get_selection_title(self) -> str:
        return "Select a task to upload code to"

    def get_no_tasks_message(self) -> str:
        return "No running tasks found. Start a task first with 'flow run'"

    def execute_on_task(self, task, client: Flow, **kwargs) -> None:
        """Execute code upload on the selected task."""
        source_dir = kwargs.get("source")
        timeout = kwargs.get("timeout", 600)

        # Validate source directory
        if source_dir:
            source_path = Path(source_dir).resolve()
            if not source_path.exists():
                raise FlowError(f"Source directory does not exist: {source_path}")
            if not source_path.is_dir():
                raise FlowError(f"Source must be a directory: {source_path}")
        else:
            source_path = Path.cwd()

        console.print(f"[dim]Uploading code from {source_path} to {task.task_id}[/dim]\n")

        # Unified transfer timeline with Ctrl+C hint
        timeline = StepTimeline(console, title="flow upload-code", title_animation="auto")
        timeline.start()
        upload_idx = timeline.add_step("Uploading code", show_bar=True)
        timeline.start_step(upload_idx)
        try:
            # Use provider's upload with timeline-based reporter and no provider console prints
            provider = client.provider
            reporter = UploadProgressReporter(timeline, upload_idx)
            # Hint about safe interruption
            try:
                from rich.text import Text

                from flow.cli.utils.theme_manager import theme_manager

                accent = theme_manager.get_color("accent")
                hint = Text()
                hint.append("  Press ")
                hint.append("Ctrl+C", style=accent)
                hint.append(" to cancel upload. Instance remains running; re-run ")
                hint.append("flow upload-code", style=accent)
                hint.append(" later.")
                timeline.set_active_hint_text(hint)
            except Exception:
                pass
            provider.upload_code_to_task(
                task_id=task.task_id,
                source_dir=source_path,
                timeout=timeout,
                console=None,
                progress_reporter=reporter,
            )
            # Next steps
            task_ref = task.name or task.task_id
            self.show_next_actions(
                [
                    f"SSH into instance: [accent]flow ssh {task_ref}[/accent]",
                    f"View logs: [accent]flow logs {task_ref} -f[/accent]",
                    "Run your updated code in the SSH session",
                ]
            )
        except KeyboardInterrupt:
            console.print(
                "\n[dim]Upload interrupted by user. Instance remains running. Re-run: flow upload-code[/dim]"
            )
        except Exception as e:
            # Check for dependency errors - providers should raise DependencyNotFoundError
            # but we handle string matching for backward compatibility
            if "rsync not found" in str(e):
                console.print("[red]Error:[/red] rsync is required for code upload\n")
                console.print("Install rsync:")
                console.print("  • macOS: [accent]brew install rsync[/accent]")
                console.print("  • Ubuntu/Debian: [accent]sudo apt-get install rsync[/accent]")
                console.print("  • RHEL/CentOS: [accent]sudo yum install rsync[/accent]")
            else:
                raise
        finally:
            timeline.finish()

    def get_command(self) -> click.Command:
        # Import completion function
        from flow.cli.utils.mode import demo_aware_command
        from flow.cli.utils.shell_completion import complete_task_ids

        @click.command(name=self.name, help=self.help)
        @click.argument("task_identifier", required=False, shell_complete=complete_task_ids)
        @click.option(
            "--source",
            "-s",
            type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
            help="Source directory to upload (default: current directory)",
        )
        @click.option(
            "--timeout",
            "-t",
            type=int,
            default=600,
            help="Upload timeout in seconds (default: 600)",
        )
        @click.option(
            "--verbose",
            "-v",
            is_flag=True,
            help="Show detailed upload patterns and troubleshooting",
        )
        @demo_aware_command()
        def upload_code(
            task_identifier: str | None, source: Path | None, timeout: int, verbose: bool
        ):
            """Upload code to a running task.

            TASK_IDENTIFIER: Task ID or name (optional - interactive selector if omitted)

            \\b
            Examples:
                flow upload-code                 # Interactive task selector
                flow upload-code my-training     # Upload to specific task
                flow upload-code -s ../lib       # Upload different directory
                flow upload-code -t 1200         # Longer timeout (20 min)

            Use 'flow upload-code --verbose' for advanced patterns and .flowignore guide.
            """
            if verbose:
                console.print("\n[bold]Code Upload Guide:[/bold]\n")
                console.print("Basic usage:")
                console.print("  flow upload-code                  # Upload current directory")
                console.print("  flow upload-code my-task          # Upload to specific task")
                console.print("  flow upload-code -s ~/project     # Upload different source\n")

                console.print("Upload behavior:")
                console.print("  • Destination: /workspace on the instance")
                console.print("  • Method: rsync with compression")
                console.print("  • Incremental: Only changed files uploaded")
                console.print("  • Progress: Real-time transfer status\n")

                console.print(".flowignore patterns:")
                console.print("  # Common patterns to exclude:")
                console.print("  .git/")
                console.print("  __pycache__/")
                console.print("  *.pyc")
                console.print("  .env")
                console.print("  venv/")
                console.print("  node_modules/")
                console.print("  *.log")
                console.print("  .DS_Store\n")

                console.print("Large project optimization:")
                console.print("  # Create minimal .flowignore")
                console.print("  echo 'data/' >> .flowignore       # Exclude large datasets")
                console.print("  echo 'models/' >> .flowignore     # Exclude model weights")
                console.print("  echo '.git/' >> .flowignore       # Exclude git history\n")

                console.print("Common workflows:")
                console.print("  # Hot reload during development")
                console.print("  flow upload-code && flow ssh task -c 'python train.py'")
                console.print("  ")
                console.print("  # Upload and monitor")
                console.print("  flow upload-code && flow logs task -f")
                console.print("  ")
                console.print("  # Sync specific module")
                console.print("  flow upload-code -s ./src/models\n")

                console.print("Troubleshooting:")
                console.print("  • Timeout errors → Increase with -t 1800 (30 min)")
                console.print("  • rsync not found → Install: brew/apt/yum install rsync")
                console.print("  • Permission denied → Check task is running: flow status")
                console.print("  • Upload too slow → Add more patterns to .flowignore\n")

                console.print("Next steps after upload:")
                console.print("  • Connect: flow ssh <task-name>")
                console.print("  • Run code: python your_script.py")
                console.print("  • Monitor: flow logs <task-name> -f\n")
                return

            self._execute(task_identifier, source=source, timeout=timeout)

        return upload_code

    def _execute(self, task_identifier: str | None, source: Path | None, timeout: int) -> None:
        """Execute the upload-code command."""
        self.execute_with_selection(task_identifier, source=source, timeout=timeout)


# Export command instance
command = UploadCodeCommand()
