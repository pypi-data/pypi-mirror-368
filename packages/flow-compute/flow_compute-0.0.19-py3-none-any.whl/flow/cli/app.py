"""Flow CLI application module.

This module provides the main CLI entry point and command registration
for the Flow GPU task orchestration system.
"""

import os
import sys
from collections import OrderedDict

# Apply console patching early to ensure all Console instances respect settings
from flow.cli.utils import console_patch

import click

from flow.cli.commands import get_commands
from flow.cli.utils.terminal_adapter import TerminalAdapter

# Optional: "did you mean" suggestions (no-op if not installed)
try:
    from click_didyoumean import DYMGroup as _DYMGroup
except Exception:  # pragma: no cover - optional dependency
    _DYMGroup = click.Group  # type: ignore

# Optional: Trogon TUI decorator (no-op if not installed)
try:
    from trogon import tui as _tui
except Exception:  # pragma: no cover - optional dependency
    def _tui(*_args, **_kwargs):  # type: ignore
        def _decorator(f):
            return f
        return _decorator


class OrderedGroup(click.Group):
    """Custom Click Group that maintains command order."""

    def __init__(self, name=None, commands=None, **attrs):
        super().__init__(name, commands, **attrs)
        self.commands = commands or OrderedDict()

    def list_commands(self, ctx):
        return list(self.commands.keys())


class OrderedDYMGroup(_DYMGroup):
    """Click Group with insertion-order listing and did-you-mean suggestions."""

    def list_commands(self, ctx):
        return list(self.commands.keys())


def print_version(ctx, param, value):
    """Print version and exit."""
    if not value or ctx.resilient_parsing:
        return
    try:
        from importlib.metadata import version

        v = version("flow-compute")
    except Exception:
        v = "0.0.7"
    click.echo(f"flow, version {v}")
    ctx.exit()


@_tui()
@click.group(
    cls=OrderedDYMGroup, context_settings={"max_content_width": TerminalAdapter.get_terminal_width()}
)
@click.option(
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="Show the version and exit.",
)
@click.option("--theme", envvar="FLOW_THEME", help="Set color theme (dark, light, high_contrast, modern)")
@click.option("--no-color", envvar="NO_COLOR", is_flag=True, help="Disable color output")
@click.option(
    "--hyperlinks/--no-hyperlinks",
    envvar="FLOW_HYPERLINKS",
    default=None,
    help="Enable/disable hyperlinks (default: auto)",
)
@click.pass_context
def cli(ctx, theme, no_color, hyperlinks):
    """Flow CLI - Submit and manage GPU tasks.

    This is the main command group for the Flow CLI. It provides commands
    for submitting, monitoring, and managing GPU compute tasks.

    \b
    Examples:

    \b
    Initial Setup:
      flow tutorial             # Guided setup & verification (alias: setup)
      flow init                  # Configure Flow SDK

    \b
    Development:
      flow dev                   # Launch cloud dev environment
      flow grab 64 h100          # 64×H100, 3.2T interconnect

    \b
    Training:
      flow run training.yaml     # Execute training pipeline from YAML
      flow example gpu-test      # Verify GPU access

    \b
    Monitoring:
      flow status                # Check running tasks
      flow ssh <task_id>         # Connect to running task
    """
    # Set up theme and hyperlink preferences
    from flow.cli.utils.theme_manager import theme_manager
    from flow.cli.utils.hyperlink_support import hyperlink_support
    import os

    # Apply theme settings
    if theme:
        # Back-compat aliases
        if theme in ("cursor", "cursor_dark"):
            theme = "modern"
        theme_manager.load_theme(theme)
    if no_color:
        os.environ["NO_COLOR"] = "1"

    # Apply hyperlink settings
    if hyperlinks is not None:
        os.environ["FLOW_HYPERLINKS"] = "1" if hyperlinks else "0"
        # Clear cache to force re-detection
        hyperlink_support._support_cached = None

    # Kick off non-blocking background prefetch early for UX wins
    try:
        # Local import to avoid import cycles during CLI bootstrap
        from .utils.prefetch import start_prefetch_for_command

        start_prefetch_for_command()
    except Exception:
        # Best-effort; never block or fail CLI startup due to prefetch
        pass

    # Store settings in context for child commands
    ctx.ensure_object(dict)
    ctx.obj["theme"] = theme
    ctx.obj["no_color"] = no_color
    ctx.obj["hyperlinks"] = hyperlinks


