#!/usr/bin/env python3
"""Real-world example: Developing a log analysis script with LocalProvider.

This shows how LocalProvider enables rapid iteration when developing
scripts that process logs - a common ML/data engineering task.
"""

import re
import time
from pathlib import Path

import flow
from flow import TaskConfig


def develop_log_analyzer():
    """Develop a log analysis script using fast local iteration."""

    print("Developing Log Analyzer with LocalProvider")
    print("=" * 50)

    # LocalProvider is configured via environment variable
    # export FLOW_PROVIDER=local
    print("Using LocalProvider for fast iteration...")
    print("(Make sure FLOW_PROVIDER=local is set)\n")

    # Version 1: Basic implementation
    print("\n1. First attempt - basic parsing:")
    v1_start = time.time()

    task = flow.run(
        TaskConfig(
            name="log-analyzer-v1",
            unique_name=True,
            command="""
        # Simulate reading training logs
        echo "[2024-01-01 10:00:00] Epoch 1/10 - Loss: 2.453"
        echo "[2024-01-01 10:05:00] Epoch 2/10 - Loss: 2.102"
        echo "[2024-01-01 10:10:00] Epoch 3/10 - Loss: 1.897"
        
        # Parse logs (buggy version)
        echo "Parsing logs..."
        # Oops, forgot to extract the loss values!
        echo "Done"
        """,
            instance_type="cpu.small",
        )
    )

    task.wait()
    print(f"Execution time: {time.time() - v1_start:.2f}s")
    print("Output:", task.logs().split("\n")[-2])  # Missing loss extraction!

    # Version 2: Fix the bug (fast iteration!)
    print("\n2. Fixed version - extract losses:")
    v2_start = time.time()

    task = flow.run(
        TaskConfig(
            name="log-analyzer-v2",
            unique_name=True,
            command="""
        # Simulate reading training logs
        logs="[2024-01-01 10:00:00] Epoch 1/10 - Loss: 2.453
[2024-01-01 10:05:00] Epoch 2/10 - Loss: 2.102
[2024-01-01 10:10:00] Epoch 3/10 - Loss: 1.897"
        
        echo "$logs"
        echo
        echo "Extracting losses..."
        
        # Extract losses using grep and awk
        echo "$logs" | grep -oE "Loss: [0-9.]+" | awk '{print $2}'
        """,
            instance_type="cpu.small",
        )
    )

    task.wait()
    print(f"Execution time: {time.time() - v2_start:.2f}s")
    print("Losses found:")
    for line in task.logs().splitlines():
        if re.match(r"^\d+\.\d+$", line):
            print(f"  - {line}")

    # Version 3: Add statistics
    print("\n3. Enhanced version - add statistics:")
    v3_start = time.time()

    task = flow.run(
        TaskConfig(
            name="log-analyzer-v3",
            unique_name=True,
            command="""
        # Simulate reading training logs
        logs="[2024-01-01 10:00:00] Epoch 1/10 - Loss: 2.453
[2024-01-01 10:05:00] Epoch 2/10 - Loss: 2.102
[2024-01-01 10:10:00] Epoch 3/10 - Loss: 1.897
[2024-01-01 10:15:00] Epoch 4/10 - Loss: 1.654
[2024-01-01 10:20:00] Epoch 5/10 - Loss: 1.423"
        
        echo "$logs"
        echo
        
        # Extract and analyze losses
        losses=$(echo "$logs" | grep -oE "Loss: [0-9.]+" | awk '{print $2}')
        
        echo "Loss Analysis:"
        echo "--------------"
        echo "$losses" | awk '
        BEGIN { min=999; max=0; sum=0; count=0 }
        {
            if ($1 < min) min=$1
            if ($1 > max) max=$1
            sum += $1
            count++
        }
        END {
            avg = sum/count
            print "Min Loss: " min
            print "Max Loss: " max
            print "Avg Loss: " avg
            print "Improvement: " sprintf("%.1f%%", (max-min)/max * 100)
        }'
        """,
            instance_type="cpu.small",
        )
    )

    task.wait()
    print(f"Execution time: {time.time() - v3_start:.2f}s")
    print("\nFinal output:")
    print(task.logs().split("Loss Analysis:")[-1].strip())

    # Total development time
    total_time = time.time() - v1_start
    print(f"\nTotal development time: {total_time:.1f}s")
    print("(Would have been ~10-15 minutes with cloud instances)")

    # Ready for production
    print("\n" + "=" * 50)
    print("Script is ready! To run in production:")
    print("1. Switch to MithrilProvider")
    print("2. Use same TaskConfig")
    print("3. Process real logs at scale")

    return task.config


def main():
    """Run the development workflow example."""
    # Develop locally
    final_config = develop_log_analyzer()

    print("\n\nProduction deployment would be:")
    print("-" * 30)
    print("flow = Flow()  # Uses Mithril")
    print("task = flow.run(final_config)")
    print("# Runs on real GPU/CPU instances")


if __name__ == "__main__":
    import os

    if os.environ.get("FLOW_PROVIDER") != "local":
        print("This example requires the local provider.")
        print("Please set: export FLOW_PROVIDER=local")
        exit(1)
    main()
