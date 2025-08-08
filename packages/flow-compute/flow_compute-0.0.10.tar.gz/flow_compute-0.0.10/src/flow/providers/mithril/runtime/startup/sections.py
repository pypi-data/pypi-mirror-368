"""Script section implementations with clear separation of concerns.

Each section is responsible for generating a specific part of the startup script.
This separation allows for easy testing, extension, and modification.
"""

import logging
import textwrap
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Protocol

from flow.core.docker import DockerConfig

from .utils import (
    ensure_command_available,
    ensure_curl_available,
    ensure_docker_available,
    ensure_basic_tools,
    get_command_fallback,
)
from ...core.constants import (
    MITHRIL_LOG_DIR,
    MITHRIL_STARTUP_LOG,
    FLOW_LEGACY_LOG_DIR,
    FLOW_LOG_DIR,
    GPU_INSTANCE_PATTERNS,
)
from ...volume_operations import VolumeOperations

logger = logging.getLogger(__name__)


@dataclass
class ScriptContext:
    """Context passed to script sections for generation.

    Contains all configuration needed to generate startup script sections.
    Each script section can access this context to determine what to generate
    and how to configure the instance.

    Attributes:
        ports: List of ports to expose through the bastion.
        volumes: List of volume configurations to mount.
        docker_image: Docker image to run, if any.
        docker_command: Command to run in the Docker container.
        user_script: Custom shell script to execute during startup.
        environment: Environment variables to set.
        upload_code: Whether to extract uploaded code archive.
        code_archive: Base64-encoded gzipped tar archive of user code.
        max_run_time_hours: Maximum runtime before auto-termination.
        min_run_time_hours: Minimum guaranteed runtime.
        deadline_hours: Hours until task deadline.
    """

    ports: list[int] = None
    volumes: list[dict[str, Any]] = None
    docker_image: str | None = None
    docker_command: list[str] | None = None
    user_script: str | None = None
    environment: dict[str, str] = None
    upload_code: bool = False
    code_archive: str | None = None  # Base64 encoded tar.gz
    instance_type: str | None = None  # Added for GPU detection
    enable_workload_resume: bool = True  # Enable automatic workload resumption
    task_id: str | None = None  # Task ID for state tracking
    task_name: str | None = None  # Task name for identification
    # Runtime limit fields
    max_run_time_hours: float | None = None
    min_run_time_hours: float | None = None
    deadline_hours: float | None = None

    def __post_init__(self):
        """Initialize default values for mutable attributes."""
        self.ports = self.ports or []
        self.volumes = self.volumes or []
        self.environment = self.environment or {}

    @property
    def has_gpu(self) -> bool:
        """Check if this is a GPU instance based on instance type."""
        if not self.instance_type:
            return False

        instance_lower = self.instance_type.lower()
        return any(pattern in instance_lower for pattern in GPU_INSTANCE_PATTERNS)


class IScriptSection(Protocol):
    """Protocol for script sections."""

    @property
    def name(self) -> str:
        """Section name for identification."""
        ...

    @property
    def priority(self) -> int:
        """Execution priority (lower numbers run first)."""
        ...

    def should_include(self, context: ScriptContext) -> bool:
        """Determine if this section should be included."""
        ...

    def generate(self, context: ScriptContext) -> str:
        """Generate the script section content."""
        ...

    def validate(self, context: ScriptContext) -> list[str]:
        """Validate the context for this section. Return list of errors."""
        ...