def setup_cli():
    """Set up the CLI by registering all available commands.

    This function discovers and registers all command modules with the
    main CLI group. It supports both individual commands and command groups.

    Returns:
        click.Group: The configured CLI group with all commands registered.

    Raises:
        TypeError: If a command module returns an invalid command type.
    """
    commands = get_commands()

    # Build a map of command name to command object
    command_map = {}
    for command in commands:
        cmd = command.get_command()
        if isinstance(cmd, (click.Command, click.Group)):
            command_map[command.name] = cmd
        else:
            raise TypeError(f"Command {command.name} must return a click.Command or click.Group")

    # Define the desired command order
    priority_order = [
        "tutorial",  # Guided setup
        "init",  # Initial setup
        "status",  # Check status
        "dev",  # Development environment
        "run",  # Run tasks
        "grab",  # Quick GPU grab
        "cancel",  # Cancel tasks
        "ssh",  # SSH to instances
        "logs",  # View logs
        "volumes",  # Manage volumes
        "mount",  # Mount volumes
        "upload-code",  # Upload code
        "health",  # Health checks
        "colab",  # Colab local runtime (placed last)
    ]

    # Add commands in priority order
    for cmd_name in priority_order:
        if cmd_name in command_map:
            cli.add_command(command_map[cmd_name])

    # Add any remaining commands not in priority order (alphabetically)
    remaining_commands = sorted(set(command_map.keys()) - set(priority_order))
    for cmd_name in remaining_commands:
        cli.add_command(command_map[cmd_name])

    # Back-compat: add 'upgrade' as an alias for 'update'
    # This allows users to run `flow upgrade` which maps to the update command
    if "update" in command_map:
        cli.add_command(command_map["update"], name="upgrade")

    # Alias: `flow setup` maps to the tutorial command for discoverability
    if "tutorial" in command_map:
        cli.add_command(command_map["tutorial"], name="setup")

    # Common alias: `flow ps` maps to `flow status`
    if "status" in command_map:
        cli.add_command(command_map["status"], name="ps")

    return cli


def create_cli():
    """Create the CLI without triggering heavy imports at module import time.

    This defers command registration until runtime, so invocations like
    `flow --version` do not import every command module.
    """
    cli_group = setup_cli()

    # Enable automatic shell completion (optional dependency)
    try:
        from auto_click_auto import enable_click_shell_completion
        from auto_click_auto.constants import ShellType

        enable_click_shell_completion(
            program_name="flow",
            shells={ShellType.BASH, ShellType.ZSH, ShellType.FISH},
        )
    except ImportError:
        # auto-click-auto not installed, fall back to manual completion
        pass

    return cli_group


def main():
    """Entry point for the Flow CLI application.

    This function provides a unified interface on top of single-responsibility
    command modules, orchestrating all CLI commands through a central entry point.

    Returns:
        int: Exit code from the CLI execution.
    """
    # Quick config check on startup (now disabled by default; enable by setting FLOW_SKIP_CONFIG_CHECK=0)
    if os.environ.get("FLOW_SKIP_CONFIG_CHECK") == "0":
        # Only check for commands that need config (not init, help, etc)
        if len(sys.argv) > 1 and sys.argv[1] not in ["init", "--help", "-h", "--version"]:
            try:
                # Try to load config without auto_init to see if it's configured
                from flow.api.config import Config

                Config.from_env(require_auth=True)
            except ValueError:
                # Config missing - provide helpful guidance
                from flow.cli.utils.theme_manager import theme_manager

                console = theme_manager.create_console()
                console.print("[yellow]⚠ Flow SDK is not configured[/yellow]\n")
                console.print("To get started, run: [cyan]flow init[/cyan]")
                console.print("Or set FLOW_API_KEY environment variable\n")
                console.print("For help: [dim]flow --help[/dim]")
                return 1

    cli_group = create_cli()
    return cli_group()


if __name__ == "__main__":
    cli()
