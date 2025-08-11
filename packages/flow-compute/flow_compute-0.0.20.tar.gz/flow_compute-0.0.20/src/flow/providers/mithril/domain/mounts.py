"""Mount adaptation service.

Converts high-level mount specs (e.g., S3 URLs) into environment variables and
attachment specs expected by startup scripts and bid payload.
"""

from __future__ import annotations

import os

from flow.api.models import TaskConfig


class MountsService:
    def inject_env_for_s3(self, config: TaskConfig) -> TaskConfig:
        """Propagate AWS creds from env into config.env if missing, used by s3fs."""
        env_updates = {}
        if "AWS_ACCESS_KEY_ID" not in (config.env or {}) and os.environ.get("AWS_ACCESS_KEY_ID"):
            env_updates["AWS_ACCESS_KEY_ID"] = os.environ["AWS_ACCESS_KEY_ID"]
        if "AWS_SECRET_ACCESS_KEY" not in (config.env or {}) and os.environ.get(
            "AWS_SECRET_ACCESS_KEY"
        ):
            env_updates["AWS_SECRET_ACCESS_KEY"] = os.environ["AWS_SECRET_ACCESS_KEY"]
        if "AWS_SESSION_TOKEN" not in (config.env or {}) and os.environ.get("AWS_SESSION_TOKEN"):
            env_updates["AWS_SESSION_TOKEN"] = os.environ["AWS_SESSION_TOKEN"]
        if env_updates:
            return config.model_copy(update={"env": {**(config.env or {}), **env_updates}})
        return config
