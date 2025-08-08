"""Shared SSH utilities for Mithril provider.

This module provides common SSH-related functionality used across
the Mithril provider, ensuring consistent behavior for SSH operations.
"""

import atexit
import logging
import os
import signal
import socket
import subprocess
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional, Callable, TYPE_CHECKING, Dict, List

from flow.api.models import Task
from flow.errors import FlowError
from flow.utils.circuit_breaker import CircuitBreaker

if TYPE_CHECKING:
    from .provider import MithrilProvider

logger = logging.getLogger(__name__)


class SSHNotReadyError(FlowError):
    """Raised when SSH is not available within the expected timeframe."""

    pass


class SSHTunnelError(FlowError):
    """Raised when SSH tunnel operations fail."""

    pass


@dataclass
class SSHTunnel:
    """Represents an active SSH tunnel."""

    process: subprocess.Popen
    local_port: int
    remote_port: int
    remote_host: str = "localhost"
    task_id: str = ""

    def is_alive(self) -> bool:
        """Check if tunnel process is still running."""
        return self.process.poll() is None

    def terminate(self) -> None:
        """Terminate the tunnel process gracefully."""
        if self.is_alive():
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()


class SSHTunnelManager:
    """Manages SSH tunnels with proper lifecycle and error handling.

    This class provides centralized SSH tunnel management with:
    - Circuit breaker pattern for resilient connections
    - Automatic port allocation
    - Process lifecycle management
    - Context manager support for automatic cleanup
    """

    # Global registry of active tunnels for cleanup
    _active_tunnels: Dict[str, SSHTunnel] = {}
    _circuit_breaker = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=30.0,
        expected_exceptions=(SSHTunnelError, subprocess.CalledProcessError),
    )

    @classmethod
    def _register_tunnel(cls, tunnel: SSHTunnel) -> None:
        """Register tunnel for global cleanup."""
        cls._active_tunnels[f"{tunnel.task_id}:{tunnel.local_port}"] = tunnel

    @classmethod
    def _unregister_tunnel(cls, tunnel: SSHTunnel) -> None:
        """Unregister tunnel from global cleanup."""
        key = f"{tunnel.task_id}:{tunnel.local_port}"
        cls._active_tunnels.pop(key, None)

    @classmethod
    def cleanup_all_tunnels(cls) -> None:
        """Clean up all active tunnels (for shutdown)."""
        for tunnel in list(cls._active_tunnels.values()):
            try:
                tunnel.terminate()
                cls._unregister_tunnel(tunnel)
            except Exception as e:
                logger.debug(f"Error cleaning up tunnel: {e}")

    @classmethod
    def create_tunnel(
        cls,
        task: Task,
        local_port: int = 0,
        remote_port: int = 22,
        remote_host: str = "localhost",
        ssh_options: Optional[List[str]] = None,
    ) -> SSHTunnel:
        """Create an SSH tunnel with circuit breaker protection.

        Args:
            task: Task with SSH connection information
            local_port: Local port to bind (0 for auto-allocation)
            remote_port: Remote port to forward
            remote_host: Remote host to connect to (default: localhost)
            ssh_options: Additional SSH options

        Returns:
            SSHTunnel instance

        Raises:
            SSHTunnelError: If tunnel creation fails
            ResourceNotAvailableError: If circuit breaker is open
        """
        return cls._circuit_breaker.call(
            cls._create_tunnel_impl,
            task=task,
            local_port=local_port,
            remote_port=remote_port,
            remote_host=remote_host,
            ssh_options=ssh_options,
        )

    @classmethod
    def _create_tunnel_impl(
        cls,
        task: Task,
        local_port: int = 0,
        remote_port: int = 22,
        remote_host: str = "localhost",
        ssh_options: Optional[List[str]] = None,
    ) -> SSHTunnel:
        """Internal implementation of tunnel creation."""
        if not task.ssh_host:
            raise SSHTunnelError(
                f"Task {task.task_id} has no SSH host information",
                suggestions=[
                    "Wait for instance to be provisioned",
                    "Check task status with 'flow status'",
                ],
            )

        # Find available port if not specified
        if local_port == 0:
            local_port = cls._find_available_port()

        # Build SSH command
        ssh_cmd = cls._build_ssh_command(
            task=task,
            local_port=local_port,
            remote_port=remote_port,
            remote_host=remote_host,
            ssh_options=ssh_options,
        )

        logger.debug(f"Creating SSH tunnel: localhost:{local_port} -> {remote_host}:{remote_port}")

        try:
            # Start SSH tunnel process
            process = subprocess.Popen(
                ssh_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if os.name != "nt" else None,
            )

            # Wait briefly to check if process started successfully
            time.sleep(0.5)
            if process.poll() is not None:
                stderr = process.stderr.read().decode() if process.stderr else ""
                raise SSHTunnelError(
                    f"SSH tunnel failed to start: {stderr}",
                    suggestions=[
                        "Check SSH connectivity with 'flow ssh'",
                        "Verify SSH keys are configured",
                        "Check network connectivity",
                    ],
                )

            # Verify tunnel is working
            if not cls._verify_tunnel(local_port, timeout=5):
                process.terminate()
                raise SSHTunnelError(
                    f"SSH tunnel on port {local_port} is not responding",
                    suggestions=[
                        "Check if remote service is running",
                        f"Verify port {remote_port} is open on remote host",
                    ],
                )

            tunnel = SSHTunnel(
                process=process,
                local_port=local_port,
                remote_port=remote_port,
                remote_host=remote_host,
                task_id=task.task_id,
            )

            cls._register_tunnel(tunnel)
            logger.info(
                f"SSH tunnel established: localhost:{local_port} -> {remote_host}:{remote_port}"
            )

            return tunnel

        except Exception as e:
            if not isinstance(e, SSHTunnelError):
                raise SSHTunnelError(f"Failed to create SSH tunnel: {str(e)}")
            raise

    @staticmethod
    def _find_available_port() -> int:
        """Find an available local port."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port

    @staticmethod
    def _build_ssh_command(
        task: Task,
        local_port: int,
        remote_port: int,
        remote_host: str,
        ssh_options: Optional[List[str]] = None,
    ) -> List[str]:
        """Build SSH command for tunnel."""
        cmd = [
            "ssh",
            "-N",  # No command execution
            "-L",
            f"{local_port}:{remote_host}:{remote_port}",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "UserKnownHostsFile=/dev/null",
            "-o",
            "PasswordAuthentication=no",
            "-o",
            "ConnectTimeout=10",
            "-o",
            "ServerAliveInterval=60",
            "-o",
            "ServerAliveCountMax=3",
            "-o",
            "ExitOnForwardFailure=yes",
        ]

        # Add custom SSH options
        if ssh_options:
            cmd.extend(ssh_options)

        # Add port if non-standard
        if task.ssh_port and task.ssh_port != 22:
            cmd.extend(["-p", str(task.ssh_port)])

        # Add SSH key if configured
        # Task objects don't have ssh_key_path attribute, check environment
        ssh_key = os.environ.get("FLOW_SSH_KEY_PATH")
        if not ssh_key:
            # Try to get from config file if available
            from pathlib import Path
            import yaml

            try:
                config_path = Path.home() / ".flow" / "config.yaml"
                if config_path.exists():
                    with open(config_path) as f:
                        config = yaml.safe_load(f)
                        ssh_key = config.get("ssh_key_path")
            except Exception:
                pass

        if ssh_key:
            ssh_key = os.path.expanduser(ssh_key)
            if os.path.exists(ssh_key):
                cmd.extend(["-i", ssh_key])

        # Add destination
        cmd.append(f"{task.ssh_user}@{task.ssh_host}")

        return cmd

    @staticmethod
    def _verify_tunnel(port: int, timeout: float = 5.0) -> bool:
        """Verify tunnel is accepting connections."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    s.connect(("localhost", port))
                    return True
            except (socket.error, socket.timeout):
                time.sleep(0.1)
        return False

    @classmethod
    @contextmanager
    def tunnel_context(
        cls,
        task: Task,
        local_port: int = 0,
        remote_port: int = 22,
        remote_host: str = "localhost",
        ssh_options: Optional[List[str]] = None,
    ):
        """Context manager for SSH tunnels with automatic cleanup.

        Example:
            with SSHTunnelManager.tunnel_context(task, remote_port=15132) as tunnel:
                # Use tunnel.local_port to connect
                response = requests.get(f"http://localhost:{tunnel.local_port}/healthz")
        """
        tunnel = None
        try:
            tunnel = cls.create_tunnel(
                task=task,
                local_port=local_port,
                remote_port=remote_port,
                remote_host=remote_host,
                ssh_options=ssh_options,
            )
            yield tunnel
        finally:
            if tunnel:
                tunnel.terminate()
                cls._unregister_tunnel(tunnel)


