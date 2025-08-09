"""Local testing provider implementation."""

import logging
import subprocess
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List, Optional

from flow._internal.config import Config
from flow.api.models import AvailableInstance, Task, TaskConfig, TaskStatus, Volume, VolumeSpec
from flow.core.provider_interfaces import IComputeProvider
from flow.providers.interfaces import IProviderInit
from flow.errors import FlowError, TaskNotFoundError, VolumeError
from flow.providers.local.config import LocalTestConfig
from flow.providers.local.executor import ContainerTaskExecutor, ProcessTaskExecutor, TaskExecutor
from flow.providers.local.logs import LocalLogManager
from flow.providers.local.storage import LocalStorage

logger = logging.getLogger(__name__)


class LocalProvider(IComputeProvider):
    """Local provider for testing Flow SDK functionality without cloud infrastructure.

    Provides high-fidelity simulation of Mithril behavior using Docker containers
    or local processes. Enables sub-second test iterations while maintaining
    behavioral accuracy.
    """

    def __init__(self, config: Config):
        """Initialize local provider.

        Args:
            config: SDK configuration object
        """
        if config.provider != "local":
            raise ValueError(f"LocalProvider requires 'local' provider, got: {config.provider}")

        self.config = config

        # Extract local-specific configuration from provider_config
        # For now, use defaults - could be extended to read from config.provider_config
        self.local_config = LocalTestConfig.default()
        self.tasks: Dict[str, Task] = {}
        self.storage = LocalStorage(self.local_config.storage_dir)
        self.log_manager = LocalLogManager(self.local_config.storage_dir)

        # Choose executor based on config and availability
        if self.local_config.use_docker:
            try:
                # Try to create Docker executor
                self.executor: TaskExecutor = ContainerTaskExecutor(self.local_config)
                logger.info("Using Docker executor for local tasks")
            except Exception as e:
                # Fall back to process executor if Docker is not available
                logger.warning(f"Docker not available ({e}), falling back to process executor")
                self.local_config.use_docker = False
                self.executor = ProcessTaskExecutor(self.local_config)
        else:
            self.executor = ProcessTaskExecutor(self.local_config)

        # Initialize provider
        self._initialize()

    @classmethod
    def from_config(cls, config: Config) -> "LocalProvider":
        """Create LocalProvider from config.

        This is the standard factory method used by the SDK.

        Args:
            config: SDK configuration

        Returns:
            Initialized LocalProvider instance
        """
        return cls(config)

    def _initialize(self):
        """Initialize local provider environment."""
        # Create storage directories
        self.storage.initialize()

        # Verify Docker if needed
        if self.local_config.use_docker:
            try:
                subprocess.run(["docker", "version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                raise FlowError(
                    "Docker not available. Install Docker or use use_docker=False"
                ) from e

        logger.info(f"LocalProvider initialized with executor: {type(self.executor).__name__}")

    def submit_task(
        self,
        instance_type: str,
        config: TaskConfig,
        volume_ids: Optional[List[str]] = None,
    ) -> Task:
        """Submit a task for local execution.

        Args:
            instance_type: Instance type (e.g., "a100", "h100")
            config: Task configuration
            volume_ids: Optional volume IDs to attach

        Returns:
            Task object with local execution details
        """
        # Generate task ID
        task_id = f"local-{uuid.uuid4().hex[:8]}"

        # Map instance type to local resources
        resources = self.local_config.get_instance_mapping(config.instance_type)

        # Create task object
        task = Task(
            task_id=task_id,
            name=config.name,
            status=TaskStatus.PENDING,
            config=config,
            created_at=datetime.now(timezone.utc),
            instance_type=config.instance_type,
            num_instances=config.num_instances,
            region="local",
            cost_per_hour="$0.00",  # Local execution is free
            ssh_host="localhost",
            ssh_port=22000 + len(self.tasks),  # Unique port per task
            ssh_user="flow",
        )
        # Set provider after creation (PrivateAttr in Pydantic)
        task._provider = self

        # Store task
        self.tasks[task_id] = task

        # Start execution asynchronously
        self._start_task_execution(task, resources)

        return task

    def _start_task_execution(self, task: Task, resources: dict):
        """Start task execution in background."""
        try:
            # Update status
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now(timezone.utc)

            # Start log capture
            self.log_manager.start_log_capture(task.task_id)

            # Execute task
            execution = self.executor.execute_task(
                task_id=task.task_id,
                config=task.config,
                resources=resources,
                log_callback=lambda line: self.log_manager.append_log(task.task_id, line),
            )

            # Store execution reference
            task.instances = [execution.container_id or execution.process_id]

            # Monitor task in background
            import threading

            monitor_thread = threading.Thread(
                target=self._monitor_task, args=(task, execution), daemon=True
            )
            monitor_thread.start()

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.message = str(e)
            logger.error(f"Failed to start task {task.task_id}: {e}")

    def _monitor_task(self, task: Task, execution):
        """Monitor task execution and update status."""
        try:
            # Wait for completion
            exit_code = execution.wait()

            # Give log streaming a moment to catch up
            time.sleep(0.5)

            # Update task status
            if exit_code == 0:
                task.status = TaskStatus.COMPLETED
            else:
                task.status = TaskStatus.FAILED
                task.message = f"Task exited with code {exit_code}"

            task.completed_at = datetime.now(timezone.utc)

            # Calculate mock cost
            duration_hours = (task.completed_at - task.started_at).total_seconds() / 3600
            hourly_rate = 0.10  # Mock rate for local testing
            task.total_cost = f"${duration_hours * hourly_rate:.2f}"

            # Stop log capture
            self.log_manager.stop_log_capture(task.task_id)

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.message = f"Monitor error: {str(e)}"
            logger.error(f"Error monitoring task {task.task_id}: {e}")

    def get_task(self, task_id: str) -> Task:
        """Get task by ID.

        Args:
            task_id: Task identifier

        Returns:
            Task object

        Raises:
            TaskNotFoundError: If task doesn't exist
        """
        if task_id not in self.tasks:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return self.tasks[task_id]

    def list_tasks(self, status: Optional[TaskStatus] = None, limit: int = 100) -> List[Task]:
        """List tasks with optional filtering.

        Args:
            status: Filter by status
            limit: Maximum tasks to return

        Returns:
            List of tasks
        """
        tasks = list(self.tasks.values())

        # Filter by status
        if status:
            tasks = [t for t in tasks if t.status == status]

        # Sort by creation time (newest first)
        tasks.sort(key=lambda t: t.created_at, reverse=True)

        return tasks[:limit]

    def stop_task(self, task_id: str) -> None:
        """Stop a running task.

        Args:
            task_id: Task to stop
        """
        task = self.get_task(task_id)

        if task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            return  # Already stopped

        # Stop execution
        try:
            self.executor.stop_task(task_id)
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now(timezone.utc)
            task.message = "Cancelled by user"
        except Exception as e:
            logger.error(f"Error stopping task {task_id}: {e}")
            raise FlowError(f"Failed to stop task: {str(e)}") from e

    def get_task_logs(self, task_id: str, tail: int = 100, log_type: str = "stdout") -> str:
        """Get task logs.

        Args:
            task_id: Task identifier
            tail: Number of lines to return from end
            log_type: Type of logs (stdout/stderr)

        Returns:
            Log content as string
        """
        task = self.get_task(task_id)

        if task.status == TaskStatus.PENDING:
            return "Task pending - no logs available yet"

        return self.log_manager.get_logs(task_id, tail=tail, log_type=log_type)

    def stream_task_logs(self, task_id: str, log_type: str = "stdout") -> Iterator[str]:
        """Stream task logs in real-time.

        Args:
            task_id: Task identifier
            log_type: Type of logs (stdout/stderr)

        Yields:
            Log lines as they become available
        """
        task = self.get_task(task_id)

        if task.status == TaskStatus.PENDING:
            yield "Task pending - waiting for execution to start..."
            # Wait for task to start
            for _ in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                if task.status != TaskStatus.PENDING:
                    break
            else:
                yield "Task failed to start"
                return

        # Stream logs
        for line in self.log_manager.stream_logs(task_id, log_type=log_type):
            yield line

            # Check if task completed
            task = self.get_task(task_id)
            if task.is_terminal:
                # Yield any final logs
                final_logs = self.log_manager.get_logs(task_id, tail=10, log_type=log_type)
                for line in final_logs.splitlines()[-5:]:
                    if line not in self.log_manager._streamed_lines.get(task_id, set()):
                        yield line
                break

    def create_volume(self, spec: VolumeSpec) -> Volume:
        """Create a local volume.

        Args:
            spec: Volume specification

        Returns:
            Volume object
        """
        volume_id = f"local-vol-{uuid.uuid4().hex[:8]}"
        volume_path = self.storage.create_volume(volume_id, spec.size_gb)

        from flow.api.models import StorageInterface

        return Volume(
            volume_id=volume_id,
            name=spec.name or volume_id,
            size_gb=spec.size_gb,
            region="local",
            interface=spec.interface or StorageInterface.BLOCK,
            created_at=datetime.now(timezone.utc),
            provider_data={"path": str(volume_path), "mount_path": spec.mount_path},
        )

    def delete_volume(self, volume_id: str) -> None:
        """Delete a volume.

        Args:
            volume_id: Volume to delete
        """
        self.storage.delete_volume(volume_id)

    def resize_volume(self, volume_id: str, new_size_gb: int) -> None:
        """Resize a volume.

        Args:
            volume_id: Volume to resize
            new_size_gb: New size in GB
        """
        # For local testing, just update metadata
        logger.info(f"Mock resizing volume {volume_id} to {new_size_gb}GB")

    def get_volume(self, volume_id: str) -> Volume:
        """Get volume details.

        Args:
            volume_id: Volume identifier

        Returns:
            Volume object
        """
        volume_info = self.storage.get_volume_info(volume_id)
        if not volume_info:
            raise VolumeError(
                f"Volume {volume_id} not found",
                suggestions=[
                    "Check the volume ID is correct",
                    "Use 'flow volume list' to see available volumes",
                    "Ensure the volume wasn't deleted",
                ],
                error_code="VOLUME_001",
            )

        from flow.api.models import StorageInterface

        return Volume(
            volume_id=volume_id,
            name=volume_info.get("name", volume_id),
            size_gb=volume_info["size_gb"],
            region="local",
            interface=StorageInterface.BLOCK,
            created_at=datetime.fromisoformat(volume_info["created_at"]),
            provider_data=volume_info,
        )

    def list_volumes(self, limit: int = 100) -> List[Volume]:
        """List all volumes.

        Args:
            limit: Maximum volumes to return

        Returns:
            List of volumes
        """
        volumes = []
        for volume_id in self.storage.list_volumes()[:limit]:
            try:
                volumes.append(self.get_volume(volume_id))
            except Exception as e:
                logger.warning(f"Error loading volume {volume_id}: {e}")

        return volumes

    def cleanup(self):
        """Clean up all local resources."""
        # Stop all running tasks
        for task_id, task in self.tasks.items():
            if task.status == TaskStatus.RUNNING:
                try:
                    self.stop_task(task_id)
                except Exception as e:
                    logger.error(f"Error stopping task {task_id} during cleanup: {e}")

        # Clean up executor
        self.executor.cleanup()

        # Optionally clean storage
        if self.local_config.clean_on_exit:
            self.storage.cleanup()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()

    def prepare_task_config(self, config: TaskConfig) -> TaskConfig:
        """Prepare task configuration with local provider defaults.

        For local provider, we don't need to modify much since everything
        runs locally. Just ensure the config is valid.

        Args:
            config: The user-provided task configuration

        Returns:
            The same task configuration (no modifications needed for local)
        """
        # LocalProvider doesn't need SSH keys or regions
        # Just return the config as-is
        return config

    def find_instances(
        self,
        requirements: Dict[str, Any],
        limit: int = 10,
    ) -> List["AvailableInstance"]:
        """Find available instances matching requirements.

        For local provider, we always have one "instance" available - the local machine.

        Args:
            requirements: Dictionary of requirements (instance_type, etc.)
            limit: Maximum number of instances to return

        Returns:
            List containing a single mock instance representing local execution
        """
        from flow.api.models import AvailableInstance

        # Get requested instance type or default to cpu.small
        instance_type = requirements.get("instance_type", "cpu.small")

        # For local provider, we always have availability
        return [
            AvailableInstance(
                allocation_id="local-instance",
                instance_type=instance_type,
                region="local",
                price_per_hour=0.0,  # Local execution is free
                status="available",
                available_quantity=1,  # One local machine
            )
        ]

    def get_init_interface(self) -> "IProviderInit":
        """Get provider initialization interface.

        Returns:
            IProviderInit implementation for local provider
        """
        from .init import LocalInit

        return LocalInit()
