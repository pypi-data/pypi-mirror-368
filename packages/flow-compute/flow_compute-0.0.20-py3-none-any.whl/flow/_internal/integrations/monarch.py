"""
Monarch-Flow integration.

Provides a production-oriented adapter that allocates GPU resources via Flow
and wires them into Monarch's process lifecycle.
"""

import asyncio
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Protocol

from flow import Flow
from flow.api.models import Task, TaskConfig
from flow.errors import FlowError

# ============================================================================
# CORE ABSTRACTIONS
# ============================================================================


@dataclass
class ComputeRequirements:
    """Pure data class representing compute needs - no implementation details."""

    gpu_count: int
    gpu_memory_gb: int | None = None
    gpu_type: str | None = None  # e.g., "a100", "h100"
    cpu_count: int | None = None
    memory_gb: int | None = None
    region: str | None = None


@dataclass
class ProcessHandle:
    """Opaque handle to a running process - no implementation details exposed."""

    id: str
    address: str
    metadata: dict[str, Any]  # For extensibility without breaking interface


class ProcessLifecycleEvents(Protocol):
    """Protocol for process lifecycle - implementations can vary."""

    async def on_created(self, handle: ProcessHandle) -> None:
        """Called when process is created but not yet running."""
        ...

    async def on_running(self, handle: ProcessHandle) -> None:
        """Called when process is fully running and ready."""
        ...

    async def on_stopped(self, handle: ProcessHandle, reason: str) -> None:
        """Called when process stops."""
        ...

    async def on_failed(self, handle: ProcessHandle, error: str) -> None:
        """Called when process fails."""
        ...


class ComputeAllocator(Protocol):
    """
    Abstract interface for allocating compute resources.
    This is the key abstraction that allows Monarch to work with any backend.
    """

    async def allocate(
        self, requirements: ComputeRequirements, lifecycle: ProcessLifecycleEvents
    ) -> ProcessHandle:
        """Allocate compute resources and return a handle to the process."""
        ...

    async def deallocate(self, handle: ProcessHandle) -> None:
        """Release compute resources associated with the handle."""
        ...

    async def health_check(self, handle: ProcessHandle) -> bool:
        """Check if the process is still healthy."""
        ...


# ============================================================================
# FLOW IMPLEMENTATION
# ============================================================================


