"""Guided tutorial command for Flow CLI.

This command walks new users through:
1) Interactive configuration (provider setup wizard)
2) Quick health validation (connectivity/auth/ssh)
3) Optional verification example run

Usage:
  flow tutorial             # Full guided setup
  flow tutorial --yes       # Auto-confirm running the verification example
  flow tutorial --skip-example
  flow tutorial --example gpu-test

Alias: `flow setup` (added by the CLI app for convenience)
"""

from typing import Optional

import click

from rich.panel import Panel
from rich.prompt import Confirm

from flow import Flow
from .base import BaseCommand, console
from flow.cli.utils.animated_progress import AnimatedEllipsisProgress
from flow._internal.config_loader import ConfigLoader
from flow.cli.utils.hyperlink_support import hyperlink_support


class TutorialCommand(BaseCommand):
    """Interactive, end-to-end onboarding for the Flow SDK."""

    @property
    def name(self) -> str:
        return "tutorial"

    @property
    def help(self) -> str:
        return "Guided setup: configure provider, validate health, and run a verification example"

    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        @click.option("--provider", envvar="FLOW_PROVIDER", help="Provider to use (e.g., mithril)")
        @click.option(
            "--example",
            type=click.Choice(["minimal", "gpu-test", "system-info"], case_sensitive=False),
            default="gpu-test",
            show_default=True,
            help="Verification example to run",
        )
        @click.option("--skip-init", is_flag=True, help="Skip interactive setup wizard")
        @click.option("--force-init", is_flag=True, help="Run setup wizard even if config is valid")
        @click.option("--skip-health", is_flag=True, help="Skip quick health validation")
        @click.option("--skip-example", is_flag=True, help="Skip verification example run")
        @click.option("--yes", "--y", "yes", is_flag=True, help="Auto-confirm prompts")
        def tutorial(
            provider: Optional[str],
            example: str,
            skip_init: bool,
            force_init: bool,
            skip_health: bool,
            skip_example: bool,
            yes: bool,
        ):
            """Run the guided tutorial."""
            # Intro
            console.print(
                Panel(
                    "Welcome! This guided flow will set up your credentials, validate connectivity, and optionally run a quick verification job.",
                    title="Flow Tutorial",
                )
            )

            # Show current configuration status (best effort)
            try:
                sources = ConfigLoader().load_all_sources()
                mith = sources.get_mithril_config()
                api_present = bool(sources.api_key)
                project = mith.get("project", "—")
                region = mith.get("region", "—")
                status_lines = [
                    f"API key: {'[green]✓[/green]' if api_present else '[red]✗[/red]'}",
                    f"Project: [cyan]{project}[/cyan]",
                    f"Region: [cyan]{region}[/cyan]",
                ]
                console.print(Panel("\n".join(status_lines), title="Current Configuration"))
            except Exception:
                pass

            # 1) Interactive configuration
            config_valid = False
            try:
                config_valid = ConfigLoader().has_valid_config()
            except Exception:
                config_valid = False

            should_run_wizard = not skip_init and (force_init or not config_valid)

            if not skip_init and config_valid and not force_init:
                console.print("[dim]Valid configuration detected. Skipping setup wizard (use --force-init to rerun).[/dim]")

            if should_run_wizard:
                from .init import run_setup_wizard

                with AnimatedEllipsisProgress(console, "Starting setup wizard", start_immediately=True):
                    ok = run_setup_wizard(provider)
                if not ok:
                    console.print("[red]Setup wizard did not complete successfully[/red]")
                    raise click.exceptions.Exit(1)
            else:
                if skip_init and not config_valid:
                    console.print("[yellow]No valid configuration found; running setup wizard is required for first-time use[/yellow]")
                    from .init import run_setup_wizard as _wiz
                    with AnimatedEllipsisProgress(console, "Starting setup wizard", start_immediately=True):
                        ok = _wiz(provider)
                    if not ok:
                        console.print("[red]Setup wizard did not complete successfully[/red]")
                        raise click.exceptions.Exit(1)
                elif skip_init:
                    console.print("[dim]Skipping setup wizard (--skip-init)[/dim]")

            # 2) Quick health validation
            if not skip_health:
                try:
                    from .health import HealthChecker

                    with AnimatedEllipsisProgress(console, "Validating connectivity and auth", transient=True):
                        checker = HealthChecker(Flow())
                        checker.check_connectivity()
                        checker.check_authentication()
                        checker.check_ssh_keys()

                    report = checker.generate_report()
                    issues = report.get("summary", {}).get("issues", 0)
                    warnings = report.get("summary", {}).get("warnings", 0)
                    successes = report.get("summary", {}).get("successes", 0)

                    status = "[green]✓ Healthy[/green]" if issues == 0 else "[yellow]⚠ Checks found issues[/yellow]"
                    console.print(
                        Panel(
                            f"{status}\n\n✓ {successes} checks passed\n⚠ {warnings} warnings\n✗ {issues} issues",
                            title="Quick Health Summary",
                        )
                    )
                    if issues > 0:
                        # Show a few actionable issues immediately
                        details = (report.get("details", {}) or {}).get("issues", [])
                        for item in details[:3]:
                            cat = item.get("category", "Issue")
                            msg = item.get("message", "")
                            console.print(f"  • [red]{cat}[/red]: {msg}")
                            if item.get("suggestion"):
                                console.print(f"    → [dim]{item['suggestion']}[/dim]")
                        console.print("\n[dim]Run 'flow health --verbose' for detailed diagnostics[/dim]")
                        console.print("[dim]Try auto-fixes: 'flow health --fix'[/dim]")
                except Exception as e:
                    console.print(f"[yellow]Health validation skipped due to error:[/yellow] {e}")
            else:
                console.print("[dim]Skipping health validation (--skip-health)[/dim]")

            # 3) Optional verification example
            if not skip_example:
                should_run = yes or Confirm.ask(
                    f"Run verification example now? [dim](recommended)[/dim]", default=True
                )
                if should_run:
                    try:
                        # Reuse example command implementation for consistent UX
                        from . import example as example_cmd

                        console.print(Panel(f"Running example: [cyan]{example}[/cyan]", title="Verification"))
                        example_cmd.command._execute(example, show=False)
                        console.print("\n[dim]Tip: Use 'flow status' to monitor, or 'flow logs <task> -f' to stream logs[/dim]")
                    except Exception as e:
                        console.print(f"[red]Failed to run example:[/red] {e}")
                        raise click.exceptions.Exit(1)
                else:
                    console.print(f"You can run later: [cyan]flow example {example}[/cyan]")
            else:
                console.print("[dim]Skipping example run (--skip-example)[/dim]")

            # Finish with next steps
            self.show_next_actions(
                [
                    "Explore examples: [cyan]flow example --verbose[/cyan]",
                    "Check status: [cyan]flow status[/cyan]",
                    "Submit a job: [cyan]flow run task.yaml[/cyan]",
                    "(Optional) Manage SSH keys: [cyan]flow ssh-keys list --sync[/cyan]",
                ]
            )

            # Link to docs for deeper dive
            try:
                link = hyperlink_support.create_link("Quickstart Guide →", "https://docs.mithril.ai/quickstart")
                console.print(f"\n[dim]{link}[/dim]")
            except Exception:
                console.print("\n[dim]Docs: https://docs.mithril.ai/quickstart[/dim]")

        return tutorial


# Export command instance
command = TutorialCommand()


