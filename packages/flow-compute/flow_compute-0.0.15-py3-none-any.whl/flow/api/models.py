"""Core data models for Flow SDK.

This module defines the complete type system for GPU compute orchestration,
following Domain-Driven Design principles with immutable value objects and
rich domain entities. All models use Pydantic for validation, serialization,
and IDE support.

Model Categories:
    1. Enums: Task lifecycle states and resource types
    2. Hardware Specs: Immutable GPU/CPU/memory specifications
    3. Core Domain: TaskConfig, Task, Volume - primary API objects
    4. Configuration: SDK settings and project metadata
    5. Provider Mapping: Request/response DTOs for provider APIs

Examples:
    Basic task submission:
        >>> config = TaskConfig(
        ...     name="training-job",
        ...     instance_type="a100",  # Or "4xa100" for 4 GPUs
        ...     command=["python", "train.py", "--epochs", "10"],
        ...     max_price_per_hour=5.0
        ... )
        >>> task = flow.run(config)

    Capability-based GPU selection:
        >>> config = TaskConfig(
        ...     name="llm-inference",
        ...     min_gpu_memory_gb=40,  # A100-40GB or better
        ...     command="python serve.py",
        ...     max_price_per_hour=10.0
        ... )

    Persistent volume management:
        >>> volume = VolumeSpec(
        ...     size_gb=1000,
        ...     mount_path="/data",
        ...     name="training-datasets"
        ... )
        >>> config.volumes = [volume]
"""

import logging
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterator, List, Literal, Optional, Set, Union
from uuid import NAMESPACE_DNS, UUID, uuid5

import yaml
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, field_validator, model_validator

from flow.errors import FlowError

logger = logging.getLogger(__name__)


# ================== Section 1: Common Enums ==================


