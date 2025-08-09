"""
Distributed Training with Monarch-Flow Integration
=================================================

This example demonstrates a realistic distributed training scenario using
Monarch's actor model with Flow SDK as the compute backend.

It implements a simplified version of the GRPO training loop shown in the
Monarch examples, demonstrating:
- Multi-mesh deployment (learner mesh + generator mesh)
- Asynchronous actor communication
- Resource-aware allocation
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

import torch
import torch.nn as nn

from flow import Flow
from flow._internal.integrations import (
    MonarchFlowBackend,
    MonarchFlowConfig,
    ProcessLifecycleEvents,
    ProcessHandle,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


# ============================================================================
# MOCK MONARCH COMPONENTS (These would come from actual Monarch library)
# ============================================================================


class Actor:
    """Base class for Monarch actors."""

    pass


def endpoint(func):
    """Decorator for actor endpoints."""
    func.is_endpoint = True
    return func


class MockProcMesh:
    """Mock implementation of Monarch's process mesh."""

    def __init__(self, flow_mesh):
        self.flow_mesh = flow_mesh
        self.actors = {}

    async def spawn(self, name: str, actor_class: type, *args, **kwargs) -> Any:
        """Spawn an actor on this mesh."""
        # In real Monarch, this would deploy the actor to the remote processes
        actor = actor_class(*args, **kwargs)
        self.actors[name] = actor
        return actor


# ============================================================================
# TRAINING COMPONENTS (Simplified from GRPO example)
# ============================================================================


@dataclass
class TrainingConfig:
    """Configuration for distributed training."""

    model_size: str = "7b"  # Model size: "7b", "13b", "70b"
    batch_size: int = 32
    learning_rate: float = 1e-4
    num_epochs: int = 3

    def get_gpu_requirements(self) -> Dict[str, Any]:
        """Get GPU requirements based on model size."""
        if self.model_size == "7b":
            return {
                "learner_gpus": 1,
                "generator_gpus": 2,
                "gpu_type": "h100",
                "min_gpu_memory_gb": 40,
            }
        elif self.model_size == "13b":
            return {
                "learner_gpus": 2,
                "generator_gpus": 4,
                "gpu_type": "h100",
                "min_gpu_memory_gb": 80,
            }
        elif self.model_size == "70b":
            return {
                "learner_gpus": 8,
                "generator_gpus": 8,
                "gpu_type": "h100",
                "min_gpu_memory_gb": 80,
            }
        else:
            raise ValueError(f"Unknown model size: {self.model_size}")


class TrainingQueue(Actor):
    """Queue for training data between components."""

    def __init__(self):
        self.queue = asyncio.Queue()

    @endpoint
    async def put(self, item: Any) -> None:
        await self.queue.put(item)

    @endpoint
    async def get(self) -> Any:
        return await self.queue.get()


class Learner(Actor):
    """Learner actor that updates the model."""

    def __init__(self, config: TrainingConfig, queue: TrainingQueue):
        self.config = config
        self.queue = queue
        self.model = self._create_model()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=config.learning_rate)
        self.step_count = 0

    def _create_model(self) -> nn.Module:
        """Create a dummy model for demonstration."""
        return nn.Sequential(
            nn.Linear(512, 1024),
            nn.ReLU(),
            nn.Linear(1024, 512),
        )

    @endpoint
    async def train_step(self) -> Dict[str, float]:
        """Perform one training step."""
        # Get batch from queue
        batch = await self.queue.get()

        # Simulate training
        loss = torch.rand(1).item()  # Dummy loss

        self.step_count += 1

        return {
            "step": self.step_count,
            "loss": loss,
        }


class Generator(Actor):
    """Generator actor that produces training data."""

    def __init__(self, config: TrainingConfig, queue: TrainingQueue):
        self.config = config
        self.queue = queue

    @endpoint
    async def generate_batch(self) -> None:
        """Generate a batch of training data."""
        # Simulate data generation
        batch = {
            "input": torch.randn(self.config.batch_size, 512),
            "target": torch.randn(self.config.batch_size, 512),
        }

        await self.queue.put(batch)


# ============================================================================
# TRAINING LIFECYCLE MONITOR
# ============================================================================


