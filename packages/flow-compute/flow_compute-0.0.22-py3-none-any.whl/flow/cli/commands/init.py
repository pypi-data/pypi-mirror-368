"""Init command for Flow SDK configuration.

Supports both interactive wizard and direct configuration via flags.

Examples:
    Interactive setup:
        $ flow init

    Direct configuration:
        $ flow init --provider mithril --api-key fkey_xxx --project myproject

    Dry run to preview:
        $ flow init --provider mithril --dry-run
"""

import asyncio
import logging
import os
from pathlib import Path

import click
import yaml
from rich.markup import escape

from flow.cli.commands.base import BaseCommand
from flow.cli.utils.config_validator import ConfigValidator
from flow.cli.utils.mask_utils import mask_api_key, mask_config_for_display
from flow.cli.utils.theme_manager import theme_manager

# Import private components
from flow.core.setup_registry import SetupRegistry, register_providers

logger = logging.getLogger(__name__)

# Create console instance
console = theme_manager.create_console()


def run_setup_wizard(provider: str | None = None) -> bool:
    """Run the setup wizard for the resolved provider.

    If provider is None, attempt to detect from existing config or prompt.
    """
    from flow.core.generic_setup_wizard import GenericSetupWizard

    # Register providers first
    register_providers()

    resolved_provider = provider
    if not resolved_provider:
        # Try to detect from existing config
        try:
            from flow._internal.config_loader import ConfigLoader

            loader = ConfigLoader()
            current = loader.load_all_sources()
            resolved_provider = current.provider or None
        except Exception:
            resolved_provider = None

    if not resolved_provider:
        # If still not resolved, and only one adapter exists, use it; otherwise list providers
        providers = SetupRegistry.list_adapters()
        if len(providers) == 1:
            resolved_provider = providers[0]
        elif len(providers) > 1:
            # Prompt user to select a provider (fallback to first if non-interactive)
            try:
                from flow.cli.utils.interactive_selector import InteractiveSelector, SelectionItem

                options = [
                    SelectionItem(value=p, id=p, title=p.title(), subtitle="", status="")
                    for p in providers
                ]
                selector = InteractiveSelector(
                    options,
                    lambda x: x,
                    title="Select provider",
                    breadcrumbs=["Flow Setup", "Provider"],
                    preferred_viewport_size=5,
                )
                choice = selector.select()
                resolved_provider = choice if isinstance(choice, str) else None
            except Exception:
                resolved_provider = providers[0]

    adapter = SetupRegistry.get_adapter(resolved_provider or "")
    if not adapter:
        console.print(f"[red]Error: Provider not available: {resolved_provider}[/red]")
        return False

    wizard = GenericSetupWizard(console, adapter)

    try:
        return wizard.run()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Setup cancelled[/yellow]")
        return False
    except Exception as e:
        console.print(f"\n\n[red]Setup error:[/red] {escape(str(e))}")
        logger.exception("Setup wizard error")
        return False


