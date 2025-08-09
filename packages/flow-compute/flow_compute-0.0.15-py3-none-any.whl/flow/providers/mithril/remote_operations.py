"""Mithril-specific implementation of remote operations via SSH.

This module provides SSH-based remote operations for Mithril tasks,
implementing the IRemoteOperations protocol with Mithril-specific behavior.
"""

import logging
import subprocess
import time
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from flow.core.provider_interfaces import IRemoteOperations
from flow.errors import FlowError
from .ssh_waiter import ExponentialBackoffSSHWaiter
from .ssh_utils import wait_for_task_ssh_info, SSHNotReadyError
from .core.constants import (
    SSH_READY_WAIT_SECONDS,
    SSH_CHECK_INTERVAL,
    SSH_QUICK_RETRY_ATTEMPTS,
    SSH_QUICK_RETRY_MAX_SECONDS,
    EXPECTED_PROVISION_MINUTES,
)

if TYPE_CHECKING:
    from .provider import MithrilProvider

logger = logging.getLogger(__name__)


class RemoteExecutionError(FlowError):
    """Raised when remote command execution fails."""

    pass


class TaskNotFoundError(FlowError):
    """Raised when task cannot be found."""

    pass


class MithrilRemoteOperations(IRemoteOperations):
    """Mithril remote operations via SSH."""

    def __init__(self, provider: "MithrilProvider"):
        """Initialize with provider reference.

        Args:
            provider: Mithril provider instance for task access
        """
        self.provider = provider

    def execute_command(self, task_id: str, command: str, timeout: Optional[int] = None) -> str:
        """Execute command on remote task via SSH.

        Args:
            task_id: Task identifier
            command: Command to execute
            timeout: Optional timeout in seconds

        Returns:
            Command output (stdout)

        Raises:
            TaskNotFoundError: Task doesn't exist
            RemoteExecutionError: Command failed
            TimeoutError: Command timed out
        """
        task = self.provider.get_task(task_id)

        # First ensure task has SSH info using shared utility
        try:
            # For commands, use a shorter timeout than interactive SSH
            task = wait_for_task_ssh_info(
                task=task,
                provider=self.provider,
                timeout=SSH_QUICK_RETRY_MAX_SECONDS
                * 2,  # Give it a bit more time than quick retries
                check_interval=2,  # Check more frequently for commands
            )
        except SSHNotReadyError as e:
            raise RemoteExecutionError(
                f"No SSH access for task {task_id}: {str(e)}", suggestions=e.suggestions
            ) from e

        # Get the SSH key path for this task
        ssh_key_path, error_msg = self.provider.get_task_ssh_connection_info(task_id)
        if not ssh_key_path:
            raise RemoteExecutionError(f"SSH key resolution failed: {error_msg}")

        # Now check if SSH service is ready (connection test)
        if not self._is_ssh_ready(task, ssh_key_path):
            # SSH info exists but service not ready - do quick retries
            start_time = time.time()
            for attempt in range(SSH_QUICK_RETRY_ATTEMPTS):
                elapsed = time.time() - start_time
                if elapsed > SSH_QUICK_RETRY_MAX_SECONDS:
                    break

                time.sleep(2 * (attempt + 1))  # Exponential backoff: 2, 4, 6, 8, 10 seconds
                if self._is_ssh_ready(task, ssh_key_path):
                    break
            else:
                # Still not ready after quick retries
                # Check instance age to provide better messaging
                instance_age_seconds = task.instance_age_seconds
                instance_age_minutes = (
                    int(instance_age_seconds / 60) if instance_age_seconds else None
                )

                # Check if we have instance status information
                instance_status = task.instance_status if hasattr(task, "instance_status") else None

                if instance_status == "STATUS_STARTING":
                    # Instance is explicitly in starting state
                    raise RemoteExecutionError(
                        f"Instance is starting up. SSH will be available once startup completes. "
                        f"Please try again in a moment or check 'flow status' for current state."
                    )
                elif (
                    instance_age_minutes is not None
                    and instance_age_minutes < EXPECTED_PROVISION_MINUTES
                ):
                    # Instance is still within normal startup time
                    raise RemoteExecutionError(
                        f"Instance is still starting up ({instance_age_minutes} minutes elapsed). "
                        f"SSH startup can take up to {EXPECTED_PROVISION_MINUTES} minutes. "
                        f"Please try again in a moment."
                    )
                else:
                    # Instance is older or age unknown - use generic message
                    raise RemoteExecutionError(
                        f"SSH service on {task.ssh_host} is not responding. "
                        f"The instance may still be starting up (can take up to {EXPECTED_PROVISION_MINUTES} minutes). "
                        f"Please try again in a moment."
                    )

        ssh_cmd = [
            "ssh",
            "-p",
            str(task.ssh_port),
            "-i",
            str(ssh_key_path),  # Add the SSH key
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "ConnectTimeout=10",
            "-o",
            "ServerAliveInterval=10",
            "-o",
            "ServerAliveCountMax=3",
            f"{task.ssh_user}@{task.ssh_host}",
            command,
        ]

        if timeout:
            ssh_cmd = ["timeout", str(timeout)] + ssh_cmd

        try:
            result = subprocess.run(ssh_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                # Check for common SSH errors
                stderr = result.stderr.lower()
                if "connection closed" in stderr or "connection reset" in stderr:
                    raise RemoteExecutionError(
                        f"SSH connection was closed. The instance may still be starting up. "
                        f"Please wait a moment and try again."
                    )
                raise RemoteExecutionError(f"Command failed: {result.stderr}")
            return result.stdout
        except subprocess.TimeoutExpired as e:
            raise TimeoutError(f"Command timed out after {timeout} seconds") from e
        except Exception as e:
            raise RemoteExecutionError(f"SSH execution failed: {str(e)}") from e

    def retrieve_file(self, task_id: str, remote_path: str) -> bytes:
        """Retrieve file from remote task via SSH.

        Args:
            task_id: Task identifier
            remote_path: Path to file on remote system

        Returns:
            File contents as bytes

        Raises:
            TaskNotFoundError: Task doesn't exist
            FileNotFoundError: Remote file doesn't exist
            RemoteExecutionError: Retrieval failed
        """
        # Use SSH cat to retrieve file
        try:
            output = self.execute_command(task_id, f"cat {remote_path}")
            return output.encode("utf-8")
        except RemoteExecutionError as e:
            if "No such file" in str(e) or "cannot open" in str(e):
                raise FileNotFoundError(f"Remote file not found: {remote_path}") from e
            raise

    def open_shell(
        self, task_id: str, command: Optional[str] = None, progress_context=None
    ) -> None:
        """Open interactive SSH shell to remote task.

        Args:
            task_id: Task identifier
            command: Optional command to execute

        Raises:
            TaskNotFoundError: Task doesn't exist
            RemoteExecutionError: Shell access failed
        """
        # Try cache first for instant response
        from flow.cli.utils.task_index_cache import TaskIndexCache
        from flow.cli.utils.ssh_key_cache import SSHKeyCache

        task_cache = TaskIndexCache()
        ssh_cache = SSHKeyCache()

        # Try to get cached info first
        cached_task = task_cache.get_cached_task(task_id)
        cached_ssh_key = ssh_cache.get_key_path(task_id)

        # If we have everything cached, we can proceed immediately
        if cached_task and cached_task.get("ssh_host") and cached_ssh_key:
            # Create a minimal task object from cache
            task = type(
                "Task",
                (),
                {
                    "task_id": task_id,
                    "ssh_host": cached_task["ssh_host"],
                    "ssh_port": cached_task.get("ssh_port", 22),
                    "ssh_user": cached_task.get("ssh_user", "ubuntu"),
                    "name": cached_task.get("name"),
                },
            )()
            ssh_key_path = Path(cached_ssh_key)
        else:
            # Fall back to full lookup
            task = self.provider.get_task(task_id)
            if not task or not task.ssh_host:
                raise RemoteExecutionError(f"No SSH access for task {task_id}")

            # Get the SSH key path for this task
            ssh_key_path, error_msg = self.provider.get_task_ssh_connection_info(task_id)
            if not ssh_key_path:
                raise RemoteExecutionError(f"SSH key resolution failed: {error_msg}")

        # Check if SSH is ready first
        ssh_is_ready = self._is_ssh_ready(task, ssh_key_path)

        # Update progress message if we have an AnimatedEllipsisProgress
        if progress_context and hasattr(progress_context, "update_message"):
            if ssh_is_ready:
                progress_context.update_message("SSH ready, connecting...")
            else:
                progress_context.update_message("Waiting for SSH to be ready...")

        # Enhanced SSH waiting with progress reporting
        if not ssh_is_ready:
            # Don't immediately close progress_context - let it show while we wait for SSH
            # We'll close it later, right before starting the SSH subprocess

            from rich.console import Console
            from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
            import signal

            console = Console()

            # Check task age and status to determine appropriate messaging
            task_age_minutes = 0
            is_paused_or_resuming = False
            if hasattr(task, "created_at") and task.created_at:
                from datetime import datetime, timezone
                from flow.api.models import TaskStatus

                age = task.instance_age_seconds
                task_age_minutes = int(age / 60) if age else 0

                # Check if task is paused or recently resumed
                if hasattr(task, "status"):
                    is_paused_or_resuming = task.status == TaskStatus.PAUSED
                # Also check if task was recently paused (SSH not immediately ready after resume)
                if not is_paused_or_resuming and hasattr(task, "paused_at") and task.paused_at:
                    paused_age = (datetime.now(timezone.utc) - task.paused_at).total_seconds()
                    if paused_age < 300:  # Within 5 minutes of being paused
                        is_paused_or_resuming = True

            # Determine appropriate timeout and message based on context
            if is_paused_or_resuming:
                # For paused/resuming instances
                ssh_wait_timeout = 120  # 2 minutes for resumed instances
                initial_message = (
                    f"\n[yellow]Instance is resuming from paused state[/yellow] "
                    f"(IP: {task.ssh_host})"
                )
                timeout_message = (
                    "SSH service needs to restart after resume. This typically takes 1-2 minutes."
                )
            elif task_age_minutes > 30:
                # For long-running instances, use a shorter timeout since SSH should already be ready
                # But still give it a chance in case SSH service is temporarily unavailable
                ssh_wait_timeout = 60  # 1 minute for established instances
                initial_message = (
                    f"\n[yellow]Reconnecting to established instance[/yellow] "
                    f"(IP: {task.ssh_host}, age: {task_age_minutes} minutes)"
                )
                timeout_message = "Checking SSH availability..."
            else:
                # For new instances, use the standard timeout
                ssh_wait_timeout = SSH_READY_WAIT_SECONDS
                initial_message = (
                    f"\n[yellow]Instance is starting up[/yellow] (IP: {task.ssh_host})"
                )
                timeout_message = f"This can take up to {EXPECTED_PROVISION_MINUTES} minutes for Mithril instances."

            # Show initial status
            console.print(initial_message)
            console.print(timeout_message)
            console.print("[dim]Press Ctrl+C to cancel[/dim]\n")

            # Flag for graceful shutdown
            interrupted = False

            def signal_handler(signum, frame):
                nonlocal interrupted
                interrupted = True
                console.print("\n[yellow]Cancelling SSH connection...[/yellow]")
                # Don't exit immediately - let the loop handle cleanup

            # Set up signal handler
            old_handler = signal.signal(signal.SIGINT, signal_handler)

            try:
                # Check if we should use AnimatedEllipsisProgress instead
                from flow.cli.utils.animated_progress import AnimatedEllipsisProgress

                # If progress_context is AnimatedEllipsisProgress that's already running,
                # reuse it instead of creating a new Progress display
                if (
                    isinstance(progress_context, AnimatedEllipsisProgress)
                    and progress_context._active
                ):
                    # Reuse the existing AnimatedEllipsisProgress
                    progress_context.update_message("Waiting for SSH to be ready")

                    start_time = time.time()
                    attempts = 0
                    ssh_ready = False

                    while time.time() - start_time < ssh_wait_timeout and not interrupted:
                        # Check if SSH is ready
                        if self._is_ssh_ready(task, ssh_key_path):
                            ssh_ready = True
                            break

                        # Exponential backoff with cap
                        wait_time = min(2 ** (attempts / 10), 10)  # Cap at 10 seconds
                        wait_start = time.time()
                        while time.time() - wait_start < wait_time and not interrupted:
                            time.sleep(0.1)  # Check for interrupt every 100ms

                        attempts += 1

                    # Handle results after the loop
                    if not interrupted and not ssh_ready:
                        # Continue to timeout handling below
                        pass
                else:
                    # Original Progress display for backward compatibility
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        TimeElapsedColumn(),
                        console=console,
                        transient=True,
                    ) as progress:
                        progress_task = progress.add_task(
                            "Waiting for SSH to be ready...", total=None
                        )

                        start_time = time.time()
                        attempts = 0

                        while time.time() - start_time < ssh_wait_timeout and not interrupted:
                            elapsed = time.time() - start_time
                            attempts += 1

                            # Simple waiting message without misleading specifics
                            elapsed_min = int(elapsed / 60)
                            elapsed_sec = int(elapsed % 60)

                            # Every 30 seconds, show more detailed status
                            if attempts % 15 == 0 and elapsed > 30:
                                progress.update(
                                    progress_task,
                                    description=f"SSH service is starting up ({elapsed_min}m {elapsed_sec}s elapsed)",
                                )
                            else:
                                progress.update(
                                    progress_task,
                                    description=f"Waiting for SSH to be ready ({elapsed_min}m {elapsed_sec}s elapsed)",
                                )

                            # Check if SSH is ready
                            if self._is_ssh_ready(task, ssh_key_path):
                                progress.update(
                                    progress_task, description="[green]✓ SSH is ready![/green]"
                                )
                                break

                            # Exponential backoff with cap, but check for interrupts
                            wait_time = min(2 ** (attempts / 10), 10)  # Cap at 10 seconds
                            wait_start = time.time()
                            while time.time() - wait_start < wait_time and not interrupted:
                                time.sleep(0.1)  # Check for interrupt every 100ms

                    if interrupted:
                        progress.stop()
                        console.print("\n[yellow]SSH connection cancelled by user[/yellow]")
                        console.print("\nYou can reconnect later with:")
                        console.print(f"  [cyan]flow ssh {task.name or task_id}[/cyan]")
                        raise KeyboardInterrupt("User cancelled SSH connection")

                    if time.time() - start_time >= ssh_wait_timeout:
                        # Timeout
                        console.print("\n[red]✗ SSH connection timed out[/red]")

                        if is_paused_or_resuming:
                            # For paused/resuming instances
                            console.print(
                                f"\n[yellow]SSH service is still restarting after resume[/yellow]"
                            )
                            console.print("\nThis can happen when:")
                            console.print("  • The instance was paused for an extended period")
                            console.print("  • System services are still initializing")
                            console.print("  • Container runtime is restarting")
                            console.print("\nRecommended actions:")
                            console.print(
                                f"  • Wait another minute and retry: [cyan]flow ssh {task.name or task_id}[/cyan]"
                            )
                            console.print(
                                f"  • Check instance status: [cyan]flow status {task.name or task_id}[/cyan]"
                            )
                            console.print(
                                f"  • View logs: [cyan]flow logs {task.name or task_id}[/cyan]"
                            )
                            error_msg = "SSH not ready yet after resume. Please wait a moment and try again."
                        elif task_age_minutes > 30:
                            # For long-running instances, show different message
                            console.print(
                                f"\n[red]SSH service is not responding on established instance[/red]"
                            )
                            console.print(f"Instance age: {task_age_minutes} minutes")
                            console.print("\nThis is unexpected. Possible causes:")
                            console.print("  • SSH service crashed or was stopped")
                            console.print("  • Instance was preempted and recreated")
                            console.print("  • Container or system issue")
                            console.print("\nRecommended actions:")
                            console.print(
                                f"  • Check instance health: [cyan]flow health {task.name or task_id}[/cyan]"
                            )
                            console.print(
                                f"  • View logs: [cyan]flow logs {task.name or task_id}[/cyan]"
                            )
                            console.print(
                                f"  • Restart the instance: [cyan]flow cancel {task.name or task_id} && flow dev[/cyan]"
                            )

                            # Show manual connection command
                            console.print(
                                "\nConnection failed. You can try connecting manually with:"
                            )
                            console.print(
                                f"  ssh -p {task.ssh_port} {task.ssh_user}@{task.ssh_host}\n"
                            )

                            error_msg = (
                                f"SSH service not responding on {task_age_minutes}-minute old instance. "
                                "The instance may need to be restarted."
                            )
                        else:
                            # For new instances, show standard timeout message
                            console.print(
                                f"\nThis instance has been starting for {int(elapsed / 60)} minutes."
                            )
                            console.print("You can:")
                            console.print(
                                f"  • Check startup logs: [cyan]flow logs {task.name or task_id}[/cyan]"
                            )
                            console.print(
                                f"  • Try again: [cyan]flow ssh {task.name or task_id}[/cyan]"
                            )
                            console.print(
                                f"  • Check status: [cyan]flow status {task.name or task_id}[/cyan]"
                            )
                            error_msg = "SSH connection timed out"

                        raise RemoteExecutionError(error_msg)
            finally:
                # Restore original signal handler
                signal.signal(signal.SIGINT, old_handler)

        # Now run the actual SSH command
        ssh_cmd = [
            "ssh",
            "-p",
            str(task.ssh_port),
            "-i",
            str(ssh_key_path),
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "ConnectTimeout=10",
            "-o",
            "ServerAliveInterval=10",
            "-o",
            "ServerAliveCountMax=3",
            f"{task.ssh_user}@{task.ssh_host}",
        ]
        if command:
            ssh_cmd.append(command)

        try:
            # For commands, capture output; for interactive shell, run normally
            if command:
                result = subprocess.run(ssh_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    # Command succeeded, print output
                    if result.stdout:
                        print(result.stdout, end="")
                    return
            else:
                # Interactive shell - stop animation before taking over terminal
                # Only stop if we haven't already stopped it during SSH wait
                if progress_context and hasattr(progress_context, "_active"):
                    # Check if the progress context is still active
                    # AnimatedEllipsisProgress should have this attribute
                    if progress_context._active:
                        progress_context.__exit__(None, None, None)

                # Run SSH without capturing (takes over terminal)
                result = subprocess.run(ssh_cmd)
                return

            # Handle errors for command execution
            if result.returncode != 0:
                stderr = result.stderr.lower()
                # Provide helpful error messages based on SSH failure type
                if "connection timed out" in stderr or "operation timed out" in stderr:
                    # Check if instance was recently created
                    if hasattr(task, "created_at") and task.created_at:
                        from datetime import datetime, timezone

                        elapsed = task.instance_age_seconds or 0
                        if elapsed < EXPECTED_PROVISION_MINUTES * 60:
                            raise RemoteExecutionError(
                                f"SSH connection timed out. Instance may still be provisioning "
                                f"(elapsed: {elapsed / 60:.1f} minutes). Mithril instances can take up to "
                                f"{EXPECTED_PROVISION_MINUTES} minutes to become fully available. Please try again later."
                            )
                    raise RemoteExecutionError(
                        "SSH connection timed out. Possible causes:\n"
                        f"  - Instance is still provisioning (can take up to {EXPECTED_PROVISION_MINUTES} minutes)\n"
                        "  - Network connectivity issues\n"
                        "  - Security group/firewall blocking SSH (port 22)"
                    )
            elif "connection refused" in stderr:
                raise RemoteExecutionError(
                    "SSH connection refused. The instance is reachable but SSH service "
                    "is not ready yet. Please wait a few more minutes and try again."
                )
            elif "connection reset by peer" in stderr or "kex_exchange_identification" in stderr:
                raise RemoteExecutionError(
                    "SSH connection was reset. The SSH service is still initializing.\n"
                    "This typically happens during the first few minutes after instance creation.\n"
                    "Please wait 1-2 minutes and try again."
                )
            elif "permission denied" in stderr:
                # This shouldn't happen now that we resolve SSH keys, but keep for safety
                error_msg = "SSH authentication failed despite key resolution.\n\n"
                error_msg += (
                    "This is unexpected - the SSH key was found but authentication failed.\n"
                )
                error_msg += "Possible causes:\n"
                error_msg += "  1. The private key file permissions are too open (should be 600)\n"
                error_msg += "  2. The key file is corrupted or invalid\n"
                error_msg += "  3. The instance was created with a different key than expected\n\n"
                error_msg += "Debug information:\n"
                error_msg += f"  - SSH command: {' '.join(ssh_cmd[:6])}...\n"
                error_msg += f"  - Task ID: {task_id}\n"
                # Extract SSH key path from command if available
                if "-i" in ssh_cmd:
                    key_idx = ssh_cmd.index("-i") + 1
                    if key_idx < len(ssh_cmd):
                        error_msg += f"  - Using SSH key: {ssh_cmd[key_idx]}\n"

                raise RemoteExecutionError(error_msg)
            else:
                raise RemoteExecutionError(f"SSH connection failed: {result.stderr}")
        except RemoteExecutionError:
            raise
        except Exception as e:
            raise RemoteExecutionError(f"SSH shell failed: {str(e)}") from e

    def _is_ssh_ready(self, task, ssh_key_path: str) -> bool:
        """Check if SSH is ready to accept connections.

        Args:
            task: Task with SSH information
            ssh_key_path: Path to SSH private key

        Returns:
            True if SSH is ready, False otherwise
        """
        # Quick TCP port check first
        import socket

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((task.ssh_host, task.ssh_port))
            sock.close()
            if result != 0:
                return False
        except:
            return False

        # Test actual SSH connectivity
        test_cmd = [
            "ssh",
            "-p",
            str(task.ssh_port),
            "-i",
            str(ssh_key_path),
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "UserKnownHostsFile=/dev/null",
            "-o",
            "ConnectTimeout=5",
            "-o",
            "PasswordAuthentication=no",
            "-o",
            "BatchMode=yes",
            f"{task.ssh_user}@{task.ssh_host}",
            "echo",
            "SSH_OK",
        ]

        try:
            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)

            # Check for specific error conditions
            if result.returncode == 255:
                stderr = result.stderr.lower()
                # Connection reset typically means SSH daemon is starting up
                if "connection reset by peer" in stderr or "kex_exchange_identification" in stderr:
                    logger.debug("SSH connection reset - daemon likely still starting")
                    return False
                # Connection closed also indicates incomplete startup
                elif "connection closed" in stderr:
                    logger.debug("SSH connection closed - service not ready")
                    return False

            return result.returncode == 0 and "SSH_OK" in result.stdout
        except subprocess.TimeoutExpired:
            logger.debug("SSH readiness check timed out")
            return False
        except Exception as e:
            logger.debug(f"SSH readiness check failed: {e}")
            return False
