"""SDK interface for Flow development environments.

This module provides programmatic access to Flow's persistent development
environment functionality, enabling fast iterative development with
container-based execution on a long-running VM.

The implementation reuses the core components from the CLI dev command
while providing a clean SDK interface that follows Flow's design principles.
"""

import hashlib
import logging
import os
import time
import uuid
from typing import Any, Dict, List, Optional, TypedDict, Union

from flow.api.models import Task, TaskConfig, TaskStatus
from flow.cli.commands.dev import DevContainerExecutor, DevVMManager
from flow.errors import DevVMNotFoundError, DevVMStartupError, DevContainerError, NetworkError

logger = logging.getLogger(__name__)


class ContainerInfo(TypedDict):
    """Docker container information."""

    Names: str
    Status: str
    Image: str
    Command: str
    CreatedAt: str
    ID: str


class DevEnvironmentStatus(TypedDict):
    """Development environment status information."""

    vm: Optional[Dict[str, Any]]  # VM info dictionary
    active_containers: int
    containers: List[ContainerInfo]


class ImprovedDevContainerExecutor(DevContainerExecutor):
    """Enhanced container executor with better error handling."""

    def execute_command(self, command: str, image: str = None, interactive: bool = False) -> int:
        """Execute command with improved error handling."""
        try:
            # Get remote operations using clean interface
            remote_ops = self.flow_client.get_remote_operations()
        except (AttributeError, NotImplementedError) as e:
            raise DevContainerError(
                "Provider doesn't support remote operations required for dev containers", cause=e
            )

        # Store remote_ops temporarily on flow_client._provider for compatibility
        # This is a temporary measure until DevContainerExecutor is refactored
        if hasattr(self.flow_client, "_provider"):
            self.flow_client._provider.get_remote_operations = lambda: remote_ops

        try:
            return super().execute_command(command, image, interactive)
        except Exception as e:
            # Convert generic exceptions to specific dev errors
            error_msg = str(e)

            if "unable to find image" in error_msg.lower():
                raise DevContainerError(
                    f"Docker image '{image or 'default'}' not found",
                    command=command,
                    image=image,
                    cause=e,
                )
            elif "docker: command not found" in error_msg.lower():
                raise DevContainerError(
                    "Docker is not installed on the dev VM", command=command, cause=e
                )
            elif "connection refused" in error_msg.lower():
                raise DevContainerError(
                    "Cannot connect to Docker daemon on dev VM", command=command, cause=e
                )
            else:
                raise DevContainerError(
                    f"Container execution failed: {error_msg}",
                    command=command,
                    image=image,
                    cause=e,
                )


