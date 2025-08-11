"""Mount command - attach volumes to tasks.

Dynamically attaches storage volumes to tasks. If the task isn't running yet,
the volume attachment completes now and the mount finalizes when the task
starts and is SSH-ready.

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
- Task can be pending/starting; mount finalizes when the task is ready (SSH available)
- Volume and task must be in same region
- Volume cannot already be attached to the task
- SSH access is required only for immediate mount; otherwise completes on startup
"""

import re

import click

from flow import Flow
from flow.cli.commands.base import BaseCommand, console
from flow.cli.utils.animated_progress import AnimatedEllipsisProgress
from flow.cli.utils.task_resolver import resolve_task_identifier
from flow.cli.utils.volume_resolver import get_volume_display_name, resolve_volume_identifier
from flow.errors import (
    AuthenticationError,
    RemoteExecutionError,
    ResourceNotFoundError,
    ValidationError,
)


class MountCommand(BaseCommand):
    """Mount volumes to tasks (finalizes when task is ready)."""

    def validate_mount_point(self, mount_point: str) -> str | None:
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
        allowed_prefixes = ["/volumes/", "/mnt/", "/data/", "/opt/", "/var/"]
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
        return "Attach storage volumes to tasks (may require machine restart to take effect)"

    def get_command(self) -> click.Command:
        """Return the mount command."""
        # Import completion functions
        from flow.cli.utils.mode import demo_aware_command
        from flow.cli.utils.shell_completion import complete_task_ids, complete_volume_ids

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
            help="Custom mount path on the instance (default: /volumes/{volume_name})",
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
        @demo_aware_command()
        def mount(
            volume_identifier: str | None,
            task_identifier: str | None,
            volume: str | None,
            task: str | None,
            instance: int | None,
            mount_point: str | None,
            dry_run: bool,
            verbose: bool,
        ):
            """Mount a volume to a task.

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
                console.print("  • Default: /volumes/{volume_name}")
                console.print("  • Example: volume 'datasets' → /volumes/datasets")
                console.print("  • Custom: --mount-point /data/my-volume")
                console.print("  • Allowed prefixes: /volumes/, /mnt/, /data/, /opt/, /var/")
                console.print("  • Access: cd /volumes/datasets\n")

                console.print("Common workflows:")
                console.print("  # Mount dataset to a training job")
                console.print("  flow volumes list                 # Find volume")
                console.print("  flow status                       # Find task")
                console.print("  flow mount dataset training-job   # Mount it")
                console.print("  ")
                console.print("  # Share data between tasks")
                console.print("  flow mount shared-data task1")
                console.print("  flow mount shared-data task2\n")

                console.print("Requirements:")
                console.print("  • Task can be pending; mount finalizes when task starts")
                console.print("  • Volume and task in same region")
                console.print("  • Volume not already mounted")
                console.print("  • SSH access available\n")

                console.print("Troubleshooting:")
                console.print("  • Permission denied → Check volume exists: flow volumes list")
                console.print("  • Task not found → Verify status: flow status")
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
                    from flow.cli.utils.interactive_selector import select_volume

                    volumes = flow_client.list_volumes()
                    if not volumes:
                        console.print("[yellow]No volumes available.[/yellow]")
                        console.print(
                            "\nCreate a volume with: [accent]flow volumes create --size 100[/accent]"
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
                    # Get available tasks
                    from flow.cli.utils.interactive_selector import select_task
                    from flow.cli.utils.status_utils import is_active_like

                    tasks = [t for t in flow_client.list_tasks() if is_active_like(t)]
                    if not tasks:
                        console.print("[yellow]No eligible tasks available.[/yellow]")
                        console.print("\nStart a task with: [accent]flow run[/accent]")
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
                        from rich.markup import escape

                        console.print(f"[red]Error:[/red] {escape(str(e))}")
                        return

                # Show what we're about to mount
                console.print(
                    f"\nMounting volume [accent]{volume_display}[/accent] to task [accent]{task_display}[/accent]"
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
                            "  • Create a file share volume: [accent]flow volumes create --interface file --size 100[/accent]"
                        )
                        console.print(
                            "  • Use an existing file share: [accent]flow volumes list --interface file[/accent]"
                        )
                        console.print("  • Mount to a single-instance task instead")
                        return

                # Check task status
                if task.status.lower() not in ["running", "active"]:
                    console.print(
                        f"[yellow]Note:[/yellow] Task is {task.status}. The attachment will complete now; the mount will finalize when the task is ready (SSH available)."
                    )

                # Determine mount path
                if validated_mount_point:
                    actual_mount_path = validated_mount_point
                else:
                    actual_mount_path = f"/volumes/{volume.name or f'volume-{volume.id[-6:]}'}"

                # Dry run mode
                if dry_run:
                    console.print("\n[accent]DRY RUN - No changes will be made[/accent]")
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
                                "[yellow]Note:[/yellow] Instance-specific mounting not yet implemented. Mounting to all instances."
                            )
                        # Pass custom mount point if provided
                        if validated_mount_point:
                            flow_client.mount_volume(
                                volume.id, task.task_id, mount_point=validated_mount_point
                            )
                        else:
                            flow_client.mount_volume(volume.id, task.task_id)
                    except ValidationError as e:
                        from rich.markup import escape

                        console.print(f"[red]Validation Error:[/red] {escape(str(e))}")
                        return
                    except RemoteExecutionError as e:
                        from rich.markup import escape

                        console.print(f"[red]Mount Failed:[/red] {escape(str(e))}")
                        console.print("\n[yellow]Troubleshooting:[/yellow]")
                        console.print("  - Ensure the task is ready (SSH available)")
                        console.print("  - Check that the volume is not already mounted")
                        console.print("  - Verify region compatibility")
                        return

                # Success - use the actual mount path we determined earlier
                mount_path = actual_mount_path

                # Check if task is still starting
                if task.status.lower() in ["pending", "starting", "initializing"]:
                    console.print(
                        "[green]✓[/green] Volume attached to task. Mount will complete when the task is ready."
                    )
                    console.print(
                        f"\n[yellow]Note:[/yellow] Task is still starting. The volume will be available at "
                        f"[accent]{mount_path}[/accent] once the task starts."
                    )
                    console.print(
                        "\nMithril instances can take several minutes to start. To check status:"
                    )
                    task_ref = task.name or task.task_id
                    self.show_next_actions(
                        [
                            f"Check task status: [accent]flow status {task_ref}[/accent]",
                            f"Wait for SSH and mount: [accent]flow ssh {task_ref} -c 'df -h {mount_path}'[/accent]",
                            f"Stream startup logs: [accent]flow logs {task_ref} -f[/accent]",
                        ]
                    )
                else:
                    # Task is ready; mount should be immediate
                    console.print(
                        f"[green]✓[/green] Volume mounted successfully at [accent]{mount_path}[/accent]"
                    )
                    console.print(
                        "\n[yellow]Note:[/yellow] In some cases, the task may need to be restarted for the mount to take effect."
                    )
                    task_ref = task.name or task.task_id
                    self.show_next_actions(
                        [
                            f"SSH into task: [accent]flow ssh {task_ref}[/accent]",
                            f"Verify mount: [accent]flow ssh {task_ref} -c 'df -h {mount_path}'[/accent]",
                            "List all volumes: [accent]flow volumes list[/accent]",
                        ]
                    )

            except AuthenticationError:
                self.handle_auth_error()
            except ResourceNotFoundError as e:
                from rich.markup import escape

                console.print(f"[red]Not Found:[/red] {escape(str(e))}")
            except Exception as e:
                self.handle_error(str(e))

        return mount


# Export command instance
command = MountCommand()