class FlowComputeAllocator:
    """
    Production-ready Flow implementation of ComputeAllocator.
    This is the ONLY place where Flow-specific code exists.
    """

    def __init__(
        self,
        flow_client: Flow | None = None,
        provider: str = "mithril",
        default_instance_type: str | None = None,
        startup_timeout: float = 300.0,
    ):
        """
        Initialize the Flow compute allocator.

        Args:
            flow_client: Flow client instance (creates one if not provided)
            provider: Cloud provider to use (default: "mithril")
            default_instance_type: Default instance type if not specified
            startup_timeout: Timeout for process startup in seconds
        """
        self._flow = flow_client or Flow()
        self._provider = provider
        self._default_instance_type = default_instance_type
        self._startup_timeout = startup_timeout
        self._tasks: dict[str, Task] = {}
        self._monitors: dict[str, asyncio.Task] = {}
        self._logger = logging.getLogger(__name__)

    async def allocate(
        self, requirements: ComputeRequirements, lifecycle: ProcessLifecycleEvents
    ) -> ProcessHandle:
        """Allocate compute via Flow SDK."""
        # Build Flow task configuration from requirements
        config_dict = {
            "name": f"monarch-worker-{requirements.gpu_count}gpu",
            "command": self._create_monarch_worker_command(),
        }

        # Map requirements to Flow configuration
        if requirements.gpu_type:
            # Handle multi-GPU instance types
            if requirements.gpu_count > 1:
                config_dict["instance_type"] = f"{requirements.gpu_count}x{requirements.gpu_type}"
            else:
                config_dict["instance_type"] = requirements.gpu_type
        elif requirements.gpu_memory_gb:
            config_dict["min_gpu_memory_gb"] = requirements.gpu_memory_gb
            # Note: TaskConfig doesn't have min_gpu_count field
            # When using min_gpu_memory_gb, we need to use instance type for multi-GPU
            if requirements.gpu_count and requirements.gpu_count > 1:
                # Default to multi-GPU h100 when memory requirement is specified
                config_dict["instance_type"] = f"{requirements.gpu_count}xh100"
                # Remove min_gpu_memory_gb to avoid conflict with instance_type
                del config_dict["min_gpu_memory_gb"]
        elif self._default_instance_type:
            config_dict["instance_type"] = self._default_instance_type
        else:
            # Default to h100 if nothing specified
            if requirements.gpu_count > 1:
                config_dict["instance_type"] = f"{requirements.gpu_count}xh100"
            else:
                config_dict["instance_type"] = "h100"

        # Add optional requirements
        # Note: TaskConfig doesn't support min_cpu_count or min_memory_gb
        # These would need to be translated to specific instance types

        if requirements.region:
            config_dict["region"] = requirements.region

        # Add Monarch-specific configuration
        config_dict["env"] = {
            "MONARCH_MODE": "flow",
            "MONARCH_WORKER_PORT": "8000",
            "PYTHONPATH": "/workspace:$PYTHONPATH",
        }

        # Enable code upload for Monarch worker
        config_dict["upload_code"] = True

        # Create TaskConfig
        config = TaskConfig(**config_dict)

        # Launch Flow task
        self._logger.info(f"Launching Flow task for Monarch worker: {config_dict}")
        task = await self._flow.run(config)

        # Wait for task to get an ID
        while not task.task_id:
            await asyncio.sleep(0.1)

        # Create process handle
        handle = ProcessHandle(
            id=task.task_id,
            address=f"{task.ssh_host}:8000" if task.ssh_host else "pending",
            metadata={
                "provider": self._provider,
                "instance_type": task.instance_type,
                "gpu_count": requirements.gpu_count,
                "region": task.region,
            },
        )

        self._tasks[handle.id] = task

        # Start lifecycle monitoring
        monitor = asyncio.create_task(self._monitor_lifecycle(handle, task, lifecycle))
        self._monitors[handle.id] = monitor

        # Notify created
        await lifecycle.on_created(handle)

        return handle

    async def deallocate(self, handle: ProcessHandle) -> None:
        """Stop Flow task and clean up resources."""
        if handle.id not in self._tasks:
            return

        self._logger.info(f"Deallocating Monarch process {handle.id}")

        # Cancel monitor
        if handle.id in self._monitors:
            self._monitors[handle.id].cancel()
            try:
                await self._monitors[handle.id]
            except asyncio.CancelledError:
                pass
            del self._monitors[handle.id]

        # Stop task
        task = self._tasks[handle.id]
        await task.stop()
        del self._tasks[handle.id]

    async def health_check(self, handle: ProcessHandle) -> bool:
        """Check if Flow task is healthy."""
        if handle.id not in self._tasks:
            return False

        task = self._tasks[handle.id]
        # Refresh status from provider
        task.refresh()
        return task.status == "running"

    def _create_monarch_worker_command(self) -> list[str]:
        """Generate startup command for Monarch worker process."""
        # This returns a command that will be executed on the GPU instance
        # The actual Monarch worker code should be uploaded via upload_code=True
        return [
            "bash",
            "-c",
            """
            # Install Monarch if needed
            if [ ! -d "/workspace/monarch" ]; then
                echo "Installing Monarch..."
                pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
                git clone https://github.com/pytorch-labs/monarch.git /workspace/monarch
                cd /workspace/monarch && pip install -e .
            fi
            
            # Start Monarch worker process
            echo "Starting Monarch worker on port 8000..."
            python -m monarch.worker --mode=flow --address=0.0.0.0:8000
            """,
        ]

    async def _monitor_lifecycle(
        self, handle: ProcessHandle, task: Task, lifecycle: ProcessLifecycleEvents
    ) -> None:
        """Monitor Flow task and emit lifecycle events."""
        try:
            # Wait for task to be running
            start_time = asyncio.get_event_loop().time()
            while task.status == "pending":
                await asyncio.sleep(1)
                task.refresh()

                # Check timeout
                if asyncio.get_event_loop().time() - start_time > self._startup_timeout:
                    await lifecycle.on_failed(handle, "Startup timeout exceeded")
                    return

            if task.status == "running":
                # Update address with actual SSH host
                if task.ssh_host:
                    handle.address = f"{task.ssh_host}:8000"
                await lifecycle.on_running(handle)

                # Monitor until stopped
                while task.status == "running":
                    await asyncio.sleep(5)
                    task.refresh()

            # Task stopped
            if task.status == "completed":
                await lifecycle.on_stopped(handle, "completed")
            elif task.status == "cancelled":
                await lifecycle.on_stopped(handle, "user_requested")
            elif task.status == "failed":
                error_msg = task.message or "unknown_error"
                await lifecycle.on_failed(handle, error_msg)

        except asyncio.CancelledError:
            # Monitor was cancelled, likely due to deallocation
            pass
        except Exception as e:
            self._logger.error(f"Monitor error for {handle.id}: {e}")
            await lifecycle.on_failed(handle, str(e))

    async def cleanup(self) -> None:
        """Clean up all monitor tasks."""
        # Cancel all monitor tasks
        for monitor_id, monitor_task in list(self._monitors.items()):
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
        self._monitors.clear()

        # Cancel any running tasks
        for task_id, task in self._tasks.items():
            if task.status in ("pending", "running"):
                try:
                    self._flow.cancel(task_id)
                except Exception as e:
                    self._logger.error(f"Failed to cancel task {task_id}: {e}")


