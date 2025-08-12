"""Demo command - Control Flow demo mode and mock behavior.

Usage:
  flow demo status            # Show current demo mode
  flow demo start             # Enable demo for this shell (export)
  flow demo stop              # Disable demo for this shell
  flow demo profile realistic # Apply preset latencies
  flow demo profile quick     # Minimal delays
  flow demo set KEY=VALUE     # Set a mock latency/flag for this shell

Semantics:
  - start/stop: set FLOW_DEMO_MODE and FLOW_PROVIDER for the current process
  - profile: apply a known set of latency envs for realistic demos
  - set: convenient helper to set per-operation latency vars
"""

from __future__ import annotations

import os
from pathlib import Path

import click

from flow.cli.commands.base import BaseCommand, console
from flow.cli.utils.mode import (
    apply_demo_mode,
    is_demo_active,
    load_persistent_demo_env,
    show_demo_banner_once,
)
from flow.cli.utils.theme_manager import theme_manager


class DemoCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "demo"

    @property
    def help(self) -> str:
        return "Control demo mode and mock provider behavior"

    def get_command(self) -> click.Group:
        @click.group(name=self.name, help=self.help)
        def demo():
            pass

        @demo.command("status", help="Show current demo mode")
        def status_cmd():
            # Load persisted env as context (without overriding current)
            load_persistent_demo_env()
            active = is_demo_active()
            accent = theme_manager.get_color("accent")
            console.print(
                f"Demo mode: [{'green' if active else 'red'}]{'ON' if active else 'OFF'}[/]"
            )
            provider = os.environ.get("FLOW_PROVIDER")
            console.print(f"Provider: [accent]{provider or '—'}[/accent]")

        @demo.command("start", help="Enable demo for this shell (no persistence)")
        def start_cmd():
            # Enable demo for current process
            apply_demo_mode(True)
            show_demo_banner_once()
            # No persistence; affects only current process
            try:
                from flow.cli.utils.theme_manager import theme_manager as _tm
                ok = _tm.get_color("success")
                console.print(f"[{ok}]✓[/{ok}] Demo mode enabled for this shell (no persistence)")
            except Exception:
                pass

        @demo.command("stop", help="Disable demo mode")
        def stop_cmd():
            import shutil as _shutil
            from pathlib import Path as _Path

            from flow.cli.utils.theme_manager import theme_manager as _tm

            ok = _tm.get_color("success")
            # Disable for current process
            os.environ["FLOW_DEMO_MODE"] = "0"
            if os.environ.get("FLOW_PROVIDER", "").lower() == "mock":
                os.environ["FLOW_PROVIDER"] = "mithril"
            # Best-effort clean-up of any legacy persisted state
            try:
                env_path = _Path.home() / ".flow" / "demo.env"
                if env_path.exists():
                    env_path.unlink()
            except Exception:
                pass
            # Remove demo state and cache (best effort)
            try:
                state_path = _Path.home() / ".flow" / "demo_state.json"
                if state_path.exists():
                    state_path.unlink()
            except Exception:
                pass
            try:
                cache_dir = _Path.home() / ".flow" / "cache"
                if cache_dir.exists():
                    _shutil.rmtree(cache_dir, ignore_errors=True)
            except Exception:
                pass
            # If config.yaml currently pins provider to mock, switch back to mithril
            try:
                cfg_path = _Path.home() / ".flow" / "config.yaml"
                if cfg_path.exists():
                    import yaml as _yaml

                    data = _yaml.safe_load(cfg_path.read_text()) or {}
                    if isinstance(data, dict) and str(data.get("provider", "")).lower() == "mock":
                        data["provider"] = "mithril"
                        cfg_path.write_text(
                            _yaml.safe_dump(data, default_flow_style=False, sort_keys=False)
                        )
                        console.print(f"[{ok}]✓[/{ok}] Switched provider to mithril in {cfg_path}")
            except Exception:
                # Best effort only; user can run `flow init --provider mithril` if needed
                pass
            console.print("[dim]Demo mode disabled.[/dim]")


        @demo.command("profile", help="Apply a latency preset (quick|realistic|slow_network)")
        @click.argument("name", type=click.Choice(["quick", "realistic", "slow_network"]))
        def profile_cmd(name: str):
            presets = {
                "quick": {
                    "FLOW_MOCK_LATENCY_MS": "50",
                    "FLOW_MOCK_LATENCY_JITTER_PCT": "0.05",
                },
                "realistic": {
                    "FLOW_MOCK_LATENCY_MS": "150",
                    "FLOW_MOCK_LATENCY_SUBMIT_MS": "300",
                    "FLOW_MOCK_LATENCY_LIST_MS": "200",
                    "FLOW_MOCK_LATENCY_STATUS_MS": "100",
                    "FLOW_MOCK_LATENCY_GET_TASK_MS": "100",
                    "FLOW_MOCK_LATENCY_INSTANCES_MS": "250",
                    "FLOW_MOCK_LATENCY_VOLUME_CREATE_MS": "250",
                    "FLOW_MOCK_LATENCY_VOLUME_DELETE_MS": "250",
                    "FLOW_MOCK_LATENCY_VOLUME_LIST_MS": "150",
                    "FLOW_MOCK_LATENCY_LOGS_MS": "75",
                    "FLOW_MOCK_LATENCY_CANCEL_MS": "150",
                    "FLOW_MOCK_LATENCY_MOUNT_MS": "150",
                    "FLOW_MOCK_LATENCY_UPLOAD_MS": "200",
                    "FLOW_MOCK_LATENCY_JITTER_PCT": "0.1",
                },
                "slow_network": {
                    "FLOW_MOCK_LATENCY_MS": "300",
                    "FLOW_MOCK_LATENCY_JITTER_PCT": "0.3",
                },
            }
            for k, v in presets[name].items():
                os.environ[k] = v
            console.print(f"[dim]Applied profile[/dim] [accent]{name}[/accent]")

        @demo.command("set", help="Set a demo/mock env var for this shell (KEY=VALUE)")
        @click.argument("assignment")
        def set_cmd(assignment: str):
            if "=" not in assignment:
                console.print("[red]Invalid format. Use KEY=VALUE[/red]")
                return
            key, val = assignment.split("=", 1)
            key = key.strip()
            val = val.strip()
            if not key:
                console.print("[red]Invalid key[/red]")
                return
            os.environ[key] = val
            console.print(f"[dim]Set[/dim] {key}=[accent]{val}[/accent]")

        @demo.command("refresh", help="Reset demo state and optionally clear CLI caches")
        @click.option(
            "--cache/--no-cache",
            "clear_cache",
            default=True,
            show_default=True,
            help="Also clear ~/.flow/cache",
        )
        @click.option(
            "--reseed/--no-reseed",
            default=True,
            show_default=True,
            help="Force re-seeding by touching the mock provider",
        )
        def refresh_cmd(clear_cache: bool, reseed: bool):
            """Remove persisted demo state and optionally clear caches.

            Useful after changing mock seed data or when the demo display looks stale.
            """
            import shutil
            from pathlib import Path

            state_path = Path.home() / ".flow" / "demo_state.json"
            cache_dir = Path.home() / ".flow" / "cache"

            # Remove state
            try:
                if state_path.exists():
                    state_path.unlink()
                    from flow.cli.utils.theme_manager import theme_manager as _tm

                    ok = _tm.get_color("success")
                    console.print(f"[{ok}]✓[/{ok}] Removed {state_path}")
                else:
                    console.print(f"[dim]No demo state found at {state_path}[/dim]")
            except Exception as e:
                from rich.markup import escape

                console.print(f"[red]Failed to remove demo state:[/red] {escape(str(e))}")

            # Remove cache if requested
            if clear_cache:
                try:
                    if cache_dir.exists():
                        shutil.rmtree(cache_dir, ignore_errors=True)
                        from flow.cli.utils.theme_manager import theme_manager as _tm2

                        ok = _tm2.get_color("success")
                        console.print(f"[{ok}]✓[/{ok}] Cleared cache directory {cache_dir}")
                    else:
                        console.print(f"[dim]No cache directory found at {cache_dir}[/dim]")
                except Exception as e:
                    from rich.markup import escape

                    console.print(f"[red]Failed to clear cache:[/red] {escape(str(e))}")

            # Optionally trigger provider initialization to re-seed immediately
            if reseed:
                try:
                    from flow import Flow

                    # Touch provider to trigger seeding in mock
                    Flow().list_tasks(limit=1)
                    console.print("[dim]Re-seeded demo provider state[/dim]")
                except Exception:
                    # Non-fatal; next command will seed
                    pass

            console.print(
                "\nNext: run [accent]flow status[/accent] (you can prefix with FLOW_PREFETCH=0 for a cold fetch)"
            )

        return demo


command = DemoCommand()
