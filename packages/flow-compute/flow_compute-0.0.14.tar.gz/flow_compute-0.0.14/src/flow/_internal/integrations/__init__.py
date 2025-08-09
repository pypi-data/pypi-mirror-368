"""Flow integrations package."""

# Monarch integration exports
from .monarch import (
    ComputeRequirements,
    ProcessHandle,
    ProcessLifecycleEvents,
    ComputeAllocator,
    FlowComputeAllocator,
    ComputeAllocatorFactory,
    MonarchFlowConfig,
    MonarchFlowError,
    AllocationError,
    NetworkError,
)

from .monarch_adapter import (
    MonarchAllocatorAdapter,
    MonarchFlowBackend,
    FlowProcMesh,
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