# ============================================================================
# FACTORY PATTERN
# ============================================================================


class ComputeAllocatorFactory:
    """Factory for creating allocators - extensible without modification."""

    _creators: dict[str, type] = {}

    @classmethod
    def register(cls, name: str, creator: type):
        """Register a new allocator type."""
        cls._creators[name] = creator

    @classmethod
    def create(cls, name: str, **kwargs) -> ComputeAllocator:
        """Create an allocator by name."""
        if name not in cls._creators:
            raise ValueError(f"Unknown allocator: {name}")
        return cls._creators[name](**kwargs)


# Register Flow implementation
ComputeAllocatorFactory.register("flow", FlowComputeAllocator)


# ============================================================================
# CONFIGURATION
# ============================================================================


@dataclass
class MonarchFlowConfig:
    """Configuration for Monarch-Flow integration."""

    provider: str = "mithril"
    default_instance_type: str | None = None
    startup_timeout: float = 300.0
    health_check_interval: float = 30.0

    # Advanced options
    custom_worker_script: str | None = None
    environment_vars: dict[str, str] = field(default_factory=dict)
    mount_paths: list[str] = field(default_factory=list)

    @classmethod
    def from_env(cls) -> "MonarchFlowConfig":
        """Load configuration from environment variables."""
        return cls(
            provider=os.getenv("MONARCH_FLOW_PROVIDER", "mithril"),
            default_instance_type=os.getenv("MONARCH_FLOW_INSTANCE_TYPE"),
            startup_timeout=float(os.getenv("MONARCH_FLOW_STARTUP_TIMEOUT", "300")),
            health_check_interval=float(os.getenv("MONARCH_FLOW_HEALTH_CHECK_INTERVAL", "30")),
        )


# ============================================================================
# ERROR HANDLING
# ============================================================================


class MonarchFlowError(FlowError):
    """Base exception for Monarch-Flow integration errors."""

    pass


class AllocationError(MonarchFlowError):
    """Failed to allocate compute resources."""

    pass


class NetworkError(MonarchFlowError):
    """Network connectivity issues between processes."""

    pass
