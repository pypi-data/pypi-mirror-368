from __future__ import annotations

import shlex

from flow.core.docker import DockerConfig
from flow.core.paths import WORKSPACE_DIR, EPHEMERAL_NVME_DIR, default_volume_mount_path
from flow.providers.mithril.runtime.startup.sections.base import ScriptContext, ScriptSection
from flow.providers.mithril.runtime.startup.utils import (
    ensure_docker_available,
    ensure_command_available,
)


class DockerSection(ScriptSection):
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
        pre_setup = []
        if context.has_gpu:
            pre_setup.append(
                ensure_command_available(
                    "nvidia-container-toolkit",
                    install_method=(
                        "if command -v apt-get >/dev/null 2>&1; then apt-get update -qq && apt-get install -y -qq nvidia-container-toolkit || true; "
                        "elif command -v yum >/dev/null 2>&1; then yum -y install nvidia-container-toolkit || true; "
                        "elif command -v dnf >/dev/null 2>&1; then dnf -y install nvidia-container-toolkit || true; "
                        "else install_pkgs nvidia-container-toolkit || true; fi"
                    ),
                )
            )
        return "\n".join(
            [
                "# Docker setup",
                f'echo "Setting up Docker and running {context.docker_image}"',
                ensure_docker_available(),
                *pre_setup,
                "docker rm -f main 2>/dev/null || true",
                docker_run_cmd,
                "sleep 5",
                "docker ps",
                "docker logs main --tail 50",
            ]
        )

    def _build_docker_run_command(self, context: ScriptContext) -> str:
        cmd_parts = [
            "docker run",
            "-d",
            "--restart=unless-stopped",
            "--name=main",
            "--log-driver=json-file",
            "--log-opt max-size=100m",
            "--log-opt max-file=3",
            "--label=flow.task_role=main",
            '"--label=flow.task_name=${FLOW_TASK_NAME:-unknown}"',
            '"--label=flow.task_id=${FLOW_TASK_ID:-unknown}"',
        ]
        if context.environment.get("FLOW_DEV_VM") == "true":
            cmd_parts.extend(
                [
                    "--privileged",
                    "-v",
                    "/var/run/docker.sock:/var/run/docker.sock",
                    "-v",
                    "/var/lib/docker:/var/lib/docker",
                    "-v",
                    "/home/persistent:/root",
                    "-w",
                    "/root",
                ]
            )
        if context.has_gpu:
            cmd_parts.append("--gpus all")
        # Validate and add port mappings
        for port in context.ports:
            try:
                port_int = int(port)
            except Exception:
                continue
            if 1 <= port_int <= 65535:
                cmd_parts.append(f"-p {port_int}:{port_int}")
        for i, volume in enumerate(context.volumes):
            mount_path = volume.get("mount_path") or default_volume_mount_path(
                name=volume.get("name"), index=i
            )
            if not DockerConfig.should_mount_in_container(mount_path):
                continue
            # Quote mount paths to prevent path injection and handle spaces
            cmd_parts.append(
                f"-v {shlex.quote(str(mount_path))}:{shlex.quote(str(mount_path))}"
            )
        if context.upload_code and context.environment.get("FLOW_DEV_VM") != "true":
            # Quote workdir safely
            cmd_parts.append(f"-w {shlex.quote(WORKSPACE_DIR)}")
            cmd_parts.append(f"-v {shlex.quote(WORKSPACE_DIR)}:{shlex.quote(WORKSPACE_DIR)}")
        # Bind instance ephemeral NVMe storage if present
        cmd_parts.append(
            f'$([ -d {shlex.quote(EPHEMERAL_NVME_DIR)} ] && echo "-v {shlex.quote(EPHEMERAL_NVME_DIR)}:{shlex.quote(EPHEMERAL_NVME_DIR)}")'
        )
        for key, value in context.environment.items():
            import re as _re
            # Validate environment variable names to avoid malformed/injection-prone keys
            if not _re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", str(key)):
                # Skip invalid env var names silently to avoid breaking docker run
                # Consider logging in the future via a template-aware echo
                continue
            safe_val = shlex.quote(str(value))
            cmd_parts.append(f"-e {key}={safe_val}")
        # Provide sensible default cache/temp locations on fast ephemeral storage
        default_cache_env = {
            "XDG_CACHE_HOME": f"{EPHEMERAL_NVME_DIR}/.cache",
            "PIP_CACHE_DIR": f"{EPHEMERAL_NVME_DIR}/.cache/pip",
            "HF_HOME": f"{EPHEMERAL_NVME_DIR}/.cache/huggingface",
            "TRANSFORMERS_CACHE": f"{EPHEMERAL_NVME_DIR}/.cache/huggingface/transformers",
            "TORCH_HOME": f"{EPHEMERAL_NVME_DIR}/.cache/torch",
            "CUDA_CACHE_PATH": f"{EPHEMERAL_NVME_DIR}/.nv/ComputeCache",
            "TMPDIR": f"{EPHEMERAL_NVME_DIR}/tmp",
        }
        for env_key, env_value in default_cache_env.items():
            if env_key not in context.environment:
                cmd_parts.append(f'-e {env_key}="{env_value}"')
        for var in [
            "FLOW_NODE_RANK",
            "FLOW_NUM_NODES",
            "FLOW_MAIN_IP",
            "MASTER_ADDR",
            "MASTER_PORT",
        ]:
            cmd_parts.append(f'-e {var}="${{{var}}}"')
        # Quote image name to avoid accidental shell metacharacter interpretation
        cmd_parts.append(shlex.quote(str(context.docker_image)))
        if context.docker_command:
            if len(context.docker_command) == 1:
                cmd_str = context.docker_command[0]
                cmd_parts.extend(["bash", "-lc", shlex.quote(cmd_str)])
            else:
                for arg in context.docker_command:
                    cmd_parts.append(shlex.quote(arg))
        return " \\\n+    ".join(cmd_parts)

    def validate(self, context: ScriptContext) -> list[str]:
        errors: list[str] = []
        if (
            context.docker_image
            and "/" not in context.docker_image
            and ":" not in context.docker_image
        ):
            official = {
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
            if image_name not in official:
                errors.append(
                    f"Docker image should include registry/namespace: {context.docker_image}"
                )
        return errors


__all__ = ["DockerSection"]
