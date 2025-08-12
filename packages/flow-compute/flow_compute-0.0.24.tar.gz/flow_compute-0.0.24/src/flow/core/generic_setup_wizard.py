"""Generic setup wizard for Flow SDK providers.

Uses the adapter pattern to provide a consistent UI while allowing each
provider to implement its own specific logic.
"""

import time
import os
import shutil
from datetime import datetime
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from flow.cli.commands._init_components.setup_components import select_from_options
from flow.cli.utils.hyperlink_support import hyperlink_support
from flow.cli.utils.interactive_selector import InteractiveSelector, SelectionItem
from flow.cli.utils.mask_utils import mask_sensitive_value, mask_strict_last4
from flow.cli.utils.theme_manager import theme_manager
from flow.cli.utils.visual_constants import (
    SPACING,
    DENSITY,
    format_text,
    get_colors,
    get_panel_styles,
    get_status_display,
)
from flow.core.setup_adapters import FieldType, ProviderSetupAdapter


def _build_selector_header(adapter: ProviderSetupAdapter, existing_config: dict[str, Any]) -> str:
    """Return a concise, non-redundant header for the in-selector context.

    Design goals:
    - Avoid repeating the full status table shown above the selector
    - Surface only what's actionable inside the selector: which required items
      are still missing. When everything is configured, return an empty string
      so the selector dedicates space to the list itself.
    - Keep formatting minimal and terminal-safe.
    """
    try:
        fields = adapter.get_configuration_fields()
        missing_required: list[str] = []
        for f in fields:
            if not getattr(f, "required", False):
                continue
            if existing_config.get(f.name) in (None, ""):
                missing_required.append(f.display_name or f.name.replace("_", " ").title())

        if missing_required:
            # Show a single succinct line listing missing items.
            # Example: "Missing: API Key, Project"
            missing_str = ", ".join(missing_required)
            return f"<b>Missing</b>: {missing_str}"

        # Fully configured — do not repeat details here.
        return ""
    except Exception:
        return ""


def interactive_menu_select(
    options: list,
    title: str = "Select an option",
    default_index: int = 0,
    extra_header_html: str | None = None,
    breadcrumbs: list[str] | None = None,
) -> str | None:
    """Interactive menu selector using arrow keys with graceful fallback.

    Args:
        options: List of tuples (value, display_text, description)
        title: Menu title
        default_index: Index of default selection

    Returns:
        Selected value or None if cancelled
    """
    # Check if we can use interactive mode safely
    import os
    import sys

    # Try to import termios (Unix/Linux/Mac only)
    try:
        import termios

        has_termios = True
    except ImportError:
        has_termios = False
        termios = None

    # Prefer interactive mode when /dev/tty is available even if stdio not TTY
    if os.environ.get("FLOW_NONINTERACTIVE"):
        return _fallback_menu_select(options, title, default_index)

    stdio_is_tty = sys.stdin.isatty() and sys.stdout.isatty()
    term_is_dumb = os.environ.get("TERM") == "dumb"
    ci_env = os.environ.get("CI") is not None

    if not stdio_is_tty or term_is_dumb or ci_env:
        # Try /dev/tty for interactive I/O
        try:
            with open("/dev/tty"):
                # Allow InteractiveSelector to bind to /dev/tty downstream
                os.environ.setdefault("FLOW_FORCE_INTERACTIVE", "true")
        except Exception:
            return _fallback_menu_select(options, title, default_index)

    # Save terminal state for restoration (Unix-like systems only)
    old_term = None
    if has_termios and hasattr(sys.stdin, "fileno"):
        try:
            old_term = termios.tcgetattr(sys.stdin.fileno())
        except:
            old_term = None

    # Try interactive selector directly - most cases should work
    try:
        menu_items = []
        for i, (value, display_text, description) in enumerate(options):
            menu_items.append(
                {"value": value, "name": display_text, "id": value, "description": description}
            )

        def menu_to_selection(item: dict) -> SelectionItem[str]:
            return SelectionItem(
                value=item["value"],
                id=item["id"],
                title=item["name"],
                subtitle=item["description"],
                status="",
            )

        selector = InteractiveSelector(
            items=menu_items,
            item_to_selection=menu_to_selection,
            title=title,
            allow_multiple=False,
            allow_back=True,
            show_preview=False,
            extra_header_html=extra_header_html,
            breadcrumbs=breadcrumbs,
        )

        # Set default selection
        if 0 <= default_index < len(menu_items):
            selector.selected_index = default_index

        result = selector.select()
        # Treat back navigation as cancel to return to previous context
        if result is InteractiveSelector.BACK_SENTINEL:
            return None
        return result

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        if has_termios and old_term and hasattr(sys.stdin, "fileno"):
            try:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, old_term)
            except:
                pass
        # Re-raise to let the parent handler deal with it
        raise
    except Exception:
        # Fall back to numbered menu
        return _fallback_menu_select(options, title, default_index)
    finally:
        # Restore terminal state
        if has_termios and old_term and hasattr(sys.stdin, "fileno"):
            try:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, old_term)
            except:
                pass