class DevEnvironment:
    """Programmatic interface for Flow development environments.

    Provides SDK access to the same persistent VM functionality available
    through the CLI dev command. Enables fast container-based command
    execution on a long-running development VM.

    Example:
        >>> flow = Flow()
        >>> # Start or connect to dev VM
        >>> vm = flow.dev.start()
        >>>
        >>> # Execute commands in containers
        >>> exit_code = flow.dev.exec("python train.py")
        >>>
        >>> # Run with custom image
        >>> flow.dev.exec("cargo build", image="rust:latest")
        >>>
        >>> # Check status
        >>> status = flow.dev.status()
        >>> print(f"Active containers: {status['active_containers']}")
        >>>
        >>> # Clean up
        >>> flow.dev.reset()  # Reset containers
        >>> flow.dev.stop()   # Stop VM
    """

    def __init__(self, flow_client, auto_stop: bool = False):
        """Initialize dev environment manager.

        Args:
            flow_client: Flow SDK client instance
            auto_stop: Automatically stop VM when used as context manager
        """
        self._flow = flow_client
        self._vm_manager = DevVMManager(flow_client)
        self._current_vm = None
        self._executor = None
        self._auto_stop = auto_stop
        self._context_started = False

    def start(
        self,
        instance_type: Optional[str] = None,
        ssh_keys: Optional[list] = None,
        max_price_per_hour: Optional[float] = None,
        force_new: bool = False,
    ) -> Task:
        """Start or connect to development VM.

        Creates a new persistent VM or connects to an existing one.
        The VM runs continuously to provide fast container execution.

        Args:
            instance_type: GPU/CPU instance type (default: h100)
            ssh_keys: SSH keys for VM access
            max_price_per_hour: Maximum hourly price in USD
            force_new: Force creation of new VM even if one exists

        Returns:
            Task object representing the dev VM

        Example:
            >>> vm = flow.dev.start(instance_type="a100")
            >>> print(f"Dev VM started: {vm.name}")
        """
        # Stop existing VM if force_new
        if force_new:
            existing_vm = self._vm_manager.find_dev_vm()
            if existing_vm:
                logger.info("Force stopping existing dev VM")
                self._vm_manager.stop_dev_vm()

        # Find or create VM
        vm = self._vm_manager.find_dev_vm()
        if not vm:
            logger.info("Creating new dev VM")
            vm = self._vm_manager.create_dev_vm(
                instance_type=instance_type,
                ssh_keys=ssh_keys,
                max_price_per_hour=max_price_per_hour,
            )

            # Wait for VM to be ready
            self._wait_for_vm(vm)
        else:
            logger.info(f"Using existing dev VM: {vm.name}")

        self._current_vm = vm
        self._executor = ImprovedDevContainerExecutor(self._flow, vm)
        return vm

    def ensure_started(
        self,
        instance_type: Optional[str] = None,
        ssh_keys: Optional[list] = None,
        max_price_per_hour: Optional[float] = None,
    ) -> Task:
        """Ensure dev VM is running, starting if needed.

        Convenience method that finds existing VM or creates new one.
        This mirrors the CLI behavior of `flow dev` with no command.

        Args:
            instance_type: GPU/CPU instance type (only used if creating new VM)
            ssh_keys: SSH keys for VM access (only used if creating new VM)
            max_price_per_hour: Maximum hourly price (only used if creating new VM)

        Returns:
            Task object representing the dev VM

        Example:
            >>> # Ensure VM is running then connect
            >>> vm = flow.dev.ensure_started()
            >>> flow.dev.connect()
            >>>
            >>> # Or just start and get VM info
            >>> vm = flow.dev.ensure_started(instance_type="a100")
            >>> print(f"Dev VM ready: {vm.name}")
        """
        vm = self._vm_manager.find_dev_vm()
        if vm:
            logger.info(f"Using existing dev VM: {vm.name}")
            self._current_vm = vm
            self._executor = DevContainerExecutor(self._flow, vm)
            return vm

        # No existing VM, create new one
        return self.start(
            instance_type=instance_type, ssh_keys=ssh_keys, max_price_per_hour=max_price_per_hour
        )

    def _ensure_vm(self) -> Task:
        """Ensure a dev VM is available, finding existing or raising error.

        Returns:
            Task object for the dev VM

        Raises:
            RuntimeError: If no dev VM is running
        """
        if self._current_vm:
            return self._current_vm

        vm = self._vm_manager.find_dev_vm()
        if not vm:
            raise DevVMNotFoundError()

        self._current_vm = vm
        self._executor = ImprovedDevContainerExecutor(self._flow, vm)
        return vm

    def connect(self, command: Optional[str] = None) -> None:
        """Connect interactively to the dev VM via SSH.

        Opens an interactive SSH session to the dev VM, providing
        direct access to the persistent Ubuntu environment.

        Args:
            command: Optional command to run instead of interactive shell

        Raises:
            RuntimeError: If dev VM is not started

        Example:
            >>> flow.dev.connect()  # Interactive SSH session
            >>> flow.dev.connect("tmux attach")  # Run specific command
        """
        vm = self._ensure_vm()
        self._flow.shell(vm.task_id, command=command)

    def run(
        self,
        command: Optional[str] = None,
        image: Optional[str] = None,
        instance_type: Optional[str] = None,
        **kwargs,
    ) -> Union[int, Task]:
        """Run command on dev VM or connect interactively.

        Convenience method that combines common dev workflows:
        - If command provided: execute in container
        - If no command: connect via SSH

        This mirrors the CLI behavior of `flow dev -c 'command'`.

        Args:
            command: Command to execute (None for interactive SSH)
            image: Docker image for container execution
            instance_type: Instance type if creating new VM
            **kwargs: Additional arguments for start()

        Returns:
            Exit code (int) for commands, Task object for interactive

        Example:
            >>> # Execute command
            >>> flow.dev.run("python train.py")
            >>>
            >>> # Interactive SSH (same as connect)
            >>> flow.dev.run()
            >>>
            >>> # With specific image
            >>> flow.dev.run("cargo test", image="rust:latest")
        """
        # Ensure VM is running
        vm = self.ensure_started(instance_type=instance_type, **kwargs)

        if command:
            # Execute command in container
            return self.exec(command, image=image)
        else:
            # Connect interactively
            self.connect()
            return vm

    def exec(
        self, command: str, image: Optional[str] = None, interactive: bool = False, retries: int = 1
    ) -> int:
        """Execute command in container on dev VM.

        Runs the specified command in a new container with workspace
        mounted. Containers are ephemeral but share the persistent
        workspace directory.

        Args:
            command: Command to execute in container
            image: Docker image (default: ubuntu:22.04)
            interactive: Enable interactive mode for shells
            retries: Number of retries for transient failures (default: 1)

        Returns:
            Exit code of the command (0 for success)

        Raises:
            DevVMNotFoundError: If dev VM is not started
            DevContainerError: If container execution fails
            NetworkError: If network issues prevent execution

        Example:
            >>> # Run Python script
            >>> exit_code = flow.dev.exec("python train.py")
            >>>
            >>> # Interactive Python session
            >>> flow.dev.exec("python", interactive=True)
            >>>
            >>> # Use specific image with retry
            >>> flow.dev.exec("npm test", image="node:18", retries=2)
        """
        self._ensure_vm()

        last_error = None
        for attempt in range(max(1, retries)):
            try:
                return self._executor.execute_command(command, image=image, interactive=interactive)
            except (NetworkError, DevContainerError) as e:
                last_error = e

                # Don't retry certain errors
                if interactive:
                    raise  # Interactive commands shouldn't retry

                error_msg = str(e).lower()
                if any(
                    msg in error_msg
                    for msg in [
                        "docker: command not found",
                        "docker is not installed",
                        "no dev vm running",
                    ]
                ):
                    raise  # These won't be fixed by retry

                if attempt < retries - 1:
                    logger.warning(
                        f"Container execution failed (attempt {attempt + 1}/{retries}): {e}"
                    )
                    time.sleep(2**attempt)  # Exponential backoff: 1s, 2s, 4s
                else:
                    raise

        # This should never be reached, but just in case
        if last_error:
            raise last_error

    def reset(self) -> None:
        """Reset all containers on dev VM.

        Stops and removes all dev containers, cleans up images.
        The VM itself remains running for fast restarts.

        Raises:
            RuntimeError: If dev VM is not started
        """
        self._ensure_vm()
        self._executor.reset_containers()
        logger.info("Dev containers reset successfully")

    def stop(self) -> bool:
        """Stop the development VM.

        Terminates the persistent VM and all containers.

        Returns:
            True if VM was stopped, False if no VM was running
        """
        stopped = self._vm_manager.stop_dev_vm()
        if stopped:
            self._current_vm = None
            self._executor = None
            logger.info("Dev VM stopped successfully")
        return stopped

    def status(self) -> DevEnvironmentStatus:
        """Get status of dev environment.

        Returns information about the running VM and active containers.

        Returns:
            DevEnvironmentStatus with status information:
                - vm: VM details (name, id, instance_type, uptime)
                - active_containers: Number of running containers
                - containers: List of container details

        Example:
            >>> status = flow.dev.status()
            >>> if status['vm']:
            >>>     print(f"VM: {status['vm']['name']}")
            >>>     print(f"Containers: {status['active_containers']}")
        """
        vm = self._vm_manager.find_dev_vm()

        if not vm:
            return {"vm": None, "active_containers": 0, "containers": []}

        # Build VM info
        vm_info = {
            "name": vm.name,
            "id": vm.task_id,
            "instance_type": vm.instance_type,
            "status": "running",
        }

        # Calculate uptime if available
        if vm.started_at:
            from datetime import datetime, timezone

            uptime = datetime.now(timezone.utc) - vm.started_at
            vm_info["uptime_hours"] = round(uptime.total_seconds() / 3600, 2)

        # Get container status
        container_status = {"active_containers": 0, "containers": []}
        try:
            executor = DevContainerExecutor(self._flow, vm)
            container_status = executor.get_container_status()
        except Exception as e:
            logger.debug(f"Could not fetch container status: {e}")

        return {
            "vm": vm_info,
            "active_containers": container_status["active_containers"],
            "containers": container_status["containers"],
        }

    def _wait_for_vm(self, vm: Task) -> None:
        """Wait for VM to be ready for use.

        Args:
            vm: VM task object
        """
        from flow.cli.commands.utils import wait_for_task

        # Wait for running status
        final_status = wait_for_task(self._flow, vm.task_id, watch=False)

        if final_status != "running":
            # Try to get more details about the failure
            error_msg = None
            try:
                task = self._flow.get_task(vm.task_id)
                if hasattr(task, "message") and task.message:
                    error_msg = task.message
            except:
                pass

            raise DevVMStartupError(
                message=error_msg, instance_type=getattr(vm, "instance_type", None)
            )

        # Wait for SSH readiness if needed
        if not vm.ssh_host:
            from flow.providers.mithril.ssh_utils import wait_for_task_ssh_info

            # Ensure provider is initialized
            provider = self._flow._ensure_provider()
            if provider:
                try:
                    vm = wait_for_task_ssh_info(
                        task=vm, provider=provider, timeout=1200, show_progress=False
                    )
                except Exception as e:
                    logger.warning(f"SSH info wait failed: {e}")

        # Give SSH a moment to initialize
        time.sleep(2)

    def __enter__(self):
        """Context manager entry - ensure VM is started.

        Example:
            >>> with flow.dev as dev:
            ...     dev.exec("python train.py")
            ...     # VM automatically stopped on exit if auto_stop=True
        """
        self._context_started = True
        self.ensure_started()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - optionally stop VM.

        Args:
            exc_type: Exception type if error occurred
            exc_val: Exception value if error occurred
            exc_tb: Exception traceback if error occurred
        """
        if self._auto_stop and self._current_vm:
            try:
                self.stop()
            except Exception as e:
                logger.warning(f"Failed to auto-stop dev VM: {e}")

        self._context_started = False
        return False  # Don't suppress exceptions
