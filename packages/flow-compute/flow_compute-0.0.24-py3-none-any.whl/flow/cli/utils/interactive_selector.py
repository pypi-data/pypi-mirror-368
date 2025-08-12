"""Interactive resource selector for Flow CLI.

Provides an interactive picker for resources (tasks, volumes, etc) with TTY
fallbacks and sensible defaults.
"""

from __future__ import annotations

import os
import sys
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Generic, TypeVar

from prompt_toolkit import Application
from prompt_toolkit.filters import Condition
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import FormattedTextControl, HSplit, Layout, VSplit, Window
from rich.markup import escape
from flow.cli.utils.visual_constants import SPACING, DENSITY

from flow.api.models import Task, Volume
from flow.cli.utils.gpu_formatter import GPUFormatter
from flow.cli.utils.task_formatter import TaskFormatter
from flow.cli.utils.terminal_adapter import TerminalAdapter
from flow.cli.utils.theme_manager import theme_manager

T = TypeVar("T")


def _map_rich_to_prompt_toolkit_color(rich_color: str) -> str:
    """Map Rich color names to prompt_toolkit color names.

    Rich and prompt_toolkit have different interpretations of standard color names.
    This function ensures consistent color rendering between the two libraries.

    Args:
        rich_color: Color name from Rich/theme manager

    Returns:
        Equivalent color name for prompt_toolkit
    """
    # Map standard ANSI colors to their prompt_toolkit equivalents
    color_map = {
        "green": "ansigreen",  # Rich's green -> PT's ansigreen for softer appearance
        "red": "ansired",
        "yellow": "ansiyellow",
        "blue": "ansiblue",
        "cyan": "ansicyan",
        "magenta": "ansimagenta",
        "white": "ansiwhite",
        "black": "ansiblack",
        # Bright variants
        "bright_green": "ansibrightgreen",
        "bright_red": "ansibrightred",
        "bright_yellow": "ansibrightyellow",
        "bright_blue": "ansibrightblue",
        "bright_cyan": "ansibrightcyan",
        "bright_magenta": "ansibrightmagenta",
        # Some PT versions don't accept ansibrightwhite/ansibrightblack; map to base
        "bright_white": "ansiwhite",
        "bright_black": "ansiblack",
        # Dark variants
        "dark_green": "darkgreen",
        "dark_red": "darkred",
        "dark_blue": "darkblue",
        # Other colors remain as-is
    }

    # Normalize a couple of problematic variants first
    if rich_color in {"ansibrightwhite", "brightwhite"}:
        return "ansiwhite"
    if rich_color in {"ansibrightblack", "brightblack"}:
        return "ansiblack"

    mapped = color_map.get(rich_color, rich_color)
    # Guard against invalid style names like "ansibrightwhite" when themes
    # pass through composite values (e.g., "bold white", "underline #RRGGBB").
    try:
        # If the value contains spaces or hash colors, leave it as-is and rely
        # on prompt_toolkit to ignore unsupported attributes gracefully in our
        # minimal style usage. For pure color tokens, ensure they start with
        # "ansi" or are one of the known PT names.
        if " " in mapped or mapped.startswith("#"):
            return mapped
        # Normalize a few common aliases
        if mapped == "bright_white" or mapped == "ansibrightwhite":
            return "ansiwhite"
        if mapped == "bright_black" or mapped == "ansibrightblack":
            return "ansiblack"
    except Exception:
        pass
    return mapped


def _style(text: str, fg: str | None = None, bg: str | None = None) -> str:
    """Wrap text with prompt_toolkit HTML style tag.

    Args:
        text: Inner text (can include other HTML like <b>, <i>)
        fg: Foreground color (prompt_toolkit color name)
        bg: Background color (prompt_toolkit color name)

    Returns:
        Styled HTML string using <style fg='..' bg='..'>text</style>
    """
    parts: list[str] = []
    if fg:
        parts.append(f"fg='{fg}'")
    if bg:
        parts.append(f"bg='{bg}'")
    if parts:
        return f"<style {' '.join(parts)}>{text}</style>"
    return text


def _highlight_matches(text: str, query: str, color_name: str) -> str:
    """Return HTML with case-insensitive highlight of query in text.

    The returned string keeps the same visible width; tags are inserted around
    matched substrings only.
    """
    if not text or not query:
        return text
    try:
        import re as _re

        pattern = _re.compile(_re.escape(query), _re.IGNORECASE)

        def _repl(m):
            return _style(m.group(0), fg=_map_rich_to_prompt_toolkit_color(color_name))

        return pattern.sub(_repl, text)
    except Exception:
        return text


def _parse_tokens(query: str) -> tuple[dict[str, str], str]:
    """Parse simple key:value tokens from a query string.

    Returns (tokens, free_text). Unknown tokens are accepted but only used if
    caller recognizes keys.
    """
    try:
        parts = [p for p in (query or "").split() if p]
        tokens: dict[str, str] = {}
        free: list[str] = []
        for p in parts:
            if ":" in p and not p.startswith(":"):
                k, v = p.split(":", 1)
                if k and v:
                    tokens[k.lower()] = v
                else:
                    free.append(p)
            else:
                free.append(p)
        return tokens, " ".join(free)
    except Exception:
        return {}, query or ""


def _rank_items_with_fuzzy(
    query_free: str,
    items: list[SelectionItem],
    search_keys: list[str],
    mode: str,
    top_k: int,
) -> list[int]:
    """Return indices of items ranked by fuzzy score with guards.

    - Uses substring prefilter for very large lists or empty queries.
    - Attempts rapidfuzz if requested; falls back to difflib; ends with substring.
    """
    import heapq as _heapq

    q = (query_free or "").strip().lower()
    if not q:
        # No free text -> keep order
        return list(range(len(items)))

    n = len(items)
    # Simple substring prefilter for large lists
    candidate_indices: list[int]
    if n > 1000:
        candidate_indices = [i for i, key in enumerate(search_keys) if q in key]
        if not candidate_indices:
            return []
    else:
        candidate_indices = list(range(n))

    # Try rapidfuzz if requested
    if mode == "rapidfuzz":
        try:
            from rapidfuzz import fuzz

            scored = []
            for i in candidate_indices:
                key = search_keys[i]
                title = items[i].title or ""
                s = max(
                    fuzz.WRatio(q, title),
                    fuzz.WRatio(q, key),
                )
                if s > 0:
                    scored.append((s, i))
            # Top-K
            top = _heapq.nlargest(top_k, scored, key=lambda t: (t[0], -t[1]))
            return [i for _, i in sorted(top, key=lambda t: (-t[0], t[1]))]
        except Exception:
            pass

    # Fallback to difflib
    try:
        import difflib as _difflib

        scored = []
        for i in candidate_indices:
            key = search_keys[i]
            title = (items[i].title or "").lower()
            score = 0
            if q in title:
                score += 50
            if title.startswith(q):
                score += 30
            if q in key:
                score += 20
            score += int(_difflib.SequenceMatcher(None, q, title).ratio() * 40)
            score += int(_difflib.SequenceMatcher(None, q, key).ratio() * 10)
            if score > 0:
                scored.append((score, i))
        top = _heapq.nlargest(top_k, scored, key=lambda t: (t[0], -t[1]))
        return [i for _, i in sorted(top, key=lambda t: (-t[0], t[1]))]
    except Exception:
        pass

    # Final fallback: substring across all
    return [i for i, key in enumerate(search_keys) if q in key]


def _format_task_duration(task: Task) -> str:
    """Format task duration or time since creation."""
    try:
        # Use started_at if available, otherwise created_at
        if task.started_at:
            start = task.started_at
            end = task.completed_at or datetime.now(timezone.utc)
            prefix = ""
        else:
            # Task hasn't started yet, show time since creation
            start = task.created_at
            end = datetime.now(timezone.utc)
            prefix = "created "

        # Handle timezone-aware datetimes
        if not isinstance(start, datetime):
            start = datetime.fromisoformat(str(start).replace("Z", "+00:00"))
        if not isinstance(end, datetime):
            end = datetime.fromisoformat(str(end).replace("Z", "+00:00"))

        # Ensure timezone awareness
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)

        # Calculate duration
        duration = end - start

        # Format
        if duration.days > 0:
            return f"{prefix}{duration.days}d {duration.seconds // 3600}h ago"

        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60

        if hours > 0:
            return f"{prefix}{hours}h {minutes}m ago"
        elif minutes > 0:
            return f"{prefix}{minutes}m ago"
        else:
            return f"{prefix}just now"
    except Exception:
        return "unknown"


@dataclass
class SelectionItem(Generic[T]):
    """Wrapper for selectable items with display information.

    Attributes:
        value: Original item value.
        id: Stable identifier used for selection tracking.
        title: Primary label.
        subtitle: Secondary information shown inline.
        status: Status string or enum name for rendering.
        extra: Optional metadata for renderer hints.
    """

    value: T
    id: str
    title: str
    subtitle: str | None
    status: str | object | None
    extra: dict | None = None


