"""Example usage of Flow SDK dev environment functionality."""

from flow import Flow


def main():
    # Initialize Flow client
    flow = Flow()

    # Example 1: Basic dev VM usage
    print("Example 1: Basic dev VM usage")
    # Start or connect to existing dev VM
    vm = flow.dev.ensure_started()
    print(f"Dev VM ready: {vm.name}")

    # Execute a command in a container
    exit_code = flow.dev.exec("echo 'Hello from container!'")
    print(f"Command exit code: {exit_code}")

    # Example 2: Using specific Docker images
    print("\nExample 2: Using specific Docker images")
    # Run Python code with specific version
    flow.dev.exec("python --version", image="python:3.11")

    # Run Node.js commands
    flow.dev.exec("node --version", image="node:18")

    # Example 3: Interactive SSH connection
    print("\nExample 3: Interactive SSH connection")
    print("To connect interactively to the dev VM:")
    print("  flow.dev.connect()")
    print("Or run a specific command:")
    print("  flow.dev.connect('tmux attach')")

    # Example 4: Status and management
    print("\nExample 4: Status and management")
    status = flow.dev.status()
    print(f"VM: {status['vm']['name'] if status['vm'] else 'Not running'}")
    print(f"Active containers: {status['active_containers']}")

    # Example 5: Run method (convenience)
    print("\nExample 5: Using the run() convenience method")
    # Execute command (returns exit code)
    exit_code = flow.dev.run("python -c 'print(\"Hello Python!\")'")

    # Connect interactively (would open SSH)
    # flow.dev.run()  # Same as flow.dev.connect()

    # Example 6: Cleanup
    print("\nExample 6: Cleanup")
    # Reset all containers (VM stays running)
    flow.dev.reset()
    print("Containers reset")

    # Stop the dev VM completely
    # stopped = flow.dev.stop()
    # print(f"VM stopped: {stopped}")


if __name__ == "__main__":
    main()
