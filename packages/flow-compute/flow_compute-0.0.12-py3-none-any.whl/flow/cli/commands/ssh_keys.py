"""SSH key management commands for Flow CLI.

This module provides commands to list, sync, and manage SSH keys between
local system and the Mithril platform.
"""

from pathlib import Path

import click
from rich.console import Console

from flow import Flow
from flow.core.ssh_resolver import SmartSSHKeyResolver

from ..utils.animated_progress import AnimatedEllipsisProgress
from ..utils.table_styles import create_flow_table, wrap_table_in_panel
from .base import BaseCommand


def truncate_platform_id(platform_id: str, max_len: int = 10) -> str:
    """Truncate platform ID for display, keeping prefix intact."""
    if not platform_id or len(platform_id) <= max_len:
        return platform_id

    # Keep the sshkey_ prefix and first few chars of the actual ID
    if platform_id.startswith("sshkey_"):
        return f"sshkey_{platform_id[7 : 7 + max_len - 7]}…"
    return f"{platform_id[: max_len - 1]}…"


def truncate_key_name(name: str, max_len: int = 26) -> str:
    """Truncate key name for consistent display."""
    if not name or len(name) <= max_len:
        return name

    # Account for bullet point if present
    if name.startswith("● "):
        return f"● {name[2 : max_len - 3]}…"
    return f"{name[: max_len - 1]}…"


