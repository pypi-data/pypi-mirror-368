#!/usr/bin/env python3
"""
Monarch Integration Example: Basic Compute Allocation

This example shows what already works in the current Monarch integration.
Note: This is experimental and only demonstrates resource allocation, not
actual Monarch actor functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from flow._internal.integrations.monarch_adapter import create_monarch_backend
from flow._internal.integrations.monarch import MonarchFlowConfig


async def main():
    """Demonstrate basic Monarch compute allocation through Flow."""

    print("Monarch + Flow Integration: Current Capabilities Demo")
    print("=" * 50)
    print()

    # 1. Create configuration
    config = MonarchFlowConfig(
        provider="mithril",
        default_instance_type="h100",
        startup_timeout=1200.0,
        environment_vars={"MONARCH_TEST": "true"},
    )

    print("1. Creating Monarch backend with Mithril provider...")
    backend = await create_monarch_backend(provider="mithril", config=config)
    print("   ✓ Backend created")
    print()

    # 2. Allocate compute resources
    print("2. Allocating compute resources (1 node, 2 GPUs)...")
    try:
        mesh = await backend.create_proc_mesh(
            shape=(1, 2),
            constraints={"gpu_type": "h100"},  # 1 node, 2 GPUs
        )
        print(f"   ✓ Created mesh with shape {mesh.shape}")
        print(f"   ✓ Mesh ID: {mesh.id}")
        print()

        # 3. Show what's actually running
        print("3. What's actually running:")
        print("   - Flow tasks have been created for Monarch workers")
        print("   - Workers have Monarch installed (or will install on startup)")
        print("   - SSH access is available to the workers")
        print()

        # 4. Demonstrate what doesn't work
        print("4. What doesn't work yet:")
        print("   - Actor spawning (mesh.spawn() throws NotImplementedError)")
        print("   - Actor communication (no message passing)")
        print("   - Monarch-specific APIs (@endpoint, etc.)")
        print()

        # Try to spawn an actor (this will fail)
        try:
            print("5. Attempting to spawn an actor (will fail)...")

            class DummyActor:
                pass

            await mesh.spawn("dummy", DummyActor)

        except NotImplementedError as e:
            print(f"   ✗ Expected error: {e}")
            print("   This confirms actor spawning is not implemented")

    except Exception as e:
        print(f"   ✗ Error creating mesh: {e}")
        print("   Make sure you have Flow configured and Mithril access")

    print()
    print("Summary: The integration can allocate compute but not run Monarch actors.")
    print("Use standard Flow commands to manage the allocated tasks.")


if __name__ == "__main__":
    asyncio.run(main())
