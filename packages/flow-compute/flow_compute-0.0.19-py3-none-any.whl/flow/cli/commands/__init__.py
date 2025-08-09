"""Flow CLI commands registry with lazy import.

Each command lives in its own module and exposes a module-level `command`
object implementing `BaseCommand`. We avoid importing all command modules at
package import time to keep CLI startup fast and resilient to optional
dependencies.

This module provides `get_commands()` which imports available command modules
defensively and returns their `command` objects. Missing or broken optional
commands are skipped gracefully.
"""

from importlib import import_module
from typing import List

from .base import BaseCommand

# Known command module names. Keep alphabetical; do not include private helpers.
# Modules that are absent will be skipped without failing CLI startup.
_COMMAND_MODULE_NAMES = [
    "alloc",
    "cancel",
    "colab",
    "completion",
    "dev",
    "example",
    "feedback",
    "grab",
    "health",
    "init",
    "innit",
    "logs",
    "mount",
    "pricing",
    "release",
    "run",
    "ssh",
    "ssh_keys",
    "status",
    "tutorial",
    "update",
    "upload_code",
    "volumes",
]


def get_commands() -> List[BaseCommand]:
    """Discover and return all available CLI command objects.

    Imports each known module defensively and collects its `command` attribute
    if present. Any ImportError or missing `command` is ignored to ensure the
    CLI remains usable even when optional features are unavailable.
    """
    discovered: List[BaseCommand] = []
    base_package = __name__

    for module_name in _COMMAND_MODULE_NAMES:
        try:
            module = import_module(f"{base_package}.{module_name}")
        except Exception:
            # Optional or unavailable module; skip
            continue

        cmd = getattr(module, "command", None)
        if cmd is not None:
            discovered.append(cmd)

    return discovered


__all__ = ["BaseCommand", "get_commands"]
