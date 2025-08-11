"""Code upload orchestration service.

Provides a high-level API to decide and perform code upload (embedded vs SCP)
without keeping this logic in the provider facade.
"""

from __future__ import annotations

from flow.api.models import Task, TaskConfig
from flow.providers.mithril.code_transfer import CodeTransferConfig, CodeTransferManager


class CodeUploadPlan:
    def __init__(self, use_scp: bool) -> None:
        self.use_scp = use_scp


class CodeUploadService:
    def __init__(self, provider) -> None:
        self._provider = provider

    def plan(self, config: TaskConfig) -> CodeUploadPlan:
        strategy = (getattr(config, "upload_strategy", None) or "embedded").lower()
        use_scp = strategy in {"scp", "rsync", "ssh"}
        return CodeUploadPlan(use_scp=use_scp)

    def maybe_package_embedded(self, config: TaskConfig) -> TaskConfig:
        # Delegate to provider public helper for embedded packaging to avoid duplication
        return self._provider.package_local_code(config)

    def initiate_async_upload(self, task: Task, config: TaskConfig) -> None:
        manager = CodeTransferManager(provider=self._provider)
        # Fire-and-forget in background via provider public helper
        self._provider.start_background_code_upload(manager, task, CodeTransferConfig())
