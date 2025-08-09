#!/usr/bin/env python3
"""
Production GPU infrastructure with Pulumi + Flow SDK.

Architecture:
- Persistent GPU clusters via high spot bids
- Shared storage volumes
- Separate compute tiers (training vs inference)
"""

import pulumi
import flow
from typing import Dict, List

# Configuration
config = pulumi.Config()
env = pulumi.get_stack()

# Spot bidding strategy; example prices
BIDS = {
    "a100": 25.0,
    "8xa100": 50.0,
    "h100": 100.0,
}


def create_storage() -> Dict[str, flow.Volume]:
    """Persistent storage volumes."""
    return {
        "data": flow.create_volume(2000, f"{env}-data"),
        "models": flow.create_volume(500, f"{env}-models"),
        "scratch": flow.create_volume(1000, f"{env}-scratch"),
    }


def create_compute(storage: Dict[str, flow.Volume]) -> Dict[str, flow.Task]:
    """GPU compute clusters."""

    # Training cluster - high performance
    training = flow.run(
        "sleep infinity",
        instance_type="8xa100",
        num_instances=4,
        name=f"{env}-training",
        max_price_per_hour=BIDS["8xa100"],
        volumes=[
            {"volume_id": storage["data"].volume_id, "mount_path": "/data"},
            {"volume_id": storage["models"].volume_id, "mount_path": "/models"},
            {"volume_id": storage["scratch"].volume_id, "mount_path": "/scratch"},
        ],
    )

    # Inference cluster - cost optimized
    inference = flow.run(
        "sleep infinity",
        instance_type="a100",
        num_instances=2,
        name=f"{env}-inference",
        max_price_per_hour=BIDS["a100"],
        volumes=[{"volume_id": storage["models"].volume_id, "mount_path": "/models"}],
    )

    # Wait for all
    training.wait_for_status("RUNNING", timeout=600)
    inference.wait_for_status("RUNNING", timeout=600)

    return {"training": training, "inference": inference}


def main():
    """Deploy infrastructure."""

    # Create resources
    storage = create_storage()
    compute = create_compute(storage)

    # Export endpoints
    pulumi.export("storage", {name: vol.volume_id for name, vol in storage.items()})

    pulumi.export(
        "training",
        {
            "id": compute["training"].task_id,
            "ips": [i.public_ip for i in compute["training"].instances],
            "ssh": f"ssh ubuntu@{compute['training'].instances[0].public_ip}",
        },
    )

    pulumi.export(
        "inference",
        {
            "id": compute["inference"].task_id,
            "endpoints": [f"http://{i.public_ip}:8080" for i in compute["inference"].instances],
        },
    )

    # Useful commands
    pulumi.export(
        "commands",
        {
            "train": (
                f"ssh ubuntu@{compute['training'].instances[0].public_ip} "
                "'cd /models && python train.py'"
            ),
            "logs": f"flow logs {compute['training'].task_id} -f",
        },
    )


if __name__ == "__main__":
    main()
