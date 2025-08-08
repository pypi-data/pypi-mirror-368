"""Mount command - Attach volumes to running tasks.

This module implements the mount command for dynamically attaching
storage volumes to already running tasks without requiring restart.

Command Usage:
    flow mount VOLUME_ID TASK_ID
    flow mount VOLUME_ID TASK_ID --mount-point /custom/path

Examples:
    Mount by volume ID:
        $ flow mount vol_abc123def456 task_xyz789

    Mount by volume name:
        $ flow mount training-data gpu-job-1

    Mount using indices:
        $ flow mount :1 :2

    Mount with custom path:
        $ flow mount datasets ml-training --mount-point /data/training

The mount operation:
1. Validates volume and task exist
2. Checks region compatibility
3. Updates task configuration via API
4. Executes mount command via SSH
5. Volume becomes available at /mnt/{volume_name}

Requirements:
- Task must be running (not pending or terminated)
- Volume and task must be in same region
- Volume cannot already be attached to the task
- SSH access must be available to the task
"""

import click
import re
from typing import Optional, Tuple

from flow import Flow
from flow.errors import (
    AuthenticationError,
    ResourceNotFoundError,
    ValidationError,
)
from flow.providers.mithril.remote_operations import RemoteExecutionError

from .base import BaseCommand, console
from ..utils.task_resolver import resolve_task_identifier
from ..utils.volume_resolver import resolve_volume_identifier, get_volume_display_name
from ..utils.animated_progress import AnimatedEllipsisProgress


