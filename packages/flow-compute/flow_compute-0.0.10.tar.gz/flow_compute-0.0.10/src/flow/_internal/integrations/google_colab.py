"""Google Colab integration for Flow SDK.

Provides true Google Colab integration through local runtime connection protocol.
Uses Jupyter server with WebSocket extension for bi-directional communication.
"""

import logging
import re
import secrets
import socket
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional

from flow import Flow, TaskConfig
from flow.api.models import VolumeSpec
from flow.api.models import Task, TaskStatus
from flow.errors import FlowError, TaskNotFoundError, ValidationError

logger = logging.getLogger(__name__)


@dataclass
class ColabConnection:
    """Connection details for Google Colab to connect to Flow GPU instance."""

    connection_url: str  # http://localhost:8888/?token=...
    ssh_command: str  # ssh -L 8888:localhost:8888 ubuntu@...
    instance_ip: str
    instance_type: str
    task_id: str
    session_id: str
    created_at: datetime
    jupyter_token: str
    remote_port: int

    def to_dict(self) -> Dict[str, str]:
        """Return non-sensitive connection details for display/logging."""
        return {
            # Intentionally DO NOT include connection_url (contains token)
            "ssh_command": self.ssh_command,
            "instance_ip": self.instance_ip,
            "instance_type": self.instance_type,
            "task_id": self.task_id,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "remote_port": str(self.remote_port),
        }

    def connection_url_for_localport(self, local_port: int) -> str:
        return f"http://localhost:{local_port}/?token={self.jupyter_token}"

    def get_token(self) -> str:
        return self.jupyter_token