# Register cleanup handler
atexit.register(SSHTunnelManager.cleanup_all_tunnels)


def _handle_signal(signum, frame):
    """Handle process signals for cleanup."""
    SSHTunnelManager.cleanup_all_tunnels()
    signal.default_int_handler(signum, frame)


# Register signal handlers for cleanup
if hasattr(signal, "SIGTERM"):
    signal.signal(signal.SIGTERM, _handle_signal)
if hasattr(signal, "SIGINT"):
    signal.signal(signal.SIGINT, _handle_signal)


def wait_for_task_ssh_info(
    task: Task,
    provider: Optional["MithrilProvider"] = None,
    timeout: Optional[int] = None,
    check_interval: Optional[int] = None,
    progress_callback: Optional[Callable[[str], None]] = None,
    show_progress: bool = True,
) -> Task:
    """Wait for a task to have SSH connection information.

    This function waits for an instance to be provisioned and have
    SSH host/port information available. It's used by various commands
    that need SSH access (ssh, logs, code upload, etc.).

    Args:
        task: Task to wait for
        provider: Optional provider to refresh task details
        timeout: Maximum seconds to wait (default: from constants)
        check_interval: Seconds between checks (default: from constants)
        progress_callback: Optional callback for progress updates
        show_progress: Whether to show AnimatedEllipsisProgress if no callback provided

    Returns:
        Task: Updated task object with SSH information

    Raises:
        SSHNotReadyError: If SSH info not available within timeout
    """
    from .core.constants import (
        EXPECTED_PROVISION_MINUTES,
        INSTANCE_IP_WAIT_SECONDS,
        INSTANCE_IP_CHECK_INTERVAL,
    )

    # Use defaults from constants if not provided
    if timeout is None:
        timeout = EXPECTED_PROVISION_MINUTES * 60 * 2  # Default to 2x expected provision time
    if check_interval is None:
        check_interval = INSTANCE_IP_CHECK_INTERVAL

    start_time = time.time()

    # Quick return if already has SSH info
    if task.ssh_host:
        return task

    logger.info(f"Waiting for task {task.task_id} to be provisioned with SSH details")

    # Set up progress display if needed
    progress_context = None
    internal_callback = progress_callback

    if not progress_callback and show_progress:
        # No callback provided - use AnimatedEllipsisProgress
        try:
            from flow.cli.utils.animated_progress import AnimatedEllipsisProgress
            from rich.console import Console

            console = Console()
            progress_context = AnimatedEllipsisProgress(
                console,
                f"Waiting for instance provisioning (can take up to {EXPECTED_PROVISION_MINUTES} minutes)",
                transient=True,
            )
            progress_context.__enter__()

            # Create internal callback that doesn't show the "can take up to" part again
            def internal_callback(msg: str):
                # Strip the redundant "can take up to" part if present
                if "can take up to" in msg:
                    msg = msg.split(" - can take up to")[0]
                # Update the progress message
                if hasattr(progress_context, "base_message"):
                    progress_context.base_message = msg

        except ImportError:
            # CLI utils not available (e.g., when called from SDK)
            logger.debug(
                "AnimatedEllipsisProgress not available, proceeding without progress display"
            )

    try:
        while True:
            elapsed = time.time() - start_time

            # Check timeout
            if elapsed >= timeout:
                raise SSHNotReadyError(
                    f"Task {task.task_id} did not receive SSH information within {timeout} seconds",
                    suggestions=[
                        f"Check task status: flow status {task.task_id}",
                        f"Instance provisioning can take up to {EXPECTED_PROVISION_MINUTES} minutes",
                        "Try increasing the timeout",
                        "The task may have failed to start - check logs",
                    ],
                )

            # Update progress if callback provided
            if internal_callback:
                mins, secs = divmod(int(elapsed), 60)
                if mins < 1:
                    msg = f"Waiting for instance provisioning ({secs}s elapsed) - can take up to {EXPECTED_PROVISION_MINUTES} minutes"
                else:
                    msg = f"Waiting for instance provisioning ({mins}m {secs}s elapsed) - can take up to {EXPECTED_PROVISION_MINUTES} minutes"
                internal_callback(msg)

            # Refresh task details if provider available
            if provider and not task.ssh_host:
                try:
                    updated_task = provider.get_task(task.task_id)
                    if updated_task:
                        task = updated_task
                        if task.ssh_host:
                            logger.info(
                                f"Task {task.task_id} now has SSH info: {task.ssh_host}:{task.ssh_port}"
                            )
                            return task
                except Exception as e:
                    logger.debug(f"Failed to refresh task details: {e}")

            # Wait before next check (with interrupt support)
            try:
                time.sleep(check_interval)
            except KeyboardInterrupt:
                # Allow graceful interruption
                raise SSHNotReadyError(
                    f"Wait for SSH interrupted by user",
                    suggestions=[
                        f"The task may still be provisioning",
                        f"Check later with: flow ssh {task.task_id}",
                        f"Check status with: flow status {task.task_id}",
                    ],
                )
    finally:
        # Clean up progress display if we created it
        if progress_context:
            try:
                progress_context.__exit__(None, None, None)
            except Exception:
                pass  # Ignore cleanup errors


