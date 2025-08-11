#!/usr/bin/env python3
"""Distributed Training with Monarch-Flow Integration (Experimental).

This mirrors the previous mocked actor orchestration, kept here for clarity.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

import torch
import torch.nn as nn

from flow._internal.integrations import (
    MonarchFlowBackend,
    MonarchFlowConfig,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class Actor:  # mock
    pass


def endpoint(func):  # mock
    func.is_endpoint = True
    return func


class MockProcMesh:
    def __init__(self, flow_mesh):
        self.flow_mesh = flow_mesh
        self.actors = {}

    async def spawn(self, name: str, actor_class: type, *args, **kwargs) -> Any:
        actor = actor_class(*args, **kwargs)
        self.actors[name] = actor
        return actor


@dataclass
class TrainingConfig:
    model_size: str = "7b"
    batch_size: int = 32
    learning_rate: float = 1e-4
    num_epochs: int = 3

    def get_gpu_requirements(self) -> dict[str, Any]:
        if self.model_size == "7b":
            return {
                "learner_gpus": 1,
                "generator_gpus": 2,
                "gpu_type": "h100",
                "min_gpu_memory_gb": 40,
            }
        if self.model_size == "13b":
            return {
                "learner_gpus": 2,
                "generator_gpus": 4,
                "gpu_type": "h100",
                "min_gpu_memory_gb": 80,
            }
        if self.model_size == "70b":
            return {
                "learner_gpus": 8,
                "generator_gpus": 8,
                "gpu_type": "h100",
                "min_gpu_memory_gb": 80,
            }
        raise ValueError(f"Unknown model size: {self.model_size}")


class TrainingQueue(Actor):
    def __init__(self):
        self.queue = asyncio.Queue()

    @endpoint
    async def put(self, item: Any) -> None:
        await self.queue.put(item)

    @endpoint
    async def get(self) -> Any:
        return await self.queue.get()


class Learner(Actor):
    def __init__(self, config: TrainingConfig, queue: TrainingQueue):
        self.config = config
        self.queue = queue
        self.model = nn.Sequential(nn.Linear(512, 1024), nn.ReLU(), nn.Linear(1024, 512))
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=config.learning_rate)
        self.step_count = 0

    @endpoint
    async def train_step(self) -> dict[str, float]:
        batch = await self.queue.get()
        loss = torch.rand(1).item()
        self.step_count += 1
        return {"step": self.step_count, "loss": loss}


class Generator(Actor):
    def __init__(self, config: TrainingConfig, queue: TrainingQueue):
        self.config = config
        self.queue = queue

    @endpoint
    async def generate_batch(self) -> None:
        batch = {
            "input": torch.randn(self.config.batch_size, 512),
            "target": torch.randn(self.config.batch_size, 512),
        }
        await self.queue.put(batch)


class DistributedTrainingOrchestrator:
    def __init__(self, config: TrainingConfig, backend: MonarchFlowBackend):
        self.config = config
        self.backend = backend
        self.learner_mesh = None
        self.generator_mesh = None

    async def setup_infrastructure(self):
        reqs = self.config.get_gpu_requirements()
        self.learner_mesh = await self.backend.create_proc_mesh(
            shape=(1, reqs["learner_gpus"]),
            constraints={
                "gpu_type": reqs["gpu_type"],
                "min_gpu_memory_gb": reqs["min_gpu_memory_gb"],
            },
        )
        self.generator_mesh = await self.backend.create_proc_mesh(
            shape=(1, reqs["generator_gpus"]),
            constraints={
                "gpu_type": reqs["gpu_type"],
                "min_gpu_memory_gb": reqs["min_gpu_memory_gb"],
            },
        )

    async def run_training(self):
        learner_mesh = MockProcMesh(self.learner_mesh)
        gen_mesh = MockProcMesh(self.generator_mesh)
        queue = await learner_mesh.spawn("queue", TrainingQueue)
        learner = await learner_mesh.spawn("learner", Learner, self.config, queue)
        generator = await gen_mesh.spawn("generator", Generator, self.config, queue)
        for epoch in range(self.config.num_epochs):
            for step in range(10):
                await generator.generate_batch()
                metrics = await learner.train_step()
                if step % 5 == 0:
                    logging.info(f"epoch {epoch} step {metrics['step']} loss={metrics['loss']:.4f}")

    async def cleanup(self):
        await self.backend.stop_all()


async def main():
    cfg = TrainingConfig(model_size="7b", batch_size=32, learning_rate=1e-4, num_epochs=3)
    backend = MonarchFlowBackend(
        config=MonarchFlowConfig(provider="mithril", startup_timeout=600.0)
    )
    orch = DistributedTrainingOrchestrator(cfg, backend)
    try:
        await orch.setup_infrastructure()
        await orch.run_training()
    finally:
        await orch.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
