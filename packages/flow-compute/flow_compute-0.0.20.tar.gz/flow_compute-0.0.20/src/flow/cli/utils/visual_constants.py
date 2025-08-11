"""Shared visual constants for CLI styling.

Defines colors, typography, and UI patterns used across the Flow CLI for
consistent presentation.
"""

from flow.cli.utils.theme_manager import theme_manager

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


def get_colors() -> dict[str, str]:
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


def get_typography() -> dict[str, str]:
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


def get_panel_styles() -> dict[str, dict]:
    """Get theme-aware panel styles for consistent UI.

    Returns:
        Dictionary of panel style configurations
    """
    from flow.cli.utils.theme_manager import theme_manager

    # Use theme manager colors for consistency
    return {
        "main": {
            "border_style": theme_manager.get_color("table.border"),
            "title_align": "center",
            "padding": (1, 2),
            "box": "ROUNDED",  # Standard box style
        },
        "secondary": {
            "border_style": theme_manager.get_color("muted"),
            "title_align": "left",
            "padding": (0, 1),
            "box": "ROUNDED",
        },
        "success": {
            "border_style": theme_manager.get_color("success"),
            "title_align": "center",
            "padding": (1, 2),
            "box": "ROUNDED",
        },
        "error": {
            "border_style": theme_manager.get_color("error"),
            "title_align": "center",
            "padding": (1, 2),
            "box": "ROUNDED",
        },
        "info": {
            "border_style": theme_manager.get_color("info"),
            "title_align": "center",
            "padding": (1, 2),
            "box": "ROUNDED",
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
    # Use darker ink for readable text; bright color for the dot when available
    # Default mapping aligns with semantic palette guidance
    if status == "configured":
        # Use themed accent for the configured state
        dot_color = theme_manager.get_color("accent")
        text_color = theme_manager.get_color("accent")
    elif status in ("error", "danger"):
        dot_color = theme_manager.get_color("error.icon") or colors["error"]
        text_color = theme_manager.get_color("error")
    elif status in ("missing", "invalid", "warning"):
        dot_color = theme_manager.get_color("warning.icon") or colors["warning"]
        text_color = theme_manager.get_color("warning")
    elif status in ("detected", "info"):
        dot_color = theme_manager.get_color("info.icon") or colors["info"]
        text_color = theme_manager.get_color("info")
    elif status == "optional":
        dot_color = colors["muted"]
        text_color = colors["muted"]
    else:
        dot_color = colors["accent"]
        text_color = colors["accent"]

    return f"[{dot_color}]{icon}[/{dot_color}] [{text_color}]{text}[/{text_color}]"


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

    # Always close with a reset tag to avoid mismatches (e.g. "[bold cyan]" -> "[/]")
    return f"{template}{text}[/]"
