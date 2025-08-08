"""Advanced usage of Flow SDK dev environment with error handling and context managers."""

from flow import Flow
from flow.errors import DevVMNotFoundError, DevContainerError


def main():
    # Initialize Flow client
    flow = Flow()

    # Example 1: Robust error handling
    print("Example 1: Robust error handling")
    try:
        # Try to execute without starting VM first
        flow.dev.exec("echo 'This will fail'")
    except DevVMNotFoundError as e:
        print(f"Expected error: {e}")
        print("Starting VM now...")
        flow.dev.start()

    # Example 2: Retry on transient failures
    print("\nExample 2: Automatic retry for transient failures")
    # This will retry up to 3 times on network errors
    exit_code = flow.dev.exec("curl -s https://api.github.com/zen", retries=3)
    print(f"Command completed with exit code: {exit_code}")

    # Example 3: Context manager with auto-cleanup
    print("\nExample 3: Context manager with auto-stop")
    # VM will be automatically stopped when exiting the context
    with flow.dev_context(auto_stop=True) as dev:
        print("VM started in context")
        dev.exec("echo 'Running in context'")
        dev.exec("python --version", image="python:3.11")
        # VM will stop automatically after this block

    print("VM has been stopped automatically")

    # Example 4: Context manager keeping VM running
    print("\nExample 4: Context manager without auto-stop")
    with flow.dev_context(auto_stop=False) as dev:
        dev.ensure_started()  # Start or reuse existing
        dev.exec("echo 'VM will keep running'")
    # VM continues running after context exit

    status = flow.dev.status()
    print(f"VM still running: {status['vm'] is not None}")

    # Example 5: Handling specific container errors
    print("\nExample 5: Handling specific container errors")
    try:
        # Try to use a non-existent image
        flow.dev.exec("echo test", image="nonexistent/image:latest")
    except DevContainerError as e:
        print(f"Container error: {e}")
        # Error includes helpful suggestions
        if hasattr(e, "suggestions"):
            print("Suggestions:")
            for suggestion in e.suggestions:
                print(f"  - {suggestion}")

    # Example 6: Using the clean remote operations API
    print("\nExample 6: Direct remote operations")
    vm = flow.dev.ensure_started()

    # Get remote operations interface
    remote_ops = flow.get_remote_operations()

    # Execute command directly on VM (not in container)
    output = remote_ops.execute_command(vm.task_id, "df -h | grep /dev/root")
    print(f"VM disk usage: {output.strip()}")

    # Example 7: Development workflow with error recovery
    print("\nExample 7: Complete development workflow")

    def run_tests_with_recovery():
        """Run tests with automatic recovery on failures."""
        try:
            # Ensure VM is running
            flow.dev.ensure_started(instance_type="h100")

            # Reset containers for clean state
            flow.dev.reset()

            # Run test suite with retries
            result = flow.dev.exec("pytest tests/ -v", image="python:3.11", retries=2)

            if result != 0:
                # Tests failed - get more info
                flow.dev.exec("pytest tests/ --lf -v")  # Run last failed

            return result

        except DevVMStartupError as e:
            print(f"Failed to start VM: {e}")
            # Try with a different instance type
            flow.dev.start(instance_type="h100")
            return run_tests_with_recovery()

        except DevContainerError as e:
            print(f"Container error: {e}")
            # Connect to debug directly
            print("Opening SSH session for debugging...")
            flow.dev.connect()

    # Clean up at the end
    print("\nCleaning up...")
    flow.dev.stop()
    print("Dev VM stopped")


if __name__ == "__main__":
    main()