class TrainingLifecycleMonitor(ProcessLifecycleEvents):
    """Monitor training cluster lifecycle."""

    def __init__(self, cluster_name: str):
        self.cluster_name = cluster_name
        self.ready_count = 0
        self.failed_count = 0
        self.all_ready = asyncio.Event()

    async def on_created(self, handle: ProcessHandle) -> None:
        logging.info(f"[{self.cluster_name}] Process {handle.id} created")

    async def on_running(self, handle: ProcessHandle) -> None:
        logging.info(f"[{self.cluster_name}] Process {handle.id} running at {handle.address}")
        self.ready_count += 1

        # Check if all expected processes are ready
        expected = handle.metadata.get("expected_count", 1)
        if self.ready_count >= expected:
            self.all_ready.set()

    async def on_stopped(self, handle: ProcessHandle, reason: str) -> None:
        logging.warning(f"[{self.cluster_name}] Process {handle.id} stopped: {reason}")

    async def on_failed(self, handle: ProcessHandle, error: str) -> None:
        logging.error(f"[{self.cluster_name}] Process {handle.id} failed: {error}")
        self.failed_count += 1
        self.all_ready.set()  # Set to unblock waiters


# ============================================================================
# DISTRIBUTED TRAINING ORCHESTRATOR
# ============================================================================


class DistributedTrainingOrchestrator:
    """Orchestrates distributed training using Monarch and Flow."""

    def __init__(self, config: TrainingConfig, backend: MonarchFlowBackend):
        self.config = config
        self.backend = backend
        self.learner_mesh = None
        self.generator_mesh = None

    async def setup_infrastructure(self):
        """Set up the distributed infrastructure."""
        gpu_reqs = self.config.get_gpu_requirements()

        # Create learner mesh
        logging.info("Creating learner mesh...")
        self.learner_mesh = await self.backend.create_proc_mesh(
            shape=(1, gpu_reqs["learner_gpus"]),
            constraints={
                "gpu_type": gpu_reqs["gpu_type"],
                "min_gpu_memory_gb": gpu_reqs["min_gpu_memory_gb"],
            },
        )

        # Create generator mesh
        logging.info("Creating generator mesh...")
        self.generator_mesh = await self.backend.create_proc_mesh(
            shape=(1, gpu_reqs["generator_gpus"]),
            constraints={
                "gpu_type": gpu_reqs["gpu_type"],
                "min_gpu_memory_gb": gpu_reqs["min_gpu_memory_gb"],
            },
        )

        logging.info(f"Infrastructure ready:")
        logging.info(f"  Learner mesh: {self.learner_mesh.shape} at {self.learner_mesh.addresses}")
        logging.info(
            f"  Generator mesh: {self.generator_mesh.shape} at {self.generator_mesh.addresses}"
        )

    async def run_training(self):
        """Run the distributed training loop."""
        # Convert Flow meshes to Mock Monarch meshes
        learner_mesh = MockProcMesh(self.learner_mesh)
        gen_mesh = MockProcMesh(self.generator_mesh)

        # Spawn actors
        queue = await learner_mesh.spawn("queue", TrainingQueue)
        learner = await learner_mesh.spawn("learner", Learner, self.config, queue)
        generator = await gen_mesh.spawn("generator", Generator, self.config, queue)

        # Training loop
        logging.info("Starting training loop...")
        for epoch in range(self.config.num_epochs):
            logging.info(f"\nEpoch {epoch + 1}/{self.config.num_epochs}")

            # Generate batches and train
            for step in range(10):  # 10 steps per epoch for demo
                # Generate batch
                await generator.generate_batch()

                # Train step
                metrics = await learner.train_step()

                if step % 5 == 0:
                    logging.info(f"  Step {metrics['step']}: loss={metrics['loss']:.4f}")

            # Epoch complete
            logging.info(f"Epoch {epoch + 1} complete")

        logging.info("\nTraining complete!")

    async def cleanup(self):
        """Clean up resources."""
        await self.backend.stop_all()


# ============================================================================
# MAIN TRAINING SCRIPT
# ============================================================================


async def main():
    """Run distributed training with Monarch-Flow integration."""

    # Training configuration
    config = TrainingConfig(
        model_size="7b",  # Change to "13b" or "70b" for larger models
        batch_size=32,
        learning_rate=1e-4,
        num_epochs=3,
    )

    # Create Monarch backend with Flow
    backend_config = MonarchFlowConfig(
        provider="mithril",
        startup_timeout=600.0,  # 10 minutes for large instances
    )
    backend = MonarchFlowBackend(config=backend_config)

    # Create orchestrator
    orchestrator = DistributedTrainingOrchestrator(config, backend)

    try:
        # Set up infrastructure
        await orchestrator.setup_infrastructure()

        # Run training
        await orchestrator.run_training()

    except Exception as e:
        logging.error(f"Training failed: {e}")
        raise

    finally:
        # Clean up
        logging.info("Cleaning up resources...")
        await orchestrator.cleanup()
        logging.info("Done!")


if __name__ == "__main__":
    # Note: Requires FLOW_API_KEY and FLOW_PROJECT environment variables
    asyncio.run(main())