class InteractiveSelector(Generic[T]):
    """Interactive selector for CLI resources.

    Provides a rich, keyboard-navigable interface for selecting
    resources like tasks or volumes. Falls back gracefully to
    simple selection in non-interactive environments.
    """

    # Sentinel value for back navigation
    BACK_SENTINEL = object()

    def __init__(
        self,
        items: list[T],
        item_to_selection: Callable[[T], SelectionItem[T]],
        title: str = "Select an item",
        allow_multiple: bool = False,
        show_preview: bool = True,
        allow_back: bool = False,
        breadcrumbs: list[str] | None = None,
        extra_header_html: str | None = None,
        preferred_viewport_size: int | None = None,
    ):
        self.items = items
        self.item_to_selection = item_to_selection
        self.title = title
        self.allow_multiple = allow_multiple
        self.show_preview = show_preview
        self.allow_back = allow_back
        self.breadcrumbs = breadcrumbs or []
        self.extra_header_html = extra_header_html
        self.console = theme_manager.create_console()
        self.terminal = TerminalAdapter()
        self.show_help = False  # Toggle for extended help
        self.preferred_viewport_size = preferred_viewport_size
        # Base row spacing from central constants; can be overridden/adapted below
        try:
            self.item_gap: int = int(SPACING.get("item_gap", 0))  # blank lines between items
        except Exception:
            self.item_gap = 0
        # Environment-controlled toggles (undocumented; support use only)
        try:
            if os.environ.get("FLOW_SELECTOR_PREVIEW", "").lower() in {"0", "off", "false"}:
                self.show_preview = False
        except Exception:
            pass
        # Fuzzy mode: off | basic | rapidfuzz
        self._fuzzy_mode = os.environ.get("FLOW_FUZZY", "basic").lower() or "basic"
        # Virtualization caps
        try:
            self._fuzzy_disable_threshold = int(
                os.environ.get("FLOW_SELECTOR_FUZZY_THRESHOLD", "2000")
            )
        except Exception:
            self._fuzzy_disable_threshold = 2000
        try:
            self._top_k_results = max(50, int(os.environ.get("FLOW_SELECTOR_TOPK", "400")))
        except Exception:
            self._top_k_results = 400
        # Active highlight token (free-text portion of query)
        self._active_highlight_query: str = ""

        # Convert items to selection items
        self.selection_items = [item_to_selection(item) for item in items]
        # Build lowercase search keys once for fast filtering
        self._search_keys = [
            (si.id + si.title + (si.subtitle or "")).lower() for si in self.selection_items
        ]

        # State
        self.selected_index = 0
        self.selected_ids: set[str] = set()  # Track selected items by stable id
        self.filter_text = ""
        self.filtered_items = self.selection_items  # No need to copy initially

        # Viewport for scrolling - derive size from terminal height for better UX
        try:
            import shutil

            self.terminal_lines = shutil.get_terminal_size().lines or 24
        except Exception:
            self.terminal_lines = 24

        # Density override via environment variable (compact|comfortable)
        try:
            density_env = (os.environ.get("FLOW_SELECTOR_DENSITY", "") or "").strip().lower()
            # Inherit from global density when not explicitly overridden
            if not density_env:
                density_env = DENSITY.mode
            if density_env == "compact":
                self.item_gap = 0
            elif density_env == "comfortable":
                self.item_gap = max(self.item_gap, 1)
        except Exception:
            pass

        # Adaptive spacing: make short menus feel more designed on tall terminals
        try:
            if not density_env:
                if len(self.items) <= 6 and self.terminal_lines >= 28:
                    self.item_gap = max(self.item_gap, 1)
        except Exception:
            pass

        # Deterministic viewport in "lines": clamp between 6 and 8, reserve 10 lines for chrome
        # Then convert to a number of items accounting for per-item height (1 + item_gap)
        default_viewport_lines = max(6, min(8, self.terminal_lines - 10))
        effective_item_height = max(1, 1 + int(self.item_gap))
        default_viewport_items = max(3, default_viewport_lines // effective_item_height)

        # If caller provided a preferred viewport size, use it as a clamp only
        if self.preferred_viewport_size is not None:
            self.viewport_size = max(
                3, min(default_viewport_items, int(self.preferred_viewport_size))
            )
        else:
            self.viewport_size = default_viewport_items

        self.viewport_start = 0
        # Prefer using /dev/tty for interactive I/O when stdio is not a TTY
        self._use_dev_tty: bool = False

    # --- Header utilities -------------------------------------------------
    def _visible_html_length(self, html_text: str) -> int:
        """Return the printable length of a minimal HTML string.

        We use prompt_toolkit's very small HTML subset (e.g., <b>, <i>, style tags).
        Strip tags to measure how wide the text will render so we can wrap cleanly
        without splitting tokens mid-word.
        """
        try:
            import re as _re

            return len(_re.sub(r"<[^>]+>", "", html_text))
        except Exception:
            return len(html_text)

    def _reflow_header_text(self, text: str, max_width: int) -> str:
        """Reflow a chip-like header string into neat wrapped lines.

        The input is expected to be a sequence of tokens separated by " \u2022 "
        (middle dot). We wrap only at those boundaries so chips never break
        awkwardly in the middle, which keeps the layout elegant on any terminal
        width.
        """
        if not text:
            return ""

        # Split on the bullet separator used by _build_selector_header
        tokens = [t.strip() for t in text.split("  •  ") if t.strip()]
        # If no recognizable separator, return as-is (let normal wrapping handle it)
        if len(tokens) <= 1:
            return text

        lines: list[str] = []
        def _truncate_chip(token: str, width: int) -> str:
            """Truncate the value part of a chip while preserving the label and HTML.

            Expected token format: "<i>Label</i>: value"; falls back to middle truncation
            of the whole token when pattern doesn't match.
            """
            try:
                import re as _re

                m = _re.match(r"^(<i>.*?</i>):\s*(.*)$", token)
                if not m:
                    # Generic fallback
                    plain = _re.sub(r"<[^>]+>", "", token)
                    shortened = self.terminal.intelligent_truncate(plain, width, "middle")
                    return shortened
                label_html = m.group(1)
                value_html = m.group(2)
                label_len = self._visible_html_length(label_html) + 2  # account for ': '
                if label_len >= width - 4:  # ensure a minimal tail for value
                    return label_html  # show only the label in extreme constraint
                value_budget = max(4, width - label_len)
                # Strip tags before truncation to avoid breaking HTML; value rarely contains tags
                value_plain = _re.sub(r"<[^>]+>", "", value_html)
                value_short = self.terminal.intelligent_truncate(value_plain, value_budget, "middle")
                return f"{label_html}: {value_short}"
            except Exception:
                return token

        # Pre-truncate any chip that is itself wider than the available width
        norm_tokens: list[str] = []
        for tok in tokens:
            if self._visible_html_length(tok) > max_width:
                norm_tokens.append(_truncate_chip(tok, max_width))
            else:
                norm_tokens.append(tok)

        current = norm_tokens[0]
        cur_len = self._visible_html_length(current)
        sep = "  •  "

        for tok in norm_tokens[1:]:
            tok_len = self._visible_html_length(tok)
            # Account for the separator between chips
            projected = cur_len + len(sep) + tok_len
            if projected <= max_width:
                current += sep + tok
                cur_len = projected
            else:
                lines.append(current)
                current = tok
                cur_len = tok_len

        lines.append(current)
        return "\n".join(lines)

    def select(self) -> T | None | list[T]:
        """Show interactive selector and return selected item(s)."""
        # Check if we're in an interactive terminal
        force_interactive = os.environ.get("FLOW_FORCE_INTERACTIVE", "").lower() == "true"
        stdout_is_tty = sys.stdout.isatty()
        stdin_is_tty = sys.stdin.isatty()

        # Skip interactive mode if explicitly disabled
        if os.environ.get("FLOW_NONINTERACTIVE"):
            if os.environ.get("FLOW_DEBUG"):
                self.console.print("[dim]FLOW_NONINTERACTIVE is set[/dim]")
            return self._fallback_selection()

        # If stdout is not a TTY, avoid running prompt_toolkit by default to prevent
        # glitchy redraw output in piped contexts. Users can force interactivity by
        # setting FLOW_FORCE_INTERACTIVE=true explicitly.
        if not stdout_is_tty and not force_interactive:
            if os.environ.get("FLOW_DEBUG"):
                self.console.print("[dim]stdout is not a TTY; using fallback selection[/dim]")
            return self._fallback_selection()

        # Check terminal compatibility for prompt_toolkit
        # Some terminals (like certain CI environments) can't support it
        term = os.environ.get("TERM", "")
        # If not attached to a real TTY, only attempt /dev/tty when explicitly forced
        if not (stdin_is_tty and stdout_is_tty):
            if force_interactive:
                dev_tty_available = False
                try:
                    with open("/dev/tty"):
                        dev_tty_available = True
                except Exception:
                    dev_tty_available = False
                if dev_tty_available:
                    self._use_dev_tty = True
                    if os.environ.get("FLOW_DEBUG"):
                        self.console.print("[dim]Using /dev/tty for interactive I/O (forced)[/dim]")
                else:
                    if os.environ.get("FLOW_DEBUG"):
                        self.console.print(
                            "[dim]/dev/tty unavailable; using fallback despite force request[/dim]"
                        )
                    return self._fallback_selection()
            else:
                # Not forced; use fallback rather than trying /dev/tty implicitly
                if os.environ.get("FLOW_DEBUG"):
                    self.console.print(
                        "[dim]stdin/stdout not both TTY; using fallback selection[/dim]"
                    )
                return self._fallback_selection()
        if term == "dumb" and not force_interactive and not self._use_dev_tty:
            if os.environ.get("FLOW_DEBUG"):
                self.console.print("[dim]Dumb terminal detected, using fallback[/dim]")
            return self._fallback_selection()

        # Check if we have items to select
        if not self.items:
            self.console.print("[yellow]No items available to select[/yellow]")
            return None if not self.allow_multiple else []

        # Single item optimization
        if len(self.items) == 1 and not self.allow_multiple:
            item = self.selection_items[0]
            success_color = theme_manager.get_color("success")
            self.console.print(
                f"[{success_color}]Auto-selecting:[/{success_color}] {item.title} ({item.id})"
            )
            return item.value

        # Run interactive selector
        try:
            if os.environ.get("FLOW_DEBUG"):
                self.console.print("[dim]Attempting to run interactive selector...[/dim]")

            # Clear any pending terminal input before starting interactive mode
            # This prevents ANSI escape sequences from appearing
            self._clear_terminal_input()

            return self._run_interactive()
        except ImportError as e:
            # Missing dependency
            self.console.print(
                "[yellow]Interactive mode unavailable. Falling back to numbered list.[/yellow]"
            )
            if os.environ.get("FLOW_DEBUG"):
                self.console.print(f"[red]Missing dependency: {escape(str(e))}[/red]")
            return self._fallback_selection()
        except Exception as e:
            # Fallback on any error - but always show the error in debug mode
            if os.environ.get("FLOW_DEBUG"):
                self.console.print(
                    f"[red]Interactive mode failed: {escape(type(e).__name__)}: {escape(str(e))}[/red]"
                )
                import traceback

                traceback.print_exc()
            else:
                # In non-debug mode, check if it's a common error
                error_msg = str(e).lower()
                if "invalid argument" in error_msg or "errno 22" in error_msg:
                    # This is likely a terminal capability issue
                    self.console.print(
                        "[yellow]Note: Interactive mode not supported in this terminal. Using numbered selection.[/yellow]"
                    )
                else:
                    # Unknown error, show generic message but log the error type
                    self.console.print(
                        "[yellow]Interactive mode unavailable. Falling back to numbered list.[/yellow]"
                    )
                    if os.environ.get("FLOW_LOG_ERRORS"):
                        self.console.print(f"[dim]Error was: {type(e).__name__}[/dim]")
            return self._fallback_selection()

    def _clear_terminal_input(self):
        """Clear any pending terminal input to prevent ANSI escape sequences from appearing.

        This handles cursor position reports (CPR) like ^[[27;1R that terminals send
        in response to queries from prompt_toolkit or other terminal libraries.
        """
        try:
            import select
            import termios
            import tty

            if not sys.stdin.isatty():
                return

            fd = sys.stdin.fileno()

            # Save current terminal settings
            old_settings = termios.tcgetattr(fd)

            try:
                # Set terminal to non-canonical mode to read pending input
                tty.setcbreak(fd)

                # Read and discard any pending input (with timeout)
                while True:
                    # Check if there's input available (non-blocking)
                    ready, _, _ = select.select([fd], [], [], 0.01)
                    if not ready:
                        break
                    # Read and discard one character
                    os.read(fd, 1024)  # Read up to 1024 bytes at once

            finally:
                # Restore terminal settings
                termios.tcsetattr(fd, termios.TCSANOW, old_settings)

        except (ImportError, OSError):
            # termios not available (Windows) or other error - safe to ignore
            pass
        except Exception:
            # Any other error - safe to ignore as this is a best-effort cleanup
            pass

    def _run_interactive(self) -> T | None | list[T]:
        """Run the interactive selection interface."""
        # Check terminal compatibility first
        if os.environ.get("FLOW_DEBUG"):
            self.console.print("[dim]Checking terminal compatibility...[/dim]")
            self.console.print(f"[dim]TERM={os.environ.get('TERM', 'not set')}[/dim]")
            self.console.print(
                f"[dim]stdin isatty={sys.stdin.isatty()}, stdout isatty={sys.stdout.isatty()}[/dim]"
            )

            # Check if we can access /dev/tty
            try:
                with open("/dev/tty"):
                    self.console.print("[dim]/dev/tty is accessible[/dim]")
            except Exception as e:
                self.console.print(f"[red]/dev/tty not accessible: {escape(str(e))}[/red]")

        # Build key bindings - keep it simple
        kb = KeyBindings()

        # Navigation
        @kb.add("up")
        @kb.add("k")
        def move_up(event):
            if self.selected_index > 0:
                self.selected_index -= 1
                self._update_viewport()

        @kb.add("down")
        @kb.add("j")
        def move_down(event):
            if self.selected_index < len(self.filtered_items) - 1:
                self.selected_index += 1
                self._update_viewport()

        # Page navigation
        @kb.add("pageup")
        def page_up(event):
            self.selected_index = max(0, self.selected_index - self.viewport_size)
            self._update_viewport()

        @kb.add("pagedown")
        def page_down(event):
            self.selected_index = min(
                len(self.filtered_items) - 1, self.selected_index + self.viewport_size
            )
            self._update_viewport()

        # Additional navigation
        @kb.add("home")
        @kb.add("g")
        def go_top(event):
            self.selected_index = 0
            self._update_viewport()

        @kb.add("end")
        @kb.add("G")
        def go_bottom(event):
            if self.filtered_items:
                self.selected_index = len(self.filtered_items) - 1
                self._update_viewport()

        @kb.add("c-n")
        def ctrl_n(event):
            if self.selected_index < len(self.filtered_items) - 1:
                self.selected_index += 1
                self._update_viewport()

        @kb.add("c-p")
        def ctrl_p(event):
            if self.selected_index > 0:
                self.selected_index -= 1
                self._update_viewport()

        # Selection
        @kb.add("enter")
        def confirm(event):
            if self.filtered_items:
                if self.allow_multiple:
                    if self.selected_ids:
                        # Preserve original order from initial list
                        ordered = [
                            si.value for si in self.selection_items if si.id in self.selected_ids
                        ]
                        event.app.exit(result=ordered)
                    else:
                        # If nothing toggled, select the highlighted one
                        event.app.exit(result=[self.filtered_items[self.selected_index].value])
                else:
                    event.app.exit(result=self.filtered_items[self.selected_index].value)

        @kb.add("space")
        def toggle_selection(event):
            if self.allow_multiple and self.filtered_items:
                current = self.filtered_items[self.selected_index]
                if current.id in self.selected_ids:
                    self.selected_ids.remove(current.id)
                else:
                    self.selected_ids.add(current.id)

        # Multi-select helpers: select all / clear all (when not filtering to avoid conflicts)
        @kb.add("a")
        def select_all(event):
            # If user is typing a filter, treat 'a' as input
            if self.filter_text:
                self.filter_text += "a"
                self._update_filter()
                return
            if self.allow_multiple and self.filtered_items:
                for si in self.filtered_items:
                    self.selected_ids.add(si.id)

        @kb.add("A")
        def clear_all(event):
            # If user is typing a filter, treat 'A' as input
            if self.filter_text:
                self.filter_text += "A"
                self._update_filter()
                return
            if self.allow_multiple and self.selected_ids:
                self.selected_ids.clear()

        # Back navigation
        if self.allow_back:

            @kb.add("b")
            def go_back_b(event):
                event.app.exit(result=self.BACK_SENTINEL)

            @kb.add("backspace", filter=Condition(lambda: self.allow_back and not self.filter_text))
            def go_back_backspace(event):
                event.app.exit(result=self.BACK_SENTINEL)

        # Help toggle
        @kb.add("?")
        def toggle_help(event):
            self.show_help = not self.show_help

        # Preview toggle
        @kb.add("p")
        def toggle_preview(event):
            # If user is typing a filter, treat 'p' as input
            if self.filter_text:
                self.filter_text += "p"
                self._update_filter()
                return
            self.show_preview = not self.show_preview

        # Exit
        @kb.add("escape")
        @kb.add("c-c")  # Ctrl+C
        def cancel(event):
            # For Ctrl+C, we want to exit the entire program, not just this selector
            if event.key_sequence[0].key == "c-c":
                # Set a special flag to indicate we should exit
                event.app.exit(result=("__KEYBOARD_INTERRUPT__",))
            else:
                # For Escape, just cancel this selection (or go back if allowed)
                if self.allow_back:
                    event.app.exit(result=self.BACK_SENTINEL)
                else:
                    event.app.exit(result=None)

        # Number key shortcuts (gated when not filtering)
        for i in range(1, 10):

            @kb.add(str(i))
            def handle_number(event, index=i - 1):
                # If a filter is active, treat digits as filter text
                key_char = event.key_sequence[0].key
                if self.filter_text:
                    self.filter_text += key_char
                    self._update_filter()
                    return
                if index < len(self.filtered_items):
                    self.selected_index = index
                    self._update_viewport()  # Ensure item is visible
                    if self.allow_multiple:
                        # Toggle the selection by stable id
                        current = self.filtered_items[index]
                        if current.id in self.selected_ids:
                            self.selected_ids.remove(current.id)
                        else:
                            self.selected_ids.add(current.id)
                    else:
                        # Single selection - just exit with this item
                        event.app.exit(result=self.filtered_items[index].value)

        # Filter management
        @kb.add("backspace", filter=Condition(lambda: bool(self.filter_text)))
        def handle_backspace(event):
            self.filter_text = self.filter_text[:-1]
            self._update_filter()

        @kb.add("c-u")  # Clear filter like in vim
        def clear_filter(event):
            self.filter_text = ""
            self._update_filter()

        # Single handler for all typing with set lookup (O(1) instead of O(n))
        import string

        allowed_chars = set(string.ascii_letters + string.digits + " -._")

        @kb.add("<any>")
        def handle_typing(event):
            key = event.key_sequence[0].key
            # Fast set lookup instead of string iteration
            # Avoid double-handling digits 1-9 which have dedicated handlers
            if key.isdigit() and key != "0":
                return
            if len(key) == 1 and key in allowed_chars:
                self.filter_text += key
                self._update_filter()

        # Create layout with sticky header and scrolling body
        def get_header_text():
            default_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("default"))
            muted_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
            border_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))

            # No extra top margin; avoid layout jitter and stray glyphs near header
            html = ""

            if self.extra_header_html:
                # Wrap header content at chip separators so it breaks cleanly
                # instead of mid-token. Use terminal width for an accurate wrap.
                term_w_for_header = self.terminal.get_terminal_width()
                # Leave a small margin so the rule below aligns nicely
                wrap_width = max(20, min(term_w_for_header - 6, 100))
                wrapped = self._reflow_header_text(self.extra_header_html.rstrip(), wrap_width)
                html += wrapped + "\n\n"

            if self.breadcrumbs:
                breadcrumb_text = " › ".join(self.breadcrumbs)
                html += _style(breadcrumb_text, fg=muted_color) + "\n\n"

            html += _style(f"<b>{self.title}</b>", fg=default_color) + "\n"
            if self.allow_back:
                html += _style("ESC back • Ctrl+C exit", fg=muted_color) + "\n"
            else:
                html += _style("ESC cancel • Ctrl+C exit", fg=muted_color) + "\n"

            terminal_width = self.terminal.get_terminal_width()

            # Intelligent preview width adjustment (avoid confusing cramped layouts)
            def _should_adjust_for_preview() -> bool:
                if not self.show_preview:
                    return False
                if terminal_width < 100:
                    return False
                try:
                    itm = self.filtered_items[self.selected_index] if self.filtered_items else None
                    if not itm:
                        return False
                    is_simple = (not itm.status) and (
                        not itm.subtitle or "Created:" not in itm.subtitle
                    )
                    return not is_simple
                except Exception:
                    return False

            if _should_adjust_for_preview():
                terminal_width = max(20, terminal_width - 42)  # account for preview panel
            separator_width = max(10, min(terminal_width - 4, 80))
            html += _style("" + ("─" * separator_width), fg=border_color) + "\n"

            return HTML(html)

        def get_body_text():
            border_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
            terminal_width = self.terminal.get_terminal_width()

            # Intelligent preview width adjustment
            def _should_adjust_for_preview_body() -> bool:
                if not self.show_preview:
                    return False
                if terminal_width < 100:
                    return False
                try:
                    itm = self.filtered_items[self.selected_index] if self.filtered_items else None
                    if not itm:
                        return False
                    is_simple = (not itm.status) and (
                        not itm.subtitle or "Created:" not in itm.subtitle
                    )
                    return not is_simple
                except Exception:
                    return False

            if _should_adjust_for_preview_body():
                terminal_width = max(20, terminal_width - 42)  # account for preview panel
            separator_width = max(10, min(terminal_width - 4, 80))

            def _visible_len(s: str) -> int:
                try:
                    import re as _re

                    return len(_re.sub(r"<[^>]+>", "", s))
                except Exception:
                    return len(s)

            html = ""

            # Filter indicator with better spacing (subtle, single blank line)
            muted_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
            if self.filter_text:
                html += _style(f"<i>Filter: {self.filter_text}</i>", fg=muted_color) + "\n"
            else:
                # Subtle inline hint when no filter is active
                html += _style("Type to filter, '?' for help", fg=muted_color) + "\n"
            # Add a small breathing space above the list for readability
            try:
                if self.terminal_lines >= 24:
                    html += "\n"
            except Exception:
                pass

            # Calculate viewport
            viewport_end = min(self.viewport_start + self.viewport_size, len(self.filtered_items))

            # Scroll indicators
            if self.viewport_start > 0:
                muted_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
                html += _style(f"  ↑ {self.viewport_start} more above...", fg=muted_color) + "\n"

            # Get column widths once
            column_widths = self._calculate_column_widths()

            # Centered column header
            try:
                left_pad = self._compute_left_padding(column_widths)  # type: ignore[attr-defined]
            except Exception:
                left_pad = 2
            try:
                header_block = self._format_columns_header(column_widths)  # type: ignore[attr-defined]
                for hline in header_block.split("\n"):
                    html += (" " * left_pad) + hline + "\n"
            except Exception:
                pass

            # Ensure selected item is visible. Prefer showing context ABOVE the
            # selection so the last item doesn't appear alone with no preceding items.
            try:
                if self.selected_index >= viewport_end:
                    # Anchor selection near the bottom of the viewport so preceding
                    # options remain visible when the default is the last item.
                    self.viewport_start = max(0, self.selected_index - self.viewport_size + 1)
                    viewport_end = min(
                        self.viewport_start + self.viewport_size, len(self.filtered_items)
                    )
                if self.selected_index < self.viewport_start:
                    self.viewport_start = self.selected_index
                    viewport_end = min(
                        self.viewport_start + self.viewport_size, len(self.filtered_items)
                    )
            except Exception:
                pass

            # Items in viewport
            for i in range(self.viewport_start, viewport_end):
                item = self.filtered_items[i]
                is_selected = i == self.selected_index
                line = self._format_item_line(item, is_selected, column_widths, i)
                html += (" " * left_pad) + line + "\n"
                # Optional breathing room between rows
                if self.item_gap > 0 and i < (viewport_end - 1):
                    try:
                        html += "\n" * int(self.item_gap)
                    except Exception:
                        pass

            # Bottom scroll indicator
            if viewport_end < len(self.filtered_items):
                muted_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
                html += (
                    _style(
                        f"  ↓ {len(self.filtered_items) - viewport_end} more below...",
                        fg=muted_color,
                    )
                    + "\n"
                )

            # Adaptive footer navigation (compact to avoid wrapping)
            shortcut_color = _map_rich_to_prompt_toolkit_color(
                theme_manager.get_color("shortcut_key")
            )
            muted_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
            html += "\n"
            html += _style("" + ("─" * separator_width), fg=muted_color) + "\n"
            # Add a subtle gap between header rule and options
            html += "\n"

            if self.show_help:
                # Extended help mode - one action per line, aligned
                html += _style("<b>Navigation Help</b>", fg=shortcut_color) + "\n"
                html += _style("  ↑/k", fg=shortcut_color) + "    Move up\n"
                html += _style("  ↓/j", fg=shortcut_color) + "    Move down\n"
                html += _style("  ↩", fg=shortcut_color) + "      Select item\n"
                if self.allow_multiple:
                    html += _style("  Space", fg=shortcut_color) + "  Toggle selection\n"
                html += _style("  1-9", fg=shortcut_color) + "    Jump to item\n"
                if self.allow_back:
                    html += _style("  b", fg=shortcut_color) + "      Go back\n"
                html += _style("  Esc", fg=shortcut_color) + "    Cancel\n"
                html += _style("  ?", fg=shortcut_color) + "      Toggle help"
            else:
                # Compact mode - standardized format
                parts = [
                    _style("↑↓", fg=shortcut_color) + " nav",
                    _style("↩", fg=shortcut_color) + " select",
                ]
                if self.allow_multiple:
                    parts.append(_style("Space", fg=shortcut_color) + " toggle")
                    # Selection count
                    if self.selected_ids:
                        parts.append(
                            _style(f"{len(self.selected_ids)}", fg=shortcut_color) + " selected"
                        )
                if self.allow_back:
                    parts.append(_style("b", fg=shortcut_color) + " back")
                parts.append(_style("Esc", fg=shortcut_color) + " cancel")
                parts.append(_style("?", fg=shortcut_color) + " help")
                if self.allow_multiple:
                    parts.append(_style("a", fg=shortcut_color) + " all")
                    parts.append(_style("A", fg=shortcut_color) + " none")
                # Only show preview hint when preview is likely to render
                try:
                    term_w = self.terminal.get_terminal_width()
                    show_prev_hint = False
                    if term_w >= 100 and self.show_preview:
                        sample = (
                            self.filtered_items[self.selected_index]
                            if self.filtered_items
                            else None
                        )
                        if sample and (
                            sample.status
                            or (sample.subtitle and "Created:" in sample.subtitle)
                            or getattr(sample, "extra", None)
                        ):
                            show_prev_hint = True
                    if show_prev_hint:
                        parts.append(_style("p", fg=shortcut_color) + " preview")
                except Exception:
                    pass

                line = "  ".join(parts)
                max_footer = separator_width  # fit under separator width
                estimated_length = _visible_len(line)
                while estimated_length > max_footer and len(parts) > 3:
                    if any("Space" in p for p in parts):
                        parts = [p for p in parts if "Space" not in p]
                    elif any(" back" in p for p in parts):
                        parts = [p for p in parts if " back" not in p]
                    elif any(" cancel" in p for p in parts):
                        parts = [p.replace(" cancel", "") for p in parts]
                    else:
                        break
                    line = "  ".join(parts)
                    estimated_length = _visible_len(line)

                html += line

            return HTML(html)

        # Optional preview panel on the right
        def get_preview_text():
            try:
                term_w = self.terminal.get_terminal_width()
                if (not self.show_preview) or term_w < 100 or not self.filtered_items:
                    return HTML("")
                item = self.filtered_items[self.selected_index]
                is_simple = (not item.status) and (
                    not item.subtitle or "Created:" not in item.subtitle
                )
                if is_simple:
                    return HTML("")
                default_color = _map_rich_to_prompt_toolkit_color(
                    theme_manager.get_color("default")
                )
                muted = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
                success = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("success"))

                lines = []
                lines.append(_style(f"<b>{escape(item.title)}</b>", fg=default_color))
                lines.append(_style(f"ID: {escape(item.id)}", fg=muted))
                if item.status:
                    status_str = str(item.status).replace("TaskStatus.", "").capitalize()
                    lines.append(_style(f"Status: {status_str}", fg=success))
                if item.subtitle:
                    lines.append(_style(f"{escape(item.subtitle)}", fg=muted))
                # Show extra fields if provided
                if getattr(item, "extra", None):
                    for k, v in item.extra.items():
                        if v is None:
                            continue
                        kv = f"{k.replace('_',' ').title()}: {v}"
                        lines.append(_style(escape(str(kv)), fg=muted))
                return HTML("\n".join(lines))
            except Exception:
                return HTML("")

        # Build layout with optional VSplit when preview is enabled and useful
        # Hide the cursor in non-editable windows to avoid a stray caret in the header.
        main_body = Window(FormattedTextControl(get_body_text), always_hide_cursor=True)
        use_preview = False
        try:
            term_w = self.terminal.get_terminal_width()
            if self.show_preview and term_w >= 100:
                sample = self.filtered_items[self.selected_index] if self.filtered_items else None
                if sample and (
                    sample.status
                    or (sample.subtitle and "Created:" in sample.subtitle)
                    or getattr(sample, "extra", None)
                ):
                    use_preview = True
        except Exception:
            use_preview = False

        if use_preview:
            layout_body = VSplit(
                [
                    main_body,
                    Window(width=2, char=" ", always_hide_cursor=True),  # spacer
                    Window(
                        FormattedTextControl(get_preview_text), width=40, dont_extend_height=False, always_hide_cursor=True
                    ),
                ]
            )
        else:
            layout_body = main_body

        # Ensure layout reserves enough lines for header and footer chrome
        layout = Layout(
            HSplit(
                [
                    Window(
                        FormattedTextControl(get_header_text),
                        height=5,
                        dont_extend_height=False,
                        always_hide_cursor=True,
                        wrap_lines=True,
                    ),
                    layout_body,
                ]
            )
        )

        # Create app with better error handling for terminal issues
        try:
            # Try to create with specific input/output handling
            from prompt_toolkit.input import create_input
            from prompt_toolkit.output import create_output

            # Debug: try to create input/output separately to isolate issues
            if os.environ.get("FLOW_DEBUG"):
                try:
                    test_input = create_input()
                    self.console.print(f"[dim]Input created: {type(test_input)}[/dim]")
                except Exception as e:
                    self.console.print(
                        f"[red]Failed to create input: {escape(type(e).__name__)}: {escape(str(e))}[/red]"
                    )

                try:
                    test_output = create_output()
                    self.console.print(f"[dim]Output created: {type(test_output)}[/dim]")
                except Exception as e:
                    self.console.print(
                        f"[red]Failed to create output: {escape(type(e).__name__)}: {escape(str(e))}[/red]"
                    )

            # Set environment variable to prevent cursor position queries
            # This prevents the terminal from sending CPR sequences like ^[[27;1R
            old_cpr = os.environ.get("PROMPT_TOOLKIT_NO_CPR")
            os.environ["PROMPT_TOOLKIT_NO_CPR"] = "1"

            # Prepare prompt_toolkit input/output, preferring /dev/tty when requested
            pt_input = None
            pt_output = None
            dev_tty_handle = None
            try:
                if getattr(self, "_use_dev_tty", False):
                    try:
                        dev_tty_handle = open("/dev/tty", "r+")
                        pt_input = create_input(stdin=dev_tty_handle)
                        pt_output = create_output(stdout=dev_tty_handle)
                        if os.environ.get("FLOW_DEBUG"):
                            self.console.print("[dim]Bound prompt_toolkit to /dev/tty[/dim]")
                    except Exception as e:
                        if os.environ.get("FLOW_DEBUG"):
                            self.console.print(
                                f"[red]Failed to bind to /dev/tty: {escape(type(e).__name__)}: {escape(str(e))}[/red]"
                            )
                        # Fall back to default stdio
                        pt_input = create_input()
                        pt_output = create_output()
                else:
                    pt_input = create_input()
                    pt_output = create_output()

                app = Application(
                    layout=layout,
                    key_bindings=kb,
                    full_screen=False,  # Render inline so previous context (status panel) stays visible
                    mouse_support=False,  # Disable mouse to avoid conflicts
                    color_depth=None,  # Auto-detect
                    erase_when_done=True,  # Restore screen after exit
                    input=pt_input,
                    output=pt_output,
                )
            finally:
                # Restore original environment variable
                if old_cpr is None:
                    os.environ.pop("PROMPT_TOOLKIT_NO_CPR", None)
                else:
                    os.environ["PROMPT_TOOLKIT_NO_CPR"] = old_cpr
        except Exception as e:
            if os.environ.get("FLOW_DEBUG"):
                self.console.print(
                    f"[red]Failed to create Application: {escape(type(e).__name__)}: {escape(str(e))}[/red]"
                )
            raise

        # Run and get result - handle existing event loop
        try:
            import asyncio

            # Use create_app_session for proper terminal handling
            # Prefer the same input/output used by the Application
            from prompt_toolkit.application import create_app_session

            session_kwargs = {}
            try:
                if app.input is not None:
                    session_kwargs["input"] = app.input
                if app.output is not None:
                    session_kwargs["output"] = app.output
            except Exception:
                session_kwargs = {}

            with create_app_session(**session_kwargs):
                # Check if we're in an event loop
                try:
                    asyncio.get_running_loop()
                    # We're in an event loop, use run_in_executor
                    import queue
                    import threading

                    result_queue = queue.Queue()

                    def run_app():
                        try:
                            result = app.run()
                            result_queue.put(("success", result))
                        except KeyboardInterrupt:
                            result_queue.put(("keyboard_interrupt", None))
                        except OSError as e:
                            if e.errno == 22:  # Invalid argument
                                result_queue.put(("tty_error", e))
                            else:
                                result_queue.put(("error", e))
                        except Exception as e:
                            result_queue.put(("error", e))

                    thread = threading.Thread(target=run_app)
                    thread.start()
                    thread.join()

                    status, result = result_queue.get()
                    if status == "keyboard_interrupt":
                        raise KeyboardInterrupt()
                    elif status == "tty_error":
                        # TTY error - fall back gracefully
                        if os.environ.get("FLOW_DEBUG"):
                            self.console.print(f"[red]TTY error: {escape(str(result))}[/red]")
                        raise result
                    elif status == "error":
                        raise result
                except RuntimeError:
                    # No event loop running, safe to use app.run()
                    result = app.run()
        except OSError as e:
            if e.errno == 22:  # Invalid argument - common TTY issue
                if os.environ.get("FLOW_DEBUG"):
                    self.console.print(
                        "[red]TTY not available for interactive mode (errno 22)[/red]"
                    )
                    self.console.print("[dim]This is common in certain terminal environments[/dim]")

                # Fall back without terminal manipulation
                return self._fallback_selection()
            else:
                # Re-raise other OS errors
                raise
        except KeyboardInterrupt:
            # Re-raise KeyboardInterrupt to properly exit
            raise
        except Exception as e:
            # Clean up terminal state after prompt_toolkit failure
            if os.environ.get("FLOW_DEBUG"):
                self.console.print(
                    f"[red]Prompt toolkit app.run() failed: {escape(type(e).__name__)}: {escape(str(e))}[/red]"
                )

            # Fall back to simple selection
            return self._fallback_selection()

        # Ensure we close any opened /dev/tty handle
        try:
            if "dev_tty_handle" in locals() and dev_tty_handle is not None:
                try:
                    dev_tty_handle.close()
                except Exception:
                    pass
        finally:
            pass

        # Check for special keyboard interrupt flag
        if isinstance(result, tuple) and len(result) == 1 and result[0] == "__KEYBOARD_INTERRUPT__":
            raise KeyboardInterrupt()

        # Check for back navigation
        if result is self.BACK_SENTINEL:
            return self.BACK_SENTINEL

        if result is None:
            return None if not self.allow_multiple else []
        else:
            return result

    def _update_filter(self):
        """Update filtered items based on filter text."""
        if not self.filter_text:
            self.filtered_items = self.selection_items
            self._active_highlight_query = ""
        else:
            raw_q = self.filter_text
            tokens, free_text = _parse_tokens(raw_q)
            self._active_highlight_query = free_text.strip().lower()

            # Apply token filters when possible (only a few known keys)
            def _token_allows(item: SelectionItem) -> bool:
                if not tokens:
                    return True
                try:
                    # status:running
                    st = tokens.get("status")
                    if st:
                        st_norm = st.strip().lower()
                        item_status = str(item.status or "").replace("TaskStatus.", "").lower()
                        if item_status != st_norm:
                            return False
                    # gpu: pattern check in subtitle
                    gpu = tokens.get("gpu")
                    if gpu:
                        sub = item.subtitle or ""
                        if str(gpu) not in sub:
                            return False
                    # id: substring in id
                    tid = tokens.get("id")
                    if tid and tid.lower() not in (item.id or "").lower():
                        return False
                    return True
                except Exception:
                    return True

            token_filtered_indices = [
                i for i, it in enumerate(self.selection_items) if _token_allows(it)
            ]

            # If fuzzy is disabled or list extremely large, prefer substring prefilter
            query = free_text.strip().lower()
            if not query:
                # Only tokens applied
                self.filtered_items = [self.selection_items[i] for i in token_filtered_indices]
            else:
                # Rank using selected engine within token-filtered set
                sub_items = [self.selection_items[i] for i in token_filtered_indices]
                sub_keys = [self._search_keys[i] for i in token_filtered_indices]

                mode = self._fuzzy_mode
                if mode not in {"off", "basic", "rapidfuzz"}:
                    mode = "basic"
                if mode == "off" or len(self.selection_items) >= self._fuzzy_disable_threshold:
                    # Simple substring ranking on token-filtered set
                    ranked_idx = [
                        i
                        for i, k in zip(token_filtered_indices, sub_keys, strict=False)
                        if query in k
                    ]
                else:
                    ranked_local = _rank_items_with_fuzzy(
                        query, sub_items, sub_keys, mode, self._top_k_results
                    )
                    ranked_idx = [token_filtered_indices[i] for i in ranked_local]

                self.filtered_items = [self.selection_items[i] for i in ranked_idx]

        # Simpler index reset
        self.selected_index = min(self.selected_index, max(0, len(self.filtered_items) - 1))
        # Reset viewport when filtering
        self.viewport_start = 0
        self._update_viewport()

    def _update_viewport(self):
        """Update viewport to ensure selected item is visible."""
        if not self.filtered_items:
            return

        # If selected item is above viewport, scroll up
        if self.selected_index < self.viewport_start:
            self.viewport_start = self.selected_index

        # If selected item is below viewport, scroll down
        elif self.selected_index >= self.viewport_start + self.viewport_size:
            self.viewport_start = self.selected_index - self.viewport_size + 1

        # Ensure viewport doesn't go out of bounds
        max_start = max(0, len(self.filtered_items) - self.viewport_size)
        self.viewport_start = max(0, min(self.viewport_start, max_start))

    def _calculate_column_widths(self) -> dict:
        """Calculate consistent column widths for tabular layout."""
        terminal_width = self.terminal.get_terminal_width()
        # Reserve space for margins, arrow, and spacing between columns
        available_width = terminal_width - 12

        # Fixed widths for other columns - optimized for readability
        status_width = 13  # Enough for "● Preempting"

        # Derive GPU width from visible items, with a reasonable cap
        gpu_width = 11  # Default minimum
        try:
            for item in self.filtered_items[:20]:  # Check first 20 visible items
                if item.subtitle:
                    gpu_part = item.subtitle.split(" • ")[0] if " • " in item.subtitle else ""
                    gpu_width = max(gpu_width, len(gpu_part))
            gpu_width = min(16, gpu_width)  # Cap at 16 chars
        except:
            gpu_width = 14  # Safe fallback for multi-node strings

        # Time column width adaptive based on visible items
        try:
            max_time_len = 0
            for item in self.filtered_items[:20]:
                if item.subtitle and " • " in item.subtitle:
                    time_part = item.subtitle.split(" • ")[-1]
                    max_time_len = max(max_time_len, len(time_part))
            time_width = max(16, min(20, max_time_len or 20))
        except Exception:
            time_width = 20

        # Give remaining space to name column, but cap it
        name_width = (
            available_width - status_width - gpu_width - time_width - 8
        )  # Extra spacing between columns
        name_width = max(20, min(name_width, 36))  # Between 20-36 chars for better alignment

        return {
            "name": name_width,
            "status": status_width,
            "gpu": gpu_width,
            "time": time_width,
        }

    def _apply_selection_style(self, content: str, is_selected: bool) -> str:
        """Apply consistent selection background to content.

        Args:
            content: The formatted content string
            is_selected: Whether the item is selected

        Returns:
            Content with selection background applied if selected
        """
        if is_selected:
            selection_bg = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("selected_bg"))
            selection_fg = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("selected_fg"))
            # Apply both background and foreground to guarantee readable contrast
            return f"<style bg='{selection_bg}' fg='{selection_fg}'>" f"{content}</style>"
        return content

    def _format_item_line(
        self, item: SelectionItem, is_selected: bool, column_widths: dict, idx: int | None = None
    ) -> str:
        """Format a single item line with consistent column layout.

        Args:
            item: The selection item to format
            is_selected: Whether this item is currently selected
            column_widths: Dictionary of column widths

        Returns:
            Formatted HTML line
        """
        # Marker for multi-select (track by stable id)
        is_checked = self.allow_multiple and (item.id in self.selected_ids)
        selection_marker = "[x]" if is_checked else ("[ ]" if self.allow_multiple else "  ")

        # Check if this is a simple item (no status/subtitle columns needed)
        is_simple_item = not item.status and (not item.subtitle or "Created:" not in item.subtitle)

        if is_simple_item:
            # Simple format for action items like "Generate new SSH key"
            if is_selected:
                arrow_color = _map_rich_to_prompt_toolkit_color(
                    theme_manager.get_color("selected_arrow")
                )
                line = f"{_style('▸', fg=arrow_color)} {selection_marker} <b>{item.title}</b>"
                return self._apply_selection_style(line, True)
            else:
                return f"   {selection_marker} <b>{item.title}</b>"

        # Check if this is an SSH key item (has Created: in subtitle)
        is_ssh_key = item.subtitle and "Created:" in item.subtitle

        if is_ssh_key:
            # Special formatting for SSH keys with proper alignment
            terminal_width = self.terminal.get_terminal_width()
            available_width = terminal_width - 10

            # Calculate widths for SSH key display
            name_width = min(30, available_width // 2)
            metadata_width = available_width - name_width - 2

            # Truncate name if needed
            name = self.terminal.intelligent_truncate(item.title, name_width, priority="start")

            # Format subtitle nicely
            subtitle = item.subtitle
            if len(subtitle) > metadata_width:
                # Keep the Created date and truncate the fingerprint
                parts = subtitle.split("SHA256:")
                if len(parts) == 2:
                    date_part = parts[0].strip()
                    fingerprint = "SHA256:" + parts[1][:8] + "..."
                    subtitle = f"{date_part}{fingerprint}"

            if is_selected:
                arrow_color = _map_rich_to_prompt_toolkit_color(
                    theme_manager.get_color("selected_arrow")
                )
                muted_sel_color = _map_rich_to_prompt_toolkit_color(
                    theme_manager.get_color("selected_muted_fg")
                )
                name_part = f"<b>{name:<{name_width}}</b>"
                subtitle_part = _style(subtitle, fg=muted_sel_color)
                line = (
                    f"{_style('▸', fg=arrow_color)} {selection_marker} {name_part}  {subtitle_part}"
                )
                return self._apply_selection_style(line, True)
            else:
                muted_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
                return f"   {selection_marker} {name:<{name_width}}  {_style(subtitle, fg=muted_color)}"

        # Check if this is a project or other simple item with status
        if item.status and not item.subtitle:
            # Simple item with status (like projects)
            terminal_width = self.terminal.get_terminal_width()
            available_width = terminal_width - 10
            name_width = available_width - 20  # Leave space for status

            name = self.terminal.intelligent_truncate(item.title, name_width, priority="start")

            if is_selected:
                arrow_color = _map_rich_to_prompt_toolkit_color(
                    theme_manager.get_color("selected_arrow")
                )
                success_color = _map_rich_to_prompt_toolkit_color(
                    theme_manager.get_color("success")
                )
                status_part = _style(f"● {item.status}", fg=success_color)
                line = f"{_style('▸', fg=arrow_color)} {selection_marker} <b>{name:<{name_width}}</b>  {status_part}"
                return self._apply_selection_style(line, True)
            else:
                success_color = _map_rich_to_prompt_toolkit_color(
                    theme_manager.get_color("success")
                )
                status_part = _style(f"● {item.status}", fg=success_color)
                return f"   {selection_marker} {name:<{name_width}}  {status_part}"

        # Extract components from subtitle
        subtitle_parts = item.subtitle.split(" • ") if item.subtitle else []
        gpu_info = subtitle_parts[0] if len(subtitle_parts) > 0 else ""
        time_info = subtitle_parts[-1] if len(subtitle_parts) > 0 else ""

        # Get status formatting
        status_str = str(item.status).replace("TaskStatus.", "") if item.status else ""
        status_display = status_str.capitalize() if status_str else ""
        # Use optional status metadata provided via SelectionItem.extra to avoid domain coupling
        status_symbol = None
        status_color_name = None
        if getattr(item, "extra", None):
            status_symbol = item.extra.get("status_symbol")
            status_color_name = item.extra.get("status_color")

        # Truncate name to fit column - keep the beginning of the name
        name = self.terminal.intelligent_truncate(
            item.title, column_widths["name"], priority="start"
        )

        if is_selected:
            # Selected line with subtle cyan arrow
            arrow_color = _map_rich_to_prompt_toolkit_color(
                theme_manager.get_color("selected_arrow")
            )
            line = f"{_style('▸', fg=arrow_color)} {selection_marker} "
            # Status first
            if status_display:
                symbol = status_symbol or ""
                text = f"{symbol} {status_display}".strip()
                color_to_use = (
                    _map_rich_to_prompt_toolkit_color(status_color_name)
                    if status_color_name
                    else _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
                )
                line += _style(f"{text:<{column_widths['status']}}", fg=color_to_use) + "  "
            else:
                line += " " * (column_widths["status"] + 2)
            # Then name (with optional highlight). Pad first, then highlight to keep spacing.
            padded_plain = f"{name:<{column_widths['name']}}"
            if self._active_highlight_query:
                name_h = _highlight_matches(
                    padded_plain,
                    self._active_highlight_query,
                    theme_manager.get_color("shortcut_key"),
                )
            else:
                name_h = padded_plain
            line += f"<b>{name_h}</b>  "
            # Use selection-aware muted color for readability on highlight
            muted_sel_color = _map_rich_to_prompt_toolkit_color(
                theme_manager.get_color("selected_muted_fg")
            )
            gpu_part = f"{gpu_info:<{column_widths['gpu']}}"
            time_part = f"{time_info:<{column_widths['time']}}"
            if self._active_highlight_query:
                gpu_part = _highlight_matches(
                    gpu_part, self._active_highlight_query, theme_manager.get_color("shortcut_key")
                )
                time_part = _highlight_matches(
                    time_part, self._active_highlight_query, theme_manager.get_color("shortcut_key")
                )
            line += _style(gpu_part, fg=muted_sel_color)
            line += _style(time_part, fg=muted_sel_color)
            line = self._apply_selection_style(line, True)
        else:
            # Normal line with proper theme colors
            line = "   "
            default_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("default"))
            muted_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))

            line += f"{selection_marker} "
            # Status first
            if status_display:
                symbol = status_symbol or ""
                text = f"{symbol} {status_display}".strip()
                color_to_use = (
                    _map_rich_to_prompt_toolkit_color(status_color_name)
                    if status_color_name
                    else _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
                )
                line += _style(f"{text:<{column_widths['status']}}", fg=color_to_use) + "  "
            else:
                line += " " * (column_widths["status"] + 2)
            # Then name (with optional highlight). Pad first, then highlight to keep spacing.
            padded_plain = f"{name:<{column_widths['name']}}"
            if self._active_highlight_query:
                name_h = _highlight_matches(
                    padded_plain,
                    self._active_highlight_query,
                    theme_manager.get_color("shortcut_key"),
                )
            else:
                name_h = padded_plain
            line += _style(name_h, fg=default_color) + "  "
            gpu_part = f"{gpu_info:<{column_widths['gpu']}}"
            time_part = f"{time_info:<{column_widths['time']}}"
            if self._active_highlight_query:
                gpu_part = _highlight_matches(
                    gpu_part, self._active_highlight_query, theme_manager.get_color("shortcut_key")
                )
                time_part = _highlight_matches(
                    time_part, self._active_highlight_query, theme_manager.get_color("shortcut_key")
                )
            line += _style(gpu_part, fg=muted_color)
            line += _style(time_part, fg=muted_color)

        return line

    def _fallback_selection(self) -> T | None | list[T]:
        """Simple numbered selection for non-interactive environments with pagination."""
        if not self.items:
            return None if not self.allow_multiple else []

        # Ensure terminal is in a clean state before fallback
        try:
            import os as _os

            _os.system("stty sane 2>/dev/null || true")
        except Exception:
            pass
        if os.environ.get("FLOW_DEBUG"):
            self.console.print("[dim]Preparing terminal for fallback selection...[/dim]")

        # Precompute duplicate-name counts to disambiguate identical titles
        name_counts: dict[str, int] = {}
        try:
            name_counts = dict(Counter(si.title for si in self.selection_items))
        except Exception:
            name_counts = {}

        # Display items with pagination for long lists
        accent_color = theme_manager.get_color("accent")
        border_color = theme_manager.get_color("table.border")
        self.console.print(f"\n[bold {accent_color}]{self.title}[/bold {accent_color}]")
        self.console.print(f"[{border_color}]" + "─" * 60 + f"[/{border_color}]")

        # Pagination settings
        page_size = 20
        total_items = len(self.selection_items)
        current_page = 0
        total_pages = (total_items + page_size - 1) // page_size

        # Simple filter support
        filtered_items = list(self.selection_items)
        filter_text = ""

        while True:
            # Calculate page boundaries
            start_idx = current_page * page_size
            end_idx = min(start_idx + page_size, len(filtered_items))

            # Clear screen for better UX (optional, can be removed if problematic)
            if current_page > 0 or filter_text:
                self.console.print("\n" * 2)  # Just add spacing instead of clearing

            # Show filter if active
            if filter_text:
                self.console.print(f"[dim]Filter: {filter_text}[/dim]")
                self.console.print(
                    f"[dim]Showing {len(filtered_items)} of {total_items} items[/dim]"
                )
            elif total_pages > 1:
                self.console.print(
                    f"[dim]Page {current_page + 1}/{total_pages} (items {start_idx + 1}-{end_idx} of {len(filtered_items)})[/dim]"
                )

            # Display current page items
            for i in range(start_idx, end_idx):
                item = filtered_items[i]
                # Build display line - aligned and consistent
                name = item.title
                # For fallback mode, use a reasonable fixed width
                name = TerminalAdapter.intelligent_truncate(name, 60)

                # Build clean line without duplicate numbering. If the label already
                # contains an index token like "[1] Foo", avoid adding the leading
                # "1. " prefix which would produce "1. [1] Foo".
                if name.strip().startswith("[") and "]" in name:
                    line = f"  {name}"
                else:
                    # Disambiguate duplicate names by appending short ID
                    if name_counts.get(item.title, 0) > 1 and item.id:
                        short_id = (item.id[:8] + "…") if len(item.id) > 8 else item.id
                        name = f"{name} [dim]{short_id}[/dim]"
                    line = f"  {i + 1}. {name}"

                if item.status:
                    status_str = str(item.status).replace("TaskStatus.", "")
                    status_display = status_str.capitalize()
                    # Use metadata if available
                    status_symbol = ""
                    status_color = theme_manager.get_color("muted")
                    if getattr(item, "extra", None):
                        status_symbol = item.extra.get("status_symbol", "")
                        status_color = item.extra.get("status_color", status_color)
                    line += f" [{status_color}]{status_symbol}[/{status_color}] {status_display}".strip()

                if item.subtitle:
                    line += f" [dim]• {item.subtitle}[/dim]"

                self.console.print(line)

            # Show navigation options
            nav_parts = []
            if current_page > 0:
                nav_parts.append("'p' = prev page")
            if end_idx < len(filtered_items):
                nav_parts.append("'n' = next page")
            if not filter_text and len(self.selection_items) > 10:
                nav_parts.append("'/' = filter")
            if filter_text:
                nav_parts.append("'c' = clear filter")

            if nav_parts:
                self.console.print(f"\n[dim]{' | '.join(nav_parts)}[/dim]")

            # Get user input with ESC-sequence sanitization to avoid stray CPR echoes
            prompt = f"\nSelect (1-{len(filtered_items)})"
            if self.allow_multiple:
                prompt += " or ranges (e.g. 1,3-5)"
            prompt += ": "

            def _readline_sanitized(prompt_text: str) -> str | None:
                try:
                    import fcntl
                    import os as _os
                    import re as _re
                    import select as _select
                    import termios
                    import tty

                    fd = sys.stdin.fileno()
                    if not sys.stdin.isatty():
                        # Fallback to blocking read
                        self.console.print(prompt_text, end="")
                        sys.stdout.flush()
                        try:
                            return sys.stdin.readline()
                        except EOFError:
                            return None

                    # Save attrs and turn off echo, cbreak for minimal processing
                    old_attrs = termios.tcgetattr(fd)
                    new_attrs = termios.tcgetattr(fd)
                    new_attrs[3] = new_attrs[3] & ~termios.ECHO  # lflags: disable ECHO
                    termios.tcsetattr(fd, termios.TCSANOW, new_attrs)
                    tty.setcbreak(fd)

                    # Non-blocking reads to accumulate and filter
                    old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
                    fcntl.fcntl(fd, fcntl.F_SETFL, old_flags | _os.O_NONBLOCK)

                    try:
                        sys.stdout.write(prompt_text)
                        sys.stdout.flush()

                        buf: list[str] = []
                        esc_pattern = _re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")

                        while True:
                            r, _, _ = _select.select([fd], [], [], 0.5)
                            if not r:
                                continue
                            try:
                                ch = _os.read(fd, 1)
                            except BlockingIOError:
                                continue
                            if not ch:
                                return ""
                            c = ch.decode(errors="ignore")
                            if c == "\n" or c == "\r":
                                sys.stdout.write("\n")
                                sys.stdout.flush()
                                return "".join(buf)
                            if c == "\x7f":  # backspace
                                if buf:
                                    buf.pop()
                                    sys.stdout.write("\b \b")
                                    sys.stdout.flush()
                                continue
                            if c == "\x1b":
                                seq = c
                                # consume rest of escape sequence
                                for _ in range(16):
                                    r2, _, _ = _select.select([fd], [], [], 0.01)
                                    if not r2:
                                        break
                                    try:
                                        ch2 = _os.read(fd, 1)
                                    except BlockingIOError:
                                        break
                                    if not ch2:
                                        break
                                    seq += ch2.decode(errors="ignore")
                                    if esc_pattern.search(seq):
                                        break
                                # do not echo; ignore sequence
                                continue
                            # Accept only simple selection chars
                            if self.allow_multiple:
                                valid = c.isdigit() or c in {" ", ",", "-"}
                            else:
                                valid = c.isdigit()
                            if valid:
                                buf.append(c)
                                sys.stdout.write(c)
                                sys.stdout.flush()
                        # unreachable
                    finally:
                        fcntl.fcntl(fd, fcntl.F_SETFL, old_flags)
                        termios.tcsetattr(fd, termios.TCSANOW, old_attrs)
                except Exception:
                    # Safe fallback path
                    try:
                        self.console.print(prompt_text, end="")
                        sys.stdout.flush()
                        return sys.stdin.readline()
                    except EOFError:
                        return None

            try:
                response_raw = _readline_sanitized(prompt)
                if response_raw is None:
                    return None if not self.allow_multiple else []
                response = response_raw.strip().lower()
            except (EOFError, KeyboardInterrupt):
                return None if not self.allow_multiple else []

            # Handle navigation commands
            if response == "n" and end_idx < len(filtered_items):
                current_page = min(current_page + 1, total_pages - 1)
                continue
            elif response == "p" and current_page > 0:
                current_page = max(current_page - 1, 0)
                continue
            elif response == "/" and not filter_text:
                self.console.print("Filter: ", end="")
                sys.stdout.flush()
                filter_text = sys.stdin.readline().strip()
                if filter_text:
                    # Simple substring filter
                    filtered_items = [
                        item
                        for item in self.selection_items
                        if filter_text.lower() in item.title.lower()
                        or (item.subtitle and filter_text.lower() in item.subtitle.lower())
                    ]
                    current_page = 0
                    total_pages = (
                        (len(filtered_items) + page_size - 1) // page_size if filtered_items else 1
                    )
                continue
            elif response == "c" and filter_text:
                filter_text = ""
                filtered_items = list(self.selection_items)
                current_page = 0
                total_pages = (total_items + page_size - 1) // page_size
                continue

            # Handle selection
            break

        # Process selection after pagination/filtering
        try:
            # response variable contains the user's selection from the pagination loop
            if self.allow_multiple:
                # Multiple selection mode
                if response == "all":
                    return [item.value for item in filtered_items]
                elif response == "none" or not response:
                    return []
                # Parse selection ranges
                try:
                    parts = response.replace(",", " ").split()
                    indices: list[int] = []
                    for part in parts:
                        if "-" in part:
                            a, b = part.split("-", 1)
                            a_i = int(a) - 1
                            b_i = int(b) - 1
                            if a_i <= b_i:
                                indices.extend(list(range(a_i, b_i + 1)))
                            else:
                                indices.extend(list(range(b_i, a_i + 1)))
                        else:
                            indices.append(int(part) - 1)
                    return [
                        filtered_items[i].value for i in indices if 0 <= i < len(filtered_items)
                    ]
                except ValueError:
                    self.console.print("[yellow]Invalid input, returning empty selection[/yellow]")
                    return []
            else:
                # Single selection mode
                if not response or response in {"q", "quit", "cancel"}:
                    return None

                try:
                    choice = int(response)
                    if 1 <= choice <= len(filtered_items):
                        return filtered_items[choice - 1].value
                    else:
                        self.console.print(
                            f"[yellow]Please enter a number between 1 and {len(filtered_items)}[/yellow]"
                        )
                        # Could re-prompt but avoiding recursion for simplicity
                        return None
                except ValueError:
                    self.console.print("[yellow]Please enter a valid number[/yellow]")
                    return None
        except (KeyboardInterrupt, EOFError):
            self.console.print("\n[yellow]Cancelled[/yellow]")

        return None if not self.allow_multiple else []