def _fallback_menu_select(options: list, title: str, default_index: int = 0) -> str | None:
    """Fallback numbered menu selection."""
    import os
    import re
    import sys

    from rich.console import Console

    console = Console()
    console.print(f"\n[bold]{title}[/bold]")

    # Calculate max width for display text
    max_width = max(len(opt[1]) for opt in options) if options else 30

    for i, (value, display_text, description) in enumerate(options):
        # Avoid duplicate numbering like "1. [1] ..." if label already includes an index token
        if display_text.strip().startswith("[") and "]" in display_text:
            prefix = "  "
        else:
            prefix = f"  {i + 1}. "
        if description:
            console.print(f"{prefix}{display_text:<{max_width}} • {description}")
        else:
            console.print(f"{prefix}{display_text}")

    # Simple numeric input, no terminal control sequences
    # Sanitize terminal state in case a previous interactive session failed mid-flight
    try:
        os.system("stty sane 2>/dev/null || true")
    except Exception:
        pass

    # Patterns for stray escape sequences (e.g., cursor position report "\x1b[27;1R")
    _noise_full_re = re.compile(r"^\x1b\[[0-9;?]*[A-Za-z]$")
    _noise_any_re = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")

    def _readline_sanitized(prompt_text: str) -> str | None:
        """Read a line while ignoring stray terminal escape reports.

        On UNIX terminals, temporarily switch to cbreak and disable ECHO so
        the TTY doesn't echo escape responses like "\x1b[27;1R". We manually
        echo only permitted characters (digits, spaces, comma, dash).
        Falls back to normal input() on any error.
        """
        try:
            import fcntl
            import os as _os
            import select as _select
            import termios
            import tty

            fd = sys.stdin.fileno()
            if not sys.stdin.isatty():
                return input(prompt_text)

            old_attrs = termios.tcgetattr(fd)
            # Disable ECHO to prevent stray CPR sequences from being printed
            new_attrs = termios.tcgetattr(fd)
            new_attrs[3] = new_attrs[3] & ~termios.ECHO  # lflags: disable ECHO
            termios.tcsetattr(fd, termios.TCSANOW, new_attrs)
            # cbreak mode keeps line processing minimal
            tty.setcbreak(fd)

            # Non-blocking reads so we can filter bursts
            old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)

            try:
                sys.stdout.write(prompt_text)
                sys.stdout.flush()
                buf: list[str] = []

                while True:
                    r, _, _ = _select.select([fd], [], [], 0.5)
                    if not r:
                        continue
                    try:
                        ch = _os.read(fd, 1)
                    except BlockingIOError:
                        continue

                    if not ch:
                        return ""  # EOF

                    c = ch.decode(errors="ignore")
                    if c == "\n" or c == "\r":
                        sys.stdout.write("\n")
                        sys.stdout.flush()
                        return "".join(buf)
                    if c == "\x7f":  # backspace
                        if buf:
                            buf.pop()
                            # Erase last char visually
                            sys.stdout.write("\b \b")
                            sys.stdout.flush()
                        continue
                    if c == "\x1b":  # start of an escape sequence; consume until letter
                        seq = c
                        # read the rest non-blocking (bounded)
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
                            if _noise_any_re.search(seq):
                                break
                        # Do not echo ESC sequences
                        continue
                    # Accept only digits and spaces
                    if c.isdigit() or c in {" ", ",", "-"}:
                        buf.append(c)
                        sys.stdout.write(c)
                        sys.stdout.flush()
                        continue
                    # Ignore other control/printable chars
                # unreachable
            finally:
                # Restore flags and attributes
                fcntl.fcntl(fd, fcntl.F_SETFL, old_flags)
                termios.tcsetattr(fd, termios.TCSANOW, old_attrs)
        except Exception:
            try:
                return input(prompt_text)
            except EOFError:
                return None

    while True:
        try:
            default_num = str(default_index + 1)
            prompt = f"Select [1-{len(options)}] ({default_num}): "
            response = _readline_sanitized(prompt)
            if response is None:
                console.print("\n[yellow]Cancelled[/yellow]")
                return None

            response = response.strip()
            # Strip any embedded escape reports (extra safety)
            response = _noise_any_re.sub("", response)

            if not response:
                return options[default_index][0]

            choice_num = int(response)
            if 1 <= choice_num <= len(options):
                return options[choice_num - 1][0]
            console.print("Please enter a valid number")
        except KeyboardInterrupt:
            console.print("\n\n[yellow]Setup cancelled[/yellow]")
            sys.exit(0)
        except ValueError:
            console.print("\n[yellow]Please enter a number[/yellow]")
            continue


def simple_choice_prompt(prompt_text: str, choices: list, default: str = None) -> str:
    """Simple, reliable choice prompt that bypasses Rich completely."""
    import os
    import sys

    # Ensure we're using raw terminal input
    if hasattr(sys.stdin, "fileno"):
        try:
            # Reset terminal settings to ensure clean input
            os.system("stty sane 2>/dev/null || true")
        except:
            pass

    # Use plain print instead of Rich console
    while True:
        if default:
            prompt_display = f"{prompt_text} [{'/'.join(choices)}] ({default}): "
        else:
            prompt_display = f"{prompt_text} [{'/'.join(choices)}]: "

        try:
            # Flush any pending output and use raw input
            sys.stdout.flush()
            sys.stderr.flush()
            response = input(prompt_display).strip()

            if not response and default:
                return default
            if response in choices:
                return response
            print("Please select one of the available options")
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled")
            sys.exit(1)


class AnimatedDots:
    """Minimal animated dots implementation for progress messages."""

    def __init__(self):
        self._counter = 0
        self._dots = ["", ".", "..", "..."]

    def next(self) -> str:
        """Get next dots pattern in sequence."""
        dots = self._dots[self._counter % len(self._dots)]
        self._counter += 1
        return dots


