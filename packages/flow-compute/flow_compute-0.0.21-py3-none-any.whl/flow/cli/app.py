"""Flow CLI application module.

Main CLI entry point and command registration for Flow.
"""

import os
import sys
import threading
from collections import OrderedDict
from collections.abc import Callable

import click

# Apply console patching early to ensure all Console instances respect settings
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

    def __init__(
        self,
        name: str | None = None,
        commands: dict[str, click.Command] | None = None,
        **attrs: object,
    ) -> None:
        super().__init__(name, commands, **attrs)
        self.commands = commands or OrderedDict()

    def list_commands(self, ctx: click.Context) -> list[str]:
        """Return command names preserving insertion order."""
        return list(self.commands.keys())


class OrderedDYMGroup(_DYMGroup):
    """Click Group with insertion-order listing and did-you-mean suggestions."""

    def list_commands(self, ctx: click.Context) -> list[str]:
        """Return command names preserving insertion order."""
        return list(self.commands.keys())


class LazyDYMGroup(OrderedDYMGroup):
    """Lazy-loading Click Group.

    Stores loader callables for commands and imports them only when invoked.
    Also allows fast help rendering without importing every command.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        # Optional short help map to avoid importing modules on --help
        self._help_summaries: dict[str, str] = {}
        # Optional example map for golden-path usage snippets
        self._examples: dict[str, str] = {}
        # Hidden commands not shown in grouped help
        self._hidden: set[str] = set()
        # Guard against double-loading from concurrent help/resolve
        self._cmd_lock = threading.Lock()

    def add_lazy_command(
        self,
        name: str,
        loader: Callable[[], click.Command | click.Group],
        help_summary: str | None = None,
        example: str | None = None,
        hidden: bool | None = None,
    ) -> None:
        # Store a callable that returns a click.Command when invoked
        self.commands[name] = loader
        if help_summary:
            self._help_summaries[name] = help_summary
        if example:
            self._examples[name] = example
        if hidden:
            self._hidden.add(name)

    def get_command(
        self, ctx: click.Context | None, cmd_name: str
    ) -> click.Command | click.Group | None:
        cmd_obj = self.commands.get(cmd_name)
        if cmd_obj is None:
            return None
        # If it's a callable loader, resolve and replace
        if callable(cmd_obj) and not isinstance(cmd_obj, click.Command):
            with self._cmd_lock:
                # Re-check under lock in case another thread resolved it
                current = self.commands.get(cmd_name)
                if isinstance(current, (click.Command, click.Group)):
                    return current
                try:
                    resolved = cmd_obj()
                    if isinstance(resolved, (click.Command, click.Group)):
                        self.commands[cmd_name] = resolved
                        return resolved
                except Exception as e:  # pragma: no cover - avoid breaking help
                    # Optionally log in debug mode; hide command from help
                    if os.environ.get("FLOW_DEBUG_ERRORS") == "1":
                        try:
                            sys.stderr.write(f"[flow-debug] failed to load command '{cmd_name}': {e}\n")
                        except Exception:
                            pass
                    return None
        return cmd_obj

    def format_commands(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        # Group commands into lifecycle sections without importing heavy modules
        groups: dict[str, list[str]] = {
            "Getting started": ["tutorial", "init", "completion", "demo"],
            "Run": ["run", "dev", "colab", "example", "grab"],
            "Observe": ["status", "logs", "health"],
            "Manage": ["cancel", "ssh", "volumes", "mount", "upload-code", "release"],
            "Advanced": ["update", "theme"],
        }

        listed = set()
        for title, names in groups.items():
            rows: list[tuple[str, str]] = []
            for name in names:
                if name not in self.commands or name in self._hidden:
                    continue
                listed.add(name)
                help_text = self._help_summaries.get(name, "")
                example = self._examples.get(name)
                if example:
                    help_text = f"{help_text}  e.g., {example}"
                rows.append((name, help_text))
            if rows:
                with formatter.section(title):
                    formatter.write_dl(rows)

        # Any remaining commands not categorized
        remaining = [n for n in self.list_commands(ctx) if n not in listed and n not in self._hidden]
        if remaining:
            rows = []
            for name in remaining:
                help_text = self._help_summaries.get(name, "")
                example = self._examples.get(name)
                if example:
                    help_text = f"{help_text}  e.g., {example}"
                rows.append((name, help_text))
            with formatter.section("Other"):
                formatter.write_dl(rows)


def print_version(ctx: click.Context, param: click.Option | None, value: bool) -> None:
    """Print version and exit.

    Args:
        ctx: Click context.
        param: Bound option (unused).
        value: Whether the option was provided.
    """
    if not value or ctx.resilient_parsing:
        return
    try:
        from flow._version import get_version

        v = get_version()
    except Exception as e:
        # Do not explode on import issues; offer optional debug
        if os.environ.get("FLOW_DEBUG_ERRORS") == "1":
            try:
                click.echo(f"warning: failed to load version: {e}", err=True)
            except Exception:
                pass
        v = "0.0.0+unknown"
    click.echo(f"flow, version {v}")
    ctx.exit()


# TUI decorator is optional; if trogon is unavailable, _tui is a no-op
@_tui()
@click.group(
    cls=LazyDYMGroup,
    context_settings={"max_content_width": TerminalAdapter.get_terminal_width()},
    invoke_without_command=True,
)
@click.option(
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="Show the version and exit.",
)
@click.option(
    "--theme",
    envvar="FLOW_THEME",
    help="Set color theme (dark, light, high_contrast, modern, modern_light)",
)
@click.option("--no-color", envvar="NO_COLOR", is_flag=True, help="Disable color output")
@click.option(
    "--hyperlinks/--no-hyperlinks",
    envvar="FLOW_HYPERLINKS",
    default=None,
    help="Enable/disable hyperlinks (default: auto)",
)
@click.option(
    "--demo/--no-demo",
    envvar="FLOW_DEMO_MODE",
    default=None,
    help="Demo mode: simulate runs with a mock provider (no real provisioning).",
)
@click.option(
    "--simple/--no-simple",
    envvar="FLOW_SIMPLE_OUTPUT",
    default=None,
    help="Simple output: reduce animations and panels; ideal for CI/logs.",
)
@click.pass_context
def cli(
    ctx: click.Context,
    theme: str | None,
    no_color: bool,
    hyperlinks: bool | None,
    demo: bool | None,
    simple: bool | None,
) -> None:
    """Flow CLI - Submit and manage GPU tasks.

    The Flow CLI helps you provision GPU instances/clusters, run workloads from YAML or command, and
    monitor/manage tasks end-to-end.

    \b
    Quickstart:
      1) flow tutorial             # Guided setup
      2) flow init                  # Configure API key (or set FLOW_API_KEY)
      3) flow example gpu-test      # Verify GPU access
      4) flow run training.yaml     # Run a job from YAML

    \b
    Common commands:

    \b
      Setup:
        flow tutorial              # First-time guided setup
        flow completion install     # Enable shell completion

    \b
      Development:
        flow dev                    # Persistent dev VM
        flow grab 64 h100           # 64×H100, 3.2T interconnect

    \b
      Run & examples:
        flow run <file.yaml>        # Submit task from YAML
        flow example gpu-test       # Minimal GPU validation

    \b
      Observe & manage:
        flow status                # List and filter tasks
        flow logs <task_id>         # Stream task logs
        flow ssh <task_id>          # SSH into a running task
        flow cancel <pattern>       # Cancel by id/name/pattern

    \b
      Storage:
        flow volumes ...            # Manage persistent volumes
        flow mount ...              # Attach volumes to tasks
        flow upload-code <task_id>  # Sync local code to a running task

    \b
      Utilities:
        flow pricing                # Show pricing defaults
        flow health                 # Run health checks
        flow update                # Update Flow SDK
        flow colab                  # Use Colab UI with Flow GPU runtime

    \b
    Tips:
      - Use --hyperlinks/--no-hyperlinks to control clickable links (auto by default)
      - Set a color theme with --theme [dark|light|high_contrast|modern|modern_light]
      - Configure credentials via 'flow init' or set FLOW_API_KEY
    """
    # Mark origin as CLI for this process (does not override explicit env)
    try:
        from flow.utils.origin import set_cli_origin_env

        set_cli_origin_env()
    except Exception:
        pass

    # Set up theme and hyperlink preferences
    import os

    from flow.cli.utils.hyperlink_support import hyperlink_support
    from flow.cli.utils.theme_manager import theme_manager

    # Apply theme settings
    if theme:
        theme_manager.load_theme(theme)
    if no_color:
        os.environ["NO_COLOR"] = "1"

    # Apply hyperlink settings
    if hyperlinks is not None:
        os.environ["FLOW_HYPERLINKS"] = "1" if hyperlinks else "0"
        # Clear cache to force re-detection
        hyperlink_support._support_cached = None

    # Apply simple output preference globally for this session
    if simple is not None:
        os.environ["FLOW_SIMPLE_OUTPUT"] = "1" if simple else "0"

    # Kick off non-blocking background prefetch early for UX wins
    try:
        # Local import to avoid import cycles during CLI bootstrap
        from flow.cli.utils.prefetch import start_prefetch_for_command

        start_prefetch_for_command()
    except Exception:
        # Best-effort; never block or fail CLI startup due to prefetch
        pass

    # Demo mode: load persisted env and resolve state; defer banner to individual commands
    try:
        from flow.cli.utils.mode import apply_demo_mode, load_persistent_demo_env

        # Load ~/.flow/demo.env if present so demo start persists across commands
        load_persistent_demo_env()
        apply_demo_mode(demo)
    except Exception:
        pass

    # Store settings in context for child commands
    ctx.ensure_object(dict)
    ctx.obj["theme"] = theme
    ctx.obj["no_color"] = no_color
    ctx.obj["hyperlinks"] = hyperlinks
    ctx.obj["simple"] = simple

    # If no subcommand was provided, show help instead of erroring.
    # This allows invocations like `flow --theme modern_light` to render themed help.
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit(0)


def setup_cli() -> click.Group:
    """Set up the CLI by registering all available commands.

    This function discovers and registers all command modules with the
    main CLI group. It supports both individual commands and command groups.

    Returns:
        The configured CLI group with all commands registered.

    Raises:
        TypeError: If a command module returns an invalid command type.
    """

    # Register lazy loaders to avoid importing all command modules at startup
    # Helper to create a loader for a module
    def _loader(mod_name: str):
        def _load():
            from importlib import import_module

            module = import_module(f"flow.cli.commands.{mod_name}")
            return module.command.get_command()

        return _load

    # Desired command order with short helps and module names
    # (cli_name, module_name, help_summary)
    lazy_commands: list[tuple[str, str, str, str]] = [
        ("tutorial", "tutorial", "Guided setup", "flow tutorial"),
        ("init", "init", "Configure credentials", "flow init"),
        ("demo", "demo", "Control demo mode", "flow demo on"),
        ("status", "status", "List and monitor tasks", "flow status --watch"),
        ("dev", "dev", "Development environment", "flow dev"),
        ("run", "run", "Submit task from YAML or command", "flow run training.yaml"),
        ("grab", "grab", "Quick resource selection", "flow grab 8 h100"),
        ("cancel", "cancel", "Cancel tasks", "flow cancel :1"),
        ("ssh", "ssh", "SSH into task", "flow ssh :1"),
        ("logs", "logs", "View task logs", "flow logs :1 -f"),
        ("volumes", "volumes", "Manage volumes", "flow volumes list"),
        ("mount", "mount", "Attach volumes", "flow mount :1 myvol:/data"),
        ("ports", "ports", "Manage ports and tunnels", "flow ports open :1 --port 8080"),
        ("upload-code", "upload_code", "Upload code to task", "flow upload-code :1"),
        ("health", "health", "Run health checks", "flow health overview"),
        ("colab", "colab", "Colab local runtime", "flow colab"),
        ("theme", "theme", "Manage CLI color themes", "flow theme set modern"),
        ("update", "update", "Update Flow SDK", "flow update"),
        ("daemon", "daemon", "Manage local background agent", "flow daemon status"),
        ("example", "example", "Run or show example configs", "flow example gpu-test"),
    ]

    for cli_name, module_name, help_summary, example in lazy_commands:
        try:
            # Support hyphen aliases by exposing module names that differ from command names
            # Use loader that imports on first invocation
            if isinstance(cli, LazyDYMGroup):
                # Hide daemon in help to reduce surface area; still available by name
                hidden = True if cli_name == "daemon" else None
                cli.add_lazy_command(cli_name, _loader(module_name), help_summary, example, hidden)
        except Exception:
            # Skip broken/optional commands silently
            pass

    return cli


def create_cli() -> click.Group:
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


def main() -> int:
    """Entry point for the Flow CLI application.

    This function provides a unified interface on top of single-responsibility
    command modules, orchestrating all CLI commands through a central entry point.

    Returns:
        Exit code from the CLI execution.
    """
    # Initialize centralized logging (idempotent, respects env)
    try:
        from flow.utils.logging import configure_logging

        # Only initialize when explicitly requested or when running CLI (default True here)
        # This avoids affecting host apps when Flow is imported as a library.
        if os.environ.get("FLOW_LOG_INIT", "1") == "1":
            configure_logging()
    except Exception:
        # Never fail CLI due to logging setup
        pass

    # Fast-path version without building CLI or importing commands
    argv = sys.argv[1:]
    if any(a in ("--version", "-V") for a in argv):
        # Use the same print_version callback
        print_version(click.Context(None), None, True)
        return 0

    # Quick config check on startup (now disabled by default; enable by setting FLOW_SKIP_CONFIG_CHECK=0)
    if os.environ.get("FLOW_SKIP_CONFIG_CHECK") == "0":
        # Only check for commands that need config (not init, help, etc)
        if len(sys.argv) > 1 and sys.argv[1] not in ["init", "--help", "-h", "--version"]:
            try:
                # Try to load config without auto_init to see if it's configured
                from flow._internal.config import Config

                Config.from_env(require_auth=True)
            except ValueError:
                # Config missing - provide helpful guidance
                from flow.cli.utils.theme_manager import theme_manager

                console = theme_manager.create_console()
                console.print("[yellow]⚠ Flow SDK is not configured[/yellow]\n")
                console.print("To get started, run: [accent]flow init[/accent]")
                console.print("Or set FLOW_API_KEY environment variable\n")
                console.print("For help: [dim]flow --help[/dim]")
                return 1

    cli_group = create_cli()

    # Opt-in usage telemetry wrapper
    try:
        from flow.utils.telemetry import Telemetry

        telemetry = Telemetry()
        if telemetry.enabled:
            # Command name is first argv or "help"
            cmd_name = sys.argv[1] if len(sys.argv) > 1 else "help"
            with telemetry.track_command(cmd_name):
                return cli_group()
        else:
            return cli_group()
    except Exception:
        # Never fail due to telemetry
        return cli_group()


if __name__ == "__main__":
    cli()

# Ensure subcommands are registered when this module is imported so that
# tests importing `cli` directly can invoke subcommands without calling
# create_cli()/setup_cli() explicitly.
try:
    # Safe to call multiple times; loaders are lightweight and idempotent
    setup_cli()
except Exception:
    # Never block import due to optional/missing commands in certain envs
    pass
