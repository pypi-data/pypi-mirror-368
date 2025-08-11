"""Run command - submit GPU tasks from YAML or direct command.

Parses configuration, validates requirements, and submits tasks to the
configured provider.

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
- Volume: volume://vol-id → auto-mounts to /volumes
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

from __future__ import annotations

import json
import os

import click
import yaml

from flow.api.client import Flow
from flow.api.models import TaskConfig
from flow.cli.commands.base import BaseCommand, console
from flow.cli.commands.messages import print_next_actions
from flow.cli.commands.utils import display_config, wait_for_task
from flow.cli.provider_resolver import ProviderResolver
from flow.cli.utils.step_progress import (
    AllocationProgressAdapter,
    SSHWaitProgressAdapter,
    StepTimeline,
    UploadProgressReporter,
)
from flow.errors import AuthenticationError, ValidationError


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
  flow run "python -m http.server 8080" --port 8080  # Expose a service on port 8080

 Notes:
 - Command may be provided positionally (recommended) or via -c/--command.
 - Use --port (repeatable) to expose high ports (>=1024) on the instance's public IP.
 - No runtime limit is applied by default. To auto-terminate, set max_run_time_hours in your TaskConfig (YAML or SDK)."""

    def get_command(self) -> click.Command:
        from flow.cli.utils.mode import demo_aware_command

        @click.command(name=self.name, help=self.help)
        @click.argument("config_file", required=False)
        @click.argument("extra_args", nargs=-1)
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
            "--on-name-conflict",
            type=click.Choice(["error", "suffix"], case_sensitive=False),
            default=None,
            help="When provided name already exists: error (default) or suffix to auto-append",
        )
        @click.option(
            "--force-new",
            is_flag=True,
            help="Alias for --on-name-conflict=suffix",
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
            "--allocation",
            type=click.Choice(["spot", "reserved", "auto"], case_sensitive=False),
            default=None,
            help="Allocation strategy: spot (default), reserved (scheduled), or auto",
        )
        @click.option(
            "--reservation-id",
            default=None,
            help="Bind to an existing reservation (advanced)",
        )
        @click.option(
            "--start",
            "start_time",
            default=None,
            help="When --allocation reserved: ISO8601 UTC start time (e.g., 2025-01-31T18:00:00Z)",
        )
        @click.option(
            "--duration",
            "duration_hours",
            type=int,
            default=None,
            help="When --allocation reserved: reservation duration in hours (3-336)",
        )
        @click.option(
            "--env",
            "env_kv",
            multiple=True,
            help="Environment variables KEY=VALUE (repeatable)",
        )
        @click.option("--pricing", is_flag=True, help="Show pricing details in the config table")
        @click.option("--compact", is_flag=True, help="Compact table (hide image, region, mounts)")
        @click.option(
            "--slurm",
            is_flag=True,
            help="Treat input as a SLURM script (auto-detected for .slurm/.sbatch)",
        )
        @click.option(
            "--mount",
            multiple=True,
            help="Mount storage (format: source or target=source). Auto-mounts: s3://→/data, volume://→/volumes",
        )
        @click.option(
            "--port",
            type=int,
            multiple=True,
            help="Expose a port (repeatable). High ports only (>=1024).",
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
        @click.option(
            "--on-upload-failure",
            type=click.Choice(["continue", "fail"], case_sensitive=False),
            default="continue",
            help=(
                "Policy when code upload fails (CLI-managed SCP only): "
                "continue (default) or fail to abort the run"
            ),
        )
        @click.option(
            "--demo/--no-demo",
            default=None,
            help="Override demo mode for this command (mock provider, no real provisioning)",
        )
        @click.option("--max-price-per-hour", "-m", type=float, help="Maximum hourly price in USD")
        @click.option(
            "--num-instances", "-N", type=int, default=1, help="Number of instances (default: 1)"
        )
        @click.option(
            "--distributed",
            type=click.Choice(["auto", "manual"], case_sensitive=False),
            help="Distributed rendezvous mode when --num-instances > 1 (default: auto)",
        )
        @click.option(
            "--verbose",
            "-v",
            is_flag=True,
            help="Show detailed configuration options and workflows",
        )
        @demo_aware_command(flag_param="demo")
        def run(
            config_file: str | None,
            instance_type: str | None,
            ssh_keys: tuple[str, ...],
            image: str,
            name: str | None,
            no_unique: bool,
            command: str | None,
            extra_args: tuple[str, ...],
            priority: str | None,
            wait: bool,
            dry_run: bool,
            watch: bool,
            output_json: bool,
            env_kv: tuple[str, ...],
            pricing: bool,
            compact: bool,
            mount: tuple[str, ...],
            port: tuple[int, ...],
            upload_strategy: str,
            upload_timeout: int,
            on_upload_failure: str,
            demo: bool | None,
            max_price_per_hour: float | None,
            num_instances: int,
            verbose: bool,
            slurm: bool,
            on_name_conflict: str | None,
            force_new: bool,
            distributed: str | None,
            allocation: str | None,
            reservation_id: str | None,
            start_time: str | None,
            duration_hours: int | None,
        ) -> None:
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
            if verbose and not config_file and not command and not extra_args:
                console.print("\n[bold]Flow Run Configuration Guide:[/bold]\n")
                console.print("Quick start patterns:")
                console.print("  flow run                          # Interactive 8xH100 instance")
                console.print("  flow run 'nvidia-smi'             # Quick GPU test")
                console.print("  flow run 'python train.py' -i h100  # Run script on specific GPU")
                console.print("  flow run training.yaml            # From configuration file\n")

                console.print("Configuration file format:")
                console.print("  name: my-training-job")
                console.print(
                    "  instance_type: 8xh100  # Prefer simplified names; provider maps to native type"
                )
                console.print("  image: nvidia/cuda:12.1.0-runtime-ubuntu22.04")
                console.print("  command: python train.py --epochs 100")
                console.print("  volumes:")
                console.print("    - size_gb: 100")
                console.print("      mount_path: /data")
                console.print("  env:")
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
                console.print("  --mount volume://vol-123          # Mount volume to /volumes")
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
            # Demo mode already applied by decorator

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
                env_kv,
                mount,
                port,
                upload_strategy,
                upload_timeout,
                on_upload_failure,
                command,
                extra_args,
                max_price_per_hour,
                num_instances,
                slurm,
                pricing,
                compact,
                on_name_conflict,
                force_new,
                distributed,
                allocation,
                reservation_id,
                start_time,
                duration_hours,
            )

        return run

    def _execute(
        self,
        config_file: str | None,
        instance_type: str | None,
        ssh_keys: tuple[str, ...],
        image: str,
        name: str | None,
        no_unique: bool,
        priority: str | None,
        wait: bool,
        dry_run: bool,
        watch: bool,
        output_json: bool,
        env_kv: tuple[str, ...],
        mount: tuple[str, ...],
        port: tuple[int, ...],
        upload_strategy: str,
        upload_timeout: int,
        on_upload_failure: str,
        command: str | None = None,
        extra_args: tuple[str, ...] = (),
        max_price_per_hour: float | None = None,
        num_instances: int = 1,
        slurm: bool = False,
        show_pricing: bool = False,
        compact: bool = False,
        on_name_conflict: str | None = None,
        force_new: bool = False,
        distributed: str | None = None,
        allocation: str | None = None,
        reservation_id: str | None = None,
        start_time: str | None = None,
        duration_hours: int | None = None,
    ) -> None:
        """Execute the run command.

        Args:
            config_file: Path to YAML config, or None when using command/interactive.
            instance_type: GPU instance type override.
            ssh_keys: SSH key FIDs or paths to inject.
            image: Docker image to use.
            name: Optional task name.
            no_unique: Do not append unique suffix to name.
            priority: Task priority (low/med/high).
            wait: Wait for task to start running.
            dry_run: Validate and print configuration without submitting.
            watch: Watch task progress after submission.
            output_json: Print machine-readable JSON output.
            mount: Storage mount specifications provided on CLI.
            upload_strategy: Code upload strategy (auto|embedded|scp|none).
            upload_timeout: Upload timeout in seconds.
            command: Command to run instead of using a config file.
            max_price_per_hour: Maximum hourly price in USD.
            num_instances: Number of instances for multi-node runs.
            slurm: Treat input as SLURM script (or auto-detected).
            show_pricing: Include pricing details in config display.
            compact: Use compact table output.
            on_name_conflict: Policy for name conflicts (error|suffix).
            force_new: If True, auto-suffix on name conflict.
            distributed: Distributed rendezvous mode when using multiple instances.
            allocation: Allocation strategy for capacity (spot|reserved|auto).
            reservation_id: Reservation identifier when binding to an existing reservation.
            start_time: ISO8601 UTC start time for reserved allocation.
            duration_hours: Reservation duration in hours for reserved allocation.

        Raises:
            click.exceptions.Exit: On handled CLI error paths.
        """
        # Unified timeline for non-JSON output
        timeline: StepTimeline | None = None
        if not output_json:
            timeline = StepTimeline(console, title="flow run", title_animation="auto")
            timeline.start()

        try:
            # Default flags for later branches
            is_slurm = False
            configs = None
            # Prefer explicit "-- <args>" for inline command tokens
            inline_cmd_tokens: list[str] | None = None
            if extra_args:
                # Reconstruct command when user passed '--' and Click captured
                # the first token as config_file and the remainder as extra_args.
                combined: list[str] = []
                if config_file:
                    lower = config_file.lower()
                    looks_like_config = lower.endswith(
                        (".yaml", ".yml", ".slurm", ".sbatch")
                    ) or os.path.exists(config_file)
                    if not looks_like_config:
                        combined.append(config_file)
                        config_file = None
                combined.extend(list(extra_args))
                inline_cmd_tokens = combined or None
                # If we assembled a command from positionals, ensure we treat as no config file
                if inline_cmd_tokens is not None:
                    config_file = None
            # Fallback: treat a single bare token with common command names as a command
            if (
                not inline_cmd_tokens
                and config_file
                and not command
                and not os.path.exists(config_file)
            ):
                common = ("python", "bash", "sh", "./", "nvidia-smi", "echo", "env", "hostname")
                if (" " in config_file) or any(config_file.startswith(p) for p in common):
                    inline_cmd_tokens = config_file.split()
                    config_file = None
            # Last-resort: parse tokens after "--" from sys.argv
            # No further argv sniffing; Click already provided extra_args

            # Validate mutually exclusive options
            if config_file and command:
                self.handle_error("Cannot specify both a config file and a command")
                return

            # Remove this check - we'll use default instance type if not specified

            # Default provider name for mount path resolution; resolve from config when available
            provider_name = os.environ.get("FLOW_PROVIDER", "mithril").lower()

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
                            with open(config_file) as f:
                                head = f.read(4096)
                                if "#SBATCH" in head:
                                    is_slurm = True
                        except Exception:
                            pass

                if is_slurm:
                    # Route through the SLURM adapter to produce TaskConfig(s)
                    import asyncio

                    from flow._internal.frontends.slurm.adapter import SlurmFrontendAdapter
                    from flow._internal.frontends.slurm.parser import parse_sbatch_script

                    adapter = SlurmFrontendAdapter()
                    slurm_overrides: dict[str, object] = {}
                    if instance_type:
                        # Map Flow instance_type to a SLURM-like GPU hint: 4xa100 -> a100:4
                        it = instance_type.strip().lower()
                        if "x" in it:
                            try:
                                count, gpu = it.split("x", 1)
                                _ = int(count)
                                slurm_overrides["gpus"] = f"{gpu}:{count}"
                            except Exception:
                                slurm_overrides["gpus"] = it
                        else:
                            slurm_overrides["gpus"] = it

                    if num_instances and num_instances != 1:
                        slurm_overrides["nodes"] = num_instances

                    # Detect array jobs and expand when present
                    _slurm_cfg = parse_sbatch_script(str(config_file))
                    if getattr(_slurm_cfg, "array", None):
                        configs = self._safe_async_run(
                            adapter.parse_array_job(config_file, **slurm_overrides)
                        )
                    else:
                        single = self._safe_async_run(
                            adapter.parse_and_convert(config_file, **slurm_overrides)
                        )
                        configs = [single]
                else:
                    # Load YAML manually to avoid implicit unique name suffixing
                    try:
                        with open(config_file) as _f:
                            _data = yaml.safe_load(_f)
                        if not isinstance(_data, dict):
                            raise yaml.YAMLError("YAML must be a mapping of keys to values")
                        _data.setdefault("unique_name", False)
                        config = TaskConfig(**_data)
                    except FileNotFoundError:
                        self.handle_error(f"Configuration file does not exist: {config_file}")
                        return
                    except yaml.YAMLError as e:
                        self.handle_error(f"Invalid YAML: {e}")
                        return
                    except Exception as e:
                        self.handle_error(f"Invalid YAML: {e}")
                        return

                # Apply CLI overrides
                if is_slurm:
                    # Handle list of TaskConfig(s)
                    updated_configs = []
                    for cfg in configs:
                        updates = {}
                        if upload_strategy != "auto":
                            updates["upload_strategy"] = upload_strategy
                            updates["upload_timeout"] = upload_timeout
                        elif upload_timeout != 600:
                            updates["upload_timeout"] = upload_timeout
                        if priority is not None:
                            updates["priority"] = priority.lower()
                        if max_price_per_hour is not None:
                            updates["max_price_per_hour"] = max_price_per_hour
                        if num_instances != 1:
                            updates["num_instances"] = num_instances
                        if distributed:
                            updates["distributed_mode"] = distributed.lower()
                        updated_configs.append(cfg.model_copy(update=updates) if updates else cfg)
                    configs = updated_configs
                else:
                    updates = {}
                    if upload_strategy != "auto":
                        updates["upload_strategy"] = upload_strategy
                        updates["upload_timeout"] = upload_timeout
                    elif upload_timeout != 600:
                        updates["upload_timeout"] = upload_timeout
                    if priority is not None:
                        updates["priority"] = priority.lower()
                    if max_price_per_hour is not None:
                        updates["max_price_per_hour"] = max_price_per_hour
                    if num_instances != 1:
                        updates["num_instances"] = num_instances
                    if distributed:
                        updates["distributed_mode"] = distributed.lower()
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
                    (inline_cmd_tokens if inline_cmd_tokens else command),
                    priority,
                    max_price_per_hour,
                    num_instances,
                )
                if distributed:
                    config_dict["distributed_mode"] = distributed.lower()
                config = TaskConfig(**config_dict)

            # Apply ports collected from CLI (validate: >= 1024)
            if port:
                try:
                    ports_clean = []
                    for p in port:
                        pi = int(p)
                        if pi < 1024 or pi > 65535:
                            self.handle_error(
                                f"Invalid --port {pi}. Only ports in 1024-65535 are supported."
                            )
                            return
                        ports_clean.append(pi)
                    if is_slurm:
                        configs = [c.model_copy(update={"ports": ports_clean}) for c in configs]
                    else:
                        config = config.model_copy(update={"ports": ports_clean})
                except Exception as e:
                    self.handle_error(f"Invalid --port values: {e}")
                    return

            # Reserved allocation wiring
            try:
                res_updates = {}
                if allocation:
                    res_updates["allocation_mode"] = allocation.lower()
                if reservation_id:
                    res_updates["reservation_id"] = reservation_id
                if start_time:
                    from datetime import datetime as _dt

                    iso = start_time.replace("Z", "+00:00")
                    res_updates["scheduled_start_time"] = _dt.fromisoformat(iso)
                if duration_hours is not None:
                    res_updates["reserved_duration_hours"] = duration_hours
                if res_updates:
                    if is_slurm:
                        configs = [c.model_copy(update=res_updates) for c in configs]
                    else:
                        config = config.model_copy(update=res_updates)
            except Exception as e:
                self.handle_error(f"Invalid reservation options: {e}")
                return

            # Apply upload strategy and timeout if specified
            if is_slurm:
                if upload_strategy != "auto":
                    configs = [
                        c.model_copy(
                            update={
                                "upload_strategy": upload_strategy,
                                "upload_timeout": upload_timeout,
                            }
                        )
                        for c in configs
                    ]
                elif upload_timeout != 600:
                    configs = [
                        c.model_copy(update={"upload_timeout": upload_timeout}) for c in configs
                    ]
            else:
                if upload_strategy != "auto":
                    config = config.model_copy(
                        update={
                            "upload_strategy": upload_strategy,
                            "upload_timeout": upload_timeout,
                        }
                    )
                elif upload_timeout != 600:
                    # Only update timeout if non-default
                    config = config.model_copy(update={"upload_timeout": upload_timeout})

            # Parse --env KEY=VALUE pairs into config.env
            try:
                if env_kv:
                    env_updates = {}
                    for kv in env_kv:
                        if "=" not in kv:
                            self.handle_error(
                                f"Invalid --env '{kv}'. Expected format KEY=VALUE (e.g., FOO=bar)"
                            )
                            return
                        k, v = kv.split("=", 1)
                        env_updates[k] = v
                    if env_updates:
                        if is_slurm:
                            updated = []
                            for c in configs:
                                merged_env = dict(getattr(c, "env", {}) or {})
                                merged_env.update(env_updates)
                                c2 = c.model_copy(update={"env": merged_env})
                                try:
                                    object.__setattr__(c2, "environment", c2.env)
                                except Exception:
                                    pass
                                updated.append(c2)
                            configs = updated
                        else:
                            merged_env = dict(getattr(config, "env", {}) or {})
                            merged_env.update(env_updates)
                            config = config.model_copy(update={"env": merged_env})
                            try:
                                object.__setattr__(config, "environment", config.env)
                            except Exception:
                                pass
            except Exception:
                pass

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

            if is_slurm:
                # For SLURM arrays, display summary; for single, display detailed config
                if not output_json:
                    if len(configs) == 1:
                        display_config(
                            configs[0].model_dump(), show_pricing=show_pricing, compact=compact
                        )
                    else:
                        console.print(f"[bold]SLURM array detected[/bold]: {len(configs)} tasks")
                        # Show the first config as template
                        display_config(
                            {"template": True, **configs[0].model_dump()},
                            show_pricing=False,
                            compact=True,
                        )
                    if mount_dict:
                        console.print("\n[bold]Mounts:[/bold]")
                        for target, source in mount_dict.items():
                            console.print(f"  {target} → {source}")
            else:
                if not output_json:
                    display_config(config.model_dump(), show_pricing=show_pricing, compact=compact)
                    if mount_dict:
                        console.print("\n[bold]Mounts:[/bold]")
                        for target, source in mount_dict.items():
                            console.print(f"  {target} → {source}")

            if dry_run:
                if output_json:
                    if is_slurm:
                        result = {"status": "valid", "configs": [c.model_dump() for c in configs]}
                    else:
                        result = {"status": "valid", "config": config.model_dump()}
                    if mount_dict:
                        result["mounts"] = mount_dict
                    console.print(json.dumps(result))
                else:
                    if timeline:
                        try:
                            timeline.finish()
                        except Exception:
                            pass
                    from flow.cli.utils.theme_manager import theme_manager as _tm

                    success_color = _tm.get_color("success")
                    if is_slurm and len(configs) > 1:
                        console.print(
                            f"\n[{success_color}]✓[/{success_color}] {len(configs)} configurations are valid"
                        )
                    else:
                        console.print(
                            f"\n[{success_color}]✓[/{success_color}] Configuration is valid"
                        )
                return

            # If user explicitly requested scp upload, let CLI own upload step by disabling provider auto-upload
            cli_managed_scp = False
            try:
                if upload_strategy == "scp":
                    config = config.model_copy(update={"upload_strategy": "none"})
                    cli_managed_scp = True
            except Exception:
                pass

            # Initialize Flow client only when we're ready to submit
            flow_client = Flow()

            if is_slurm and len(configs) > 1:
                tasks = []
                if not output_json:
                    console.print(f"Submitting {len(configs)} array tasks...")
                for cfg in configs:
                    try:
                        t = flow_client.run(cfg, mounts=mount_dict)
                        tasks.append(t)
                        if not output_json:
                            console.print(
                                f"Task ID: [accent]{t.task_id}[/accent]  ([dim]{cfg.name}[/dim])"
                            )
                    except Exception as e:
                        t_retry = self._handle_name_conflict_retry(
                            e,
                            cfg,
                            flow_client,
                            mounts=mount_dict,
                            policy=(on_name_conflict or ("suffix" if (force_new or not name) else "error")),
                        )
                        if t_retry is None:
                            raise
                        tasks.append(t_retry)
                        if not output_json:
                            console.print(
                                f"[dim]Name conflict resolved by using: {getattr(t_retry, 'name', '?')}[/dim]"
                            )
            else:
                # Single task submission path (original behavior)
                if not output_json and timeline:
                    submit_idx = timeline.add_step("Submitting task", show_bar=False)
                    timeline.start_step(submit_idx)
                    try:
                        task = flow_client.run(config, mounts=mount_dict)
                    except Exception as e:
                        task_retry = self._handle_name_conflict_retry(
                            e,
                            config,
                            flow_client,
                            mounts=mount_dict,
                            policy=(on_name_conflict or ("suffix" if (force_new or not name) else "error")),
                        )
                        if task_retry is None:
                            raise
                        task = task_retry
                        console.print(
                            f"[dim]Name conflict resolved by using: {getattr(task, 'name', '?')}[/dim]"
                        )
                    timeline.complete_step()
                else:
                    try:
                        task = flow_client.run(config, mounts=mount_dict)
                    except Exception as e:
                        task_retry = self._handle_name_conflict_retry(
                            e,
                            config,
                            flow_client,
                            mounts=mount_dict,
                            policy=(on_name_conflict or ("suffix" if (force_new or not name) else "error")),
                        )
                        if task_retry is None:
                            raise
                        task = task_retry
                        if not output_json:
                            console.print(
                                f"[dim]Name conflict resolved by using: {getattr(task, 'name', '?')}[/dim]"
                            )

            # Always print task ID early so automation/tests can detect it
            try:
                if not output_json and not (is_slurm and len(configs) > 1):
                    console.print(f"Task ID: [accent]{task.task_id}[/accent]")
            except Exception:
                pass

            # Invalidate and opportunistically refresh task list caches
            try:
                from flow.cli.utils.prefetch import (
                    invalidate_cache_for_current_context,
                    refresh_active_task_caches,
                    refresh_all_tasks_cache,
                )

                invalidate_cache_for_current_context(
                    ["tasks_running", "tasks_pending", "tasks_all"]
                )

                import threading

                def _refresh():
                    try:
                        refresh_active_task_caches()
                        refresh_all_tasks_cache()
                    except Exception:
                        pass

                threading.Thread(target=_refresh, daemon=True).start()
            except Exception:
                pass

            if output_json:
                if is_slurm and len(configs) > 1:
                    result = {
                        "status": "submitted",
                        "tasks": [{"task_id": t.task_id, "name": t.name} for t in tasks],
                    }
                    console.print(json.dumps(result))
                    return
                else:
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

            if is_slurm and len(configs) > 1:
                # For arrays, do not wait in aggregate path; suggest next actions
                if not output_json:
                    console.print(
                        f"\nSubmitted {len(configs)} tasks. Use filters by name to operate on the set."
                    )
                    print_next_actions(
                        console,
                        [
                            "List tasks: [accent]flow status --all[/accent]",
                            "Cancel by name pattern: [accent]flow cancel -n '<prefix>*'[/accent]",
                        ],
                    )
                return

            if not wait:
                task_ref = task.name or task.task_id
                if task.name:
                    console.print(f"\nTask submitted: [accent]{task.name}[/accent]")
                else:
                    console.print(f"\nTask submitted with ID: [accent]{task.task_id}[/accent]")
                print_next_actions(
                    console,
                    [
                        f"Check task status: [accent]flow status {task_ref}[/accent]",
                        f"Stream logs: [accent]flow logs {task_ref} --follow[/accent]",
                        f"Cancel if needed: [accent]flow cancel {task_ref}[/accent]",
                    ],
                )
                return

            # Allocation step
            if timeline:
                alloc_idx = timeline.add_step(
                    "Allocating instance", show_bar=True, estimated_seconds=120
                )
                alloc_adapter = AllocationProgressAdapter(
                    timeline, alloc_idx, estimated_seconds=120
                )
                with alloc_adapter:
                    status = wait_for_task(
                        flow_client,
                        task.task_id,
                        watch=False,
                        json_output=False,
                        task_name=task.name,
                        progress_adapter=alloc_adapter,
                    )
            else:
                status = wait_for_task(
                    flow_client, task.task_id, watch=watch, json_output=False, task_name=task.name
                )

            if status == "running":
                from flow.cli.utils.theme_manager import theme_manager as _tm2

                success_color = _tm2.get_color("success")
                console.print(f"\n[{success_color}]✓[/{success_color}] Task launched successfully!")
                if task.name:
                    console.print(f"Task name: [accent]{task.name}[/accent]")
                    console.print(f"Task ID: [dim]{task.task_id}[/dim]")
                else:
                    console.print(f"Task ID: [accent]{task.task_id}[/accent]")

                # Common task reference used in subsequent hints/actions
                task_ref = task.name or task.task_id

                # Provisioning & SSH step (only when CLI will upload via scp)
                if cli_managed_scp and timeline:
                    from flow.api.ssh_utils import DEFAULT_PROVISION_MINUTES

                    # Seed from instance age to allow resume after Ctrl+C to reflect total wait
                    baseline = 0
                    try:
                        baseline = int(getattr(task, "instance_age_seconds", None) or 0)
                    except Exception:
                        baseline = 0
                    prov_idx = timeline.add_step(
                        "Provisioning & SSH",
                        show_bar=True,
                        estimated_seconds=DEFAULT_PROVISION_MINUTES * 60,
                        baseline_elapsed_seconds=baseline,
                    )
                    ssh_adapter = SSHWaitProgressAdapter(
                        timeline,
                        prov_idx,
                        DEFAULT_PROVISION_MINUTES * 60,
                        baseline_elapsed_seconds=baseline,
                    )
                    # Hint for Ctrl+C safe exit
                    try:
                        from rich.text import Text

                        from flow.cli.utils.theme_manager import theme_manager

                        accent = theme_manager.get_color("accent")
                        hint = Text()
                        hint.append("  Press ")
                        hint.append("Ctrl+C", style=accent)
                        hint.append(" to stop waiting. Upload later with ")
                        hint.append("flow upload-code", style=accent)
                        timeline.set_active_hint_text(hint)
                    except Exception:
                        pass
                    with ssh_adapter:
                        task = flow_client.wait_for_ssh(
                            task_id=task.task_id,
                            timeout=DEFAULT_PROVISION_MINUTES * 60,
                            show_progress=False,
                            progress_adapter=ssh_adapter,
                        )

                # Code upload step (CLI-managed scp)
                if cli_managed_scp and timeline:
                    try:
                        provider = flow_client.provider
                        upload_idx = timeline.add_step("Uploading code", show_bar=True)
                        timeline.start_step(upload_idx)
                        reporter = UploadProgressReporter(timeline, upload_idx)
                        # Ctrl+C guidance
                        try:
                            from rich.text import Text

                            from flow.cli.utils.theme_manager import theme_manager

                            accent = theme_manager.get_color("accent")
                            hint2 = Text()
                            hint2.append("  Press ")
                            hint2.append("Ctrl+C", style=accent)
                            hint2.append(" to cancel upload. Instance keeps running; resume with ")
                            hint2.append("flow upload-code", style=accent)
                            timeline.set_active_hint_text(hint2)
                        except Exception:
                            pass
                        provider.upload_code_to_task(
                            task_id=task.task_id,
                            source_dir=None,
                            timeout=upload_timeout or 600,
                            console=None,
                            target_dir="~",
                            progress_reporter=reporter,
                        )
                    except KeyboardInterrupt:
                        # Interrupting upload is safe; surface a clear message
                        console.print(
                            "\n[dim]Upload interrupted by user. Instance remains running.\nResume anytime with: flow upload-code[/dim]"
                        )
                    except Exception as e:
                        from flow.cli.utils.theme_manager import theme_manager as _tm_hint

                        warn_color = _tm_hint.get_color("warning")
                        console.print(f"\n[{warn_color}]Upload skipped: {e}[/{warn_color}]")
                        # Instance continues running; surface clear manual action
                        try:
                            console.print(
                                f"[dim]Instance is running. Sync later with: flow upload-code {task_ref}[/dim]"
                            )
                        except Exception:
                            pass
                        # Honor policy for CLI-managed upload failures
                        try:
                            if (on_upload_failure or "").lower() == "fail":
                                import click as _click

                                raise _click.ClickException(f"Code upload failed: {e}")
                        except Exception:
                            # If policy handling fails, continue without aborting
                            pass

                # If provider is handling background upload (auto-selected SCP), hint to the user
                if not cli_managed_scp and getattr(task, "_upload_pending", False):
                    try:
                        from flow.cli.utils.theme_manager import theme_manager as _tm_hint2

                        muted = _tm_hint2.get_color("muted")
                        console.print(
                            f"[{muted}]Code upload will run in background. If it fails, sync manually with: flow upload-code {task_ref}[/{muted}]"
                        )
                    except Exception:
                        pass
                # If background upload already failed, surface definitive notice
                if not cli_managed_scp and getattr(task, "_upload_failed", False):
                    try:
                        err = getattr(task, "_upload_error", "") or "code upload failed"
                        from flow.cli.utils.theme_manager import theme_manager as _tm_hint3

                        warn = _tm_hint3.get_color("warning")
                        accent = _tm_hint3.get_color("accent")
                        console.print(
                            f"[{warn}]Background code upload failed[/{warn}]: {err}. "
                            f"Sync manually with: [{accent}]flow upload-code {task_ref}[/{accent}]"
                        )
                    except Exception:
                        pass

                recommendations = [
                    f"SSH into instance: [accent]flow ssh {task_ref}[/accent]",
                    f"Stream logs: [accent]flow logs {task_ref} --follow[/accent]",
                    f"Check status: [accent]flow status {task_ref}[/accent]",
                ]
                # If the run intended to upload code, offer manual upload as a next action
                try:
                    if getattr(config, "upload_code", False):
                        recommendations.append(
                            f"Upload code: [accent]flow upload-code {task_ref}[/accent]"
                        )
                except Exception:
                    pass
                print_next_actions(console, recommendations)
            elif status == "failed":
                console.print("\n[red]✗[/red] Task failed to start")
                print_next_actions(
                    console,
                    [
                        f"View error logs: [accent]flow logs {task.name or task.task_id}[/accent]",
                        f"Check task details: [accent]flow status {task.name or task.task_id}[/accent]",
                        "Retry with different parameters: [accent]flow run <config.yaml>[/accent]",
                    ],
                )
            elif status == "cancelled":
                console.print("\n[yellow]![/yellow] Task was cancelled")
                print_next_actions(
                    console,
                    [
                        "Submit a new task: [accent]flow run <config.yaml>[/accent]",
                        "View task history: [accent]flow status --all[/accent]",
                    ],
                )

        except AuthenticationError:
            self.handle_auth_error()
        except ValidationError as e:
            from rich.markup import escape

            self.handle_error(f"Invalid configuration: {escape(str(e))}")
        except FileNotFoundError:
            self.handle_error(f"Configuration file not found: {config_file}")
        except yaml.YAMLError as e:
            from rich.markup import escape

            self.handle_error(f"Invalid YAML: {escape(str(e))}")
        except click.exceptions.Exit:
            # Re-raise cleanly to avoid duplicate error lines
            raise
        except Exception as e:
            # Preserve structured suggestions if present on exception
            self.handle_error(e)
        finally:
            # Ensure timeline is closed if started
            if timeline:
                try:
                    timeline.finish()
                except Exception:
                    pass

    def _ensure_nest(self) -> None:
        try:
            import nest_asyncio  # type: ignore

            try:
                nest_asyncio.apply()
            except Exception:
                pass
        except Exception:
            pass

    def _safe_async_run(self, awaitable):
        try:
            loop = __import__("asyncio").get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            self._ensure_nest()
            return loop.run_until_complete(awaitable)
        else:
            return __import__("asyncio").run(awaitable)

    def _handle_name_conflict_retry(
        self,
        exc: Exception,
        cfg_or_config: TaskConfig,
        flow_client: Flow,
        *,
        mounts: dict | None,
        policy: str | None,
    ):
        """Retry submission with a suffixed name when policy requires it.

        Returns the new Task on retry success, or None if not retried or failed.
        """
        try:
            msg = str(exc)
            chosen_policy = (policy or "error").lower()
            is_conflict = (
                ("already in use" in msg.lower())
                or ("already exists" in msg.lower())
                or ("name conflict" in msg.lower())
            )
            if is_conflict and chosen_policy == "suffix":
                import uuid as _uuid

                base = getattr(cfg_or_config, "name", None) or "flow-task"
                retry_name = f"{base}-{_uuid.uuid4().hex[:6]}"
                updated = cfg_or_config.model_copy(update={"name": retry_name, "unique_name": False})
                return flow_client.run(updated, mounts=mounts)
        except Exception:
            return None
        return None

    def _create_interactive_config(
        self,
        instance_type: str,
        ssh_keys: tuple[str, ...],
        image: str,
        name: str | None,
        no_unique: bool,
        command: str | None = None,
        priority: str | None = None,
        max_price_per_hour: float | None = None,
        num_instances: int = 1,
    ) -> dict:
        """Create a minimal config for interactive instances.

        Args:
            instance_type: Instance type to launch (e.g., "h100", "8xh100").
            ssh_keys: SSH keys to inject.
            image: Docker image.
            name: Desired task name (auto-generated if None).
            no_unique: Do not append unique suffix to the generated name.
            command: Optional command to execute (keeps container alive if None).
            priority: Optional priority override.
            max_price_per_hour: Optional price ceiling.
            num_instances: Number of instances for multi-node.

        Returns:
            Dict representing a TaskConfig suitable for initialization.
        """
        from flow.cli.utils.name_generator import generate_unique_name

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

        # Build config dictionary; keep env empty so --env merges are exact in tests
        config = {
            "name": name,
            "unique_name": False,  # We handle uniqueness ourselves with --no-unique
            "instance_type": instance_type,
            "image": image,
            "env": {},
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
