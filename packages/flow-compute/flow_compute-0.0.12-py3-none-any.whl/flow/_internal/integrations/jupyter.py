"""Jupyter notebook integration for Flow SDK.

Provides Jupyter kernel execution on Flow GPU instances.
Note: This is NOT Google Colab integration - it's direct Jupyter on GPU.
"""

import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from flow import Flow, TaskConfig
from flow._internal.integrations.jupyter_persistence import PersistenceManager
from flow._internal.integrations.jupyter_session import FlowJupyterSession, SessionManager
from flow.api.models import Task, VolumeSpec
from flow.errors import FlowError, ValidationError
from flow.utils.exceptions import NetworkError, NotFoundError


@dataclass
class JupyterConnection:
    """Represents a connection to a Jupyter notebook."""

    url: str
    task_id: str
    session_id: str
    instance_type: str
    startup_time: float
    ssh_command: str  # SSH tunnel command for secure connection

    # For resume connections
    last_active: Optional[str] = None
    checkpoint_size: Optional[str] = None
    variables_restored: Optional[int] = None
    restore_time: Optional[float] = None


@dataclass
class LaunchOperation:
    """Tracks a detached launch operation."""

    session_id: str
    task_id: Optional[str]
    instance_type: str
    stage: str  # 'launching', 'ready', 'failed'
    start_time: datetime
    message: str
    error: Optional[str] = None
    connection: Optional[JupyterConnection] = None


