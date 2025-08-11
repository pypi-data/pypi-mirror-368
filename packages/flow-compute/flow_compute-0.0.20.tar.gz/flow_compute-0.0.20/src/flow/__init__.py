"""Flow SDK - GPU compute made simple."""

import sys

# Friendly guard for older Python versions, to avoid cryptic SyntaxErrors on import
if sys.version_info < (3, 10):
    raise ImportError(
        "Flow SDK requires Python 3.10 or later. You are using "
        f"Python {sys.version_info.major}.{sys.version_info.minor}. "
        "Install a newer Python (recommended: use 'uv' — https://docs.astral.sh/uv/) "
        "or see the installation guide in the docs."
    )

# Public API imports
from flow.api.client import Flow
from flow.api.decorators import FlowApp, app
from flow.api.invoke import invoke
from flow.api.models import Retries, Task, TaskConfig, TaskStatus, Volume, VolumeSpec
from flow.api.secrets import Secret

# Public errors and constants
from flow.errors import (
    APIError,
    AuthenticationError,
    ConfigParserError,
    DependencyNotFoundError,
    FlowError,
    FlowOperationError,
    InstanceNotReadyError,
    InsufficientBidPriceError,
    NameConflictError,
    NetworkError,
    ProviderError,
    QuotaExceededError,
    RemoteExecutionError,
    ResourceNotAvailableError,
    ResourceNotFoundError,
    TaskExecutionError,
    TaskNotFoundError,
    TimeoutError,
    ValidationAPIError,
    ValidationError,
    VolumeError,
)

# Provider-agnostic constants
DEFAULT_REGION = "us-central1-b"  # Default region (Mithril default)
# Align user messaging with provider constants to avoid inconsistent guidance
DEFAULT_PROVISION_MINUTES = 20  # Typical provision time for GPU instances

# SSH utilities
# Version (single source of truth)
from flow._version import __version__  # noqa: E402
from flow.api.ssh_utils import (
    SSHNotReadyError,
    check_task_age_for_ssh,
    wait_for_task_ssh_info,
)


# Convenience functions
def run(task_or_command, **kwargs):
    """Submit task to GPU infrastructure using default Flow client.

    This is a convenience wrapper that creates a Flow instance internally.
    For advanced usage requiring multiple operations, use `with Flow() as flow:`.

    Args:
        task_or_command: TaskConfig, path to YAML file, or command string
        **kwargs: When task_or_command is a string command:
            - instance_type: GPU instance type (e.g., "a100", "8xh100")
            - image: Docker image to use
            - wait: Whether to wait for task to start
            - mounts: Data sources to mount
            - Any other TaskConfig field

    Returns:
        Task: The submitted task object

    Examples:
        >>> import flow
        >>> # Simple command with instance type
        >>> task = flow.run("python train.py", instance_type="a100")
        >>>
        >>> # With Docker image
        >>> task = flow.run("python train.py",
        ...                 instance_type="a100",
        ...                 image="pytorch/pytorch:2.0.0-cuda11.8-cudnn8")
        >>>
        >>> # From TaskConfig
        >>> config = flow.TaskConfig(name="training", instance_type="8xh100",
        ...                          command="python train.py")
        >>> task = flow.run(config)
    """
    from flow.api.client import Flow

    # Extract Flow.run() specific args
    wait = kwargs.pop("wait", False)
    mounts = kwargs.pop("mounts", None)

    # If task_or_command is a string and not a file path, treat it as a command
    if isinstance(task_or_command, str) and not task_or_command.endswith((".yaml", ".yml")):
        # Check if it looks like a file path
        from pathlib import Path

        if not Path(task_or_command).exists():
            # It's a command string, create TaskConfig with it
            config = TaskConfig(command=task_or_command, **kwargs)
            with Flow() as client:
                return client.run(config, wait=wait, mounts=mounts)

    # Otherwise, pass through as-is (TaskConfig or YAML path)
    with Flow() as client:
        return client.run(task_or_command, wait=wait, mounts=mounts)


__all__ = [
    # Main API
    "Flow",
    "FlowApp",
    "invoke",
    "app",
    "run",
    # Models
    "TaskConfig",
    "Task",
    "Volume",
    "VolumeSpec",
    "TaskStatus",
    "Secret",
    "Retries",
    # Errors
    "FlowError",
    "AuthenticationError",
    "ResourceNotFoundError",
    "TaskNotFoundError",
    "ValidationError",
    "APIError",
    "ValidationAPIError",
    "InsufficientBidPriceError",
    "NetworkError",
    "TimeoutError",
    "ProviderError",
    "ConfigParserError",
    "ResourceNotAvailableError",
    "QuotaExceededError",
    "VolumeError",
    "TaskExecutionError",
    "FlowOperationError",
    # Constants
    "DEFAULT_REGION",
]
