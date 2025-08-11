"""Monarch adapter for Flow integration.

Adapter that lets Monarch use Flow as a compute backend, translating between
Monarch's allocator interface and Flow's ``ComputeAllocator`` abstraction.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

from flow._internal.integrations.monarch import (
    ComputeAllocator,
    ComputeRequirements,
    FlowComputeAllocator,
    MonarchFlowConfig,
    ProcessHandle,
    ProcessLifecycleEvents,
)

# ============================================================================
# MONARCH-SPECIFIC TYPES (These would normally come from Monarch)
# ============================================================================


@dataclass
class AllocSpec:
    """Monarch's allocation specification."""

    shape: tuple[int, int]  # (num_hosts, gpus_per_host)
    constraints: dict[str, Any] = None

    def __post_init__(self):
        if self.constraints is None:
            self.constraints = {}


@dataclass
class MonarchAllocation:
    """Monarch's allocation result."""

    handles: list[ProcessHandle]
    shape: tuple[int, int]
    addresses: list[str]


# ============================================================================
# LIFECYCLE ADAPTER
# ============================================================================


class MonarchLifecycleAdapter(ProcessLifecycleEvents):
    """Adapts our lifecycle events to Monarch's needs."""

    def __init__(self, host_idx: int, backend: "MonarchFlowBackend"):
        self.host_idx = host_idx
        self.backend = backend
        self.ready = asyncio.Event()
        self.failed = False
        self.error_msg: str | None = None

    async def on_created(self, handle: ProcessHandle) -> None:
        """Called when process is created."""
        logging.info(f"Monarch host {self.host_idx} created: {handle.id}")

    async def on_running(self, handle: ProcessHandle) -> None:
        """Called when process is running."""
        logging.info(f"Monarch host {self.host_idx} running at {handle.address}")
        self.ready.set()

    async def on_stopped(self, handle: ProcessHandle, reason: str) -> None:
        """Called when process stops."""
        logging.info(f"Monarch host {self.host_idx} stopped: {reason}")
        if not self.ready.is_set():
            self.failed = True
            self.error_msg = f"Process stopped before becoming ready: {reason}"
            self.ready.set()

    async def on_failed(self, handle: ProcessHandle, error: str) -> None:
        """Called when process fails."""
        logging.error(f"Monarch host {self.host_idx} failed: {error}")
        self.failed = True
        self.error_msg = error
        self.ready.set()


# ============================================================================
# MONARCH ADAPTER
# ============================================================================


class MonarchAllocatorAdapter:
    """
    Adapts our clean ComputeAllocator interface to Monarch's Allocator trait.
    This is the ONLY place where Monarch-specific translation occurs.
    """

    def __init__(self, allocator: ComputeAllocator):
        """
        Initialize the adapter.

        Args:
            allocator: The compute allocator to use (e.g., FlowComputeAllocator)
        """
        self._allocator = allocator
        self._allocations: dict[str, MonarchAllocation] = {}
        self._handles: dict[str, ProcessHandle] = {}
        self._logger = logging.getLogger(__name__)

    async def allocate(self, spec: AllocSpec) -> MonarchAllocation:
        """
        Monarch's allocate method - translates to our clean interface.

        Args:
            spec: Monarch's allocation specification

        Returns:
            MonarchAllocation containing process handles and addresses
        """
        hosts, gpus_per_host = spec.shape

        # Extract requirements from Monarch's AllocSpec
        requirements = ComputeRequirements(
            gpu_count=gpus_per_host,
            gpu_type=spec.constraints.get("gpu_type"),
            gpu_memory_gb=spec.constraints.get("min_gpu_memory_gb"),
            cpu_count=spec.constraints.get("cpu_count"),
            memory_gb=spec.constraints.get("memory_gb"),
            region=spec.constraints.get("region"),
        )

        # Allocate processes for each host
        handles = []
        lifecycle_adapters = []

        for host_idx in range(hosts):
            # Create lifecycle adapter for this host
            lifecycle = MonarchLifecycleAdapter(host_idx, self)
            lifecycle_adapters.append(lifecycle)

            # Allocate compute through our clean interface
            handle = await self._allocator.allocate(requirements, lifecycle)
            handles.append(handle)
            self._handles[handle.id] = handle

        # Create allocation result
        allocation = MonarchAllocation(
            handles=handles, shape=spec.shape, addresses=[h.address for h in handles]
        )

        # Store allocation for later reference
        allocation_id = f"alloc-{id(allocation)}"
        self._allocations[allocation_id] = allocation

        # Wait for all processes to be ready (with timeout)
        ready_tasks = [
            asyncio.wait_for(adapter.ready.wait(), timeout=300) for adapter in lifecycle_adapters
        ]

        try:
            await asyncio.gather(*ready_tasks)

            # Check if any failed
            for idx, adapter in enumerate(lifecycle_adapters):
                if adapter.failed:
                    # Clean up and raise error
                    await self._cleanup_allocation(allocation)
                    raise RuntimeError(f"Host {idx} failed to start: {adapter.error_msg}")

            # Update addresses now that all are running
            allocation.addresses = [h.address for h in handles]

        except asyncio.TimeoutError:
            # Clean up on timeout
            await self._cleanup_allocation(allocation)
            raise RuntimeError("Timeout waiting for Monarch processes to start")

        return allocation

    async def deallocate(self, allocation: MonarchAllocation) -> None:
        """
        Deallocate all processes in a Monarch allocation.

        Args:
            allocation: The allocation to deallocate
        """
        await self._cleanup_allocation(allocation)

    async def _cleanup_allocation(self, allocation: MonarchAllocation) -> None:
        """Clean up all processes in an allocation."""
        # Deallocate all handles
        tasks = [self._allocator.deallocate(handle) for handle in allocation.handles]
        await asyncio.gather(*tasks, return_exceptions=True)

        # Remove from tracking
        for handle in allocation.handles:
            self._handles.pop(handle.id, None)

    async def health_check_all(self) -> dict[str, bool]:
        """
        Check health of all allocated processes.

        Returns:
            Dictionary mapping process IDs to health status
        """
        results = {}
        for handle_id, handle in self._handles.items():
            results[handle_id] = await self._allocator.health_check(handle)
        return results


