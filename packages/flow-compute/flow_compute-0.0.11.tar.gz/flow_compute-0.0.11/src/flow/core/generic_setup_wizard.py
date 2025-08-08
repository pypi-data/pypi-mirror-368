"""Generic setup wizard for Flow SDK providers.

This wizard uses the adapter pattern to provide a beautiful, consistent UI
while allowing each provider to implement its own specific logic.
"""

import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table

from flow.core.setup_adapters import ProviderSetupAdapter, FieldType
from flow.cli.utils.visual_constants import (
    get_status_display,
    format_text,
    get_panel_styles,
    get_colors,
    SPACING,
)
from flow.cli.commands._init_components.setup_components import select_from_options
from flow.cli.utils.interactive_selector import InteractiveSelector, SelectionItem


def interactive_menu_select(
    options: list, title: str = "Select an option", default_index: int = 0
) -> Optional[str]:
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

    # Force fallback in problematic environments
    if (
        not sys.stdin.isatty()
        or os.environ.get("FLOW_NONINTERACTIVE")
        or os.environ.get("CI")
        or os.environ.get("TERM") == "dumb"
    ):
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
                id="",
                title=item["name"],
                subtitle=item["description"],
                status="",
            )

        selector = InteractiveSelector(
            items=menu_items, item_to_selection=menu_to_selection, title=title, allow_multiple=False
        )

        # Set default selection
        if 0 <= default_index < len(menu_items):
            selector.selected_index = default_index

        result = selector.select()
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


def _fallback_menu_select(options: list, title: str, default_index: int = 0) -> Optional[str]:
    """Fallback numbered menu selection."""
    import sys
    import signal
    from rich.console import Console

    console = Console()
    console.print(f"\n[bold]{title}[/bold]")

    # Calculate max width for display text
    max_width = max(len(opt[1]) for opt in options) if options else 30

    for i, (value, display_text, description) in enumerate(options):
        # Don't show marker in fallback mode - it's confusing since it's not interactive
        if description:
            console.print(f"    [{i + 1}] {display_text:<{max_width}} • {description}")
        else:
            console.print(f"    [{i + 1}] {display_text}")

    console.print()
    console.print(
        "[dim]Use arrow keys to navigate and Enter to select (if supported by your terminal)[/dim]"
    )
    console.print("[dim]Or enter a number to select an option[/dim]")

    # Try to enable raw input for arrow keys if possible
    try:
        import termios
        import tty

        has_termios = True
        if hasattr(sys.stdin, "fileno"):
            old_settings = termios.tcgetattr(sys.stdin.fileno())
            tty.setraw(sys.stdin.fileno())
        else:
            has_termios = False
    except (ImportError, termios.error):
        has_termios = False

    # Define signal handler for clean exit
    def signal_handler(signum, frame):
        if has_termios and "old_settings" in locals():
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, old_settings)
        console.print("\n\n[yellow]Setup cancelled[/yellow]")
        sys.exit(0)

    # Register signal handlers
    old_sigint = signal.signal(signal.SIGINT, signal_handler)
    old_sigterm = signal.signal(signal.SIGTERM, signal_handler)

    selected = default_index

    try:
        if has_termios and "old_settings" in locals():
            # Raw mode with arrow key support
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, old_settings)
            console.print(f"\nNavigate with arrow keys or numbers. Press Enter to select.")

            while True:
                # Redraw menu with current selection
                console.print("\033[2J\033[H")  # Clear screen and move to top
                console.print(f"\n[bold]{title}[/bold]\n")

                # Calculate max width for display text
                max_width = max(len(opt[1]) for opt in options) if options else 30

                for i, (value, display_text, description) in enumerate(options):
                    prefix = "  > " if i == selected else "    "
                    style = "reverse" if i == selected else None

                    if description:
                        text = f"{prefix}[{i + 1}] {display_text:<{max_width}} • {description}"
                    else:
                        text = f"{prefix}[{i + 1}] {display_text}"

                    console.print(text, style=style)

                console.print("\n[dim]↑/↓: Navigate | Enter: Select | Number: Jump to option[/dim]")

                # Get single key
                try:
                    import getch

                    key = getch.getch()
                except ImportError:
                    # Fallback to regular input
                    key = input().strip()

                if key == "\r" or key == "\n":  # Enter
                    return options[selected][0]
                elif key == "\x1b":  # Escape sequence
                    next1 = sys.stdin.read(1)
                    next2 = sys.stdin.read(1)
                    if next1 == "[" and next2 == "A":  # Up arrow
                        selected = max(0, selected - 1)
                    elif next1 == "[" and next2 == "B":  # Down arrow
                        selected = min(len(options) - 1, selected + 1)
                elif key.isdigit():
                    num = int(key)
                    if 1 <= num <= len(options):
                        selected = num - 1
                        return options[selected][0]
                elif key == "\x03":  # Ctrl+C
                    raise KeyboardInterrupt()
        else:
            # Fallback to simple numbered input
            while True:
                try:
                    default_num = str(default_index + 1)
                    response = input(f"Enter number [1-{len(options)}] ({default_num}): ").strip()

                    if not response:
                        return options[default_index][0]

                    choice_num = int(response)
                    if 1 <= choice_num <= len(options):
                        return options[choice_num - 1][0]
                    else:
                        console.print("Please enter a valid number")

                except KeyboardInterrupt:
                    console.print("\n\n[yellow]Setup cancelled[/yellow]")
                    sys.exit(0)
                except (ValueError, EOFError):
                    console.print("\n[yellow]Cancelled[/yellow]")
                    return None
    finally:
        # Restore terminal settings
        if has_termios and "old_settings" in locals():
            try:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, old_settings)
            except:
                pass
        # Restore original signal handlers
        signal.signal(signal.SIGINT, old_sigint)
        signal.signal(signal.SIGTERM, old_sigterm)


