#!/usr/bin/env python3
"""GPU instance verification.

Validates GPU functionality, system environment, and storage mounting.

Prerequisites:
    - Flow SDK configured (`flow init`)
    - Valid API credentials

Usage:
    python 01_verify_instance.py

Returns:
    0: Success
    1: Failure
"""

import sys
from datetime import datetime

from flow import Flow, TaskConfig
from flow.api.models import TaskStatus


def main():
    """Execute GPU instance verification."""
    # Verification script: comprehensive system checks
    verification_script = """#!/bin/bash
set -euo pipefail

log() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"; }

log "Starting GPU instance verification"

# System information
log "System: $(uname -r), $(nproc) CPUs, $(free -h | grep Mem | awk '{print $2}') RAM"

# GPU verification
if ! command -v nvidia-smi &> /dev/null; then
    log "ERROR: nvidia-smi not found"
    exit 1
fi

nvidia-smi --query-gpu=name,memory.total,compute_mode --format=csv
log "GPU count: $(nvidia-smi -L | wc -l)"

# CUDA test
if command -v python3 &> /dev/null; then
    python3 -c "
import torch
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB')
" 2>/dev/null || log "PyTorch not available"
fi

# Storage verification  
log "Storage:"
df -h | grep -E '(^Filesystem|/volumes)'

if [ -d "/volumes/test" ]; then
    testfile="/volumes/test/verify_$(date +%s).txt"
    echo "test" > "$testfile" && log "Volume write: OK" || log "Volume write: FAILED"
    rm -f "$testfile"
else
    log "WARNING: Volume not mounted at /volumes/test"
fi

log "Verification complete"
"""

    # Generate unique task identifier
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Task configuration
    config = TaskConfig(
        name=f"verify-gpu-{timestamp}",
        unique_name=True,
        instance_type="h100-80gb.sxm.8x",
        region="us-central1-b",
        max_price_per_hour=98.32,  # H100x8 pricing
        command=verification_script,
        volumes=[{"name": "test", "size_gb": 10, "mount_path": "/volumes/test"}],
    )

    print(f"Submitting verification task: {config.instance_type} @ ${config.max_price_per_hour}/hr")

    try:
        with Flow() as flow_client:
            # Submit task
            task = flow_client.run(config)
            print(f"Task ID: {task.task_id}")

            # Stream logs
            print("\nLogs:")
            for line in task.logs(follow=True):
                print(line, end="")

            # Wait for completion
            task.wait()

            # Check status
            if task.status == TaskStatus.COMPLETED:
                print("\n✓ Verification successful")
                return 0
            else:
                print(f"\n✗ Task failed: {task.status}")
                return 1

    except Exception as e:
        print(f"\nError: {e}")
        if "api key" in str(e).lower():
            print("Configure credentials: flow init")
        return 1


if __name__ == "__main__":
    sys.exit(main())
