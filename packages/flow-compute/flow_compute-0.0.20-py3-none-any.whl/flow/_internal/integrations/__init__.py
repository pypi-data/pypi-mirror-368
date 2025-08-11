"""Flow integrations package."""

# Monarch integration exports
from flow._internal.integrations.monarch import (
    AllocationError,
    ComputeAllocator,
    ComputeAllocatorFactory,
    ComputeRequirements,
    FlowComputeAllocator,
    MonarchFlowConfig,
    MonarchFlowError,
    NetworkError,
    ProcessHandle,
    ProcessLifecycleEvents,
)
from flow._internal.integrations.monarch_adapter import (
    FlowProcMesh,
    MonarchAllocatorAdapter,
    MonarchFlowBackend,
    create_monarch_backend,
)

__all__ = [
    # Core abstractions
    "ComputeRequirements",
    "ProcessHandle",
    "ProcessLifecycleEvents",
    "ComputeAllocator",
    # Flow implementation
    "FlowComputeAllocator",
    "ComputeAllocatorFactory",
    "MonarchFlowConfig",
    # Monarch adapter
    "MonarchAllocatorAdapter",
    "MonarchFlowBackend",
    "FlowProcMesh",
    "create_monarch_backend",
    # Errors
    "MonarchFlowError",
    "AllocationError",
    "NetworkError",
]
