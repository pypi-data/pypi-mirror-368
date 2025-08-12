#!/usr/bin/env python3
"""Hello GPU: the minimal Flow quickstart.

Submits a simple command on a single GPU and prints the last few log lines.

Usage:
    python hello_gpu.py
"""

import flow


def main() -> int:
    task = flow.run("nvidia-smi", instance_type="a100", max_run_time_hours=0.25, wait=True)
    print(task.logs(tail=20))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
