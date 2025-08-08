"""Volumes command group - Manage persistent storage volumes for GPU tasks.

This module implements the volumes command group for the Flow CLI. It provides
comprehensive volume management capabilities including creation, deletion,
listing, and bulk operations for persistent storage used by GPU compute tasks.

Command Usage:
    flow volumes SUBCOMMAND [OPTIONS]

Subcommands:
    list        List all volumes with region and interface info
    create      Create a new volume
    delete      Delete a volume by ID or name
    delete-all  Delete multiple volumes

Examples:
    List all volumes:
        $ flow volumes list

    Create a 100GB block volume:
        $ flow volumes create --size 100

    Create a named file storage volume:
        $ flow volumes create --size 50 --name training-data --interface file

    Delete by volume ID:
        $ flow volumes delete vol_abc123def456

    Delete by volume name (exact or partial match):
        $ flow volumes delete training-data
        $ flow volumes delete training  # Works if only one match

    Delete without confirmation:
        $ flow volumes delete training-data --yes

    Delete all volumes (with confirmation):
        $ flow volumes delete-all

    Delete volumes matching pattern:
        $ flow volumes delete-all --pattern "test-*"

    Preview deletion without executing:
        $ flow volumes delete-all --dry-run

Volume properties:
- ID: Unique identifier (e.g., vol_abc123...)
- Name: Optional human-readable name (can be used instead of ID)
- Region: Where the volume is located (must match task region)
- Size: Storage capacity in GB
- Interface: Storage type (block or file)
- Status: Available or attached (with count)
- Created: Timestamp of creation

The commands will:
- Support both volume IDs and names for operations
- Show region constraints for better planning
- Validate size limits per region
- Handle volume lifecycle operations
- Manage volume attachments to tasks

Note:
    Volumes can only be deleted when not attached to running tasks.
    Volumes must be in the same region as the tasks that use them.
    Both volume IDs and names can be used in task configurations.

    Name Resolution:
    - You can use either volume ID (vol_xxx) or volume name in commands
    - Exact name matches are preferred over partial matches
    - If multiple volumes match a name, you'll be prompted to use the ID
    - Partial name matching works if there's only one match
"""

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, Optional, Tuple

import click
from rich.table import Table

from flow import Flow
from flow.errors import AuthenticationError

from .base import BaseCommand, console
from ..utils.volume_operations import VolumeOperations, BulkOperationResults
from ..utils.table_styles import create_flow_table, wrap_table_in_panel, add_centered_column
from ..utils.theme_manager import theme_manager
from ..utils.volume_resolver import resolve_volume_identifier, get_volume_display_name
from ..utils.volume_index_cache import VolumeIndexCache
from ..utils.animated_progress import AnimatedEllipsisProgress
from ..utils.terminal_adapter import TerminalAdapter