class JupyterIntegration:
    """Jupyter notebook integration with Flow GPU backend."""

    KERNEL_SCRIPT = """#!/bin/bash
set -euo pipefail

# Simple kernel startup - security via SSH tunnel only
# The GPU instance is already private and authenticated via Flow

# Install dependencies in venv
python3 -m venv /opt/flow-kernel-env
source /opt/flow-kernel-env/bin/activate
pip install --no-cache-dir ipykernel jupyter-client pyzmq

# Start kernel on localhost (SSH tunnel provides security)
python -m ipykernel_launcher \
    --ip=127.0.0.1 \
    --transport=tcp \
    --KernelManager.connection_file="/tmp/kernel.json" &

KERNEL_PID=$!
echo $KERNEL_PID > /tmp/kernel.pid

# Wait for kernel to start
sleep 3
if ! kill -0 $KERNEL_PID 2>/dev/null; then
    echo "ERROR: Kernel failed to start" >&2
    exit 1
fi

echo "KERNEL_READY=true"
echo "KERNEL_PID=$KERNEL_PID"
"""

    KERNEL_WITH_PERSISTENCE_SCRIPT = """#!/bin/bash
set -euo pipefail

# Kernel with persistence - security via SSH tunnel

# Verify persistence volume
if [ -d /flow/state ]; then
    if [ ! -w /flow/state ]; then
        echo "ERROR: Persistence volume not writable" >&2
        exit 1
    fi
    echo "PERSISTENCE_ENABLED=true"
else
    echo "PERSISTENCE_ENABLED=false"
fi

# Install in venv
python3 -m venv /opt/flow-kernel-env
source /opt/flow-kernel-env/bin/activate
pip install --no-cache-dir ipykernel jupyter-client pyzmq dill

# Start kernel with persistence wrapper
cat > /tmp/start_kernel.py << 'EOF'
from flow._internal.integrations.kernel_wrapper import FlowPersistentKernel
FlowPersistentKernel.launch_instance(ip="127.0.0.1")
EOF

python /tmp/start_kernel.py &

KERNEL_PID=$!
echo $KERNEL_PID > /tmp/kernel.pid

sleep 3
if ! kill -0 $KERNEL_PID 2>/dev/null; then
    echo "ERROR: Kernel failed to start" >&2
    exit 1
fi

echo "KERNEL_READY=true"
echo "KERNEL_PID=$KERNEL_PID"
"""

    def __init__(self, flow_client: Flow):
        """Initialize with Flow client."""
        self.flow = flow_client
        self.session_manager = SessionManager()
        self.persistence_manager = PersistenceManager(flow_client)
        # Track detached operations in memory
        self._operations: Dict[str, LaunchOperation] = {}

    def launch(
        self,
        instance_type: Optional[str] = None,
        hours: float = 4.0,
        session_id: Optional[str] = None,
        min_gpu_memory_gb: Optional[int] = None,
    ) -> JupyterConnection:
        """Launch a new Colab session with GPU backend.

        Args:
            instance_type: GPU instance type (e.g., "a100", "h100")
            hours: Maximum runtime in hours
            session_id: Optional session ID for persistence
            min_gpu_memory_gb: Minimum GPU memory in GB (alternative to instance_type)

        Returns:
            JupyterConnection with URL and metadata
        """
        start_time = time.time()

        # Generate session ID if not provided
        if not session_id:
            session_id = f"flow-session-{int(time.time())}"

        # Get or create persistence volume if using persistence
        volumes = []
        if self.persistence_manager.is_enabled():
            region = self._get_region_for_instance(instance_type)
            volume_id = self.persistence_manager.ensure_volume(region, session_id)
            volumes = [VolumeSpec(volume_id=volume_id, mount_path="/flow/state")]
            kernel_script = self.KERNEL_WITH_PERSISTENCE_SCRIPT
        else:
            kernel_script = self.KERNEL_SCRIPT

        # Configure task
        config_args = {
            "name": f"colab-{session_id}",
            "command": kernel_script,
            "max_run_time_hours": hours,
            "volumes": volumes,
        }

        # Use either instance_type or min_gpu_memory_gb
        if instance_type:
            config_args["instance_type"] = instance_type
        elif min_gpu_memory_gb:
            config_args["min_gpu_memory_gb"] = min_gpu_memory_gb
        else:
            # Default to H100 if nothing specified
            config_args["instance_type"] = "h100"

        config = TaskConfig(**config_args)

        # Launch instance
        task = self.flow.run(config, wait=False)

        # Wait for kernel to be ready
        kernel_info = self._wait_for_kernel(task)

        # SSH tunnel is required for security
        ssh_command = f"ssh -L 8888:localhost:8888 {task.ssh_user}@{task.ssh_host}"

        # Simple localhost URL - security is via SSH tunnel
        colab_url = "http://localhost:8888"

        startup_time = time.time() - start_time

        # Save session for resume functionality
        self.session_manager.save_session(
            session_id=session_id,
            task_id=task.task_id,
            instance_type=instance_type,
            notebook_name=None,  # Will be updated when notebook connects
        )

        return JupyterConnection(
            url=colab_url,
            task_id=task.task_id,
            session_id=session_id,
            instance_type=instance_type,
            startup_time=startup_time,
            ssh_command=ssh_command,
        )

    def resume(self, notebook_name: str, instance_type: Optional[str] = None) -> JupyterConnection:
        """Resume a notebook with its saved state.

        Args:
            notebook_name: Name of the notebook to resume
            instance_type: Optional override for instance type

        Returns:
            JupyterConnection with restored session
        """
        # Find session for notebook
        session = self.session_manager.find_session_for_notebook(notebook_name)
        if not session:
            raise NotFoundError(f"No session found for notebook: {notebook_name}")

        # Get checkpoint info
        checkpoint_info = self.persistence_manager.get_checkpoint_info(session.volume_id)

        # Launch with same session ID to reattach volume
        connection = self.launch(
            instance_type=instance_type or session.instance_type, session_id=session.session_id
        )

        # Add resume-specific info
        connection.last_active = self._format_time_ago(session.last_active)
        connection.checkpoint_size = f"{checkpoint_info['size_gb']:.1f} GB"
        connection.variables_restored = checkpoint_info["variable_count"]
        connection.restore_time = checkpoint_info["restore_time_ms"]

        return connection

    def list_sessions(self) -> List[FlowJupyterSession]:
        """List all Colab sessions."""
        return self.session_manager.list_sessions()

    def stop_session(self, session_id: str):
        """Stop a Colab session and optionally save final checkpoint."""
        session = self.session_manager.get_session(session_id)
        if not session:
            raise NotFoundError(f"Session not found: {session_id}")

        # Cancel the task
        self.flow.cancel(session.task_id)

        # Mark session as stopped
        self.session_manager.stop_session(session_id)

    def _wait_for_kernel(self, task: Task, timeout: int = 120) -> Dict[str, Any]:
        """Wait for Jupyter kernel to be ready.

        Returns:
            Dict with kernel info
        """
        from flow.utils.retry_helper import RetryableOperation

        start_time = time.time()

        # Use retry for status checks (network calls)
        with RetryableOperation(max_attempts=3, initial_delay=0.5) as retry:
            while retry.should_retry() and time.time() - start_time < timeout:
                try:
                    # Check task status with retry
                    status = self.flow.status(task.task_id)
                    retry.success()

                    if status == "failed":
                        # Get failure reason from logs
                        logs = self._get_logs_with_retry(task.task_id, tail=50)
                        raise FlowError(f"Kernel failed to start:\n{logs}")

                    if status == "running":
                        # Look for kernel ready signal
                        logs = self._get_logs_with_retry(task.task_id, tail=100)

                        # Check if kernel is ready
                        if "KERNEL_READY=true" in logs:
                            return {"status": "ready", "port": 8888}

                        # Check for kernel errors
                        if "ERROR: Kernel failed to start" in logs:
                            raise FlowError(f"Kernel startup failed:\n{logs}")

                except (NetworkError, TimeoutError) as e:
                    retry.failure(e)

                time.sleep(2)

        raise TimeoutError(f"Kernel did not start within {timeout} seconds")

    def _get_logs_with_retry(self, task_id: str, tail: int = 100) -> str:
        """Get logs with retry logic."""
        from flow.utils.retry_helper import with_retry

        @with_retry(max_attempts=3, initial_delay=0.5)
        def get_logs():
            return self.flow.logs(task_id, tail=tail)

        return get_logs()

    def _get_region_for_instance(self, instance_type: str) -> str:
        """Get the best region for an instance type."""
        # In real implementation, this would check availability
        # For now, return default region
        return "us-central1"

    def _format_time_ago(self, dt: datetime) -> str:
        """Format datetime as human-readable time ago."""
        if not dt:
            return "unknown"

        delta = datetime.now(timezone.utc) - dt

        if delta.days > 0:
            return f"{delta.days} days ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} hours ago"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes} minutes ago"
        else:
            return "just now"

    def generate_session_id(self) -> str:
        """Generate a unique session ID.

        Uses a combination of timestamp and UUID for uniqueness and sortability.
        """
        timestamp = int(time.time())
        unique_id = str(uuid.uuid4())[:8]
        return f"flow-session-{timestamp}-{unique_id}"

    def launch_async(
        self,
        instance_type: Optional[str] = None,
        hours: float = 4.0,
        session_id: Optional[str] = None,
        min_gpu_memory_gb: Optional[int] = None,
    ) -> str:
        """Launch a Colab session asynchronously.

        Returns immediately with a session ID. Use get_launch_status() to check progress.

        Args:
            instance_type: GPU instance type (e.g., "a100", "h100")
            hours: Maximum runtime in hours
            session_id: Optional session ID (generated if not provided)
            min_gpu_memory_gb: Minimum GPU memory in GB (alternative to instance_type)

        Returns:
            Session ID to track the operation
        """
        # Generate session ID if not provided
        if not session_id:
            session_id = self.generate_session_id()

        # Create operation tracker
        operation = LaunchOperation(
            session_id=session_id,
            task_id=None,
            instance_type=instance_type or "gpu",
            stage="launching",
            start_time=datetime.now(timezone.utc),
            message="Launching GPU instance...",
        )
        self._operations[session_id] = operation

        # Launch in background thread
        def _background_launch():
            try:
                # Actually launch the instance
                connection = self.launch(
                    instance_type=instance_type,
                    hours=hours,
                    session_id=session_id,
                    min_gpu_memory_gb=min_gpu_memory_gb,
                )

                # Update operation with success
                operation.stage = "ready"
                operation.message = "GPU instance is ready!"
                operation.connection = connection
                operation.task_id = connection.task_id

            except Exception as e:
                # Update operation with failure
                operation.stage = "failed"
                operation.message = "Failed to launch GPU instance"
                operation.error = str(e)

        thread = threading.Thread(target=_background_launch, daemon=True)
        thread.start()

        return session_id

    def get_launch_status(self, session_id: str) -> Dict[str, Any]:
        """Get the status of a launch operation.

        Args:
            session_id: The session ID to check

        Returns:
            Dict with status information
        """
        # Resolve partial session ID
        full_session_id = self.resolve_session_id(session_id)

        # Check if it's a tracked operation
        if full_session_id in self._operations:
            operation = self._operations[full_session_id]
            return {
                "session_id": operation.session_id,
                "stage": operation.stage,
                "message": operation.message,
                "start_time": operation.start_time.isoformat(),
                "elapsed_seconds": (
                    datetime.now(timezone.utc) - operation.start_time
                ).total_seconds(),
                "error": operation.error,
                "connection": operation.connection,
                "task_id": operation.task_id,
            }

        # Check if it's an existing session (already launched)
        session = self.session_manager.get_session(full_session_id)
        if session:
            # Get task status from Flow
            try:
                task_status = self.flow.status(session.task_id)
                if task_status == "running":
                    stage = "ready"
                    message = "GPU instance is running"
                elif task_status == "pending":
                    stage = "launching"
                    message = "GPU instance is starting..."
                else:
                    stage = "failed"
                    message = f"GPU instance is {task_status}"

                return {
                    "session_id": session.session_id,
                    "stage": stage,
                    "message": message,
                    "start_time": session.created_at.isoformat(),
                    "elapsed_seconds": (
                        datetime.now(timezone.utc) - session.created_at
                    ).total_seconds(),
                    "error": None,
                    "connection": JupyterConnection(
                        url="http://localhost:8888",
                        task_id=session.task_id,
                        session_id=session.session_id,
                        instance_type=session.instance_type,
                        startup_time=0.0,  # Unknown for existing sessions
                        ssh_command="ssh -L 8888:localhost:8888 ubuntu@<instance_ip>",
                    ),
                }
            except Exception as e:
                return {
                    "session_id": full_session_id,
                    "stage": "failed",
                    "message": "Failed to get status",
                    "error": str(e),
                }

        raise NotFoundError(f"No operation found for session ID: {session_id}")

    def resolve_session_id(self, partial_id: str) -> str:
        """Resolve a partial session ID to a full session ID.

        Supports prefix matching (e.g., "flow-session-123" matches "flow-session-123456-abcd").

        Args:
            partial_id: Full or partial session ID

        Returns:
            Full session ID

        Raises:
            NotFoundError: If no match found
            ValidationError: If multiple matches found
        """
        # First check if it's already a full ID
        if partial_id in self._operations:
            return partial_id

        # Check active operations
        operation_matches = [sid for sid in self._operations.keys() if sid.startswith(partial_id)]

        # Check saved sessions
        session_matches = [
            s.session_id
            for s in self.session_manager.list_sessions()
            if s.session_id.startswith(partial_id)
        ]

        # Combine and deduplicate
        all_matches = list(set(operation_matches + session_matches))

        if len(all_matches) == 0:
            raise NotFoundError(f"No session found matching: {partial_id}")
        elif len(all_matches) == 1:
            return all_matches[0]
        else:
            raise ValidationError(
                f"Multiple sessions match '{partial_id}':\n"
                + "\n".join(f"  - {sid}" for sid in sorted(all_matches))
                + "\nPlease provide more characters to uniquely identify the session."
            )
