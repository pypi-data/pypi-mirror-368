"""Provider-agnostic SSH utilities for Flow SDK.

Shared helpers used by the CLI and other components.
"""

import time
from typing import TYPE_CHECKING, ContextManager, Optional

from flow.api.models import Task

if TYPE_CHECKING:
    from flow.providers.base import IProvider


# Default provisioning timeout expectations
DEFAULT_PROVISION_MINUTES = 12  # Typical provision time for GPU instances


class SSHNotReadyError(Exception):
    """Raised when SSH is not ready within expected timeframe."""

    pass


def check_task_age_for_ssh(task: Task) -> str | None:
    """Check if task has been running long enough for SSH to be ready.

    Args:
        task: Task to check

    Returns:
        Message about SSH readiness based on task age, or None if age is normal
    """
    if not task.started_at:
        return None

    from datetime import datetime, timezone

    # Ensure timezone-aware comparison
    started_at = task.started_at
    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=timezone.utc)

    age = datetime.now(timezone.utc) - started_at
    age_minutes = age.total_seconds() / 60

    if age_minutes > DEFAULT_PROVISION_MINUTES * 2:
        return f"Task has been running for {int(age_minutes)} minutes - SSH should be available by now (unexpected delay)"
    elif age_minutes > DEFAULT_PROVISION_MINUTES:
        return f"Task has been running for {int(age_minutes)} minutes - SSH is taking longer than usual"

    return None


def wait_for_task_ssh_info(
    task: Task,
    provider: Optional["IProvider"] = None,
    timeout: int = 600,
    show_progress: bool = True,
    *,
    progress_adapter: object | None = None,
) -> Task:
    """Wait for task to have SSH connection information.

    Args:
        task: Task to wait for
        provider: Provider instance (optional, for updating task info)
        timeout: Maximum seconds to wait
        show_progress: Whether to show progress animation

    Returns:
        Updated task with SSH info

    Raises:
        SSHNotReadyError: If SSH info not available within timeout
    """
    from flow.cli.commands.base import console
    from flow.cli.utils.animated_progress import AnimatedEllipsisProgress

    start_time = time.time()

    if show_progress and progress_adapter is None:
        progress = AnimatedEllipsisProgress(
            console,
            "Waiting for SSH access",
            transient=True,
            start_immediately=True,
            estimated_seconds=DEFAULT_PROVISION_MINUTES * 60,  # Use existing constant
            show_progress_bar=True,
            # Prefer instance_created_at to reflect current VM age; fall back to task.created_at
            task_created_at=(
                getattr(task, "instance_created_at", None) or getattr(task, "created_at", None)
            ),
        )
    else:
        progress = None

    try:
        while time.time() - start_time < timeout:
            # Check if task already has SSH info
            if task.ssh_host:
                if progress:
                    progress.__exit__(None, None, None)
                return task

            # Update task info if provider is available
            if provider:
                try:
                    from flow.providers.base import ITaskManager

                    if hasattr(provider, "task_manager") and isinstance(
                        provider.task_manager, ITaskManager
                    ):
                        updated_task = provider.task_manager.get_task(task.task_id)
                        if updated_task and updated_task.ssh_host:
                            task = updated_task
                            if progress:
                                progress.__exit__(None, None, None)
                            return task
                except Exception:
                    # Continue waiting if update fails
                    pass

            # Wait before next check
            if progress_adapter is not None:
                try:
                    # Allow adapter to update timeline with best-effort percent/eta
                    if hasattr(progress_adapter, "update_eta"):
                        progress_adapter.update_eta()
                except Exception:
                    pass
                time.sleep(1)
            else:
                time.sleep(2)

        # Timeout reached
        if progress:
            progress.__exit__(None, None, None)

        elapsed = int(time.time() - start_time)
        raise SSHNotReadyError(f"SSH access not available after {elapsed} seconds")

    except KeyboardInterrupt:
        if progress:
            progress.__exit__(None, None, None)
        raise SSHNotReadyError("SSH wait interrupted by user")
    except Exception:
        if progress:
            progress.__exit__(None, None, None)
        raise


class SSHTunnelManager:
    """Simplified SSH tunnel manager interface.

    This is a placeholder that should delegate to the provider's
    actual SSH tunnel implementation.
    """

    @staticmethod
    def tunnel_context(task: Task, remote_port: int, local_port: int = 0) -> ContextManager[None]:
        """Create SSH tunnel context.

        This should be implemented by importing the actual provider's
        SSH tunnel manager at runtime based on the task's provider.
        """
        # This is a simplified implementation
        # In practice, this would delegate to the provider's SSH tunnel
        raise NotImplementedError(
            "SSH tunnel support requires provider-specific implementation. "
            "Use flow_client.provider.get_ssh_tunnel_manager() instead."
        )