def check_task_age_for_ssh(task: Task) -> Optional[str]:
    """Check task age and return appropriate message for SSH issues.

    Args:
        task: Task to check

    Returns:
        Optional message about task age and SSH readiness
    """
    if not hasattr(task, "created_at") or not task.created_at:
        return None

    age_seconds = task.instance_age_seconds
    if age_seconds is None:
        return None
    age_minutes = int(age_seconds / 60)

    # Get task status string
    status_str = task.status.value if hasattr(task, "status") else "unknown"

    if age_minutes > 30 and not task.ssh_host:
        # Long-running task without SSH - differentiate by status
        if status_str == "pending":
            return (
                f"Task has been pending for {age_minutes} minutes without being assigned resources. "
                "This indicates the task is stuck in queue or resources are unavailable."
            )
        elif status_str == "running":
            return (
                f"Instance has been running for {age_minutes} minutes but has no SSH access. "
                "This is unexpected and may indicate the instance has issues."
            )
        else:
            return (
                f"Task created {age_minutes} minutes ago (status: {status_str}) has no SSH access. "
                "SSH is only available for running instances."
            )
    elif age_minutes < 20 and not task.ssh_host:
        from .core.constants import EXPECTED_PROVISION_MINUTES

        if status_str == "pending":
            return (
                f"Task has been pending for {age_minutes} minutes. "
                f"Resource allocation can take up to {EXPECTED_PROVISION_MINUTES} minutes depending on availability."
            )
        elif status_str == "running":
            return (
                f"Instance is {age_minutes} minutes old and still provisioning. "
                f"This can take up to {EXPECTED_PROVISION_MINUTES} minutes for Mithril instances."
            )

    return None