@click.command()
@click.option("--sync", is_flag=True, help="Upload local SSH keys to platform")
@click.option("--show-auto", is_flag=True, help="Show auto-generated keys (hidden by default)")
@click.option("--verbose", "-v", is_flag=True, help="Show file paths and detailed information")
def list(sync: bool, show_auto: bool, verbose: bool):
    """List SSH keys and their status.

    \b
    Key Types:
      Active     - Keys used when you run tasks (configured in ~/.flow/config.yaml)
      Available  - Keys ready to use but not configured
      Local      - Keys on your machine not yet uploaded to platform
      Platform   - Keys only on platform (no local backup)
      Auto       - Auto-generated keys (hidden by default)

    \b
    Common Workflows:
      1. First time setup:
         $ flow ssh-keys list --sync              # Upload local keys to platform
         $ flow ssh-keys list                     # Copy platform ID (sshkey_XXX)
         # Add to ~/.flow/config.yaml:
         ssh_keys:
           - sshkey_XXX

      2. Check which keys are active:
         $ flow ssh-keys list                     # Active keys marked with •

      3. Clean up unused keys:
         $ flow ssh-keys list --show-auto         # Show all including auto-generated
         $ flow ssh-keys delete sshkey_XXX        # Remove from platform
    """
    console = Console()

    try:
        with AnimatedEllipsisProgress(console, "Loading SSH keys") as progress:
            # Get SSH key manager from Flow instance
            flow = Flow()
            try:
                ssh_key_manager = flow.get_ssh_key_manager()
            except AttributeError:
                console.print(
                    "[yellow]SSH key management not supported by current provider[/yellow]"
                )
                return

            resolver = SmartSSHKeyResolver(ssh_key_manager)

            # Get configured SSH keys
            configured_keys = flow.config.provider_config.get("ssh_keys", [])

            # Get local keys
            local_keys = resolver.find_available_keys()

            # Get platform keys
            platform_keys = ssh_key_manager.list_keys()

        # Separate user keys from auto-generated keys
        user_keys = []
        auto_keys = []

        for name, path in local_keys:
            if name.startswith("flow:flow-auto-"):
                auto_keys.append((name, path))
            else:
                user_keys.append((name, path))

        # Create lookup for platform keys by ID
        platform_keys_by_id = {pkey.fid: pkey for pkey in platform_keys}

        # Create a map of local keys to platform IDs for quick lookup
        local_to_platform = {}
        for _name, path in local_keys:
            pub_path = path.with_suffix(".pub")
            if pub_path.exists():
                try:
                    local_pub = pub_path.read_text().strip()
                    for pkey in platform_keys:
                        if (
                            hasattr(pkey, "public_key")
                            and pkey.public_key
                            and ssh_key_manager._normalize_public_key(local_pub)
                            == ssh_key_manager._normalize_public_key(pkey.public_key)
                        ):
                            local_to_platform[str(path)] = pkey.fid
                            break
                except Exception:
                    pass

        # Show explanation if helpful
        if not configured_keys:
            console.print("\n[yellow]ℹ️  No SSH keys configured for Flow tasks.[/yellow]")
            if user_keys:
                console.print("   You have local SSH keys that can be used.")
                if not sync:
                    console.print(
                        "   Run [cyan]flow ssh-keys list --sync[/cyan] to upload them first."
                    )
            console.print()

        # Create table using centralized formatter
        # Don't show borders since we're wrapping in a panel
        table = create_flow_table(show_borders=False)

        # Add columns matching flow status style
        table.add_column("Name", style="white", width=28, header_style="bold white", justify="left")
        table.add_column(
            "Type", style="cyan", width=10, header_style="bold white", justify="center"
        )
        table.add_column(
            "Platform ID", style="yellow", width=12, header_style="bold white", justify="left"
        )
        table.add_column("Status", width=12, header_style="bold white", justify="center")

        # Track active keys separately for summary
        active_key_count = 0

        # Show active keys (from config) first - marked with indicator
        for key_ref in configured_keys:
            found = False

            # Check if it's a platform ID
            if key_ref.startswith("sshkey_") and key_ref in platform_keys_by_id:
                pkey = platform_keys_by_id[key_ref]
                # Find if there's a local key for this
                local_path = None
                for path, pid in local_to_platform.items():
                    if pid == key_ref:
                        local_path = path
                        break

                if local_path:
                    name = truncate_key_name(
                        f"● {Path(local_path).name}"
                    )  # Bullet indicates active
                    key_type = "Active"
                    status = "[green]Ready[/green]"
                else:
                    name = truncate_key_name(f"● {pkey.name}")
                    key_type = "Active"
                    status = "[yellow]No backup[/yellow]"

                table.add_row(name, key_type, truncate_platform_id(key_ref), status)
                found = True
                active_key_count += 1

            if not found:
                table.add_row(truncate_key_name(f"● {key_ref}"), "Active", "", "[red]Missing[/red]")
                active_key_count += 1

        # Add available keys (not active)
        available_user_keys = [
            (n, p) for n, p in user_keys if local_to_platform.get(str(p), "") not in configured_keys
        ]

        # Add separator if we had active keys
        if configured_keys and available_user_keys:
            table.add_section()

        for name, path in available_user_keys:
            platform_id = local_to_platform.get(str(path), "")

            # Show cleaner name without "flow:" prefix for flow-managed keys
            display_name = name.replace("flow:", "") if name.startswith("flow:") else name

            if platform_id:
                key_type = "Available"
                status = "[dim]Ready[/dim]"
                show_id = platform_id
            else:
                key_type = "Local"
                status = "[dim]Not uploaded[/dim]"
                show_id = "[dim]-[/dim]"

            table.add_row(
                truncate_key_name(display_name),
                key_type,
                truncate_platform_id(show_id) if show_id not in ("[dim]-[/dim]", "") else show_id,
                status,
            )

        # Add auto-generated keys (only if requested)
        if show_auto and auto_keys:
            # Add separator
            if configured_keys or available_user_keys:
                table.add_section()

            # Show only first few unless verbose
            keys_to_show = auto_keys if verbose else auto_keys[:5]

            for name, path in keys_to_show:
                platform_id = local_to_platform.get(str(path), "")
                is_configured = platform_id in configured_keys

                display_name = name.replace("flow:", "")

                if is_configured:
                    # Active auto-generated key
                    key_type = "[dim]Auto[/dim]"
                    status = "[green dim]Active[/green dim]"
                    show_name = f"[dim]● {display_name}[/dim]"  # Bullet for active
                elif platform_id:
                    key_type = "[dim]Auto[/dim]"
                    status = "[dim]Available[/dim]"
                    show_name = f"[dim]{display_name}[/dim]"
                else:
                    key_type = "[dim]Auto[/dim]"
                    status = "[dim]Local only[/dim]"
                    show_name = f"[dim]{display_name}[/dim]"

                show_id = f"[dim]{truncate_platform_id(platform_id) if platform_id else '-'}[/dim]"
                table.add_row(show_name, key_type, show_id, status)

            if not verbose and len(auto_keys) > 5:
                remaining = len(auto_keys) - 5
                table.add_row(
                    f"[dim]... {remaining} more auto-generated[/dim]",
                    "[dim]...[/dim]",
                    "[dim]...[/dim]",
                    "[dim]...[/dim]",
                )

        # Add platform-only keys (no local copy)
        platform_only = []
        for pkey in platform_keys:
            # Skip if already shown or is auto-generated
            if pkey.name.startswith("flow-auto-") and not show_auto:
                continue

            is_local = False
            for _path, pid in local_to_platform.items():
                if pid == pkey.fid:
                    is_local = True
                    break

            if not is_local:
                platform_only.append(pkey)

        if platform_only:
            # Add separator
            if configured_keys or available_user_keys or (show_auto and auto_keys):
                table.add_section()

            for pkey in platform_only:
                is_configured = pkey.fid in configured_keys
                if is_configured:
                    name = truncate_key_name(f"● {pkey.name}")  # Bullet for active
                    key_type = "Active"
                    status = "[yellow]No backup[/yellow]"
                else:
                    name = truncate_key_name(pkey.name)
                    key_type = "Platform"
                    status = "[dim]Available[/dim]"
                table.add_row(name, key_type, truncate_platform_id(pkey.fid), status)

        # Create descriptive title
        total_keys = len(configured_keys) + len(available_user_keys) + len(platform_only)
        if show_auto:
            total_keys += len(auto_keys)

        title = f"SSH Keys ({total_keys} total"
        if not show_auto and auto_keys:
            title += f", {len(auto_keys)} auto-generated hidden"
        title += ")"

        # Wrap table in a styled panel
        wrap_table_in_panel(table, title, console)

        # Show summary with quick legend
        if auto_keys and not show_auto:
            summary = f"\n[dim]Keys: {active_key_count} active • {len(available_user_keys)} available • {len(auto_keys)} auto-generated (hidden)[/dim]"
        else:
            summary = f"\n[dim]Keys: {active_key_count} active • {len(available_user_keys)} available • {len(platform_only)} platform-only[/dim]"
        console.print(summary)
        console.print(
            "[dim]• = active (used for tasks) | See --help for key type explanations[/dim]"
        )

        # Sync if requested
        if sync:
            console.print("\n[bold]Syncing local keys to platform...[/bold]")
            synced_count = 0

            with AnimatedEllipsisProgress(console, "Uploading SSH keys") as progress:
                for name, path in user_keys:  # Only sync user keys, not auto-generated
                    pub_path = path.with_suffix(".pub")
                    if pub_path.exists():
                        # Check if already synced
                        if str(path) not in local_to_platform:
                            try:
                                # Upload the key
                                result = ssh_key_manager.ensure_platform_keys([str(path)])
                                if result:
                                    console.print(f"  ✓ Uploaded {name}")
                                    synced_count += 1
                            except Exception as e:
                                console.print(f"  ✗ Failed to upload {name}: {e}")
                        else:
                            console.print(f"  - {name} already synced")

            if synced_count > 0:
                console.print(f"\n[green]Successfully synced {synced_count} keys[/green]")
            else:
                console.print("\n[yellow]All user keys already synced[/yellow]")

        # Show actionable next steps
        if not configured_keys:
            console.print("\n[yellow]⚠️  No SSH keys configured for Flow tasks[/yellow]")

            # Check if they have any synced keys
            synced_user_keys = [(n, p) for n, p in user_keys if str(p) in local_to_platform]

            if synced_user_keys:
                # Get first synced key
                for _name, path in synced_user_keys[:1]:
                    platform_id = local_to_platform[str(path)]
                    console.print("\nQuick fix: Add this to ~/.flow/config.yaml")
                    console.print(f"[dim]ssh_keys:\n  - {platform_id}[/dim]")
            elif user_keys:
                console.print("\nNext: [cyan]flow ssh-keys list --sync[/cyan] to upload your keys")
            else:
                console.print("\nNext: [cyan]ssh-keygen -t ed25519[/cyan] to create an SSH key")
        elif active_key_count > 0:
            # Show active key summary
            console.print(
                f"\n[green]✓ {active_key_count} key{'s' if active_key_count > 1 else ''} configured for Flow tasks[/green]"
            )

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e)) from e


