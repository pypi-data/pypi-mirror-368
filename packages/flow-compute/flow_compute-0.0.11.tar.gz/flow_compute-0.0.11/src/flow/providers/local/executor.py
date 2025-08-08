"""Task execution strategies for local provider."""

import logging
import os
import shlex
import subprocess
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Optional

from flow.api.models import TaskConfig
from flow.providers.local.config import LocalTestConfig

logger = logging.getLogger(__name__)

# Try to import Mithril startup builder for production startup scripts
try:
    from flow.providers.mithril.runtime.startup.sections import ScriptContext
    from flow.providers.mithril.runtime.startup.builder import MithrilStartupScriptBuilder

    HAS_MITHRIL_STARTUP_BUILDER = True
except ImportError:
    HAS_MITHRIL_STARTUP_BUILDER = False
    logger.debug("MithrilStartupScriptBuilder not available, using simple scripts")


@dataclass
class TaskExecution:
    """Represents a running task execution."""

    task_id: str
    container_id: Optional[str] = None
    process_id: Optional[str] = None
    process: Optional[subprocess.Popen] = None

    def wait(self) -> int:
        """Wait for execution to complete and return exit code."""
        if self.container_id:
            # Docker container
            import docker

            client = docker.from_env()
            container = client.containers.get(self.container_id)
            result = container.wait()
            return result["StatusCode"]
        elif self.process:
            # Local process
            return self.process.wait()
        else:
            raise RuntimeError("No execution to wait for")


class TaskExecutor(ABC):
    """Abstract base class for task execution strategies."""

    def __init__(self, config: LocalTestConfig):
        self.config = config
        self.executions: Dict[str, TaskExecution] = {}

    @abstractmethod
    def execute_task(
        self,
        task_id: str,
        config: TaskConfig,
        resources: dict,
        log_callback: Optional[Callable[[str], None]] = None,
    ) -> TaskExecution:
        """Execute a task with given configuration."""
        pass

    @abstractmethod
    def stop_task(self, task_id: str) -> None:
        """Stop a running task."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up all resources."""
        pass


