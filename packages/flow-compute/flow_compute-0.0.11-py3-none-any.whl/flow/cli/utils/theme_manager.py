"""Theme management system for Flow CLI.

Provides automatic terminal theme detection, theme loading, and theme-aware
console creation for consistent visual presentation across different terminal
environments.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass
import json
import yaml

from rich.console import Console
from rich.theme import Theme as RichTheme


@dataclass
class FlowTheme:
    """Flow theme definition."""

    name: str
    colors: Dict[str, str]
    is_dark: bool = True

    def to_rich_theme(self) -> RichTheme:
        """Convert Flow theme to Rich theme."""
        return RichTheme(self.colors)


class ThemeManager:
    """Manages theme detection, loading, and application for Flow CLI."""

    # Built-in themes
    THEMES = {
        "dark": FlowTheme(
            name="dark",
            is_dark=True,
            colors={
                # Base colors
                "default": "white",
                "muted": "bright_black",
                "border": "bright_black",
                "accent": "cyan",
                "selected": "dark_cyan",
                "selected_arrow": "dark_cyan",
                "shortcut_key": "dark_cyan",
                # Status colors
                "success": "green",
                "warning": "yellow",
                "error": "red",
                "info": "blue",
                # Task status colors
                "status.pending": "yellow",
                "status.starting": "blue",
                "status.preparing": "blue",
                "status.running": "green",
                "status.paused": "cyan",
                "status.preempting": "yellow",
                "status.completed": "green",
                "status.failed": "red",
                "status.cancelled": "bright_black",
                # Table elements
                "table.header": "bold white",
                "table.border": "cyan",
                "table.row": "white",
                "table.row.dim": "bright_black",
                # Semantic elements
                "task.name": "white",
                "task.id": "cyan",
                "task.gpu": "white",
                "task.ip": "cyan",
                "task.time": "bright_black",
                "task.duration": "bright_black",
            },
        ),
        "light": FlowTheme(
            name="light",
            is_dark=False,
            colors={
                # Base colors - high contrast for light backgrounds
                "default": "black",
                "muted": "bright_black",
                "border": "black",
                "accent": "blue",
                "selected": "blue",
                "selected_arrow": "blue",
                "shortcut_key": "blue",
                # Status colors - darker for light backgrounds
                "success": "dark_green",
                "warning": "dark_goldenrod",
                "error": "dark_red",
                "info": "dark_blue",
                # Task status colors
                "status.pending": "dark_goldenrod",
                "status.starting": "dark_blue",
                "status.preparing": "dark_blue",
                "status.running": "dark_green",
                "status.paused": "dark_cyan",
                "status.preempting": "dark_goldenrod",
                "status.completed": "dark_green",
                "status.failed": "dark_red",
                "status.cancelled": "bright_black",
                # Table elements
                "table.header": "bold black",
                "table.border": "dark_blue",
                "table.row": "black",
                "table.row.dim": "bright_black",
                # Semantic elements
                "task.name": "black",
                "task.id": "dark_blue",
                "task.gpu": "black",
                "task.ip": "dark_blue",
                "task.time": "bright_black",
                "task.duration": "bright_black",
            },
        ),
        "high_contrast": FlowTheme(
            name="high_contrast",
            is_dark=True,
            colors={
                # Base colors - maximum contrast
                "default": "bright_white",
                "muted": "white",
                "border": "bright_white",
                "accent": "bright_cyan",
                "selected": "bright_cyan",
                "selected_arrow": "bright_cyan",
                "shortcut_key": "bright_cyan",
                # Status colors - bright variants
                "success": "bright_green",
                "warning": "bright_yellow",
                "error": "bright_red",
                "info": "bright_blue",
                # Task status colors
                "status.pending": "bright_yellow",
                "status.starting": "bright_blue",
                "status.preparing": "bright_blue",
                "status.running": "bright_green",
                "status.paused": "bright_cyan",
                "status.preempting": "bright_yellow",
                "status.completed": "bright_green",
                "status.failed": "bright_red",
                "status.cancelled": "white",
                # Table elements
                "table.header": "bold bright_white",
                "table.border": "bright_cyan",
                "table.row": "bright_white",
                "table.row.dim": "white",
                # Semantic elements
                "task.name": "bright_white",
                "task.id": "bright_cyan",
                "task.gpu": "bright_white",
                "task.ip": "bright_cyan",
                "task.time": "white",
                "task.duration": "white",
            },
        ),
        # A subdued modern dark theme inspired by IDE/agent consoles,
        # with muted borders and a bright cyan accent for links.
        "modern": FlowTheme(
            name="modern",
            is_dark=True,
            colors={
                # Base colors
                "default": "#D1D5DB",          # soft light gray text
                "muted": "#9CA3AF",            # muted gray
                "border": "#4B5563",           # slate/gray border
                "accent": "#5ECDF8",           # cyan accent for links
                "selected": "#334155",
                "selected_arrow": "#5ECDF8",
                "shortcut_key": "#5ECDF8",
                # Status colors
                "success": "#10B981",
                "warning": "#F59E0B",
                "error":   "#EF4444",
                "info":    "#60A5FA",
                # Task status colors
                "status.pending":    "#F59E0B",
                "status.starting":   "#60A5FA",
                "status.preparing":  "#60A5FA",
                "status.running":    "#10B981",
                "status.paused":     "#22D3EE",
                "status.preempting": "#F59E0B",
                "status.completed":  "#10B981",
                "status.failed":     "#EF4444",
                "status.cancelled":  "#6B7280",
                # Table elements
                "table.header": "bold #D1D5DB",
                "table.border": "#4B5563",
                "table.row": "#D1D5DB",
                "table.row.dim": "#9CA3AF",
                # Semantic elements
                "task.name": "#D1D5DB",
                "task.id": "#5ECDF8",
                "task.gpu": "#D1D5DB",
                "task.ip": "#5ECDF8",
                "task.time": "#9CA3AF",
                "task.duration": "#9CA3AF",
            },
        ),
    }

    def __init__(self):
        """Initialize theme manager."""
        self.current_theme_name = None
        self.current_theme = None
        self.custom_themes_dir = Path.home() / ".flow" / "themes"
        self._console_cache = {}

    def detect_terminal_theme(self) -> str:
        """Auto-detect terminal background color.

        Returns:
            "light" or "dark" based on terminal detection
        """
        # Check environment variables first
        if os.environ.get("FLOW_THEME"):
            return os.environ["FLOW_THEME"]

        # Check common terminal theme indicators
        if os.environ.get("COLORFGBG"):
            # Format: "foreground;background"
            colors = os.environ["COLORFGBG"].split(";")
            if len(colors) >= 2:
                try:
                    bg = int(colors[1])
                    # Common light backgrounds: 7 (white), 15 (bright white)
                    if bg in [7, 15]:
                        return "light"
                except ValueError:
                    pass

        # Check terminal-specific environment variables
        if os.environ.get("ITERM_PROFILE"):
            # iTerm2 specific
            profile = os.environ["ITERM_PROFILE"].lower()
            if any(light in profile for light in ["light", "solarized-light", "papercolor"]):
                return "light"

        # Check if running in light mode terminals
        if os.environ.get("TERMINAL_EMULATOR") == "JetBrains-JediTerm":
            # IntelliJ IDEA terminal often uses light themes
            return "light"

        # Default to dark theme
        return "dark"

    def load_theme(self, theme_name: Optional[str] = None) -> FlowTheme:
        """Load theme by name or auto-detect.

        Args:
            theme_name: Theme name to load, or None to auto-detect

        Returns:
            Loaded theme
        """
        if theme_name is None:
            theme_name = self.detect_terminal_theme()

        # Back-compat aliases
        alias_map = {
            "cursor": "modern",
            "cursor_dark": "modern",
        }
        theme_name = alias_map.get(str(theme_name), theme_name)

        # Check built-in themes first
        if theme_name in self.THEMES:
            self.current_theme_name = theme_name
            self.current_theme = self.THEMES[theme_name]
            return self.current_theme

        # Try to load custom theme
        custom_theme = self._load_custom_theme(theme_name)
        if custom_theme:
            self.current_theme_name = theme_name
            self.current_theme = custom_theme
            return custom_theme

        # Fallback to default
        self.current_theme_name = "dark"
        self.current_theme = self.THEMES["dark"]
        return self.current_theme

    def _load_custom_theme(self, theme_name: str) -> Optional[FlowTheme]:
        """Load custom theme from file.

        Args:
            theme_name: Name of custom theme

        Returns:
            Loaded theme or None if not found
        """
        if not self.custom_themes_dir.exists():
            return None

        # Try YAML first, then JSON
        for ext in [".yaml", ".yml", ".json"]:
            theme_file = self.custom_themes_dir / f"{theme_name}{ext}"
            if theme_file.exists():
                try:
                    with open(theme_file) as f:
                        if ext == ".json":
                            data = json.load(f)
                        else:
                            data = yaml.safe_load(f)

                    return FlowTheme(
                        name=data.get("name", theme_name),
                        colors=data.get("colors", {}),
                        is_dark=data.get("is_dark", True),
                    )
                except Exception:
                    # Invalid theme file
                    pass

        return None

    def create_console(
        self, force_color: Optional[bool] = None, no_color: Optional[bool] = None, **kwargs
    ) -> Console:
        """Create theme-aware Rich Console instance.

        Args:
            force_color: Force color output
            no_color: Disable color output
            **kwargs: Additional arguments for Console

        Returns:
            Configured Console instance
        """
        # Load theme if not already loaded
        if self.current_theme is None:
            self.load_theme()

        # Handle color forcing
        if no_color or os.environ.get("NO_COLOR"):
            kwargs["no_color"] = True
        elif force_color:
            kwargs["force_terminal"] = True

        # Apply theme
        kwargs["theme"] = self.current_theme.to_rich_theme()

        # Create console
        console = Console(**kwargs)

        return console

    def get_color(self, color_key: str) -> str:
        """Get color value for a given key.

        Args:
            color_key: Color key (e.g., "status.running")

        Returns:
            Color value or default
        """
        if self.current_theme is None:
            self.load_theme()

        return self.current_theme.colors.get(color_key, "default")

    def list_themes(self) -> list[str]:
        """List all available themes.

        Returns:
            List of theme names
        """
        themes = list(self.THEMES.keys())

        # Add custom themes
        if self.custom_themes_dir.exists():
            for theme_file in self.custom_themes_dir.glob("*.{yaml,yml,json}"):
                theme_name = theme_file.stem
                if theme_name not in themes:
                    themes.append(theme_name)

        return sorted(themes)


# Global theme manager instance
theme_manager = ThemeManager()
