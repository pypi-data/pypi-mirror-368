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
from typing import Optional

import click
import yaml
from flow.cli.commands.base import BaseCommand
from ..utils.theme_manager import theme_manager
from flow.cli.utils.config_validator import ConfigValidator, ValidationStatus

# Import private components
from flow.core.setup_registry import SetupRegistry, register_providers

logger = logging.getLogger(__name__)

# Create console instance
console = theme_manager.create_console()


def run_setup_wizard(provider: Optional[str] = None) -> bool:
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
                selector = InteractiveSelector(options, lambda x: x, title="Select provider")
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
        console.print(f"\n\n[red]Setup error:[/red] {e}")
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
        @click.command(name=self.name, help=self.help)
        @click.option("--provider", envvar="FLOW_PROVIDER", help="Provider to use")
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
        def init(
            provider: Optional[str],
            api_key: Optional[str],
            project: Optional[str],
            region: Optional[str],
            api_url: Optional[str],
            dry_run: bool,
            output: Optional[str],
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
            if verbose and not any([provider, api_key, project, region, api_url, dry_run]):
                console.print("\n[bold]Flow SDK Configuration Guide:[/bold]\n")
                console.print("Interactive setup:")
                console.print("  flow init                         # Step-by-step wizard")
                console.print("  flow init --dry-run               # Preview without saving\n")

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

                    console.print(_yaml.safe_dump(sources.as_dict(), default_flow_style=False))
                except Exception as e:
                    console.print(f"[red]Error loading configuration:[/red] {e}")
                    raise click.exceptions.Exit(1)
                return

            # Run async function
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
        provider: Optional[str],
        api_key: Optional[str],
        project: Optional[str],
        region: Optional[str],
        api_url: Optional[str],
        dry_run: bool,
        verbose: bool = False,
        reset: bool = False,
        output_path: Optional[str] = None,
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
                console.print("[green]✓[/green] Configuration reset successfully")
                if not (provider or api_key or project or region or api_url):
                    console.print("\nStarting fresh setup...")
                    console.print("")  # Add blank line before wizard
            else:
                return  # User cancelled or error occurred

        if provider or api_key or project or region or api_url or dry_run:
            # Non-interactive mode with provided options
            success = await self._configure_with_options(
                provider, api_key, project, region, api_url, dry_run, output_path
            )
        else:
            # Interactive mode - use refactored wizard
            if assume_yes:
                console.print(
                    "[red]Error:[/red] --yes requires non-interactive options. Provide --provider and related flags."
                )
                return False
            # Pass provider if given; otherwise let wizard resolve
            success = run_setup_wizard(provider)
            if success:
                # Show next actions after successful setup
                console.print("")  # Add blank line for spacing
                self.show_next_actions(
                    [
                        "Run an example: [cyan]flow example minimal[/cyan]",
                        "View all examples: [cyan]flow example[/cyan]",
                        "Submit your first task: [cyan]flow run task.yaml[/cyan]",
                    ]
                )

        # Set up shell completion after successful configuration (not on dry run)
        if success and not dry_run:
            self._setup_shell_completion()

        if not success:
            raise click.exceptions.Exit(1)

    async def _configure_with_options(
        self,
        provider: Optional[str],
        api_key: Optional[str],
        project: Optional[str],
        region: Optional[str],
        api_url: Optional[str],
        dry_run: bool,
        output_path: Optional[str],
    ) -> bool:
        """Configure using command-line options.

        Prompts for missing required values if needed.
        Validates provider and saves configuration.

        Returns:
            bool: True if configuration was successful, False otherwise
        """
        # Register providers
        register_providers()

        # Resolve adapter-only path
        if not provider:
            console.print("[red]Error:[/red] Provider must be specified with --provider in non-interactive mode")
            return False

        adapter = SetupRegistry.get_adapter(provider)
        if not adapter:
            console.print(f"[red]Error:[/red] Unknown or unavailable provider: {provider}")
            return False

        # Build config from provided options only (no prompts in non-interactive path)
        config: dict = {"provider": provider}
        if api_key:
            # Validate via adapter
            vr = adapter.validate_field("api_key", api_key)
            if not vr.is_valid:
                console.print(f"[red]Invalid API key:[/red] {vr.message}")
                return False
            config["api_key"] = api_key
        if project:
            vr = adapter.validate_field("project", project, {"api_key": config.get("api_key")})
            if not vr.is_valid:
                console.print(f"[red]Invalid project:[/red] {vr.message}")
                return False
            config["project"] = project
        if region:
            vr = adapter.validate_field("region", region)
            if not vr.is_valid:
                console.print(f"[red]Invalid region:[/red] {vr.message}")
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
            console.print(yaml.safe_dump(config, default_flow_style=False))
            if output_path:
                try:
                    with open(output_path, "w") as f:
                        yaml.safe_dump(config, f, default_flow_style=False)
                    console.print(f"\n[green]✓[/green] Wrote preview to {output_path}")
                except Exception as e:
                    console.print(f"[red]Error writing output file:[/red] {e}")
                    return False
            return True

        # Save via adapter to ensure consistent behavior
        saved = adapter.save_configuration(config)
        if not saved:
            console.print("[red]Failed to save configuration[/red]")
            return False

        console.print("\n[green]✓[/green] Configuration saved")
        self.show_next_actions(
            [
                "Test your setup: [cyan]flow health[/cyan]",
                "Run an example: [cyan]flow example minimal[/cyan]",
                "View all examples: [cyan]flow example[/cyan]",
                "Submit your first task: [cyan]flow run task.yaml[/cyan]",
                "(Optional) Upload existing SSH key: [cyan]flow ssh-keys upload ~/.ssh/id_ed25519.pub[/cyan]",
            ]
        )
        return True

    async def _prompt_for_value(
        self, name: str, password: bool = False, default: Optional[str] = None
    ) -> Optional[str]:
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

    def _mask_api_key(self, api_key: str) -> str:
        """Mask API key for safe display.

        Example:
            'fkey_abcd1234efgh5678' -> 'fkey_abc...5678'
        """
        if len(api_key) > 10:
            return f"{api_key[:8]}...{api_key[-4:]}"
        return "[CONFIGURED]"

    async def _reset_configuration(self) -> bool:
        """Reset Flow SDK configuration to initial state.

        Surgical removal of configuration files with safety prompt.
        Following principles:
        - Single responsibility: only resets config
        - User safety: shows what will be deleted
        - No surprises: requires confirmation

        Returns:
            bool: True if reset, False if cancelled
        """
        from pathlib import Path
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

        # Safety prompt (80/20: most users want confirmation)
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
                console.print(f"[red]Error deleting {file}: {e}[/red]")
                return False

        return True

    def _setup_shell_completion(self):
        """Automatically set up shell completion after successful init.

        This follows the 80/20 principle - works for most users automatically,
        while advanced users can still customize if needed.
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

            # Generate appropriate completion line
            if shell_name == "bash":
                completion_line = 'eval "$(_FLOW_COMPLETE=bash_source flow)"'
            elif shell_name == "zsh":
                completion_line = 'eval "$(_FLOW_COMPLETE=zsh_source flow)"'
            elif shell_name == "fish":
                completion_line = "_FLOW_COMPLETE=fish_source flow | source"
            else:
                return

            # Add completion to shell config
            with open(config_file, "a") as f:
                f.write(f"\n{completion_marker}\n{completion_line}\n")

            console.print(f"\n[green]✓ Shell completion enabled for {shell_name}[/green]")
            console.print(f"  Restart your shell or run: [cyan]source {config_file}[/cyan]")

        except Exception:
            # Silently skip if completion setup fails
            pass


# Export command instance
command = InitCommand()
