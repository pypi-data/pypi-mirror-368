"""Shared utilities for CLI commands."""

import time
from typing import Any, Dict, Optional

from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from flow import Flow, TaskStatus
from flow._internal import pricing
from flow._internal.config import Config
from ..utils.theme_manager import theme_manager
from ..utils.table_styles import create_flow_table, wrap_table_in_panel
from ..utils.terminal_adapter import TerminalAdapter

console = theme_manager.create_console()


def display_config(
    config: Dict[str, Any], show_pricing: bool = False, compact: bool = False
) -> None:
    """Display task configuration in a polished, responsive table."""
    layout = TerminalAdapter.get_responsive_layout()

    table = create_flow_table(title=None, show_borders=layout["show_borders"], padding=1)
    table.show_header = False
    table.add_column("Setting", style=theme_manager.get_color("accent"), no_wrap=True)
    table.add_column("Value", style=theme_manager.get_color("default"))

    # Name
    if "name" in config:
        table.add_row("Name", f"[bold]{config.get('name')}[/bold]")

    # Command (compact if very long)
    command = config.get("command", "N/A")
    if isinstance(command, list):
        command = " ".join(command)
    max_cmd_len = 80 if layout["density"].value != "compact" else 50
    if isinstance(command, str) and len(command) > max_cmd_len:
        from ..utils.terminal_adapter import TerminalAdapter as TA
        command = TA.intelligent_truncate(command, max_cmd_len, "middle")
    table.add_row("Command", f"[dim]{command}[/dim]")

    # Image
    if not compact:
        image = config.get("image")
        if image:
            table.add_row("Image", image)

    # Instance type and count
    instance_type = config.get("instance_type", "N/A")
    num_instances = int(config.get("num_instances", 1) or 1)
    if num_instances > 1:
        table.add_row("Instances", f"{num_instances} × {instance_type}")
    else:
        table.add_row("Instance Type", instance_type)

    # Region if present
    if not compact:
        region = config.get("region")
        if region:
            table.add_row("Region", region)

    # Priority (always visible)
    priority = (config.get("priority") or "med").lower()
    table.add_row("Priority", priority.capitalize())

    # Pricing (hidden by default; shown when --pricing flag is set)
    if show_pricing:
        if config.get("max_price_per_hour"):
            per_instance_price = float(config["max_price_per_hour"]) or 0.0
            table.add_row("Max Price/Instance", f"${per_instance_price:.2f}/hr")
            if num_instances > 1:
                total_price = per_instance_price * num_instances
                table.add_row("Max Price/Job", f"${total_price:.2f}/hr ({num_instances} instances)")
        else:
            # Priority-based limit pricing summary
            instance_type_lower = (instance_type or "").lower()
            try:
                flow_config = Config.load()
                pricing_table = (
                    flow_config.provider_config.limit_prices
                    if flow_config and flow_config.provider_config and hasattr(flow_config.provider_config, "limit_prices")
                    else pricing.DEFAULT_PRICING
                )
            except Exception:
                pricing_table = pricing.DEFAULT_PRICING
            gpu_type, gpu_count = pricing.extract_gpu_info(instance_type_lower)
            per_gpu_price = pricing_table.get(gpu_type, pricing_table.get("default", {})).get(
                priority, pricing.DEFAULT_PRICING.get("default", {}).get("med", 4.0)
            )
            instance_price = per_gpu_price * max(gpu_count, 1)
            table.add_row("Limit Price/GPU", f"${per_gpu_price:.2f}/hr")
            table.add_row("Limit Price/Instance", f"${instance_price:.2f}/hr ({gpu_count} GPU{'s' if gpu_count > 1 else ''})")
            if num_instances > 1:
                table.add_row("Limit Price/Job", f"${instance_price * num_instances:.2f}/hr ({num_instances} instances)")

    # Upload strategy/timeout
    if not compact and ("upload_strategy" in config or "upload_timeout" in config):
        strategy = config.get("upload_strategy", "auto")
        timeout = int(config.get("upload_timeout", 600))
        table.add_row("Code Upload", f"{strategy} (timeout {timeout}s)")

    # SSH keys count
    if not compact:
        ssh_keys = config.get("ssh_keys") or []
        if isinstance(ssh_keys, (list, tuple)) and len(ssh_keys) > 0:
            shown = ", ".join(ssh_keys[:2]) + (" …" if len(ssh_keys) > 2 else "")
            table.add_row("SSH Keys", shown)

    # Mounts summary
    if not compact and "mounts" in config and config["mounts"]:
        mount_strs = []
        for mount in config["mounts"]:
            if isinstance(mount, dict):
                source = mount.get("source", "")
                target = mount.get("target", "")
                mount_strs.append(f"{target} → {source}")
        if mount_strs:
            table.add_row("Mounts", "\n".join(mount_strs[:5] + (["…"] if len(mount_strs) > 5 else [])))

    # Resources (if present)
    if not compact and "resources" in config:
        resources = config["resources"] or {}
        vcpus = resources.get("vcpus")
        mem = resources.get("memory")
        gpus = resources.get("gpus")
        if vcpus:
            table.add_row("vCPUs", str(vcpus))
        if mem:
            table.add_row("Memory", f"{mem} GB")
        if gpus:
            table.add_row("GPUs", str(gpus))

    # Print within a panel title
    wrap_table_in_panel(table, "Task Configuration", console)


