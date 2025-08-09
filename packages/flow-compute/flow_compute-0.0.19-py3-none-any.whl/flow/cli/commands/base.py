"""Base command interface for Flow CLI.

Defines the contract for all CLI commands to ensure consistency.

Example implementation:
    class MyCommand(BaseCommand):
        @property
        def name(self) -> str:
            return "mycommand"

        @property
        def help(self) -> str:
            return "Do something useful"

        def get_command(self) -> click.Command:
            @click.command(name=self.name, help=self.help)
            def mycommand():
                console.print("Hello!")
            return mycommand
"""

from abc import ABC, abstractmethod
import os

import click
from ..utils.theme_manager import theme_manager
from rich.markup import escape

console = theme_manager.create_console()


class BaseCommand(ABC):
    """Abstract base for CLI commands."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Command name for CLI usage."""
        pass

    @property
    @abstractmethod
    def help(self) -> str:
        """Help text for the command."""
        pass

    @abstractmethod
    def get_command(self) -> click.Command:
        """Create and return click command."""
        pass

    @property
    def manages_own_progress(self) -> bool:
        """Whether this command manages its own progress display.

        Commands that return True will not have the default "Looking up task..."
        animation shown by the task selector mixin. This prevents flickering
        when commands have their own progress indicators.

        Returns:
            False by default, override to return True if command has custom progress
        """
        return False

    def handle_error(self, error: Exception, exit_code: int = 1) -> None:
        """Display error and exit.

        Args:
            error: Exception to display
            exit_code: Process exit code
        """
        # Many FlowError messages already include a formatted "Suggestions:" block.
        # Avoid printing suggestions twice by detecting this case.
        message_text = str(error)

        # Strong, opinionated routing for auth misconfiguration
        if (
            isinstance(error, ValueError)
            and (
                ("Authentication not configured" in message_text)
                or ("MITHRIL_API_KEY" in message_text)
            )
        ) or (
            "Authentication not configured" in message_text
        ):
            self.handle_auth_error()
            return

        console.print(f"[red]Error:[/red] {escape(message_text)}")

        # Display suggestions only if not already embedded in the message
        if ("Suggestions:" not in message_text) and hasattr(error, "suggestions") and error.suggestions:
            console.print("\n[dim]Suggestions:[/dim]")
            for suggestion in error.suggestions:
                console.print(f"  • {escape(str(suggestion))}")

        raise click.exceptions.Exit(exit_code)

    def handle_auth_error(self) -> None:
        """Display top-tier authentication guidance and exit.

        Provides actionable, shell-aware steps and CI-friendly options.
        """
        console.print("[red]Authentication not configured[/red]\n")

        console.print("[dim]Quick fixes:[/dim]")
        console.print("  1) Run [cyan]flow init[/cyan] (recommended interactive setup)")
        console.print("  2) Or set [cyan]MITHRIL_API_KEY[/cyan] in your environment")

        # Suggest a shell-specific one-liner
        shell = os.environ.get("SHELL", "").lower()
        if "fish" in shell:
            example = 'set -x MITHRIL_API_KEY "fkey_XXXXXXXXXXXXXXXX"'
        elif "powershell" in shell or "pwsh" in shell:
            example = '$env:MITHRIL_API_KEY = "fkey_XXXXXXXXXXXXXXXX"'
        elif os.name == "nt":  # Windows CMD
            example = 'set MITHRIL_API_KEY="fkey_XXXXXXXXXXXXXXXX"'
        else:  # bash/zsh/sh
            example = 'export MITHRIL_API_KEY="fkey_XXXXXXXXXXXXXXXX"'

        console.print(f"     e.g., [cyan]{example}[/cyan]")

        # Helpful links and non-interactive options
        console.print("\n[dim]Get an API key:[/dim] [link]https://app.mithril.ai/account/api-keys[/link]")
        console.print(
            "[dim]CI/non-interactive:[/dim] [cyan]flow init --api-key $MITHRIL_API_KEY --yes[/cyan]"
        )
        console.print("[dim]Inspect current config:[/dim] [cyan]flow init --show[/cyan]")

        raise click.exceptions.Exit(1)

    def show_next_actions(self, recommendations: list) -> None:
        """Display next action recommendations.

        Args:
            recommendations: List of recommended commands/actions
        """
        if not recommendations:
            return

        console.print("\n[dim]Next steps:[/dim]")
        for recommendation in recommendations:
            console.print(f"  • {recommendation}")