class Retries(BaseModel):
    """Advanced retry configuration for task execution.

    Provides fine-grained control over retry behavior with exponential
    backoff, jitter, and failure handling. Compatible with provider
    retry mechanisms.

    Retry behavior:
        - On failure, wait initial_delay seconds before first retry
        - Each subsequent retry multiplies delay by backoff_coefficient
        - Maximum delay is capped at max_delay
        - Total retries limited by max_retries

    Examples:
        Fixed interval retries:
            >>> Retries(max_retries=3, backoff_coefficient=1.0, initial_delay=5.0)
            # Retries at: 5s, 5s, 5s

        Exponential backoff:
            >>> Retries(max_retries=4, backoff_coefficient=2.0, initial_delay=1.0)
            # Retries at: 1s, 2s, 4s, 8s

        With maximum delay cap:
            >>> Retries(max_retries=5, backoff_coefficient=3.0,
            ...         initial_delay=1.0, max_delay=10.0)
            # Retries at: 1s, 3s, 9s, 10s, 10s (capped)
    """

    max_retries: int = Field(3, ge=0, le=10, description="Maximum retry attempts (0-10)")
    backoff_coefficient: float = Field(
        2.0, ge=1.0, le=10.0, description="Delay multiplier between retries"
    )
    initial_delay: float = Field(
        1.0, ge=0.1, le=300.0, description="Initial delay in seconds before first retry"
    )
    max_delay: Optional[float] = Field(
        None, ge=1.0, le=3600.0, description="Maximum delay between retries (seconds)"
    )

    @model_validator(mode="after")
    def validate_delays(self) -> "Retries":
        """Ensure max_delay is greater than initial_delay if set."""
        if self.max_delay is not None and self.max_delay < self.initial_delay:
            raise ValueError(
                f"max_delay ({self.max_delay}s) must be >= initial_delay ({self.initial_delay}s)"
            )
        return self

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for a given retry attempt.

        Args:
            attempt: Retry attempt number (1-based)

        Returns:
            Delay in seconds before this retry attempt
        """
        if attempt <= 0:
            return 0.0

        # Calculate exponential backoff
        delay = self.initial_delay * (self.backoff_coefficient ** (attempt - 1))

        # Apply max_delay cap if set
        if self.max_delay is not None:
            delay = min(delay, self.max_delay)

        return delay

    @classmethod
    def fixed(cls, retries: int = 3, delay: float = 5.0) -> "Retries":
        """Create fixed-interval retry configuration.

        Args:
            retries: Number of retry attempts
            delay: Fixed delay between retries (seconds)

        Returns:
            Retries with fixed intervals

        Example:
            >>> retry = Retries.fixed(retries=5, delay=10.0)
            # Retries every 10 seconds, up to 5 times
        """
        return cls(max_retries=retries, backoff_coefficient=1.0, initial_delay=delay)

    @classmethod
    def exponential(
        cls,
        retries: int = 3,
        initial: float = 1.0,
        multiplier: float = 2.0,
        max_delay: Optional[float] = None,
    ) -> "Retries":
        """Create exponential backoff retry configuration.

        Args:
            retries: Number of retry attempts
            initial: Initial delay (seconds)
            multiplier: Delay multiplier for each retry
            max_delay: Maximum delay cap (seconds)

        Returns:
            Retries with exponential backoff

        Example:
            >>> retry = Retries.exponential(
            ...     retries=4,
            ...     initial=2.0,
            ...     multiplier=3.0,
            ...     max_delay=60.0
            ... )
            # Delays: 2s, 6s, 18s, 54s
        """
        return cls(
            max_retries=retries,
            backoff_coefficient=multiplier,
            initial_delay=initial,
            max_delay=max_delay,
        )


class TaskStatus(str, Enum):
    """Task execution lifecycle states.

    Represents the complete lifecycle of a GPU workload from submission
    to termination. States follow a directed acyclic graph with clear
    transition rules enforced by providers.

    State Transitions:
        PENDING → RUNNING → COMPLETED (exit 0)
                ↘       ↘→ FAILED (non-zero exit)
                        ↘→ CANCELLED (user action)
                        ↘→ PREEMPTING → CANCELLED (provider preemption)
                        ↘→ PAUSED ↘→ RUNNING (maintenance/operations)

    Attributes:
        PENDING: Submitted, awaiting resource allocation
        RUNNING: Executing on provisioned GPU instance (billing active)
        PAUSED: Resources allocated but temporarily stopped (billing paused)
        PREEMPTING: Running but will be terminated soon by cloud provider
        COMPLETED: Finished successfully with exit code 0
        FAILED: Terminated with error (non-zero exit or system failure)
        CANCELLED: Terminated by user request or provider preemption

    Terminal States:
        COMPLETED, FAILED, CANCELLED are terminal (no further transitions)

    Example:
        >>> task = flow.run(config)
        >>> while task.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
        ...     print(f"Status: {task.status}")
        ...     if task.status == TaskStatus.PREEMPTING:
        ...         print("WARNING: Instance will be preempted soon!")
        ...     time.sleep(5)
        ...     task.refresh()
    """

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    PREEMPTING = "preempting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class InstanceStatus(str, Enum):
    """Status of a compute instance."""

    PENDING = "pending"
    RUNNING = "running"
    STOPPED = "stopped"
    TERMINATED = "terminated"


class StorageInterface(str, Enum):
    """Storage interface type."""

    BLOCK = "block"
    FILE = "file"


# ================== Section 2: Hardware Specifications ==================


class GPUSpec(BaseModel):
    """Immutable GPU hardware specification.

    Comprehensive GPU characteristics for capability matching, cost
    optimization, and performance modeling. All fields are frozen
    after initialization to ensure thread safety.

    Used by the instance matching system to find suitable hardware
    based on workload requirements. Supports comparison operators
    for ranking GPUs by capability.
    """

    model_config = ConfigDict(frozen=True)

    vendor: str = Field(default="NVIDIA", description="GPU vendor")
    model: str = Field(..., description="GPU model (e.g., A100, H100)")
    memory_gb: int = Field(..., gt=0, description="GPU memory in GB")
    memory_type: str = Field(default="", description="Memory type (HBM2e, HBM3, GDDR6)")
    architecture: str = Field(default="", description="GPU architecture (Ampere, Hopper)")
    compute_capability: tuple[int, int] = Field(
        default=(0, 0), description="CUDA compute capability"
    )
    tflops_fp32: float = Field(default=0.0, ge=0, description="FP32 performance in TFLOPS")
    tflops_fp16: float = Field(default=0.0, ge=0, description="FP16 performance in TFLOPS")
    memory_bandwidth_gb_s: float = Field(default=0.0, ge=0, description="Memory bandwidth in GB/s")

    @property
    def canonical_name(self) -> str:
        """Canonical name: nvidia-a100-80gb."""
        return f"{self.vendor}-{self.model}-{self.memory_gb}gb".lower()

    @property
    def display_name(self) -> str:
        """Human-friendly name: NVIDIA A100 80GB."""
        return f"{self.vendor} {self.model.upper()} {self.memory_gb}GB"


class CPUSpec(BaseModel):
    """CPU specification."""

    model_config = ConfigDict(frozen=True)

    vendor: str = Field(default="Intel", description="CPU vendor")
    model: str = Field(default="Xeon", description="CPU model")
    cores: int = Field(..., gt=0, description="Number of CPU cores")
    threads: int = Field(default=0, ge=0, description="Number of threads (0 = same as cores)")
    base_clock_ghz: float = Field(default=0.0, ge=0, description="Base clock speed in GHz")

    @model_validator(mode="after")
    def set_threads_default(self) -> "CPUSpec":
        """Set threads to cores if not specified."""
        if self.threads == 0:
            object.__setattr__(self, "threads", self.cores)
        return self


class MemorySpec(BaseModel):
    """System memory specification."""

    model_config = ConfigDict(frozen=True)

    size_gb: int = Field(..., gt=0, description="Memory size in GB")
    type: str = Field(default="DDR4", description="Memory type")
    speed_mhz: int = Field(default=3200, gt=0, description="Memory speed in MHz")
    ecc: bool = Field(default=True, description="ECC memory support")


class StorageSpec(BaseModel):
    """Storage specification."""

    model_config = ConfigDict(frozen=True)

    size_gb: int = Field(..., ge=0, description="Storage size in GB")
    type: str = Field(default="NVMe", description="Storage type (NVMe, SSD, HDD)")
    iops: Optional[int] = Field(default=None, ge=0, description="IOPS rating")
    bandwidth_mb_s: Optional[int] = Field(default=None, ge=0, description="Bandwidth in MB/s")


class NetworkSpec(BaseModel):
    """Network specification."""

    model_config = ConfigDict(frozen=True)

    intranode: str = Field(default="", description="Intra-node interconnect (SXM4, SXM5, PCIe)")
    internode: Optional[str] = Field(
        default=None, description="Inter-node network (InfiniBand, Ethernet)"
    )
    bandwidth_gbps: Optional[float] = Field(
        default=None, ge=0, description="Network bandwidth in Gbps"
    )

    @property
    def has_high_speed_interconnect(self) -> bool:
        """Check if this has high-speed interconnect."""
        return self.internode in {"InfiniBand", "IB", "IB_1600", "IB_3200"}


class InstanceType(BaseModel):
    """Canonical instance type specification.

    Single source of truth for hardware capabilities. Immutable for thread safety.
    """

    model_config = ConfigDict(frozen=True)

    # Hardware specifications
    gpu: GPUSpec
    gpu_count: int = Field(..., gt=0, description="Number of GPUs")
    cpu: CPUSpec
    memory: MemorySpec
    storage: StorageSpec
    network: NetworkSpec

    # Identity and metadata
    id: Optional[UUID] = Field(default=None, description="Unique instance type ID")
    aliases: Set[str] = Field(default_factory=set, description="Alternative names")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def compute_id_and_aliases(self) -> "InstanceType":
        """Compute ID and generate aliases."""
        # Generate stable UUID from content
        content = self._canonical_string()
        if not self.id:
            object.__setattr__(self, "id", uuid5(NAMESPACE_DNS, content))

        # Generate default aliases if none provided
        if not self.aliases:
            object.__setattr__(self, "aliases", self._generate_aliases())

        return self

    def _canonical_string(self) -> str:
        """Generate canonical string representation for hashing."""
        parts = [
            f"gpu:{self.gpu.vendor}-{self.gpu.model}-{self.gpu.memory_gb}gb",
            f"count:{self.gpu_count}",
            f"cpu:{self.cpu.cores}",
            f"mem:{self.memory.size_gb}",
            f"net:{self.network.intranode}-{self.network.internode}",
        ]
        return "|".join(parts)

    def _generate_aliases(self) -> Set[str]:
        """Generate common aliases for this instance type."""
        aliases = set()

        # API style: gpu.nvidia.a100
        api_style = f"gpu.{self.gpu.vendor.lower()}.{self.gpu.model.lower()}"
        aliases.add(api_style)

        # Short form: a100-80gb
        short_form = f"{self.gpu.model.lower()}-{self.gpu.memory_gb}gb"
        aliases.add(short_form)

        # With count: 8xa100
        with_count = f"{self.gpu_count}x{self.gpu.model.lower()}"
        aliases.add(with_count)

        return aliases

    @property
    def canonical_name(self) -> str:
        """Canonical name following consistent convention."""
        return f"gpu.{self.gpu.vendor.lower()}.{self.gpu.model.lower()}"

    @property
    def display_name(self) -> str:
        """Human-friendly display name."""
        return f"{self.gpu_count}x {self.gpu.display_name}"

    @property
    def total_gpu_memory_gb(self) -> int:
        """Total GPU memory across all GPUs."""
        return self.gpu.memory_gb * self.gpu_count

    @property
    def total_tflops_fp32(self) -> float:
        """Total FP32 compute power."""
        return self.gpu.tflops_fp32 * self.gpu_count


class InstanceMatch(BaseModel):
    """Result of matching an instance with pricing/availability."""

    instance: InstanceType
    region: str
    availability: int = Field(..., ge=0, description="Number of available instances")
    price_per_hour: float = Field(..., ge=0, description="Price in USD per hour")
    match_score: float = Field(default=1.0, ge=0, le=1.0, description="Match quality score")

    @property
    def price_performance(self) -> float:
        """TFLOPS per dollar."""
        if self.price_per_hour > 0:
            return self.instance.total_tflops_fp32 / self.price_per_hour
        return 0.0


# ================== Section 3: Core Domain Models ==================


class User(BaseModel):
    """User identity information.

    Human-readable details resolved from opaque user IDs.
    """

    user_id: str = Field(..., description="Unique user identifier (e.g., 'user_kfV4CCaapLiqCNlv')")
    username: str = Field(..., description="Username for display")
    email: str = Field(..., description="User email address")
    # Future fields: full_name, organization, created_at


class VolumeSpec(BaseModel):
    """Persistent storage volume specification.

    Defines block storage for data persistence across task lifecycles.
    Supports both creating new volumes and attaching existing ones.
    Volumes are project-scoped and region-specific.

    Volume Lifecycle:
        1. Create: New volume with specified size
        2. Attach: Mount to task at specified path
        3. Detach: Automatic on task completion
        4. Delete: Explicit deletion required

    Performance Tiers (via iops/throughput):
        - Standard: 3 IOPS/GB, 125 MB/s baseline
        - Performance: Up to 64,000 IOPS, 1000 MB/s

    Best Practices:
        - Mount at /var/lib/docker for layer cache persistence
        - Use descriptive names for team collaboration
        - Set IOPS only for database workloads
        - Size for growth (no online expansion)
    """

    model_config = ConfigDict(extra="forbid")

    # Human-friendly name
    name: Optional[str] = Field(
        None,
        description="Human-readable name (3-64 chars, lowercase alphanumeric with hyphens)",
        pattern="^[a-z0-9][a-z0-9-]*[a-z0-9]$",
        min_length=3,
        max_length=64,
    )

    # Core fields
    size_gb: int = Field(1, ge=1, le=15000, description="Size in GB")
    mount_path: str = Field("/data", description="Mount path in container")

    # Volume ID for existing volumes
    volume_id: Optional[str] = Field(None, description="ID of existing volume to attach")

    # Advanced options
    interface: StorageInterface = Field(
        StorageInterface.BLOCK, description="Storage interface type"
    )
    iops: Optional[int] = Field(None, ge=100, le=64000, description="Provisioned IOPS")
    throughput_mb_s: Optional[int] = Field(
        None, ge=125, le=1000, description="Provisioned throughput"
    )

    @model_validator(mode="after")
    def validate_volume_spec(self) -> "VolumeSpec":
        """Validate volume specification."""
        if self.volume_id and (self.iops or self.throughput_mb_s):
            raise ValueError("Cannot specify IOPS/throughput for existing volumes")
        return self


class MountSpec(BaseModel):
    """Provider-agnostic mount specification.

    Abstracts volumes, S3, HTTP, and other data sources.
    """

    source: str = Field(..., description="Source URL or path")
    target: str = Field(..., description="Mount path in container")
    mount_type: Literal["bind", "volume", "s3fs"] = Field("bind", description="Type of mount")
    options: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific options")

    # Performance hints
    cache_key: Optional[str] = Field(None, description="Key for caching mount metadata")
    size_estimate_gb: Optional[float] = Field(None, ge=0, description="Estimated size for planning")


class TaskConfig(BaseModel):
    """Complete task execution specification.

    Primary configuration object defining all aspects of GPU workload
    execution. Designed for minimal boilerplate with sensible defaults
    while enabling full control when needed.

    Configuration Philosophy:
        - Explicit over implicit behavior
        - Fail-fast validation at configuration time
        - One obvious way to specify requirements
        - Progressive disclosure of advanced features

    Required Fields:
        - Instance: instance_type OR min_gpu_memory_gb

    Optional Fields:
        - Command: defaults to 'sleep infinity' for interactive devbox use

    Common Patterns:
        - Single GPU: instance_type="a100"
        - Multi-GPU: instance_type="4xa100" or "8xh100"
        - Flexible: min_gpu_memory_gb=40 (gets cheapest)
        - Cost cap: max_price_per_hour=10.0
        - Time limit: max_run_time_hours=24.0
        - Min runtime: min_run_time_hours=2.0 (guaranteed minimum)
        - Deadline: deadline_hours=4.0 (due in 4 hours)

    Validation Rules:
        - Name: alphanumeric with dash/underscore
        - Volumes: size_gb if new, volume_id if existing
        - Runtime: max 168 hours (7 days)
        - Min runtime: must be less than max_run_time_hours if both specified
        - Deadline: positive hours from submission
        - Price: positive USD amount
        - SSH keys: must exist in project

    """

    model_config = ConfigDict(extra="forbid")

    # Basic configuration
    name: str = Field(
        "flow-task", description="Task identifier", pattern="^[a-zA-Z0-9][a-zA-Z0-9-_]*$"
    )
    unique_name: bool = Field(True, description="Append unique suffix to name to ensure uniqueness")

    # Instance specification - either explicit type or capability-based
    instance_type: Optional[str] = Field(None, description="Explicit instance type")
    min_gpu_memory_gb: Optional[int] = Field(
        None, ge=1, le=640, description="Minimum GPU memory requirement"
    )

    # Command specification - accepts string, list, or multi-line script
    command: Optional[Union[str, List[str]]] = Field(
        None, description="Command to execute (string, list, or script)"
    )

    # Environment
    image: str = Field("nvidia/cuda:12.1.0-runtime-ubuntu22.04", description="Container image")
    env: Dict[str, str] = Field(default_factory=dict, description="Environment")
    working_dir: str = Field("/workspace", description="Container working directory")

    # Resources
    volumes: List[Union[VolumeSpec, Dict[str, Any]]] = Field(default_factory=list)
    data_mounts: List[MountSpec] = Field(default_factory=list, description="Data to mount")

    # Execution options
    max_price_per_hour: Optional[float] = Field(
        None, gt=0, description="Maximum hourly price (USD)"
    )
    max_run_time_hours: Optional[float] = Field(
        None, gt=0, le=168, description="Maximum runtime hours (default: None)"
    )
    min_run_time_hours: Optional[float] = Field(
        None, gt=0, description="Minimum guaranteed runtime hours"
    )
    deadline_hours: Optional[float] = Field(
        None, gt=0, le=168, description="Hours from submission until deadline"
    )

    # SSH and access
    ssh_keys: List[str] = Field(default_factory=list, description="Authorized SSH key IDs")

    # Advanced options
    region: Optional[str] = Field(None, description="Target region")
    num_instances: int = Field(1, ge=1, le=100, description="Instance count")
    priority: Literal["low", "med", "high"] = Field(
        "med", description="Task priority tier affecting limit price"
    )
    upload_code: bool = Field(True, description="Upload current directory code to job")
    upload_strategy: Literal["auto", "embedded", "scp", "none"] = Field(
        "auto",
        description=(
            "Strategy for uploading code to instances:\n"
            "  - auto: Use SCP for large (>8KB), embedded for small\n"
            "  - embedded: Include in startup script (10KB limit)\n"
            "  - scp: Transfer after instance starts (no size limit)\n"
            "  - none: No code upload"
        ),
    )
    upload_timeout: int = Field(
        600, ge=60, le=3600, description="Maximum seconds to wait for code upload (60-3600)"
    )

    @field_validator("command", mode="before")
    def normalize_command(cls, v: Any) -> Union[str, List[str]]:
        """Normalize command input while preserving original form.

        This validator accepts strings and lists but doesn't transform them,
        allowing downstream code to handle different command types appropriately.
        Multi-line scripts, shell commands, and argv arrays are all preserved.

        Args:
            v: Command specification:
                - str: Single-line command or multi-line script
                - List[str]: Argv array for exec form

        Returns:
            Union[str, List[str]]: Original command form preserved

        Examples:
            "python train.py" → "python train.py" (string preserved)
            ["python", "train.py"] → ["python", "train.py"] (list preserved)
            "#!/bin/bash\n..." → "#!/bin/bash\n..." (script preserved)

        Note: Downstream code detects command type to apply appropriate execution strategy.
        """
        # Accept both strings and lists without transformation
        if isinstance(v, (str, list)):
            return v
        return v

    @field_validator("volumes", mode="before")
    def normalize_volumes(cls, v: Any) -> List[VolumeSpec]:
        """Convert volume dictionaries to VolumeSpec objects.

        Enables flexible volume specification in YAML/JSON configs
        while maintaining type safety in the domain model.

        Args:
            v: List of volume specifications, each either:
                - VolumeSpec: Already typed (passed through)
                - dict: Raw config to convert

        Returns:
            List[VolumeSpec]: Typed volume specifications

        Example:
            Input: [{"size_gb": 100, "mount_path": "/data"}]
            Output: [VolumeSpec(size_gb=100, mount_path="/data")]
        """
        result = []
        for vol in v:
            if isinstance(vol, dict):
                result.append(VolumeSpec(**vol))
            else:
                result.append(vol)
        return result

    @model_validator(mode="after")
    def validate_config(self) -> "TaskConfig":
        """Enforce TaskConfig business rules and mutual exclusions.

        Validates that the configuration represents a coherent,
        executable workload specification. Fails fast with clear
        error messages to prevent runtime failures.

        Validation Rules:
            1. Command specification:
               - Optional - defaults to 'sleep infinity' for interactive use
               - Supports string, list, or multi-line script

            2. Instance specification (mutually exclusive):
               - Exactly ONE of: instance_type, min_gpu_memory_gb
               - instance_type: Direct instance selection
               - min_gpu_memory_gb: Capability-based selection

            3. Volume consistency:
               - volume_id XOR (size_gb + name)
               - No IOPS settings for existing volumes

            4. Resource limits:
               - max_run_time_hours ≤ 168 (7 days)
               - min_run_time_hours < max_run_time_hours (if both set)
               - deadline_hours >= max_run_time_hours (if both set)
               - num_instances ≤ 100
               - max_price_per_hour > 0 (if set)

        Raises:
            ValueError: Configuration violates business rules
        """
        # Default command for interactive/devbox use
        if not self.command:
            self.command = "sleep infinity"

        # Handle unique_name field by appending UUID suffix
        if self.unique_name:
            import uuid

            suffix = uuid.uuid4().hex[:6]
            self.name = f"{self.name}-{suffix}"

        # Validate instance specification
        if self.instance_type and self.min_gpu_memory_gb:
            raise ValueError(
                "Cannot specify both instance_type and min_gpu_memory_gb. Choose one:\n"
                "  instance_type='a100' (specific GPU)\n"
                "  min_gpu_memory_gb=40 (any GPU with 40GB+)"
            )
        if not self.instance_type and not self.min_gpu_memory_gb:
            raise ValueError(
                "Must specify either instance_type or min_gpu_memory_gb:\n"
                "  instance_type='a100' or '4xa100' or 'h100'\n"
                "  min_gpu_memory_gb=24, 40, or 80"
            )

        # Validate runtime constraints
        if self.min_run_time_hours and self.max_run_time_hours:
            if self.min_run_time_hours > self.max_run_time_hours:
                raise ValueError(
                    f"min_run_time_hours ({self.min_run_time_hours}) cannot exceed "
                    f"max_run_time_hours ({self.max_run_time_hours})"
                )

        # Validate deadline makes sense with max_run_time
        if self.deadline_hours and self.max_run_time_hours:
            if self.deadline_hours < self.max_run_time_hours:
                raise ValueError(
                    f"deadline_hours ({self.deadline_hours}) should be >= "
                    f"max_run_time_hours ({self.max_run_time_hours})"
                )

        return self

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> "TaskConfig":
        """Load task configuration from YAML file.

        Parses YAML configuration with full validation and type conversion.
        Supports all TaskConfig fields in YAML format.

        Args:
            path: Path to YAML configuration file

        Returns:
            TaskConfig: Validated configuration object

        Raises:
            FileNotFoundError: Configuration file not found
            yaml.YAMLError: Invalid YAML syntax
            ValidationError: Configuration validation failed

        Example YAML:
            ```yaml
            name: distributed-training
            instance_type: 8xa100
            command: python train.py --distributed
            env:
              BATCH_SIZE: "256"
              WORLD_SIZE: "8"
            volumes:
              - size_gb: 1000
                mount_path: /data
                name: training-data
            max_price_per_hour: 50.0
            max_run_time_hours: 24.0
            ```
        """
        from flow.errors import ConfigParserError

        try:
            with open(path) as f:
                data = yaml.safe_load(f)
                if not isinstance(data, dict):
                    raise ConfigParserError(
                        f"Task configuration must be a YAML dictionary, got {type(data).__name__}",
                        suggestions=[
                            "Ensure your YAML file contains key: value pairs",
                            "Example: instance_type: 'A100-40GB'",
                            f"Check the structure of {path}",
                        ],
                        error_code="CONFIG_003",
                    )
        except yaml.YAMLError as e:
            raise ConfigParserError(
                f"Invalid YAML syntax in task configuration {path}: {str(e)}",
                suggestions=[
                    "Check YAML indentation (use spaces, not tabs)",
                    "Ensure all GPU types are quoted (e.g., 'A100-40GB')",
                    "Validate syntax at yamllint.com",
                ],
                error_code="CONFIG_001",
            ) from e

        return cls(**data)

    def to_yaml(self, path: Union[str, Path]) -> None:
        """Save configuration to YAML file."""
        with open(path, "w") as f:
            yaml.dump(self.model_dump(exclude_none=True), f, sort_keys=False)


class Task(BaseModel):
    """Active task execution handle.

    Rich domain object providing complete lifecycle management for GPU
    workloads. Returned by flow.run() and flow.get_task(), this is the
    primary interface for task monitoring and control.

    Lifecycle Methods:
        - refresh(): Update status from provider
        - wait(timeout): Block until completion
        - cancel(): Request graceful termination
        - logs(follow=True): Stream output in real-time
        - ssh(): Open interactive shell session

    Properties:
        - is_running: Currently executing
        - is_terminal: Completed/failed/cancelled
        - public_ip: Primary instance IP (if available)

    Extended Information:
        - get_user(): Resolve task creator details
        - get_instances(): Multi-node instance details

    Thread Safety:
        Methods are NOT thread-safe. Use one Task instance per thread
        or implement external synchronization.

    Example:
        >>> task = flow.run(config)
        >>> task.wait()  # Block until running
        >>>
        >>> # Stream logs
        >>> for line in task.logs(follow=True):
        ...     if "ERROR" in line:
        ...         task.cancel()
        ...         break
        >>>
        >>> # Interactive debugging
        >>> if task.is_running:
        ...     task.ssh()
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    task_id: str = Field(..., description="Task UUID")
    name: str = Field(..., description="Human-readable name")
    status: TaskStatus = Field(..., description="Execution state")
    config: Optional[TaskConfig] = Field(None, description="Original configuration")

    # Timestamps
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    instance_created_at: Optional[datetime] = Field(
        None, description="Creation time of current instance (for preempted/restarted tasks)"
    )

    # Resources
    instance_type: str
    num_instances: int
    region: str

    # Cost information
    cost_per_hour: str = Field(..., description="Hourly cost")
    total_cost: Optional[str] = Field(None, description="Accumulated cost")

    # User information
    created_by: Optional[str] = Field(None, description="Creator user ID")

    # Access information
    ssh_host: Optional[str] = Field(None, description="SSH endpoint")
    ssh_port: Optional[int] = Field(22, description="SSH port")
    ssh_user: str = Field("ubuntu", description="SSH user")
    shell_command: Optional[str] = Field(None, description="Complete shell command")

    # Endpoints and runtime info
    endpoints: Dict[str, str] = Field(default_factory=dict, description="Exposed service URLs")
    instances: List[str] = Field(default_factory=list, description="Instance identifiers")
    message: Optional[str] = Field(None, description="Human-readable status")

    # Provider-specific metadata
    provider_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Provider-specific state and metadata (e.g., Mithril bid status, preemption reasons)",
    )

    # Provider reference (for method implementations)
    _provider: Optional[object] = PrivateAttr(default=None)

    # Cached user information
    _user: Optional[User] = PrivateAttr(default=None)

    @property
    def is_running(self) -> bool:
        """Check if task is currently running."""
        return self.status == TaskStatus.RUNNING

    @property
    def instance_status(self) -> Optional[str]:
        """Get the instance provisioning status from provider metadata.

        Returns the raw instance status (e.g., STATUS_STARTING, STATUS_RUNNING)
        which is distinct from the task status. This allows showing more
        granular provisioning states.
        """
        return self.provider_metadata.get("instance_status")

    @property
    def instance_age_seconds(self) -> Optional[float]:
        """Get age of current instance in seconds (for SSH diagnostics).

        Returns instance_created_at age if available (for preempted/restarted tasks),
        otherwise falls back to task created_at.
        """
        from datetime import datetime, timezone

        if self.instance_created_at:
            return (datetime.now(timezone.utc) - self.instance_created_at).total_seconds()
        elif self.created_at:
            return (datetime.now(timezone.utc) - self.created_at).total_seconds()
        return None

    @property
    def is_terminal(self) -> bool:
        """Check if task is in a terminal state."""
        return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]

    @property
    def has_ssh_access(self) -> bool:
        """Check if task has SSH access configured."""
        return bool(self.ssh_host and self.shell_command)

    @property
    def ssh_keys_configured(self) -> bool:
        """Check if task was submitted with SSH keys (even if not yet accessible)."""
        return bool(self.config and self.config.ssh_keys) if self.config else False

    @property
    def host(self) -> Optional[str]:
        """Get the primary host address for the task."""
        return self.ssh_host

    @property
    def capabilities(self) -> Dict[str, bool]:
        """Task capabilities based on configuration."""
        return {
            "ssh": self.has_ssh_access,
            "logs": self.has_ssh_access,  # Currently logs require SSH
            "interactive": self.has_ssh_access,
        }

    def logs(
        self, follow: bool = False, tail: int = 100, stderr: bool = False
    ) -> Union[str, Iterator[str]]:
        """Retrieve or stream task output logs.

        Provides both historical retrieval and real-time streaming of
        task stdout/stderr. Streaming includes automatic reconnection
        on network failures.

        Args:
            follow: Enable real-time streaming. When True, returns an
                iterator that yields new lines as they arrive. When False,
                returns a string with recent history.
            tail: Number of most recent lines to retrieve (follow=False only).
                Useful for getting just the end of long outputs.

        Returns:
            Union[str, Iterator[str]]:
                - follow=False: String with last 'tail' lines
                - follow=True: Iterator yielding lines in real-time

        Raises:
            RuntimeError: Task not connected to provider (shouldn't happen
                in normal usage as Task objects come from provider)

        Example:
            >>> # Get recent output
            >>> print(task.logs(tail=50))

            >>> # Stream until completion
            >>> for line in task.logs(follow=True):
            ...     if "loss:" in line:
            ...         print(line.strip())
            ...     if task.is_terminal:
            ...         break
        """
        if not self._provider:
            raise RuntimeError("Task not connected to provider")

        if follow:
            return self._provider.stream_task_logs(
                self.task_id, log_type="stderr" if stderr else "stdout"
            )
        else:
            return self._provider.get_task_logs(
                self.task_id, tail=tail, log_type="stderr" if stderr else "stdout"
            )

    def wait(self, timeout: Optional[int] = None) -> None:
        """Block until task reaches terminal state.

        Synchronously waits for task completion, failure, or cancellation.
        Polls status at regular intervals and updates local state.

        Args:
            timeout: Maximum seconds to wait. None waits indefinitely.
                Common values:
                - 60: Quick jobs
                - 3600: Standard training (1 hour)
                - 86400: Long runs (24 hours)

        Raises:
            TimeoutError: Task didn't reach terminal state within timeout.
                Task continues running; call cancel() to stop it.

        Polling:
            - Interval: 2 seconds (balanced for responsiveness vs API load)
            - Automatic refresh() updates local state
            - Network failures silently retried

        Example:
            >>> # Wait with timeout and error handling
            >>> try:
            ...     task.wait(timeout=3600)  # 1 hour max
            ...     if task.status == TaskStatus.FAILED:
            ...         print(f"Task failed: {task.logs(tail=50)}")
            ... except TimeoutError:
            ...     print("Task taking too long, cancelling...")
            ...     task.cancel()
        """
        import time

        start_time = time.time()

        while not self.is_terminal:
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Task {self.task_id} did not complete within {timeout} seconds")
            time.sleep(2)
            if self._provider:
                self.refresh()

    def refresh(self) -> None:
        """Synchronize state with provider."""
        if not self._provider:
            raise RuntimeError("Task not connected to provider")

        updated = self._provider.get_task(self.task_id)
        for field in self.model_fields:
            if hasattr(updated, field) and field != "_provider":
                setattr(self, field, getattr(updated, field))

    def stop(self) -> None:
        """Terminate task execution."""
        if not self._provider:
            raise RuntimeError("Task not connected to provider")
        self._provider.stop_task(self.task_id)
        self.status = TaskStatus.CANCELLED

    def cancel(self) -> None:
        """Alias for stop()."""
        self.stop()

    @property
    def public_ip(self) -> Optional[str]:
        """Primary instance public IP.

        For multi-instance tasks, use get_instances().
        """
        if self.ssh_host and self._is_ip_address(self.ssh_host):
            return self.ssh_host
        return None

    def _is_ip_address(self, host: str) -> bool:
        """Validate IP address format."""
        try:
            import ipaddress

            ipaddress.ip_address(host)
            return True
        except ValueError:
            return False

    def get_instances(self) -> List["Instance"]:
        """Fetch detailed instance information.

        Returns Instance objects with IP addresses for multi-node coordination.
        """
        if not self._provider:
            raise FlowError("No provider available for instance resolution")

        return self._provider.get_task_instances(self.task_id)

    def get_user(self) -> Optional[User]:
        """Resolve task creator details.

        Cached after first call. Returns None on error.
        """
        if not self.created_by:
            return None
        if self._user:
            return self._user
        if not self._provider:
            logger.debug(f"Cannot fetch user for task {self.task_id}: no provider")
            return None
        try:
            self._user = self._provider.get_user(self.created_by)
            return self._user
        except Exception as e:
            logger.warning(f"Failed to fetch user {self.created_by}: {e}")
            return None

    def result(self) -> Any:
        """Retrieve function execution result from remote task.

        Fetches the result JSON file created by decorator-wrapped functions.
        Uses provider-specific remote operations to retrieve the result.

        Returns:
            The function's return value if successful, or raises an exception
            if the function failed.

        Raises:
            FlowError: If result cannot be retrieved (task not completed,
                remote access unavailable, result file missing)
            Exception: The original exception from the remote function if it failed

        Example:
            >>> @app.function(gpu="a100")
            ... def compute(x: int) -> dict:
            ...     return {"result": x * 2}
            >>>
            >>> task = compute.remote(5)
            >>> task.wait()
            >>> result = task.result()  # {"result": 10}
        """
        import json

        if not self.is_terminal:
            raise FlowError(
                f"Cannot retrieve result from task in {self.status} state",
                suggestions=[
                    "Wait for task to complete with task.wait()",
                    "Check task status with task.status",
                    "Results are only available after task completes",
                ],
            )

        if not self._provider:
            raise RuntimeError("Task not connected to provider")

        remote_ops = self._provider.get_remote_operations()
        if not remote_ops:
            raise FlowError(
                "Provider does not support remote operations",
                suggestions=[
                    "This provider does not support result retrieval",
                    "Use a provider that implements remote operations",
                    "Store results in cloud storage or volumes instead",
                ],
            )

        try:
            # Use provider's remote operations to retrieve the file
            result_data = remote_ops.retrieve_file(self.task_id, "/tmp/flow_result.json")
            result_json = json.loads(result_data.decode("utf-8"))

            # Support both current and legacy error formats
            success = result_json.get("success")
            has_error_field = "error" in result_json
            if success is False or has_error_field:
                error_field = result_json.get("error")

                # Normalize to type/message/traceback
                if isinstance(error_field, dict):
                    err_type = error_field.get("type") or error_field.get("error_type") or "Unknown"
                    message = error_field.get("message") or error_field.get("error") or "No message"
                    tb = error_field.get("traceback")
                else:
                    message = str(error_field) if error_field is not None else "Unknown error"
                    err_type = result_json.get("error_type", "Unknown")
                    tb = result_json.get("traceback")

                suggestions = [
                    "Check the full traceback in task logs",
                    "Use task.logs() to see the complete error",
                ]
                if tb:
                    # Provide a short tail of the traceback for convenience
                    try:
                        tail = "\n".join(tb.strip().splitlines()[-5:])
                        suggestions.append(f"Traceback (last lines):\n{tail}")
                    except Exception:
                        pass

                raise FlowError(
                    f"Remote function failed: {err_type}: {message}",
                    suggestions=suggestions,
                )

            return result_json.get("result")

        except FileNotFoundError:
            raise FlowError(
                "Result file not found on remote instance",
                suggestions=[
                    "The function may not have completed successfully",
                    "Check task logs with task.logs() for errors",
                    "Ensure your function is wrapped with @app.function decorator",
                ],
            )
        except json.JSONDecodeError as e:
            raise FlowError(
                "Failed to parse result JSON",
                suggestions=[
                    "The result file may be corrupted",
                    "Check task logs for errors during execution",
                    "Ensure the function returns JSON-serializable data",
                ],
            ) from e

    def shell(
        self, command: Optional[str] = None, node: Optional[int] = None, progress_context=None
    ) -> None:
        """Open shell connection to running task instance.

        Establishes shell access for debugging, monitoring, or interactive
        development. Uses provider-specific remote operations (SSH, kubectl exec,
        cloud APIs, etc.) based on the underlying infrastructure.

        Args:
            command: Remote command to execute. If provided, runs the
                command and exits. If None, starts an interactive shell
                session. Shell metacharacters are supported.
            node: For multi-instance tasks, specify which node to
                connect to (0-indexed). Currently connects to primary
                node regardless, but parameter reserved for future use.

        Raises:
            FlowError: Connection failed due to:
                - Task not in RUNNING state
                - Provider doesn't support shell access
                - Network connectivity issues
                - Command execution failure (non-zero exit)
            ValueError: Invalid node index for multi-instance task

        Examples:
            >>> # Interactive debugging
            >>> task.shell()  # Opens shell

            >>> # Run commands
            >>> task.shell("nvidia-smi")  # Check GPU
            >>> task.shell("ps aux | grep python")  # Check processes
            >>> task.shell("tail -f /workspace/training.log")  # Stream logs
        """
        if not self._provider:
            raise RuntimeError("Task not connected to provider")

        remote_ops = self._provider.get_remote_operations()
        if not remote_ops:
            raise FlowError(
                "Provider does not support shell access",
                suggestions=[
                    "This provider does not support remote shell access",
                    "Use a provider that implements remote operations",
                    "Check provider documentation for supported features",
                ],
            )

        # Use provider's remote operations with progress callback
        remote_ops.open_shell(self.task_id, command, progress_context)

    def is_provisioning(self) -> bool:
        """Check if task instance is still provisioning.

        Returns:
            True if instance is likely still provisioning, False otherwise
        """
        if self.status != TaskStatus.RUNNING:
            return False

        # If no SSH host, instance might still be provisioning
        if not self.ssh_host:
            return True

        # Check elapsed time since creation
        if self.created_at:
            from datetime import datetime, timezone

            elapsed = (datetime.now(timezone.utc) - self.created_at).total_seconds()
            # Consider provisioning if less than 30 minutes and no SSH
            # This is conservative to handle different provider provisioning times
            return elapsed < 1800  # 30 minutes

        return False

    def get_provisioning_message(self) -> Optional[str]:
        """Get helpful message about provisioning status.

        Returns:
            Message string if provisioning, None otherwise
        """
        if not self.is_provisioning():
            return None

        if self.created_at:
            from datetime import datetime, timezone

            elapsed = (datetime.now(timezone.utc) - self.created_at).total_seconds()
            elapsed_min = elapsed / 60

            if elapsed_min < 5:
                return f"Instance starting up ({elapsed_min:.1f} min elapsed)"
            elif elapsed_min < 10:
                return f"Instance provisioning ({elapsed_min:.1f} min elapsed) - SSH will be available soon"
            else:
                # Don't show remaining time as it's provider-specific
                return f"Instance provisioning ({elapsed_min:.1f} min elapsed) - this can take several minutes"

        return "Instance provisioning - this can take several minutes"


