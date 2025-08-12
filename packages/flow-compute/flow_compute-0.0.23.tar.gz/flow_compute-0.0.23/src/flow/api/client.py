"""Unified GPU workload orchestration.

A concise, explicit interface for submitting, monitoring, and managing GPU
workloads across providers. Designed for the common path with clear escape
hatches.

Examples:
    Quick start:
        >>> flow = Flow()
        >>> task = flow.run("python train.py", instance_type="a100", wait=True)
        >>> print(task.status)

    Using TaskConfig with volumes, environment, image, and code_root:
        >>> from flow.api.models import TaskConfig, VolumeSpec
        >>> cfg = TaskConfig(
        ...     name="ddp-train",
        ...     instance_type="8xa100",
        ...     command=["torchrun", "--nproc_per_node=8", "train.py"],
        ...     env={"EPOCHS": "100", "BATCH_SIZE": "512"},
        ...     volumes=[VolumeSpec(size_gb=500, mount_path="/data", name="datasets")],
        ...     image="pytorch/pytorch:2.2.2-cuda12.1-cudnn8",
        ...     code_root="./src",
        ...     max_price_per_hour=25.0,
        ... )
        >>> task = flow.run(cfg, wait=True)
        >>> for line in flow.logs(task.task_id, follow=True):
        ...     if "loss:" in line: break
"""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, TypedDict

from flow._internal.config import Config
from flow._internal.data import URLResolver, VolumeLoader
from flow._internal.data.resolver import DataError
from flow.api.models import (
    AvailableInstance,
    MountSpec,
    Task,
    TaskConfig,
    TaskStatus,
    Volume,
    VolumeSpec,
)
from flow.core.provider_interfaces import IProvider
from flow.core.resources import GPUParser, InstanceMatcher
from flow.errors import (
    AuthenticationError,
    FlowError,
    ResourceNotAvailableError,
    ValidationError,
    VolumeError,
)
from flow.providers.factory import create_provider
from flow.providers.interfaces import IProviderInit

if TYPE_CHECKING:  # pragma: no cover - imported for static type checking only
    from flow.api.dev import DevEnvironment

logger = logging.getLogger(__name__)


# ================== Type Definitions ==================


class GPUInstanceDict(TypedDict):
    """GPU instance dictionary returned by _find_gpus_by_memory()."""

    name: str
    gpu_memory_gb: int
    price_per_hour: float
    gpu_model: str


class TaskDict(TypedDict):
    """Task dictionary returned by list() method."""

    id: str
    name: str
    status: str
    instance_type: str
    created: str | None


class InstanceRequirements(TypedDict, total=False):
    """Instance requirements dictionary for find_instances()."""

    instance_type: str
    min_gpu_count: int
    max_price: float
    region: str
    gpu_memory_gb: int
    gpu_type: str


class CatalogEntry(TypedDict):
    """Instance catalog entry dictionary."""

    name: str
    gpu_type: str
    gpu_count: int
    price_per_hour: float
    available: bool
    gpu: dict[str, Any]  # Nested GPU info with model and memory_gb


