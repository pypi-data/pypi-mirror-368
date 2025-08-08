"""Dev command - Persistent development VM with optional isolated environments.

This module implements the dev command for the Flow CLI. It provides a
persistent VM for development with two modes:

1. Default mode: Direct VM execution (no containers) - fast and simple
2. Named environments: Container-isolated environments for different projects

Command Usage:
    flow dev [COMMAND] [OPTIONS]
    flow dev -c COMMAND [OPTIONS]  # Alternative syntax

Examples:
    # Default environment (no containers, direct VM):
    $ flow dev                      # SSH to persistent VM
    $ flow dev "pip install torch"  # Install directly on VM
    $ flow dev "python train.py"    # Run with installed packages
    $ flow dev -c "nvidia-smi"      # Alternative syntax with -c

    # Named environments (isolated containers):
    $ flow dev "pip install tensorflow" -e ml  # Isolated env
    $ flow dev "npm install express" -e web    # Another env
    $ flow dev "python model.py" -e ml         # Has TF, not express

Key design:
- Default env: Direct VM execution at /root (no container overhead)
- Named envs: Isolated containers at /envs/NAME
- Shared data: Named envs can read /root as /shared
- Auto-upload: Code syncs on each run (rsync - only changes)
"""

import hashlib
import json
import logging
import os
import shlex
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, Any, TypedDict, List

import click

from flow import Flow, TaskConfig, ValidationError
from flow.api.models import TaskStatus, Task
from flow.errors import AuthenticationError, TaskNotFoundError

from .base import BaseCommand, console
from .utils import wait_for_task

logger = logging.getLogger(__name__)


class ContainerInfo(TypedDict):
    """Docker container information from 'docker ps --format json'."""

    Names: str
    Status: str
    Image: str
    Command: str
    CreatedAt: str
    ID: str


class ContainerStatus(TypedDict):
    """Container status information for dev VM."""

    active_containers: int
    containers: List[ContainerInfo]


