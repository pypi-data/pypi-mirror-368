"""SSH connection waiter for Mithril instances.

This module provides functionality to wait for SSH availability on newly
provisioned Mithril instances, with exponential backoff and progress reporting.
"""

import logging
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional, Protocol

from flow.api.models import Task
from flow.errors import FlowError
from .ssh_utils import wait_for_task_ssh_info, SSHNotReadyError
from .core.constants import EXPECTED_PROVISION_MINUTES

logger = logging.getLogger(__name__)


class SSHTimeoutError(FlowError):
    """Raised when SSH connection times out."""

    pass


@dataclass
class SSHConnectionInfo:
    """SSH connection details for a task."""

    host: str
    port: int
    user: str
    key_path: Path
    task_id: str

    @property
    def destination(self) -> str:
        """Get SSH destination string."""
        return f"{self.user}@{self.host}"


class ISSHWaiter(Protocol):
    """Protocol for SSH connection waiters."""

    def wait_for_ssh(
        self,
        task: Task,
        timeout: int = None,
        probe_interval: float = 10.0,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> SSHConnectionInfo:
        """Wait for SSH to become available on a task.

        Args:
            task: Task to wait for SSH on
            timeout: Maximum seconds to wait (default: 2x expected provision time)
            probe_interval: Initial interval between probes
            progress_callback: Optional callback for progress updates

        Returns:
            SSHConnectionInfo with connection details

        Raises:
            SSHTimeoutError: If SSH doesn't become available within timeout
        """
        ...


class ExponentialBackoffSSHWaiter:
    """SSH waiter with exponential backoff strategy.

    Waits for SSH connectivity with increasing delays between attempts
    to reduce load on newly provisioning instances.
    """

    def __init__(self, provider: Optional["MithrilProvider"] = None):
        """Initialize SSH waiter.

        Args:
            provider: Optional Mithril provider for SSH key resolution
        """
        self.provider = provider
        self.max_backoff = 60  # Maximum delay between attempts
        self.backoff_multiplier = 1.5  # Exponential growth factor

    def wait_for_ssh(
        self,
        task: Task,
        timeout: int = None,
        probe_interval: float = 10.0,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> SSHConnectionInfo:
        """Wait for SSH to become available with exponential backoff.

        Args:
            task: Task to wait for SSH on
            timeout: Maximum seconds to wait (default: 2x expected provision time)
            probe_interval: Initial interval between probes
            progress_callback: Optional callback for progress updates

        Returns:
            SSHConnectionInfo with connection details

        Raises:
            SSHTimeoutError: If SSH doesn't become available within timeout
            ValueError: If task lacks SSH connection information
        """
        if timeout is None:
            timeout = EXPECTED_PROVISION_MINUTES * 60 * 2  # 2x expected provision time

        start_time = time.time()

        # First, use the shared utility to wait for SSH info
        try:
            task = wait_for_task_ssh_info(
                task=task,
                provider=self.provider,
                timeout=timeout,
                progress_callback=progress_callback,
            )
        except SSHNotReadyError as e:
            # Convert to SSHTimeoutError for compatibility
            raise SSHTimeoutError(str(e), suggestions=e.suggestions) from e

        # Get SSH key path
        ssh_key_path = self._get_ssh_key_path(task)

        # Build connection info
        connection_info = SSHConnectionInfo(
            host=task.ssh_host,
            port=task.ssh_port,
            user=task.ssh_user,
            key_path=ssh_key_path,
            task_id=task.task_id,
        )

        # Continue using the same start_time from provisioning wait
        attempt = 0
        current_interval = probe_interval

        logger.info(f"Waiting for SSH on {connection_info.destination}:{connection_info.port}")

        while True:
            elapsed = time.time() - start_time

            # Check timeout
            if elapsed >= timeout:
                self._handle_timeout(task, elapsed, timeout)

            # Update progress - skip if None to avoid duplicate output
            # The higher-level AnimatedEllipsisProgress handles the display
            if progress_callback:
                mins, secs = divmod(int(elapsed), 60)
                status = f"Establishing secure connection ({mins}m {secs}s)"
                progress_callback(status)

            # Test SSH connection
            if self._test_ssh_connection(connection_info):
                logger.info(f"SSH available after {elapsed:.1f} seconds")
                return connection_info

            # Calculate next delay with exponential backoff
            delay = min(current_interval, self.max_backoff)
            logger.debug(f"SSH not ready, waiting {delay:.1f}s before retry")
            time.sleep(delay)

            # Increase interval for next attempt
            current_interval *= self.backoff_multiplier
            attempt += 1

    def _test_ssh_connection(self, connection: SSHConnectionInfo) -> bool:
        """Test if SSH connection is available.

        Args:
            connection: SSH connection details

        Returns:
            True if SSH is available, False otherwise
        """
        cmd = [
            "ssh",
            "-p",
            str(connection.port),
            "-i",
            str(connection.key_path),
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "UserKnownHostsFile=/dev/null",
            "-o",
            "ConnectTimeout=5",
            "-o",
            "ServerAliveInterval=5",
            "-o",
            "ServerAliveCountMax=1",
            "-o",
            "PasswordAuthentication=no",
            "-o",
            "BatchMode=yes",
            connection.destination,
            "echo",
            "SSH_TEST_OK",
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            # Check if we got the expected response
            if result.returncode == 0 and "SSH_TEST_OK" in result.stdout:
                return True

            # Log specific failure reason for debugging
            if result.returncode == 255:
                # SSH connection error
                stderr = result.stderr.lower()
                if "connection refused" in stderr:
                    logger.debug("SSH connection refused - service not ready")
                elif "connection timed out" in stderr:
                    logger.debug("SSH connection timed out - instance may be booting")
                elif "no route to host" in stderr:
                    logger.debug("No route to host - network not ready")
                else:
                    logger.debug(f"SSH error: {result.stderr.strip()}")

            return False

        except subprocess.TimeoutExpired:
            logger.debug("SSH connection test timed out")
            return False
        except Exception as e:
            logger.debug(f"SSH test failed with error: {e}")
            return False

    def _get_ssh_key_path(self, task: Task) -> Path:
        """Get SSH key path for task.

        Args:
            task: Task to get SSH key for

        Returns:
            Path to SSH private key

        Raises:
            FlowError: If SSH key cannot be resolved
        """
        if not self.provider:
            # Try default locations
            default_key = Path.home() / ".ssh" / "id_rsa"
            if default_key.exists():
                return default_key
            raise FlowError("No SSH key available - provider not set")

        # Use provider's SSH key resolution
        key_path, error_msg = self.provider.get_task_ssh_connection_info(task.task_id)
        if not key_path:
            raise FlowError(f"Failed to resolve SSH key: {error_msg}")

        return Path(key_path)

    def _handle_timeout(self, task: Task, elapsed: float, timeout: int) -> None:
        """Handle SSH timeout with helpful error message.

        Args:
            task: Task that timed out
            elapsed: Seconds elapsed
            timeout: Timeout limit that was exceeded

        Raises:
            SSHTimeoutError: Always raises with detailed message
        """
        mins, secs = divmod(int(elapsed), 60)

        # Build helpful error message
        error_msg = f"SSH connection timeout after {mins}m {secs}s"

        # Add instance age information if available
        instance_age = task.instance_age_seconds
        instance_mins = int(instance_age / 60) if instance_age else None

        if instance_mins is not None and instance_mins < 20:
            from .core.constants import EXPECTED_PROVISION_MINUTES

            error_msg += (
                f"\n\nThe instance was created {instance_mins} minutes ago. "
                f"Mithril instances can take up to {EXPECTED_PROVISION_MINUTES} minutes to become fully available. "
                f"The instance may still be provisioning."
            )

        # Add suggestions
        suggestions = [
            f"Wait longer: flow upload-code {task.task_id} --timeout {timeout + 600}",
            f"Check task status: flow status {task.task_id}",
            "Try again in a few minutes",
            "Check if the instance type typically takes longer to provision",
        ]

        raise SSHTimeoutError(error_msg, suggestions=suggestions)
