from __future__ import annotations

import textwrap

from flow.providers.mithril.runtime.startup.sections.base import ScriptContext, ScriptSection


class CompletionSection(ScriptSection):
    @property
    def name(self) -> str:
        return "completion"

    @property
    def priority(self) -> int:
        return 100

    def should_include(self, context: ScriptContext) -> bool:
        return True

    def generate(self, context: ScriptContext) -> str:
        return textwrap.dedent(
            """
            echo "Mithril startup script completed successfully at $(date)"
            mkdir -p /var/run || true
            touch /var/run/mithril-startup-complete
            touch /var/lib/flow/first-boot-completed || true
            uname -a
            df -h || true
            (free -h || true)
        """
        ).strip()


__all__ = ["CompletionSection"]
