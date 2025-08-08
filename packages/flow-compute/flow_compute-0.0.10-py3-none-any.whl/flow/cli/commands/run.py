"""Run command - Submit GPU compute tasks from YAML configuration files.

This module implements the run command for the Flow CLI. It parses task
configuration files, validates requirements, and submits tasks to the
configured compute provider for execution.

Examples:
    # Submit a simple training job
    $ flow run training.yaml

    # Quick GPU test without a config file
    $ flow run "nvidia-smi"
    $ flow run "nvidia-smi" -i h100

    # Run Python scripts directly
    $ flow run "python train.py"
    $ flow run "python train.py --epochs 100" -i 8xh100

    # Mount data and run with custom image
    $ flow run task.yaml --mount s3://datasets/imagenet --image pytorch/pytorch:2.0-cuda12

Command Usage:
    flow run CONFIG_FILE [OPTIONS]
    flow run COMMAND [OPTIONS]
    flow run -i INSTANCE_TYPE COMMAND [OPTIONS]
    flow run -c COMMAND [OPTIONS]  # Alternative syntax

Storage mount formats:
- S3: s3://bucket/path → auto-mounts to /data
- Volume: volume://vol-id → auto-mounts to /mnt
- Custom: /local/path=/container/path or remote=/container/path

The command will:
- Parse and validate the YAML configuration
- Check GPU availability and requirements
- Handle storage volume mounting
- Submit the task to the provider
- Display task ID and status
- Optionally wait for task to start or watch progress

Configuration file format:
    name: my-task
    instance_type: h100x8
    command: python train.py
    max_price_per_hour: 98.32
    volumes:
      - size_gb: 100
        mount_path: /data

Note:
    Use --dry-run to validate configurations before submission.
    The --watch flag provides real-time task status updates.
"""

import json
import os

import click
import yaml

from flow import Flow, TaskConfig, ValidationError
from flow.errors import AuthenticationError

from ..provider_resolver import ProviderResolver
from .base import BaseCommand, console
from .utils import display_config, wait_for_task


