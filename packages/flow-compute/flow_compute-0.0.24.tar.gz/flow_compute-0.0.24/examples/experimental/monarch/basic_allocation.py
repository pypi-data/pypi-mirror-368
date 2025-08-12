#!/usr/bin/env python3
"""Monarch Integration Example: Basic Compute Allocation (Experimental).

Uses internal integration APIs; not for production use.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

from flow._internal.integrations.monarch import MonarchFlowConfig
from flow._internal.integrations.monarch_adapter import create_monarch_backend


async def main():
    print("Monarch + Flow Integration: Current Capabilities Demo")
    print("=" * 50)
    print()

    config = MonarchFlowConfig(
        provider="mithril", default_instance_type="h100", startup_timeout=1200.0
    )
    print("1. Creating Monarch backend with Mithril provider...")
    backend = await create_monarch_backend(provider="mithril", config=config)
    print("   ✓ Backend created\n")

    print("2. Allocating compute resources (1 node, 2 GPUs)...")
    try:
        mesh = await backend.create_proc_mesh(shape=(1, 2), constraints={"gpu_type": "h100"})
        print(f"   ✓ Created mesh with shape {mesh.shape}")
        print(f"   ✓ Mesh ID: {mesh.id}\n")

        print("3. What works today:")
        print("   - Flow tasks created for Monarch workers")
        print("   - SSH access available to workers\n")

        print("4. Not implemented yet:")
        print("   - Actor spawning")
        print("   - Actor communication\n")
    except Exception as e:
        print(f"   ✗ Error creating mesh: {e}")
        print("   Ensure Flow config and access are set up")


if __name__ == "__main__":
    asyncio.run(main())
