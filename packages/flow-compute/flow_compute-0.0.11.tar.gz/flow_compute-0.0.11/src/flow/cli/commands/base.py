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

import click
from ..utils.theme_manager import theme_manager

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
        console.print(f"[red]Error:[/red] {message_text}")

        # Display suggestions only if not already embedded in the message
        if ("Suggestions:" not in message_text) and hasattr(error, "suggestions") and error.suggestions:
            console.print("\n[dim]Suggestions:[/dim]")
            for suggestion in error.suggestions:
                console.print(f"  • {suggestion}")

        raise click.exceptions.Exit(exit_code)

    def handle_auth_error(self) -> None:
        """Display auth error and guide to init command."""
        console.print("[red]Authentication failed[/red]")
        console.print("\nPlease run [cyan]flow init[/cyan] to configure your credentials")
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