class GenericSetupWizard:
    """Generic setup wizard that works with any provider adapter.

    Provides the beautiful UI and flow from the original AdaptiveSetupWizard
    while delegating provider-specific logic to the adapter.
    """

    @staticmethod
    def _coerce_to_type(field, value):
        """Coerce a value to the appropriate type based on field type.

        Args:
            field: The ConfigField specification
            value: The raw value to coerce

        Returns:
            The value coerced to the appropriate type
        """
        if field.field_type == FieldType.BOOLEAN:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ("true", "yes", "1", "on")
            return bool(value)

        # For other types, return as-is (TEXT, PASSWORD, CHOICE are strings)
        return value

    def __init__(self, console: Console, adapter: ProviderSetupAdapter):
        """Initialize the wizard.

        Args:
            console: Rich console for output
            adapter: Provider-specific setup adapter
        """
        self.console = console
        self.adapter = adapter
        self.config = {}  # New configuration values
        # Track whether we've already shown the demo-mode panel to avoid duplication
        self._shown_demo_panel: bool = False
        # Cache field validation results to avoid repeated network calls
        self._validation_cache: dict[str, tuple[str, bool]] = {}
        # Track fields updated in this session for live highlight
        self._recently_updated: set[str] = set()

    def _prompt_text_with_escape(
        self, label: str, *, is_password: bool = False, default: str | None = None
    ) -> str | None:
        """Prompt for text input where ESC returns None (go back)."""
        try:
            from prompt_toolkit import PromptSession
            from prompt_toolkit.application import create_app_session
            from prompt_toolkit.input import create_input
            from prompt_toolkit.key_binding import KeyBindings
            from prompt_toolkit.output import create_output

            kb = KeyBindings()
            cancelled = {"value": False}

            @kb.add("escape")
            def _(event):  # type: ignore
                cancelled["value"] = True
                event.app.exit(result=None)

            # Some terminals send ESC as Control-[ (same keycode)
            @kb.add("c-[")
            def _(event):  # type: ignore
                cancelled["value"] = True
                event.app.exit(result=None)

            # Provide an additional universal cancel
            @kb.add("c-g")
            def _(event):  # type: ignore
                cancelled["value"] = True
                event.app.exit(result=None)

            # Create explicit input/output to avoid TTY autodetect issues
            pt_input = create_input()
            pt_output = create_output()
            session = PromptSession(input=pt_input, output=pt_output)
            prompt_text = f"\n{label}: "
            # Ensure we have an application session so key bindings are active reliably
            with create_app_session(input=pt_input, output=pt_output):
                value = session.prompt(
                    prompt_text,
                    is_password=is_password,
                    default=(default or ""),
                    key_bindings=kb,
                )
            if cancelled["value"]:
                return None
            return value
        except Exception:
            # Robust fallback that captures ESC and avoids markup artifacts.
            import sys as _sys
            import select as _select
            import os as _os
            
            def _drain_stdin():
                try:
                    if not _sys.stdin.isatty():
                        return
                    r, _, _ = _select.select([_sys.stdin], [], [], 0)
                    while r:
                        try:
                            _os.read(_sys.stdin.fileno(), 1024)
                        except Exception:
                            break
                        r, _, _ = _select.select([_sys.stdin], [], [], 0)
                except Exception:
                    pass

            # If not a TTY, fall back to plain input() with 'back' sentinel.
            if not _sys.stdin.isatty():
                try:
                    prompt_display = f"\n{label}: "
                    if default:
                        prompt_display = f"\n{label} ({default}): "
                    _drain_stdin()
                    resp = input(prompt_display)
                    if resp is None:
                        return None
                    resp = resp.strip()
                    if resp.lower() in {"back", "b"}:
                        return None
                    if not resp and default is not None:
                        return default
                    return resp
                except Exception:
                    return None

            # TTY: implement a tiny line editor that treats ESC as back
            try:
                import termios, tty

                fd = _sys.stdin.fileno()
                old_attrs = termios.tcgetattr(fd)
                new_attrs = termios.tcgetattr(fd)
                if is_password:
                    # Disable echo for password-like input
                    new_attrs[3] = new_attrs[3] & ~termios.ECHO
                termios.tcsetattr(fd, termios.TCSANOW, new_attrs)
                tty.setcbreak(fd)

                _drain_stdin()
                prompt_display = f"\n{label}: "
                if default:
                    prompt_display = f"\n{label} ({default}): "
                _sys.stdout.write(prompt_display)
                _sys.stdout.flush()

                buf: list[str] = []
                while True:
                    ch = _os.read(fd, 1)
                    if not ch:
                        break
                    c = ch.decode(errors="ignore")
                    if c in ("\n", "\r"):
                        _sys.stdout.write("\n")
                        _sys.stdout.flush()
                        break
                    if c == "\x1b":  # ESC → back
                        # Print nothing and return to previous menu
                        _sys.stdout.write("\n")
                        _sys.stdout.flush()
                        buf = []
                        return None
                    if c == "\x7f":  # Backspace
                        if buf:
                            buf.pop()
                            if not is_password:
                                _sys.stdout.write("\b \b")
                                _sys.stdout.flush()
                        continue
                    # Ignore control characters
                    if ord(c) < 32:
                        continue
                    buf.append(c)
                    if not is_password:
                        _sys.stdout.write(c)
                        _sys.stdout.flush()

                val = "".join(buf).strip()
                if not val and default is not None:
                    return default
                return val
            except Exception:
                return None
            finally:
                try:
                    termios.tcsetattr(fd, termios.TCSANOW, old_attrs)  # type: ignore[name-defined]
                except Exception:
                    pass

    def _confirm_with_escape(self, question: str, default: bool = True) -> bool | None:
        """Confirm where ESC returns None (go back)."""
        try:
            from prompt_toolkit import PromptSession
            from prompt_toolkit.application import create_app_session
            from prompt_toolkit.input import create_input
            from prompt_toolkit.key_binding import KeyBindings
            from prompt_toolkit.output import create_output

            kb = KeyBindings()
            cancelled = {"value": False}

            @kb.add("escape")
            def _(event):  # type: ignore
                cancelled["value"] = True
                event.app.exit(result=None)

            @kb.add("c-[")
            def _(event):  # type: ignore
                cancelled["value"] = True
                event.app.exit(result=None)

            @kb.add("c-g")
            def _(event):  # type: ignore
                cancelled["value"] = True
                event.app.exit(result=None)

            pt_input = create_input()
            pt_output = create_output()
            session = PromptSession(input=pt_input, output=pt_output)
            suffix = "[Y/n]" if default else "[y/N]"
            prompt_text = f"\n{question} {suffix} "
            with create_app_session(input=pt_input, output=pt_output):
                value = session.prompt(prompt_text, key_bindings=kb)
            if cancelled["value"]:
                return None
            if not value.strip():
                return default
            v = value.strip().lower()
            if v in {"y", "yes"}:
                return True
            if v in {"n", "no"}:
                return False
            return default
        except Exception:
            # Fallback without prompt_toolkit: accept 'back' or 'b' to return
            # Strip any Rich markup in the question to avoid visual artifacts
            import re as _re
            import sys as _sys
            import select as _select
            import os as _os
            
            def _strip_markup(text: str) -> str:
                try:
                    return _re.sub(r"\[/?.*?\]", "", text)
                except Exception:
                    return text

            def _drain_stdin():
                try:
                    if not _sys.stdin.isatty():
                        return
                    # Non-blocking drain of any leftover bytes
                    r, _, _ = _select.select([_sys.stdin], [], [], 0)
                    while r:
                        try:
                            _os.read(_sys.stdin.fileno(), 1024)
                        except Exception:
                            break
                        r, _, _ = _select.select([_sys.stdin], [], [], 0)
                except Exception:
                    pass

            try:
                suffix = "[Y/n]" if default else "[y/N]"
                clean_q = _strip_markup(question).strip() or "Are you sure?"
                while True:
                    _drain_stdin()  # ensure no pending input carries into the next prompt
                    try:
                        resp = (
                            input(f"\n{clean_q} {suffix} (type 'back' to return): ")
                            .strip()
                            .lower()
                        )
                    except (EOFError, KeyboardInterrupt):
                        return default

                    if not resp:
                        return default
                    if resp in {"y", "yes"}:
                        return True
                    if resp in {"n", "no"}:
                        return False
                    if resp in {"back", "b"}:
                        # Treat as an immediate return to the previous menu
                        _drain_stdin()
                        return None
                    print("Please enter Y, N, or 'back'")
            except Exception:
                return default

    def run(self) -> bool:
        """Run the setup wizard.

        Returns:
            True if setup completed successfully
        """
        import signal
        import sys

        # Set up global keyboard interrupt handler
        def keyboard_interrupt_handler(signum, frame):
            self.console.print("\n\n[yellow]Setup cancelled[/yellow]")
            # Reset terminal to ensure clean exit
            try:
                import os

                os.system("stty sane 2>/dev/null || true")
            except:
                pass
            sys.exit(0)

        # Install the handler
        old_handler = signal.signal(signal.SIGINT, keyboard_interrupt_handler)

        try:
            self._show_welcome()

            # Opportunistic prefetch for fast menus (projects, ssh keys)
            try:
                from flow.cli.utils.prefetch import prefetch_for_command

                # Pretend like we're in 'init' to reuse prefetch plan
                prefetch_for_command(["flow", "init"])
            except Exception:
                pass

            # Detect existing configuration
            existing_config = self.adapter.detect_existing_config()

            # Show configuration status
            if not self._show_configuration_status(existing_config):
                return False

            # Check if fully configured
            if self._is_fully_configured(existing_config):
                # Allow reconfiguration and persist any changes made
                proceed = self._handle_fully_configured(existing_config)
                if not proceed:
                    return False
                try:
                    if self.config:
                        final_config = existing_config.copy()
                        final_config.update(self.config)
                        if not self.adapter.save_configuration(final_config):
                            self.console.print("\n[red]Failed to save configuration[/red]")
                            return False
                    return True
                except Exception:
                    # Non-fatal; allow exit
                    return True
            else:
                # Not fully configured - configure missing items
                if not self._configure_missing_items(existing_config):
                    return False

                # Save configuration
                final_config = existing_config.copy()
                final_config.update(self.config)

                if not self.adapter.save_configuration(final_config):
                    self.console.print("\n[red]Failed to save configuration[/red]")
                    return False

                # Final verification
                if self._verify_configuration(final_config):
                    self._show_completion()
                    return True
                else:
                    self.console.print(
                        "\n[yellow]Setup completed but verification failed. Check your settings.[/yellow]"
                    )
                    return False
        finally:
            # Restore original handler
            signal.signal(signal.SIGINT, old_handler)

    def _show_welcome(self):
        """Display setup wizard welcome screen."""
        self.console.clear()

        # Enhanced welcome using visual constants
        colors = get_colors()
        panel_styles = get_panel_styles()
        title, features = self.adapter.get_welcome_message()
        welcome_content = (
            f"{format_text('title', 'Flow SDK Setup')}\n\n"
            f"{format_text('muted', f'Configure your environment for GPU workloads on {self.adapter.get_provider_name().upper()}')}\n\n"
            f"{format_text('body', 'This wizard will:')}\n"
        )

        for feature in features:
            welcome_content += f"  [{colors['primary']}]◦[/{colors['primary']}] {feature}\n"

        self.console.print(
            Panel(
                welcome_content.rstrip(),
                title=f"{format_text('title', '⚡ Flow')}",
                title_align=panel_styles["main"]["title_align"],
                border_style=panel_styles["main"]["border_style"],
                padding=panel_styles["main"]["padding"],
                width=SPACING["panel_width"],
            )
        )
        self.console.print()

        # If running the mock provider, show a single standardized demo-mode panel
        try:
            if str(self.adapter.get_provider_name()).lower() == "mock":
                panel = self._create_demo_mode_panel()
                self.console.print(panel)
                self.console.print()
                # Mark that we have already shown demo-mode guidance
                self._shown_demo_panel = True
        except Exception:
            # Non-fatal; continue without the info panel
            pass

    def _show_configuration_status(self, existing_config: dict[str, Any]) -> bool:
        """Display current configuration status in a table.

        Args:
            existing_config: Dictionary of existing configuration

        Returns:
            Always True
        """
        self.console.print()
        panel_styles = get_panel_styles()
        try:
            # Clamp panel width so it doesn't stretch excessively on very wide terminals
            from flow.cli.utils.terminal_adapter import TerminalAdapter as _TA

            term_w = _TA.get_terminal_width()
            panel_w = min(term_w - 4, max(56, int(term_w * 0.6)))
        except Exception:
            panel_w = SPACING.get("panel_width", 60)

        self.console.print(
            Panel(
                self._build_status_content(existing_config),
                title=f"{format_text('title', 'Configuration Status')}",
                title_align=panel_styles["secondary"]["title_align"],
                border_style=panel_styles["secondary"]["border_style"],
                padding=panel_styles["secondary"]["padding"],
                width=panel_w,
            )
        )

        # Add spacing before contextual guidance only if it won't push content off-screen
        try:
            import shutil as _shutil
            term_lines = _shutil.get_terminal_size().lines or 24
            if term_lines >= 22:
                self.console.print()
        except Exception:
            pass

        # If in demo/mock setup, show a compact panel with accents and bullets
        try:
            if str(self.adapter.get_provider_name()).lower() == "mock" and not getattr(self, "_shown_demo_panel", False):
                # Show the demo-mode card only when there are missing required items,
                # otherwise it's redundant with the status table.
                required_missing = any(
                    (f.required and not existing_config.get(f.name))
                    for f in self.adapter.get_configuration_fields()
                )
                if required_missing:
                    self.console.print()
                    self.console.print(self._create_demo_mode_panel())
                # Avoid re-showing later in the flow
                self._shown_demo_panel = True
        except Exception:
            pass

        # Contextual guidance beneath the status table (non-demo only to avoid repetition)
        try:
            if str(self.adapter.get_provider_name()).lower() != "mock":
                from flow.links import WebLinks
                self.console.print(
                    f"{format_text('muted', 'About SSH access:')} "
                    f"{format_text('body', 'Your Default SSH Key lets you securely log into instances. ')}"
                    f"{format_text('body', 'Choose an existing key in your Mithril account or select Auto‑generate to have a fresh key per instance (recommended).')}\n"
                    f"{format_text('muted', 'Manage keys:')} [link]{WebLinks.ssh_keys()}[/link]"
                )
        except Exception:
            pass

        # When showing the main configuration menu next, render its header context inside the selector
        self._last_status_header = _build_selector_header(self.adapter, existing_config)
        return True

    def _build_status_content(self, existing_config: dict[str, Any]) -> Table:
        """Build the configuration status content string."""
        colors = get_colors()
        fields = self.adapter.get_configuration_fields()
        # Use global density for subtle row height tuning
        row_vpad = 1 if getattr(DENSITY, "table_row_vpad", 0) > 0 else 0
        table = Table(show_header=True, box=None, padding=(row_vpad, 2))
        table.add_column("Component", style=colors["accent"], min_width=15, justify="left")
        table.add_column("Status", min_width=12, justify="left")
        table.add_column("Value", style=colors["muted"], min_width=18, justify="left")
        table.add_column("Source", style=colors["muted"], min_width=8, justify="left")

        # Sort items by importance: required first, then optional
        required_fields = [f for f in fields if f.required]
        optional_fields = [f for f in fields if not f.required]

        numbered_fields = required_fields + optional_fields
        for idx, field in enumerate(numbered_fields):
            # Prefer newly provided values in this session
            value = self.config.get(field.name, existing_config.get(field.name))

            # Determine status, with special handling for verified/invalid values
            status_display = None
            display_value = "[dim]—[/dim]"
            source_display = "[dim]—[/dim]"

            if value:
                # API key: show Verified only if validated; Invalid if format/API check fails
                if field.name == "api_key":
                    cache = self._validation_cache.get("api_key")
                    is_valid = False
                    try:
                        if not cache or cache[0] != str(value):
                            vr = self.adapter.validate_field("api_key", str(value), None)
                            is_valid = bool(getattr(vr, "is_valid", False))
                            self._validation_cache["api_key"] = (str(value), is_valid)
                        else:
                            is_valid = cache[1]
                    except Exception:
                        is_valid = False
                    if is_valid:
                        status_display = get_status_display("configured", "Verified")
                    else:
                        status_display = get_status_display("invalid", "Invalid")
                    # Mask value when present
                    try:
                        display_value = mask_strict_last4(str(value))
                    except Exception:
                        display_value = "••••"
                    source_display = "detected"

                # SSH key: treat _auto_ as configured; otherwise verify presence when possible
                elif field.name == "default_ssh_key":
                    key_id = str(value)
                    if key_id.strip() == "_auto_":
                        status_display = get_status_display("configured", "Configured")
                        display_value = "Auto‑generate per instance"
                        source_display = "detected"
                    else:
                        # Verify against API choices if api_key + project are available
                        context = {
                            "api_key": self.config.get("api_key", existing_config.get("api_key")),
                            "project": self.config.get("project", existing_config.get("project")),
                        }
                        found = None
                        try:
                            if context["api_key"] and context["project"]:
                                choices = self.adapter.get_dynamic_choices("default_ssh_key", context)
                                # Choices are strings like "id|name|..."; match on id
                                for c in choices:
                                    if c.split("|")[0] == key_id:
                                        found = c
                                        break
                        except Exception:
                            found = None
                        if found:
                            status_display = get_status_display("configured", "Configured")
                            # Prefer readable name
                            parts = found.split("|")
                            display_value = parts[1] if len(parts) > 1 else key_id
                            source_display = "detected"
                        else:
                            status_display = get_status_display("invalid", "Unknown")
                            display_value = key_id
                            source_display = "detected"

                else:
                    # Generic configured handling
                    status_display = get_status_display("configured", "Configured")
                    # Get display value
                    if field.mask_display and value:
                        display_value = mask_strict_last4(value)
                    else:
                        # Friendly display for SSH key auto-generation sentinel (kept for safety)
                        if (
                            field.name == "default_ssh_key"
                            and isinstance(value, str)
                            and value.strip() == "_auto_"
                        ):
                            display_value = "Auto‑generate per instance (recommended)"
                        else:
                            display_value = str(value)
                    source_display = "detected"

            else:
                if field.required:
                    status_display = get_status_display("missing", "Missing")
                else:
                    status_display = get_status_display("optional", "Optional")
                display_value = "[dim]—[/dim]"
                source_display = "[dim]—[/dim]"

            display_name = field.display_name or field.name.replace("_", " ").title()

            # Highlight values updated in this session for visibility
            if field.name in getattr(self, "_recently_updated", set()) and display_value and "[dim]" not in display_value:
                try:
                    success_color = theme_manager.get_color("success")
                    display_value = f"[{success_color}]{display_value}[/{success_color}]"
                except Exception:
                    pass
            table.add_row(display_name, status_display, display_value, source_display)

        return table

    def _is_fully_configured(self, existing_config: dict[str, Any]) -> bool:
        """Check if all required components are configured."""
        fields = self.adapter.get_configuration_fields()
        required_fields = [f for f in fields if f.required]
        # Use effective checks (format-level) to avoid false positives from stale values
        for f in required_fields:
            if not self._is_field_effectively_configured(f, existing_config):
                return False
        return True

    def _is_field_effectively_configured(self, field, existing_config: dict[str, Any]) -> bool:
        """Conservative readiness check that avoids network calls.

        Treats placeholders and obviously invalid formats as not configured to
        prevent defaulting to 'Done' when values are stale or demo.
        """
        value = self.config.get(field.name) or existing_config.get(field.name)
        if value in (None, ""):
            return False
        name = field.name
        try:
            if name == "api_key":
                v = str(value)
                if v.startswith("YOUR_"):
                    return False
                return v.startswith("fkey_") and len(v) >= 20
            if name == "project":
                v = str(value).strip()
                if v.startswith("YOUR_"):
                    return False
                return len(v) > 0
            if name == "default_ssh_key":
                v = str(value).strip()
                return v == "_auto_" or v.startswith("sshkey_")
        except Exception:
            return False
        return True

    def _handle_fully_configured(self, existing_config: dict[str, Any]) -> bool:
        """Handle case where all required items are already configured."""
        self.console.print(
            f"\n{get_status_display('configured', 'All required components are configured')}"
        )

        # Interactive menu options (avoid embedding numeric prefixes in labels)
        menu_options = [
            ("1", "Exit without verification", ""),
            ("2", "Verify configuration and exit", ""),
            ("3", "Reconfigure components", ""),
        ]

        self.console.print()  # Add spacing
        # Build header from latest status
        header = _build_selector_header(self.adapter, existing_config)
        action = interactive_menu_select(
            options=menu_options,
            title="What would you like to do?",
            default_index=0,  # Default to first option (exit)
            extra_header_html=header,
            breadcrumbs=["Flow Setup", "Complete"],
        )

        if action == "1":
            self.console.print("\n[dim]Exiting without verification.[/dim]")
            return True
        elif action == "2":
            success, error = self.adapter.verify_configuration(existing_config)
            if success:
                success_color = theme_manager.get_color("success")
                self.console.print(
                    f"\n[{success_color}]✓ Configuration verified successfully![/{success_color}]"
                )
                return True
            else:
                self.console.print(f"\n[yellow]Verification failed: {error}[/yellow]")
                return self._configure_missing_items(existing_config)
        elif action == "3":
            return self._configure_missing_items(existing_config)

        return True

    def _configure_missing_items(self, existing_config: dict[str, Any]) -> bool:
        """Configure missing or selected items."""
        fields = self.adapter.get_configuration_fields()

        # Avoid vertical creep and repeated warnings when returning to the menu.
        spacer_printed = False
        # Track if we've already shown the empty-choices hint for a field in this session
        # Store on the instance so nested calls (e.g., _configure_field) can access it
        self._shown_empty_choice_hint = set()

        while True:
            # Always refresh the screen with the latest status to avoid stale hints
            try:
                self.console.clear()
            except Exception:
                pass
            try:
                # After we change sensitive or dependent fields, re-detect to avoid stale demo values
                # Prefer adapter detection unless we are mid-edit with fresh self.config values
                detected = self.adapter.detect_existing_config()
                current_state = {**detected, **self.config}
                self._show_configuration_status(current_state)
                # Update existing_config with detected so the loop keeps latest truth
                existing_config.update(detected)
            except Exception:
                # Non-fatal UI refresh issues should never block configuration flow
                pass

            # Build interactive menu options
            menu_options = []
            choice_map = {}
            choice_num = 1

            for field in fields:
                existing_value = existing_config.get(field.name)
                field_title = field.display_name or field.name.replace("_", " ").title()

                if existing_value:
                    if field.mask_display:
                        display_val = mask_strict_last4(existing_value)
                    else:
                        display_val = existing_value
                    display_text = f"[{choice_num}] Reconfigure {field_title}"
                    description = ""
                else:
                    display_text = f"[{choice_num}] Configure {field_title}"
                    # If this field depends on others, surface a concise hint
                    try:
                        depends_on = getattr(field, "depends_on", None) or []
                        missing = [d for d in depends_on if not (existing_config.get(d) or self.config.get(d))]
                        # Strict disable: mark disabled if any dependency missing
                        if missing:
                            description = f"Requires: {', '.join(m.replace('_', ' ').title() for m in missing)}"
                            # Render disabled in title, and skip mapping to a selectable choice
                            menu_options.append((f"disabled_{choice_num}", f"[{choice_num}] {field_title} (disabled)", description))
                            choice_num += 1
                            continue
                        else:
                            description = ""
                    except Exception:
                        description = ""

                menu_options.append((str(choice_num), display_text, description))
                choice_map[str(choice_num)] = field.name
                choice_num += 1

            # Add exit option
            menu_options.append(("done", f"[{choice_num}] Done (save and exit)", ""))

            if not spacer_printed:
                self.console.print()  # Add spacing once
                spacer_printed = True
            # Choose sensible default: first missing field, otherwise "Done"
            try:
                # Default to first selectable, missing field. If none, default to Done.
                default_index = 0
                # Build a mapping from field order to menu index for enabled entries
                field_to_menu_index: dict[str, int] = {}
                for mi, (val, title, _desc) in enumerate(menu_options):
                    if val.startswith("disabled_"):
                        continue
                    # Extract field number from title pattern "[n] <name>"
                    # We rely on choice_map for correctness instead of parsing title
                    pass
                # Use choice_map to map first missing field to menu index
                first_missing_menu_index = None
                for idx, field in enumerate(fields):
                    if not self._is_field_effectively_configured(field, existing_config):
                        # Find the menu index whose value equals this choice number (as string)
                        # choice_map maps choice number string -> field.name
                        # We need the inverse: find key for field.name
                        chosen_key = None
                        for k, v in choice_map.items():
                            if v == field.name:
                                chosen_key = k
                                break
                        if chosen_key is not None:
                            # Find its position in menu_options
                            for mi, (val, _t, _d) in enumerate(menu_options):
                                if val == chosen_key:
                                    first_missing_menu_index = mi
                                    break
                        break
                if first_missing_menu_index is not None:
                    default_index = first_missing_menu_index
                else:
                    # All effectively configured; default to Done (last row)
                    default_index = len(menu_options) - 1
            except Exception:
                default_index = 0

            # Pass last status header into the selector so users keep context in fullscreen
            header = getattr(self, "_last_status_header", None)
            choice = interactive_menu_select(
                options=menu_options,
                title="Configuration Menu",
                default_index=default_index,
                extra_header_html=header,
                breadcrumbs=["Flow Setup", "Configuration"],
            )

            # Handle ESC/back (returns None) - simply return to the menu without
            # any extra confirmation to match user expectations for "Back".
            if choice is None:
                # Re-render the menu in place without adding extra spacing
                continue

            if choice == "done":
                # Check if required items are configured
                required_fields = [f for f in fields if f.required]
                missing = []
                for field in required_fields:
                    if not existing_config.get(field.name) and not self.config.get(field.name):
                        missing.append(field.display_name or field.name.replace("_", " ").title())

                if missing:
                    self.console.print(
                        f"\n[yellow]Warning: Required items not configured: {', '.join(missing)}[/yellow]"
                    )
                    exit_anyway = self._confirm_with_escape("Exit anyway?", default=False)
                    if not exit_anyway:
                        continue
                return True

            field_name = choice_map.get(choice)
            if field_name:
                if self._configure_field(field_name, existing_config):
                    # Update existing_config for dependency purposes
                    existing_config[field_name] = self.config[field_name]
                # If field configuration was cancelled (returned False),
                # just continue to show menu again

        return True

    def _configure_field(self, field_name: str, context: dict[str, Any]) -> bool:
        """Configure a single field."""
        fields = {f.name: f for f in self.adapter.get_configuration_fields()}
        field = fields[field_name]

        display_name = field.display_name or field.name.replace("_", " ").title()
        # For non-choice fields, show a Rich header above the prompt. For CHOICE fields,
        # the interactive selector will render its own header and breadcrumbs to avoid
        # duplicate section headers on screen.
        if field.field_type != FieldType.CHOICE:
            try:
                self.console.clear()
            except Exception:
                pass
            self.console.print(f"\n[bold]Flow Setup › Configuration › {display_name}[/bold]")
            self.console.print("─" * 50)
            self.console.print("[dim]ESC to go back • Ctrl+C to exit[/dim]")

            if field.help_text:
                self.console.print(f"[dim]{field.help_text}[/dim]")

            if field.help_url:
                # Render the URL with tasteful accent color and keep it clickable
                # in supported terminals via OSC 8 hyperlinks. Do not wrap an OSC 8
                # hyperlink in Rich's [link] tag to avoid nested/duplicated links.
                try:
                    link_text = hyperlink_support.create_link(field.help_url, field.help_url)
                except Exception:
                    link_text = field.help_url
                self.console.print(f"[dim]More info: [/dim]{link_text}")

        # Get field value based on type
        if field.field_type == FieldType.CHOICE:
            if field.dynamic_choices:
                # Get dynamic choices
                # Try prefetch cache first for snappy UX
                choice_strings = None
                try:
                    if field_name == "project":
                        from flow.cli.utils.prefetch import get_cached

                        cached_projects = get_cached("projects")
                        if isinstance(cached_projects, list) and cached_projects:
                            # Normalize projects to simple names
                            choice_strings = [p.get("name") for p in cached_projects if isinstance(p, dict) and p.get("name")]
                    elif field_name == "default_ssh_key":
                        from flow.cli.utils.prefetch import get_cached

                        cached_keys = get_cached("ssh_keys")
                        if isinstance(cached_keys, list) and cached_keys:
                            # Normalize to id|name|created|fingerprint strings for display
                            norm = []
                            for k in cached_keys:
                                try:
                                    fid = k.get("id") or k.get("fid")
                                    name = k.get("name") or "Unnamed"
                                    created = (k.get("created_at") or "")
                                    fprint = (k.get("fingerprint") or "")
                                    if fid:
                                        norm.append(f"{fid}|{name}|{created}|{fprint}")
                                except Exception:
                                    continue
                            if norm:
                                choice_strings = [
                                    "_auto_|Platform auto-generates per instance (recommended)",
                                    "GENERATE_SERVER|Generate new SSH key on Mithril platform",
                                    "GENERATE_LOCAL|Generate new SSH key locally with ssh-keygen",
                                ] + norm
                except Exception:
                    choice_strings = None

                if choice_strings is None:
                    choice_strings = self.adapter.get_dynamic_choices(
                        field_name, {**context, **self.config}
                    )
                if not choice_strings:
                    # If dynamic choices are empty, provide a clearer, non-repeating hint
                    hint = getattr(field, "empty_choices_hint", None)
                    depends_on = getattr(field, "depends_on", None) or []
                    missing = [d for d in depends_on if not (context.get(d) or self.config.get(d))]
                    if hint and field_name not in getattr(self, "_shown_empty_choice_hint", set()):
                        try:
                            from rich.panel import Panel as _Panel
                            warn_color = theme_manager.get_color("warning")
                            if missing:
                                missing_str = ", ".join(m.replace("_", " ").title() for m in missing)
                                text = f"{hint} (missing: {missing_str})."
                            else:
                                text = hint
                            self.console.print(_Panel(text, border_style=warn_color))
                        except Exception:
                            if missing:
                                missing_str = ", ".join(m.replace("_", " ").title() for m in missing)
                                self.console.print(f"\n[yellow]{hint} (missing: {missing_str}).[/yellow]")
                            else:
                                self.console.print(f"\n[yellow]{hint}[/yellow]")
                        try:
                            self._shown_empty_choice_hint.add(field_name)
                        except Exception:
                            pass
                    else:
                        # Fall back to the original generic message, but only once per field per session
                        if field_name not in getattr(self, "_shown_empty_choice_hint", set()):
                            try:
                                from rich.panel import Panel as _Panel
                                warn_color = theme_manager.get_color("warning")
                                self.console.print(_Panel("No options available. Skipping this field.", border_style=warn_color))
                            except Exception:
                                self.console.print("\n[yellow]No options available. Skipping this field.[/yellow]")
                            try:
                                self._shown_empty_choice_hint.add(field_name)
                            except Exception:
                                pass
                    return False

                # Convert to dictionaries for intelligent selection
                choices = []
                is_ssh_key_selection = field_name == "default_ssh_key"

                for choice_str in choice_strings:
                    if "|" in choice_str:
                        parts = choice_str.split("|")
                        if len(parts) >= 4 and is_ssh_key_selection:
                            # Enhanced SSH key format: "id|name|created_at|fingerprint"
                            id_part = parts[0]
                            name_part = parts[1]
                            created_at = parts[2]
                            fingerprint = parts[3] if len(parts) > 3 else ""

                            # Format created date
                            created_display = ""
                            if created_at and created_at.strip():
                                try:
                                    # Handle ISO format with Z suffix
                                    clean_date = created_at.replace("Z", "+00:00").split("T")[0]
                                    if len(clean_date) >= 10:  # YYYY-MM-DD
                                        created_display = clean_date[:10]
                                    else:
                                        dt = datetime.fromisoformat(
                                            created_at.replace("Z", "+00:00")
                                        )
                                        created_display = dt.strftime("%Y-%m-%d")
                                except:
                                    created_display = ""

                            choices.append(
                                {
                                    "name": name_part,
                                    "id": id_part,
                                    "display": name_part,
                                    "created_at": created_display,
                                    "fingerprint": fingerprint,
                                }
                            )
                        else:
                            # Simple format: "id|name"
                            id_part = parts[0]
                            name_part = parts[1] if len(parts) > 1 else id_part
                            choices.append({"name": name_part, "id": id_part, "display": name_part})
                    elif "(" in choice_str and choice_str.endswith(")"):
                        # Legacy format: "name (id)" - extract both
                        name_part = choice_str.split("(")[0].strip()
                        id_part = choice_str.split("(")[-1].rstrip(")")
                        choices.append({"name": name_part, "id": id_part, "display": choice_str})
                    else:
                        # Simple string choice
                        choices.append(
                            {"name": choice_str, "id": choice_str, "display": choice_str}
                        )

                # Use intelligent selection
                # Compose compact header for inline selector
                header_parts: list[str] = []
                last_status = getattr(self, "_last_status_header", None)
                if last_status:
                    header_parts.append(last_status)
                if field.help_text:
                    header_parts.append(field.help_text)
                if field.help_url:
                    header_parts.append(f"More info: {field.help_url}")
                # Add concise, actionable tip for SSH key uploads right where choices are shown
                if is_ssh_key_selection:
                    header_parts.append(
                        "Tip: Upload from this machine:\n  flow ssh-keys upload ~/.ssh/id_ed25519.pub"
                    )
                    from flow.links import WebLinks
                    header_parts.append(f"Manage keys: {WebLinks.ssh_keys()}")

                selected = select_from_options(
                    console=self.console,
                    options=choices,
                    name_key="display",
                    id_key="id",
                    title=f"Select {field.display_name or field.name.replace('_', ' ').title()}",
                    show_ssh_table=is_ssh_key_selection,
                    extra_header_html=("\n\n".join(header_parts) if header_parts else None),
                    breadcrumbs=["Flow Setup", "Configuration", display_name],
                    preferred_viewport_size=5,
                )

                if selected:
                    value = selected["id"]
                else:
                    return False
            else:
                # Static choices - convert to dict format
                choice_strings = field.choices or []
                choices = [{"name": choice, "id": choice} for choice in choice_strings]

                # Compose compact header for inline selector
                header_parts: list[str] = []
                last_status = getattr(self, "_last_status_header", None)
                if last_status:
                    header_parts.append(last_status)
                if field.help_text:
                    header_parts.append(field.help_text)
                if field.help_url:
                    header_parts.append(f"More info: {field.help_url}")

                selected = select_from_options(
                    console=self.console,
                    options=choices,
                    name_key="name",
                    id_key="id",
                    title=f"Select {field.display_name or field.name.replace('_', ' ').title()}",
                    extra_header_html=("\n\n".join(header_parts) if header_parts else None),
                    breadcrumbs=["Flow Setup", "Configuration", display_name],
                    preferred_viewport_size=5,
                )

                if selected:
                    value = selected["id"]
                else:
                    return False

        elif field.field_type == FieldType.PASSWORD:
            value = self._prompt_text_with_escape(display_name, is_password=True)
            if value is None:
                # Silent return to menu for a smoother experience
                return False
            # Provide immediate masked feedback after entry
            try:
                if isinstance(value, str) and value:
                    preview_masked = mask_strict_last4(value)
                    colors = get_colors()
                    check = theme_manager.get_color("success")
                    # Show masked feedback synchronously so users see paste worked
                    self.console.print(f"[{colors['muted']}]Received:[/{colors['muted']}] {preview_masked}")
            except Exception:
                pass
        elif field.field_type == FieldType.BOOLEAN:
            confirm = self._confirm_with_escape(f"\n{display_name}", default=bool(field.default))
            if confirm is None:
                return False
            value = confirm
        else:  # TEXT
            value = self._prompt_text_with_escape(
                display_name, is_password=False, default=field.default
            )
            if value is None:
                return False

        # Validate the field with full context (pass string for adapter compatibility)
        validation_result = None
        # For API key (password), show a spinner to make verification latency explicit
        if field.field_type == FieldType.PASSWORD and field.name == "api_key":
            # Use centralized animated progress for DRY and consistent UX
            try:
                from flow.cli.utils.animated_progress import AnimatedEllipsisProgress as _Anim
                with _Anim(self.console, "Verifying API key", transient=True, start_immediately=True):
                    validation_result = self.adapter.validate_field(
                        field_name, str(value), {**context, **self.config}
                    )
            except Exception:
                validation_result = self.adapter.validate_field(
                    field_name, str(value), {**context, **self.config}
                )
        else:
            validation_result = self.adapter.validate_field(
                field_name, str(value), {**context, **self.config}
            )

        if validation_result.is_valid:
            # Use processed_value if available (e.g., for SSH key generation)
            if (
                hasattr(validation_result, "processed_value")
                and validation_result.processed_value is not None
            ):
                # Store processed value with proper type
                self.config[field_name] = self._coerce_to_type(
                    field, validation_result.processed_value
                )
            else:
                # Store canonical type based on field type
                self.config[field_name] = self._coerce_to_type(field, value)

            # Show confirmation with masked value for sensitive fields
            if validation_result.display_value:
                display_value = validation_result.display_value
            elif field.mask_display:
                # Mask sensitive values like API keys
                display_value = mask_strict_last4(str(self.config[field_name]))
            else:
                display_value = str(self.config[field_name])

            success_color = theme_manager.get_color("success")
            self.console.print(
                f"[{success_color}]✓[/{success_color}] {display_name}: {display_value}"
            )
            # Track recently updated for live status highlight
            try:
                self._recently_updated.add(field_name)
            except Exception:
                pass
            # Export to process env so background prefetch can use fresh values
            try:
                if field_name == "api_key" and isinstance(self.config.get(field_name), str):
                    os.environ["MITHRIL_API_KEY"] = str(self.config[field_name])
                    from flow.cli.utils.prefetch import prefetch_for_command as _pf
                    _pf(["flow", "init"])  # warm projects/keys using fresh auth
                elif field_name == "project" and isinstance(self.config.get(field_name), str):
                    os.environ["MITHRIL_PROJECT"] = str(self.config[field_name])
                    from flow.cli.utils.prefetch import prefetch_for_command as _pf
                    _pf(["flow", "init"])  # warm ssh keys for selected project
                elif field_name == "region" and isinstance(self.config.get(field_name), str):
                    os.environ["MITHRIL_REGION"] = str(self.config[field_name])
            except Exception:
                pass
            # Refresh the compact status header so subsequent screens show updated values
            try:
                merged_status = {**context, **self.config}
                self._last_status_header = _build_selector_header(self.adapter, merged_status)
            except Exception:
                pass
            return True
        else:
            self.console.print(f"[red]{validation_result.message}[/red]")
            try_again = self._confirm_with_escape("Try again?", default=True)
            if try_again:
                return self._configure_field(field_name, context)
            return False

    def _verify_configuration(self, config: dict[str, Any]) -> bool:
        """Verify that configuration works end-to-end."""
        self.console.print(f"\n{format_text('title', 'Verifying Configuration')}")
        self.console.print("─" * 50)

        start_time = time.time()
        dots = AnimatedDots()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=self.console,
            transient=True,
        ) as progress:
            task = progress.add_task("Connecting to API...", total=None)

            try:
                # Update progress with animation
                progress.update(task, description=f"Connecting to API{dots.next()}")
                time.sleep(0.5)  # Brief pause for UI

                progress.update(task, description=f"Testing configuration{dots.next()}")
                success, error = self.adapter.verify_configuration(config)

                elapsed = time.time() - start_time
                if success:
                    success_color = theme_manager.get_color("success")
                    progress.update(
                        task,
                        description=f"[{success_color}]✓ Configuration verified! ({elapsed:.1f}s)[/{success_color}]",
                    )
                    return True
                else:
                    progress.update(
                        task, description=f"[red]✗ Verification failed ({elapsed:.1f}s)[/red]"
                    )
                    self.console.print(f"\n[red]Error:[/red] {error}")
                    return False

            except Exception as e:
                elapsed = time.time() - start_time
                progress.update(
                    task, description=f"[red]✗ Verification failed ({elapsed:.1f}s)[/red]"
                )
                self.console.print(f"\n[red]Error:[/red] {e}")
                return False

    def _show_completion(self):
        """Display setup completion message."""
        self.console.print("\n" + "─" * 50)

        completion_message = self.adapter.get_completion_message()

        # Check if billing reminder is needed
        billing_reminder = ""
        if hasattr(self.adapter, "billing_not_configured") and self.adapter.billing_not_configured:
            link_color = theme_manager.get_color("link")
            from flow.links import WebLinks
            billing_link = WebLinks.billing_settings()
            billing_reminder = (
                "\n\n[yellow]Remember to configure billing to use GPU resources:[/yellow]\n"
                f"[{link_color}]{billing_link}[/{link_color}]"
            )

        colors = get_colors()
        panel_styles = get_panel_styles()
        self.console.print(
            Panel(
                f"{format_text('success', completion_message)}\n\n"
                f"{format_text('body', 'Your configuration is ready for GPU workloads.')}\n"
                f"{format_text('muted', 'All credentials are securely stored and verified.')}"
                f"{billing_reminder}",
                title=f"{format_text('success', '✓ Success')}",
                title_align=panel_styles["success"]["title_align"],
                border_style=panel_styles["success"]["border_style"],
                padding=panel_styles["success"]["padding"],
                width=SPACING["panel_width"],
            )
        )

    def _create_demo_mode_panel(self) -> Panel:
        """Create the standardized blue demo-mode panel used throughout the flow."""
        from flow.links import WebLinks
        colors = get_colors()
        panel_styles = get_panel_styles()
        bullet = f"[{colors['primary']}]•[/{colors['primary']}]"

        body_lines = [
            f"{bullet} [bold]Sandbox only — no real resources are created.[/bold]",
            f"{bullet} Provider: [accent]mock[/accent]",
            f"{bullet} Switch to real: [accent]flow init --provider mithril[/accent] or [accent]flow demo stop[/accent]",
            f"{bullet} SSH access: Your [bold]Default SSH Key[/bold] lets you securely log in",
            f"{bullet} Manage keys: [link]{WebLinks.ssh_keys()}[/link]",
        ]

        return Panel(
            "\n".join(body_lines),
            title=f"{format_text('subtitle', 'DEMO MODE')}",
            title_align=panel_styles["info"]["title_align"],
            border_style=theme_manager.get_color("warning"),
            padding=panel_styles["info"]["padding"],
            width=SPACING["panel_width"],
        )