class AvailableInstance(BaseModel):
    """Available compute resource."""

    allocation_id: str = Field(..., description="Resource allocation ID")
    instance_type: str = Field(..., description="Instance type identifier")
    region: str = Field(..., description="Availability region")
    price_per_hour: float = Field(..., description="Hourly price (USD)")

    # Hardware specs
    gpu_type: Optional[str] = Field(None, description="GPU type")
    gpu_count: Optional[int] = Field(None, description="Number of GPUs")
    cpu_count: Optional[int] = Field(None, description="Number of CPUs")
    memory_gb: Optional[int] = Field(None, description="Memory in GB")

    # Availability info
    available_quantity: Optional[int] = Field(None, description="Number available")
    status: Optional[str] = Field(None, description="Allocation status")
    expires_at: Optional[datetime] = Field(None, description="Expiration time")


class Instance(BaseModel):
    """Compute instance entity."""

    instance_id: str = Field(..., description="Instance UUID")
    task_id: str = Field(..., description="Parent task ID")
    status: InstanceStatus = Field(..., description="Instance state")

    # Connection info
    ssh_host: Optional[str] = Field(None, description="Public hostname/IP")
    private_ip: Optional[str] = Field(None, description="VPC-internal IP")

    # Timestamps
    created_at: datetime
    terminated_at: Optional[datetime] = None