class MountCommand(BaseCommand):
    """Mount volumes to running tasks."""

    def validate_mount_point(self, mount_point: str) -> Optional[str]:
        """Validate and sanitize a custom mount point.

        Args:
            mount_point: User-provided mount path

        Returns:
            Sanitized mount path or None if invalid

        Raises:
            ValidationError: If mount point is invalid
        """
        if not mount_point:
            return None

        # Must be absolute path
        if not mount_point.startswith("/"):
            raise ValidationError("Mount point must be an absolute path (start with '/')")

        # Check for path traversal
        if ".." in mount_point:
            raise ValidationError("Mount point cannot contain '..' (path traversal)")

        # Check allowed prefixes
        allowed_prefixes = ["/mnt/", "/data/", "/opt/", "/var/"]
        if not any(mount_point.startswith(prefix) for prefix in allowed_prefixes):
            raise ValidationError(
                f"Mount point must start with one of: {', '.join(allowed_prefixes)}"
            )

        # Check length
        if len(mount_point) > 255:
            raise ValidationError("Mount point path too long (max 255 characters)")

        # Check valid characters
        if not re.match(r"^/[a-zA-Z0-9/_-]+$", mount_point):
            raise ValidationError(
                "Mount point can only contain letters, numbers, hyphens, underscores, and slashes"
            )

        return mount_point

    @property
    def name(self) -> str:
        return "mount"

    @property
    def help(self) -> str:
        return "Attach storage volumes to running tasks - no restart required"

    def get_command(self) -> click.Command:
        """Return the mount command."""
        # Import completion functions
        from ..utils.shell_completion import complete_volume_ids, complete_task_ids

        @click.command(name=self.name, help=self.help)
        @click.argument("volume_identifier", required=False, shell_complete=complete_volume_ids)
        @click.argument("task_identifier", required=False, shell_complete=complete_task_ids)
        @click.option(
            "--volume", "-v", help="Volume ID or name to mount", shell_complete=complete_volume_ids
        )
        @click.option(
            "--task", "-t", help="Task ID or name to mount to", shell_complete=complete_task_ids
        )
        @click.option(
            "--instance",
            "-i",
            type=int,
            help="Specific instance index (0-based) for multi-instance tasks",
        )
        @click.option(
            "--mount-point",
            "-m",
            type=str,
            help="Custom mount path on the instance (default: /mnt/{volume_name})",
        )
        @click.option(
            "--dry-run", is_flag=True, help="Preview the mount operation without executing"
        )
        @click.option(
            "--verbose",
            "-V",
            is_flag=True,
            help="Show detailed mount workflows and troubleshooting",
        )
        def mount(
            volume_identifier: Optional[str],
            task_identifier: Optional[str],
            volume: Optional[str],
            task: Optional[str],
            instance: Optional[int],
            mount_point: Optional[str],
            dry_run: bool,
            verbose: bool,
        ):
            """Mount a volume to a running task.

            \b
            Examples:
                flow mount vol-abc123 my-task    # Mount by IDs/names
                flow mount dataset training-job   # Mount by names
                flow mount :1 :2                  # Mount by indices
                flow mount -v data -t task -i 0   # Specific instance
                flow mount vol-123 task-456 --mount-point /data/datasets  # Custom path

            Use 'flow mount --verbose' for detailed workflows and troubleshooting.
            """
            if verbose:
                console.print("\n[bold]Volume Mounting Guide:[/bold]\n")
                console.print("Basic usage:")
                console.print("  flow mount VOLUME TASK            # Positional arguments")
                console.print("  flow mount -v VOLUME -t TASK      # Using flags")
                console.print("  flow mount --dry-run VOLUME TASK  # Preview operation\n")

                console.print("Multi-instance tasks:")
                console.print("  flow mount data distributed-job -i 0    # Mount to head node")
                console.print("  flow mount data distributed-job -i 1    # Mount to worker")
                console.print(
                    "  flow mount data distributed-job         # Mount to all instances\n"
                )

                console.print("Selection methods:")
                console.print("  flow mount vol_abc123 task_xyz789       # By full IDs")
                console.print("  flow mount training-data my-job         # By names")
                console.print(
                    "  flow mount :1 :2                        # By index from listings\n"
                )

                console.print("Mount locations:")
                console.print("  • Default: /mnt/{volume_name}")
                console.print("  • Example: volume 'datasets' → /mnt/datasets")
                console.print("  • Custom: --mount-point /data/my-volume")
                console.print("  • Allowed prefixes: /mnt/, /data/, /opt/, /var/")
                console.print("  • Access: cd /mnt/datasets\n")

                console.print("Common workflows:")
                console.print("  # Mount dataset to running training")
                console.print("  flow volumes list                 # Find volume")
                console.print("  flow status                       # Find task")
                console.print("  flow mount dataset training-job   # Mount it")
                console.print("  ")
                console.print("  # Share data between tasks")
                console.print("  flow mount shared-data task1")
                console.print("  flow mount shared-data task2\n")

                console.print("Requirements:")
                console.print("  • Task must be running (not pending)")
                console.print("  • Volume and task in same region")
                console.print("  • Volume not already mounted")
                console.print("  • SSH access available\n")

                console.print("Troubleshooting:")
                console.print("  • Permission denied → Check volume exists: flow volumes list")
                console.print("  • Task not found → Verify running: flow status")
                console.print("  • Region mismatch → Create volume in task's region")
                console.print("  • Mount failed → Check SSH: flow ssh <task>\n")
                return
            try:
                flow_client = Flow(auto_init=True)

                # Handle both positional and flag-based arguments
                volume_id = volume or volume_identifier
                task_id = task or task_identifier

                # Track if we used interactive selection
                selected_volume = None
                selected_task = None

                # Interactive selection if arguments are missing
                if not volume_id:
                    # Get available volumes
                    from ..utils.interactive_selector import select_volume

                    volumes = flow_client.list_volumes()
                    if not volumes:
                        console.print("[yellow]No volumes available.[/yellow]")
                        console.print(
                            "\nCreate a volume with: [cyan]flow volumes create --size 100[/cyan]"
                        )
                        return

                    selected_volume = select_volume(volumes, title="Select a volume to mount")
                    if not selected_volume:
                        console.print("[yellow]No volume selected.[/yellow]")
                        return
                    volume_id = selected_volume.volume_id
                    # Debug: Show what we selected
                    if verbose:
                        console.print(f"[dim]Selected volume ID: {volume_id}[/dim]")

                if not task_id:
                    # Get running tasks
                    from ..utils.interactive_selector import select_task

                    tasks = [
                        t
                        for t in flow_client.list_tasks()
                        if t.status.lower() in ["running", "active"]
                    ]
                    if not tasks:
                        console.print("[yellow]No running tasks available.[/yellow]")
                        console.print("\nStart a task with: [cyan]flow run[/cyan]")
                        return

                    selected_task = select_task(tasks, title="Select a task to mount to")
                    if not selected_task:
                        console.print("[yellow]No task selected.[/yellow]")
                        return
                    task_id = selected_task.task_id

                # Resolve volume (skip if we already have it from interactive selection)
                if selected_volume:
                    volume = selected_volume
                    volume_display = get_volume_display_name(volume)
                else:
                    with AnimatedEllipsisProgress(console, "Resolving volume") as progress:
                        volume, volume_error = resolve_volume_identifier(flow_client, volume_id)
                        if volume_error:
                            console.print(f"[red]Error:[/red] {volume_error}")
                            return
                        volume_display = get_volume_display_name(volume)

                # Resolve task (skip if we already have it from interactive selection)
                if selected_task:
                    task = selected_task
                    task_display = task.name or task.task_id
                else:
                    with AnimatedEllipsisProgress(console, "Resolving task") as progress:
                        task, task_error = resolve_task_identifier(flow_client, task_id)
                        if task_error:
                            console.print(f"[red]Error:[/red] {task_error}")
                            return
                        task_display = task.name or task.task_id

                # Validate mount point if provided
                validated_mount_point = None
                if mount_point:
                    try:
                        validated_mount_point = self.validate_mount_point(mount_point)
                    except ValidationError as e:
                        console.print(f"[red]Error:[/red] {e}")
                        return

                # Show what we're about to mount
                console.print(
                    f"\nMounting volume [cyan]{volume_display}[/cyan] to task [cyan]{task_display}[/cyan]"
                )

                # Multi-instance check
                num_instances = getattr(
                    task, "num_instances", len(task.instances) if hasattr(task, "instances") else 1
                )
                if num_instances > 1:
                    # Check if volume is a file share (supports multi-instance)
                    is_file_share = hasattr(volume, "interface") and volume.interface == "file"

                    if is_file_share:
                        console.print(
                            f"[green]✓[/green] File share volume can be mounted to all {num_instances} instances"
                        )
                    else:
                        # Block storage cannot be multi-attached
                        console.print(
                            f"[red]Error:[/red] Cannot mount block storage to multi-instance task ({num_instances} nodes)"
                        )
                        console.print(
                            "[yellow]Suggestion:[/yellow] Use file storage (--type file) for multi-instance tasks"
                        )
                        console.print("\nOptions:")
                        console.print(
                            "  • Create a file share volume: [cyan]flow volumes create --interface file --size 100[/cyan]"
                        )
                        console.print(
                            "  • Use an existing file share: [cyan]flow volumes list --interface file[/cyan]"
                        )
                        console.print("  • Mount to a single-instance task instead")
                        return

                # Check task status
                if task.status.lower() not in ["running", "active"]:
                    console.print(
                        f"[yellow]Warning:[/yellow] Task is {task.status}. Mount may fail if task is not fully running."
                    )

                # Determine mount path
                if validated_mount_point:
                    actual_mount_path = validated_mount_point
                else:
                    actual_mount_path = f"/mnt/{volume.name or f'volume-{volume.id[-6:]}'}"

                # Dry run mode
                if dry_run:
                    console.print("\n[cyan]DRY RUN - No changes will be made[/cyan]")
                    console.print(f"Would mount volume {volume.id} to task {task.task_id}")
                    if instance is not None:
                        console.print(f"Target instance: {instance}")
                    else:
                        console.print(f"Target instances: ALL ({num_instances} instances)")
                    console.print(f"Mount path: {actual_mount_path}")
                    return

                # Perform the attachment (and optional mount)
                # Change message to be more accurate about what we're doing
                action_msg = (
                    "Attaching volume"
                    if task.status.lower() in ["pending", "starting"]
                    else "Mounting volume"
                )

                with AnimatedEllipsisProgress(console, action_msg) as progress:
                    try:
                        # TODO: Update mount_volume to accept instance parameter
                        # For now, mount to all instances (current behavior)
                        if instance is not None:
                            console.print(
                                f"[yellow]Note:[/yellow] Instance-specific mounting not yet implemented. Mounting to all instances."
                            )
                        # Pass custom mount point if provided
                        if validated_mount_point:
                            flow_client.mount_volume(
                                volume.id, task.task_id, mount_point=validated_mount_point
                            )
                        else:
                            flow_client.mount_volume(volume.id, task.task_id)
                    except ValidationError as e:
                        console.print(f"[red]Validation Error:[/red] {e}")
                        return
                    except RemoteExecutionError as e:
                        console.print(f"[red]Mount Failed:[/red] {e}")
                        console.print("\n[yellow]Troubleshooting:[/yellow]")
                        console.print("  - Ensure the task is fully running (SSH ready)")
                        console.print("  - Check that the volume is not already mounted")
                        console.print("  - Verify region compatibility")
                        return

                # Success - use the actual mount path we determined earlier
                mount_path = actual_mount_path

                # Check if task is still starting
                if task.status.lower() in ["pending", "starting", "initializing"]:
                    console.print(
                        f"[green]✓[/green] Volume attached to task. Mount will complete when instance is ready."
                    )
                    console.print(
                        f"\n[yellow]Note:[/yellow] Task is still starting. The volume will be available at "
                        f"[cyan]{mount_path}[/cyan] once the instance is running."
                    )
                    console.print(
                        f"\nMithril instances can take several minutes to start. To check status:"
                    )
                    task_ref = task.name or task.task_id
                    self.show_next_actions(
                        [
                            f"Check task status: [cyan]flow status {task_ref}[/cyan]",
                            f"Wait for SSH and mount: [cyan]flow ssh {task_ref} -c 'df -h {mount_path}'[/cyan]",
                            f"Stream startup logs: [cyan]flow logs {task_ref} -f[/cyan]",
                        ]
                    )
                else:
                    # Instance is running, mount should be immediate
                    console.print(
                        f"[green]✓[/green] Volume mounted successfully at [cyan]{mount_path}[/cyan]"
                    )
                    console.print(
                        f"\n[yellow]Note:[/yellow] In some cases, the instance may need to be restarted for the mount to take effect."
                    )
                    task_ref = task.name or task.task_id
                    self.show_next_actions(
                        [
                            f"SSH into task: [cyan]flow ssh {task_ref}[/cyan]",
                            f"Verify mount: [cyan]flow ssh {task_ref} -c 'df -h {mount_path}'[/cyan]",
                            "List all volumes: [cyan]flow volumes list[/cyan]",
                        ]
                    )

            except AuthenticationError:
                self.handle_auth_error()
            except ResourceNotFoundError as e:
                console.print(f"[red]Not Found:[/red] {e}")
            except Exception as e:
                self.handle_error(str(e))

        return mount


# Export command instance
command = MountCommand()