class DevVMManager:
    """Manages the lifecycle of development VMs."""

    def __init__(self, flow_client: Flow):
        """Initialize VM manager.

        Args:
            flow_client: Flow SDK client instance
        """
        self.flow_client = flow_client
        self.dev_vm_prefix = "flow-dev"

    def get_dev_vm_name(self, force_unique: bool = False) -> str:
        """Generate consistent dev VM name for current user.

        Args:
            force_unique: If True, append a unique suffix to ensure uniqueness

        Returns:
            Unique dev VM name based on username
        """
        from ..utils.name_generator import generate_unique_name

        user = os.environ.get("USER", "default")
        # Create a short hash to ensure uniqueness
        name_hash = hashlib.md5(f"{user}-dev".encode()).hexdigest()[:6]
        base_name = f"dev-{name_hash}"

        # Use shared utility for consistent unique name generation
        if force_unique:
            vm_name = generate_unique_name(prefix="dev", base_name=base_name, add_unique=True)
        else:
            vm_name = base_name

        logger.debug(f"Generated dev VM name: {vm_name} for user: {user}")
        return vm_name

    def find_dev_vm(self, include_not_ready=False):
        """Find existing dev VM for current user.

        Args:
            include_not_ready: If True, also return VMs without SSH access yet

        Returns:
            Task object if found, None otherwise
        """
        base_vm_name = self.get_dev_vm_name()
        # Build the expected dev VM prefix for this user
        user = os.environ.get("USER", "default")
        # The prefix matches our new naming pattern
        name_hash = hashlib.md5(f"{user}-dev".encode()).hexdigest()[:6]
        vm_prefix = f"dev-{name_hash}"

        # Also check for legacy naming pattern
        legacy_prefix = f"flow-dev-{user}"

        try:
            # List running tasks
            logger.debug(
                f"Searching for existing dev VM with prefix: {vm_prefix} or {legacy_prefix}"
            )
            tasks = self.flow_client.list_tasks(status=TaskStatus.RUNNING)

            logger.debug(f"Found {len(tasks)} running tasks")

            # Find all tasks that match our dev VM naming patterns (old and new)
            # Since we can't reliably check config.env (it's not returned by list_tasks),
            # we rely on the naming convention which is unique per user
            dev_vm_candidates = []
            not_ready_vms = []

            for task in tasks:
                # Check both new and legacy naming patterns
                if task.name.startswith(vm_prefix) or task.name.startswith(legacy_prefix):
                    logger.debug(f"Found potential dev VM: {task.name} (ID: {task.task_id})")
                    # Separate ready and not-ready VMs
                    if task.ssh_host:
                        dev_vm_candidates.append(task)
                        logger.debug(f"  - Has SSH access: {task.ssh_host}:{task.ssh_port}")
                    else:
                        not_ready_vms.append(task)
                        logger.debug(f"  - No SSH access yet")

            # If we only have not-ready VMs and include_not_ready is True, return the newest
            if include_not_ready and not dev_vm_candidates and not_ready_vms:
                not_ready_vms.sort(key=lambda t: t.created_at, reverse=True)
                logger.info(f"Found {len(not_ready_vms)} dev VM(s) still provisioning")
                return not_ready_vms[0]

            if not dev_vm_candidates:
                logger.debug("No ready dev VMs found")
                return None

            # If we have multiple dev VMs, use the most recent one
            if len(dev_vm_candidates) > 1:
                logger.info(f"Found {len(dev_vm_candidates)} ready dev VMs - selecting most recent")
                # Sort by created_at timestamp (newest first)
                dev_vm_candidates.sort(key=lambda t: t.created_at, reverse=True)

            selected_vm = dev_vm_candidates[0]
            logger.info(f"Using existing dev VM: {selected_vm.name} (ID: {selected_vm.task_id})")
            return selected_vm

        except Exception as e:
            logger.warning(f"Error searching for dev VM: {e}")
            return None

    def create_dev_vm(
        self,
        instance_type: str = None,
        ssh_keys: list = None,
        max_price_per_hour: float = None,
        no_unique: bool = False,
    ) -> Task:
        """Create a new dev VM.

        Args:
            instance_type: GPU/CPU instance type
            ssh_keys: SSH keys for access
            max_price_per_hour: Maximum hourly price in USD
            no_unique: If True, don't add unique suffix on name conflict

        Returns:
            Task object for the new VM
        """
        # First try with consistent name
        vm_name = self.get_dev_vm_name()

        # Default instance type for dev
        if not instance_type:
            instance_type = os.environ.get("FLOW_DEV_INSTANCE_TYPE", "h100")

        # Create VM configuration
        # For dev VMs, we use a startup script that prepares the environment
        # Note: Since TaskConfig doesn't support Docker socket mounts or privileged mode,
        # the dev VM runs containers directly on the host VM, not nested inside another container
        dev_startup_script = """#!/bin/bash
set -e

# Install essential dev tools
apt-get update -qq
apt-get install -y -qq git vim htop curl wget python3-pip

# Install Docker CLI to use host's Docker daemon via socket
if ! command -v docker >/dev/null 2>&1; then
    echo "Installing Docker CLI..."
    apt-get install -y -qq docker.io
    echo "Docker CLI installed successfully"
fi

# Verify Docker works (using host's daemon via socket)
docker version || echo "Docker not yet available"

# Keep VM running
exec sleep infinity
"""

        config_dict = {
            "name": vm_name,
            "unique_name": False,  # We handle uniqueness ourselves with get_dev_vm_name
            "instance_type": instance_type,
            # Use Docker image to trigger DockerSection which handles dev VM setup
            "image": os.environ.get("FLOW_DEV_IMAGE", "ubuntu:22.04"),
            "command": ["bash", "-c", dev_startup_script],
            "env": {
                "FLOW_DEV_VM": "true",
                "FLOW_DEV_USER": os.environ.get("USER", "default"),
                "DEBIAN_FRONTEND": "noninteractive",
            },
            "ssh_keys": ssh_keys or [],
            "priority": "high",  # High priority for dev VMs
        }

        # Add max_price_per_hour if specified
        if max_price_per_hour is not None:
            config_dict["max_price_per_hour"] = max_price_per_hour

        config = TaskConfig(**config_dict)

        # Submit task
        logger.info(f"Creating dev VM with instance type: {instance_type}")
        try:
            return self.flow_client.run(config)
        except Exception as e:
            # Check if it's a name conflict - providers should raise NameConflictError
            # but also handle legacy string matching for backward compatibility
            error_msg = str(e)
            if "Name already used" in error_msg or "already exists" in error_msg.lower():
                # Prefer attaching to the existing dev VM rather than creating a new uniquely named one
                logger.info("Dev VM name already in use; attempting to use the existing VM")
                existing = self.find_dev_vm(include_not_ready=True)
                if existing:
                    return existing
                # Briefly wait and retry once to account for eventual consistency
                time.sleep(2)
                existing = self.find_dev_vm(include_not_ready=True)
                if existing:
                    return existing
                if no_unique:
                    # User explicitly doesn't want a uniquely-suffixed name
                    raise
                # As a last resort, we can generate a unique suffix to avoid blocking the user
                # But this will create a second dev VM; recommend using --force-new if that's desired.
                logger.info("Existing VM not discoverable; generating unique dev VM name")
                vm_name = self.get_dev_vm_name(force_unique=True)
                config.name = vm_name
                return self.flow_client.run(config)
            else:
                # Re-raise other errors
                raise

    def stop_dev_vm(self) -> bool:
        """Stop the dev VM.

        Returns:
            True if VM was stopped, False if not found
        """
        vm = self.find_dev_vm()
        if vm:
            self.flow_client.cancel(vm.task_id)
            return True
        return False


