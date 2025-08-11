from __future__ import annotations

import textwrap

from flow.providers.mithril.runtime.startup.sections.base import ScriptContext, ScriptSection


class CodeUploadSection(ScriptSection):
    @property
    def name(self) -> str:
        return "code_upload"

    @property
    def priority(self) -> int:
        return 35

    def should_include(self, context: ScriptContext) -> bool:
        return context.upload_code and context.code_archive is not None

    def generate(self, context: ScriptContext) -> str:
        if not context.upload_code or not context.code_archive:
            return ""
        return textwrap.dedent(
            f"""
            echo "Extracting uploaded code to /workspace..."
            mkdir -p /workspace
            cd /workspace
            echo "{context.code_archive}" | base64 -d | tar -xzf -
            chmod -R 755 /workspace
        """
        ).strip()


__all__ = ["CodeUploadSection"]