class Volume(BaseModel):
    """Persistent storage volume."""

    volume_id: str = Field(..., description="Volume UUID")
    name: str = Field(..., description="Human-readable name")
    size_gb: int = Field(..., description="Capacity (GB)")
    region: str = Field(..., description="Storage region")
    interface: StorageInterface = Field(..., description="Access interface")

    # Metadata
    created_at: datetime
    attached_to: List[str] = Field(default_factory=list, description="Attached instance IDs")

    @property
    def id(self) -> str:
        """ID property alias."""
        return self.volume_id


# ================== Section 4: Configuration Models ==================


class FlowConfig(BaseModel):
    """Flow SDK configuration settings.

    Immutable configuration for API authentication and default behaviors.
    Typically loaded from environment variables or config files rather
    than constructed directly.

    Configuration Sources (precedence order):
        1. Explicit FlowConfig object
        2. Environment variables (FLOW_*)
        3. Local .flow/config.yaml
        4. Global ~/.flow/config.yaml
        5. Interactive setup (flow init)

    Security:
        - API keys should never be committed to version control
        - Use environment variables in CI/CD pipelines
        - Keys are project-scoped for access isolation

    Example:
        >>> # From environment
        >>> os.environ['FLOW_API_KEY'] = 'mithril-...'
        >>> os.environ['FLOW_PROJECT'] = 'ml-research'
        >>> flow = Flow()  # Auto-discovers config

        >>> # Explicit config
        >>> config = FlowConfig(
        ...     api_key='mithril-...',
        ...     project='ml-research',
        ...     region='us-west-2'
        ... )
        >>> flow = Flow(config=config)
    """

    model_config = ConfigDict(frozen=True)

    api_key: str = Field(..., description="Authentication key")
    project: str = Field(..., description="Project identifier")
    region: str = Field(default="us-central1-b", description="Default deployment region")
    api_url: str = Field(default="https://api.mithril.ai", description="API base URL")


