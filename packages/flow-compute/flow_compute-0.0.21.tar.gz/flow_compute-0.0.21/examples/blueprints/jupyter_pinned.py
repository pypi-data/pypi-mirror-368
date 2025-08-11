#!/usr/bin/env python3
"""Blueprint: Jupyter pinned image with TTL (GPU)."""

from __future__ import annotations

from flow import Flow, TaskConfig


def main() -> int:
    cfg = TaskConfig(
        name="bp-jupyter",
        unique_name=True,
        instance_type="a100",
        image="pytorch/pytorch:2.2.2-cuda12.1-cudnn8-runtime",
        command="""
python -m pip install -q jupyter notebook ipykernel
mkdir -p /volumes/notebooks
exec jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.notebook_dir=/volumes/notebooks
""",
        volumes=[{"name": "notebooks", "size_gb": 20, "mount_path": "/volumes/notebooks"}],
        max_run_time_hours=4.0,
    )
    task = Flow().run(cfg)
    print("Task:", task.task_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