# ============================================================================
# MONARCH BACKEND
# ============================================================================


class MonarchFlowBackend:
    """
    Monarch backend that uses Flow for compute allocation.
    This would be integrated into Monarch's codebase.
    """

    def __init__(
        self,
        allocator: ComputeAllocator | None = None,
        config: MonarchFlowConfig | None = None,
    ):
        """
        Initialize the Monarch Flow backend.

        Args:
            allocator: Custom allocator to use (creates FlowComputeAllocator if not provided)
            config: Configuration for the backend
        """
        self._config = config or MonarchFlowConfig.from_env()
        self._allocator = allocator or FlowComputeAllocator(
            provider=self._config.provider,
            default_instance_type=self._config.default_instance_type,
            startup_timeout=self._config.startup_timeout,
        )
        self._adapter = MonarchAllocatorAdapter(self._allocator)
        self._proc_meshes: list[FlowProcMesh] = []
        self._logger = logging.getLogger(__name__)

    async def create_proc_mesh(
        self, shape: tuple[int, int], constraints: dict[str, Any] | None = None
    ) -> "FlowProcMesh":
        """
        Create a Monarch ProcMesh using Flow compute.

        Args:
            shape: (num_hosts, gpus_per_host) tuple
            constraints: Optional constraints for allocation

        Returns:
            FlowProcMesh instance
        """
        spec = AllocSpec(shape=shape, constraints=constraints or {})

        # Allocate through adapter
        allocation = await self._adapter.allocate(spec)

        # Create ProcMesh wrapper
        mesh = FlowProcMesh(allocation, self)
        self._proc_meshes.append(mesh)

        return mesh

    async def stop_all(self) -> None:
        """Stop all process meshes."""
        tasks = [mesh.stop() for mesh in self._proc_meshes]
        await asyncio.gather(*tasks, return_exceptions=True)
        self._proc_meshes.clear()


class FlowProcMesh:
    """
    ProcMesh implementation backed by Flow compute.
    This mimics Monarch's ProcMesh interface.
    """

    def __init__(self, allocation: MonarchAllocation, backend: MonarchFlowBackend):
        self._allocation = allocation
        self._backend = backend
        self._stopped = False

    @property
    def shape(self) -> tuple[int, int]:
        """Get the shape of this mesh."""
        return self._allocation.shape

    @property
    def addresses(self) -> list[str]:
        """Get network addresses of all processes."""
        return self._allocation.addresses

    async def spawn(self, name: str, actor_class: type, *args, **kwargs) -> Any:
        """
        Spawn an actor on this mesh.

        Note: This is a placeholder - actual implementation would depend on
        Monarch's actor spawning mechanism.
        """
        # In a real implementation, this would:
        # 1. Connect to the processes via their addresses
        # 2. Deploy the actor code
        # 3. Return a proxy to interact with the actor
        raise NotImplementedError("Actor spawning not implemented in this prototype")

    async def stop(self) -> None:
        """Stop this mesh."""
        if not self._stopped:
            await self._backend._adapter.deallocate(self._allocation)
            self._stopped = True

    async def health_check(self) -> dict[str, bool]:
        """Check health of all processes in this mesh."""
        results = {}
        for handle in self._allocation.handles:
            results[handle.id] = await self._backend._allocator.health_check(handle)
        return results


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================


async def create_monarch_backend(provider: str = "mithril", **kwargs) -> MonarchFlowBackend:
    """
    Create a Monarch backend configured for a specific provider.

    Args:
        provider: Cloud provider to use ("mithril", "aws", etc.)
        **kwargs: Additional configuration options

    Returns:
        Configured MonarchFlowBackend instance
    """
    config = MonarchFlowConfig(provider=provider, **kwargs)
    return MonarchFlowBackend(config=config)