@click.command()
@click.argument("key_id")
@click.option("--verbose", "-v", is_flag=True, help="Show full public key")
def details(key_id: str, verbose: bool):
    """Show detailed information about an SSH key.

    KEY_ID: Platform SSH key ID (e.g., sshkey_abc123)

    Shows:
    - Key metadata (name, creation date)
    - Tasks that launched with this key
    - Local key mapping
    """
    console = Console()

    try:
        # Get Flow instance
        flow = Flow()
        try:
            ssh_key_manager = flow.get_ssh_key_manager()
        except AttributeError:
            console.print("[yellow]SSH key management not supported by current provider[/yellow]")
            return

        # Get the key details with progress
        with AnimatedEllipsisProgress(console, "Fetching SSH key details") as progress:
            key = ssh_key_manager.get_key(key_id)
            if not key:
                console.print(f"\n[red]SSH key {key_id} not found[/red]")
                return

            # Check for local copy
            from flow.core.ssh_resolver import SmartSSHKeyResolver

            resolver = SmartSSHKeyResolver(ssh_key_manager)
            local_keys = resolver.find_available_keys()

            local_path = None
            for _name, path in local_keys:
                pub_path = path.with_suffix(".pub")
                if pub_path.exists():
                    try:
                        local_pub = pub_path.read_text().strip()
                        if (
                            hasattr(key, "public_key")
                            and key.public_key
                            and ssh_key_manager._normalize_public_key(local_pub)
                            == ssh_key_manager._normalize_public_key(key.public_key)
                        ):
                            local_path = path
                            break
                    except Exception:
                        pass

            # Get configured SSH keys
            configured_keys = flow.config.provider_config.get("ssh_keys", [])
            is_configured = key_id in configured_keys

        # Create a formatted panel for key info
        from rich.panel import Panel
        from rich.table import Table

        info_table = Table(show_header=False, box=None, padding=(0, 1))
        info_table.add_column(style="bold")
        info_table.add_column()

        info_table.add_row("Platform ID", key.fid)
        info_table.add_row("Name", key.name)
        if hasattr(key, "created_at") and key.created_at:
            info_table.add_row("Created", str(key.created_at))

        if local_path:
            info_table.add_row("Local key", str(local_path))
        else:
            info_table.add_row("Local key", "[dim]Not found[/dim]")

        if is_configured:
            info_table.add_row("Status", "[green]● Active[/green] (in ~/.flow/config.yaml)")
        else:
            info_table.add_row("Status", "[dim]Available[/dim]")

        console.print("\n")
        console.print(Panel(info_table, title="[bold]SSH Key Details[/bold]", border_style="blue"))

        # Find tasks using this key
        console.print("\n[bold]Tasks launched with this key:[/bold]")

        with AnimatedEllipsisProgress(console, "Searching task history") as progress:
            tasks_using_key = []

            # For Mithril provider, we need to fetch bid data directly
            # since Task objects don't preserve the launch_specification
            if hasattr(flow._provider, "http"):  # Mithril provider
                try:
                    # Get all bids/tasks
                    project_id = flow._provider._get_project_id()
                    response = flow._provider.http.request(
                        method="GET",
                        url="/v2/spot/bids",
                        params={"project": project_id, "limit": 100},
                    )
                    bids = response.get("data", [])

                    for bid in bids:
                        launch_spec = bid.get("launch_specification", {})
                        task_ssh_keys = launch_spec.get("ssh_keys", [])
                        if key_id in task_ssh_keys:
                            # Build a task representation with all the info we need
                            tasks_using_key.append(
                                {
                                    "name": bid.get("name", f"task-{bid['fid'][:8]}"),
                                    "status": bid.get("status", "unknown"),
                                    "instance_type": bid.get("instance_type", "N/A"),
                                    "created_at": bid.get("created_at"),
                                    "task_id": bid.get("fid"),
                                    "region": bid.get("region", "unknown"),
                                }
                            )
                except Exception as e:
                    # Fallback if API fails
                    console.print(f"[yellow]Could not fetch task history: {e}[/yellow]")
            else:
                # For other providers, we can't determine SSH key usage
                console.print("[dim]Task history not available for this provider[/dim]")

        if tasks_using_key:
            # Sort by creation date (newest first)
            tasks_using_key.sort(key=lambda x: x["created_at"] or "", reverse=True)

            # Create a simple table
            from ..utils.table_styles import create_flow_table

            table = create_flow_table(show_borders=False)
            table.add_column("Task", style="cyan", width=20)
            table.add_column("Status", style="white", width=10)
            table.add_column("GPU", style="yellow", width=8)
            table.add_column("Region", style="blue", width=12)
            table.add_column("Started", style="dim")

            # Group running tasks first
            running_tasks = [t for t in tasks_using_key if t["status"] == "running"]
            other_tasks = [t for t in tasks_using_key if t["status"] != "running"]

            ordered_tasks = running_tasks + other_tasks

            for task_data in ordered_tasks[:15]:  # Show up to 15 tasks
                status_color = {
                    "running": "green",
                    "completed": "blue",
                    "failed": "red",
                    "cancelled": "yellow",
                    "pending": "cyan",
                }.get(task_data["status"].lower(), "white")

                created_str = "Unknown"
                if task_data["created_at"]:
                    try:
                        # Handle both datetime objects and ISO strings
                        if isinstance(task_data["created_at"], str):
                            from datetime import datetime

                            created_dt = datetime.fromisoformat(
                                task_data["created_at"].replace("Z", "+00:00")
                            )
                            created_str = created_dt.strftime("%m-%d %H:%M")
                        else:
                            created_str = task_data["created_at"].strftime("%m-%d %H:%M")
                    except Exception:
                        created_str = str(task_data["created_at"])[:10]

                # Extract GPU type from instance type
                gpu_type = (
                    task_data["instance_type"].split("-")[0]
                    if "-" in task_data["instance_type"]
                    else task_data["instance_type"]
                )

                # Truncate long task names
                task_name = task_data["name"]
                if len(task_name) > 20:
                    task_name = task_name[:17] + "..."

                table.add_row(
                    task_name,
                    f"[{status_color}]{task_data['status']}[/{status_color}]",
                    gpu_type,
                    task_data.get("region", "").replace("us-", "").replace("-1", ""),
                    created_str,
                )

            console.print(table)

            if len(tasks_using_key) > 15:
                console.print(f"\n[dim]... and {len(tasks_using_key) - 15} more tasks[/dim]")

            # Show summary stats
            running_count = len([t for t in tasks_using_key if t["status"] == "running"])
            total_count = len(tasks_using_key)

            console.print(
                f"\n[dim]Total: {total_count} tasks • {running_count} currently running[/dim]"
            )

            # Show quick action for running tasks
            if running_tasks:
                recent_running = running_tasks[0]
                console.print(
                    f"\n[dim]Quick connect: [cyan]flow ssh {recent_running['name']}[/cyan][/dim]"
                )
        else:
            console.print("[dim]No tasks found using this key[/dim]")
            if not is_configured:
                console.print("\n[dim]To use this key, add it to ~/.flow/config.yaml:[/dim]")
                console.print(f"[dim]ssh_keys:\n  - {key_id}[/dim]")

        # Show public key if available (collapsed by default)
        if hasattr(key, "public_key") and key.public_key and verbose:
            console.print("\n[bold]Public key:[/bold]")
            console.print(Panel(key.public_key.strip(), border_style="dim"))
        elif hasattr(key, "public_key") and key.public_key:
            # Show fingerprint instead of full key
            import base64
            import hashlib

            try:
                # Parse the public key to get fingerprint
                key_data = key.public_key.strip().split()[1]  # Get the base64 part
                decoded = base64.b64decode(key_data)
                fingerprint = hashlib.md5(decoded).hexdigest()
                fp_formatted = ":".join(
                    fingerprint[i : i + 2] for i in range(0, len(fingerprint), 2)
                )
                console.print(f"\n[dim]Fingerprint: {fp_formatted}[/dim]")
                console.print("[dim]Use --verbose to see full public key[/dim]")
            except Exception:
                console.print("\n[dim]Use --verbose to see full public key[/dim]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e)) from e


@click.command()
@click.argument("key_identifier")
def delete(key_identifier: str):
    """Delete an SSH key from the platform.

    KEY_IDENTIFIER: Platform SSH key ID (e.g., sshkey_abc123) or key name
    """
    console = Console()

    try:
        # Get SSH key manager from Flow instance
        flow = Flow()
        try:
            ssh_key_manager = flow.get_ssh_key_manager()
        except AttributeError:
            console.print("[yellow]SSH key management not supported by current provider[/yellow]")
            return

        # Resolve key identifier to platform ID
        key_id = key_identifier
        if not key_identifier.startswith("sshkey_"):
            # Search for key by name
            matching_keys = ssh_key_manager.find_keys_by_name(key_identifier)

            if not matching_keys:
                console.print(f"[red]SSH key '{key_identifier}' not found[/red]")
                console.print("\n[dim]Available keys:[/dim]")
                all_keys = ssh_key_manager.list_keys()
                for key in all_keys[:10]:  # Show first 10 keys
                    console.print(f"  • {key.name} ({key.fid})")
                if len(all_keys) > 10:
                    console.print(f"  [dim]... and {len(all_keys) - 10} more[/dim]")
                return

            if len(matching_keys) > 1:
                console.print(f"[yellow]Multiple keys found with name '{key_identifier}':[/yellow]")
                for key in matching_keys:
                    console.print(f"  • {key.name} ({key.fid})")
                console.print(
                    "\n[dim]Please use the platform ID (sshkey_xxx) to delete a specific key[/dim]"
                )
                return

            key_id = matching_keys[0].fid
            console.print(f"[dim]Found key: {matching_keys[0].name} ({key_id})[/dim]")

        # Confirm deletion
        if not click.confirm(f"Delete SSH key {key_id}?"):
            return

        # Delete the key using proper abstraction
        from flow.providers.mithril.resources.ssh import SSHKeyNotFoundError, SSHKeyError

        try:
            ssh_key_manager.delete_key(key_id)
            console.print(f"[green]✓ Deleted SSH key {key_id}[/green]")
        except SSHKeyNotFoundError:
            console.print(f"[red]SSH key {key_id} not found[/red]")
            console.print("[dim]The key may have already been deleted[/dim]")
        except SSHKeyError as e:
            console.print(f"[red]{e}[/red]")
            raise click.ClickException(str(e)) from e

    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e)) from e


