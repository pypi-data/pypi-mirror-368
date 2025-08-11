#!/usr/bin/env python3
"""Blueprint: Elastic multi-node with capability-based selection.

Requests nodes by capability (min GPU memory, CPU, RAM) and uses torch elastic.
Now leverages Flow distributed auto-rendezvous so you don't need to wire
FLOW_NODE_RANK/NUM_NODES/MAIN_IP manually.
"""

from __future__ import annotations

from flow import Flow, TaskConfig


def main() -> int:
    base_script = """
set -e
pip install -q torch torchvision
cat > train.py <<'PY'
print('Elastic training start')
PY
torchrun \
  --nproc_per_node=8 \
  --nnodes=${FLOW_NUM_NODES} \
  --node_rank=${FLOW_NODE_RANK} \
  --master_addr=${FLOW_MAIN_IP} \
  --master_port=29500 \
  train.py
"""

    # Base capability-driven selection: choose cheapest with >=40GB VRAM
    base = {
        "min_gpu_memory_gb": 40,
        "image": "nvcr.io/nvidia/pytorch:23.10-py3",
        "max_run_time_hours": 2.0,
    }

    with Flow() as client:
        # Submit a single multi-node job; Flow auto-assigns ranks via rendezvous
        config = TaskConfig(
            name="bp-elastic-auto",
            unique_name=True,
            command=base_script,
            num_instances=2,
            **base,
        )
        task = client.run(config)
        print("Distributed task:", task.task_id)
        print("Monitor logs with `flow logs <task-id> --follow`.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