def select_task(
    tasks: list[Task], title: str = "Select a task", allow_multiple: bool = False
) -> Task | None | list[Task]:
    """Interactive task selector."""

    # Deduplicate tasks by task_id while preserving order to avoid repeated entries
    try:
        seen_ids: set[str] = set()
        unique_tasks: list[Task] = []
        for t in tasks:
            tid = getattr(t, "task_id", None)
            if tid and tid not in seen_ids:
                seen_ids.add(tid)
                unique_tasks.append(t)
        tasks = unique_tasks or tasks
    except Exception:
        pass

    def task_to_selection(task: Task) -> SelectionItem[Task]:
        # Calculate duration
        duration = _format_task_duration(task)

        # Format GPU using ultra-compact format - include num_instances for multi-node
        gpu_fmt = GPUFormatter()
        gpu_display = gpu_fmt.format_ultra_compact(
            task.instance_type, getattr(task, "num_instances", 1)
        )

        # Format cost if available (gated by environment variable)
        show_price = os.environ.get("FLOW_SHOW_PRICE", "").lower() == "true"
        cost_str = ""
        if show_price and hasattr(task, "price_per_hour") and task.price_per_hour:
            cost_str = f" • ${task.price_per_hour:.2f}/hr"

        # Provide status metadata to avoid domain coupling inside selector
        status_symbol = ""
        status_color = None
        if getattr(task, "status", None):
            status_str = str(task.status).replace("TaskStatus.", "").lower()
            try:
                cfg = TaskFormatter.get_status_config(status_str)
                status_symbol = cfg.get("symbol", "")
                status_color = cfg.get("color")
            except Exception:
                pass

        return SelectionItem(
            value=task,
            id=task.task_id,
            title=task.name or "Unnamed task",
            subtitle=f"{gpu_display}{cost_str} • {duration}",
            status=task.status,
            extra={
                "instance_type": task.instance_type,
                "duration": duration,
                "status_symbol": status_symbol,
                "status_color": status_color,
            },
        )

    selector = InteractiveSelector(
        items=tasks, item_to_selection=task_to_selection, title=title, allow_multiple=allow_multiple
    )

    return selector.select()


def select_volume(
    volumes: list[Volume], title: str = "Select a volume", allow_multiple: bool = False
) -> Volume | None | list[Volume]:
    """Interactive volume selector."""

    def volume_to_selection(volume: Volume) -> SelectionItem[Volume]:
        # Format subtitle with available information
        subtitle_parts = [f"{volume.size_gb}GB"]
        if hasattr(volume, "region") and volume.region:
            subtitle_parts.append(volume.region)
        if hasattr(volume, "interface") and volume.interface:
            subtitle_parts.append(str(volume.interface))

        # Determine status
        status = ""
        if hasattr(volume, "status"):
            status = "ACTIVE" if volume.status == "available" else str(volume.status).upper()

        return SelectionItem(
            value=volume,
            id=volume.volume_id,
            title=volume.name or volume.volume_id,
            subtitle=" • ".join(subtitle_parts),
            status=status,
            extra={"size_gb": volume.size_gb},
        )

    selector = InteractiveSelector(
        items=volumes,
        item_to_selection=volume_to_selection,
        title=title,
        allow_multiple=allow_multiple,
    )

    return selector.select()