class ScriptSection(ABC):
    """Base class for script sections."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    def priority(self) -> int:
        return 50  # Default middle priority

    def should_include(self, context: ScriptContext) -> bool:
        """By default, include if generate returns non-empty content."""
        return bool(self.generate(context).strip())

    @abstractmethod
    def generate(self, context: ScriptContext) -> str:
        pass

    def validate(self, context: ScriptContext) -> list[str]:
        """Default validation (none)."""
        return []


class HeaderSection(ScriptSection):
    """Generate script header with safety checks."""

    @property
    def name(self) -> str:
        return "header"

    @property
    def priority(self) -> int:
        return 10  # Always first

    def should_include(self, context: ScriptContext) -> bool:
        return True  # Always include header

    def generate(self, context: ScriptContext) -> str:
        return textwrap.dedent(
            f"""
            #!/bin/bash
            set -euxo pipefail
            
            # Mithril Startup Script with SLURM-like logging
            echo "Starting Mithril instance initialization at $(date)"
            
            # Ensure we're running as root
            if [ "$EUID" -ne 0 ]; then
                echo "Error: Script must run as root" >&2
                exit 1
            fi
            
            {ensure_basic_tools()}
            
            # Get task ID from various sources
            # Try: task name from Flow, hostname, or generate UUID
            TASK_NAME="{context.task_name if hasattr(context, "task_name") else ""}"
            TASK_ID="${{TASK_NAME:-${{HOSTNAME:-$(command -v uuidgen >/dev/null 2>&1 && uuidgen || echo "task-$(date +%s)-$$")}}}}"
            
            # Create log directories
            LOG_DIR="{FLOW_LOG_DIR}"
            mkdir -p "$LOG_DIR"
            mkdir -p {FLOW_LEGACY_LOG_DIR}  # Legacy directory for compatibility
            
            # Create SLURM-like log files
            STDOUT_LOG="$LOG_DIR/$TASK_ID.out"
            STDERR_LOG="$LOG_DIR/$TASK_ID.err"
            COMBINED_LOG="$LOG_DIR/$TASK_ID.log"
            
            # Create symlink for legacy compatibility
            ln -sf "$COMBINED_LOG" {FLOW_LEGACY_LOG_DIR}/startup.log
            
            # Redirect outputs to separate files (like SLURM)
            exec 1> >(tee -a "$STDOUT_LOG" "$COMBINED_LOG")
            exec 2> >(tee -a "$STDERR_LOG" "$COMBINED_LOG" >&2)
            
            # Log startup information
            echo "[$(date)] Task $TASK_ID starting on $(hostname)"
            echo "Logs: stdout=$STDOUT_LOG stderr=$STDERR_LOG combined=$COMBINED_LOG"
            
            # Create Mithril-compatible log locations
            echo "Creating Mithril log symlinks..."
            mkdir -p {MITHRIL_LOG_DIR}
            ln -sf "$COMBINED_LOG" {MITHRIL_STARTUP_LOG}
        """
        ).strip()


class PortForwardingSection(ScriptSection):
    """Configure port forwarding through Mithril bastion."""

    @property
    def name(self) -> str:
        return "port_forwarding"

    @property
    def priority(self) -> int:
        return 20

    def should_include(self, context: ScriptContext) -> bool:
        return bool(context.ports)

    def generate(self, context: ScriptContext) -> str:
        if not context.ports:
            return ""

        # Generate nginx configs
        nginx_configs = []
        for port in context.ports:
            nginx_configs.append(self._generate_nginx_config(port))

        return textwrap.dedent(
            f"""
            # Port forwarding setup
            echo "Configuring port forwarding for ports: {", ".join(map(str, context.ports))}"
            
            # Install nginx for local reverse proxy
            {ensure_command_available("nginx")}
            
            # Remove default site
            rm -f /etc/nginx/sites-enabled/default
            
            {chr(10).join(nginx_configs)}
            
            # Test and reload nginx
            nginx -t
            systemctl enable nginx
            systemctl restart nginx
            
            {self._generate_foundrypf_service()}
        """
        ).strip()

    def _generate_nginx_config(self, port: int) -> str:
        """Generate nginx configuration for a single port."""
        return textwrap.dedent(
            f"""
            # Configure port {port}
            cat > /etc/nginx/sites-available/port{port} <<'NGINX_EOF'
            server {{
                listen {port};
                server_name _;
                
                location / {{
                    proxy_pass http://127.0.0.1:{port};
                    proxy_http_version 1.1;
                    proxy_set_header Upgrade $http_upgrade;
                    proxy_set_header Connection 'upgrade';
                    proxy_set_header Host $host;
                    proxy_set_header X-Real-IP $remote_addr;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                    proxy_set_header X-Forwarded-Proto $scheme;
                    proxy_cache_bypass $http_upgrade;
                    proxy_read_timeout 86400;
                }}
            }}
            NGINX_EOF
            ln -sf /etc/nginx/sites-available/port{port} /etc/nginx/sites-enabled/
        """
        ).strip()

    def _generate_foundrypf_service(self) -> str:
        """Generate systemd service for foundrypf."""
        return textwrap.dedent(
            """
            # Create systemd service for foundrypf
            cat > /etc/systemd/system/foundrypf.service <<'SYSTEMD_EOF'
            [Unit]
            Description=Foundry Port Forwarding
            After=network-online.target
            Wants=network-online.target
            
            [Service]
            Type=simple
            ExecStart=/usr/local/bin/foundrypf
            Restart=always
            RestartSec=10
            StandardOutput=journal
            StandardError=journal
            SyslogIdentifier=foundrypf
            
            [Install]
            WantedBy=multi-user.target
            SYSTEMD_EOF
            
            systemctl daemon-reload
            systemctl enable foundrypf
            systemctl start foundrypf
        """
        ).strip()

    def validate(self, context: ScriptContext) -> list[str]:
        errors = []
        for port in context.ports:
            if not (1 <= port <= 65535):
                errors.append(f"Invalid port number: {port}")
        return errors


class VolumeSection(ScriptSection):
    """Handle volume mounting with proper error handling."""

    @property
    def name(self) -> str:
        return "volumes"

    @property
    def priority(self) -> int:
        return 30

    def should_include(self, context: ScriptContext) -> bool:
        return bool(context.volumes)

    def generate(self, context: ScriptContext) -> str:
        if not context.volumes:
            return ""

        mount_commands = []
        for i, volume in enumerate(context.volumes):
            # Check if this is a file share
            if volume.get("interface") == "file":
                mount_commands.append(self._generate_file_mount(i, volume))
            else:
                mount_commands.append(self._generate_block_mount(i, volume))

        return textwrap.dedent(
            f"""
            # Volume mounting
            echo "Mounting {len(context.volumes)} volume(s)"
            
            {chr(10).join(mount_commands)}
            
            # Verify all mounts
            echo "Mounted volumes:"
            mount | grep -E "(^/dev/(vd|xvd)[f-z]|type nfs)"
        """
        ).strip()

    def _generate_file_mount(self, index: int, volume: dict[str, Any]) -> str:
        """Mount file share using shared volume operations."""
        mount_path = volume.get("mount_path", f"/data{index}")
        volume_id = volume.get("volume_id")

        return VolumeOperations.generate_mount_script(
            volume_index=index, mount_path=mount_path, volume_id=volume_id, is_file_share=True
        )

    def _generate_block_mount(self, index: int, volume: dict[str, Any]) -> str:
        """Mount block storage device using shared volume operations."""
        mount_path = volume.get("mount_path", f"/data{index}")
        # Volumes at startup use device letters starting from 'f' (after system disks)
        volume_index = index + 2  # Skip vda/b (system), vdc (local), vdd/e reserved

        return VolumeOperations.generate_mount_script(
            volume_index=volume_index,
            mount_path=mount_path,
            format_if_needed=True,
            add_to_fstab=True,
            is_file_share=False,
        )

    def validate(self, context: ScriptContext) -> list[str]:
        errors = []
        if len(context.volumes) > 20:  # AWS limit
            errors.append(f"Too many volumes: {len(context.volumes)} (max 20)")

        for i, volume in enumerate(context.volumes):
            mount_path = volume.get("mount_path", f"/data{i}")
            if not mount_path.startswith("/"):
                errors.append(f"Volume {i}: mount_path must be absolute: {mount_path}")

        return errors


class S3Section(ScriptSection):
    """Handle S3 mounting via s3fs."""

    @property
    def name(self) -> str:
        return "s3_mounts"

    @property
    def priority(self) -> int:
        return 35  # After volumes, before docker

    def should_include(self, context: ScriptContext) -> bool:
        # Check if we have S3 mount environment variables
        return any(
            k.startswith("S3_MOUNT_") and k.endswith("_BUCKET") for k in context.environment.keys()
        )

    def generate(self, context: ScriptContext) -> str:
        # Count S3 mounts
        mount_count = int(context.environment.get("S3_MOUNTS_COUNT", "0"))
        if mount_count == 0:
            return ""

        mount_commands = []
        for i in range(mount_count):
            mount_key = f"S3_MOUNT_{i}"
            bucket = context.environment.get(f"{mount_key}_BUCKET")
            path = context.environment.get(f"{mount_key}_PATH", "")
            target = context.environment.get(f"{mount_key}_TARGET")

            if bucket and target:
                mount_commands.append(self._generate_s3_mount(bucket, path, target))

        return textwrap.dedent(
            f"""
            # S3 mounting via s3fs
            echo "Setting up S3 mounts"
            
            # Install s3fs
            {ensure_command_available("s3fs")}
            
            # Create credential file for s3fs
            echo "${{AWS_ACCESS_KEY_ID}}:${{AWS_SECRET_ACCESS_KEY}}" > /tmp/s3fs_passwd
            chmod 600 /tmp/s3fs_passwd
            
            {chr(10).join(mount_commands)}
            
            # Verify S3 mounts
            echo "S3 mounts configured:"
            mount | grep s3fs
        """
        ).strip()

    def _generate_s3_mount(self, bucket: str, path: str, target: str) -> str:
        """Generate s3fs mount command for a single S3 location."""
        s3_path = f"{bucket}:/{path}" if path else bucket

        return textwrap.dedent(
            f"""
            # Mount S3: {bucket}/{path} -> {target}
            echo "Mounting S3 bucket {bucket} to {target}"
            
            # Create mount point
            mkdir -p {target}
            
            # Mount with s3fs
            s3fs {s3_path} {target} \\
                -o passwd_file=/tmp/s3fs_passwd \\
                -o allow_other \\
                -o use_cache=/tmp/s3fs_cache \\
                -o ro \\
                -o retries=5 \\
                -o connect_timeout=10 \\
                -o readwrite_timeout=30
            
            # Verify mount
            if mountpoint -q {target}; then
                echo "Successfully mounted S3 to {target}"
            else
                echo "ERROR: Failed to mount S3 to {target}" >&2
                exit 1
            fi
        """
        ).strip()

    def validate(self, context: ScriptContext) -> list[str]:
        errors = []

        # Check for AWS credentials
        if not context.environment.get("AWS_ACCESS_KEY_ID"):
            errors.append("AWS_ACCESS_KEY_ID not set in environment")
        if not context.environment.get("AWS_SECRET_ACCESS_KEY"):
            errors.append("AWS_SECRET_ACCESS_KEY not set in environment")

        return errors


class CodeUploadSection(ScriptSection):
    """Extract and prepare uploaded local code.

    This section handles extracting user code that was packaged and embedded
    in the startup script. The code archive is base64-encoded and gzipped
    to minimize startup script size while preserving directory structure.

    The extracted code is placed in /workspace, which becomes the working
    directory for Docker containers when upload_code=True.
    """

    @property
    def name(self) -> str:
        """Return section identifier.

        Returns:
            str: Section name used for identification and debugging.
        """
        return "code_upload"

    @property
    def priority(self) -> int:
        """Return execution priority.

        Returns:
            int: Priority value (35) - runs after volumes, before Docker.
        """
        return 35  # After volumes, before Docker

    def should_include(self, context: ScriptContext) -> bool:
        """Determine if code upload section should be included.

        Args:
            context: Script generation context containing upload settings.

        Returns:
            bool: True if upload_code is enabled and archive is provided.
        """
        return context.upload_code and context.code_archive is not None

    def generate(self, context: ScriptContext) -> str:
        """Generate shell script to extract uploaded code.

        Args:
            context: Script generation context with code archive.

        Returns:
            str: Shell script that extracts code to /workspace.
        """
        if not context.upload_code or not context.code_archive:
            return ""

        return textwrap.dedent(
            f"""
            # Extract uploaded code
            echo "Extracting uploaded code to /workspace..."
            mkdir -p /workspace
            cd /workspace
            
            # Decode and extract the code archive
            echo "{context.code_archive}" | base64 -d | tar -xzf -
            
            # List extracted files
            echo "Extracted files:"
            ls -la
            
            # Set proper permissions
            chmod -R 755 /workspace
        """
        ).strip()

    def validate(self, context: ScriptContext) -> list[str]:
        """Validate context for code upload requirements.

        Args:
            context: Script generation context to validate.

        Returns:
            List[str]: List of validation errors, empty if valid.
        """
        errors = []
        if context.upload_code and not context.code_archive:
            errors.append("upload_code is True but no code archive provided")
        return errors


class DevVMDockerSection(ScriptSection):
    """Docker setup for dev VMs - ensures Docker is available on the host."""

    @property
    def name(self) -> str:
        return "dev_vm_docker"

    @property
    def priority(self) -> int:
        return 38  # Before DockerSection

    def should_include(self, context: ScriptContext) -> bool:
        # Only include if this is a dev VM
        return context.environment.get("FLOW_DEV_VM") == "true"

    def generate(self, context: ScriptContext) -> str:
        # For dev VMs, we just need Docker on the host to run the privileged container
        # The actual Docker installation inside the container happens via the command
        return textwrap.dedent(
            """
            # Docker setup for dev VM host
            echo "Ensuring Docker is available on host for dev VM"
            
            # Install Docker on host if not present
            {ensure_docker_available()}
            
            # Create persistent home directory for dev containers
            echo "Creating persistent home directory..."
            mkdir -p /home/persistent
            chmod 755 /home/persistent
            
            echo "Docker and persistent storage ready for dev VM"
            """
        ).strip()


class DockerSection(ScriptSection):
    """Docker installation and container management."""

    @property
    def name(self) -> str:
        return "docker"

    @property
    def priority(self) -> int:
        return 40

    def should_include(self, context: ScriptContext) -> bool:
        return bool(context.docker_image)

    def generate(self, context: ScriptContext) -> str:
        if not context.docker_image:
            return ""

        docker_run_cmd = self._build_docker_run_command(context)

        # For dev VMs, we need to install Docker inside the container
        dev_vm_docker_setup = ""
        if context.environment.get("FLOW_DEV_VM") == "true":
            dev_vm_docker_setup = textwrap.dedent(
                """
                # Install Docker inside the container for dev VM
                docker exec main bash -c '
                    if ! command -v docker >/dev/null 2>&1; then
                        echo "Installing Docker inside dev container..."
                        if ! command -v curl >/dev/null 2>&1; then
                            apt-get update -qq && apt-get install -y -qq curl ca-certificates
                        fi
                        curl -fsSL https://get.docker.com | sh
                        # Add Docker group permissions
                        groupadd -f docker
                        usermod -aG docker root || true
                    fi
                '
                """
            ).strip()

        # GPU-specific setup
        gpu_setup = ""
        if context.has_gpu:
            gpu_setup = textwrap.dedent(
                """
                # Install NVIDIA Container Toolkit for GPU support
                echo "Installing NVIDIA Container Toolkit..."
                {ensure_command_available('curl')}
                distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
                curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
                curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list
                apt-get update && apt-get install -y nvidia-container-toolkit
                systemctl restart docker
                
                # Wait for Docker to be ready after restart
                timeout 30 sh -c 'until docker info >/dev/null 2>&1; do sleep 1; done'
                
                # Verify GPU support
                echo "Verifying GPU support in Docker..."
                docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi || echo "Warning: GPU test failed"
                """
            ).strip()

        # Get registry authentication if needed
        registry_auth = self._get_registry_auth_script(context)

        return textwrap.dedent(
            f"""
            # Docker setup
            echo "Setting up Docker and running {context.docker_image}"
            
            # Install Docker
            {ensure_docker_available()}
            
            {gpu_setup}
            
            {registry_auth}
            
            # Pull the image if not already present
            echo "Checking Docker image: {context.docker_image}"
            docker image inspect {context.docker_image} >/dev/null 2>&1 || docker pull {context.docker_image}
            
            # Run the container
            echo "Starting container..."
            {docker_run_cmd}
            
            # Verify container is running
            sleep 5
            docker ps
            docker logs main --tail 50
            
            # Save task state for resume functionality
            {self._generate_task_state_save(context)}
        """
        ).strip()

    def _build_docker_run_command(self, context: ScriptContext) -> str:
        """Build the docker run command with all options."""
        cmd_parts = [
            "docker run",
            "-d",
            "--restart=unless-stopped",
            "--name=main",
            "--log-driver=json-file",
            "--log-opt max-size=100m",
            "--log-opt max-file=3",
        ]

        # For dev VMs, add privileged mode and volume for Docker socket
        if context.environment.get("FLOW_DEV_VM") == "true":
            cmd_parts.extend(
                [
                    "--privileged",
                    "-v",
                    "/var/run/docker.sock:/var/run/docker.sock",
                    "-v",
                    "/var/lib/docker:/var/lib/docker",
                    # Mount persistent home directory
                    "-v",
                    "/home/persistent:/root",
                    # Set working directory to home
                    "-w",
                    "/root",
                ]
            )

        # Add GPU support if this is a GPU instance
        if context.has_gpu:
            cmd_parts.append("--gpus all")

        # Add port mappings
        for port in context.ports:
            cmd_parts.append(f"-p {port}:{port}")

        # Add volume mounts
        for i, volume in enumerate(context.volumes):
            mount_path = volume.get("mount_path", f"/data{i}")
            # Use centralized Docker configuration to check mount restrictions
            if not DockerConfig.should_mount_in_container(mount_path):
                logger.debug(f"Skipping restricted mount path '{mount_path}' inside container")
                continue
            cmd_parts.append(f"-v {mount_path}:{mount_path}")

        # Add working directory if code was uploaded (skip for dev VMs, already set)
        if context.upload_code and context.environment.get("FLOW_DEV_VM") != "true":
            cmd_parts.append("-w /workspace")
            # Also mount /workspace from host to container
            cmd_parts.append("-v /workspace:/workspace")

        # Add environment variables
        for key, value in context.environment.items():
            cmd_parts.append(f'-e {key}="{value}"')

        # Add image
        cmd_parts.append(context.docker_image)

        # Add command if specified
        if context.docker_command:
            # docker_command is now a list from TaskConfig validation
            # Need to properly handle command execution
            import shlex

            # Check if this looks like a shell command that needs bash -c
            # This includes commands with shell operators like &&, ||, ;, |, etc.
            needs_shell = False
            if len(context.docker_command) == 1:
                cmd_str = context.docker_command[0]
                # Check for shell operators or multi-line commands
                shell_operators = ["&&", "||", ";", "|", ">", "<", "\n"]
                if any(op in cmd_str for op in shell_operators):
                    needs_shell = True

            if needs_shell:
                # Use bash -c to execute shell commands
                cmd_parts.extend(["bash", "-c", shlex.quote(context.docker_command[0])])
            else:
                # Regular command with arguments
                for arg in context.docker_command:
                    cmd_parts.append(shlex.quote(arg))

        return " \\\n    ".join(cmd_parts)

    def validate(self, context: ScriptContext) -> list[str]:
        errors = []
        # Only warn about images that look like they need a registry
        if (
            context.docker_image
            and "/" not in context.docker_image
            and ":" not in context.docker_image
        ):
            # Skip validation for common official images
            official_images = {
                "ubuntu",
                "debian",
                "alpine",
                "centos",
                "fedora",
                "nginx",
                "redis",
                "postgres",
                "mysql",
                "python",
                "node",
                "golang",
            }
            image_name = context.docker_image.split(":")[0]
            if image_name not in official_images:
                errors.append(
                    f"Docker image should include registry/namespace: {context.docker_image}"
                )
        return errors

    def _generate_task_state_save(self, context: ScriptContext) -> str:
        """Generate commands to save task state for resume functionality."""
        if not context.enable_workload_resume:
            return ""

        return textwrap.dedent(
            f"""
            # Save task state for workload resume
            mkdir -p /var/lib/flow
            cat > /var/lib/flow/task-state <<'TASK_STATE_EOF'
            # Flow Task State
            # This file is used to resume workloads after preemption/relocation
            TASK_ID="$HOSTNAME"
            TASK_NAME="{context.task_name or "unknown"}"
            TASK_TYPE="docker"
            DOCKER_IMAGE="{context.docker_image}"
            DOCKER_COMMAND='{" ".join(repr(arg) for arg in context.docker_command) if context.docker_command else ""}'
            WORKLOAD_STARTED="$(date -Iseconds)"
            # Save key environment variables
{self._generate_env_vars_for_state(context)}
            TASK_STATE_EOF
            echo "Task state saved for resume functionality"
            """
        ).strip()

    def _generate_env_vars_for_state(self, context: ScriptContext) -> str:
        """Generate environment variable declarations for task state."""
        if not context.environment:
            return ""

        env_lines = []
        for key, value in context.environment.items():
            # Skip internal/sensitive variables
            if key.startswith("_") or "KEY" in key or "SECRET" in key or "PASSWORD" in key:
                continue
            # Escape the value for shell
            escaped_value = value.replace('"', '\\"').replace("$", "\\$").replace("`", "\\`")
            env_lines.append(f'            ENV_{key}="{escaped_value}"')

        return "\n".join(env_lines) if env_lines else ""

    def _get_registry_auth_script(self, context: ScriptContext) -> str:
        """Generate ECR authentication if detected and AWS credentials present."""
        if not context.docker_image:
            return ""

        # ECR: 123456789.dkr.ecr.region.amazonaws.com
        import re

        ecr_pattern = r"^(\d+)\.dkr\.ecr\.([a-z0-9-]+)\.amazonaws\.com"
        match = re.match(ecr_pattern, context.docker_image)

        if match and context.environment.get("AWS_ACCESS_KEY_ID"):
            region = match.group(2)
            registry = match.group(0)
            return textwrap.dedent(
                f"""
            # ECR Authentication
            {ensure_command_available("aws")}
            if command -v aws >/dev/null 2>&1; then
                aws ecr get-login-password --region {region} | \\
                    docker login --username AWS --password-stdin {registry}
            else
                echo "WARNING: AWS CLI not available for ECR authentication"
            fi
            """
            ).strip()

        return ""


class UserScriptSection(ScriptSection):
    """Execute user-provided startup script."""

    @property
    def name(self) -> str:
        return "user_script"

    @property
    def priority(self) -> int:
        return 90  # Run near the end

    def should_include(self, context: ScriptContext) -> bool:
        return bool(context.user_script and context.user_script.strip())

    def generate(self, context: ScriptContext) -> str:
        if not context.user_script or not context.user_script.strip():
            return ""

        # Ensure script has a shebang
        script_content = context.user_script.strip()
        if not script_content.startswith("#!"):
            script_content = "#!/bin/bash\n" + script_content

        return textwrap.dedent(
            f"""
            # User startup script
            echo "Executing user startup script"
            
            cat > /tmp/user_startup.sh <<'USER_SCRIPT_EOF'
            {script_content}
            USER_SCRIPT_EOF
            
            chmod +x /tmp/user_startup.sh
            /tmp/user_startup.sh
            
            echo "User startup script completed"
            
            {self._generate_task_state_save(context)}
        """
        ).strip()

    def _generate_task_state_save(self, context: ScriptContext) -> str:
        """Generate commands to save task state for resume functionality."""
        if not context.enable_workload_resume:
            return ""

        return textwrap.dedent(
            f"""
            # Save task state for workload resume
            mkdir -p /var/lib/flow
            cat > /var/lib/flow/task-state <<'TASK_STATE_EOF'
            # Flow Task State
            # This file is used to resume workloads after preemption/relocation
            TASK_ID="$HOSTNAME"
            TASK_NAME="{context.task_name or "unknown"}"
            TASK_TYPE="script"
            USER_SCRIPT_PATH="/tmp/user_startup.sh"
            WORKLOAD_STARTED="$(date -Iseconds)"
            TASK_STATE_EOF
            echo "Task state saved for resume functionality"
            """
        ).strip()


class WorkloadResumeSection(ScriptSection):
    """Create systemd service for automatic workload resumption after preemption.

    This section creates a systemd service that runs on every boot to detect
    if this is a fresh start or a resume after preemption/relocation. It handles
    both Docker and non-Docker workloads, automatically resuming work from the
    last known state.

    The service:
    - Checks for previous task state markers
    - Detects if Docker containers need to be restarted
    - Re-runs user scripts if configured for resume
    - Preserves task continuity across instance lifecycle events
    """

    @property
    def name(self) -> str:
        return "workload_resume"

    @property
    def priority(self) -> int:
        return 85  # After Docker (40) and before UserScript (90)

    def should_include(self, context: ScriptContext) -> bool:
        """Include if there's a workload to resume (Docker or user script)."""
        return context.enable_workload_resume and bool(
            context.docker_image or (context.user_script and context.user_script.strip())
        )

    def generate(self, context: ScriptContext) -> str:
        """Generate systemd service for workload resumption."""
        # Create the resume script content
        resume_script = self._generate_resume_script(context)

        # Create the systemd service
        systemd_service = self._generate_systemd_service()

        return textwrap.dedent(
            f"""
            # Workload Resume Service Setup
            echo "Setting up automatic workload resumption service"
            
            # Create state directory
            mkdir -p /var/lib/flow
            
            # Create resume script
            cat > /usr/local/sbin/flow-workload-resume.sh <<'RESUME_SCRIPT_EOF'
{resume_script}
RESUME_SCRIPT_EOF
            
            chmod +x /usr/local/sbin/flow-workload-resume.sh
            
            # Create systemd service
            cat > /etc/systemd/system/flow-workload-resume.service <<'SYSTEMD_SERVICE_EOF'
{systemd_service}
SYSTEMD_SERVICE_EOF
            
            # Enable the service to run on boot
            systemctl daemon-reload
            systemctl enable flow-workload-resume.service
            
            echo "Workload resume service configured successfully"
            """
        ).strip()

    def validate(self, context: ScriptContext) -> list[str]:
        """Validate resume configuration."""
        return []

    def _generate_resume_script(self, context: ScriptContext) -> str:
        """Generate the resume script that handles both Docker and non-Docker workloads."""
        # Determine what type of workload we're resuming
        if context.docker_image:
            workload_check = self._generate_docker_resume_logic(context)
        else:
            workload_check = self._generate_script_resume_logic(context)

        return textwrap.dedent(
            f"""#!/bin/bash
            set -euo pipefail
            
            # Flow Workload Resume Script
            # This script runs on every boot to resume workloads after preemption/relocation
            
            LOG_FILE="/var/log/flow/workload-resume.log"
            STATE_FILE="/var/lib/flow/task-state"
            BOOT_MARKER="/var/lib/flow/first-boot-completed"
            
            # Ensure log directory exists
            mkdir -p /var/log/flow
            
            # Logging function
            log() {{
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
            }}
            
            log "Starting workload resume check"
            
            # Check if this is the first boot
            if [ ! -f "$BOOT_MARKER" ]; then
                # First boot - mark it and exit (startup script handles everything)
                log "First boot detected, marking as completed"
                touch "$BOOT_MARKER"
                exit 0
            fi
            
            # Check if we have a previous task state
            if [ ! -f "$STATE_FILE" ]; then
                log "No previous task state found, this appears to be a fresh instance"
                exit 0
            fi
            
            log "Previous task state detected, checking workload status"
            
            # Source the task state
            source "$STATE_FILE"
            
            # Detect if this is a GPU instance
            GPU_INSTANCE=""
            if command -v nvidia-smi >/dev/null 2>&1; then
                GPU_INSTANCE="yes"
                log "GPU instance detected"
            fi
            
            # Restore volume mounts
            VOLUME_MOUNTS=""
            for mount in $(mount | grep -E "^/dev/(vd|xvd)[f-z]" | awk '{{print $3}}'); do
                if [ -d "$mount" ]; then
                    VOLUME_MOUNTS="$VOLUME_MOUNTS -v $mount:$mount"
                fi
            done
            log "Volume mounts: $VOLUME_MOUNTS"
            
            {workload_check}
            
            log "Workload resume check completed"
            """
        ).strip()

    def _generate_docker_resume_logic(self, context: ScriptContext) -> str:
        """Generate Docker-specific resume logic."""
        docker_cmd = self._build_docker_run_command_for_resume(context)

        return textwrap.dedent(
            f"""
            # Docker workload resume logic
            if command -v docker >/dev/null 2>&1; then
                # Check if our main container exists
                if docker ps -a --format '{{{{.Names}}}}' | grep -q '^main$'; then
                    CONTAINER_STATUS=$(docker inspect -f '{{{{.State.Status}}}}' main 2>/dev/null || echo "unknown")
                    log "Container 'main' status: $CONTAINER_STATUS"
                    
                    case "$CONTAINER_STATUS" in
                        "running")
                            log "Container is already running"
                            ;;
                        "exited"|"stopped")
                            log "Restarting stopped container"
                            docker start main
                            sleep 5
                            docker logs main --tail 50
                            ;;
                        *)
                            log "Container in unexpected state: $CONTAINER_STATUS"
                            log "Removing and recreating container"
                            docker rm -f main 2>/dev/null || true
                            {docker_cmd}
                            ;;
                    esac
                else
                    log "Container 'main' not found, creating new container"
                    {docker_cmd}
                fi
                
                # Verify container is running
                sleep 5
                if docker ps --format '{{{{.Names}}}}' | grep -q '^main$'; then
                    log "Container 'main' is running successfully"
                else
                    log "ERROR: Failed to start container 'main'"
                    exit 1
                fi
            else
                log "Docker not found, cannot resume Docker workload"
                exit 1
            fi
            """
        ).strip()

    def _generate_script_resume_logic(self, context: ScriptContext) -> str:
        """Generate logic for resuming user scripts."""
        if not context.user_script or not context.user_script.strip():
            return 'log "No user script to resume"'

        # Ensure script has a shebang
        script_content = context.user_script.strip()
        if not script_content.startswith("#!"):
            script_content = "#!/bin/bash\n" + script_content

        return textwrap.dedent(
            f"""
            # User script resume logic
            if [ -f /tmp/user_startup.sh ]; then
                log "Found user script, checking if it should be re-run"
                
                # Check if user script is meant to be idempotent/resumable
                # This is a simple check - in production, you might want more sophisticated logic
                if grep -q "FLOW_RESUME_SAFE" /tmp/user_startup.sh; then
                    log "User script marked as resume-safe, re-running"
                    /tmp/user_startup.sh
                else
                    log "User script not marked as resume-safe, skipping re-run"
                    log "To make your script resume-safe, add '# FLOW_RESUME_SAFE' comment"
                fi
            else
                log "Creating and running user script"
                cat > /tmp/user_startup.sh <<'USER_SCRIPT_EOF'
{script_content}
USER_SCRIPT_EOF
                chmod +x /tmp/user_startup.sh
                /tmp/user_startup.sh
            fi
            """
        ).strip()

    def _build_docker_run_command_for_resume(self, context: ScriptContext) -> str:
        """Build docker run command specifically for resume scenarios."""
        # Note: This reads environment variables from the saved state file
        # The actual command is built dynamically in the resume script
        return r"""docker run \
                    -d \
                    --restart=unless-stopped \
                    --name=main \
                    $([ -n "$GPU_INSTANCE" ] && echo "--gpus all") \
                    $(grep "^ENV_" "$STATE_FILE" 2>/dev/null | sed 's/^ENV_\([^=]*\)=\(.*\)/-e \1=\2/' | tr '\n' ' ' || true) \
                    $VOLUME_MOUNTS \
                    $([ -d /workspace ] && echo "-v /workspace:/workspace -w /workspace") \
                    "$DOCKER_IMAGE" \
                    $DOCKER_COMMAND"""

    def _generate_systemd_service(self) -> str:
        """Generate the systemd service definition."""
        return textwrap.dedent(
            """[Unit]
            Description=Flow Workload Resume Service
            After=network-online.target docker.service
            Wants=network-online.target
            # Only run if we have a previous task state (not first boot)
            ConditionPathExists=/var/lib/flow/task-state
            
            [Service]
            Type=oneshot
            ExecStart=/usr/local/sbin/flow-workload-resume.sh
            RemainAfterExit=yes
            StandardOutput=journal
            StandardError=journal
            SyslogIdentifier=flow-workload-resume
            
            [Install]
            WantedBy=multi-user.target"""
        ).strip()


