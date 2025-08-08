"""Provider interface protocols for Flow SDK.

This module defines the core contracts for cloud provider implementations.
All protocols use structural typing via Python's Protocol class, enabling
duck typing with static analysis.

The module provides three main protocol categories:
  - IComputeProvider: GPU instance lifecycle management
  - IStorageProvider: Persistent volume operations
  - IProvider: Combined compute + storage + user management

These protocols enable dependency inversion where core depends on abstractions
rather than implementations, allowing new providers to extend functionality
without modifying core SDK code.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional, Protocol, Tuple

from flow.api.models import Instance, Task, TaskConfig, TaskStatus, User, Volume

if TYPE_CHECKING:
    from flow.providers.base import ProviderCapabilities


class IRemoteOperations(Protocol):
    """Provider-agnostic remote operations on running tasks.

    This abstraction enables providers to implement remote operations
    using their platform-specific mechanisms (SSH, kubectl exec,
    cloud APIs, etc.) while maintaining a consistent interface.
    """

    def execute_command(self, task_id: str, command: str, timeout: Optional[int] = None) -> str:
        """Execute a command on a remote task.

        Args:
            task_id: Task identifier
            command: Command to execute
            timeout: Optional timeout in seconds

        Returns:
            Command output (stdout)

        Raises:
            TaskNotFoundError: Task doesn't exist
            RemoteExecutionError: Command failed
            TimeoutError: Command timed out
        """
        ...

    def retrieve_file(self, task_id: str, remote_path: str) -> bytes:
        """Retrieve file contents from a remote task.

        Args:
            task_id: Task identifier
            remote_path: Path to file on remote system

        Returns:
            File contents as bytes

        Raises:
            TaskNotFoundError: Task doesn't exist
            FileNotFoundError: Remote file doesn't exist
            RemoteExecutionError: Retrieval failed
        """
        ...

    def open_shell(self, task_id: str, command: Optional[str] = None) -> None:
        """Open interactive shell or execute command with TTY.

        Args:
            task_id: Task identifier
            command: Optional command to execute

        Raises:
            TaskNotFoundError: Task doesn't exist
            RemoteExecutionError: Shell access failed
        """
        ...


class IComputeProvider(Protocol):
    """GPU compute infrastructure provider interface.

    Defines the contract for cloud provider integrations, enabling uniform task
    submission and monitoring across heterogeneous infrastructure (Mithril, AWS, GCP,
    Azure, Lambda Labs).

    All operations are task-centric, using task_id as the primary key. Methods
    validate inputs early and map provider-specific errors to the FlowError
    hierarchy for consistent client experience.

    Performance expectations:
      - find_instances: <1s for catalog query
      - submit_task: <10s for instance provisioning
      - get_task_status: <500ms for status check
      - stream_logs: <100ms latency per chunk
    """

    def normalize_instance_request(
        self, gpu_count: int, gpu_type: Optional[str] = None
    ) -> Tuple[str, int, Optional[str]]:
        """Normalize GPU request to valid instance configuration.

        Handles provider-specific constraints like minimum node sizes.
        For example, H100s on Mithril only come in 8-GPU nodes.

        Args:
            gpu_count: Number of GPUs requested by user
            gpu_type: GPU type requested (e.g., "h100", "a100")

        Returns:
            Tuple of (instance_type, num_instances, warning_message)
            - instance_type: Provider-specific instance type (e.g., "8xh100")
            - num_instances: Number of instances needed
            - warning_message: Optional message about adjustments made

        Example:
            >>> # User requests 1 H100, but they only come in 8x
            >>> instance_type, num_instances, warning = provider.normalize_instance_request(1, "h100")
            >>> # Returns: ("8xh100", 1, "H100s only available in 8-GPU nodes. Allocating 8 GPUs.")
        """
        # Default implementation - no provider-specific constraints
        if not gpu_type:
            gpu_type = "a100"  # Default GPU type

        if gpu_count >= 8 and gpu_count % 8 == 0:
            return f"8x{gpu_type}", gpu_count // 8, None
        elif gpu_count >= 4 and gpu_count % 4 == 0:
            return f"4x{gpu_type}", gpu_count // 4, None
        elif gpu_count >= 2 and gpu_count % 2 == 0:
            return f"2x{gpu_type}", gpu_count // 2, None
        else:
            return gpu_type, gpu_count, None

    def find_instances(
        self,
        requirements: Dict[str, Any],
        limit: int = 10,
    ) -> List[Instance]:
        """Find available GPU instances matching requirements.

        Searches provider inventory for instances satisfying all specified
        constraints. Returns best matches first based on price/performance.

        Args:
            requirements: Constraint dictionary with optional keys:
                instance_type: Exact instance type to match. Provider-specific
                    format (e.g., "p3.2xlarge", "a100-80gb"). If specified,
                    other constraints are hints.
                min_gpu_count: Minimum number of GPUs required. Range: 1-16
                    typical, up to 64 for special instances.
                max_price: Maximum hourly price in USD. Spot/preemptible
                    pricing. None means any price.
                region: Target region/zone for deployment. Provider-specific
                    format ("us-east-1", "us-central1-b").
                gpu_memory_gb: Minimum GPU memory per device. Common values:
                    16, 24, 40, 80. Used for capability matching.
                gpu_type: GPU model hint ("a100", "v100", "h100"). Lowercase,
                    no vendor prefix.
            limit: Maximum results to return. Range: 1-100.

        Returns:
            Available instances sorted by preference: (1) Price ascending,
            (2) GPU memory descending, (3) Availability descending. Empty
            list if no instances match all requirements.

        Raises:
            ValidationError: Invalid requirements.
            ProviderError: Provider API failure or permission issue.

        Example:
            >>> # Find cheapest A100 instance
            >>> instances = provider.find_instances({
            ...     "gpu_type": "a100",
            ...     "max_price": 10.0,
            ...     "region": "us-east-1"
            ... })
            >>> if instances:
            ...     cheapest = instances[0]
        """
        ...

    def submit_task(
        self,
        instance_type: str,
        config: TaskConfig,
        volume_ids: Optional[List[str]] = None,
    ) -> Task:
        """Submit task with automatic instance and region selection.

        Launches computational workload on best available instance matching the
        requested type. Provider handles translation from user-friendly instance
        types to internal IDs and selects optimal region automatically.

        Args:
            instance_type: User-friendly instance type specification. Examples:
                "a100", "4xa100", "8xh100", "2xv100". Provider handles all
                format translation and validation.
            config: Complete task specification including command/script/shell
                (execution target), image (container with GPU support), env
                (environment variables), ssh_keys (authorized keys),
                max_run_time_hours (auto-termination timeout), and optional
                region preference.
            volume_ids: List of volume IDs to attach. Volumes must not be
                attached to other instances and must match mount paths in
                config.volumes.

        Returns:
            Task handle with task_id, status, connection details (ssh_host/port
            when running), and methods for monitoring and control.

        Raises:
            ResourceNotAvailableError: No instances of requested type available.
            ValidationError: Invalid instance type or configuration.
            VolumeError: Volume attachment failed.
            ProviderError: Launch failure (quota, permissions).
        """
        ...

    def get_task(self, task_id: str) -> Task:
        """Retrieve complete task state with fresh data.

        Fetches current task information from provider, including status,
        connection details, and cost information. More expensive than
        get_task_status() but provides full metadata.

        Args:
            task_id: Task identifier from submit_task(). Must be valid task
                owned by current project.

        Returns:
            Complete task object with all original fields from submission,
            updated status and timestamps, SSH connection info (if running),
            cost accumulation, and error messages (if failed).

        Raises:
            TaskNotFoundError: Task doesn't exist or access denied.
            ProviderError: API communication failure.
        """
        ...

    def get_task_status(self, task_id: str) -> TaskStatus:
        """Query task status efficiently.

        Lightweight status check optimized for polling. Returns only
        status enum without full task metadata. Use for wait loops
        and progress monitoring.

        Args:
            task_id: Task identifier to check

        Returns:
            TaskStatus: Current state enum:
                - PENDING: Queued or provisioning
                - RUNNING: Executing on GPU
                - COMPLETED: Finished (exit 0)
                - FAILED: Error or non-zero exit
                - CANCELLED: User termination

        Raises:
            TaskNotFoundError: Invalid or inaccessible task

        Performance:
            Target: <200ms (may use short-lived cache)
        """
        ...

    def stop_task(self, task_id: str) -> bool:
        """Terminate task execution gracefully.

        Initiates shutdown sequence: SIGTERM, wait 30s, then SIGKILL if needed.
        Cleans up resources and stops billing immediately.

        Args:
            task_id: Task to terminate. Must be PENDING or RUNNING.

        Returns:
            True if termination initiated, False if already terminal.
        """
        ...

    def cancel_task(self, task_id: str) -> bool:
        """Cancel task execution (deprecated).

        Deprecated:
            Use stop_task() instead. This method exists only
            for backward compatibility and will be removed.

        Args:
            task_id: Task to cancel

        Returns:
            bool: Result from stop_task()
        """
        ...

    def get_task_logs(
        self,
        task_id: str,
        tail: int = 100,
        log_type: str = "stdout",  # stdout, stderr
    ) -> str:
        """Fetch recent task output logs.

        Retrieves last N lines of task stdout/stderr. Handles
        large outputs efficiently with server-side tail.

        Args:
            task_id: Task whose logs to retrieve
            tail: Number of recent lines to return.
                Range: 1-10000. Large values may be slow.
            log_type: Output stream to fetch:
                - "stdout": Standard output (default)
                - "stderr": Standard error
                - "combined": Both streams interleaved

        Returns:
            str: Log lines joined with newlines.
                Empty string if no output yet.
                May include partial lines at boundaries.

        Raises:
            TaskNotFoundError: Invalid task ID
            ProviderError: Log retrieval failed

        Performance:
            - 100 lines: ~200ms
            - 1000 lines: ~500ms
            - 10000 lines: ~2s
        """
        ...

    def stream_task_logs(
        self,
        task_id: str,
        log_type: str = "stdout",  # stdout, stderr
    ) -> Iterator[str]:
        """Stream task logs in real-time.

        Returns iterator that yields new log lines as they arrive. Handles
        reconnection and backpressure automatically.

        Args:
            task_id: Task to stream logs from.
            log_type: Stream selection - "stdout" (default), "stderr", or
                "combined" (both interleaved).

        Yields:
            Individual log lines without newlines. Empty strings for keepalive.
            Stops when task terminates.

        Raises:
            TaskNotFoundError: Invalid task.
            ProviderError: Streaming setup failed.
        """
        ...

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        limit: int = 100,
    ) -> List[Task]:
        """List tasks with optional status filter.

        Retrieves recent tasks for current project/user. Results
        must be ordered by creation time (newest first). Providers
        should request newest-first ordering from their APIs and
        apply client-side sorting if necessary to ensure consistent
        behavior.

        Args:
            status: Filter by specific status. None returns all.
            limit: Maximum tasks to return. Range: 1-1000.
                Large limits increase response time.

        Returns:
            List[Task]: Task objects with full metadata.
                Empty list if no matching tasks.
                Ordered by created_at descending (newest first).

        Performance:
            O(limit) response time, typically 2-5ms per task
        """
        ...

    def prepare_task_config(self, config: TaskConfig) -> TaskConfig:
        """Apply provider-specific defaults to task configuration.

        Enriches user configuration with provider requirements and optimizations.
        Called automatically by Flow.run() before instance selection.

        Args:
            config: User-provided configuration.

        Returns:
            Enhanced configuration with SSH keys added if missing, region set
            from provider default, image adjusted for provider, startup scripts
            injected, and security settings applied.
        """
        ...

    def get_task_instances(self, task_id: str) -> List[Instance]:
        """Fetch detailed instance information for task.

        Retrieves connection details for all instances in a multi-node
        task. Essential for distributed training coordination and
        debugging multi-instance deployments.

        Args:
            task_id: Task to query. Must exist and be accessible.

        Returns:
            List[Instance]: Instance details for each node:
                - instance_id: Cloud provider instance ID
                - public_ip: External IP address
                - private_ip: VPC-internal IP
                - ssh_host/port: SSH connection info
                - status: Instance state
                Order matches num_instances from config.

        Raises:
            TaskNotFoundError: Task doesn't exist
            ProviderError: Instance query failed

        Use Cases:
            - Get IPs for distributed training setup
            - SSH to specific nodes in multi-instance
            - Monitor individual instance health
            - Configure node-to-node communication
        """
        ...


class IStorageProvider(Protocol):
    """Persistent storage volume management interface.

    Defines operations for durable block storage that persists across task
    lifecycles. Volumes provide high-performance storage for datasets,
    checkpoints, and shared state.

    Volumes are project-scoped and region-specific, support concurrent reads
    with exclusive writes, are automatically formatted on first use (ext4),
    and encrypted at rest with provider-managed keys.
    """

    def create_volume(
        self,
        size_gb: int,
        name: Optional[str] = None,
        interface: str = "block",
    ) -> Volume:
        """Create new persistent storage volume.

        Provisions network-attached storage in the current region.

        Args:
            size_gb: Volume size in gigabytes. Range: 1-16384 (16TB).
            name: Human-readable identifier. Optional but recommended. Must be
                3-63 chars, lowercase alphanumeric + dash, unique within project.
            interface: Storage type - "block" (high-performance exclusive) or
                "file" (shared NFS access).

        Returns:
            Created volume with volume_id, name, size_gb, region, and status.

        Raises:
            ValidationError: Invalid size or name.
            QuotaExceededError: Storage limit reached.
            ProviderError: Provisioning failed.
        """
        ...

    def delete_volume(self, volume_id: str) -> bool:
        """Delete storage volume permanently.

        Immediately destroys volume and all data. Cannot be undone.
        Fails if volume is currently attached to running tasks.

        Args:
            volume_id: Volume to delete (from create_volume)

        Returns:
            bool: True if deleted, False if not found

        Raises:
            VolumeInUseError: Volume attached to task
            ProviderError: Deletion failed

        Warning:
            No recovery after deletion. Backup critical data first.
        """
        ...

    def list_volumes(
        self,
        limit: int = 100,
    ) -> List[Volume]:
        """List storage volumes in project.

        Enumerates all volumes accessible to current credentials.
        Includes attached and detached volumes across all regions.

        Args:
            limit: Maximum results. Range: 1-1000.

        Returns:
            List[Volume]: Volumes ordered by created_at (newest first).
                Includes size, region, and attachment status.

        Performance:
            Linear in limit, ~1ms per volume
        """
        ...

    def upload_file(
        self,
        volume_id: str,
        local_path: Path,
        remote_path: Optional[str] = None,
    ) -> bool:
        """Upload local file to volume.

        Transfers file to specified path within volume. Volume must
        be detached or attached to a stopped instance. Creates parent
        directories as needed.

        Args:
            volume_id: Target volume ID
            local_path: Source file path
            remote_path: Destination path in volume.
                Relative to volume root. Defaults to filename.

        Returns:
            bool: True if uploaded successfully

        Raises:
            FileNotFoundError: Local file doesn't exist
            VolumeNotFoundError: Invalid volume ID
            VolumeInUseError: Volume attached to running task
            ProviderError: Transfer failed

        Note:
            For large files, consider mounting volume and using
            task-based transfer for better performance.
        """
        ...

    def upload_directory(
        self,
        volume_id: str,
        local_path: Path,
        remote_path: Optional[str] = None,
    ) -> bool:
        """Upload directory tree to volume.

        Recursively transfers directory contents preserving structure.
        Handles nested directories and maintains permissions.

        Args:
            volume_id: Target volume
            local_path: Source directory
            remote_path: Destination in volume.
                Created if not exists.

        Returns:
            bool: True if all files uploaded

        Performance:
            ~10MB/s typical, varies by file count/size
        """
        ...

    def download_file(
        self,
        volume_id: str,
        remote_path: str,
        local_path: Path,
    ) -> bool:
        """Download file from volume."""
        ...

    def download_directory(
        self,
        volume_id: str,
        remote_path: str,
        local_path: Path,
    ) -> bool:
        """Download directory recursively."""
        ...

    def is_volume_id(self, identifier: str) -> bool:
        """Determine if identifier is volume ID or name.

        Distinguishes between volume IDs (provider-generated) and
        human-friendly names. Used for volume resolution in commands.

        Args:
            identifier: String to check

        Returns:
            bool: True if ID format, False if name format

        ID Formats:
            - Mithril: "vol-" + random (e.g., "vol-abc123def456")
            - AWS: "vol-" + hex (e.g., "vol-0a1b2c3d4e5f6")
            - GCP: Numeric (e.g., "1234567890123456789")

        Name Format:
            - 3-63 characters
            - Lowercase alphanumeric + dash
            - No "vol-" prefix
        """
        ...


class IProvider(IComputeProvider, IStorageProvider):
    """Complete provider interface combining compute and storage.

    Primary abstraction for cloud providers, combining GPU compute
    and persistent storage operations. Implementations provide
    full lifecycle management for tasks and data.

    Additional Capabilities:
        - User identity resolution
        - Provider feature detection
        - Cross-service integration
        - Remote operations support
        - Instance type resolution
    """

    def get_remote_operations(self) -> Optional[IRemoteOperations]:
        """Get remote operations handler if supported.

        Returns:
            Remote operations handler or None if not supported
        """
        return None

    def resolve_instance_type(self, user_spec: str) -> str:
        """Convert user-friendly instance spec to provider format.

        Args:
            user_spec: User input like "a100", "4xa100", etc.

        Returns:
            Provider-specific instance identifier

        Raises:
            InstanceTypeError: Invalid or unsupported spec
        """
        # Default implementation - pass through
        return user_spec

    def get_user(self, user_id: str) -> "User":
        """Resolve opaque user ID to identity information.

        Maps provider-specific user identifiers to human-readable
        information. Used for audit trails and collaboration features.

        Args:
            user_id: Provider user identifier.
                Format varies: "user_abc123", email, UUID.

        Returns:
            User: Identity information:
                - user_id: Same as input
                - username: Human-readable name
                - email: Contact email

        Raises:
            UserNotFoundError: Invalid or inaccessible user
            ProviderError: Identity service failure

        Privacy:
            Only returns users in same organization/project
        """
        ...

    def get_capabilities(self) -> "ProviderCapabilities":
        """Query provider feature support and limitations.

        Returns static capability descriptor enabling SDK to adapt
        behavior to provider-specific features and constraints.
        Used for graceful degradation and optimal feature usage.

        Returns:
            ProviderCapabilities: Feature flags and limits:
                - supports_spot_instances: Has preemptible compute
                - supports_persistent_volumes: Volume attachment
                - supports_ssh_access: Direct instance SSH
                - max_instances_per_task: Multi-node limit
                - max_volume_size_gb: Storage constraints
                - supported_regions: Available locations
                - gpu_types: Available accelerators

        Usage:
            Checked by SDK to conditionally enable features
            and provide appropriate error messages.
        """
        ...
