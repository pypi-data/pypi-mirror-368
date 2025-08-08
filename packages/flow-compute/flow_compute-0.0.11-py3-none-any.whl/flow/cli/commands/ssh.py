"""SSH command for connecting to running GPU instances.

Provides secure shell access to running tasks for debugging and development.

Examples:
    Connect interactively:
        $ flow ssh task-abc123

    Execute remote command:
        $ flow ssh task-abc123 -c 'nvidia-smi'

    Check GPU utilization:
        $ flow ssh task-abc123 -c 'watch -n1 nvidia-smi'
"""

import sys
import os
from typing import Optional

import click

from flow import Flow
from flow.errors import FlowError
from flow.api.models import Task

from .base import BaseCommand, console
from ..provider_resolver import ProviderResolver
from ..utils.task_resolver import resolve_task_identifier
from ..utils.task_formatter import TaskFormatter
from ..utils.interactive_selector import select_task
from ..utils.task_selector_mixin import TaskOperationCommand, TaskFilter
from ..utils.animated_progress import AnimatedEllipsisProgress
from ..utils.task_index_cache import TaskIndexCache
from flow.cli.utils.selection import Selection, SelectionParseError


class SSHCommand(BaseCommand, TaskOperationCommand):
    """SSH command implementation.

    Handles both interactive sessions and remote command execution.
    Requires task to be in running state with SSH keys configured.
    """

    def __init__(self):
        """Initialize command with formatter."""
        super().__init__()
        self.task_formatter = TaskFormatter()

    @property
    def name(self) -> str:
        return "ssh"

    @property
    def manages_own_progress(self) -> bool:
        """SSH manages its own progress display."""
        return True

    @property
    def help(self) -> str:
        return """SSH to running GPU instances - Interactive shell or remote command execution

Quick connect:
  flow ssh                         # Interactive task selector
  flow ssh my-training             # Connect by task name
  flow ssh abc-123                 # Connect by task ID

Remote commands:
  flow ssh task -c 'nvidia-smi'    # Check GPU status
  flow ssh task -c 'htop'          # Monitor system resources
  flow ssh task --node 1           # Connect to specific node (multi-instance)"""

    # TaskSelectorMixin implementation
    def get_task_filter(self):
        """Only show tasks with SSH access."""
        return TaskFilter.with_ssh

    def get_selection_title(self) -> str:
        return "Select a running task to SSH into"

    def get_no_tasks_message(self) -> str:
        return "No running tasks available for SSH"

    # Command execution
    def execute_on_task(self, task: Task, client: Flow, **kwargs) -> None:
        """Execute SSH connection on the selected task."""
        command = kwargs.get("command")
        node = kwargs.get("node", 0)

        # Validate node parameter for multi-instance tasks
        if hasattr(task, "num_instances") and task.num_instances > 1:
            if node < 0 or node >= task.num_instances:
                console.print(
                    f"[red]Error: Node index {node} out of bounds (task has {task.num_instances} nodes)[/red]"
                )
                console.print(f"Valid nodes: 0-{task.num_instances - 1}")
                raise SystemExit(1)
            # Include node in display for multi-instance tasks
            task_display = f"{self.task_formatter.format_task_display(task)} [node {node}]"
        else:
            # Single-instance task
            if node != 0:
                console.print(
                    f"[red]Error: Task '{task.name or task.task_id}' is single-instance[/red]"
                )
                console.print("Remove --node flag for single-instance tasks")
                raise SystemExit(1)
            task_display = self.task_formatter.format_task_display(task)

        # Check SSH capability and wait for IP if needed
        if not task.ssh_host:
            # Import shared SSH utilities
            from flow import check_task_age_for_ssh

            # Check task age to provide appropriate message
            age_message = check_task_age_for_ssh(task)

            if age_message:
                # Check if it's a stuck pending task
                if "stuck in queue" in age_message:
                    console.print(f"\n[red]{age_message}[/red]")
                    console.print("\nPossible issues:")
                    console.print("  • No available GPU resources matching your requirements")
                    console.print("  • Bid price too low for current market conditions")
                    console.print("  • Provider capacity exhausted in selected regions")
                    console.print("\nRecommended actions:")
                    console.print(
                        f"  • Check task details: [cyan]flow status {task.name or task.task_id}[/cyan]"
                    )
                    console.print(
                        f"  • Cancel and retry with different parameters: [cyan]flow cancel {task.name or task.task_id}[/cyan]"
                    )
                    console.print(
                        "  • Try a different instance type or increase max_price_per_hour"
                    )
                    console.print("  • Consider using a different region")
                    raise SystemExit(1)
                elif "unexpected" in age_message:
                    # Instance has been running for a while without SSH
                    console.print(f"\n[red]{age_message}[/red]")
                    console.print("\nPossible issues:")
                    console.print("  • Instance may have been preempted or terminated")
                    console.print("  • SSH service may have crashed")
                    console.print("  • Network configuration issues")
                    console.print("\nRecommended actions:")
                    console.print(
                        f"  • Check instance health: [cyan]flow health {task.name or task.task_id}[/cyan]"
                    )
                    console.print(
                        f"  • View logs: [cyan]flow logs {task.name or task.task_id}[/cyan]"
                    )
                    console.print(
                        f"  • Consider restarting: [cyan]flow cancel {task.name or task.task_id} && flow dev[/cyan]"
                    )
                    raise SystemExit(1)
            else:
                # Instance might still be provisioning - wait for IP assignment
                from flow import DEFAULT_PROVISION_MINUTES as EXPECTED_PROVISION_MINUTES

                console.print(
                    f"\n[yellow]Instance is provisioning[/yellow] (waiting for IP assignment)"
                )
                console.print(
                    f"This can take up to {EXPECTED_PROVISION_MINUTES} minutes for Mithril instances."
                )
                if age_message:
                    console.print(age_message)
                console.print("[dim]Press Ctrl+C to cancel[/dim]\n")

            from flow import SSHNotReadyError

            try:
                # Use client's public method to wait for SSH with elapsed anchored to created_at
                # The underlying progress uses task.created_at when provided
                task = client.wait_for_ssh(
                    task_id=task.task_id,
                    timeout=300,  # 5 minutes for SSH
                    show_progress=True,  # This will use built-in AnimatedEllipsisProgress
                )

                if task.ssh_host:
                    console.print("[green]✓[/green] IP assigned!")

            except SSHNotReadyError as e:
                if "interrupted by user" in str(e).lower():
                    console.print("\n[cyan]✗ SSH wait interrupted[/cyan]")
                    console.print(
                        "\nThe instance should still be provisioning. You can check later with:"
                    )
                    console.print(f"  [cyan]flow ssh {task.name or task.task_id}[/cyan]")
                    console.print(f"  [cyan]flow status {task.name or task.task_id}[/cyan]")
                else:
                    console.print(f"\n[red]✗ {str(e)}[/red]")
                    console.print("\nPossible issues:")
                    console.print("  • Instance is stuck in provisioning")
                    console.print("  • Task was created without SSH keys")
                    console.print("  • Cloud provider resource limits reached")
                    console.print(
                        f"\nCheck task status: [cyan]flow status {task.name or task.task_id}[/cyan]"
                    )
                raise SystemExit(1)

        # Now we have an IP, update display
        task_display = self.task_formatter.format_task_display(task)

        if command:
            # Run command remotely - no progress needed for non-interactive
            client.shell(task.task_id, command=command, node=node)
        else:
            # Interactive SSH - animation already started in _execute if applicable
            progress = kwargs.get("progress_context")

            if not progress:
                # Fallback if called directly without animation
                progress = AnimatedEllipsisProgress(
                    console, f"Connecting to {task_display}", transient=True
                )
                progress.__enter__()

            try:
                # This will run SSH preparation, then stop animation before subprocess
                client.shell(task.task_id, node=node, progress_context=progress)
            except Exception as e:
                # Ensure animation stops on error if we started it
                if not kwargs.get("animation_started"):
                    progress.__exit__(None, None, None)
                # Get provider for error handling
                provider_name = "mithril"  # Currently only Mithril provider supports SSH

                # Show connection command for manual debugging
                connection_cmd = ProviderResolver.get_connection_command(provider_name, task)
                if connection_cmd:
                    console.print(
                        "\n[yellow]Connection failed. You can try connecting manually with:[/yellow]"
                    )
                    console.print(f"  {connection_cmd}\n")

                # Re-raise the original exception
                raise

        # Show next actions after SSH session ends
        if not command:  # Only show after interactive sessions
            task_ref = task.name or task.task_id
            self.show_next_actions(
                [
                    f"View logs: [cyan]flow logs {task_ref} --follow[/cyan]",
                    f"Check status: [cyan]flow status {task_ref}[/cyan]",
                    f"Run nvidia-smi: [cyan]flow ssh {task_ref} -c 'nvidia-smi'[/cyan]",
                ]
            )

    def get_command(self) -> click.Command:
        # Import completion function
        from ..utils.shell_completion import complete_task_ids

        @click.command(name=self.name, help=self.help)
        @click.argument("task_identifier", required=False, shell_complete=complete_task_ids)
        @click.option("--command", "-c", help="Command to run on remote host")
        @click.option(
            "--node", type=int, default=0, help="Node index for multi-instance tasks (default: 0)"
        )
        @click.option("--verbose", "-v", is_flag=True, help="Show detailed help and examples")
        def ssh(task_identifier: Optional[str], command: Optional[str], node: int, verbose: bool):
            """SSH to a running task.

            TASK_IDENTIFIER: Task ID or name (optional - interactive selector if omitted)

            \b
            Examples:
                flow ssh                    # Interactive task selector
                flow ssh my-training        # Connect by name
                flow ssh task-abc123        # Connect by ID
                flow ssh task -c 'nvidia-smi'  # Run command remotely

            Use 'flow ssh --verbose' for troubleshooting and advanced examples.
            """
            if verbose:
                console.print("\n[bold]Advanced SSH Usage:[/bold]\n")
                console.print("Multi-instance tasks:")
                console.print("  flow ssh distributed-job --node 1    # Connect to worker node")
                console.print(
                    "  flow ssh task -c 'hostname' --node 2 # Run command on specific node\n"
                )

                console.print("File transfer:")
                console.print("  scp file.py $(flow ssh task -c 'echo $USER@$HOSTNAME'):~/")
                console.print(
                    "  rsync -av ./data/ $(flow ssh task -c 'echo $USER@$HOSTNAME'):/data/\n"
                )

                console.print("Port forwarding:")
                console.print(
                    "  ssh -L 8888:localhost:8888 $(flow ssh task -c 'echo $USER@$HOSTNAME')"
                )
                console.print(
                    "  ssh -L 6006:localhost:6006 $(flow ssh task -c 'echo $USER@$HOSTNAME')  # TensorBoard\n"
                )

                console.print("Monitoring:")
                console.print("  flow ssh task -c 'watch -n1 nvidia-smi'    # GPU usage")
                console.print("  flow ssh task -c 'htop'                     # System resources")
                console.print("  flow ssh task -c 'tail -f output.log'       # Stream logs\n")

                console.print("Troubleshooting:")
                console.print("  • No SSH info? Wait 2-5 minutes for instance provisioning")
                console.print("  • Permission denied? Run: flow ssh-keys upload ~/.ssh/id_rsa.pub")
                console.print("  • Connection refused? Check: flow health --task <name>")
                console.print("  • Task terminated? Check: flow status <name>\n")
                return

            # Selection support (works after 'flow status')
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
                                console.print("[red]Selection must resolve to exactly one task for ssh[/red]")
                                return
                            task_identifier = task_ids[0]
                    except SelectionParseError:
                        # Fall through to normal resolution
                        pass

            self._execute(task_identifier, command, node)

        return ssh

    def _execute(
        self, task_identifier: Optional[str], command: Optional[str], node: int = 0
    ) -> None:
        """Execute SSH connection or command."""
        # For non-interactive commands, use standard flow
        if command:
            self.execute_with_selection(task_identifier, command=command, node=node)
            return

        # For interactive SSH, start animation IMMEDIATELY
        from ..utils.animated_progress import AnimatedEllipsisProgress
        from ..utils.task_index_cache import TaskIndexCache

        # Get display name from cache for instant feedback
        display_msg = "Connecting"
        if task_identifier:
            cache = TaskIndexCache()

            if task_identifier.startswith(":"):
                task_id, _ = cache.resolve_index(task_identifier)
                if task_id:
                    cached_task = cache.get_cached_task(task_id)
                    if cached_task:
                        display_msg = (
                            f"Connecting to {cached_task.get('name', task_id)} ({task_id[:12]})"
                        )
                    else:
                        display_msg = f"Connecting to {task_id[:12]}"
            else:
                cached_task = cache.get_cached_task(task_identifier)
                if cached_task:
                    display_msg = f"Connecting to {cached_task.get('name', task_identifier)} ({task_identifier[:12]})"
                else:
                    display_msg = f"Connecting to {task_identifier}"

            # Add node info if multi-instance and non-default node
            if node != 0:
                display_msg += f" [node {node}]"

        # Start animation immediately - before any network calls
        progress = AnimatedEllipsisProgress(
            console, display_msg, transient=True, start_immediately=True
        )

        try:
            # Store progress in kwargs so execute_on_task can access it
            self.execute_with_selection(
                task_identifier,
                command=command,
                node=node,
                progress_context=progress,
                animation_started=True,
            )
        except Exception:
            # Ensure animation stops on any error
            progress.__exit__(None, None, None)
            raise


# Export command instance
command = SSHCommand()
