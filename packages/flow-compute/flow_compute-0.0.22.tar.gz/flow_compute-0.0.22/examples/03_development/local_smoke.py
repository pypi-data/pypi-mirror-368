#!/usr/bin/env python3
"""Local provider smoke test (non-interactive).

Runs a trivial command on the LocalProvider to validate wiring.
Skips gracefully if FLOW_PROVIDER is not set to 'local'.
"""

from __future__ import annotations

import os

from flow import Flow, TaskConfig


def main() -> int:
    if os.environ.get("FLOW_PROVIDER") != "local":
        print("Skipping: set FLOW_PROVIDER=local for local smoke test")
        return 0

    config = TaskConfig(
        name="local-smoke",
        unique_name=True,
        instance_type="cpu",
        command="echo 'local ok'",
    )

    task = Flow().run(config)
    task.wait()
    logs = task.logs()
    print(logs.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
