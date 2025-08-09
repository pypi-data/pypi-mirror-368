"""Visual feedback module for Flow CLI commands.

This module provides clean abstractions for success/error messages and visual
feedback, building on the rich library's capabilities.
"""

import os
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align


class FeedbackStyle:
    """Configurable styles for feedback messages."""

    # Success styles
    SUCCESS_COLOR = "green"
    SUCCESS_ICON = "✓"
    SUCCESS_BORDER = "green"

    # Error styles
    ERROR_COLOR = "red"
    ERROR_ICON = "✗"
    ERROR_BORDER = "red"

    # Info styles
    INFO_COLOR = "blue"
    INFO_ICON = "ℹ"
    INFO_BORDER = "blue"

    # Panel width
    PANEL_WIDTH = 60


class Feedback:
    """Provides visual feedback for CLI operations."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize feedback with optional console override."""
        self.console = console or Console()
        self.style = FeedbackStyle()
        # Simple mode for CI/CD or minimal output preference
        self.simple_mode = os.environ.get("FLOW_SIMPLE_OUTPUT", "").lower() in ("1", "true", "yes")

    def success(
        self,
        message: str,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
    ) -> None:
        """Display a success message with visual styling."""
        self._display_feedback(
            message=message,
            title=title or "Success",
            subtitle=subtitle,
            icon=self.style.SUCCESS_ICON,
            color=self.style.SUCCESS_COLOR,
            border_style=self.style.SUCCESS_BORDER,
        )

    def error(
        self,
        message: str,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
    ) -> None:
        """Display an error message with visual styling."""
        self._display_feedback(
            message=message,
            title=title or "Error",
            subtitle=subtitle,
            icon=self.style.ERROR_ICON,
            color=self.style.ERROR_COLOR,
            border_style=self.style.ERROR_BORDER,
        )

    def info(
        self,
        message: str,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
    ) -> None:
        """Display an informational message with visual styling."""
        self._display_feedback(
            message=message,
            title=title or "Info",
            subtitle=subtitle,
            icon=self.style.INFO_ICON,
            color=self.style.INFO_COLOR,
            border_style=self.style.INFO_BORDER,
        )

    def _display_feedback(
        self,
        message: str,
        title: str,
        icon: str,
        color: str,
        border_style: str,
        subtitle: Optional[str] = None,
    ) -> None:
        """Internal method to display formatted feedback."""
        if self.simple_mode:
            # Simple output for CI/CD environments
            self.console.print(f"{icon} {title}: {message}", style=color)
            return

        # Build title with icon
        title_text = Text()
        title_text.append(f"{icon} ", style=f"bold {color}")
        title_text.append(title, style=f"bold {color}")

        # Build content
        content = Text(message, style=color)

        # Create panel
        panel = Panel(
            Align.center(content),
            title=title_text,
            subtitle=subtitle,
            border_style=border_style,
            width=self.style.PANEL_WIDTH,
            padding=(1, 2),
        )

        # Display with spacing
        self.console.print()
        self.console.print(Align.center(panel))
        self.console.print()


# Global feedback instance for convenience
feedback = Feedback()
