#!/usr/bin/env python3
"""Blueprint: Single-node multi-GPU DDP with pinned image and TTL."""

from __future__ import annotations

from flow import Flow, TaskConfig


def main() -> int:
    script = """
set -e
pip install -q torch torchvision
cat > train_distributed.py <<'PY'
import os, torch, torch.nn as nn
from torch.nn.parallel import DistributedDataParallel as DDP
import torch.distributed as dist
def main():
    local_rank=int(os.environ.get('LOCAL_RANK',0)); torch.cuda.set_device(local_rank)
    dist.init_process_group(backend='nccl')
    model=DDP(nn.Linear(1024,512).cuda(), device_ids=[local_rank])
    x=torch.randn(32,1024).cuda(); y=model(x)
    print('ok', y.shape)
if __name__=='__main__': main()
PY
torchrun --nproc_per_node=8 --standalone train_distributed.py
"""

    cfg = TaskConfig(
        name="bp-single-node-ddp",
        unique_name=True,
        instance_type="h100-80gb.sxm.8x",
        image="nvcr.io/nvidia/pytorch:23.10-py3",
        command=script,
        max_price_per_hour=120.0,
        max_run_time_hours=2.0,
        volumes=[{"name": "ckpt", "size_gb": 50, "mount_path": "/volumes/ckpt"}],
        env={"NCCL_DEBUG": "WARN"},
    )

    task = Flow().run(cfg)
    task.wait()
    print(task.logs())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
