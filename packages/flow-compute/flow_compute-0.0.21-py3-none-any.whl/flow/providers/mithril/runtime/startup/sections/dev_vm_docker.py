from __future__ import annotations

import textwrap

from flow.providers.mithril.runtime.startup.sections.base import ScriptContext, ScriptSection
from flow.providers.mithril.runtime.startup.utils import ensure_docker_available


class DevVMDockerSection(ScriptSection):
    @property
    def name(self) -> str:
        return "dev_vm_docker"

    @property
    def priority(self) -> int:
        return 38

    def should_include(self, context: ScriptContext) -> bool:
        return context.environment.get("FLOW_DEV_VM") == "true"

    def generate(self, context: ScriptContext) -> str:
        return textwrap.dedent(
            f"""
            echo "Ensuring Docker is available on host for dev VM"
            {ensure_docker_available()}
            mkdir -p /home/persistent
            chmod 755 /home/persistent
            echo "Docker and persistent storage ready for dev VM"
        """
        ).strip()


__all__ = ["DevVMDockerSection"]