class VolumesCommand(BaseCommand):
    """Manage storage volumes."""

    @property
    def name(self) -> str:
        return "volumes"

    @property
    def help(self) -> str:
        return "Manage persistent storage volumes - create, list, delete"

    def _build_instance_task_map(self, flow_client: Flow) -> Dict[str, Tuple[str, str]]:
        """Build mapping of instance_id -> (task_name, task_id).

        Returns empty dict on error to gracefully degrade.
        """
        try:
            # Fetch recent tasks to find volume associations
            tasks = flow_client.list_tasks(limit=500)
            instance_map = {}
            for task in tasks:
                # Map each instance to its task
                for instance_id in task.instances:
                    instance_map[instance_id] = (task.name, task.task_id)
            return instance_map
        except Exception:
            # Graceful degradation - volumes still display without task info
            return {}

    def get_command(self) -> click.Group:
        """Return the volumes command group."""

        @click.group(name=self.name, help=self.help)
        @click.option("--verbose", "-v", is_flag=True, help="Show detailed volume management guide")
        def volumes(verbose: bool):
            """Manage storage volumes.

            \b
            Examples:
                flow volumes list            # List all volumes
                flow volumes create --size 100  # Create 100GB volume
                flow volumes delete vol-123  # Delete volume

            Use 'flow volumes --verbose' for comprehensive storage guide.
            """
            if verbose:
                console.print("\n[bold]Storage Volume Management:[/bold]\n")
                console.print("Volume types:")
                console.print("  • block - High-performance block storage (default)")
                console.print("  • file  - Shared file storage (NFS-like)\n")

                console.print("Creating volumes:")
                console.print(
                    "  flow volumes create --size 100                # 100GB block volume"
                )
                console.print(
                    "  flow volumes create --size 50 --interface file # 50GB file storage"
                )
                console.print("  flow volumes create --size 200 --name datasets # Named volume")
                console.print("  flow volumes create --size 500 --region us-west-2\n")

                console.print("Listing and filtering:")
                console.print("  flow volumes list                    # All volumes")
                console.print("  flow volumes list --details          # Show task attachments")
                console.print("  flow volumes list | grep available   # Filter by status\n")

                console.print("Deleting volumes:")
                console.print("  flow volumes delete vol_abc123       # By ID")
                console.print("  flow volumes delete training-data    # By name")
                console.print("  flow volumes delete-all --pattern 'test-*'  # Pattern matching")
                console.print("  flow volumes delete-all --dry-run    # Preview deletions\n")

                console.print("Using volumes in tasks:")
                console.print("  # In YAML config:")
                console.print("  volumes:")
                console.print("    - volume_id: vol_abc123")
                console.print("      mount_path: /data")
                console.print("  # Or by name:")
                console.print("    - volume_name: training-data")
                console.print("      mount_path: /datasets\n")

                console.print("Important constraints:")
                console.print("  • Volumes are region-specific")
                console.print("  • Can't delete volumes attached to running tasks")
                console.print("  • Size limits vary by region (check provider docs)")
                console.print("  • File volumes support multiple concurrent attachments\n")

                console.print("Common workflows:")
                console.print("  # Create and use dataset volume")
                console.print("  flow volumes create --size 500 --name imagenet")
                console.print("  flow run train.yaml  # References volume by name")
                console.print("  ")
                console.print("  # Share data between tasks")
                console.print("  flow mount shared-data task1")
                console.print("  flow mount shared-data task2\n")
            pass

        # Add subcommands
        volumes.add_command(self._list_command())
        volumes.add_command(self._create_command())
        volumes.add_command(self._delete_command())
        volumes.add_command(self._delete_all_command())

        return volumes

    def _list_command(self) -> click.Command:
        @click.command(name="list")
        @click.option("--details", "-d", is_flag=True, help="Show which tasks use each volume")
        def volumes_list(details: bool):
            """List all volumes."""
            try:
                flow_client = Flow(auto_init=True)

                with AnimatedEllipsisProgress(console, "Fetching volumes") as progress:
                    volumes = flow_client.list_volumes()

                if not volumes:
                    console.print("\nNo volumes found.")
                    self.show_next_actions(
                        [
                            "Create a new volume: [cyan]flow volumes create --size 100[/cyan]",
                            "Create a named volume: [cyan]flow volumes create --size 50 --name training-data[/cyan]",
                            "Create file storage: [cyan]flow volumes create --size 200 --interface file[/cyan]",
                        ]
                    )
                    return

                # Build instance-to-task mapping if details requested
                instance_task_map = {}
                if details:
                    with AnimatedEllipsisProgress(
                        console, "Fetching task associations"
                    ) as progress:
                        instance_task_map = self._build_instance_task_map(flow_client)

                # Get terminal width for responsive layout
                terminal_width = TerminalAdapter.get_terminal_width()

                # Create table with Flow standard styling
                table = create_flow_table(
                    show_borders=False
                )  # No borders since we'll wrap in panel

                # Always show core columns
                add_centered_column(
                    table,
                    "Name",
                    style=theme_manager.get_color("task.name"),
                    ratio=1,  # Gets remaining space
                    overflow="ellipsis",
                    min_width=20,  # Ensure reasonable minimum
                )
                add_centered_column(
                    table,
                    "Region",
                    style=theme_manager.get_color("accent"),
                    width=15,  # Fixed width for regions like "us-central1-b"
                    overflow="crop",  # Never wrap
                )
                add_centered_column(
                    table,
                    "Size\n(GB)",  # Split header to save width
                    width=8,  # Fixed for "10000" max
                )

                # Show additional columns based on terminal width
                show_interface = terminal_width >= 80
                show_status = terminal_width >= 90
                show_created = terminal_width >= 100

                if show_interface:
                    add_centered_column(
                        table,
                        "Interface",
                        style=theme_manager.get_color("muted"),
                        width=9,  # Fixed for "block"/"file"
                    )
                if show_status:
                    add_centered_column(table, "Status", width=14)  # Fixed for "attached (99)"
                if show_created:
                    add_centered_column(
                        table,
                        "Created",
                        style=theme_manager.get_color("task.time"),
                        width=16,  # Fixed for "2025-07-29 20:32"
                    )

                for volume in volumes:
                    # Format status with color
                    status = "[green]available[/green]"
                    task_names = []

                    if hasattr(volume, "attached_to") and volume.attached_to:
                        # Collect task names if details requested
                        if details and instance_task_map:
                            for instance_id in volume.attached_to:
                                if instance_id in instance_task_map:
                                    task_name, _ = instance_task_map[instance_id]
                                    task_names.append(task_name)

                        # Format status based on whether we have task details
                        if task_names and details:
                            # Show task names (limit to 2 for space)
                            task_list = ", ".join(task_names[:2])
                            if len(task_names) > 2:
                                task_list += f" +{len(task_names) - 2}"
                            status = f"[yellow]{task_list}[/yellow]"
                        else:
                            status = f"[yellow]attached ({len(volume.attached_to)})[/yellow]"

                    # Get interface type
                    interface = getattr(volume, "interface", "block")
                    if hasattr(interface, "value"):
                        interface = interface.value

                    # Use volume ID as name if no name is set
                    display_name = volume.name or volume.volume_id

                    # Build row data based on visible columns
                    row_data = [display_name, volume.region, str(volume.size_gb)]

                    if show_interface:
                        row_data.append(interface)
                    if show_status:
                        row_data.append(status)
                    if show_created:
                        row_data.append(
                            volume.created_at.strftime("%Y-%m-%d %H:%M")
                            if volume.created_at
                            else "-"
                        )

                    table.add_row(*row_data)

                    # Add detail rows if requested and volume has attachments
                    if details and task_names and terminal_width >= 100:
                        for i, (instance_id, task_name) in enumerate(
                            (inst_id, instance_task_map.get(inst_id, ("Unknown", ""))[0])
                            for inst_id in volume.attached_to
                            if inst_id in instance_task_map
                        ):
                            if i >= 3:  # Limit detail rows
                                remaining = len(volume.attached_to) - 3
                                detail_row = ["  └─ ...", "", ""]
                                if show_interface:
                                    detail_row.append("")
                                if show_status:
                                    detail_row.append(f"[dim]+{remaining} more[/dim]")
                                if show_created:
                                    detail_row.append("")
                                table.add_row(*detail_row)
                                break

                            task_id = instance_task_map[instance_id][1]
                            detail_row = [f"  └─ {task_name}", "", ""]
                            if show_interface:
                                detail_row.append("")
                            if show_status:
                                detail_row.append(f"[dim]{task_id[:8]}[/dim]")
                            if show_created:
                                detail_row.append("")
                            table.add_row(*detail_row)

                # Save indices for quick reference
                cache = VolumeIndexCache()
                cache.save_indices(volumes)

                # Wrap in panel like flow status does
                wrap_table_in_panel(table, f"Volumes ({len(volumes)} total)", console)

                # Show next actions with index support
                volume_count = min(len(volumes), 5)  # Show up to 5 index examples
                index_help = f":1-{volume_count}" if volume_count > 1 else ":1"

                self.show_next_actions(
                    [
                        "Create a new volume: [cyan]flow volumes create --size 100[/cyan]",
                        f"Delete a volume: [cyan]flow volumes delete <volume-name-or-id>[/cyan] or [cyan]flow volumes delete {index_help}[/cyan]",
                    ]
                )

            except AuthenticationError:
                self.handle_auth_error()
            except Exception as e:
                self.handle_error(str(e))

        return volumes_list

    def _create_command(self) -> click.Command:
        @click.command(name="create")
        @click.option("--size", "-s", type=int, required=True, help="Volume size in GB")
        @click.option("--name", "-n", help="Optional name for the volume")
        @click.option(
            "--interface",
            "-i",
            type=click.Choice(["block", "file"]),
            default="block",
            help="Storage interface type",
        )
        def volumes_create(size: int, name: Optional[str], interface: str):
            """Create a new volume."""
            try:
                flow_client = Flow(auto_init=True)

                from ..utils.animated_progress import AnimatedEllipsisProgress

                with AnimatedEllipsisProgress(
                    console, f"Creating {size}GB {interface} volume"
                ) as progress:
                    volume = flow_client.create_volume(size_gb=size, name=name, interface=interface)

                console.print(f"[green]✓[/green] Volume created: [cyan]{volume.volume_id}[/cyan]")
                if name:
                    console.print(f"Name: {name}")

                # Show next actions
                self.show_next_actions(
                    [
                        "List all volumes: [cyan]flow volumes list[/cyan]",
                        f"Use in task config: Add to YAML under storage.volumes",
                        "Submit task with volume: [cyan]flow run task.yaml[/cyan]",
                    ]
                )

            except AuthenticationError:
                self.handle_auth_error()
            except Exception as e:
                # Check if provider supports capability discovery
                if "not available" in str(e) or "maximum" in str(e).lower():
                    # Show storage capabilities if available
                    try:
                        caps = (
                            flow_client.provider.get_storage_capabilities()
                            if hasattr(flow_client.provider, "get_storage_capabilities")
                            else None
                        )
                        if caps:
                            console.print("\n[yellow]Available storage options:[/yellow]")
                            for region, cap in caps.items():
                                if cap.get("available", False):
                                    types = ", ".join(cap.get("types", []))
                                    max_gb = cap.get("max_gb", 0)
                                    console.print(
                                        f"  [cyan]{region}[/cyan]: {types} (up to {max_gb:,}GB)"
                                    )
                    except Exception:
                        pass  # Don't fail if capability discovery fails

                self.handle_error(str(e))

        return volumes_create

    def _delete_command(self) -> click.Command:
        # Import completion function
        from ..utils.shell_completion import complete_volume_ids

        @click.command(name="delete")
        @click.argument("volume_identifier", shell_complete=complete_volume_ids)
        @click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
        def volumes_delete(volume_identifier: str, yes: bool):
            """Delete a volume by ID, name, or 'all'.

            \b
            Examples:
                flow volumes delete vol_abc123def456
                flow volumes delete training-data
                flow volumes delete :1
                flow volumes delete all
                flow volumes delete training --yes
            """
            try:
                flow_client = Flow(auto_init=True)

                # Special handling for "all"
                if volume_identifier.lower() == "all":
                    volumes = flow_client.list_volumes()
                    if not volumes:
                        console.print("No volumes found.")
                        return

                    console.print(f"Found {len(volumes)} volume(s) to delete:")
                    for volume in volumes:
                        display_name = get_volume_display_name(volume)
                        console.print(f"  - {display_name}")

                    if not yes:
                        confirm = click.confirm(f"\nDelete all {len(volumes)} volume(s)?")
                        if not confirm:
                            console.print("Cancelled")
                            return

                    # Delete all volumes
                    from ..utils.animated_progress import AnimatedEllipsisProgress

                    deleted_count = 0
                    with AnimatedEllipsisProgress(
                        console, f"Deleting {len(volumes)} volumes"
                    ) as progress:
                        for i, volume in enumerate(volumes):
                            volume_name = get_volume_display_name(volume)
                            progress.base_message = (
                                f"Deleting {volume_name} ({i + 1}/{len(volumes)})"
                            )
                            try:
                                flow_client.delete_volume(volume.volume_id)
                                console.print(f"[green]✓[/green] Deleted {volume_name}")
                                deleted_count += 1
                            except Exception as e:
                                console.print(f"[red]✗[/red] Failed to delete {volume_name}: {e}")

                    console.print(f"\nDeleted {deleted_count} volume(s)")
                else:
                    # Resolve volume identifier to actual volume
                    volume, error = resolve_volume_identifier(flow_client, volume_identifier)
                    if error:
                        console.print(f"[red]Error:[/red] {error}")
                        return

                    # Get display name for confirmation
                    display_name = get_volume_display_name(volume)

                    if not yes:
                        confirm = click.confirm(f"Delete volume {display_name}?")
                        if not confirm:
                            console.print("Cancelled")
                            return

                    from ..utils.animated_progress import AnimatedEllipsisProgress

                    with AnimatedEllipsisProgress(
                        console, f"Deleting volume {display_name}"
                    ) as progress:
                        flow_client.delete_volume(volume.volume_id)
                    console.print(f"[green]✓[/green] Volume {display_name} deleted")

                # Show next actions
                self.show_next_actions(
                    [
                        "List remaining volumes: [cyan]flow volumes list[/cyan]",
                        "Create a new volume: [cyan]flow volumes create --size 100[/cyan]",
                    ]
                )

            except AuthenticationError:
                self.handle_auth_error()
            except Exception as e:
                self.handle_error(str(e))

        return volumes_delete

    def _delete_all_command(self) -> click.Command:
        @click.command(name="delete-all")
        @click.option("--pattern", "-p", help="Only delete volumes matching pattern")
        @click.option("--dry-run", is_flag=True, help="Show what would be deleted")
        @click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
        def volumes_delete_all(pattern: Optional[str], dry_run: bool, yes: bool):
            """Delete all volumes (with optional pattern matching)."""
            try:
                flow_client = Flow(auto_init=True)
                volume_ops = VolumeOperations(flow_client)

                # Find volumes matching pattern
                matching_volumes, _ = volume_ops.find_volumes_by_pattern(pattern)

                if not matching_volumes:
                    if pattern:
                        console.print(f"No volumes found matching pattern: {pattern}")
                    else:
                        console.print("No volumes found.")
                    return

                # Show what will be deleted
                console.print(f"Found {len(matching_volumes)} volume(s) to delete:")
                for volume_str in volume_ops.format_volume_summary(matching_volumes):
                    console.print(f"  - {volume_str}")

                if dry_run:
                    console.print("\n[yellow]Dry run - no volumes deleted[/yellow]")
                    return

                # Confirm deletion
                if not yes:
                    confirm = click.confirm(f"\nDelete {len(matching_volumes)} volume(s)?")
                    if not confirm:
                        console.print("Cancelled")
                        return

                # Delete volumes with progress callback
                def progress_callback(result):
                    if result.success:
                        console.print(f"[green]✓[/green] Deleted {result.volume_id}")
                    else:
                        console.print(
                            f"[red]✗[/red] Failed to delete {result.volume_id}: {result.error}"
                        )

                results = volume_ops.delete_volumes(matching_volumes, progress_callback)

                # Summary
                console.print(f"\nDeleted {results.succeeded} volume(s)")
                if results.failed > 0:
                    console.print(f"[red]Failed to delete {results.failed} volume(s)[/red]")

                # Show next actions
                self.show_next_actions(
                    [
                        "List remaining volumes: [cyan]flow volumes list[/cyan]",
                        "Create a new volume: [cyan]flow volumes create --size 100[/cyan]",
                    ]
                )

            except AuthenticationError:
                self.handle_auth_error()
            except Exception as e:
                self.handle_error(str(e))

        return volumes_delete_all


# Export command instance
command = VolumesCommand()