class GPUdHealthSection(ScriptSection):
    """Install and configure GPUd health monitoring for GPU instances."""

    @property
    def name(self) -> str:
        return "gpud_health"

    @property
    def priority(self) -> int:
        return 55  # After volumes, before docker

    def should_include(self, context: ScriptContext) -> bool:
        # Only include if this is a GPU instance and health monitoring is enabled
        health_enabled = context.environment.get("FLOW_HEALTH_MONITORING", "true").lower() == "true"
        return context.has_gpu and health_enabled

    def generate(self, context: ScriptContext) -> str:
        # Extract configuration from environment
        gpud_version = context.environment.get("FLOW_GPUD_VERSION", "v0.5.1")
        gpud_port = context.environment.get("FLOW_GPUD_PORT", "15132")
        gpud_bind = context.environment.get("FLOW_GPUD_BIND", "127.0.0.1")

        # Metrics configuration
        metrics_endpoint = context.environment.get("FLOW_METRICS_ENDPOINT", "")
        metrics_interval = context.environment.get("FLOW_METRICS_INTERVAL", "60")
        metrics_auth_token = context.environment.get("FLOW_METRICS_AUTH_TOKEN", "")
        metrics_batch_size = context.environment.get("FLOW_METRICS_BATCH_SIZE", "10")

        # Task and instance info
        task_id = context.task_id or "unknown"
        task_name = context.task_name or "unknown"
        instance_type = context.instance_type or "unknown"

        return textwrap.dedent(
            f"""
            # GPUd Health Monitoring Setup
            log "Setting up GPUd health monitoring for GPU instance"
            
            # Mark that GPUd setup was attempted (for Flow health checks)
            echo "attempted" | sudo tee /var/run/flow-gpud-status > /dev/null
            
            # Install GPUd
            log "Installing GPUd {gpud_version}..."
            {ensure_curl_available()}
            if ! curl -fsSL https://pkg.gpud.dev/install.sh | bash -s -- {gpud_version}; then
                log "WARNING: Failed to install GPUd, health monitoring will be limited"
                echo "install_failed" | sudo tee /var/run/flow-gpud-status > /dev/null
                return 0  # Don't fail startup
            fi
            
            # Configure and start GPUd
            export GPUD_PORT="{gpud_port}"
            export GPUD_BIND="{gpud_bind}"
            
            log "Starting GPUd on ${{GPUD_BIND}}:${{GPUD_PORT}}..."
            if ! sudo gpud up --private --web-address="${{GPUD_BIND}}:${{GPUD_PORT}}"; then
                log "WARNING: Failed to start GPUd, health monitoring will be limited"
                echo "start_failed" | sudo tee /var/run/flow-gpud-status > /dev/null
                return 0  # Don't fail startup
            fi
            
            # Wait for GPUd to be ready
            GPUD_URL="http://${{GPUD_BIND}}:${{GPUD_PORT}}"
            GPUD_READY=false
            for i in {{1..30}}; do
                if curl -s -o /dev/null -w "%{{http_code}}" "${{GPUD_URL}}/healthz" 2>/dev/null | grep -q "200"; then
                    log "GPUd is ready at ${{GPUD_URL}}"
                    GPUD_READY=true
                    break
                fi
                sleep 2
            done
            
            if [ "$GPUD_READY" = "false" ]; then
                log "WARNING: GPUd did not become ready in time"
                echo "not_ready" | sudo tee /var/run/flow-gpud-status > /dev/null
                return 0  # Don't fail startup
            fi
            
            # Mark successful setup
            echo "running" | sudo tee /var/run/flow-gpud-status > /dev/null
            
            # Create metrics streaming script
            log "Setting up metrics streaming..."
            {ensure_command_available("python3")}
            cat > /usr/local/bin/flow-metrics-streamer.py << 'METRICS_SCRIPT_EOF'
#!/usr/bin/env python3
import json
import time
import requests
import socket
import os
import signal
import sys
from datetime import datetime
from typing import Dict, List, Any

# Configuration
GPUD_BASE_URL = "http://{gpud_bind}:{gpud_port}"
METRICS_ENDPOINT = "{metrics_endpoint}" if "{metrics_endpoint}" else None
METRICS_INTERVAL = {metrics_interval}
METRICS_AUTH_TOKEN = "{metrics_auth_token}" if "{metrics_auth_token}" else None
METRICS_BATCH_SIZE = {metrics_batch_size}
TASK_ID = "{task_id}"
TASK_NAME = "{task_name}"
INSTANCE_ID = socket.gethostname()
INSTANCE_TYPE = "{instance_type}"

# Metrics buffer for batching
metrics_buffer = []

def signal_handler(signum, frame):
    '''Handle shutdown gracefully.'''
    print(f"Received signal {{signum}}, flushing metrics and exiting...")
    if metrics_buffer:
        send_metrics_batch(metrics_buffer)
    sys.exit(0)

def collect_metrics() -> Dict[str, Any]:
    '''Collect all metrics from GPUd.'''
    metrics = {{
        "task_id": TASK_ID,
        "task_name": TASK_NAME,
        "instance_id": INSTANCE_ID,
        "instance_type": INSTANCE_TYPE,
        "timestamp": datetime.utcnow().isoformat(),
    }}
    
    # GPUd health check
    try:
        resp = requests.get(f"{{GPUD_BASE_URL}}/healthz", timeout=5)
        metrics["gpud_healthy"] = resp.status_code == 200
    except Exception as e:
        metrics["gpud_healthy"] = False
        print(f"Failed to check GPUd health: {{e}}")
    
    # Machine info
    try:
        resp = requests.get(f"{{GPUD_BASE_URL}}/machine-info", timeout=5)
        if resp.status_code == 200:
            metrics["machine_info"] = resp.json()
    except Exception as e:
        metrics["machine_info"] = None
        print(f"Failed to get machine info: {{e}}")
    
    # Health states
    try:
        resp = requests.get(f"{{GPUD_BASE_URL}}/v1/states", timeout=5)
        if resp.status_code == 200:
            metrics["health_states"] = resp.json()
    except Exception as e:
        metrics["health_states"] = []
        print(f"Failed to get health states: {{e}}")
    
    # System metrics
    try:
        resp = requests.get(f"{{GPUD_BASE_URL}}/v1/metrics", timeout=5)
        if resp.status_code == 200:
            metrics["system_metrics"] = resp.json()
    except Exception as e:
        metrics["system_metrics"] = {{}}
        print(f"Failed to get system metrics: {{e}}")
    
    # Events
    try:
        resp = requests.get(f"{{GPUD_BASE_URL}}/v1/events", timeout=5)
        if resp.status_code == 200:
            metrics["events"] = resp.json()
    except Exception as e:
        metrics["events"] = []
        print(f"Failed to get events: {{e}}")
    
    return metrics

def send_metrics_batch(batch: List[Dict[str, Any]]) -> None:
    '''Send a batch of metrics to the endpoint.'''
    if not batch:
        return
    
    headers = {{"Content-Type": "application/json"}}
    if METRICS_AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {{METRICS_AUTH_TOKEN}}"
    
    try:
        if METRICS_ENDPOINT:
            # Send to remote endpoint
            response = requests.post(
                METRICS_ENDPOINT,
                json={{"metrics": batch, "batch_size": len(batch)}},
                headers=headers,
                timeout=30
            )
            if response.status_code >= 400:
                print(f"Failed to send metrics: {{response.status_code}} - {{response.text}}")
        else:
            # Log locally with daily rotation
            log_file = f"/var/log/flow/health-metrics-{{datetime.utcnow().strftime('%Y%m%d')}}.jsonl"
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, "a") as f:
                for metric in batch:
                    f.write(json.dumps(metric) + "\\n")
    except Exception as e:
        print(f"Error sending metrics batch: {{e}}")
        # Fall back to error log
        try:
            os.makedirs("/var/log/flow", exist_ok=True)
            with open("/var/log/flow/health-metrics-error.jsonl", "a") as f:
                for metric in batch:
                    f.write(json.dumps(metric) + "\\n")
        except:
            pass

def stream_metrics() -> None:
    '''Main loop to stream metrics.'''
    global metrics_buffer
    
    # Set up signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    print(f"Starting Flow metrics streamer...")
    print(f"GPUd URL: {{GPUD_BASE_URL}}")
    print(f"Metrics endpoint: {{METRICS_ENDPOINT or 'local storage'}}")
    print(f"Collection interval: {{METRICS_INTERVAL}}s")
    
    while True:
        try:
            metrics = collect_metrics()
            metrics_buffer.append(metrics)
            
            # Send batch if buffer is full
            if len(metrics_buffer) >= METRICS_BATCH_SIZE:
                send_metrics_batch(metrics_buffer)
                metrics_buffer = []
            
        except Exception as e:
            print(f"Error collecting metrics: {{e}}")
        
        time.sleep(METRICS_INTERVAL)

if __name__ == "__main__":
    stream_metrics()
METRICS_SCRIPT_EOF
            
            chmod +x /usr/local/bin/flow-metrics-streamer.py
            
            # Create systemd service for metrics streaming
            cat > /etc/systemd/system/flow-metrics-streamer.service << 'SERVICE_EOF'
[Unit]
Description=Flow Health Metrics Streamer
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/local/bin/flow-metrics-streamer.py
Restart=on-failure
RestartSec=30
StandardOutput=journal
StandardError=journal
SyslogIdentifier=flow-metrics

[Install]
WantedBy=multi-user.target
SERVICE_EOF
            
            # Enable and start the service
            systemctl daemon-reload
            systemctl enable flow-metrics-streamer.service
            systemctl start flow-metrics-streamer.service
            
            log "GPUd health monitoring setup complete"
            """
        ).strip()

    def validate(self, context: ScriptContext) -> list[str]:
        """Validate GPUd configuration."""
        errors = []

        # Check port is valid
        port = context.environment.get("FLOW_GPUD_PORT", "15132")
        try:
            port_num = int(port)
            if not 1 <= port_num <= 65535:
                errors.append(f"Invalid GPUd port: {port}")
        except ValueError:
            errors.append(f"GPUd port must be a number: {port}")

        # Validate metrics endpoint if provided
        endpoint = context.environment.get("FLOW_METRICS_ENDPOINT", "")
        if endpoint and not (endpoint.startswith("http://") or endpoint.startswith("https://")):
            errors.append("Metrics endpoint must be a valid HTTP(S) URL")

        return errors