class InitCommand(BaseCommand):
    """Init command implementation.

    Handles both interactive wizard mode and direct configuration
    via command-line options.
    """

    def __init__(self):
        """Initialize init command."""
        super().__init__()
        self.validator = ConfigValidator()

    @property
    def name(self) -> str:
        return "init"

    @property
    def help(self) -> str:
        return "Configure Flow SDK credentials and provider settings"

    def get_command(self) -> click.Command:
        from flow.cli.utils.mode import demo_aware_command

        @click.command(name=self.name, help=self.help)
        @click.option("--provider", envvar="FLOW_PROVIDER", help="Provider to use")
        @click.option(
            "--demo",
            is_flag=True,
            help="Enable demo mode: configure mock provider (no real provisioning)",
        )
        @click.option("--api-key", help="API key for authentication")
        @click.option("--project", help="Project name")
        @click.option("--region", help="Default region")
        @click.option("--api-url", help="API endpoint URL")
        @click.option("--dry-run", is_flag=True, help="Show configuration without saving")
        @click.option(
            "--output",
            type=click.Path(dir_okay=False),
            help="Write dry-run YAML to file (with --dry-run)",
        )
        @click.option("--verbose", "-v", is_flag=True, help="Show detailed setup information")
        @click.option("--reset", is_flag=True, help="Reset configuration to start fresh")
        @click.option("--show", is_flag=True, help="Print current resolved configuration and exit")
        @click.option("--yes", is_flag=True, help="Non-interactive; answer yes to prompts (CI)")
        @demo_aware_command(flag_param="demo")
        def init(
            provider: str | None,
            demo: bool,
            api_key: str | None,
            project: str | None,
            region: str | None,
            api_url: str | None,
            dry_run: bool,
            output: str | None,
            verbose: bool,
            reset: bool,
            show: bool,
            yes: bool,
        ):
            """Configure Flow SDK.

            \b
            Examples:
                flow init                    # Interactive setup wizard
                flow init --dry-run          # Preview configuration
                flow init --provider mithril --api-key xxx  # Direct setup

            Use 'flow init --verbose' for detailed configuration options.
            """
            if demo:
                # Force mock provider and clear sensitive fields
                provider = "mock"
                api_key = None
                os.environ["FLOW_DEMO_MODE"] = "1"
                os.environ["FLOW_PROVIDER"] = "mock"

            if verbose and not any([provider, api_key, project, region, api_url, dry_run, demo]):
                console.print("\n[bold]Flow SDK Configuration Guide:[/bold]\n")
                console.print("Interactive setup:")
                console.print("  flow init                         # Step-by-step wizard")
                console.print("  flow init --dry-run               # Preview without saving")
                console.print(
                    "  flow init --demo                  # Configure mock provider (no real instances)\n"
                )

                console.print("Direct configuration:")
                console.print(
                    "  flow init --provider mithril --api-key fkey_xxx --project myproject"
                )
                console.print("  flow init --region us-west-2      # Set default region")
                console.print("  flow init --api-url https://custom.api.com  # Custom endpoint\n")

                console.print("Environment variables:")
                console.print("  export FLOW_API_KEY=fkey_xxx      # Set API key")
                console.print("  export FLOW_PROJECT=myproject     # Set project")
                console.print("  export FLOW_REGION=us-west-2      # Set region\n")

                console.print("Configuration files:")
                console.print("  ~/.flow/config.yaml               # User configuration")
                console.print("  ./.flow/config.yaml               # Project configuration")
                console.print("  $FLOW_CONFIG                      # Custom config path\n")

                console.print("Next steps after init:")
                console.print("  • Test connection: flow health")
                console.print("  • Upload SSH keys: flow ssh-keys upload ~/.ssh/id_rsa.pub")
                console.print("  • Run first task: flow run examples/hello-gpu.yaml")
                console.print("  • Start dev environment: flow dev\n")
                return

            # Handle --show
            if show:
                try:
                    from flow._internal.config_loader import ConfigLoader

                    loader = ConfigLoader()
                    sources = loader.load_all_sources()
                    import yaml as _yaml

                    # Build a user-facing view and mask sensitive values
                    show_dict = {
                        "provider": sources.provider,
                        "api_key": mask_api_key(sources.api_key),
                        "mithril": sources.get_mithril_config(),
                    }
                    console.print(_yaml.safe_dump(show_dict, default_flow_style=False))
                except Exception as e:
                    console.print(f"[red]Error loading configuration:[/red] {escape(str(e))}")
                    raise click.exceptions.Exit(1)
                return

            # Run async function safely in or out of an existing loop
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None
            if loop and loop.is_running():
                try:
                    import nest_asyncio  # type: ignore

                    try:
                        nest_asyncio.apply()
                    except Exception:
                        pass
                except Exception:
                    pass
                loop.run_until_complete(
                    self._init_async(
                        provider,
                        api_key,
                        project,
                        region,
                        api_url,
                        dry_run,
                        verbose,
                        reset,
                        output_path=output,
                        assume_yes=yes,
                    )
                )
            else:
                asyncio.run(
                    self._init_async(
                        provider,
                        api_key,
                        project,
                        region,
                        api_url,
                        dry_run,
                        verbose,
                        reset,
                        output_path=output,
                        assume_yes=yes,
                    )
                )

        return init

    async def _init_async(
        self,
        provider: str | None,
        api_key: str | None,
        project: str | None,
        region: str | None,
        api_url: str | None,
        dry_run: bool,
        verbose: bool = False,
        reset: bool = False,
        output_path: str | None = None,
        assume_yes: bool = False,
    ):
        """Execute init command.

        Args:
            provider: Provider name
            api_key: API key for authentication
            project: Project name
            region: Default region
            api_url: Custom API endpoint
            dry_run: Preview without saving
            reset: Reset existing configuration first
        """
        # Handle reset flag first
        if reset:
            if await self._reset_configuration():
                from flow.cli.utils.theme_manager import theme_manager as _tm

                success_color = _tm.get_color("success")
                console.print(
                    f"[{success_color}]✓[/{success_color}] Configuration reset successfully"
                )
                if not (provider or api_key or project or region or api_url):
                    console.print("\nStarting fresh setup...")
                    console.print("")  # Add blank line before wizard
            else:
                return  # User cancelled or error occurred

        # In demo mode with provider 'mock' and no explicit options, fast-path to a friendly UX
        try:
            from flow.cli.utils.mode import is_demo_active

            demo_on = is_demo_active()
        except Exception:
            demo_on = False

        # Honor explicit provider choice: if user set --provider mithril (or any non-mock),
        # do NOT force demo/mock wizard even if demo env is active.
        if provider and provider != "mock":
            demo_on = False

        if (((provider is None) and demo_on) or (provider == "mock")) and not any(
            [api_key, project, region, api_url, dry_run]
        ):
            # Run the full setup wizard for the mock provider so users can reconfigure demo settings
            ok = run_setup_wizard("mock")
            if not ok:
                raise click.exceptions.Exit(1)
            # Enable shell completion after a successful wizard run
            self._setup_shell_completion()
            return True

        # Treat as non-interactive only when actual configuration flags are provided.
        # Having only a provider value (e.g., from demo mode env default) should not
        # force non-interactive mode; users expect the interactive wizard in that case.
        explicit_non_interactive = bool(api_key or project or region or api_url or dry_run)

        if explicit_non_interactive:
            # Non-interactive mode with provided options
            success = await self._configure_with_options(
                provider, api_key, project, region, api_url, dry_run, output_path
            )
        else:
            # Interactive mode - offer fast demo mode escape hatch only on first run
            if assume_yes:
                console.print(
                    "[red]Error:[/red] --yes requires non-interactive options. Provide --provider and related flags."
                )
                return False
            # If provider not specified, offer demo mode only on the very first init run
            # (i.e., when no user config file exists yet). Subsequent runs bypass this confirmation.
            from pathlib import Path as _Path

            first_run = not (_Path.home() / ".flow" / "config.yaml").exists()
            if not provider and first_run:
                try:
                    from rich.prompt import Confirm

                    use_demo = Confirm.ask(
                        "Start in demo mode (no real provisioning, mock provider)?",
                        default=True,
                    )
                    if use_demo:
                        # Persist provider: mock and return
                        try:
                            from flow._internal.init.writer import ConfigWriter

                            writer = ConfigWriter()
                            writer.write({"provider": "mock"}, validation=None)  # type: ignore[arg-type]
                            from flow.cli.utils.theme_manager import theme_manager as _tm0

                            success_color = _tm0.get_color("success")
                            console.print(
                                f"[{success_color}]✓[/{success_color}] Demo mode enabled (provider: mock)."
                            )
                            console.print(
                                "[dim]Tip:[/dim] Run with --no-demo or re-run 'flow init' to configure real Mithril integration."
                            )
                            self.show_next_actions(
                                [
                                    "Explore safely: [accent]flow tutorial[/accent]",
                                    "Submit a demo run: [accent]flow run --demo 'nvidia-smi' -i h100[/accent]",
                                    "Switch to real: [accent]flow init --provider mithril[/accent]",
                                ]
                            )
                            return True
                        except Exception:
                            # Fallback to wizard if writing fails
                            pass
                except Exception:
                    pass
            # Pass provider if given; otherwise let wizard resolve
            success = run_setup_wizard(provider)
            if success:
                # Clear, affirmative success panel and next actions
                try:
                    from flow.cli.commands.feedback import feedback

                    feedback.success(
                        "You're set up. Your Flow CLI is ready.",
                        title="Setup complete",
                        subtitle="Credentials saved and provider configured",
                    )
                except Exception:
                    console.print("\n[green]✓[/green] Setup complete")

                self.show_next_actions(
                    [
                        "Run your first GPU test: [accent]flow example gpu-test[/accent]",
                        "Submit a job: [accent]flow run examples/configs/basic.yaml[/accent]",
                        "Monitor tasks: [accent]flow status[/accent]",
                    ]
                )

        # Set up shell completion after successful configuration (not on dry run)
        if success and not dry_run:
            self._setup_shell_completion()

        if not success:
            raise click.exceptions.Exit(1)

    async def _configure_with_options(
        self,
        provider: str | None,
        api_key: str | None,
        project: str | None,
        region: str | None,
        api_url: str | None,
        dry_run: bool,
        output_path: str | None,
    ) -> bool:
        """Configure using command-line options.

        Prompts for missing required values if needed.
        Validates provider and saves configuration.

        Returns:
            bool: True if configuration was successful, False otherwise
        """
        # Register providers
        register_providers()

        # Resolve provider for non-interactive path with sensible defaults
        if not provider:
            adapters = SetupRegistry.list_adapters()
            if len(adapters) == 1:
                provider = adapters[0]
            elif "mithril" in adapters:
                provider = "mithril"
            else:
                console.print(
                    "[red]Error:[/red] Provider must be specified with --provider in non-interactive mode"
                )
                return False

        adapter = SetupRegistry.get_adapter(provider)
        if not adapter:
            console.print(
                f"[red]Error:[/red] Unknown or unavailable provider: {escape(str(provider))}"
            )
            return False

        # Build config from provided options only (no prompts in non-interactive path)
        config: dict = {"provider": provider}
        if api_key:
            # Validate via adapter
            vr = adapter.validate_field("api_key", api_key)
            if not vr.is_valid:
                console.print(f"[red]Invalid API key:[/red] {escape(str(vr.message))}")
                return False
            config["api_key"] = api_key
            # Show masked key for feedback
            from flow.cli.utils.theme_manager import theme_manager as _tm2

            success_color = _tm2.get_color("success")
            console.print(
                f"[{success_color}]✓[/{success_color}] API key validated: {mask_api_key(api_key)}"
            )
            # Cost awareness warning and demo hint
            if provider == "mithril":
                console.print(
                    "\n[dim]Note:[/dim] Running tasks provisions real infrastructure and may incur costs."
                )
                console.print(
                    "Use [accent]--dry-run[/accent] to preview, or [accent]flow init --demo[/accent] / [accent]flow tutorial --demo[/accent] for a safe mock mode."
                )
        if project:
            vr = adapter.validate_field("project", project, {"api_key": config.get("api_key")})
            if not vr.is_valid:
                console.print(f"[red]Invalid project:[/red] {escape(str(vr.message))}")
                return False
            config["project"] = project
        if region:
            vr = adapter.validate_field("region", region)
            if not vr.is_valid:
                console.print(f"[red]Invalid region:[/red] {escape(str(vr.message))}")
                return False
            config["region"] = region
        if api_url:
            config["api_url"] = api_url

        # If required fields missing, fail fast in non-interactive mode
        required = [f.name for f in adapter.get_configuration_fields() if f.required]
        missing = [name for name in required if name not in config]
        if missing:
            console.print(
                f"[red]Missing required fields for non-interactive init:[/red] {', '.join(missing)}"
            )
            return False

        if dry_run:
            console.print("\n[bold]Configuration (dry run)[/bold]")
            console.print("─" * 50)
            # Create masked config for display based on field specs
            display_config = mask_config_for_display(config, adapter.get_configuration_fields())
            console.print(yaml.safe_dump(display_config, default_flow_style=False))
            if output_path:
                try:
                    with open(output_path, "w") as f:
                        yaml.safe_dump(display_config, f, default_flow_style=False)
                    from flow.cli.utils.theme_manager import theme_manager as _tm3

                    success_color = _tm3.get_color("success")
                    console.print(
                        f"\n[{success_color}]✓[/{success_color}] Wrote masked preview to {output_path}"
                    )
                except Exception as e:
                    console.print(f"[red]Error writing output file:[/red] {escape(str(e))}")
                    return False
            return True

        # Save via adapter to ensure consistent behavior
        saved = adapter.save_configuration(config)
        if not saved:
            console.print("[red]Failed to save configuration[/red]")
            return False

        from flow.cli.utils.theme_manager import theme_manager as _tm4

        success_color = _tm4.get_color("success")
        console.print(f"\n[{success_color}]✓[/{success_color}] Configuration saved")
        self.show_next_actions(
            [
                "Test your setup: [accent]flow health[/accent]",
                "Run GPU test: [accent]flow example gpu-test[/accent]",
                "View examples: [accent]flow example[/accent]",
                "Submit your first task: [accent]flow run task.yaml[/accent]",
                "(Optional) Upload existing SSH key: [accent]flow ssh-keys upload ~/.ssh/id_ed25519.pub[/accent]",
            ]
        )
        return True

    async def _prompt_for_value(
        self, name: str, password: bool = False, default: str | None = None
    ) -> str | None:
        """Prompt user for configuration value.

        Args:
            name: Value name to prompt for
            password: Hide input for sensitive values
            default: Default value if none provided

        Returns:
            User input or None
        """
        from rich.prompt import Prompt

        return await asyncio.get_event_loop().run_in_executor(
            None, lambda: Prompt.ask(name, password=password, default=default)
        )

    # Legacy method removed in favor of mask_utils.mask_api_key

    async def _reset_configuration(self) -> bool:
        """Reset Flow SDK configuration to initial state.

        Removes configuration files with a safety prompt that lists what will be
        deleted and asks for confirmation.

        Returns:
            bool: True if reset, False if cancelled
        """
        from rich.prompt import Confirm

        flow_dir = Path.home() / ".flow"
        files_to_clear = []

        # Check what files exist
        if flow_dir.exists():
            config_file = flow_dir / "config.yaml"
            if config_file.exists():
                files_to_clear.append(config_file)

            # Check for provider-specific credential files
            for cred_file in flow_dir.glob("credentials.*"):
                files_to_clear.append(cred_file)

        if not files_to_clear:
            console.print("[yellow]No configuration files found to reset[/yellow]")
            return True

        # Show what will be deleted
        console.print("\n[bold]The following files will be removed:[/bold]")
        for file in files_to_clear:
            console.print(f"  • {file}")

        # Safety prompt before deletion
        console.print("")
        confirm = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: Confirm.ask("[yellow]Are you sure you want to reset configuration?[/yellow]"),
        )

        if not confirm:
            console.print("[dim]Reset cancelled[/dim]")
            return False

        # Perform deletion
        for file in files_to_clear:
            try:
                file.unlink()
            except Exception as e:
                console.print(f"[red]Error deleting {file}: {escape(str(e))}[/red]")
                return False

        return True

    def _setup_shell_completion(self):
        """Set up shell completion after successful init.

        Adds a guarded completion line to the user's shell config when
        possible. Skips silently if the shell cannot be detected.
        """
        try:
            import shutil
            from pathlib import Path

            # Check if flow command is available
            flow_cmd = shutil.which("flow")
            if not flow_cmd:
                return  # Command not in PATH yet

            # Detect user's shell
            shell_path = os.environ.get("SHELL", "")
            shell_name = os.path.basename(shell_path)

            if shell_name not in ["bash", "zsh", "fish"]:
                # Try to detect from parent process
                try:
                    import psutil

                    parent = psutil.Process(os.getppid())
                    parent_name = parent.name()
                    for shell in ["bash", "zsh", "fish"]:
                        if shell in parent_name:
                            shell_name = shell
                            break
                except Exception:
                    pass

            if shell_name not in ["bash", "zsh", "fish"]:
                return  # Can't detect shell, skip completion setup

            # Determine shell config file
            shell_configs = {
                "bash": "~/.bashrc",
                "zsh": "~/.zshrc",
                "fish": "~/.config/fish/config.fish",
            }

            config_file = Path(shell_configs.get(shell_name, "")).expanduser()
            if not config_file or not config_file.parent.exists():
                return

            # Check if completion is already installed
            completion_marker = "# Flow CLI completion"
            if config_file.exists():
                content = config_file.read_text()
                if completion_marker in content:
                    return  # Already installed

            # Generate appropriate, shell-guarded completion line
            try:
                from flow.cli.utils.shell_completion import CompletionCommand as _CompletionCommand

                completion_line = _CompletionCommand()._get_completion_line(shell_name)
            except Exception:
                # Fallback to conservative guarded lines
                if shell_name == "bash":
                    completion_line = 'if [ -n "${BASH_VERSION-}" ]; then eval "$(_FLOW_COMPLETE=bash_source flow)"; fi'
                elif shell_name == "zsh":
                    completion_line = 'if [ -n "${ZSH_VERSION-}" ]; then eval "$(_FLOW_COMPLETE=zsh_source flow)"; fi'
                elif shell_name == "fish":
                    completion_line = (
                        'if test -n "$FISH_VERSION"; _FLOW_COMPLETE=fish_source flow | source; end'
                    )
                else:
                    return

            # Add completion to shell config
            with open(config_file, "a") as f:
                f.write(f"\n{completion_marker}\n{completion_line}\n")

            from flow.cli.utils.theme_manager import theme_manager as _tm5

            success_color = _tm5.get_color("success")
            console.print(
                f"\n[{success_color}]✓ Shell completion enabled for {shell_name}[/{success_color}]"
            )
            # Offer an immediate, one-shot activation for the current shell session
            console.print(f"  Enable now in this shell: [accent]{completion_line}[/accent]")
            console.print(f"  Or restart your shell, or run: [accent]source {config_file}[/accent]")

        except Exception:
            # Silently skip if completion setup fails
            pass


# Export command instance
command = InitCommand()
