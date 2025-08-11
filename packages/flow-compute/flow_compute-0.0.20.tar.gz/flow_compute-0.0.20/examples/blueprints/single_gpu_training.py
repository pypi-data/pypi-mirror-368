#!/usr/bin/env python3
"""Blueprint: Single-GPU training (pinned image, TTL, cost-aware)."""

from __future__ import annotations

from flow import Flow, TaskConfig


def main() -> int:
    config = TaskConfig(
        name="bp-single-gpu",
        unique_name=True,
        instance_type="a100",
        image="pytorch/pytorch:2.2.2-cuda12.1-cudnn8-runtime",
        command="""
set -e
python - <<'PY'
import torch
print('PyTorch', torch.__version__)
print('CUDA?', torch.cuda.is_available())
PY
""",
        max_price_per_hour=20.0,
        max_run_time_hours=1.0,
        volumes=[{"name": "checkpoints", "size_gb": 20, "mount_path": "/volumes/ckpt"}],
    )

    task = Flow().run(config)
    task.wait()
    print(task.logs())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