class Flow:
    """Primary client for submitting and managing GPU jobs.

    - Simple for 90% of use cases (one obvious way to run a task)
    - Explicit configuration via `TaskConfig` when needed
    - Clean access to logs, SSH, volumes, and instance discovery
    """

    def __init__(self, config: Config | None = None, auto_init: bool = False):
        """Create a Flow client.

        Args:
            config: Explicit configuration. If omitted, environment discovery is used.
            auto_init: If True and auth is missing, trigger interactive setup (CLI contexts).

        Raises:
            AuthenticationError: If credentials are missing and `auto_init` is False.
        """
        if config:
            self.config = config
        else:
            try:
                # In demo/mock mode, do not require auth
                require_auth = True
                try:
                    from flow.cli.utils.mode import (
                        is_demo_active,  # CLI path; safe import in CLI contexts
                    )

                    if is_demo_active():
                        require_auth = False
                except Exception:
                    # Fallback on provider name after load attempt
                    pass
                self.config = Config.from_env(require_auth=require_auth)
            except ValueError as e:
                if auto_init:
                    # Only launch interactive setup from CLI
                    from flow._internal.auth import ensure_initialized

                    if not ensure_initialized():
                        # Re-raise as structured auth error for consistent CLI handling
                        raise AuthenticationError(
                            "Authentication not configured",
                            suggestions=[
                                "Run 'flow init' to configure your API key interactively",
                                "Or set MITHRIL_API_KEY in your environment",
                                "Non-interactive: flow init --api-key $MITHRIL_API_KEY --yes",
                            ],
                            error_code="AUTH_001",
                        ) from e
                    # Retry after setup (still respect demo mode)
                    self.config = Config.from_env(require_auth=True)
                else:
                    # In SDK usage, re-raise as structured auth error
                    raise AuthenticationError(
                        "Authentication not configured",
                        suggestions=[
                            "Set MITHRIL_API_KEY in your environment",
                            "Or initialize credentials with flow.init() / 'flow init'",
                        ],
                        error_code="AUTH_001",
                    ) from e

        self._provider: IProvider | None = None
        self._dev = None

    @property
    def dev(self) -> DevEnvironment:
        """Access the persistent dev VM API.

        Returns:
            DevEnvironment: Manage a long-lived VM for fast iteration.
        """
        if self._dev is None:
            from flow.api.dev import DevEnvironment

            self._dev = DevEnvironment(self)
        return self._dev

    def dev_context(self, auto_stop: bool = False) -> DevEnvironment:
        """Context manager for the dev VM.

        Args:
            auto_stop: Stop the VM on context exit.

        Returns:
            DevEnvironment.
        """
        from flow.api.dev import DevEnvironment

        return DevEnvironment(self, auto_stop=auto_stop)

    def _find_gpus_by_memory(
        self, min_memory_gb: int, max_price: float | None = None
    ) -> list[GPUInstanceDict]:
        """Find GPUs by minimum memory and optional price cap.

        Returns the cheapest matching instances first.
        """
        # Catalog-based selection for determinism in tests and consistent UX
        catalog = self._load_instance_catalog()
        suitable: list[GPUInstanceDict] = []
        for instance in catalog:
            gpu_info = instance.get("gpu", {})
            if not gpu_info:
                continue
            memory_gb = gpu_info.get("memory_gb", 0)
            if memory_gb < min_memory_gb:
                continue
            price = instance.get("price_per_hour")
            if price is None:
                continue
            if max_price is not None and price > max_price:
                continue
            suitable.append(
                {
                    "name": instance["name"],
                    "gpu_memory_gb": memory_gb,
                    "price_per_hour": price,
                    "gpu_model": gpu_info.get("model", "unknown"),
                }
            )
        suitable.sort(key=lambda x: x["price_per_hour"])
        return suitable

    def get_remote_operations(self) -> object:
        """Return the provider's remote operations interface.

        Raises:
            NotImplementedError: If the provider lacks remote ops.
        """
        provider = self._ensure_provider()

        if not hasattr(provider, "get_remote_operations"):
            raise NotImplementedError(
                f"Provider {provider.__class__.__name__} doesn't support remote operations"
            )

        return provider.get_remote_operations()

    def wait_for_ssh(
        self,
        task_id: str,
        timeout: int = 600,
        show_progress: bool = True,
        *,
        progress_adapter: object | None = None,
    ) -> Task:
        """Block until SSH is ready for the task or time out.

        Raises:
            SSHNotReadyError | TimeoutError.
        """
        from flow.api.ssh_utils import wait_for_task_ssh_info

        task = self.get_task(task_id)
        provider = self._ensure_provider()

        return wait_for_task_ssh_info(
            task=task,
            provider=provider,
            timeout=timeout,
            show_progress=show_progress,
            progress_adapter=progress_adapter,
        )

    def get_ssh_tunnel_manager(self) -> object:
        """Return the provider's SSH tunnel manager.

        Raises:
            NotImplementedError: If unsupported by the provider.
        """
        provider = self._ensure_provider()

        if not hasattr(provider, "get_ssh_tunnel_manager"):
            raise NotImplementedError(
                f"Provider {provider.__class__.__name__} doesn't support SSH tunnels"
            )

        return provider.get_ssh_tunnel_manager()

    def _ensure_provider(self) -> IProvider:
        """Return the lazily-initialized provider instance (cached)."""
        if self._provider is None:
            self._provider = create_provider(self.config)
        return self._provider

    @property
    def provider(self) -> IProvider:
        """Compute provider backing this client (lazily created)."""
        return self._ensure_provider()

    def run(
        self,
        task: TaskConfig | str | Path,
        wait: bool = False,
        mounts: str | dict[str, str] | None = None,
    ) -> Task:
        """Submit a task.

        Args:
            task: `TaskConfig`, path to YAML, or string path for YAML.
            wait: If True, block until the task is running before returning.
            mounts: Optional data mounts; string or mapping of target->source.

        Returns:
            Task: Handle for status, logs, SSH, cancel, etc.

        Raises:
            ValidationError: Invalid configuration or missing fields.
            FlowError: Provider errors or capacity issues.
            FileNotFoundError: When a YAML file does not exist.

        Examples:
            Command as a string with an explicit instance type:
                >>> task = flow.run("python train.py --epochs 10", instance_type="a100", wait=True)

            Full TaskConfig with volumes and price cap:
                >>> from flow.api.models import TaskConfig, VolumeSpec
                >>> cfg = TaskConfig(
                ...     name="train",
                ...     instance_type="4xa100",
                ...     command=["python", "-m", "torch.distributed.run", "--nproc_per_node=4", "train.py"],
                ...     volumes=[VolumeSpec(size_gb=200, mount_path="/data", name="train-data")],
                ...     max_price_per_hour=12.0,
                ... )
                >>> task = flow.run(cfg)

            Capability-based selection (cheapest GPU with >= 40GB):
                >>> cfg = TaskConfig(name="infer", min_gpu_memory_gb=40, command="python serve.py")
                >>> task = flow.run(cfg)
        """
        # Load from YAML if needed
        if isinstance(task, (str, Path)):
            task = TaskConfig.from_yaml(str(task))

        # Let provider prepare the task configuration with defaults
        provider = self._ensure_provider()
        task = provider.prepare_task_config(task)

        # Handle mounts parameter - convert to data_mounts
        if mounts:
            mount_specs = self._resolve_data_mounts(mounts)
            # Override any existing data_mounts with the provided mounts
            task = task.model_copy(update={"data_mounts": mount_specs})

        # Validate that either instance_type or min_gpu_memory_gb is specified
        if not task.instance_type and not task.min_gpu_memory_gb:
            raise ValidationError(
                "Must specify either 'instance_type' or 'min_gpu_memory_gb'",
                suggestions=[
                    "Add instance_type='a100' for a specific GPU",
                    "Add min_gpu_memory_gb=24 for capability-based selection",
                    "Run 'flow catalog' to see available instance types",
                ],
            )

        # Handle capability-based GPU selection if needed
        if task.min_gpu_memory_gb and not task.instance_type:
            # Find GPUs with sufficient memory, sorted by price
            suitable_types = self._find_gpus_by_memory(
                min_memory_gb=task.min_gpu_memory_gb, max_price=task.max_price_per_hour
            )

            if suitable_types:
                # Use the cheapest suitable type
                selected = suitable_types[0]
                task.instance_type = selected["name"]
                logger.info(
                    f"Auto-selected {task.instance_type} with {selected['gpu_memory_gb']}GB "
                    f"GPU memory (${selected['price_per_hour']}/hour)"
                )
            else:
                raise ResourceNotAvailableError(
                    f"No GPU instances found with at least {task.min_gpu_memory_gb}GB memory"
                    + (
                        f" under ${task.max_price_per_hour}/hour" if task.max_price_per_hour else ""
                    ),
                    suggestions=[
                        "Try reducing the minimum GPU memory requirement",
                        "Increase your max_price_per_hour limit",
                        "Use 'flow catalog' to see available instances",
                        "Try a different region with --region",
                        "Consider using a specific instance_type instead",
                    ],
                    error_code="RESOURCE_001",
                )

        # At this point we have an instance_type
        logger.debug(f"Submitting task with instance type: {task.instance_type}")

        # Handle volumes - create new ones if needed
        volume_ids = []
        for vol_spec in task.volumes:
            if vol_spec.volume_id:
                # Use existing volume
                volume_ids.append(vol_spec.volume_id)
            else:
                # Create new volume with name
                logger.info(f"Creating volume '{vol_spec.name}' ({vol_spec.size_gb}GB)")
                volume = provider.create_volume(size_gb=vol_spec.size_gb, name=vol_spec.name)
                volume_ids.append(volume.volume_id)

        # Submit task to provider - the provider handles all instance resolution,
        # region selection, and availability checking internally
        task_obj = provider.submit_task(
            instance_type=task.instance_type,
            config=task,
            volume_ids=volume_ids,
        )

        logger.info(f"Task submitted successfully: {task_obj.task_id}")

        # Wait for task to start if requested
        if wait:
            task_obj.wait()

        return task_obj

    def status(self, task_id: str) -> str:
        """Return the task status string (pending, running, completed, failed, cancelled)."""
        provider = self._ensure_provider()
        status = provider.get_task_status(task_id)
        return status.value.lower()

    def cancel(self, task_id: str) -> None:
        """Request cancellation of a running or pending task."""
        provider = self._ensure_provider()
        success = provider.stop_task(task_id)
        if not success:
            raise FlowError(f"Failed to cancel task {task_id}")
        logger.info(f"Task {task_id} cancelled successfully")

    def logs(
        self, task_id: str, follow: bool = False, tail: int = 100, stderr: bool = False
    ) -> str | Iterator[str]:
        """Return recent logs or stream them in real time.

        Args:
            task_id: The task to read logs from.
            follow: If True, stream logs until the task completes.
            tail: Number of trailing lines to fetch when `follow` is False.
            stderr: If True, select stderr (may be merged by some providers).

        Returns:
            str | Iterator[str]: A string (when `follow=False`) or an iterator of lines.

        Examples:
            Fetch and print the last 50 lines:
                >>> print(flow.logs(task_id, tail=50))

            Stream logs and stop after an error:
                >>> for line in flow.logs(task_id, follow=True):
                ...     if "ERROR" in line:
                ...         break
        """
        task = self.get_task(task_id)
        return task.logs(follow=follow, tail=tail, stderr=stderr)

    def shell(
        self,
        task_id: str,
        command: str | None = None,
        node: int | None = None,
        progress_context=None,
    ) -> None:
        """Open an interactive shell or run a command on the task instance.

        Examples:
            Open a shell:
                >>> flow.shell(task_id)

            Run a one-off command:
                >>> flow.shell(task_id, command="nvidia-smi")
        """
        task = self.get_task(task_id)
        task.shell(command, node=node, progress_context=progress_context)

    def list_tasks(
        self,
        status: TaskStatus | list[TaskStatus] | None = None,
        limit: int = 10,
        force_refresh: bool = False,
    ) -> list[Task]:
        """List recent tasks, optionally filtered by status.

        Examples:
            List running tasks and print their names:
                >>> from flow.api.models import TaskStatus
                >>> for t in flow.list_tasks(status=TaskStatus.RUNNING):
                ...     print(t.name)
        """
        provider = self._ensure_provider()
        return provider.list_tasks(status=status, limit=limit, force_refresh=force_refresh)

    # Storage operations

    def create_volume(
        self,
        size_gb: int,
        name: str | None = None,
        interface: Literal["block", "file"] = "block",
    ) -> Volume:
        """Create a persistent volume.

        Args:
            size_gb: Capacity in GB.
            name: Optional display name (used in `volume://name`).
            interface: "block" (exclusive attach) or "file" (multi-attach).

        Returns:
            Volume.

        Examples:
            Create and attach volumes to a task:
                >>> data = flow.create_volume(500, name="datasets")
                >>> ckpt = flow.create_volume(100, name="checkpoints")
                >>> cfg = TaskConfig(
                ...     name="train",
                ...     instance_type="a100",
                ...     command="python train.py",
                ...     volumes=[
                ...         {"volume_id": data.volume_id, "mount_path": "/data"},
                ...         {"volume_id": ckpt.volume_id, "mount_path": "/ckpts"},
                ...     ],
                ... )
                >>> task = flow.run(cfg)
        """
        # Validate interface parameter
        if interface not in ["block", "file"]:
            raise ValueError(f"Invalid interface: {interface}. Must be 'block' or 'file'")

        provider = self._ensure_provider()
        volume = provider.create_volume(size_gb, name, interface)
        logger.info(f"Created {interface} volume {volume.volume_id} ({size_gb}GB)")
        return volume

    def delete_volume(self, volume_id: str) -> None:
        """Delete a volume permanently (no recovery).

        Example:
            >>> flow.delete_volume("vol_abc123")
        """
        provider = self._ensure_provider()
        success = provider.delete_volume(volume_id)
        if not success:
            raise VolumeError(
                f"Failed to delete volume {volume_id}",
                suggestions=[
                    "Check if volume is currently attached to a running task",
                    "Verify volume exists with 'flow volume list'",
                    "Ensure you have permission to delete this volume",
                ],
                error_code="VOLUME_002",
            )
        logger.info(f"Volume {volume_id} deleted successfully")

    def list_volumes(self, limit: int = 100) -> list[Volume]:
        """List volumes for the current project (newest first).

        Example:
            >>> for v in flow.list_volumes():
            ...     print(v.name, v.size_gb)
        """
        provider = self._ensure_provider()
        return provider.list_volumes(limit=limit)

    def mount_volume(self, volume_id: str, task_id: str, mount_point: str | None = None) -> None:
        """Attach a volume to a running task at the given mount point.

        Examples:
            Mount by name to the default path:
                >>> flow.mount_volume("datasets", task_id)

            Mount by ID to a custom path:
                >>> flow.mount_volume("vol_abc123", task_id, mount_point="/inputs")
        """
        provider = self._ensure_provider()
        provider.mount_volume(volume_id, task_id, mount_point=mount_point)
        logger.info(f"Successfully mounted volume {volume_id} to task {task_id}")

    def get_task(self, task_id: str) -> Task:
        """Return a `Task` handle for an existing job.

        Example:
            >>> t = flow.get_task(task_id)
            >>> print(t.status)
        """
        provider = self._ensure_provider()
        return provider.get_task(task_id)

    def find_instances(
        self,
        requirements: InstanceRequirements,
        limit: int = 10,
    ) -> list[AvailableInstance]:
        """Return available instances that match the given constraints.

        Example:
            >>> flow.find_instances({"gpu_type": "a100", "max_price": 8.0}, limit=5)
        """
        provider = self._ensure_provider()
        return provider.find_instances(requirements, limit=limit)

    def submit(
        self,
        command: str,
        *,
        gpu: str | None = None,
        mounts: str | dict[str, str] | None = None,
        instance_type: str | None = None,
        wait: bool = False,
    ) -> Task:
        """Submit a shell command with minimal configuration.

        Args:
            command: Passed to the container shell.
            gpu: e.g. "a100", "a100:4", or "gpu:40gb". Ignored if `instance_type` is set.
            mounts: Optional data mounts (string or mapping of target->source).
            instance_type: Explicit override of the instance type.
            wait: If True, block until the task completes.

        Returns:
            Task.

        Examples:
            Quick usage with GPU shorthand:
                >>> task = flow.submit("python train.py", gpu="a100")

            Multiple mounts:
                >>> task = flow.submit(
                ...     "torchrun --nproc_per_node=4 train.py",
                ...     gpu="a100:4",
                ...     mounts={
                ...         "/data": "volume://datasets",
                ...         "/models": "s3://bucket/pretrained/",
                ...     },
                ...     wait=True,
                ... )
        """
        # Build config dict first, then create TaskConfig
        config_dict = {
            "name": f"flow-submit-{int(time.time())}",
            "command": command,
            "image": "ubuntu:24.04",
        }

        # Parse GPU specification and add to config dict
        if gpu and not instance_type:
            parsed_gpu = GPUParser().parse(gpu)

            # Match to instance type
            if not hasattr(self, "_instance_matcher"):
                # Load catalog (cached)
                catalog = self._load_instance_catalog()
                self._instance_matcher = InstanceMatcher(catalog)

            config_dict["instance_type"] = self._instance_matcher.match(parsed_gpu)

        elif instance_type:
            config_dict["instance_type"] = instance_type
        else:
            # No GPU or instance_type specified - let run() find any available instance
            # We'll set a dummy instance_type that run() will override
            config_dict["instance_type"] = "auto"

        # Convert mount URLs to volumes
        if mounts:
            if isinstance(mounts, str):
                # Single mount source auto-mounted
                if mounts.startswith("s3://"):
                    mounts = {"/data": mounts}
                elif mounts.startswith("volume://"):
                    mounts = {"/volumes": mounts}
                else:
                    mounts = {"/data": mounts}

            # Initialize resolver with volume loader
            resolver = URLResolver()
            resolver.add_loader("volume", VolumeLoader())

            volumes = []
            provider = self._ensure_provider()

            for target, url in mounts.items():
                spec = resolver.resolve(url, target, provider)

                # Convert MountSpec to VolumeSpec for existing API
                if spec.mount_type == "volume":
                    volume_spec = VolumeSpec(
                        volume_id=spec.options.get("volume_id"), mount_path=target
                    )
                    volumes.append(volume_spec)
                elif spec.mount_type == "s3fs":
                    # For S3, we pass mount info through environment variables
                    # Why: S3 requires runtime mounting (not provider-level) and
                    # credentials must be available in the instance for s3fs
                    if "env" not in config_dict:
                        config_dict["env"] = {}

                    # Pass AWS credentials from current environment
                    # Security: Only passes if already in env (user's responsibility)
                    if "AWS_ACCESS_KEY_ID" in os.environ:
                        config_dict["env"]["AWS_ACCESS_KEY_ID"] = os.environ["AWS_ACCESS_KEY_ID"]
                    if "AWS_SECRET_ACCESS_KEY" in os.environ:
                        config_dict["env"]["AWS_SECRET_ACCESS_KEY"] = os.environ[
                            "AWS_SECRET_ACCESS_KEY"
                        ]
                    if "AWS_SESSION_TOKEN" in os.environ:
                        config_dict["env"]["AWS_SESSION_TOKEN"] = os.environ["AWS_SESSION_TOKEN"]

                    # Pass S3 mount info through environment variables
                    s3_mount_index = sum(
                        1
                        for k in config_dict.get("env", {}).keys()
                        if k.startswith("S3_MOUNT_") and k.endswith("_BUCKET")
                    )
                    mount_key = f"S3_MOUNT_{s3_mount_index}"
                    config_dict["env"][f"{mount_key}_BUCKET"] = spec.options.get("bucket")
                    config_dict["env"][f"{mount_key}_PATH"] = spec.options.get("path", "")
                    config_dict["env"][f"{mount_key}_TARGET"] = target
                    config_dict["env"]["S3_MOUNTS_COUNT"] = str(s3_mount_index + 1)
                else:
                    # For now, only support volumes and s3
                    raise DataError(
                        f"Mount type '{spec.mount_type}' not yet supported",
                        suggestions=["Use volume:// or s3:// URLs"],
                    )

            config_dict["volumes"] = volumes

        # Create TaskConfig with all fields set
        config = TaskConfig(**config_dict)

        # Use existing run method
        return self.run(config, wait=wait)

    def _load_instance_catalog(self) -> list[CatalogEntry]:
        """Return the cached instance catalog; refresh on TTL expiry."""
        # Check cache with 5-minute TTL to avoid stale pricing
        cache_ttl = 300  # 5 minutes
        now = time.time()

        if (
            hasattr(self, "_catalog_cache")
            and hasattr(self, "_catalog_cache_time")
            and now - self._catalog_cache_time < cache_ttl
        ):
            return self._catalog_cache

        # Load from provider
        provider = self._ensure_provider()
        instances = provider.find_instances({}, limit=1000)

        # Convert to dict format for matcher
        catalog = []
        for inst in instances:
            # Provider must parse its own format
            if not hasattr(provider, "parse_catalog_instance"):
                raise FlowError(
                    "Provider does not support catalog parsing",
                    suggestions=[
                        "Provider must implement parse_catalog_instance() method",
                        "Update to a newer version of the provider",
                        "Contact provider maintainer for support",
                    ],
                )
            catalog_entry = provider.parse_catalog_instance(inst)
            catalog.append(catalog_entry)

        # Cache with timestamp
        self._catalog_cache = catalog
        self._catalog_cache_time = now
        return catalog

    def _resolve_data_mounts(self, mounts: str | dict[str, str]) -> list[MountSpec]:
        """Normalize `mounts` into `MountSpec` entries with sensible defaults."""
        from flow.api.models import MountSpec

        # Convert single string to dict format
        if isinstance(mounts, str):
            # Centralized auto-target resolution
            from flow.core.mount_rules import auto_target_for_source

            mounts = {auto_target_for_source(mounts): mounts}

        # Create MountSpec for each entry
        mount_specs = []
        for target, source in mounts.items():
            # Determine mount type based on source
            if source.startswith("s3://"):
                mount_type = "s3fs"
            elif source.startswith("volume://"):
                mount_type = "volume"
            else:
                mount_type = "bind"

            mount_specs.append(MountSpec(source=source, target=target, mount_type=mount_type))

        return mount_specs

    def get_provider_init(self) -> IProviderInit:
        """Return the provider's initialization interface."""
        provider = self._ensure_provider()
        return provider.get_init_interface()

    def list_projects(self) -> list[dict[str, str]]:
        """List provider projects accessible to the current credentials."""
        init_interface = self.get_provider_init()
        return init_interface.list_projects()

    def list_ssh_keys(self, project_id: str | None = None) -> list[dict[str, str]]:
        """List SSH keys (optionally filtered by project)."""
        init_interface = self.get_provider_init()
        return init_interface.list_ssh_keys(project_id)

    def get_ssh_key_manager(self):
        """Return the provider's SSH key manager interface."""
        provider = self._ensure_provider()
        if not hasattr(provider, "ssh_key_manager"):
            raise AttributeError(
                f"Provider {provider.__class__.__name__} doesn't support SSH key management"
            )
        return provider.ssh_key_manager

    def close(self) -> None:
        """Release provider resources (idempotent)."""
        if self._provider and hasattr(self._provider, "close"):
            self._provider.close()

    def __enter__(self) -> Flow:
        """Enter context manager (returns self)."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Exit context manager and close resources; do not suppress exceptions."""
        self.close()
        # Do not suppress exceptions
        return False