class Project(BaseModel):
    """Project metadata."""

    name: str = Field(..., description="Project identifier")
    region: str = Field(..., description="Primary region")


class ValidationResult(BaseModel):
    """Configuration validation result."""

    is_valid: bool = Field(..., description="Validation status")
    projects: List[Project] = Field(default_factory=list, description="Accessible projects")
    error_message: Optional[str] = Field(None, description="Validation error")


# ================== Section 5: Request/Response Models ==================


class SubmitTaskRequest(BaseModel):
    """Task submission request."""

    config: TaskConfig = Field(..., description="Task specification")
    wait: bool = Field(False, description="Block until complete")
    dry_run: bool = Field(False, description="Validation only")


class SubmitTaskResponse(BaseModel):
    """Task submission result."""

    task_id: str = Field(..., description="Assigned task ID")
    status: TaskStatus = Field(..., description="Initial state")
    message: Optional[str] = Field(None, description="Status details")


class ListTasksRequest(BaseModel):
    """Task listing request."""

    status: Optional[TaskStatus] = Field(None, description="Status filter")
    limit: int = Field(100, ge=1, le=1000, description="Page size")
    offset: int = Field(0, ge=0, description="Skip count")


class ListTasksResponse(BaseModel):
    """Task listing result."""

    tasks: List[Task] = Field(..., description="Task collection")
    total: int = Field(..., description="Total available")
    has_more: bool = Field(..., description="Pagination indicator")
