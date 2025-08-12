from __future__ import annotations

import os
from typing import Literal

Provider = Literal["local", "cloud"]


def detect_provider() -> Provider:
    """Detect the current provider mode for examples.

    Returns "local" when FLOW_PROVIDER=local, else "cloud".
    """
    return "local" if os.environ.get("FLOW_PROVIDER") == "local" else "cloud"


def ensure_ready(provider: Provider) -> list[str]:
    """Perform quick preflight checks and return a list of warnings.

    - local: suggest setting FLOW_PROVIDER=local
    - cloud: check for credentials in environment (~/.flow config is handled by SDK)
    """
    warnings: list[str] = []

    if provider == "local":
        if os.environ.get("FLOW_PROVIDER") != "local":
            warnings.append("FLOW_PROVIDER is not set to 'local'. Set: export FLOW_PROVIDER=local")
        return warnings

    # cloud mode
    # We do not validate ~/.flow/config.yaml here; the SDK will surface better errors.
    # Provide quick hints based on env.
    if not os.environ.get("MITHRIL_API_KEY"):
        warnings.append("MITHRIL_API_KEY not found in env (run 'flow init' if not configured).")
    if not os.environ.get("MITHRIL_PROJECT"):
        warnings.append("MITHRIL_PROJECT not found in env (run 'flow init' or set project).")

    return warnings
