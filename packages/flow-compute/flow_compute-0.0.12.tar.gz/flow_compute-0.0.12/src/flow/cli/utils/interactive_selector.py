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

import os
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Generic, TypeVar

from prompt_toolkit import Application
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import FormattedTextControl, Layout, Window

from flow.api.models import Task, Volume
from .gpu_formatter import GPUFormatter
from .task_formatter import TaskFormatter
from .terminal_adapter import TerminalAdapter
from .theme_manager import theme_manager

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

    def __init__(
        self,
        items: list[T],
        item_to_selection: Callable[[T], SelectionItem[T]],
        title: str = "Select an item",
        allow_multiple: bool = False,
        show_preview: bool = True,
    ):
        self.items = items
        self.item_to_selection = item_to_selection
        self.title = title
        self.allow_multiple = allow_multiple
        self.show_preview = show_preview
        self.console = theme_manager.create_console()
        self.terminal = TerminalAdapter()

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

            terminal_lines = shutil.get_terminal_size().lines or 24
        except Exception:
            terminal_lines = 24
        # Leave room for title, separators, footer, and spacing between rows
        # Clamp to a sensible range
        self.viewport_size = max(6, min(12, terminal_lines - 10))
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
                "[yellow]Note: Interactive navigation requires prompt_toolkit. Using numbered selection.[/yellow]"
            )
            if os.environ.get("FLOW_DEBUG"):
                self.console.print(f"[red]Missing dependency: {e}[/red]")
            return self._fallback_selection()
        except Exception as e:
            # Fallback on any error - but always show the error in debug mode
            if os.environ.get("FLOW_DEBUG"):
                self.console.print(f"[red]Interactive mode failed: {type(e).__name__}: {e}[/red]")
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
                        "[yellow]Note: Interactive mode unavailable. Using numbered selection.[/yellow]"
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
                self.console.print(f"[red]/dev/tty not accessible: {e}[/red]")

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

        # Exit
        @kb.add("escape")
        @kb.add("c-c")  # Ctrl+C
        def cancel(event):
            # For Ctrl+C, we want to exit the entire program, not just this selector
            if event.key_sequence[0].key == "c-c":
                # Set a special flag to indicate we should exit
                event.app.exit(result=("__KEYBOARD_INTERRUPT__",))
            else:
                # For Escape, just cancel this selection
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
        @kb.add("backspace")
        def handle_backspace(event):
            if self.filter_text:
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

        # Create layout
        def get_formatted_text():
            # Build complete HTML string
            # Use default color for title to match wizard's muted style
            default_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("default"))
            border_color = _map_rich_to_prompt_toolkit_color(
                theme_manager.get_color("muted")
            )  # Use muted for borders
            html = f"<{default_color}><bold>{self.title}</bold></{default_color}>\n"

            # Separator using muted color
            terminal_width = self.terminal.get_terminal_width()
            separator_width = min(terminal_width - 4, 80)  # Cap at 80 chars
            html += f"<{border_color}>{'─' * separator_width}</{border_color}>\n\n"

            # Filter indicator with better spacing
            if self.filter_text:
                muted_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
                html += f"<{muted_color}><i>Filter: {self.filter_text}</i></{muted_color}>\n\n"
            else:
                html += ""

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

                # Format the line using the extracted method, pass index to avoid O(n) lookup
                line = self._format_item_line(item, is_selected, column_widths, i)
                html += line + "\n"

                # Add extra spacing between items for better readability
                if i < viewport_end - 1:
                    html += "\n"

            # Bottom scroll indicator
            if viewport_end < len(self.filtered_items):
                muted_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
                html += f"<{muted_color}>  ↓ {len(self.filtered_items) - viewport_end} more below...</{muted_color}>\n"

            # Professional footer with clear shortcuts
            shortcut_color = _map_rich_to_prompt_toolkit_color(
                theme_manager.get_color("shortcut_key")
            )
            muted_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
            html += "\n"
            html += f"<{muted_color}>{'─' * separator_width}</{muted_color}>\n"
            html += f"<{shortcut_color}><bold>↑↓</bold></{shortcut_color}> navigate   "
            html += f"<{shortcut_color}><bold>↩</bold></{shortcut_color}> select   "
            html += f"<{shortcut_color}><bold>Space</bold></{shortcut_color}> toggle   "
            html += f"<{shortcut_color}><bold>1–9</bold></{shortcut_color}> quick-pick   "
            html += f"<{shortcut_color}><bold>Esc</bold></{shortcut_color}> cancel   "
            html += f"<{shortcut_color}><bold>Ctrl+C</bold></{shortcut_color}> exit"

            return HTML(html)

        # Create application with dynamic height
        def get_height():
            # Adjusted height for extra spacing and improved footer
            # viewport*2 (for spacing) + 8 (title, separator, filter, scroll indicators, footer)
            return (self.viewport_size * 2) + 8

        layout = Layout(
            Window(
                FormattedTextControl(get_formatted_text),
                height=get_height,  # Pass function, not value
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
                        f"[red]Failed to create input: {type(e).__name__}: {e}[/red]"
                    )

                try:
                    test_output = create_output()
                    self.console.print(f"[dim]Output created: {type(test_output)}[/dim]")
                except Exception as e:
                    self.console.print(
                        f"[red]Failed to create output: {type(e).__name__}: {e}[/red]"
                    )

            app = Application(
                layout=layout,
                key_bindings=kb,
                full_screen=False,
                mouse_support=False,  # Disable mouse to avoid conflicts
                refresh_interval=0.5,  # Prevent excessive redraws
                # Try to use simpler output mode
                color_depth=None,  # Auto-detect
                # erase_when_done=True,
            )
        except Exception as e:
            if os.environ.get("FLOW_DEBUG"):
                self.console.print(
                    f"[red]Failed to create Application: {type(e).__name__}: {e}[/red]"
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
                            self.console.print(f"[red]TTY error: {result}[/red]")
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
                    f"[red]Prompt toolkit app.run() failed: {type(e).__name__}: {e}[/red]"
                )

            # Fall back to simple selection
            return self._fallback_selection()

        # Check for special keyboard interrupt flag
        if isinstance(result, tuple) and len(result) == 1 and result[0] == "__KEYBOARD_INTERRUPT__":
            raise KeyboardInterrupt()

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
        gpu_width = 11  # Enough for "H100·080G"
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
                line = f"<{arrow_color}>→</{arrow_color}> {selection_marker} <bold>{item.title}</bold>"
                selection_color = _map_rich_to_prompt_toolkit_color(
                    theme_manager.get_color("success")
                )
                return f"<style bg='{selection_color}'>{line}</style>"
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
                muted_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
                line = f"<{arrow_color}>→</{arrow_color}> {selection_marker} <bold>{name:<{name_width}}</bold>  <{muted_color}>{subtitle}</{muted_color}>"
                selection_color = _map_rich_to_prompt_toolkit_color(
                    theme_manager.get_color("success")
                )
                return f"<style bg='{selection_color}'>{line}</style>"
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
                line = f"<{arrow_color}>→</{arrow_color}> {selection_marker} <bold>{name:<{name_width}}</bold>  <{success_color}>● {item.status}</{success_color}>"
                selection_color = _map_rich_to_prompt_toolkit_color(
                    theme_manager.get_color("success")
                )
                return f"<style bg='{selection_color}'>{line}</style>"
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
            line = f"<{arrow_color}>→</{arrow_color}> {selection_marker} "
            line += f"<bold>{name:<{column_widths['name']}}</bold>"

            if status_display:
                symbol = status_symbol or ""
                text = f"{symbol} {status_display}".strip()
                color_to_use = _map_rich_to_prompt_toolkit_color(status_color_name) if status_color_name else _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
                line += f"<{color_to_use}>{text:<{column_widths['status']}}</{color_to_use}>"
            else:
                line += " " * column_widths["status"]

            # Keep GPU and time info muted for consistency
            muted_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
            line += f"<{muted_color}>{gpu_info:<{column_widths['gpu']}}</{muted_color}>"
            line += f"<{muted_color}>{time_info:<{column_widths['time']}}</{muted_color}>"
            selection_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("success"))
            line = f"<style bg='{selection_color}'>{line}</style>"
        else:
            # Normal line with proper theme colors
            line = "   "
            default_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("default"))
            muted_color = _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))

            line += f"{selection_marker} <{default_color}>{name:<{column_widths['name']}}</{default_color}>"

            if status_display:
                symbol = status_symbol or ""
                text = f"{symbol} {status_display}".strip()
                color_to_use = _map_rich_to_prompt_toolkit_color(status_color_name) if status_color_name else _map_rich_to_prompt_toolkit_color(theme_manager.get_color("muted"))
                line += f"<{color_to_use}>{text:<{column_widths['status']}}</{color_to_use}>"
            else:
                line += " " * column_widths["status"]

            line += f"<{muted_color}>{gpu_info:<{column_widths['gpu']}}</{muted_color}>"
            line += f"<{muted_color}>{time_info:<{column_widths['time']}}</{muted_color}>"

        return line

    def _fallback_selection(self) -> T | None | list[T]:
        """Simple numbered selection for non-interactive environments."""
        if not self.items:
            return None if not self.allow_multiple else []

        # Ensure terminal is in a clean state before fallback
        if os.environ.get("FLOW_DEBUG"):
            self.console.print("[dim]Preparing terminal for fallback selection...[/dim]")

        # Display items with pagination for long lists
        accent_color = theme_manager.get_color("accent")
        border_color = theme_manager.get_color("table.border")
        self.console.print(f"\n[bold {accent_color}]{self.title}[/bold {accent_color}]")
        self.console.print(f"[{border_color}]" + "─" * 60 + f"[/{border_color}]")

        # For long lists, show only first 20 items initially
        display_limit = 20
        total_items = len(self.selection_items)

        if total_items > display_limit:
            self.console.print(f"[dim]Showing first {display_limit} of {total_items} items[/dim]")

        for i, item in enumerate(self.selection_items[:display_limit]):
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

        if total_items > display_limit:
            self.console.print(f"\n[dim]... and {total_items - display_limit} more items[/dim]")
            self.console.print(
                f"[dim]Enter a number 1-{total_items} to select, or 'all' to see all items[/dim]"
            )

        # Get selection
        try:
            # Ensure clean terminal state before prompting
            if os.environ.get("FLOW_DEBUG"):
                self.console.print("[dim]Resetting terminal before prompt...[/dim]")

            if self.allow_multiple:
                # Prompt for input with proper handling
                self.console.print("\nEnter numbers/ranges (e.g. 1 3-5), or 'all'/'none': ", end="")
                sys.stdout.flush()

                # Read from stdin with proper error handling
                try:
                    response = sys.stdin.readline().strip()
                except EOFError:
                    response = ""

                if response.lower() == "all":
                    return [item.value for item in self.selection_items]
                if response.lower() == "none":
                    return []
                if not response:
                    return []
                try:
                    parts = response.split()
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
                        self.selection_items[i].value for i in indices if 0 <= i < len(self.items)
                    ]
                except ValueError:
                    self.console.print("[yellow]Invalid input, returning empty selection[/yellow]")
                    return []
            else:
                # Handle 'all' command to show all items
                while True:
                    # Prompt for input with proper handling
                    self.console.print("\nEnter number, 'all' to list all, or 'q' to cancel: ", end="")
                    sys.stdout.flush()

                    # Read from stdin with proper error handling
                    try:
                        response = sys.stdin.readline().strip()
                    except EOFError:
                        return None

                    if not response:
                        return None

                    if response.lower() == "all":
                        # Show all items
                        self.console.print("\n[bold]All items:[/bold]")
                        for i, item in enumerate(self.selection_items):
                            line = f"  [{i + 1}] {item.title}"
                            if item.subtitle:
                                line += f" {item.subtitle}"
                            self.console.print(line)
                        continue
                    if response.lower() in {"q", "quit"}:
                        return None

                    try:
                        choice = int(response)
                        if 1 <= choice <= len(self.items):
                            return self.selection_items[choice - 1].value
                        else:
                            self.console.print(
                                f"[yellow]Please enter a number between 1 and {len(self.items)}[/yellow]"
                            )
                    except ValueError:
                        self.console.print("[yellow]Please enter a valid number or 'all'[/yellow]")
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

        # Format cost if available
        cost_str = ""
        if hasattr(task, "price_per_hour") and task.price_per_hour:
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
