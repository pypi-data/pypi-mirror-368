"""Flow CLI commands.

Commands are modular with automatic discovery:
- Each command in its own module (e.g., run.py for 'flow run')
- Modules export a 'command' instance implementing BaseCommand
- Commands are auto-registered via COMMAND_MODULES list

Example:
    Adding a new command:
    1. Create mycommand.py implementing BaseCommand
    2. Add to imports: from . import mycommand
    3. Add to COMMAND_MODULES list
"""

from typing import List, Type

# Import all command modules
from . import (
    colab,
    cancel,
    dev,
    example,
    grab,
    health,
    init,
    innit,
    logs,
    mount,
    release,
    run,
    ssh,
    ssh_keys,
    status,
    update,
    upload_code,
    volumes,
)
from .base import BaseCommand

# List of command modules
COMMAND_MODULES = [
    run,
    grab,
    release,
    status,
    cancel,
    volumes,
    mount,
    example,
    init,
    innit,
    colab,
    ssh,
    ssh_keys,
    logs,
    upload_code,
    dev,
    health,
    update,
]


def get_commands() -> List[BaseCommand]:
    """Return all registered CLI commands."""
    commands = []
    for module in COMMAND_MODULES:
        if hasattr(module, "command"):
            commands.append(module.command)
    return commands


__all__ = ["BaseCommand", "get_commands"]
