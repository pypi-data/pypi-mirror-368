#!/usr/bin/env python3
"""Data pipeline examples: S3 mounts and volumes.

Shows how to use Flow's mounts and volumes for common data workflows:
- Mount S3 buckets into the container with s3fs
- Persist data and models using volumes across runs
"""

import os
import sys

import flow
from flow import TaskConfig


def s3_mount_and_cache() -> int:
    """Mount an S3 prefix to /data and cache to a volume."""
    # Provide AWS creds in env if needed; Flow passes them through for s3fs
    env = {
        k: v
        for k, v in {
            "AWS_ACCESS_KEY_ID": os.environ.get("AWS_ACCESS_KEY_ID"),
            "AWS_SECRET_ACCESS_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY"),
            "AWS_SESSION_TOKEN": os.environ.get("AWS_SESSION_TOKEN"),
            "AWS_DEFAULT_REGION": os.environ.get("AWS_DEFAULT_REGION"),
        }.items()
        if v
    }

    script = """
set -e
echo "=== Inspect mounts ==="
df -h | sed -n '1p;/\\/data/p;/\\/volumes/p'
echo
mkdir -p /volumes/cache
if [ -d /data ]; then
  echo "Copying a small subset from /data to /volumes/cache (demo)"
  find /data -maxdepth 1 -type f | head -n 3 | xargs -I{} cp -v {} /volumes/cache/ || true
  echo "Cache contents:" && ls -la /volumes/cache || true
else
  echo "No /data mount present. Provide an s3:// URL in mounts to demo."
fi
"""

    config = TaskConfig(
        name="s3-mount-and-cache",
        unique_name=True,
        instance_type="a100",
        command=script,
        volumes=[{"name": "cache", "size_gb": 20, "mount_path": "/volumes/cache"}],
        env=env,
    )

    # Provide an S3 mount easily at submit time
    s3_url = os.environ.get("FLOW_EXAMPLE_S3")
    if not s3_url:
        print("Skipping S3 mount demo: set FLOW_EXAMPLE_S3=s3://bucket/prefix to enable")
        return 0

    task = flow.run(config, mounts={"/data": s3_url})
    task.wait()
    print(task.logs())
    return 0


def training_with_persistent_volumes() -> int:
    """Train a simple model using cached data and persist checkpoints to a volume."""
    script = """
set -e
python - << 'PY'
import torch
from pathlib import Path

cache = Path('/volumes/cache')
print('Cache present:', cache.exists(), 'files:', len(list(cache.rglob('*'))))

model = torch.nn.Linear(10, 1)
opt = torch.optim.Adam(model.parameters())
for epoch in range(3):
    x = torch.randn(32, 10)
    loss = model(x).mean()
    opt.zero_grad(); loss.backward(); opt.step()
    print(f'Epoch {epoch}: loss={loss.item():.4f}')

ckpt = Path('/volumes/models/model.pt')
ckpt.parent.mkdir(parents=True, exist_ok=True)
torch.save(model.state_dict(), ckpt)
print('Saved checkpoint to', ckpt)
PY
"""

    config = TaskConfig(
        name="training-with-volumes",
        unique_name=True,
        instance_type="a100",
        command=script,
        volumes=[
            {"name": "cache", "size_gb": 20, "mount_path": "/volumes/cache"},
            {"name": "models", "size_gb": 10, "mount_path": "/volumes/models"},
        ],
        image="pytorch/pytorch:2.2.2-cuda12.1-cudnn8-runtime",
    )

    task = flow.run(config)
    task.wait()
    print(task.logs())
    return 0


def main() -> int:
    print("\n--- Example 1: S3 mount → cache to volume ---\n")
    s3_mount_and_cache()

    print("\n--- Example 2: Train with persistent volumes ---\n")
    training_with_persistent_volumes()
    return 0


if __name__ == "__main__":
    sys.exit(main())