@click.command()
@click.argument("key_path")
@click.option("--name", help="Name for the SSH key on platform")
def upload(key_path: str, name: str | None):
    """Upload a specific SSH key to the platform.

    KEY_PATH: Path to the SSH private key (e.g., ~/.ssh/id_rsa)
    """
    console = Console()

    try:
        # Get SSH key manager from Flow instance
        flow = Flow()
        try:
            ssh_key_manager = flow.get_ssh_key_manager()
        except AttributeError:
            console.print("[yellow]SSH key management not supported by current provider[/yellow]")
            return

        # Resolve path
        path = Path(key_path).expanduser().resolve()
        if not path.exists():
            console.print(f"[red]SSH key not found: {key_path}[/red]")
            return

        # Upload the key
        result = ssh_key_manager.ensure_platform_keys([str(path)])
        if result:
            console.print(f"[green]✓ Uploaded SSH key to platform as {result[0]}[/green]")
            console.print("\nTo use this key, add to ~/.flow/config.yaml:")
            console.print("  ssh_keys:")
            console.print(f"    - {result[0]}")
        else:
            console.print("[red]✗ Failed to upload SSH key[/red]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.ClickException(str(e)) from e


class SSHKeysCommand(BaseCommand):
    """SSH keys management command."""

    @property
    def name(self) -> str:
        """Command name."""
        return "ssh-keys"

    @property
    def help(self) -> str:
        """Command help text."""
        return "Manage SSH keys - list, upload, configure for tasks"

    def get_command(self) -> click.Command:
        """Return the ssh-keys command group."""

        @click.group(name="ssh-keys")
        @click.option(
            "--verbose", "-v", is_flag=True, help="Show detailed SSH key management guide"
        )
        def ssh_keys_group(verbose: bool):
            """Manage SSH keys for Flow tasks.

            \b
            Examples:
                flow ssh-keys list           # Show all SSH keys
                flow ssh-keys upload ~/.ssh/id_rsa.pub  # Upload new key
                flow ssh-keys delete sshkey_xxx         # Remove key

            Use 'flow ssh-keys --verbose' for complete SSH setup guide.
            """
            if verbose:
                console = Console()
                console.print("\n[bold]SSH Key Management Guide:[/bold]\n")
                console.print("Initial setup:")
                console.print("  flow ssh-keys list --sync         # Upload local keys")
                console.print("  flow ssh-keys list                # View all keys")
                console.print("  # Copy platform ID (sshkey_xxx) and add to ~/.flow/config.yaml\n")

                console.print("Key locations:")
                console.print("  ~/.ssh/                           # Standard SSH keys")
                console.print("  ~/.flow/keys/                     # Flow-specific keys")
                console.print("  ~/.flow/config.yaml               # Active key configuration\n")

                console.print("Common patterns:")
                console.print("  # Use existing GitHub key")
                console.print("  flow ssh-keys upload ~/.ssh/id_ed25519.pub")
                console.print("  ")
                console.print("  # Generate new key for Flow")
                console.print("  ssh-keygen -t ed25519 -f ~/.ssh/flow_key")
                console.print("  flow ssh-keys upload ~/.ssh/flow_key.pub\n")

                console.print("Configuration in ~/.flow/config.yaml:")
                console.print("  ssh_keys:")
                console.print("    - sshkey_abc123                 # Platform ID")
                console.print("    - ~/.ssh/id_rsa                 # Local path\n")

                console.print("Troubleshooting:")
                console.print("  • Permission denied → Check key is added: flow ssh-keys list")
                console.print("  • Key not found → Run: flow ssh-keys list --sync")
                console.print("  • Multiple keys → Configure in ~/.flow/config.yaml\n")
            pass

        # Add subcommands
        ssh_keys_group.add_command(list)
        ssh_keys_group.add_command(details)
        ssh_keys_group.add_command(delete)
        ssh_keys_group.add_command(upload)

        return ssh_keys_group


# Export command instance
command = SSHKeysCommand()
