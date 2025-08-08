"""Shared utilities for CLI commands."""

import time
from typing import Any, Dict, Optional

from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from flow import Flow, TaskStatus
from flow._internal import pricing
from flow._internal.config import Config
from ..utils.theme_manager import theme_manager

console = theme_manager.create_console()


def display_config(config: Dict[str, Any]) -> None:
    """Display task configuration in a formatted table."""
    table = Table(title="Task Configuration", show_header=False)
    table.add_column("Property", style="cyan")
    table.add_column("Value")

    # Extract key configuration values
    if "name" in config:
        table.add_row("Name", config.get("name"))

    command = config.get("command", "N/A")
    if isinstance(command, list):
        command = " ".join(command)
    table.add_row("Command", command)
    table.add_row("Instance Type", config.get("instance_type", "N/A"))

    # Display instance count for multi-instance
    num_instances = config.get("num_instances", 1)
    if num_instances > 1:
        table.add_row("Instances", str(num_instances))

    # Display pricing information
    if "max_price_per_hour" in config and config["max_price_per_hour"]:
        per_instance_price = config["max_price_per_hour"]
        table.add_row("Max Price/Hour", f"${per_instance_price:.2f}")
        if num_instances > 1:
            total_price = per_instance_price * num_instances
            table.add_row("Total Job Price/Hour", f"${total_price:.2f} ({num_instances} instances)")
    elif "priority" in config:
        # Calculate and display per-GPU price based on priority
        priority = config.get("priority", "med")
        instance_type = config.get("instance_type", "").lower()

        # Extract GPU type and count from instance type
        gpu_count = 1
        gpu_type = instance_type
        if "x" in instance_type:
            try:
                parts = instance_type.split("x")
                gpu_count = int(parts[0])
                gpu_type = parts[1]
            except Exception:
                pass

        # Try to get pricing from config, otherwise use defaults
        try:
            flow_config = Config.load()
            if (
                flow_config
                and flow_config.provider_config
                and hasattr(flow_config.provider_config, "limit_prices")
            ):
                pricing_table = flow_config.provider_config.limit_prices
            else:
                pricing_table = pricing.DEFAULT_PRICING
        except Exception:
            # If config loading fails, use defaults
            pricing_table = pricing.DEFAULT_PRICING

        # Use centralized pricing calculation - recalculate with proper function
        gpu_type, gpu_count = pricing.extract_gpu_info(instance_type)
        gpu_prices = pricing_table.get(gpu_type, pricing_table.get("default", {}))
        per_gpu_price = gpu_prices.get(priority, gpu_prices.get("med", 4.0))
        instance_price = per_gpu_price * gpu_count

        table.add_row("Priority", priority.upper())
        table.add_row("Limit Price/GPU", f"${per_gpu_price:.2f}/hour")
        table.add_row(
            "Limit Price/Instance",
            f"${instance_price:.2f}/hour ({gpu_count} GPU{'s' if gpu_count > 1 else ''})",
        )

        # Show total job price for multi-instance
        if num_instances > 1:
            total_job_price = instance_price * num_instances
            table.add_row(
                "Total Job Price/Hour", f"${total_job_price:.2f}/hour ({num_instances} instances)"
            )

    if "resources" in config:
        resources = config["resources"]
        table.add_row("vCPUs", str(resources.get("vcpus", "N/A")))
        table.add_row("Memory", f"{resources.get('memory', 'N/A')} GB")
        table.add_row("GPUs", str(resources.get("gpus", 0)))

    if "storage" in config:
        table.add_row("Storage", f"{config['storage']} GB")

    if "mounts" in config and config["mounts"]:
        mount_strs = []
        for mount in config["mounts"]:
            if isinstance(mount, dict):
                source = mount.get("source", "")
                target = mount.get("target", "")
                mount_strs.append(f"{target} → {source}")
        if mount_strs:
            table.add_row("Mounts", "\n".join(mount_strs))

    console.print(table)


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