class RunCommand(BaseCommand):
    """Submit a task from YAML configuration."""

    @property
    def name(self) -> str:
        return "run"

    @property
    def help(self) -> str:
        return """Submit a task from YAML configuration

Examples:
  flow run                         # Interactive GPU instance (default: 8xh100)
  flow run "nvidia-smi" -i h100    # Quick GPU test with specific instance
  flow run "python train.py"       # Run command directly
  flow run training.yaml           # Submit from config file
  flow run task.yaml --watch       # Watch progress interactively

Note: No runtime limit is applied by default. To auto-terminate, set max_run_time_hours in your TaskConfig (YAML or SDK)."""

    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        @click.argument("config_file", required=False)
        @click.option("--instance-type", "-i", help="GPU instance type (e.g., a100, 8xa100, h100)")
        @click.option(
            "--ssh-keys", "-k", multiple=True, help="SSH keys to use (can specify multiple)"
        )
        @click.option(
            "--image",
            default="nvidia/cuda:12.1.0-runtime-ubuntu22.04",
            help="Docker image to use (default: nvidia/cuda:12.1.0-runtime-ubuntu22.04)",
        )
        @click.option("--name", "-n", help="Task name (default: auto-generated)")
        @click.option("--no-unique", is_flag=True, help="Don't append unique suffix to task name")
        @click.option("--command", "-c", help="Command to run (alternative to config file)")
        @click.option(
            "--priority",
            "-p",
            type=click.Choice(["low", "med", "high"], case_sensitive=False),
            help="Task priority (low/med/high) - affects limit price and resource allocation",
        )
        @click.option(
            "--wait/--no-wait", default=True, help="Wait for task to start running (default: wait)"
        )
        @click.option(
            "--dry-run", "-d", is_flag=True, help="Validate configuration without submitting"
        )
        @click.option("--watch", "-w", is_flag=True, help="Watch task progress interactively")
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        @click.option(
            "--slurm",
            is_flag=True,
            help="Treat input as a SLURM script (auto-detected for .slurm/.sbatch)",
        )
        @click.option(
            "--mount",
            multiple=True,
            help="Mount storage (format: source or target=source). Auto-mounts: s3://→/data, volume://→/mnt",
        )
        @click.option(
            "--upload-strategy",
            type=click.Choice(["auto", "embedded", "scp", "none"]),
            default="auto",
            help="Code upload strategy: auto (default), embedded, scp, or none",
        )
        @click.option(
            "--upload-timeout",
            type=int,
            default=600,
            help="Upload timeout in seconds for SCP uploads (default: 600)",
        )
        @click.option("--max-price-per-hour", "-m", type=float, help="Maximum hourly price in USD")
        @click.option(
            "--num-instances", "-N", type=int, default=1, help="Number of instances (default: 1)"
        )
        @click.option(
            "--verbose",
            "-v",
            is_flag=True,
            help="Show detailed configuration options and workflows",
        )
        def run(
            config_file: str,
            instance_type: str,
            ssh_keys: tuple[str, ...],
            image: str,
            name: str,
            no_unique: bool,
            command: str,
            priority: str | None,
            wait: bool,
            dry_run: bool,
            watch: bool,
            output_json: bool,
            mount: tuple[str, ...],
            upload_strategy: str,
            upload_timeout: int,
            max_price_per_hour: float,
            num_instances: int,
            verbose: bool,
            slurm: bool,
        ):
            """Submit a task from YAML configuration or run interactively.

            CONFIG_FILE: Path to YAML configuration file (optional)

            \b
            Examples:
                # Run commands directly (no config file needed)
                flow run "python train.py"                    # Simple command
                flow run "nvidia-smi"                         # GPU check
                flow run "nvidia-smi" -i h100                 # Specific GPU type
                flow run "python train.py --epochs 100" -i 8xh100  # Multi-GPU training
                flow run "bash -c 'echo Hello && date'"       # Shell command

                # Alternative syntax with -c flag
                flow run -c "nvidia-smi" -i h100              # Using -c flag
                flow run -i 8xa100 -c "python benchmark.py"   # -c with instance type

                # Interactive instance (no command)
                flow run                         # Default 8xh100 instance
                flow run --instance-type h100    # Specific instance type
                flow run -i h100 --ssh-keys my-key  # With specific SSH key

                # From config file
                flow run job.yaml              # Submit and wait
                flow run job.yaml --no-wait    # Submit and exit
                flow run job.yaml --watch      # Watch progress
                flow run job.yaml --json       # JSON output
                flow run job.yaml --mount s3://bucket/dataset  # Mount S3 bucket

                # Code upload strategies
                flow run job.yaml --upload-strategy scp    # Force SCP upload
                flow run job.yaml --upload-strategy none   # No code upload
                flow run large-project.yaml --upload-timeout 1200  # 20min timeout

            Use 'flow run --verbose' for detailed configuration guide and workflows.
            """
            if verbose and not config_file and not command:
                console.print("\n[bold]Flow Run Configuration Guide:[/bold]\n")
                console.print("Quick start patterns:")
                console.print("  flow run                          # Interactive 8xH100 instance")
                console.print("  flow run 'nvidia-smi'             # Quick GPU test")
                console.print("  flow run 'python train.py' -i h100  # Run script on specific GPU")
                console.print("  flow run training.yaml            # From configuration file\n")

                console.print("Configuration file format:")
                console.print("  name: my-training-job")
                console.print("  instance_type: 8xh100")
                console.print("  image: nvidia/cuda:12.1.0-runtime-ubuntu22.04")
                console.print("  command: python train.py --epochs 100")
                console.print("  volumes:")
                console.print("    - size_gb: 100")
                console.print("      mount_path: /data")
                console.print("  environment:")
                console.print("    CUDA_VISIBLE_DEVICES: '0,1,2,3'\n")

                console.print("Instance types:")
                console.print("  • h100, 8xh100 - Latest NVIDIA H100 GPUs")
                console.print("  • a100, 8xa100 - NVIDIA A100 GPUs")
                console.print("  • a10g, 4xa10g - Budget-friendly options")
                console.print("  • Custom: 2xh100, 16xa100, etc.\n")

                console.print("Priority levels:")
                console.print("  • high - Premium pricing, lowest preemption risk")
                console.print("  • med  - Balanced price/stability (default)")
                console.print("  • low  - Best pricing, higher preemption risk\n")

                console.print("Storage mounting:")
                console.print("  --mount s3://bucket/path          # Auto-mount to /data")
                console.print("  --mount volume://vol-123          # Mount volume to /mnt")
                console.print("  --mount /local=/remote            # Custom mount paths\n")

                console.print("Code upload strategies:")
                console.print("  • auto     - Smart detection (default)")
                console.print("  • embedded - Include in task (<10MB)")
                console.print("  • scp      - Direct transfer (>10MB)")
                console.print("  • none     - No code upload\n")

                console.print("Common workflows:")
                console.print("  # Development iteration")
                console.print("  flow run 'bash' -i h100          # Start interactive")
                console.print("  flow upload-code                  # Update code")
                console.print("  ")
                console.print("  # Production training")
                console.print("  flow run train.yaml --watch       # Monitor progress")
                console.print("  flow logs <task> -f               # Stream logs")
                console.print("  ")
                console.print("  # Multi-node training")
                console.print("  flow run distributed.yaml -N 4    # 4 instances\n")

                console.print("Next steps after submission:")
                console.print("  • Monitor: flow status <task-name>")
                console.print("  • Connect: flow ssh <task-name>")
                console.print("  • View logs: flow logs <task-name>")
                console.print("  • Cancel: flow cancel <task-name>\n")
                return
            self._execute(
                config_file,
                instance_type,
                ssh_keys,
                image,
                name,
                no_unique,
                priority,
                wait,
                dry_run,
                watch,
                output_json,
                mount,
                upload_strategy,
                upload_timeout,
                command,
                max_price_per_hour,
                num_instances,
                slurm,
            )

        return run

    def _execute(
        self,
        config_file: str,
        instance_type: str,
        ssh_keys: tuple[str, ...],
        image: str,
        name: str,
        no_unique: bool,
        priority: str | None,
        wait: bool,
        dry_run: bool,
        watch: bool,
        output_json: bool,
        mount: tuple[str, ...],
        upload_strategy: str,
        upload_timeout: int,
        command: str = None,
        max_price_per_hour: float = None,
        num_instances: int = 1,
        slurm: bool = False,
    ) -> None:
        """Execute the run command."""
        # Start animation immediately for instant feedback (unless in JSON mode)
        progress = None
        if not output_json:
            from ..utils.animated_progress import AnimatedEllipsisProgress

            progress = AnimatedEllipsisProgress(
                console, "Preparing task", start_immediately=True, transient=True
            )

        try:
            # Check if config_file looks like a command instead of a file path
            # This allows "flow run 'python train.py'" to work without -c flag
            if config_file and not command and not os.path.exists(config_file):
                # If it doesn't exist as a file and looks like it could be a command
                # (contains spaces or common command patterns), treat it as a command
                if " " in config_file or config_file.startswith(
                    ("python", "bash", "sh", "./", "nvidia-smi")
                ):
                    command = config_file
                    config_file = None

            # Validate mutually exclusive options
            if config_file and command:
                self.handle_error("Cannot specify both a config file and a command")
                return

            # Remove this check - we'll use default instance type if not specified

            # Initialize Flow client early to determine provider
            flow_client = Flow()
            # Get provider name for mount resolution
            provider_name = "mithril"  # Currently only Mithril is supported

            # Load config from file or create interactive config
            if config_file:
                # Detect SLURM scripts by flag, extension, or content signature
                is_slurm = False
                if slurm:
                    is_slurm = True
                else:
                    lower = config_file.lower()
                    if lower.endswith((".slurm", ".sbatch")):
                        is_slurm = True
                    elif os.path.exists(config_file):
                        try:
                            with open(config_file, "r") as f:
                                head = f.read(4096)
                                if "#SBATCH" in head:
                                    is_slurm = True
                        except Exception:
                            pass

                if is_slurm:
                    # Route through the SLURM adapter to produce a TaskConfig
                    from flow._internal.frontends.slurm.adapter import SlurmFrontendAdapter
                    import asyncio

                    adapter = SlurmFrontendAdapter()
                    slurm_overrides = {}
                    if instance_type:
                        # Map Flow instance_type to a SLURM-like GPU hint: 4xa100 -> a100:4
                        it = instance_type.strip().lower()
                        if "x" in it:
                            try:
                                count, gpu = it.split("x", 1)
                                # If count is like '8h100' (unlikely), fall back gracefully
                                _ = int(count)
                                slurm_overrides["gpus"] = f"{gpu}:{count}"
                            except Exception:
                                slurm_overrides["gpus"] = it
                        else:
                            slurm_overrides["gpus"] = it

                    if num_instances and num_instances != 1:
                        slurm_overrides["nodes"] = num_instances

                    config = asyncio.run(
                        adapter.parse_and_convert(config_file, **slurm_overrides)
                    )
                else:
                    config = TaskConfig.from_yaml(config_file)

                # Apply CLI overrides
                updates = {}
                if upload_strategy != "auto":
                    updates["upload_strategy"] = upload_strategy
                    updates["upload_timeout"] = upload_timeout
                elif upload_timeout != 600:
                    updates["upload_timeout"] = upload_timeout

                # Apply priority if specified via CLI (overrides config file)
                if priority is not None:
                    updates["priority"] = priority.lower()

                # Apply max_price_per_hour if specified via CLI (overrides config file)
                if max_price_per_hour is not None:
                    updates["max_price_per_hour"] = max_price_per_hour

                # Apply num_instances if specified via CLI (overrides config file)
                if num_instances != 1:
                    updates["num_instances"] = num_instances

                if updates:
                    config = config.model_copy(update=updates)
            else:
                # Create interactive instance config
                if not instance_type:
                    # Use default instance type
                    instance_type = os.environ.get("FLOW_DEFAULT_INSTANCE_TYPE", "8xh100")

                # Basic validation of instance type format
                if not instance_type.strip():
                    self.handle_error("Instance type cannot be empty")
                    return

                config_dict = self._create_interactive_config(
                    instance_type,
                    ssh_keys,
                    image,
                    name,
                    no_unique,
                    command,
                    priority,
                    max_price_per_hour,
                    num_instances,
                )
                config = TaskConfig(**config_dict)

            # Apply upload strategy and timeout if specified
            if upload_strategy != "auto":
                config = config.model_copy(
                    update={"upload_strategy": upload_strategy, "upload_timeout": upload_timeout}
                )
            elif upload_timeout != 600:
                # Only update timeout if non-default
                config = config.model_copy(update={"upload_timeout": upload_timeout})

            # Parse --mount flags using provider resolver
            mount_dict = None
            if mount:
                mount_dict = {}
                for mount_spec in mount:
                    if "=" in mount_spec:
                        # Format: target=source
                        target, source = mount_spec.split("=", 1)
                        mount_dict[target] = source
                    else:
                        # Format: source (use provider rules to resolve)
                        source = mount_spec
                        target = ProviderResolver.resolve_mount_path(provider_name, source)
                        mount_dict[target] = source

            if not output_json:
                display_config(config.model_dump())
                if mount_dict:
                    console.print("\n[bold]Mounts:[/bold]")
                    for target, source in mount_dict.items():
                        console.print(f"  {target} → {source}")

            if dry_run:
                if output_json:
                    result = {"status": "valid", "config": config.model_dump()}
                    if mount_dict:
                        result["mounts"] = mount_dict
                    console.print(json.dumps(result))
                else:
                    # Stop progress before printing
                    progress.__exit__(None, None, None)
                    console.print("\n[green]✓[/green] Configuration is valid")
                return

            # Submit task with animated progress
            if not output_json:
                # Update the existing progress message
                progress.update_message("Submitting task")
                with progress:
                    task = flow_client.run(config, mounts=mount_dict)
            else:
                task = flow_client.run(config, mounts=mount_dict)

            if output_json:
                result = {"task_id": task.task_id, "status": "submitted"}
                if wait:
                    status = wait_for_task(
                        flow_client,
                        task.task_id,
                        watch=False,
                        json_output=True,
                        task_name=task.name,
                    )
                    result["status"] = status
                    # Get full task details for JSON output
                    task_details = flow_client.get_task(task.task_id)
                    result["details"] = (
                        task_details.model_dump()
                        if hasattr(task_details, "model_dump")
                        else task_details.__dict__
                    )
                console.print(json.dumps(result))
                return

            if not wait:
                task_ref = task.name or task.task_id
                if task.name:
                    console.print(f"\nTask submitted: [cyan]{task.name}[/cyan]")
                else:
                    console.print(f"\nTask submitted with ID: [cyan]{task.task_id}[/cyan]")
                self.show_next_actions(
                    [
                        f"Check task status: [cyan]flow status {task_ref}[/cyan]",
                        f"Stream logs: [cyan]flow logs {task_ref} --follow[/cyan]",
                        f"Cancel if needed: [cyan]flow cancel {task_ref}[/cyan]",
                    ]
                )
                return

            # Wait for task to start
            status = wait_for_task(
                flow_client, task.task_id, watch=watch, json_output=False, task_name=task.name
            )

            if status == "running":
                console.print("\n[green]✓[/green] Task launched successfully!")
                if task.name:
                    console.print(f"Task name: [cyan]{task.name}[/cyan]")
                    console.print(f"Task ID: [dim]{task.task_id}[/dim]")
                else:
                    console.print(f"Task ID: [cyan]{task.task_id}[/cyan]")

                recommendations = [
                    f"SSH into instance: [cyan]flow ssh {task.name or task.task_id}[/cyan]",
                    f"Stream logs: [cyan]flow logs {task.name or task.task_id} --follow[/cyan]",
                    f"Check status: [cyan]flow status {task.name or task.task_id}[/cyan]",
                ]
                self.show_next_actions(recommendations)
            elif status == "failed":
                console.print("\n[red]✗[/red] Task failed to start")
                self.show_next_actions(
                    [
                        f"View error logs: [cyan]flow logs {task.name or task.task_id}[/cyan]",
                        f"Check task details: [cyan]flow status {task.name or task.task_id}[/cyan]",
                        "Retry with different parameters: [cyan]flow run <config.yaml>[/cyan]",
                    ]
                )
            elif status == "cancelled":
                console.print("\n[yellow]![/yellow] Task was cancelled")
                self.show_next_actions(
                    [
                        "Submit a new task: [cyan]flow run <config.yaml>[/cyan]",
                        "View task history: [cyan]flow status --all[/cyan]",
                    ]
                )

        except AuthenticationError:
            self.handle_auth_error()
        except ValidationError as e:
            self.handle_error(f"Invalid configuration: {e}")
        except FileNotFoundError:
            self.handle_error(f"Configuration file not found: {config_file}")
        except yaml.YAMLError as e:
            self.handle_error(f"Invalid YAML: {e}")
        except Exception as e:
            self.handle_error(str(e))
        finally:
            # Ensure progress animation is stopped if it was started
            if progress and progress._active:
                progress.__exit__(None, None, None)

    def _create_interactive_config(
        self,
        instance_type: str,
        ssh_keys: tuple[str, ...],
        image: str,
        name: str,
        no_unique: bool,
        command: str = None,
        priority: str | None = None,
        max_price_per_hour: float | None = None,
        num_instances: int = 1,
    ) -> dict:
        """Create a minimal config for interactive instances."""
        from ..utils.name_generator import generate_unique_name

        # Generate name if not provided
        if not name:
            # Auto-generate name with prefix
            prefix = "run" if command else "interactive"
            name = generate_unique_name(
                prefix=prefix,
                base_name=None,
                add_unique=not no_unique,  # Add unique suffix unless --no-unique
            )
        # If name is provided, use it as-is (user knows what they want)

        # Build config dictionary
        config = {
            "name": name,
            "unique_name": False,  # We handle uniqueness ourselves with --no-unique
            "instance_type": instance_type,
            "image": image,
            "env": {
                "DEBIAN_FRONTEND": "noninteractive",
                "FLOW_INTERACTIVE": "true" if not command else "false",
            },
        }

        # Set command based on user input
        if command:
            # User provided a command - use it
            config["command"] = command
        else:
            # No command - keep container running for SSH
            config["command"] = ["sleep", "infinity"]

        # Add SSH keys if specified
        if ssh_keys:
            config["ssh_keys"] = list(ssh_keys)

        # Add priority if specified
        if priority is not None:
            config["priority"] = priority.lower()

        # Add max_price_per_hour if specified
        if max_price_per_hour is not None:
            config["max_price_per_hour"] = max_price_per_hour

        # Add num_instances if specified and not default
        if num_instances != 1:
            config["num_instances"] = num_instances

        return config


# Export command instance
command = RunCommand()
