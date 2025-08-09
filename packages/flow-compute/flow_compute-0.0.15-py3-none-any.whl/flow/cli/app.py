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

from flow import Flow  # noqa: F401
from flow.cli.commands import get_commands
from flow.cli.utils.terminal_adapter import TerminalAdapter


class OrderedGroup(click.Group):
    """Custom Click Group that maintains command order."""

    def __init__(self, name=None, commands=None, **attrs):
        super().__init__(name, commands, **attrs)
        self.commands = commands or OrderedDict()

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


@click.group(
    cls=OrderedGroup, context_settings={"max_content_width": TerminalAdapter.get_terminal_width()}
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

    return cli


cli = setup_cli()

# Enable automatic shell completion
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


def main():
    """Entry point for the Flow CLI application.

    This function provides a unified interface on top of single-responsibility
    command modules, orchestrating all CLI commands through a central entry point.

    Returns:
        int: Exit code from the CLI execution.
    """
    # Quick config check on startup (can be disabled via env var)
    if os.environ.get("FLOW_SKIP_CONFIG_CHECK") != "1":
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

    return cli()


if __name__ == "__main__":
    cli()