def simple_choice_prompt(prompt_text: str, choices: list, default: str = None) -> str:
    """Simple, reliable choice prompt that bypasses Rich completely."""
    import sys
    import os

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

    def __init__(self, console: Console, adapter: ProviderSetupAdapter):
        """Initialize the wizard.

        Args:
            console: Rich console for output
            adapter: Provider-specific setup adapter
        """
        self.console = console
        self.adapter = adapter
        self.config = {}  # New configuration values

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

            # Detect existing configuration
            existing_config = self.adapter.detect_existing_config()

            # Show configuration status
            if not self._show_configuration_status(existing_config):
                return False

            # Check if fully configured
            if self._is_fully_configured(existing_config):
                return self._handle_fully_configured(existing_config)
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

    def _show_configuration_status(self, existing_config: Dict[str, Any]) -> bool:
        """Display current configuration status in a table.

        Args:
            existing_config: Dictionary of existing configuration

        Returns:
            Always True
        """
        self.console.print()
        panel_styles = get_panel_styles()
        self.console.print(
            Panel(
                self._build_status_content(existing_config),
                title=f"{format_text('title', 'Configuration Status')}",
                title_align=panel_styles["secondary"]["title_align"],
                border_style=panel_styles["secondary"]["border_style"],
                padding=panel_styles["secondary"]["padding"],
            )
        )
        return True

    def _build_status_content(self, existing_config: Dict[str, Any]) -> str:
        """Build the configuration status content string."""
        # Create status table with refined styling
        colors = get_colors()
        table = Table(show_header=True, box=None, padding=(0, 2))
        table.add_column("Component", style=colors["accent"], min_width=15, justify="left")
        table.add_column("Status", min_width=12, justify="left")
        table.add_column("Value", style=colors["muted"], min_width=18, justify="left")
        table.add_column("Source", style=colors["muted"], min_width=8, justify="left")

        fields = self.adapter.get_configuration_fields()

        # Sort items by importance: required first, then optional
        required_fields = [f for f in fields if f.required]
        optional_fields = [f for f in fields if not f.required]

        for field in required_fields + optional_fields:
            value = existing_config.get(field.name)

            if value:
                status_display = get_status_display("configured", "Configured")

                # Get display value
                if field.mask_display and value:
                    if len(value) > 10:
                        display_value = f"{value[:8]}...{value[-4:]}"
                    else:
                        display_value = "[CONFIGURED]"
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
            table.add_row(display_name, status_display, display_value, source_display)

        return table

    def _is_fully_configured(self, existing_config: Dict[str, Any]) -> bool:
        """Check if all required components are configured."""
        fields = self.adapter.get_configuration_fields()
        required_fields = [f for f in fields if f.required]

        return all(existing_config.get(field.name) for field in required_fields)

    def _handle_fully_configured(self, existing_config: Dict[str, Any]) -> bool:
        """Handle case where all required items are already configured."""
        self.console.print(
            f"\n{get_status_display('configured', 'All required components are configured')}"
        )

        # Interactive menu options
        menu_options = [
            ("1", "[1] Exit without verification", ""),
            ("2", "[2] Verify configuration and exit", ""),
            ("3", "[3] Reconfigure components", ""),
        ]

        self.console.print()  # Add spacing
        action = interactive_menu_select(
            options=menu_options,
            title="What would you like to do?",
            default_index=0,  # Default to first option (exit)
        )

        if action == "1":
            self.console.print("\n[dim]Exiting without verification.[/dim]")
            return True
        elif action == "2":
            success, error = self.adapter.verify_configuration(existing_config)
            if success:
                self.console.print("\n[green]✓ Configuration verified successfully![/green]")
                return True
            else:
                self.console.print(f"\n[yellow]Verification failed: {error}[/yellow]")
                return self._configure_missing_items(existing_config)
        elif action == "3":
            return self._configure_missing_items(existing_config)

        return True

    def _configure_missing_items(self, existing_config: Dict[str, Any]) -> bool:
        """Configure missing or selected items."""
        fields = self.adapter.get_configuration_fields()

        while True:
            # Build interactive menu options
            menu_options = []
            choice_map = {}
            choice_num = 1

            for field in fields:
                existing_value = existing_config.get(field.name)
                field_title = field.display_name or field.name.replace("_", " ").title()

                if existing_value:
                    if field.mask_display:
                        display_val = (
                            f"{existing_value[:8]}...{existing_value[-4:]}"
                            if len(existing_value) > 10
                            else "[CONFIGURED]"
                        )
                    else:
                        display_val = existing_value
                    display_text = f"[{choice_num}] Reconfigure {field_title}"
                    description = ""
                else:
                    display_text = f"[{choice_num}] Configure {field_title}"
                    description = ""

                menu_options.append((str(choice_num), display_text, description))
                choice_map[str(choice_num)] = field.name
                choice_num += 1

            # Add exit option
            menu_options.append(("done", f"[{choice_num}] Done (save and exit)", ""))

            self.console.print()  # Add spacing
            # Choose sensible default: first missing field, otherwise "Done"
            try:
                default_index = 0
                # Find first field that is not present in existing or newly provided config
                for idx, field in enumerate(fields):
                    already_configured = existing_config.get(field.name) or self.config.get(
                        field.name
                    )
                    if not already_configured:
                        default_index = idx
                        break
                else:
                    # All fields configured; default to the "Done" option at the end
                    default_index = len(menu_options) - 1
            except Exception:
                # On any unexpected error, fall back to the first option
                default_index = 0

            choice = interactive_menu_select(
                options=menu_options, title="Configuration Menu", default_index=default_index
            )

            # Handle ESC key (returns None) - go back to previous menu
            if choice is None:
                # At the main configuration menu, ESC should ask for confirmation
                if Confirm.ask("\n[yellow]Exit setup?[/yellow]", default=False):
                    self.console.print("[dim]Setup cancelled[/dim]")
                    return False
                else:
                    continue  # Stay in menu

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
                    if not Confirm.ask("Exit anyway?", default=False):
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

    def _configure_field(self, field_name: str, context: Dict[str, Any]) -> bool:
        """Configure a single field."""
        fields = {f.name: f for f in self.adapter.get_configuration_fields()}
        field = fields[field_name]

        display_name = field.display_name or field.name.replace("_", " ").title()
        self.console.print(f"\n[bold]Flow Setup › Configuration › {display_name}[/bold]")
        self.console.print("─" * 50)
        self.console.print("[dim]ESC to go back • Ctrl+C to exit[/dim]")

        if field.help_text:
            self.console.print(f"[dim]{field.help_text}[/dim]")

        if field.help_url:
            self.console.print(f"[dim]More info: {field.help_url}[/dim]")

        # Get field value based on type
        if field.field_type == FieldType.CHOICE:
            if field.dynamic_choices:
                # Get dynamic choices
                choice_strings = self.adapter.get_dynamic_choices(
                    field_name, {**context, **self.config}
                )
                if not choice_strings:
                    self.console.print(
                        "\n[yellow]No options available. Skipping this field.[/yellow]"
                    )
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
                selected = select_from_options(
                    console=self.console,
                    options=choices,
                    name_key="display",
                    id_key="id",
                    title=f"Available {(field.display_name or field.name.replace('_', ' ').title()).lower()}",
                    show_ssh_table=is_ssh_key_selection,
                )

                if selected:
                    value = selected["id"]
                else:
                    return False
            else:
                # Static choices - convert to dict format
                choice_strings = field.choices or []
                choices = [{"name": choice, "id": choice} for choice in choice_strings]

                selected = select_from_options(
                    console=self.console,
                    options=choices,
                    name_key="name",
                    id_key="id",
                    title=f"Available {(field.display_name or field.name.replace('_', ' ').title()).lower()}",
                )

                if selected:
                    value = selected["id"]
                else:
                    return False

        elif field.field_type == FieldType.PASSWORD:
            try:
                value = Prompt.ask(f"\n{display_name}", password=True)
            except KeyboardInterrupt:
                self.console.print("\n[dim]Returning to menu...[/dim]")
                return False
        elif field.field_type == FieldType.BOOLEAN:
            try:
                value = Confirm.ask(f"\n{display_name}", default=field.default)
            except KeyboardInterrupt:
                self.console.print("\n[dim]Returning to menu...[/dim]")
                return False
        else:  # TEXT
            try:
                value = Prompt.ask(f"\n{display_name}", default=field.default)
            except KeyboardInterrupt:
                self.console.print("\n[dim]Returning to menu...[/dim]")
                return False

        # Validate the field with full context
        validation_result = self.adapter.validate_field(
            field_name, str(value), {**context, **self.config}
        )

        if validation_result.is_valid:
            # Use processed_value if available (e.g., for SSH key generation)
            final_value = getattr(validation_result, "processed_value", None) or value
            self.config[field_name] = final_value

            # Show confirmation
            display_value = validation_result.display_value or str(final_value)
            self.console.print(f"[green]✓[/green] {display_name}: {display_value}")
            return True
        else:
            self.console.print(f"[red]{validation_result.message}[/red]")
            if Confirm.ask("Try again?", default=True):
                return self._configure_field(field_name, context)
            return False

    def _verify_configuration(self, config: Dict[str, Any]) -> bool:
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
                    progress.update(
                        task,
                        description=f"[green]✓ Configuration verified! ({elapsed:.1f}s)[/green]",
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
        if (
            hasattr(self.adapter, "_billing_not_configured")
            and self.adapter._billing_not_configured
        ):
            billing_reminder = "\n\n[yellow]Remember to configure billing to use GPU resources:[/yellow]\n[cyan]https://app.mithril.ai/settings/billing[/cyan]"

        colors = get_colors()
        panel_styles = get_panel_styles()
        self.console.print(
            Panel(
                f"{format_text('success', completion_message)}\n\n"
                f"{format_text('body', 'Your configuration is ready for GPU workloads.')}\n"
                f"{format_text('muted', 'All credentials are securely stored and verified.')}" \
                f"{billing_reminder}",
                title=f"{format_text('success', '✓ Success')}",
                title_align=panel_styles["success"]["title_align"],
                border_style=panel_styles["success"]["border_style"],
                padding=panel_styles["success"]["padding"],
                width=SPACING["panel_width"],
            )
        )