class GoogleColabIntegration:
    """Google Colab integration using local runtime connection.

    This integration provides the ability to connect Google Colab notebooks
    to Flow GPU instances through Colab's local runtime feature. It sets up
    a Jupyter server with WebSocket support on the GPU instance that Colab
    can connect to via an SSH tunnel.

    Architecture:
        1. Launch GPU instance with Jupyter + jupyter_http_over_ws
        2. Generate secure token for authentication
        3. User establishes SSH tunnel to instance
        4. User connects Colab to http://localhost:8888/?token=...
        5. All computation runs on Flow GPU, UI stays in Colab

    Security:
        - Token-based authentication (48 bytes of entropy)
        - SSH tunnel required (no direct internet exposure)
        - Origin restriction to colab.research.google.com
        - Tokens expire with instance termination
    """

    # Jupyter startup script for Colab compatibility
    JUPYTER_STARTUP_SCRIPT = """#!/bin/bash
set -euo pipefail

echo "Starting Jupyter server for Google Colab connection..."

# Optional websocket extension toggle (default off)
USE_WS="${FLOW_COLAB_USE_WS:-0}"

# Install dependencies if missing; pin notebook major to reduce breakage
python - <<'PY'
try:
    import notebook  # type: ignore
    print('NOTEBOOK_OK')
except Exception:
    pass
PY
if ! python - <<'PY'
import notebook
import sys
sys.exit(0)
PY
then
    pip install --upgrade --no-warn-script-location --disable-pip-version-check \
        notebook==6.* --retries 3 --timeout 60
fi
if [ "$USE_WS" = "1" ]; then
    pip install --no-warn-script-location --disable-pip-version-check \
        jupyter_http_over_ws==0.0.8 --retries 3 --timeout 60 || true
    jupyter serverextension enable --py jupyter_http_over_ws || true
fi

# Generate secure token
export JUPYTER_TOKEN=$(python - <<'PY'
import secrets; print(secrets.token_urlsafe(48))
PY
)

# Create Jupyter config
mkdir -p ~/.jupyter
cat > ~/.jupyter/jupyter_notebook_config.py << EOF
c.NotebookApp.allow_origin = 'https://colab.research.google.com'
c.NotebookApp.port_retries = 0
c.NotebookApp.token = '$JUPYTER_TOKEN'
c.NotebookApp.disable_check_xsrf = False
c.NotebookApp.allow_credentials = True
EOF

# Determine remote port (prefer dynamic free port)
REMOTE_PORT=$(python - <<'PY'
import socket
s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1]); s.close()
PY
)
echo "$REMOTE_PORT" > ~/.jupyter/colab_port

# Start Jupyter server bound to localhost
echo "Starting Jupyter server on port ${REMOTE_PORT}..."
jupyter notebook \
  --NotebookApp.allow_origin='https://colab.research.google.com' \
  --NotebookApp.port_retries=0 \
  --NotebookApp.token=$JUPYTER_TOKEN \
  --port=$REMOTE_PORT \
  --no-browser \
  --ip=127.0.0.1 &

JUPYTER_PID=$!
echo "JUPYTER_PID=$JUPYTER_PID"

# Wait for server to start using Python (no curl dependency)
for i in {1..60}; do
    python - <<PY >/dev/null 2>&1 && { echo "JUPYTER_READY=true"; break; } || true
import urllib.request, sys
url = "http://127.0.0.1:${REMOTE_PORT}/api/status"
try:
    urllib.request.urlopen(url, timeout=1)
except Exception:
    sys.exit(1)
PY
    sleep 1
done

# Keep script running
wait $JUPYTER_PID
"""

    def __init__(self, flow_client: Flow):
        """Initialize Google Colab integration.

        Args:
            flow_client: Initialized Flow SDK client
        """
        self.flow = flow_client
        self._active_connections: Dict[str, ColabConnection] = {}

    def connect(
        self,
        instance_type: str,
        hours: Optional[float] = None,
        auto_tunnel: bool = False,
        name: Optional[str] = None,
        attach_workspace: bool = True,
        workspace_size_gb: int = 50,
        workspace_name: Optional[str] = None,
    ) -> ColabConnection:
        """Launch GPU instance configured for Google Colab connection.

        This method launches a Flow GPU instance with Jupyter server configured
        for Google Colab's local runtime connection. After launch, the user
        must establish an SSH tunnel and connect from Colab.

        Args:
            instance_type: GPU type (e.g., "a100", "h100", "8xh100")
            hours: Maximum runtime in hours
            auto_tunnel: If True, attempt to establish SSH tunnel automatically
            name: Optional name for the task

        Returns:
            ColabConnection with SSH command and connection URL

        Raises:
            ValidationError: If parameters are invalid
            FlowError: If instance launch fails
        """
        # Validate parameters (None means unlimited)
        if hours is not None and (hours < 0.1 or hours > 168):
            raise ValidationError("Hours must be between 0.1 and 168 (or 0/unset for no limit)")

        # Generate session ID
        session_id = f"colab-{secrets.token_urlsafe(8)}"

        # Create task configuration
        config = TaskConfig(
            name=name or f"colab-{instance_type}-{int(time.time())}",
            instance_type=instance_type,
            command=["bash", "-c", self.JUPYTER_STARTUP_SCRIPT],
            max_run_time_hours=hours,  # None = unlimited
            priority="high",  # Prefer high priority for Colab to reduce queueing
        )

        # Optionally attach a workspace volume for persistent notebooks
        if attach_workspace and workspace_size_gb > 0:
            vol_name = workspace_name or f"colab-ws-{session_id}"
            # Use typed VolumeSpec to ensure downstream code expects attributes, not dict keys
            config.volumes = [
                VolumeSpec(name=vol_name, size_gb=workspace_size_gb, mount_path="/workspace")
            ]

        # Launch instance
        if hours is None:
            print(f"\nLaunching {instance_type} (no time limit)...")
        else:
            print(f"\nLaunching {instance_type} for {hours} hours...")
        print("Provisioning can take several minutes.")

        task = self.flow.run(config)

        # Wait for instance to be ready
        connection = self._wait_for_instance_ready(task, session_id)

        # Store connection
        self._active_connections[session_id] = connection

        # Establish SSH tunnel if requested
        if auto_tunnel:
            self._establish_ssh_tunnel(connection)

        return connection

    def _wait_for_instance_ready(
        self,
        task: Task,
        session_id: str,
        timeout: int = 900,  # 15 minutes
    ) -> ColabConnection:
        """Wait for instance to be ready and extract connection details.

        Mithril instances take 8-12 minutes to fully initialize. This method
        provides realistic progress updates while waiting.

        Args:
            task: Task object for the launched instance
            session_id: Session identifier
            timeout: Maximum wait time in seconds

        Returns:
            ColabConnection with all details populated

        Raises:
            FlowError: If instance fails to start or timeout occurs
        """
        start_time = time.time()
        last_status = None
        # Avoid fake progress spinners; print neutral, time-based updates only
        dots = 0  # kept for compatibility; no animated usage below
        jupyter_token = None
        instance_ip = None
        remote_port_val: Optional[int] = None

        while time.time() - start_time < timeout:
            elapsed = int(time.time() - start_time)

            # Get current status
            try:
                task = self.flow.get_task(task.task_id)
                status = task.status
            except Exception as e:
                logger.error(f"Failed to get task status: {e}")
                status = TaskStatus.FAILED

            # Show status updates with better visuals
            if status != last_status:
                if status == TaskStatus.PENDING:
                    if last_status is None:
                        print("\nInstance allocation started...")
                elif status == TaskStatus.RUNNING:
                    print(f"\nInstance running ({elapsed // 60}m {elapsed % 60}s)")
                    print("Preparing Jupyter environment...")
                elif status == TaskStatus.FAILED:
                    print("\nERROR: Instance failed to start")
                    raise FlowError(f"Task {task.task_id} failed: {task.message}")
                last_status = status

            # Neutral periodic update while pending (no spinner)
            if status == TaskStatus.PENDING:
                print(
                    f"\rPending... {elapsed // 60}m {elapsed % 60}s",
                    end="",
                    flush=True,
                )

            # Once running, check for Jupyter token and SSH
            if status == TaskStatus.RUNNING:
                # Get instance IP if not already obtained
                if not instance_ip and task.ssh_host:
                    instance_ip = task.ssh_host

                # Retrieve Jupyter token securely via SSH by reading config (avoid log scraping)
                if not jupyter_token and instance_ip:
                    try:
                        remote_ops = self.flow.get_remote_operations()
                        # Extract token value from jupyter_notebook_config.py without echoing it to provider logs
                        cmd = "awk -F\"'\" '/^c.NotebookApp.token/ {print $2}' ~/.jupyter/jupyter_notebook_config.py"
                        token_output = remote_ops.execute_command(task.task_id, cmd)
                        candidate = (token_output or "").strip()
                        if candidate:
                            jupyter_token = candidate
                            print("\nJupyter token obtained")
                    except Exception:
                        # Fallback to waiting
                        pass

                # Also retrieve remote port from the file we wrote
                if instance_ip and remote_port_val is None:
                    try:
                        remote_ops = self.flow.get_remote_operations()
                        port_output = remote_ops.execute_command(task.task_id, "cat ~/.jupyter/colab_port || true")
                        port_str = (port_output or "").strip()
                        if port_str.isdigit():
                            remote_port_val = int(port_str)
                    except Exception:
                        pass

                # Once we have token and port, verify Jupyter HTTP is responding remotely
                jupyter_http_ok = False
                if instance_ip and (remote_port_val is not None) and jupyter_token:
                    try:
                        remote_ops = self.flow.get_remote_operations()
                        check_cmd = (
                            f"python -c \"import urllib.request; "
                            f"urllib.request.urlopen('http://127.0.0.1:{remote_port_val}/api/status', timeout=2); "
                            f"print('OK')\""
                        )
                        http_out = (remote_ops.execute_command(task.task_id, check_cmd) or "").strip()
                        if "OK" in http_out:
                            jupyter_http_ok = True
                            print("Jupyter HTTP responding")
                    except Exception:
                        # Keep waiting
                        pass

                # Check if we have everything needed
                if instance_ip and jupyter_token and (remote_port_val is not None) and jupyter_http_ok:
                    # Verify SSH access
                    if self._verify_ssh_access(instance_ip):
                        print("\nSSH access confirmed")

                        # Create connection object
                        return ColabConnection(
                            connection_url=f"http://localhost:{remote_port_val}/?token={jupyter_token}",
                            ssh_command=f"ssh -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=60 -o ServerAliveCountMax=2 -L 8888:localhost:{remote_port_val} {task.ssh_user}@{instance_ip}",
                            instance_ip=instance_ip,
                            instance_type=task.instance_type,
                            task_id=task.task_id,
                            session_id=session_id,
                            created_at=datetime.now(timezone.utc),
                            jupyter_token=jupyter_token,
                            remote_port=remote_port_val,
                        )
                    else:
                        print(
                            f"\rWaiting for SSH... {elapsed // 60}m {elapsed % 60}s",
                            end="",
                            flush=True,
                        )
                else:
                    print(
                        f"\rWaiting for Jupyter... {elapsed // 60}m {elapsed % 60}s",
                        end="",
                        flush=True,
                    )

            time.sleep(5)

        # Timeout reached
        raise FlowError(f"Instance not ready after {timeout // 60} minutes")

    def _verify_ssh_access(self, host: str, port: int = 22) -> bool:
        """Verify SSH port is accessible.

        Args:
            host: Hostname or IP address
            port: SSH port (default 22)

        Returns:
            True if SSH is accessible, False otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def _establish_ssh_tunnel(self, connection: ColabConnection) -> None:
        """Attempt to establish SSH tunnel automatically.

        This is a future enhancement - for now just log intent.

        Args:
            connection: Connection details
        """
        logger.info(f"Auto-tunnel requested for {connection.task_id}")
        # Future: Use subprocess to establish tunnel in background
        # For now, user must run SSH command manually

    def disconnect(self, session_id: str) -> None:
        """Disconnect and terminate a Colab session.

        Args:
            session_id: Session to disconnect

        Raises:
            ValueError: If session not found
        """
        if session_id not in self._active_connections:
            raise ValueError(f"Session {session_id} not found")

        connection = self._active_connections[session_id]

        # Stop the task
        try:
            self.flow.stop(connection.task_id)
            print(f"Disconnected session {session_id}")
        except Exception as e:
            logger.error(f"Failed to stop task {connection.task_id}: {e}")
            raise FlowError(f"Failed to disconnect session: {str(e)}")
        finally:
            # Remove from active connections
            del self._active_connections[session_id]

    def list_sessions(self) -> List[Dict[str, str]]:
        """List all active Colab sessions.

        Returns:
            List of session dictionaries with connection details
        """
        sessions = []

        for session_id, connection in self._active_connections.items():
            # Get current task status
            try:
                task = self.flow.get_task(connection.task_id)
                status = task.status.value
            except TaskNotFoundError:
                status = "terminated"
            except Exception:
                status = "unknown"

            sessions.append(
                {
                    "session_id": session_id,
                    "instance_type": connection.instance_type,
                    "status": status,
                    "created_at": connection.created_at.isoformat(),
                    "connection_url": connection.connection_url,
                    "ssh_command": connection.ssh_command,
                }
            )

        return sessions

    def get_startup_progress(self, task_id: str) -> str:
        """Extract detailed startup progress from logs.

        Args:
            task_id: Task ID to check

        Returns:
            Progress message based on log content
        """
        try:
            logs = self.flow.logs(task_id, tail=50)

            if "JUPYTER_READY=true" in logs:
                return "Jupyter server ready!"
            elif re.search(r"Starting Jupyter server on port \d+", logs):
                return "Starting Jupyter server..."
            elif "Installing dependencies" in logs or "pip install" in logs:
                return "Installing dependencies..."
            elif "Starting Jupyter server for Google Colab" in logs:
                return "Initializing Jupyter environment..."
            else:
                return "Instance initializing..."
        except Exception:
            return "Waiting for instance..."
