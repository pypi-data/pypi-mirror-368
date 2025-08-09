"""Interactive resource selector for Flow CLI.

This module provides a delightful, interactive selection experience for
commands that operate on resources (tasks, volumes, etc). Inspired by
fzf and kubectl's interactive mode.

Design principles:
- Zero configuration - just works
- Graceful fallback for non-interactive environments
- Beautiful and informative display
- Keyboard navigation that feels natural
- Fast and responsive
"""

from __future__ import annotations

import os
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Generic, TypeVar, Optional

from prompt_toolkit import Application
from prompt_toolkit.filters import Condition
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import FormattedTextControl, Layout, Window, HSplit

from flow.api.models import Task, Volume
from .gpu_formatter import GPUFormatter
from .task_formatter import TaskFormatter
from .terminal_adapter import TerminalAdapter
from .theme_manager import theme_manager
from rich.markup import escape

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
        "bright_white": "ansibrightwhite",
        "bright_black": "ansibrightblack",
        # Dark variants
        "dark_green": "darkgreen",
        "dark_red": "darkred",
        "dark_blue": "darkblue",
        # Other colors remain as-is
    }

    return color_map.get(rich_color, rich_color)


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
    """Wrapper for selectable items with display information."""

    value: T
    id: str
    title: str
    subtitle: str
    status: str
    extra: dict = None

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
        breadcrumbs: Optional[list[str]] = None,
        extra_header_html: Optional[str] = None,
        preferred_viewport_size: Optional[int] = None,
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
        
        # Deterministic viewport: clamp between 6 and 8, reserve 9 lines for chrome
        # This ensures consistent behavior regardless of title content
        default_viewport = max(6, min(8, self.terminal_lines - 9))
        
        # If caller provided a preferred viewport size, use it as a clamp only
        if self.preferred_viewport_size is not None:
            self.viewport_size = max(3, min(default_viewport, int(self.preferred_viewport_size)))
        else:
            self.viewport_size = default_viewport
        
        self.viewport_start = 0

    def select(self) -> T | None | list[T]:
        """Show interactive selector and return selected item(s)."""
        # Check if we're in an interactive terminal
        force_interactive = os.environ.get("FLOW_FORCE_INTERACTIVE", "").lower() == "true"

        # Skip interactive mode if explicitly disabled
        if os.environ.get("FLOW_NONINTERACTIVE"):
            if os.environ.get("FLOW_DEBUG"):
                self.console.print("[dim]FLOW_NONINTERACTIVE is set[/dim]")
            return self._fallback_selection()

        # Check terminal compatibility for prompt_toolkit
        # Some terminals (like certain CI environments) can't support it
        term = os.environ.get("TERM", "")
        # If not attached to a real TTY, skip interactive unless forced
        if not (sys.stdin.isatty() and sys.stdout.isatty()) and not force_interactive:
            if os.environ.get("FLOW_DEBUG"):
                self.console.print("[dim]stdin/stdout not TTY, using fallback[/dim]")
            return self._fallback_selection()
        if term == "dumb" and not force_interactive:
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
            self.console.print(f"[green]Auto-selecting:[/green] {item.title} ({item.id})")
            return item.value

        # Run interactive selector
        try:
            if os.environ.get("FLOW_DEBUG"):
                self.console.print("[dim]Attempting to run interactive selector...[/dim]")

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

        # Number key shortcuts
        for i in range(1, 10):

            @kb.add(str(i))
            def handle_number(event, index=i - 1):
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
            if len(key) == 1 and key in allowed_chars:
                self.filter_text += key
                self._update_filter()

        # Create layout with sticky header and scrolling body
        def get_header_text():
            default_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("default"))
            border_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))

            # Add top margin for tall terminals (≥28 rows) for better visual balance
            if self.terminal_lines >= 28:
                html = "\n"
            else:
                html = ""
            
            if self.extra_header_html:
                html += self.extra_header_html.rstrip() + "\n\n"

            if self.breadcrumbs:
                breadcrumb_text = " › ".join(self.breadcrumbs)
                muted_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
                html += f"<{muted_color}>{breadcrumb_text}</{muted_color}>\n\n"

            html += f"<{default_color}><bold>{self.title}</bold></{default_color}>\n"
            muted_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
            if self.allow_back:
                html += f"<{muted_color}>ESC back • Ctrl+C exit</{muted_color}>\n"
            else:
                html += f"<{muted_color}>ESC cancel • Ctrl+C exit</{muted_color}>\n"

            terminal_width = self.terminal.get_terminal_width()
            separator_width = max(10, min(terminal_width - 4, 80))
            html += f"<{border_color}>{'─' * separator_width}</{border_color}>\n"

            return HTML(html)

        def get_body_text():
            border_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
            terminal_width = self.terminal.get_terminal_width()
            separator_width = max(10, min(terminal_width - 4, 80))

            html = ""

            # Filter indicator with better spacing (subtle, single blank line)
            if self.filter_text:
                muted_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
                html += f"<{muted_color}><i>Filter: {self.filter_text}</i></{muted_color}>\n"

            # Calculate viewport
            viewport_end = min(self.viewport_start + self.viewport_size, len(self.filtered_items))

            # Scroll indicators
            if self.viewport_start > 0:
                muted_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
                html += f"<{muted_color}>  ↑ {self.viewport_start} more above...</{muted_color}>\n"

            # Get column widths once
            column_widths = self._calculate_column_widths()

            # Items in viewport
            for i in range(self.viewport_start, viewport_end):
                item = self.filtered_items[i]
                is_selected = i == self.selected_index

                line = self._format_item_line(item, is_selected, column_widths, i)
                html += line + ("\n\n" if i < viewport_end - 1 else "\n")

            # Bottom scroll indicator
            if viewport_end < len(self.filtered_items):
                muted_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
                html += f"<{muted_color}>  ↓ {len(self.filtered_items) - viewport_end} more below...</{muted_color}>\n"

            # Adaptive footer navigation (compact to avoid wrapping)
            shortcut_color = _map_rich_to_prompt_toolkit_color(
                theme_manager.get_color("shortcut_key")
            )
            muted_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
            html += "\n"
            html += f"<{muted_color}>{'─' * separator_width}</{muted_color}>\n"

            if self.show_help:
                # Extended help mode - one action per line, aligned
                html += f"<{shortcut_color}><bold>Navigation Help</bold></{shortcut_color}>\n"
                html += f"  <{shortcut_color}>↑/k</{shortcut_color}>    Move up\n"
                html += f"  <{shortcut_color}>↓/j</{shortcut_color}>    Move down\n"
                html += f"  <{shortcut_color}>↩</{shortcut_color}>      Select item\n"
                if self.allow_multiple:
                    html += f"  <{shortcut_color}>Space</{shortcut_color}>  Toggle selection\n"
                html += f"  <{shortcut_color}>1-9</{shortcut_color}>    Jump to item\n"
                if self.allow_back:
                    html += f"  <{shortcut_color}>b</{shortcut_color}>      Go back\n"
                html += f"  <{shortcut_color}>Esc</{shortcut_color}>    Cancel\n"
                html += f"  <{shortcut_color}>?</{shortcut_color}>      Toggle help"
            else:
                # Compact mode - standardized format
                parts = [f"<{shortcut_color}>↑↓</{shortcut_color}> nav", f"<{shortcut_color}>↩</{shortcut_color}> select"]
                if self.allow_multiple:
                    parts.append(f"<{shortcut_color}>Space</{shortcut_color}> toggle")
                if self.allow_back:
                    parts.append(f"<{shortcut_color}>b</{shortcut_color}> back")
                parts.append(f"<{shortcut_color}>Esc</{shortcut_color}> cancel")
                parts.append(f"<{shortcut_color}>?</{shortcut_color}> help")

                line = "  ".join(parts)
                max_footer = separator_width  # fit under separator width
                # Use string length heuristic instead of heavy HTML parsing
                estimated_length = len(line) - line.count('<') * 7
                while estimated_length > max_footer and len(parts) > 3:
                    if any("Space" in p for p in parts):
                        parts = [p for p in parts if "Space" not in p]
                    elif any(">b<" in p or " back" in p for p in parts):
                        parts = [p for p in parts if " back" not in p]
                    elif any(" cancel" in p for p in parts):
                        parts = [p.replace(" cancel", "") for p in parts]
                    else:
                        break
                    line = "  ".join(parts)
                    estimated_length = len(line) - line.count('<') * 7

                html += line

            return HTML(html)

        layout = Layout(
            HSplit(
                [
                    Window(FormattedTextControl(get_header_text), dont_extend_height=True),
                    Window(FormattedTextControl(get_body_text)),
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

            app = Application(
                layout=layout,
                key_bindings=kb,
                full_screen=False,      # Render inline so previous context (status panel) stays visible
                mouse_support=False,    # Disable mouse to avoid conflicts
                color_depth=None,       # Auto-detect
                erase_when_done=True,   # Restore screen after exit
            )
        except Exception as e:
            if os.environ.get("FLOW_DEBUG"):
                self.console.print(
                    f"[red]Failed to create Application: {escape(type(e).__name__)}: {escape(str(e))}[/red]"
                )
            raise

        # Run and get result - handle existing event loop
        try:
            import asyncio

            from prompt_toolkit.application import create_app_session

            # Use create_app_session for proper terminal handling
            with create_app_session():
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
        else:
            query = self.filter_text.lower()
            # Use precomputed lowercase search keys for performance
            self.filtered_items = [
                si for si, key in zip(self.selection_items, self._search_keys) if query in key
            ]

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
        
        time_width = 20  # Enough for "created 22h 34m ago"

        # Give remaining space to name column, but cap it
        name_width = (
            available_width - status_width - gpu_width - time_width - 8
        )  # Extra spacing between columns
        name_width = max(20, min(name_width, 30))  # Between 20-30 chars for better alignment

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
            selection_bg = _map_rich_to_prompt_toolkit_color(
                theme_manager.get_color("selected_bg")
            )
            selection_fg = _map_rich_to_prompt_toolkit_color(
                theme_manager.get_color("selected_fg")
            )
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
                line = f"<{arrow_color}>▸</{arrow_color}> {selection_marker} <bold>{item.title}</bold>"
                return self._apply_selection_style(line, True)
            else:
                return f"   {selection_marker} <bold>{item.title}</bold>"

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
                line = f"<{arrow_color}>▸</{arrow_color}> {selection_marker} <bold>{name:<{name_width}}</bold>  <{muted_sel_color}>{subtitle}</{muted_sel_color}>"
                return self._apply_selection_style(line, True)
            else:
                muted_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
                return f"   {selection_marker} {name:<{name_width}}  <{muted_color}>{subtitle}</{muted_color}>"

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
                line = f"<{arrow_color}>▸</{arrow_color}> {selection_marker} <bold>{name:<{name_width}}</bold>  <{success_color}>● {item.status}</{success_color}>"
                return self._apply_selection_style(line, True)
            else:
                success_color = _map_rich_to_prompt_toolkit_color(
                    theme_manager.get_color("success")
                )
                return f"   {selection_marker} {name:<{name_width}}  <{success_color}>● {item.status}</{success_color}>"

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
            line = f"<{arrow_color}>▸</{arrow_color}> {selection_marker} "
            
            # Status first
            if status_display:
                symbol = status_symbol or ""
                text = f"{symbol} {status_display}".strip()
                color_to_use = _map_rich_to_prompt_toolkit_color(status_color_name) if status_color_name else _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
                line += f"<{color_to_use}>{text:<{column_widths['status']}}</{color_to_use}>  "
            else:
                line += " " * (column_widths["status"] + 2)
            
            # Then name
            line += f"<bold>{name:<{column_widths['name']}}</bold>  "

            # Use selection-aware muted color for readability on highlight
            muted_sel_color = _map_rich_to_prompt_toolkit_color(
                theme_manager.get_color("selected_muted_fg")
            )
            line += f"<{muted_sel_color}>{gpu_info:<{column_widths['gpu']}}</{muted_sel_color}>"
            line += f"<{muted_sel_color}>{time_info:<{column_widths['time']}}</{muted_sel_color}>"
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
                color_to_use = _map_rich_to_prompt_toolkit_color(status_color_name) if status_color_name else _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
                line += f"<{color_to_use}>{text:<{column_widths['status']}}</{color_to_use}>  "
            else:
                line += " " * (column_widths["status"] + 2)
            
            # Then name
            line += f"<{default_color}>{name:<{column_widths['name']}}</{default_color}>  "

            line += f"<{muted_color}>{gpu_info:<{column_widths['gpu']}}</{muted_color}>"
            line += f"<{muted_color}>{time_info:<{column_widths['time']}}</{muted_color}>"

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
                self.console.print(f"[dim]Showing {len(filtered_items)} of {total_items} items[/dim]")
            elif total_pages > 1:
                self.console.print(f"[dim]Page {current_page + 1}/{total_pages} (items {start_idx + 1}-{end_idx} of {len(filtered_items)})[/dim]")

            # Display current page items
            for i in range(start_idx, end_idx):
                item = filtered_items[i]
                # Build display line - aligned and consistent
                name = item.title
                # For fallback mode, use a reasonable fixed width
                name = TerminalAdapter.intelligent_truncate(name, 60)

                # Build clean line without fixed-width formatting
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
            prompt = "\nSelect (1-{})".format(len(filtered_items))
            if self.allow_multiple:
                prompt += " or ranges (e.g. 1,3-5)"
            prompt += ": "

            def _readline_sanitized(prompt_text: str) -> str | None:
                try:
                    import termios
                    import tty
                    import fcntl
                    import os as _os
                    import select as _select
                    import re as _re

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
            if response == 'n' and end_idx < len(filtered_items):
                current_page = min(current_page + 1, total_pages - 1)
                continue
            elif response == 'p' and current_page > 0:
                current_page = max(current_page - 1, 0)
                continue
            elif response == '/' and not filter_text:
                self.console.print("Filter: ", end="")
                sys.stdout.flush()
                filter_text = sys.stdin.readline().strip()
                if filter_text:
                    # Simple substring filter
                    filtered_items = [item for item in self.selection_items 
                                    if filter_text.lower() in item.title.lower() 
                                    or (item.subtitle and filter_text.lower() in item.subtitle.lower())]
                    current_page = 0
                    total_pages = (len(filtered_items) + page_size - 1) // page_size if filtered_items else 1
                continue
            elif response == 'c' and filter_text:
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
                    parts = response.replace(',', ' ').split()
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