class ContainerTaskExecutor(TaskExecutor):
    """Executes tasks in Docker containers."""

    def __init__(self, config: LocalTestConfig):
        super().__init__(config)

        # Initialize Docker client
        import docker

        self.client = docker.from_env()

        # Create test network
        self.network_name = "flow-test-network"
        try:
            self.network = self.client.networks.get(self.network_name)
        except docker.errors.NotFound:
            self.network = self.client.networks.create(self.network_name, driver="bridge")

    def execute_task(
        self,
        task_id: str,
        config: TaskConfig,
        resources: dict,
        log_callback: Optional[Callable[[str], None]] = None,
    ) -> TaskExecution:
        """Execute task in Docker container."""
        # Choose image: use task's image if specified, otherwise default
        if config.image:
            image = config.image
        elif resources.get("gpu_count", 0) > 0:
            image = self.config.gpu_docker_image
        else:
            image = self.config.docker_image

        # Build container configuration
        container_config = {
            "image": image,
            "name": f"flow-{task_id}",
            "detach": True,
            "remove": False,
            "network": self.network_name,
            "labels": {
                "flow.task_id": task_id,
                "flow.task_name": config.name,
            },
            "environment": self._build_environment(config),
            "volumes": self._build_volumes(config),
        }

        # Add resource limits
        if resources.get("memory_gb"):
            container_config["mem_limit"] = f"{resources['memory_gb']}g"

        if resources.get("cpu_cores"):
            # Docker uses CPU quota in microseconds per period
            container_config["cpu_quota"] = int(resources["cpu_cores"] * 100000)
            container_config["cpu_period"] = 100000

        # Add GPU support if needed
        if resources.get("gpu_count", 0) > 0:
            container_config["device_requests"] = [
                docker.types.DeviceRequest(count=resources["gpu_count"], capabilities=[["gpu"]])
            ]

        # Handle command execution based on type
        needs_script = False
        if config.command:
            if isinstance(config.command, list):
                # List form - pass directly to container
                container_config["command"] = config.command
            elif isinstance(config.command, str):
                # String form - check if it's a multi-line script
                if "\n" in config.command or config.command.startswith("#!"):
                    # Multi-line script - create startup script
                    needs_script = True
                else:
                    # Single-line command - let shell handle it
                    container_config["command"] = ["sh", "-c", config.command]

        if needs_script:
            # For scripts, create startup script
            script_path = self._create_startup_script(task_id, config)
            # Use sh for alpine-based images, bash for others
            shell = "sh" if image and "alpine" in image else "bash"
            # Use a unique path inside the container to avoid conflicts
            container_script_path = f"/tmp/flow-startup-{task_id}.sh"
            container_config["command"] = [shell, container_script_path]
            # Add script to volumes
            container_config["volumes"][str(script_path)] = {
                "bind": container_script_path,
                "mode": "ro",
            }

        # Start container
        try:
            container = self.client.containers.run(**container_config)

            # Start log streaming
            if log_callback:
                self._start_log_streaming(container, log_callback)

            execution = TaskExecution(task_id=task_id, container_id=container.id)
            self.executions[task_id] = execution

            return execution

        except Exception as e:
            logger.error(f"Failed to start container for task {task_id}: {e}")
            raise

    def _build_environment(self, config: TaskConfig) -> Dict[str, str]:
        """Build environment variables for container."""
        env = {
            "FLOW_TASK_ID": config.name,
            "FLOW_TASK_NAME": config.name,
            "FLOW_NODE_RANK": "0",
            "FLOW_NODE_COUNT": str(config.num_instances),
        }

        # Add multi-node environment variables for distributed training
        if config.num_instances > 1:
            env.update(
                {
                    # PyTorch distributed
                    "RANK": "0",  # Local is always rank 0
                    "LOCAL_RANK": "0",
                    "WORLD_SIZE": str(config.num_instances),
                    "MASTER_ADDR": "localhost",
                    "MASTER_PORT": "29500",
                    # TensorFlow/Horovod
                    "OMPI_COMM_WORLD_RANK": "0",
                    "OMPI_COMM_WORLD_SIZE": str(config.num_instances),
                    # NCCL settings for local testing
                    "NCCL_DEBUG": "INFO",
                    "NCCL_SOCKET_IFNAME": "lo",  # Use loopback for local
                }
            )

        # Add user environment
        if config.env:
            env.update(config.env)

        return env

    def _build_volumes(self, config: TaskConfig) -> Dict[str, dict]:
        """Build volume mounts for container."""
        volumes = {}

        # Add volume mounts
        if config.volumes:
            for vol in config.volumes:
                # Create local directory
                local_path = self.config.storage_dir / "volumes" / vol.name
                local_path.mkdir(parents=True, exist_ok=True)

                volumes[str(local_path)] = {"bind": vol.mount_path, "mode": "rw"}

        return volumes

    def _create_startup_script(self, task_id: str, config: TaskConfig) -> Path:
        """Create startup script for container."""
        script_dir = self.config.storage_dir / "scripts"
        script_dir.mkdir(parents=True, exist_ok=True)

        script_path = script_dir / f"{task_id}.sh"

        # Try to use production startup script builder if available
        if HAS_MITHRIL_STARTUP_BUILDER and self.config.use_mithril_startup_scripts:
            try:
                # Create script context for Mithril builder
                context = ScriptContext(
                    task_id=task_id,
                    task_config=config,
                    ssh_keys=[],  # No SSH in local mode
                    project_id="local",
                    lifecycle_manager=None,  # No lifecycle reporting in local
                    include_otel=False,  # No telemetry in local
                )

                # Build production startup script
                builder = MithrilStartupScriptBuilder()
                script = builder.build(context)

                if script.is_valid:
                    script_path.write_text(script.content)
                    script_path.chmod(0o755)
                    logger.debug(f"Using production startup script for task {task_id}")
                    return script_path
                else:
                    logger.warning(
                        f"Production script validation failed: {script.validation_errors}"
                    )
            except Exception as e:
                logger.debug(f"Failed to build production startup script: {e}")

        # Fall back to simple script
        # Use sh shebang for better compatibility
        script_lines = [
            "#!/bin/sh",
            "set -e",  # Exit on error
            "",
            "# Task startup script",
            f"echo 'Starting task {config.name}'",
            f"echo 'Task ID: {task_id}'",
            "echo 'Instance type: Local Docker'",
            "echo",
            "",
            "# User script",
        ]

        # Add the command/script content
        if config.command:
            if isinstance(config.command, str):
                # String command - add directly (it's a script)
                script_lines.append(config.command)
            elif isinstance(config.command, list):
                # List command - convert to shell command
                script_lines.append(" ".join(shlex.quote(arg) for arg in config.command))

        script_lines.extend(
            [
                "",
                "# Task complete",
                "echo",
                f"echo 'Task {config.name} completed'",
            ]
        )

        script_path.write_text("\n".join(script_lines))
        script_path.chmod(0o755)

        return script_path

    def _start_log_streaming(self, container, log_callback: Callable[[str], None]):
        """Start streaming container logs."""

        def stream_logs():
            try:
                # Stream logs from the beginning
                for line in container.logs(stream=True, follow=True, stdout=True, stderr=True):
                    if isinstance(line, bytes):
                        line = line.decode("utf-8", errors="replace")
                    line = line.rstrip()
                    if line:  # Skip empty lines
                        log_callback(line)
            except Exception as e:
                logger.error(f"Error streaming logs: {e}")

        thread = threading.Thread(target=stream_logs, daemon=True)
        thread.start()

    def stop_task(self, task_id: str) -> None:
        """Stop a running container."""
        if task_id not in self.executions:
            return

        execution = self.executions[task_id]
        if execution.container_id:
            try:
                container = self.client.containers.get(execution.container_id)
                container.stop(timeout=self.config.task_shutdown_timeout)
                container.remove()
            except Exception as e:
                logger.error(f"Error stopping container {execution.container_id}: {e}")

    def cleanup(self) -> None:
        """Clean up all containers and network."""
        # Stop all containers
        for task_id in list(self.executions.keys()):
            self.stop_task(task_id)

        # Remove network
        try:
            self.network.remove()
        except Exception as e:
            logger.warning(f"Error removing network: {e}")


