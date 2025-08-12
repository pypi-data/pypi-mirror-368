"""Shared utilities for running Flow examples.

Modules:
- preflight: provider detection and environment checks
- costs: lightweight cost estimators
- console: simple structured printing
"""

from examples.console import error, info, success, warn
from examples.costs import estimate_price_for_instance
from examples.logs import log_json
from examples.preflight import detect_provider, ensure_ready

__all__ = [
    "detect_provider",
    "ensure_ready",
    "estimate_price_for_instance",
    "info",
    "warn",
    "error",
    "success",
    "log_json",
]