def wait_for_task(
    flow_client: Flow,
    task_id: str,
    watch: bool = False,
    json_output: bool = False,
    task_name: Optional[str] = None,
    show_submission_message: bool = True,
) -> str:
    """Wait for a task to reach running state with progress indication.

    Args:
        flow_client: Flow client instance
        task_id: Task ID to wait for
        watch: Whether to watch task progress
        json_output: Whether to output JSON
        task_name: Optional task name for better display
        show_submission_message: Whether to show "Task submitted" message (default: True)

    Returns:
        Final task status
    """
    if json_output:
        # For JSON output, just poll without visual progress
        while True:
            status = flow_client.status(task_id)
            if status not in ["pending", "preparing"]:
                return status
            time.sleep(2)

    if watch:
        # Use animated progress for watching mode
        from ..utils.animated_progress import AnimatedEllipsisProgress

        if show_submission_message:
            if task_name:
                console.print(f"Task submitted: [cyan]{task_name}[/cyan]")
            else:
                console.print(f"Task submitted with ID: [cyan]{task_id}[/cyan]")
        console.print("[dim]Watching task progress...[/dim]\n")

        with AnimatedEllipsisProgress(
            console, "Waiting for task to start", transient=True
        ) as progress:
            while True:
                status = flow_client.status(task_id)

                if status == "running":
                    console.print(f"[green]✓[/green] Task is running")
                    task_ref = task_name or task_id
                    console.print(f"\nTip: Run [cyan]flow logs {task_ref} -f[/cyan] to stream logs")
                    return status
                elif status in ["completed", "failed", "cancelled"]:
                    return status

                time.sleep(2)
    else:
        # Simple waiting mode with animated progress
        from ..utils.animated_progress import AnimatedEllipsisProgress

        if show_submission_message:
            if task_name:
                console.print(f"Task submitted: [cyan]{task_name}[/cyan]")
            else:
                console.print(f"Task submitted with ID: [cyan]{task_id}[/cyan]")

        # Instance allocation is typically much faster than full provisioning
        # Allocation = getting assigned a GPU (usually <2 minutes)
        # Provisioning = boot + configure + SSH ready (up to 12-20 minutes)
        ALLOCATION_TIMEOUT_SECONDS = 120  # 2 minutes for GPU allocation from pool

        with AnimatedEllipsisProgress(
            console,
            "Waiting for instance allocation",
            transient=True,
            show_progress_bar=True,
            estimated_seconds=ALLOCATION_TIMEOUT_SECONDS,
        ) as progress:
            while True:
                status = flow_client.status(task_id)

                if status not in ["pending", "preparing"]:
                    return status

                time.sleep(2)


# Deprecated: Use TaskFormatter.get_status_style() instead
def get_status_style(status: str) -> str:
    """Get the color style for a task status.

    DEPRECATED: Use flow.cli.utils.task_formatter.TaskFormatter.get_status_style() instead.
    This function is kept for backward compatibility.
    """
    from ..utils.task_formatter import TaskFormatter

    return TaskFormatter.get_status_style(status)