class DevContainerExecutor:
    """Executes commands in containers on the dev VM."""

    def __init__(self, flow_client: Flow, vm_task: Task):
        """Initialize container executor.

        Args:
            flow_client: Flow SDK client
            vm_task: The dev VM task object
        """
        self.flow_client = flow_client
        self.vm_task = vm_task
        self.container_prefix = "flow-dev-exec"

    def execute_command(
        self, command: str, image: str = None, interactive: bool = False, env_name: str = "default"
    ) -> int:
        """Execute command on the dev VM.

        Default environment runs directly on VM (no containers).
        Named environments use containers for isolation.

        Args:
            command: Command to execute
            image: Docker image to use (forces container for default env)
            interactive: Whether to run interactively
            env_name: Named environment (default: "default")

        Returns:
            Exit code of the command
        """

        # Get remote operations from provider
        try:
            remote_ops = self.flow_client.get_remote_operations()
        except AttributeError:
            # Fallback for providers without remote_operations
            console.print("[red]Error: Provider doesn't support remote operations[/red]")
            return 1

        # Carmack's wisdom: Default env should be zero overhead
        # Only use containers for named environments or when image specified
        if env_name == "default" and not image:
            # Execute directly on VM - no container overhead
            logger.info(f"Executing directly on VM: {command[:50]}...")

            if interactive:
                # Interactive execution using open_shell
                try:
                    remote_ops.open_shell(self.vm_task.task_id, command=command)
                    return 0
                except Exception as e:
                    console.print(f"[red]Error: {e}[/red]")
                    return 1
            else:
                # Non-interactive - use execute_command
                try:
                    from flow import RemoteExecutionError

                    output = remote_ops.execute_command(self.vm_task.task_id, command)
                    if output:
                        console.print(output, end="")
                    return 0
                except RemoteExecutionError as e:
                    console.print(f"[red]Command failed: {e}[/red]")
                    return 1
                except Exception as e:
                    console.print(f"[red]Error: {e}[/red]")
                    return 1

        # Named environments or explicit image request - use containers
        # This code path handles isolated environments
        # Generate unique container name
        from ..utils.name_generator import generate_unique_name

        container_name = generate_unique_name(
            prefix=self.container_prefix, base_name=None, add_unique=True
        )

        # Default image
        if not image:
            image = os.environ.get("FLOW_DEV_CONTAINER_IMAGE", "ubuntu:22.04")

        # Steve Jobs: "Simplify!"
        # Short paths: /envs/NAME for isolated environments
        # Shared data just goes in /root (no need for /root/shared)
        env_dir = f"/envs/{env_name}"
        setup_env_cmd = f"mkdir -p {env_dir}"
        try:
            remote_ops.execute_command(self.vm_task.task_id, setup_env_cmd)
        except Exception:
            pass  # Directory might already exist

        # Build docker command with environment mount
        docker_args = [
            "docker",
            "run",
            "--rm",  # Remove container after execution
            "--name",
            container_name,
            "-v",
            f"{env_dir}:/workspace",  # Mount environment directory
            "-v",
            "/root:/shared:ro",  # Root is read-only shared data
            "-w",
            "/workspace",  # Working directory
            "-e",
            "HOME=/workspace",  # Set HOME to workspace
            "--pull",
            "missing",  # Pull image if not present
        ]

        # Add environment variables
        docker_args.extend(
            [
                "-e",
                "FLOW_DEV_CONTAINER=true",
                "-e",
                f"FLOW_DEV_USER={os.environ.get('USER', 'default')}",
            ]
        )

        # Add GPU support if available
        docker_args.extend(["--gpus", "all"])

        if interactive:
            docker_args.extend(["-it"])

        # Add image and command
        docker_args.append(image)
        docker_args.extend(["sh", "-c", command])

        # Build final command - no sudo needed if user is in docker group
        docker_cmd = " ".join(shlex.quote(arg) for arg in docker_args)

        # Execute via Flow's remote operations
        if interactive:
            # Interactive execution using open_shell
            try:
                remote_ops.open_shell(self.vm_task.task_id, command=docker_cmd)
                return 0
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                return 1
        else:
            # Non-interactive - use execute_command
            try:
                from flow import RemoteExecutionError

                # First, ensure image is available (pull if needed)
                logger.debug(f"Checking Docker image availability: {image}")
                try:
                    pull_output = remote_ops.execute_command(
                        self.vm_task.task_id,
                        f"docker image inspect {image} >/dev/null 2>&1 || docker pull {image}",
                    )
                    if pull_output and "Pulling from" in pull_output:
                        console.print(f"Pulling Docker image: {image}")
                        logger.info(f"Pulling Docker image: {image}")
                except RemoteExecutionError as e:
                    # Image pull might fail but container might still run with cached image
                    logger.debug(f"Image pull failed (may use cache): {e}")
                    pass

                # Execute the actual command
                logger.info(f"Executing container command: {command[:50]}...")
                output = remote_ops.execute_command(self.vm_task.task_id, docker_cmd)
                if output:
                    console.print(output, end="")
                logger.debug("Command executed successfully")
                return 0
            except RemoteExecutionError as e:
                error_msg = str(e)
                if "unable to find image" in error_msg.lower():
                    console.print(
                        f"[red]Docker image '{image}' not found and could not be pulled[/red]"
                    )
                    console.print(
                        "[yellow]Tip: Check image name or ensure internet connectivity on the dev VM[/yellow]"
                    )
                elif "docker: command not found" in error_msg.lower():
                    console.print("[red]Docker is not installed on the dev VM[/red]")
                    console.print("[yellow]Tip: SSH into the VM and install Docker first[/yellow]")
                else:
                    console.print(f"[red]Command failed: {e}[/red]")
                return 1
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                return 1

    def reset_containers(self) -> None:
        """Reset all dev containers on the VM."""
        # Get remote operations from provider
        try:
            remote_ops = self.flow_client.get_remote_operations()
        except AttributeError:
            console.print("[red]Error: Provider doesn't support remote operations[/red]")
            return

        # Commands to clean up containers
        cleanup_commands = [
            # Stop all flow-dev containers
            f"docker ps -q -f name={self.container_prefix} | xargs -r docker stop",
            # Remove stopped containers
            "docker container prune -f",
            # Clean up dangling images
            "docker image prune -f",
        ]

        for cmd in cleanup_commands:
            try:
                # Execute cleanup command using remote operations
                from flow import RemoteExecutionError

                remote_ops.execute_command(self.vm_task.task_id, cmd)
            except RemoteExecutionError as e:
                # Some commands may fail if no containers exist - that's OK
                if "requires at least 1 argument" not in str(e):
                    console.print(f"[yellow]Warning during cleanup: {e}[/yellow]")
            except Exception as e:
                console.print(f"[yellow]Warning during cleanup: {e}[/yellow]")

    def get_container_status(self) -> ContainerStatus:
        """Get status of containers on the dev VM.

        Returns:
            ContainerStatus with count and detailed container information
        """
        # Get remote operations from provider
        try:
            remote_ops = self.flow_client.get_remote_operations()
        except AttributeError:
            return {"active_containers": 0, "containers": []}

        # Get running containers
        list_cmd = f"docker ps -f name={self.container_prefix} --format json"

        try:
            from flow import RemoteExecutionError

            output = remote_ops.execute_command(self.vm_task.task_id, list_cmd)

            containers = []
            if output:
                for line in output.strip().split("\n"):
                    if line:
                        try:
                            containers.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass

            return {"active_containers": len(containers), "containers": containers}
        except RemoteExecutionError:
            return {"active_containers": 0, "containers": []}
        except Exception:
            return {"active_containers": 0, "containers": []}


