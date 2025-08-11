#!/usr/bin/env python3
"""Basic Monarch-Flow Integration Example (Experimental)."""

from __future__ import annotations

import asyncio
import logging

from flow._internal.integrations import (
    create_monarch_backend,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def basic_example():
    backend = await create_monarch_backend(provider="mithril", default_instance_type="h100")
    try:
        mesh = await backend.create_proc_mesh(shape=(2, 4), constraints={"gpu_type": "h100"})
        print(f"Process mesh created: {mesh.shape} @ {mesh.addresses}")
        health = await mesh.health_check()
        print("Health:")
        for pid, ok in health.items():
            print(f"  {pid}: {'healthy' if ok else 'unhealthy'}")
        await asyncio.sleep(10)
    finally:
        await backend.stop_all()


async def main():
    await basic_example()


if __name__ == "__main__":
    asyncio.run(main())
