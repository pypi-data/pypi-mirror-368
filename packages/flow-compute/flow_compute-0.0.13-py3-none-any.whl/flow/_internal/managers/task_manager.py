"""Task Manager (using unified provider interfaces) - Synchronous version."""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from flow.api.models import Task, TaskConfig, TaskStatus, Volume
from flow.core.provider_interfaces import IComputeProvider, IStorageProvider
from flow.errors import FlowError

logger = logging.getLogger(__name__)


class TaskManager:
    """Orchestrates task execution using compute and storage providers."""

    def __init__(
        self,
        compute_provider: IComputeProvider,
        storage_provider: IStorageProvider,
    ):
        """Initialize task manager.

        Args:
            compute_provider: Provider for compute operations
            storage_provider: Provider for storage operations
        """
        self.compute = compute_provider
        self.storage = storage_provider

    def submit_task(self, config: TaskConfig) -> Task:
        """Submit a new task.

        Args:
            config: Task configuration

        Returns:
            Created Task object

        Raises:
            FlowError: If submission fails
        """
        try:
            # Step 1: Prepare storage volumes if needed
            volume_ids = self._prepare_volumes(config)

            # Step 2: Find suitable instances
            requirements = {
                "instance_type": config.instance_type,
                "region": config.region,
                "max_price": config.max_price_per_hour,
            }

            instances = self.compute.find_instances(requirements, limit=5)
            if not instances:
                raise FlowError("No instances available matching requirements")

            # Step 3: Submit task to best instance
            instance = instances[0]  # Simple selection for now
            task = self.compute.submit_task(
                instance_id=instance.allocation_id,
                config=config,
                volume_ids=volume_ids,
            )

            # The provider returns a complete Task object
            logger.info(f"Submitted task {task.task_id}")
            return task

        except Exception as e:
            logger.error(f"Failed to submit task: {e}")
            raise FlowError(f"Task submission failed: {str(e)}")

    def get_task_status(self, task_id: str) -> Task:
        """Get current status of a task.

        Args:
            task_id: ID of the task

        Returns:
            Task object with current status
        """
        # Get full task details from compute provider
        # According to the interface, get_task returns a complete Task object
        return self.compute.get_task(task_id)

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task.

        Args:
            task_id: ID of the task to cancel

        Returns:
            True if successful
        """
        return self.compute.cancel_task(task_id)

    def get_task_logs(
        self,
        task_id: str,
        log_type: str = "stdout",
    ) -> str:
        """Get logs for a task.

        Args:
            task_id: ID of the task
            log_type: Type of logs (stdout or stderr)

        Returns:
            Log content as string
        """
        return self.compute.get_task_logs(task_id, log_type)

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        limit: int = 100,
    ) -> List[Task]:
        """List tasks with optional filtering.

        Args:
            status: Filter by status
            limit: Maximum number of tasks

        Returns:
            List of Task objects
        """
        # Get tasks from provider
        tasks_data = self.compute.list_tasks(
            status=status.value if status else None,
            limit=limit,
        )

        # Convert to Task objects
        tasks = []
        for data in tasks_data:
            task = Task(
                task_id=data["task_id"],
                name=data.get("name", ""),
                status=TaskStatus(data.get("status", "pending")),
                created_at=data.get("created_at", datetime.now()),
                instance_type=data.get("instance_type", ""),
                num_instances=len(data.get("instances", [])),
                region=data.get("region", ""),
                cost_per_hour=data.get("cost_per_hour", "$0.00"),
                instances=data.get("instances", []),
                message=data.get("message"),
            )
            tasks.append(task)

        return tasks

    def wait_for_completion(
        self,
        task_id: str,
        timeout: Optional[int] = None,
        poll_interval: int = 5,
    ) -> Task:
        """Wait for a task to complete.

        Args:
            task_id: ID of the task
            timeout: Maximum seconds to wait
            poll_interval: Seconds between status checks

        Returns:
            Final Task object

        Raises:
            FlowError: If timeout exceeded
        """
        start_time = time.time()

        while True:
            task = self.get_task_status(task_id)

            if task.is_terminal:
                return task

            if timeout and (time.time() - start_time) > timeout:
                raise FlowError(f"Timeout waiting for task {task_id}")

            time.sleep(poll_interval)

    # ============ Storage Operations ============

    def create_volume(
        self,
        size_gb: int,
        name: Optional[str] = None,
    ) -> Volume:
        """Create a storage volume.

        Args:
            size_gb: Size in GB
            name: Optional volume name

        Returns:
            Created Volume object
        """
        return self.storage.create_volume(size_gb, name)

    def upload_to_volume(
        self,
        volume_id: str,
        source: Path,
    ) -> bool:
        """Upload file or directory to volume.

        Args:
            volume_id: ID of the volume
            source: Local file or directory path

        Returns:
            True if successful
        """
        if source.is_file():
            return self.storage.upload_file(volume_id, source)
        elif source.is_dir():
            return self.storage.upload_directory(volume_id, source)
        else:
            raise FlowError(f"Source path does not exist: {source}")

    def download_from_volume(
        self,
        volume_id: str,
        remote_path: str,
        local_path: Path,
        is_directory: bool = False,
    ) -> bool:
        """Download file or directory from volume.

        Args:
            volume_id: ID of the volume
            remote_path: Path in volume
            local_path: Local destination
            is_directory: Whether remote path is a directory

        Returns:
            True if successful
        """
        if is_directory:
            return self.storage.download_directory(volume_id, remote_path, local_path)
        else:
            return self.storage.download_file(volume_id, remote_path, local_path)

    # ============ Private Methods ============

    def _prepare_volumes(self, config: TaskConfig) -> List[str]:
        """Prepare storage volumes for task.

        Args:
            config: Task configuration

        Returns:
            List of volume IDs
        """
        volume_ids = []

        for vol_spec in config.volumes:
            if vol_spec.volume_id:
                # Use existing volume
                volume_ids.append(vol_spec.volume_id)
            else:
                # Create new volume
                volume = self.storage.create_volume(
                    size_gb=vol_spec.size_gb,
                    name=f"{config.name}-volume",
                )
                volume_ids.append(volume.volume_id)
                logger.info(f"Created volume {volume.volume_id}")

        return volume_ids