class DevCommand(BaseCommand):
    """Development environment command implementation."""

    @property
    def name(self) -> str:
        return "dev"

    @property
    def help(self) -> str:
        return """Persistent dev VM (default instance: h100) - default runs directly, named envs use containers
        
Examples:
  flow dev                    # SSH to VM
  flow dev "nvidia-smi"       # Check GPUs
  flow dev "python train.py"  # Run script"""

    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        @click.argument("cmd_arg", required=False)  # Optional positional argument for command
        @click.option("--command", "-c", help="Command to execute (VM or container)")
        @click.option(
            "--env",
            "-e",
            default="default",
            help="Environment: 'default' (VM) or named (container)",
        )
        @click.option("--instance-type", "-i", help="Instance type for dev VM (e.g., a100, h100)")
        @click.option("--image", help="Docker image for container execution")
        @click.option(
            "--ssh-keys", "-k", multiple=True, help="SSH keys to use (can specify multiple)"
        )
        @click.option("--reset", "-r", is_flag=True, help="Reset all containers")
        @click.option("--stop", "-S", "-s", is_flag=True, help="Stop the dev VM")
        @click.option("--info", "status", is_flag=True, help="Show dev environment status")
        @click.option(
            "--status", "status", is_flag=True, help="Show dev environment status", hidden=True
        )
        @click.option("--force-new", is_flag=True, help="Force creation of new dev VM")
        @click.option("--max-price-per-hour", "-m", type=float, help="Maximum hourly price in USD")
        @click.option(
            "--upload/--no-upload",
            default=True,
            help="Upload current directory to VM (default: upload)",
        )
        @click.option(
            "--upload-path", default=".", help="Path to upload (default: current directory)"
        )
        @click.option(
            "--no-unique", is_flag=True, help="Don't append unique suffix to VM name on conflict"
        )
        @click.option(
            "--json", "output_json", is_flag=True, help="Output JSON (for use with --info)"
        )
        @click.option("--verbose", "-v", is_flag=True, help="Show detailed examples and workflows")
        def dev(
            cmd_arg: Optional[str],
            command: Optional[str],
            env: str,
            instance_type: Optional[str],
            image: Optional[str],
            ssh_keys: tuple,
            reset: bool,
            stop: bool,
            status: bool,
            force_new: bool,
            max_price_per_hour: Optional[float],
            upload: bool,
            upload_path: str,
            no_unique: bool,
            output_json: bool,
            verbose: bool,
        ):
            """Manage persistent development VM with optional isolated environments.

            \b
            DEFAULT MODE (no containers, fast):
                flow dev                          # SSH to VM
                flow dev "pip install numpy"      # Install on VM
                flow dev "python train.py"        # Direct execution
                flow dev "nvidia-smi"             # Check GPUs

            \b
            ISOLATED ENVIRONMENTS (containers):
                flow dev "pip install tensorflow" -e ml
                flow dev "npm install express" -e web
                flow dev "python app.py" -e ml    # Has TF, not express

            Use 'flow dev --verbose' for detailed explanation.
            """
            if verbose:
                console.print("\n[bold]Flow Dev - Architecture & Usage:[/bold]\n")

                console.print("[underline]Two Modes:[/underline]")
                console.print("1. DEFAULT: Direct VM execution (no containers)")
                console.print("   • Commands run directly on persistent VM")
                console.print("   • Packages install to /root")
                console.print("   • Zero overhead, maximum speed")
                console.print("   • Like SSH but with auto code upload\n")

                console.print("2. NAMED ENVS: Container isolation")
                console.print("   • Each env gets isolated container")
                console.print("   • Packages install to /envs/NAME")
                console.print("   • Clean separation between projects")
                console.print("   • Read-only access to /root as /shared\n")

                console.print("[underline]Examples:[/underline]")
                console.print("# Default environment (direct VM):")
                console.print("flow dev                           # SSH to VM")
                console.print("flow dev 'pip install numpy'       # Install on VM")
                console.print("flow dev 'python train.py'         # Uses numpy")
                console.print("flow dev 'nvidia-smi'              # Check GPUs\n")

                console.print("# Named environments (containers):")
                console.print("flow dev 'pip install tensorflow' -e ml")
                console.print("flow dev 'npm install express' -e web")
                console.print("flow dev 'python app.py' -e ml    # Has TF, not express\n")

                console.print("# Management:")
                console.print("flow dev --info                    # Check VM & environments")
                console.print("flow dev --stop                    # Stop VM completely\n")

                console.print("[underline]File Structure:[/underline]")
                console.print("/root/           # Default env & shared data")
                console.print("/envs/ml/        # Named env 'ml'")
                console.print("/envs/web/       # Named env 'web'\n")

                console.print("[underline]Key Points:[/underline]")
                console.print("• Code auto-uploads on each run (rsync - only changes)")
                console.print("• VM persists until you --stop")
                console.print("• Default env = your persistent workspace")
                console.print("• Named envs = isolated project spaces\n")
                return

            # Handle positional argument as command if no --command/-c was specified
            if cmd_arg and not command:
                # If it looks like a command (contains spaces or common command patterns)
                if " " in cmd_arg or cmd_arg.startswith(
                    ("python", "bash", "sh", "./", "nvidia-smi", "pip", "npm", "node")
                ):
                    command = cmd_arg

            self._execute(
                command,
                env,
                instance_type,
                image,
                ssh_keys,
                reset,
                stop,
                status,
                force_new,
                max_price_per_hour,
                upload,
                upload_path,
                no_unique,
                output_json,
            )

        return dev

    def _execute(
        self,
        command: Optional[str],
        env_name: str,
        instance_type: Optional[str],
        image: Optional[str],
        ssh_keys: tuple,
        reset: bool,
        stop: bool,
        status: bool,
        force_new: bool,
        max_price_per_hour: Optional[float],
        upload: bool,
        upload_path: str,
        no_unique: bool,
        output_json: bool,
    ) -> None:
        """Execute the dev command."""
        # Start animation immediately for all modes except stop/status
        from ..utils.animated_progress import AnimatedEllipsisProgress

        progress = None
        if not stop and not status:
            # Start animation immediately for both command and interactive modes
            initial_msg = "Starting flow dev"
            if command:
                # Show a preview of the command being run
                cmd_preview = command if len(command) <= 30 else command[:27] + "..."
                initial_msg = f"Preparing to run: {cmd_preview}"

            progress = AnimatedEllipsisProgress(
                console, initial_msg, transient=True, start_immediately=True
            )

        try:
            # Initialize Flow client and VM manager
            flow_client = Flow()
            vm_manager = DevVMManager(flow_client)

            # Handle stop command
            if stop:
                from ..utils.animated_progress import AnimatedEllipsisProgress

                with AnimatedEllipsisProgress(
                    console, "Stopping dev VM", start_immediately=True
                ) as progress:
                    if vm_manager.stop_dev_vm():
                        console.print("[green]✓[/green] Dev VM stopped successfully")
                    else:
                        console.print("[yellow]No dev VM found[/yellow]")
                return

            # Handle status command
            if status:
                if progress:
                    progress.__exit__(None, None, None)
                self._show_status(vm_manager, flow_client, output_json=output_json)
                return

            # Find or create dev VM - check for ANY existing VM first (ready or provisioning)
            vm = vm_manager.find_dev_vm(include_not_ready=True)

            if force_new and vm:
                from ..utils.animated_progress import AnimatedEllipsisProgress

                with AnimatedEllipsisProgress(
                    console, "Force stopping existing dev VM", start_immediately=True
                ) as progress:
                    vm_manager.stop_dev_vm()
                    vm = None

            # If we have a VM but it's not ready, wait for it
            if vm and not vm.ssh_host:
                # Found a VM that's still provisioning
                if progress:
                    progress.update_message(f"Found dev VM provisioning: {vm.name}")
                    progress.__exit__(None, None, None)
                    progress = None

                console.print(f"[yellow]Found dev VM still provisioning: {vm.name}[/yellow]")

                # Wait for it to be ready (similar to flow ssh)
                vm = self._wait_for_vm_ready(flow_client, vm)

            if not vm:
                # Update existing progress or create new one
                if progress:
                    progress.update_message(f"Creating new dev VM ({instance_type or 'h100'})")
                    progress.__exit__(None, None, None)
                    progress = None
                else:
                    console.print("Starting new dev VM...")

                from ..utils.animated_progress import AnimatedEllipsisProgress

                with AnimatedEllipsisProgress(
                    console,
                    f"Creating dev VM ({instance_type or 'h100'})",
                    transient=True,
                    start_immediately=True,
                ):
                    vm = vm_manager.create_dev_vm(
                        instance_type=instance_type,
                        ssh_keys=list(ssh_keys) if ssh_keys else None,
                        max_price_per_hour=max_price_per_hour,
                        no_unique=no_unique,
                    )

                # Wait for VM to be ready with better error handling
                try:
                    # wait_for_task will show "Task submitted: {task_name}" with progress bar
                    final_status = wait_for_task(
                        flow_client, vm.task_id, watch=False, task_name=vm.name
                    )

                    if final_status != "running":
                        # Get task details for error diagnosis
                        try:
                            task = flow_client.get_task(vm.task_id)
                            if hasattr(task, "message") and task.message:
                                console.print(
                                    f"[red]✗[/red] Failed to start dev VM: {task.message}"
                                )
                            else:
                                console.print(
                                    f"[red]✗[/red] Failed to start dev VM (status: {final_status})"
                                )
                        except:
                            console.print(
                                f"[red]✗[/red] Failed to start dev VM (status: {final_status})"
                            )

                        # Cleanup failed VM
                        try:
                            flow_client.cancel(vm.task_id)
                        except Exception:
                            pass
                        return
                except KeyboardInterrupt:
                    console.print("\n[yellow]Cancelled VM startup[/yellow]")
                    # Cleanup the VM being created
                    try:
                        from ..utils.animated_progress import AnimatedEllipsisProgress

                        with AnimatedEllipsisProgress(
                            console, "Cleaning up partially created VM"
                        ) as progress:
                            flow_client.cancel(vm.task_id)
                    except Exception:
                        pass
                    raise SystemExit(1)

                console.print(f"[green]✓[/green] Dev VM started: {vm.name}")

                # Wait for IP assignment and SSH readiness
                vm = self._wait_for_vm_ready(flow_client, vm)
            else:
                # Update progress message with VM info if we have a progress indicator
                if progress:
                    progress.update_message(f"Using existing dev VM: {vm.name}")
                    progress.__exit__(None, None, None)
                    progress = None
                console.print(f"Using existing dev VM: {vm.name}")

            # Handle code upload if requested
            if upload:
                upload_path_resolved = Path(upload_path).resolve()
                if not upload_path_resolved.exists():
                    console.print(f"[red]Error: Upload path does not exist: {upload_path}[/red]")
                    raise SystemExit(1)

                if not upload_path_resolved.is_dir():
                    console.print(
                        f"[red]Error: Upload path must be a directory: {upload_path}[/red]"
                    )
                    raise SystemExit(1)

                try:
                    if env_name == "default":
                        # Default env: upload directly to /root
                        provider = flow_client.provider
                        provider.upload_code_to_task(
                            task_id=vm.task_id,
                            source_dir=upload_path_resolved,
                            timeout=600,
                            console=console,
                            target_dir="~",
                        )
                        # Provider prints concise summary
                    else:
                        # Named env: create env directory and upload there
                        env_target_dir = f"/envs/{env_name}"
                        remote_ops = flow_client.get_remote_operations()

                        # Create environment directory
                        setup_cmd = f"mkdir -p {env_target_dir}"
                        remote_ops.execute_command(vm.task_id, setup_cmd)

                        # Upload to home directory first (provider default)
                        provider = flow_client.provider
                        provider.upload_code_to_task(
                            task_id=vm.task_id,
                            source_dir=upload_path_resolved,
                            timeout=1500,
                            console=console,
                            target_dir="~",
                        )

                        # Copy to environment directory with a brief spinner
                        from ..utils.animated_progress import AnimatedEllipsisProgress

                        copy_cmd = f"rsync -av \"$HOME/\" {env_target_dir}/ --exclude='/envs/'"
                        with AnimatedEllipsisProgress(
                            console,
                            f"Syncing to environment '{env_name}'",
                            transient=True,
                            start_immediately=True,
                        ):
                            remote_ops.execute_command(vm.task_id, copy_cmd)
                        console.print(f"[green]✓[/green] Code synced to environment '{env_name}'")

                except Exception as e:
                    console.print(f"[red]Error uploading code: {e}[/red]")
                    if "rsync" in str(e).lower() or "command not found" in str(e):
                        console.print("\n[yellow]Install rsync to enable code upload:[/yellow]")
                        console.print("  • macOS: [cyan]brew install rsync[/cyan]")
                        console.print("  • Ubuntu/Debian: [cyan]sudo apt-get install rsync[/cyan]")
                        console.print("  • RHEL/CentOS: [cyan]sudo yum install rsync[/cyan]")

            # Create container executor
            executor = DevContainerExecutor(flow_client, vm)

            # Handle reset command
            if reset:
                from ..utils.animated_progress import AnimatedEllipsisProgress

                with AnimatedEllipsisProgress(
                    console, "Resetting all dev containers", start_immediately=True
                ) as progress:
                    executor.reset_containers()
                console.print("[green]✓[/green] Containers reset successfully")
                return

            # Handle command execution
            if command:
                # Check if command is interactive
                interactive_commands = [
                    "bash",
                    "sh",
                    "zsh",
                    "fish",
                    "python",
                    "ipython",
                    "irb",
                    "node",
                ]
                is_interactive = command.strip() in interactive_commands

                # Update progress message with more specific info
                if progress:
                    # Keep the progress running while we prepare
                    progress.update_message("Preparing container environment")

                    # Let it show for a moment before transitioning
                    time.sleep(0.3)

                    # Stop progress before executing command
                    progress.__exit__(None, None, None)
                    progress = None  # Mark as stopped

                # Now print the message after stopping animation
                if is_interactive:
                    console.print(f"Starting interactive session: {command}")
                else:
                    console.print(f"Executing: {command}")

                exit_code = executor.execute_command(
                    command, image=image, interactive=is_interactive, env_name=env_name
                )

                if exit_code != 0 and not is_interactive:
                    raise SystemExit(exit_code)
            else:
                # No command - connect interactively to VM
                if env_name != "default":
                    console.print(f"[dim]Connecting to environment '{env_name}'[/dim]")
                else:
                    console.print(
                        "[dim]Once connected, you'll have a persistent Ubuntu environment[/dim]"
                    )

                # For named environments, create the directory
                if env_name != "default":
                    env_dir = f"/envs/{env_name}"
                    try:
                        remote_ops = flow_client.get_remote_operations()
                        setup_cmd = f"mkdir -p {env_dir}"
                        remote_ops.execute_command(vm.task_id, setup_cmd)
                        # Note: User can cd to /envs/{env_name} if they want
                    except Exception:
                        pass

                # Create a simple progress animation for the SSH connection
                # At this point, the VM is ALWAYS ready (has ssh_host) because:
                # - New VMs went through _wait_for_vm_ready()
                # - Existing VMs without SSH went through _wait_for_vm_ready()
                # - Existing VMs with SSH are already ready
                # So we never need a progress bar, just a simple connection message
                from ..utils.animated_progress import AnimatedEllipsisProgress

                progress = AnimatedEllipsisProgress(
                    console,
                    "Connecting to dev VM",
                    transient=True,
                    start_immediately=True,
                    # No progress bar needed - VM is already ready
                    show_progress_bar=False,
                )

                # Pass progress context to shell so it can be properly closed before subprocess
                # Start in environment directory for named envs
                shell_cmd = None
                if env_name != "default":
                    shell_cmd = f'bash -lc "mkdir -p /envs/{env_name} && cd /envs/{env_name} && exec bash -l"'
                flow_client.shell(vm.task_id, command=shell_cmd, progress_context=progress)

            # Show helpful next actions
            if not command or command in interactive_commands:
                if env_name == "default":
                    self.show_next_actions(
                        [
                            "Run command on VM: [cyan]flow dev 'python script.py'[/cyan]",
                            "Create isolated env: [cyan]flow dev 'pip install deps' -e project1[/cyan]",
                            "Check status: [cyan]flow dev --info[/cyan]",
                        ]
                    )
                else:
                    self.show_next_actions(
                        [
                            f"Work in {env_name}: [cyan]flow dev 'python app.py' -e {env_name}[/cyan]",
                            "Switch to default: [cyan]flow dev 'python script.py'[/cyan]",
                            "List environments: [cyan]ls /envs/[/cyan]",
                        ]
                    )

        except AuthenticationError:
            self.handle_auth_error()
        except TaskNotFoundError as e:
            self.handle_error(f"Dev VM not found: {e}")
        except ValidationError as e:
            self.handle_error(f"Invalid configuration: {e}")
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user[/yellow]")
            raise SystemExit(1)
        except Exception as e:
            # More specific error handling for common issues
            error_msg = str(e)
            if "connection refused" in error_msg.lower():
                self.handle_error(
                    "Cannot connect to Docker daemon. Ensure Docker is installed and running on the dev VM.\n"
                    "You may need to SSH into the VM and install Docker: [cyan]flow dev[/cyan]"
                )
            elif "no such image" in error_msg.lower():
                self.handle_error(
                    f"Docker image not found: {image or 'default'}\n"
                    "The image will be pulled automatically on first use."
                )
            else:
                self.handle_error(str(e))
        finally:
            # Ensure progress animation is stopped if it was started
            if progress and hasattr(progress, "_active") and progress._active:
                progress.__exit__(None, None, None)

    def _show_status(
        self, vm_manager: DevVMManager, flow_client: Flow, output_json: bool = False
    ) -> None:
        """Show dev environment status."""
        vm = vm_manager.find_dev_vm()

        if not vm:
            if output_json:
                import json as _json

                console.print(_json.dumps({"schema_version": "1.0", "dev_vm": None}))
                return
            console.print("[yellow]No dev VM running[/yellow]")
            console.print("\nStart a dev VM with: [cyan]flow dev[/cyan]")
            return

        # Get VM details
        if output_json:
            import json as _json

            payload = {
                "schema_version": "1.0",
                "dev_vm": {
                    "task_id": vm.task_id,
                    "name": vm.name,
                    "status": "running",
                    "instance_type": vm.instance_type,
                    "ssh_host": vm.ssh_host,
                    "ssh_port": getattr(vm, "ssh_port", 22),
                    "started_at": vm.started_at.isoformat() if vm.started_at else None,
                },
            }
            # Container summary
            try:
                executor = DevContainerExecutor(flow_client, vm)
                container_status = executor.get_container_status()
                payload["containers"] = container_status
            except Exception:
                payload["containers"] = {"active_containers": 0, "containers": []}
            console.print(_json.dumps(payload))
            return

        console.print(f"\n[bold]Dev VM Status[/bold]")
        console.print(f"Name: [cyan]{vm.name}[/cyan]")
        console.print(f"ID: [dim]{vm.task_id}[/dim]")
        console.print(f"Status: [green]Running[/green]")
        console.print(f"Instance: {vm.instance_type}")

        if vm.started_at:
            from datetime import datetime, timezone

            uptime = datetime.now(timezone.utc) - vm.started_at
            hours = int(uptime.total_seconds() // 3600)
            minutes = int((uptime.total_seconds() % 3600) // 60)
            console.print(f"Uptime: {hours}h {minutes}m")

        # Get container status
        try:
            executor = DevContainerExecutor(flow_client, vm)
            container_status = executor.get_container_status()

            console.print(f"\n[bold]Containers[/bold]")
            console.print(f"Active: {container_status['active_containers']}")

            if container_status["containers"]:
                console.print("\nRunning containers:")
                for container in container_status["containers"]:
                    console.print(
                        f"  - {container.get('Names', 'unknown')} ({container.get('Status', 'unknown')})"
                    )
        except Exception:
            console.print("\n[dim]Unable to fetch container status[/dim]")

    def _wait_for_vm_ready(self, flow_client: Flow, vm: Task) -> Task:
        """Wait for dev VM to have IP assignment and be ready for connections.

        Args:
            flow_client: Flow client instance
            vm: VM task object

        Returns:
            Updated VM task object with SSH info
        """
        from flow import check_task_age_for_ssh, SSHNotReadyError

        # Check if VM already has IP
        if vm.ssh_host:
            return vm

        # Check task age to provide appropriate message
        age_message = check_task_age_for_ssh(vm)

        if age_message and "unexpected" in age_message:
            # Instance has been running for a while without SSH
            console.print(f"\n[red]{age_message}[/red]")
            console.print("\nPossible issues:")
            console.print("  • Instance may have been preempted or terminated")
            console.print("  • SSH service may have crashed")
            console.print("  • Network configuration issues")
            console.print("\nRecommended actions:")
            console.print(
                f"  • Check instance health: [cyan]flow health {vm.name or vm.task_id}[/cyan]"
            )
            console.print(f"  • View logs: [cyan]flow logs {vm.name or vm.task_id}[/cyan]")
            console.print(
                f"  • Consider restarting: [cyan]flow cancel {vm.name or vm.task_id} && flow dev[/cyan]"
            )
            raise SystemExit(1)
        else:
            # Instance might still be provisioning - wait for IP assignment
            from flow.api.ssh_utils import DEFAULT_PROVISION_MINUTES

            console.print(
                f"\n[yellow]Instance is provisioning[/yellow] (waiting for IP assignment)"
            )
            console.print(
                f"This typically takes {DEFAULT_PROVISION_MINUTES} minutes for {vm.instance_type} instances."
            )
            if age_message:
                console.print(age_message)
            console.print(
                f"[dim]Ctrl+C to exit (provisioning continues) • Check: flow dev • Status: flow status {vm.name}[/dim]\n"
            )

        try:
            # Use client's public method to wait for SSH
            # Use 2x expected provision time as timeout
            from flow.api.ssh_utils import DEFAULT_PROVISION_MINUTES

            vm = flow_client.wait_for_ssh(
                task_id=vm.task_id,
                timeout=DEFAULT_PROVISION_MINUTES * 60 * 2,  # 2x expected provision time
                show_progress=True,  # This will use built-in AnimatedEllipsisProgress
            )

            if vm.ssh_host:
                console.print("[green]✓[/green] Dev VM is ready!")

        except SSHNotReadyError as e:
            if "interrupted by user" in str(e).lower():
                console.print("\n[cyan]✗ SSH wait interrupted[/cyan]")
                console.print(
                    "\nThe dev VM should still be provisioning. You can check later with:"
                )
                console.print(f"  [cyan]flow dev[/cyan]")
                console.print(f"  [cyan]flow status {vm.name or vm.task_id}[/cyan]")
            else:
                console.print("\nPossible issues:")
                console.print("  • Instance is stuck in provisioning")
                console.print("  • Cloud provider resource limits reached")
                console.print("  • Network configuration issues")
                console.print(f"\nCheck VM status: [cyan]flow status {vm.task_id}[/cyan]")
            raise SystemExit(1)

        # Give SSH a moment to fully initialize after IP assignment
        from ..utils.animated_progress import AnimatedEllipsisProgress

        with AnimatedEllipsisProgress(
            console,
            "Initializing SSH connection",
            transient=True,
            show_progress_bar=False,
            task_created_at=vm.created_at if hasattr(vm, "created_at") else None,
        ):
            pass

        return vm


# Export command instance
command = DevCommand()
