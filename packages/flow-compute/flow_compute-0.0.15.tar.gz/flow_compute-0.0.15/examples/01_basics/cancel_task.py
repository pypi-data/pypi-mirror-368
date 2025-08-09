"""Task cancellation example for Flow SDK.

This example demonstrates how to cancel running tasks gracefully.
Flow implements a two-stage cancellation: SIGTERM followed by SIGKILL.
"""

import sys
import time
from flow import Flow, TaskConfig


def main():
    """Demonstrate task cancellation."""
    # Initialize Flow client
    with Flow() as flow:
        # Start a long-running task
        print("Starting long-running task...")
        config = TaskConfig(
            name="cancellation-demo",
            unique_name=True,
            instance_type="h100-80gb.sxm.8x",
            region="us-central1-b",
            command=[
                "python",
                "-c",
                "import time; print('Task started'); time.sleep(300); print('Task completed')",
            ],
        )

        task = flow.run(config)
        print(f"Task started with ID: {task.task_id}")
        print(f"Status: {task.status}")

        # Wait a bit to ensure task is running
        time.sleep(5)

        # Cancel the task
        print("\nCancelling task...")
        task.cancel()  # or flow.cancel(task.task_id)

        print("Task cancellation requested")
        print(f"Final status: {task.status}")

        # Alternative: Cancel by task ID
        # flow.cancel(task_id)


def cancel_specific_task(task_id: str):
    """Cancel a specific task by ID."""
    with Flow() as flow:
        try:
            flow.cancel(task_id)
            print(f"Successfully cancelled task: {task_id}")
        except Exception as e:
            print(f"Failed to cancel task: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Cancel specific task ID from command line
        cancel_specific_task(sys.argv[1])
    else:
        # Run the demo
        main()