class RuntimeMonitorSection(ScriptSection):
    """Monitor runtime limits and automatically pause/cancel tasks."""

    @property
    def name(self) -> str:
        return "runtime_monitor"

    @property
    def priority(self) -> int:
        return 90  # Before completion, after everything else

    def should_include(self, context: ScriptContext) -> bool:
        # Include if any runtime limits are specified
        return any([context.max_run_time_hours, context.min_run_time_hours, context.deadline_hours])

    def generate(self, context: ScriptContext) -> str:
        # Only handle max_run_time_hours for now (80/20 principle)
        if not context.max_run_time_hours:
            return ""

        # Calculate runtime in seconds
        max_runtime_seconds = int(context.max_run_time_hours * 3600)

        # Extract minimal Mithril credentials
        mithril_api_key = context.environment.get("_FLOW_MITHRIL_API_KEY", "")
        mithril_api_url = context.environment.get(
            "_FLOW_MITHRIL_API_URL", "https://api.foundryplatform.io"
        )
        mithril_project = context.environment.get("_FLOW_MITHRIL_PROJECT", "")

        if not mithril_api_key or not mithril_project:
            logger.warning("Runtime monitoring requested but Mithril credentials not provided")
            return ""

        # Calculate when the timer should fire (with 2 minute grace for shutdown)
        timer_seconds = max(max_runtime_seconds - 120, 60)  # At least 1 minute

        return textwrap.dedent(
            f"""
            # Runtime Limit Monitoring (Systemd-native, Preemption-aware)
            log "Setting up runtime limit monitoring (max: {context.max_run_time_hours} hours)"
            
            # Store task metadata for the cancel script
            mkdir -p /var/lib/flow
            cat > /var/lib/flow/task-runtime.conf <<EOF
TASK_NAME="{context.task_name or "unknown"}"
MAX_RUNTIME_HOURS="{context.max_run_time_hours}"
MITHRIL_API_KEY="{mithril_api_key}"
MITHRIL_API_URL="{mithril_api_url}"
MITHRIL_PROJECT="{mithril_project}"
EOF
            
            # Create cancel script that discovers its own task_id
            cat > /usr/local/bin/flow-runtime-cancel.sh << 'CANCEL_EOF'
#!/bin/bash
set -euo pipefail

# Load configuration
source /var/lib/flow/task-runtime.conf

echo "[$(date)] Flow runtime limit reached, initiating graceful shutdown"

# Stop workloads gracefully
echo "Stopping Docker containers..."
docker stop -t 30 main 2>/dev/null || true

# Wait for checkpoint/state save
sleep 10

# Get instance ID from metadata
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id || hostname)
echo "Instance ID: $INSTANCE_ID"

# Find our task/bid ID by searching for this instance
echo "Looking up task ID for instance $INSTANCE_ID..."
TASK_ID=$(curl -s -H "Authorization: Bearer $MITHRIL_API_KEY" \
    "$MITHRIL_API_URL/v2/spot/bids?project=$MITHRIL_PROJECT" | \
    python3 -c "
import sys, json
data = json.load(sys.stdin)
bids = data if isinstance(data, list) else data.get('data', [])
for bid in bids:
    for instance in bid.get('instances', []):
        if instance.get('instance_id') == '$INSTANCE_ID':
            print(bid['fid'])
            sys.exit(0)
print('unknown')
")

if [ "$TASK_ID" = "unknown" ]; then
    echo "WARNING: Could not find task ID for instance $INSTANCE_ID"
    # Still proceed with shutdown
else
    echo "Found task ID: $TASK_ID"
    # Cancel the Mithril bid to release resources
    echo "Cancelling Mithril bid $TASK_ID..."
    curl -X DELETE \
        -H "Authorization: Bearer $MITHRIL_API_KEY" \
        -H "Content-Type: application/json" \
        "$MITHRIL_API_URL/v2/spot/bids/$TASK_ID" \
        --max-time 30 || true
fi

# Mark runtime exceeded
echo "Runtime limit of $MAX_RUNTIME_HOURS hours exceeded at $(date)" > /var/run/flow-runtime-exceeded

# Schedule shutdown
echo "Scheduling system shutdown..."
shutdown -h +1 "Flow runtime limit exceeded"
CANCEL_EOF

            chmod +x /usr/local/bin/flow-runtime-cancel.sh
            
            # Create systemd timer using monotonic time (survives reboots)
            cat > /etc/systemd/system/flow-runtime-limit.timer << TIMER_EOF
[Unit]
Description=Flow Runtime Limit Timer
# This timer tracks elapsed time across reboots using monotonic clock

[Timer]
# Fire after the specified runtime (monotonic = counts actual runtime, not wall time)
OnBootSec={timer_seconds}s
AccuracySec=1min
# Persistent=true ensures timer state survives reboots
Persistent=true

[Install]
WantedBy=timers.target
TIMER_EOF
            
            # Create one-shot service that runs when timer expires
            cat > /etc/systemd/system/flow-runtime-limit.service << 'SERVICE_EOF'
[Unit]
Description=Flow Runtime Limit Enforcement
After=network-online.target docker.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/flow-runtime-cancel.sh
StandardOutput=journal
StandardError=journal
SyslogIdentifier=flow-runtime-limit
# Don't restart - this should only run once
Restart=no
SERVICE_EOF
            
            # Enable and start the timer
            systemctl daemon-reload
            systemctl enable flow-runtime-limit.timer
            systemctl start flow-runtime-limit.timer
            
            # Log timer status
            log "Runtime limit timer configured:"
            systemctl status flow-runtime-limit.timer --no-pager || true
            
            # Show when the timer will fire
            NEXT_ELAPSE=$(systemctl show flow-runtime-limit.timer --property=NextElapseUSecMonotonic --value)
            if [ -n "$NEXT_ELAPSE" ] && [ "$NEXT_ELAPSE" != "0" ]; then
                REMAINING_SEC=$((NEXT_ELAPSE / 1000000))
                if command -v bc >/dev/null 2>&1; then
                    REMAINING_HOURS=$(echo "scale=1; $REMAINING_SEC / 3600" | bc)
                else
                    REMAINING_HOURS=$((REMAINING_SEC / 3600))
                fi
                log "Runtime limit will trigger in approximately $REMAINING_HOURS hours"
            fi
            """
        ).strip()

    def validate(self, context: ScriptContext) -> list[str]:
        """Validate runtime monitoring configuration."""
        errors = []

        # Validate runtime limit values
        if context.max_run_time_hours and context.max_run_time_hours > 168:
            errors.append(
                f"max_run_time_hours ({context.max_run_time_hours}) exceeds 168 hour limit"
            )

        if context.min_run_time_hours and context.max_run_time_hours:
            if context.min_run_time_hours > context.max_run_time_hours:
                errors.append(
                    f"min_run_time_hours ({context.min_run_time_hours}) exceeds "
                    f"max_run_time_hours ({context.max_run_time_hours})"
                )

        return errors


class CompletionSection(ScriptSection):
    """Mark startup as complete and perform final tasks."""

    @property
    def name(self) -> str:
        return "completion"

    @property
    def priority(self) -> int:
        return 100  # Always last

    def should_include(self, context: ScriptContext) -> bool:
        return True

    def generate(self, context: ScriptContext) -> str:
        return textwrap.dedent(
            """
            # Startup complete
            echo "Mithril startup script completed successfully at $(date)"
            
            # Create completion marker
            touch /var/run/mithril-startup-complete
            
            # Log system info
            echo "System information:"
            uname -a
            df -h
            free -h
            
            echo "Startup log saved to /var/log/mithril/startup.log"
        """
        ).strip()
