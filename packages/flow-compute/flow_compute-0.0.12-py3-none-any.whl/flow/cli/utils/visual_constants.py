"""Shared visual constants for consistent CLI styling.

Provides a unified design system for colors, typography, and UI patterns
across the Flow CLI interface. Ensures coherent visual language between
wizard flows and operational commands.

Design principles:
- Minimal color palette for clarity
- Consistent status indicators
- Professional typography without visual clutter
- Accessible contrast ratios
"""

from typing import Dict
from .theme_manager import theme_manager

# Status indicators - consistent symbols across interfaces
STATUS_INDICATORS = {
    "configured": "●",
    "missing": "○",
    "invalid": "◐",
    "optional": "○",
    "active": "●",
    "inactive": "○",
    "selected": ">",
    "unselected": " ",
}

# Interactive element spacing
SPACING = {
    "section_gap": 1,
    "item_gap": 0,
    "panel_width": 60,
    "menu_width": 50,
}


def get_colors() -> Dict[str, str]:
    """Get theme-aware color mapping.

    Returns:
        Dictionary of color names to values
    """
    return {
        # Primary colors
        "primary": theme_manager.get_color("accent"),
        "accent": theme_manager.get_color("default"),
        "muted": theme_manager.get_color("muted"),
        # Status colors
        "success": theme_manager.get_color("success"),
        "warning": theme_manager.get_color("warning"),
        "error": theme_manager.get_color("error"),
        "info": theme_manager.get_color("info"),
        # UI element colors
        "border": theme_manager.get_color("border"),
        "highlight": "reverse",
    }


def get_typography() -> Dict[str, str]:
    """Get theme-aware typography styles.

    Returns:
        Dictionary of style templates
    """
    colors = get_colors()
    return {
        "title": f"[bold {colors['primary']}]",
        "subtitle": f"[bold {colors['accent']}]",
        "body": f"[{colors['accent']}]",
        "muted": f"[{colors['muted']}]",
        "success": f"[{colors['success']}]",
        "warning": f"[{colors['warning']}]",
        "error": f"[{colors['error']}]",
    }


def get_panel_styles() -> Dict[str, Dict]:
    """Get theme-aware panel styles.

    Returns:
        Dictionary of panel style configurations
    """
    colors = get_colors()
    return {
        "main": {
            "border_style": colors["primary"],
            "title_align": "center",
            "padding": (1, 2),
        },
        "secondary": {
            "border_style": colors["border"],
            "title_align": "left",
            "padding": (0, 1),
        },
        "success": {
            "border_style": colors["success"],
            "title_align": "center",
            "padding": (1, 2),
        },
    }


def get_status_display(status: str, text: str) -> str:
    """Get consistently formatted status display.

    Args:
        status: Status type (configured, missing, etc.)
        text: Status text to display

    Returns:
        Formatted status string with icon and color
    """
    icon = STATUS_INDICATORS.get(status, "○")
    colors = get_colors()
    color = {
        "configured": colors["success"],
        "missing": colors["error"],
        "invalid": colors["warning"],
        "optional": colors["muted"],
    }.get(status, colors["accent"])

    return f"[{color}]{icon}[/{color}] [{color}]{text}[/{color}]"


def format_text(style: str, text: str) -> str:
    """Apply consistent text styling.

    Args:
        style: Style key from TYPOGRAPHY
        text: Text to format

    Returns:
        Formatted text string
    """
    typography = get_typography()
    colors = get_colors()
    template = typography.get(style, f"[{colors['accent']}]")

    # Handle closing tags
    if style in typography:
        # Extract the color from the template
        import re

        match = re.search(r"\[([^\]]+)\]", template)
        if match:
            color_spec = match.group(1)
            # Get the base color (without modifiers like 'bold')
            base_color = color_spec.split()[-1]
            return template + text + f"[/{base_color}]"

    return template + text + f"[/{colors['accent']}]"
