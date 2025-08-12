"""Theme management commands for Flow CLI.

Provides commands to set, get, and list CLI color themes, persisting the
selection to ~/.flow/config.yaml for future sessions.
"""

from pathlib import Path

import click
import yaml

from flow.cli.commands.base import BaseCommand
from flow.cli.utils.theme_manager import theme_manager


def _read_config(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_config(path: Path, config: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w") as f:
        yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)
    try:
        tmp.replace(path)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


class ThemeCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "theme"

    @property
    def help(self) -> str:
        return "Manage CLI color themes (set, get, list)"

    def get_command(self) -> click.Command:
        @click.group(name=self.name, help=self.help)
        def theme_group() -> None:
            pass

        @theme_group.command("list", help="List available themes")
        def list_cmd() -> None:
            console = theme_manager.create_console()
            names = theme_manager.list_themes()
            console.print("Available themes:\n  - " + "\n  - ".join(names))

        @theme_group.command("get", help="Show the currently configured theme")
        def get_cmd() -> None:
            console = theme_manager.create_console()
            current = theme_manager.current_theme_name or theme_manager.detect_terminal_theme()
            console.print(f"Current theme: [accent]{current}[/accent]")

        @theme_group.command("set", help="Persist a default theme (overrides auto-detect)")
        @click.argument("name", required=True)
        def set_cmd(name: str) -> None:
            console = theme_manager.create_console()
            # Validate theme name
            available = set(theme_manager.list_themes())
            if name not in available:
                raise click.BadParameter(
                    f"Unknown theme '{name}'. Use 'flow theme list' to see options."
                )

            config_path = Path.home() / ".flow" / "config.yaml"
            cfg = _read_config(config_path)
            cfg["theme"] = name
            _write_config(config_path, cfg)

            # Apply immediately in this process too
            theme_manager.load_theme(name)
            console.print(f"Saved default theme: [accent]{name}[/accent]")

        @theme_group.command("clear", help="Remove persisted theme and return to auto-detect")
        def clear_cmd() -> None:
            console = theme_manager.create_console()
            config_path = Path.home() / ".flow" / "config.yaml"
            cfg = _read_config(config_path)
            if "theme" in cfg:
                cfg.pop("theme", None)
                _write_config(config_path, cfg)
                console.print("Cleared persisted theme. Using auto-detect.")
            else:
                console.print("No persisted theme set. Using auto-detect.")

        # Alias: unset -> clear
        @theme_group.command("unset", help="Alias for clear")
        def unset_cmd() -> None:
            clear_cmd()

        return theme_group


# Export command instance
command = ThemeCommand()
