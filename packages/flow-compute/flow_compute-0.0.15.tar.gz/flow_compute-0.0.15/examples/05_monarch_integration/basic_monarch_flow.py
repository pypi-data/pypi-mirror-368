"""
Basic Monarch-Flow Integration Example
=====================================

This example demonstrates how to use Flow SDK as a compute backend for Monarch.
It shows the basic workflow of creating a process mesh and spawning actors.
"""

import asyncio
import logging
from typing import List

from flow import Flow
from flow._internal.integrations import (
    MonarchFlowBackend,
    create_monarch_backend,
    MonarchFlowConfig,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def basic_example():
    """Basic example of using Monarch with Flow backend."""

    # Create a Monarch backend using Flow
    backend = await create_monarch_backend(
        provider="mithril",
        default_instance_type="h100",
    )

    try:
        # Create a process mesh with 2 hosts, 4 GPUs each
        print("Creating process mesh...")
        mesh = await backend.create_proc_mesh(
            shape=(2, 4),  # 2 hosts, 4 GPUs per host
            constraints={
                "gpu_type": "h100",
                "region": "us-central1-a",
            },
        )

        print(f"Process mesh created with shape: {mesh.shape}")
        print(f"Addresses: {mesh.addresses}")

        # Check health of all processes
        health_status = await mesh.health_check()
        print("\nHealth check results:")
        for process_id, is_healthy in health_status.items():
            status = "healthy" if is_healthy else "unhealthy"
            print(f"  Process {process_id}: {status}")

        # In a real Monarch application, you would now spawn actors:
        # actor = await mesh.spawn("my_actor", MyActorClass, arg1, arg2)
        # result = await actor.my_method.call()

        print("\nProcess mesh is ready for Monarch actors!")
        print("In a real application, you would now spawn actors on this mesh.")

        # Keep running for demonstration
        await asyncio.sleep(30)

    finally:
        # Clean up
        print("\nStopping all processes...")
        await backend.stop_all()
        print("Done!")


async def advanced_example():
    """Advanced example with custom configuration."""

    # Create custom configuration
    config = MonarchFlowConfig(
        provider="mithril",
        default_instance_type="h100",
        startup_timeout=600.0,  # 10 minutes for large instances
        health_check_interval=15.0,
    )

    # Create backend with custom config
    backend = MonarchFlowBackend(config=config)

    try:
        # Create multiple meshes for different workloads

        # Mesh 1: Training cluster (8x H100 GPUs)
        print("Creating training mesh...")
        training_mesh = await backend.create_proc_mesh(
            shape=(1, 8),  # 1 host, 8 GPUs
            constraints={
                "gpu_type": "h100",
                "min_gpu_memory_gb": 80,
            },
        )

        # Mesh 2: Inference cluster (multiple single-GPU instances)
        print("Creating inference mesh...")
        inference_mesh = await backend.create_proc_mesh(
            shape=(4, 1),  # 4 hosts, 1 GPU each
            constraints={
                "gpu_type": "h100",
            },
        )

        print(f"\nTraining mesh: {training_mesh.shape} at {training_mesh.addresses}")
        print(f"Inference mesh: {inference_mesh.shape} at {inference_mesh.addresses}")

        # Simulate workload
        print("\nMeshes ready for distributed computing!")
        await asyncio.sleep(30)

    finally:
        await backend.stop_all()


async def capability_based_example():
    """Example using capability-based instance selection."""

    # Create backend
    backend = await create_monarch_backend(provider="mithril")

    try:
        # Request instances based on capabilities rather than specific types
        print("Creating mesh with capability-based requirements...")
        mesh = await backend.create_proc_mesh(
            shape=(2, 2),  # 2 hosts, 2 GPUs each
            constraints={
                "min_gpu_memory_gb": 40,  # At least 40GB GPU memory
                "cpu_count": 32,  # At least 32 CPUs
                "memory_gb": 128,  # At least 128GB RAM
            },
        )

        print(f"Mesh created: {mesh.shape}")
        print(f"Addresses: {mesh.addresses}")

        # The system will find suitable instances that meet these requirements

        await asyncio.sleep(30)

    finally:
        await backend.stop_all()


async def main():
    """Run examples based on command line argument."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "advanced":
        await advanced_example()
    elif len(sys.argv) > 1 and sys.argv[1] == "capability":
        await capability_based_example()
    else:
        await basic_example()


if __name__ == "__main__":
    # Note: You need to have FLOW_API_KEY and FLOW_PROJECT configured
    # See Flow SDK documentation for setup instructions
    asyncio.run(main())
