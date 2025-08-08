"""Example workflow demonstrating LocalProvider capabilities.

This example shows how to use LocalProvider for rapid development and testing
of Flow SDK workflows without cloud infrastructure.

Prerequisites:
- Flow SDK installed with local provider support
- Docker installed (optional, for container testing)

How to run:
    python examples/local_provider_workflow.py

Note: LocalProvider is for development/testing only.
"""

import time
import flow
from flow import TaskConfig, Flow


def main():
    """Demonstrate LocalProvider workflow."""
    print("=== LocalProvider Example Workflow ===\n")

    # Create Flow with local provider
    # Note: Set FLOW_PROVIDER=local environment variable
    print("Using LocalProvider for development testing")
    print("(Set FLOW_PROVIDER=local to use local provider)\n")

    # 1. Simple task execution
    print("1. Running simple task...")
    config = TaskConfig(
        name="hello-world",
        unique_name=True,
        instance_type="cpu",  # Local provider uses simplified types
        command="echo 'Hello from LocalProvider!'",
    )

    try:
        task = flow.run(config)
        print(f"   Task ID: {task.task_id}")

        # Monitor task
        task.wait()
        print(f"   Status: {task.status}")
        print(f"   Logs: {task.logs().strip()}\n")
    except Exception as e:
        print(f"   Error: {e}")
        print("   Make sure FLOW_PROVIDER=local is set\n")
        return

    # 2. Environment variables
    print("2. Testing environment variables...")
    config = TaskConfig(
        name="env-test",
        unique_name=True,
        instance_type="cpu",
        command="echo API_KEY=$API_KEY",
        env={"API_KEY": "test-123-key"},
    )
    task = flow.run(config)
    task.wait()
    print(f"   Output: {task.logs().strip()}\n")

    # 3. Multi-node setup simulation
    print("3. Testing multi-node configuration...")
    config = TaskConfig(
        name="distributed-test",
        unique_name=True,
        instance_type="gpu",  # Local provider simulates GPU
        num_instances=4,
        command="""
echo "Node ${FLOW_NODE_RANK} of ${FLOW_NUM_NODES}"
echo "Main node: ${FLOW_MAIN_IP}"
echo "Simulating distributed setup..."
        """,
    )
    task = flow.run(config)
    task.wait()
    print(f"   Multi-node output:\n{task.logs()}")

    # 4. Docker execution (if available)
    print("4. Testing Docker execution...")
    config = TaskConfig(
        name="docker-test",
        unique_name=True,
        instance_type="cpu",
        image="python:3.11-slim",
        command="python -c \"import sys; print(f'Python {sys.version}')\"",
    )

    try:
        task = flow.run(config)
        task.wait()
        print(f"   Docker output: {task.logs().strip()}\n")
    except Exception as e:
        print(f"   Docker test skipped: {e}\n")

    # 5. Volume management
    print("5. Testing volume management...")
    config = TaskConfig(
        name="volume-test",
        unique_name=True,
        instance_type="cpu",
        command="echo 'test' > /volumes/data/test.txt && cat /volumes/data/test.txt",
        volumes=[{"name": "data", "size_gb": 1}],
    )
    task = flow.run(config)
    task.wait()
    print(f"   Volume test output: {task.logs().strip()}\n")

    # 6. Concurrent tasks
    print("6. Running concurrent tasks...")
    start_time = time.time()
    task_ids = []

    for i in range(5):
        config = TaskConfig(
            name=f"concurrent-{i}",
            unique_name=True,
            instance_type="cpu",
            command=f"sleep 0.5 && echo 'Task {i} complete'",
        )
        task = flow.run(config)
        task_ids.append(task)

    # Wait for all tasks
    for task in task_ids:
        task.wait()

    elapsed = time.time() - start_time
    print(f"   Ran 5 concurrent tasks in {elapsed:.2f}s")
    print(f"   (Sequential would take ~2.5s)\n")

    # 7. Performance benchmark
    print("7. Performance benchmark...")
    num_tasks = 10
    start_time = time.time()

    task_ids = []
    for i in range(num_tasks):
        config = TaskConfig(
            name=f"perf-{i}", unique_name=True, instance_type="cpu", command=f"echo 'Task {i}'"
        )
        task = flow.run(config)
        task_ids.append(task)

    submission_time = time.time() - start_time
    avg_submission = submission_time / num_tasks

    print(f"   Submitted {num_tasks} tasks in {submission_time:.3f}s")
    print(f"   Average submission time: {avg_submission * 1000:.1f}ms per task\n")

    print("LocalProvider workflow complete!")
    print("\nKey benefits demonstrated:")
    print("- Fast iteration (no cloud startup delay)")
    print("- Environment variable support")
    print("- Multi-node simulation")
    print("- Docker support (if available)")
    print("- Volume management")
    print("- High performance task submission")


def advanced_ml_workflow():
    """Advanced example: ML training workflow."""
    print("\n=== Advanced ML Training Workflow ===\n")

    # Simulate ML training workflow
    ml_config = TaskConfig(
        name="ml-training",
        unique_name=True,
        instance_type="gpu",  # Local provider simulates GPU
        num_instances=2,
        image="pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime",
        command="""
# Simulated ML training script
echo "Initializing distributed training..."
echo "Node ${FLOW_NODE_RANK} of ${FLOW_NUM_NODES}"
echo "Main node: ${FLOW_MAIN_IP}"

# Simulate training epochs
for epoch in 1 2 3; do
    loss=$(awk -v min=100 -v max=999 'BEGIN{srand(); print int(min+rand()*(max-min+1))}')
    acc=$(awk -v min=90 -v max=99 'BEGIN{srand(); print int(min+rand()*(max-min+1))}')
    echo "Epoch $epoch: loss=0.$loss, accuracy=$acc%"
    sleep 0.5
done

echo "Training complete!"
echo "Model saved to /volumes/models/final.pt"
        """,
        env={"BATCH_SIZE": "32", "LEARNING_RATE": "0.001", "NUM_EPOCHS": "3"},
        volumes=[{"name": "datasets", "size_gb": 50}, {"name": "models", "size_gb": 20}],
    )

    print("Starting distributed ML training...")
    task = flow.run(ml_config)

    # Stream logs
    print("\nTraining logs:")
    print("-" * 50)

    for line in task.logs(follow=True):
        print(line.rstrip())

    print("-" * 50)
    print(f"\nTraining completed with status: {task.status}")


if __name__ == "__main__":
    import os

    # Check if local provider is enabled
    if os.environ.get("FLOW_PROVIDER") != "local":
        print("This example requires the local provider.")
        print("Please set: export FLOW_PROVIDER=local")
        print("\nNote: LocalProvider is for development/testing only.")
        exit(1)

    # Run basic workflow
    try:
        main()

        # Optionally run advanced ML workflow
        print("\nRun advanced ML workflow? (y/n): ", end="")
        response = input().strip().lower()
        if response == "y":
            advanced_ml_workflow()
    except KeyboardInterrupt:
        print("\n\nWorkflow interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure the local provider is properly configured.")
