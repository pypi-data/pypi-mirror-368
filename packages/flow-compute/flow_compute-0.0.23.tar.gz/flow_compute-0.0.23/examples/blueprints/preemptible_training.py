#!/usr/bin/env python3
"""Blueprint: Preemption/resume with checkpointing on volume."""

from __future__ import annotations

from flow import Flow, TaskConfig


def main() -> int:
    # Training writes checkpoint every N steps and resumes if prior checkpoint exists
    script = """
set -e
python - <<'PY'
import os, time, json
from pathlib import Path

ckpt_dir=Path('/volumes/ckpt')
ckpt_dir.mkdir(parents=True, exist_ok=True)
state_file=ckpt_dir/'state.json'

if state_file.exists():
    state=json.loads(state_file.read_text())
    step=state.get('step',0)
    print('Resuming from step', step)
else:
    step=0
    print('Starting fresh')

total=50
while step<total:
    time.sleep(0.2)
    step+=1
    if step % 10 == 0:
        state_file.write_text(json.dumps({'step': step}))
        print('Checkpointed step', step)
print('Done at step', step)
PY
"""

    cfg = TaskConfig(
        name="bp-preemptible",
        unique_name=True,
        instance_type="a100",
        image="python:3.11-slim",
        command=script,
        max_run_time_hours=0.5,
        volumes=[{"name": "ckpt", "size_gb": 10, "mount_path": "/volumes/ckpt"}],
        # Suggest low priority; actual priority mapping is provider-specific
        priority="low",
    )

    task = Flow().run(cfg)
    task.wait()
    print(task.logs())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
