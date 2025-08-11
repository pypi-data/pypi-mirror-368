#!/usr/bin/env python3
"""Decorator pattern quickstart.

Defines a function and runs it remotely with a single GPU.
"""

from flow import FlowApp

app = FlowApp()


@app.function(gpu="a100", image="python:3.11", max_run_time_hours=0.25)
def gpu_add(x: int, y: int) -> dict:
    return {"sum": x + y}


def main() -> int:
    result = gpu_add.remote(5, 7)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