class ProcessTaskExecutor(TaskExecutor):
    """Executes tasks as local processes."""

    def execute_task(
        self,
        task_id: str,
        config: TaskConfig,
        resources: dict,
        log_callback: Optional[Callable[[str], None]] = None,
    ) -> TaskExecution:
        """Execute task as local process."""
        # Create working directory
        work_dir = self.config.storage_dir / "tasks" / task_id
        work_dir.mkdir(parents=True, exist_ok=True)

        # Create startup script
        script_path = self._create_startup_script(task_id, config, work_dir)

        # Build environment
        env = os.environ.copy()
        env.update(
            {
                "FLOW_TASK_ID": task_id,
                "FLOW_TASK_NAME": config.name,
                "FLOW_NODE_RANK": "0",
                "FLOW_NODE_COUNT": str(config.num_instances),
            }
        )

        # Add multi-node environment variables for distributed training
        if config.num_instances > 1:
            env.update(
                {
                    # PyTorch distributed
                    "RANK": "0",  # Local is always rank 0
                    "LOCAL_RANK": "0",
                    "WORLD_SIZE": str(config.num_instances),
                    "MASTER_ADDR": "localhost",
                    "MASTER_PORT": "29500",
                    # TensorFlow/Horovod
                    "OMPI_COMM_WORLD_RANK": "0",
                    "OMPI_COMM_WORLD_SIZE": str(config.num_instances),
                    # NCCL settings for local testing
                    "NCCL_DEBUG": "INFO",
                    "NCCL_SOCKET_IFNAME": "lo",  # Use loopback for local
                }
            )

        if config.env:
            env.update(config.env)

        # Start process
        process = subprocess.Popen(
            ["bash", str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=str(work_dir),
            env=env,
            text=True,
            bufsize=1,  # Line buffered
        )

        # Start log streaming
        if log_callback:
            self._start_log_streaming(process, log_callback)

        execution = TaskExecution(task_id=task_id, process_id=str(process.pid), process=process)
        self.executions[task_id] = execution

        return execution

    def _create_startup_script(self, task_id: str, config: TaskConfig, work_dir: Path) -> Path:
        """Create startup script for process."""
        script_path = work_dir / "startup.sh"

        # Try to use production startup script builder if available
        if HAS_MITHRIL_STARTUP_BUILDER and self.config.use_mithril_startup_scripts:
            try:
                # Create script context for Mithril builder
                context = ScriptContext(
                    task_id=task_id,
                    task_config=config,
                    ssh_keys=[],  # No SSH in local mode
                    project_id="local",
                    lifecycle_manager=None,  # No lifecycle reporting in local
                    include_otel=False,  # No telemetry in local
                )

                # Build production startup script
                builder = MithrilStartupScriptBuilder()
                script = builder.build(context)

                if script.is_valid:
                    script_path.write_text(script.content)
                    script_path.chmod(0o755)
                    logger.debug(f"Using production startup script for task {task_id}")
                    return script_path
                else:
                    logger.warning(
                        f"Production script validation failed: {script.validation_errors}"
                    )
            except Exception as e:
                logger.debug(f"Failed to build production startup script: {e}")

        # Fall back to simple script
        script_lines = [
            "#!/bin/bash",
            "set -e",  # Exit on error
            "",
            "# Task startup script",
            f"echo 'Starting task {config.name}'",
            f"echo 'Task ID: {task_id}'",
            "echo 'Instance type: Local Process'",
            "echo",
            "",
            "# User script",
        ]

        # Add the command/script content
        if config.command:
            if isinstance(config.command, str):
                # String command - add directly (it's a script)
                script_lines.append(config.command)
            elif isinstance(config.command, list):
                # List command - convert to shell command
                script_lines.append(" ".join(shlex.quote(arg) for arg in config.command))

        script_lines.extend(
            [
                "",
                "# Task complete",
                "echo",
                f"echo 'Task {config.name} completed'",
            ]
        )

        script_path.write_text("\n".join(script_lines))
        script_path.chmod(0o755)

        return script_path

    def _start_log_streaming(self, process: subprocess.Popen, log_callback: Callable[[str], None]):
        """Start streaming process output."""

        def stream_logs():
            try:
                for line in process.stdout:
                    if line:
                        log_callback(line.rstrip())
            except Exception as e:
                logger.error(f"Error streaming logs: {e}")

        thread = threading.Thread(target=stream_logs, daemon=True)
        thread.start()

    def stop_task(self, task_id: str) -> None:
        """Stop a running process."""
        if task_id not in self.executions:
            return

        execution = self.executions[task_id]
        if execution.process:
            try:
                execution.process.terminate()
                # Give it time to terminate gracefully
                time.sleep(1)
                if execution.process.poll() is None:
                    execution.process.kill()
            except Exception as e:
                logger.error(f"Error stopping process {execution.process_id}: {e}")

    def cleanup(self) -> None:
        """Clean up all processes."""
        for task_id in list(self.executions.keys()):
            self.stop_task(task_id)
