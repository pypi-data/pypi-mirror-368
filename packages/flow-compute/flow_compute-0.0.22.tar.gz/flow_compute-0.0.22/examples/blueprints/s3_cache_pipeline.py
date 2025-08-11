#!/usr/bin/env python3
"""Blueprint: S3 mount with local volume cache (pinned image)."""

from __future__ import annotations

import os

from flow import Flow, TaskConfig


def main() -> int:
    s3 = os.environ.get("FLOW_EXAMPLE_S3")
    if not s3:
        print("Set FLOW_EXAMPLE_S3=s3://bucket/prefix to run this blueprint")
        return 0

    cmd = """
set -e
df -h | sed -n '1p;/\\/data/p;/\\/volumes/p'
mkdir -p /volumes/cache
if [ -d /data ]; then
  echo 'Copying a few files from /data to /volumes/cache'
  find /data -maxdepth 1 -type f | head -n 3 | xargs -I{} cp -v {} /volumes/cache/ || true
  ls -la /volumes/cache || true
fi
"""

    cfg = TaskConfig(
        name="bp-s3-cache",
        unique_name=True,
        instance_type="a100",
        image="ubuntu:22.04",
        command=cmd,
        volumes=[{"name": "cache", "size_gb": 20, "mount_path": "/volumes/cache"}],
        max_run_time_hours=1.0,
    )

    task = Flow().run(cfg, mounts={"/data": s3})
    task.wait()
    print(task.logs())
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
