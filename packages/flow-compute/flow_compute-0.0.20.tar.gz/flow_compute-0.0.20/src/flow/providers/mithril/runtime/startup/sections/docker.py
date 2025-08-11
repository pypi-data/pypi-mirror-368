from __future__ import annotations

from flow.core.docker import DockerConfig
from flow.providers.mithril.runtime.startup.sections.base import ScriptContext, ScriptSection
from flow.providers.mithril.runtime.startup.utils import (
    ensure_docker_available,
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
        return "\n".join(
            [
                "# Docker setup",
                f'echo "Setting up Docker and running {context.docker_image}"',
                ensure_docker_available(),
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
        for port in context.ports:
            cmd_parts.append(f"-p {port}:{port}")
        for i, volume in enumerate(context.volumes):
            mount_path = volume.get("mount_path") or (
                f"/volumes/{volume.get('name')}" if volume.get("name") else f"/volumes/volume-{i}"
            )
            if not DockerConfig.should_mount_in_container(mount_path):
                continue
            cmd_parts.append(f"-v {mount_path}:{mount_path}")
        if context.upload_code and context.environment.get("FLOW_DEV_VM") != "true":
            cmd_parts.append("-w /workspace")
            cmd_parts.append("-v /workspace:/workspace")
        # Bind instance ephemeral NVMe storage if present
        cmd_parts.append('$([ -d /mnt/local ] && echo "-v /mnt/local:/mnt/local")')
        for key, value in context.environment.items():
            cmd_parts.append(f'-e {key}="{value}"')
        # Provide sensible default cache/temp locations on fast ephemeral storage
        default_cache_env = {
            "XDG_CACHE_HOME": "/mnt/local/.cache",
            "PIP_CACHE_DIR": "/mnt/local/.cache/pip",
            "HF_HOME": "/mnt/local/.cache/huggingface",
            "TRANSFORMERS_CACHE": "/mnt/local/.cache/huggingface/transformers",
            "TORCH_HOME": "/mnt/local/.cache/torch",
            "CUDA_CACHE_PATH": "/mnt/local/.nv/ComputeCache",
            "TMPDIR": "/mnt/local/tmp",
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
            cmd_parts.append(f"-e {var}")
        cmd_parts.append(context.docker_image)
        if context.docker_command:
            import shlex

            needs_shell = False
            if len(context.docker_command) == 1:
                cmd_str = context.docker_command[0]
                if any(op in cmd_str for op in ["&&", "||", ";", "|", ">", "<", "\n"]):
                    needs_shell = True
            if needs_shell:
                cmd_parts.extend(["bash", "-c", shlex.quote(context.docker_command[0])])
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
