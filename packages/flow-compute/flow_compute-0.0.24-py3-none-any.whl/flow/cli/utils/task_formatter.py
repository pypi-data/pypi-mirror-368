"""Task formatting utilities for CLI output."""

from flow.api.models import Task
from flow.cli.utils.theme_manager import theme_manager


class TaskFormatter:
    """Handles task-related formatting for consistent display across CLI commands."""

    @staticmethod
    def format_task_display(task: Task) -> str:
        """Format task for display with name and ID.

        Args:
            task: The task to format

        Returns:
            Formatted string like "my-task" or "my-task (task_123)" if ID is not a bid
        """
        if task.name:
            # Only show ID if it's not a bid ID (for debugging/advanced users)
            if task.task_id and not task.task_id.startswith("bid_"):
                return f"{task.name} ({task.task_id})"
            return task.name
        # If no name, show task_id but this should be rare
        return task.task_id

    @staticmethod
    def format_short_task_id(task_id: str, length: int = 16) -> str:
        """Format task ID to a shorter display version.

        Args:
            task_id: Full task ID
            length: Target length for short ID

        Returns:
            Shortened task ID with ellipsis if needed
        """
        if len(task_id) <= length:
            return task_id
        return task_id[:length] + "..."

    @staticmethod
    def get_status_config(status: str) -> dict[str, str]:
        """Get complete status configuration including symbol and style.

        Args:
            status: Task status string

        Returns:
            Dictionary with symbol, color, and style configuration
        """
        status_configs = {
            "pending": {
                "symbol": "○",
                "color": theme_manager.get_color("status.pending"),
                "style": "",
            },
            "starting": {
                "symbol": "●",
                "color": theme_manager.get_color("status.starting"),
                "style": "",
            },
            "preparing": {
                "symbol": "●",
                "color": theme_manager.get_color("status.preparing"),
                "style": "",
            },
            "running": {
                "symbol": "●",
                "color": theme_manager.get_color("status.running"),
                "style": "",
            },
            "paused": {
                "symbol": "⏸",
                "color": theme_manager.get_color("status.paused"),
                "style": "",
            },
            "preempting": {
                "symbol": "●",
                "color": theme_manager.get_color("status.preempting"),
                "style": "",
            },
            "completed": {
                "symbol": "●",
                "color": theme_manager.get_color("status.completed"),
                "style": "",
            },
            "failed": {
                "symbol": "●",
                "color": theme_manager.get_color("status.failed"),
                "style": "",
            },
            "cancelled": {
                "symbol": "○",
                "color": theme_manager.get_color("status.cancelled"),
                "style": "",
            },
            "unknown": {"symbol": "○", "color": theme_manager.get_color("muted"), "style": ""},
        }
        return status_configs.get(
            status.lower(),
            {"symbol": "?", "color": theme_manager.get_color("default"), "style": ""},
        )

    @staticmethod
    def get_status_style(status: str) -> str:
        """Get the color style for a task status.

        Args:
            status: Task status string

        Returns:
            Rich color style name
        """
        config = TaskFormatter.get_status_config(status)
        return config["color"]

    @staticmethod
    def format_status_with_color(status: str) -> str:
        """Format status with appropriate symbol and color markup.

        Args:
            status: Task status string

        Returns:
            Rich-formatted status string with symbol and color
        """
        config = TaskFormatter.get_status_config(status)
        style_parts = [config["color"]]
        if config["style"]:
            style_parts.append(config["style"])
        style = " ".join(style_parts)

        # Let the table column control alignment/width; avoid manual padding here
        return f"[{style}]{config['symbol']} {status}[/{style}]"

    @staticmethod
    def format_compact_status(status: str) -> str:
        """Format status in compact mode (symbol only).

        Args:
            status: Task status string

        Returns:
            Rich-formatted status symbol with color
        """
        config = TaskFormatter.get_status_config(status)
        style_parts = [config["color"]]
        if config["style"]:
            style_parts.append(config["style"])
        style = " ".join(style_parts)

        return f"[{style}]{config['symbol']}[/{style}]"

    @staticmethod
    def get_display_status(task: Task) -> str:
        """Resolve a user-facing display status for a task.

        Maps provider/instance transitional states to compact, human-friendly words,
        and treats running-without-SSH as "starting" to avoid confusion in the UI.
        """
        # Normalize main task status (enum-safe)
        status_value = getattr(
            getattr(task, "status", None), "value", str(getattr(task, "status", "unknown")).lower()
        )

        # Terminal states should never be overridden by instance provisioning hints
        if status_value in {"completed", "failed", "cancelled"}:
            return status_value

        # Map provider/instance transitional states for active tasks only
        instance_status = getattr(task, "instance_status", None)
        if instance_status in {"STATUS_STARTING", "STATUS_INITIALIZING"}:
            # Only show as starting if the instance is young; otherwise treat as running
            try:
                age_s = getattr(task, "instance_age_seconds", None)
                if callable(age_s):
                    age_s = age_s()
            except Exception:
                age_s = None
            if age_s is None or age_s < 10 * 60:
                return "starting"
            # Age is older; fall through to base status
        if instance_status == "STATUS_SCHEDULED":
            return "pending"

        # Treat RUNNING without SSH as "starting" only for young instances
        if status_value == "running" and not getattr(task, "ssh_host", None):
            try:
                # Consider the instance young if < 15 minutes old
                age_s = getattr(task, "instance_age_seconds", None)
                if callable(age_s):
                    age_s = age_s()
                if age_s is None:
                    from datetime import datetime, timezone
                    created = getattr(task, "created_at", None)
                    if created:
                        age_s = (datetime.now(timezone.utc) - created).total_seconds()
                if age_s is None or age_s < 15 * 60:
                    return "starting"
            except Exception:
                # Be conservative if we cannot determine age
                return "starting"

        return status_value

    @staticmethod
    def format_task_summary(task: Task) -> str:
        """Format a brief task summary for listings.

        Args:
            task: The task to summarize

        Returns:
            Brief summary string
        """
        name = task.name or "unnamed"
        if len(name) > 25:
            name = name[:22] + "..."
        return name

    @staticmethod
    def get_capability_warnings(task: Task) -> list[str]:
        """Get warnings for missing task capabilities.

        Args:
            task: The task to check

        Returns:
            List of warning messages for missing capabilities
        """
        warnings = []

        # Provide appropriate SSH warnings based on task state
        if task.status.value in ["running", "completed", "failed"]:
            if not task.has_ssh_access and not getattr(task, "ssh_keys_configured", False):
                warnings.append("No SSH access - task was submitted without SSH keys")
            elif not task.has_ssh_access and getattr(task, "ssh_keys_configured", False):
                warnings.append("SSH keys configured but access not yet available")
        elif task.status.value == "pending" and not getattr(task, "ssh_keys_configured", False):
            warnings.append("No SSH keys configured - logs won't be available")

        return warnings

    @staticmethod
    def format_capabilities(task: Task) -> str:
        """Format task capabilities for display.

        Args:
            task: The task to check

        Returns:
            Formatted capabilities string
        """
        capabilities = task.capabilities
        icons = {
            "ssh": "🔐" if capabilities.get("ssh") else "🚫",
            "logs": "📋" if capabilities.get("logs") else "🚫",
        }

        return f"SSH: {icons['ssh']}  Logs: {icons['logs']}"

    @staticmethod
    def format_post_submit_info(task: Task) -> list[str]:
        """Format post-submission information and warnings.

        Args:
            task: The submitted task

        Returns:
            List of lines to display after task submission
        """
        lines = []

        # Basic info - use task name instead of ID
        task_ref = task.name or task.task_id
        from flow.cli.utils.theme_manager import theme_manager as _tm

        ok = _tm.get_color("success")
        lines.append(f"[{ok}]✓[/{ok}] Task submitted: {task_ref}")

        # Capability warnings
        warnings = TaskFormatter.get_capability_warnings(task)
        if warnings:
            lines.append("")
            warn = _tm.get_color("warning")
            lines.append(f"[{warn}]⚠ Warning:[/{warn}]")
            for warning in warnings:
                lines.append(f"  {warning}")
            lines.append("  Run 'flow init' to configure SSH keys for future tasks")
        else:
            # Show available commands using task name
            lines.append("")
            lines.append("Commands:")
            lines.append(f"  [accent]flow status {task_ref}[/accent]")
            lines.append(f"  [accent]flow logs {task_ref}[/accent] [--follow]")
            lines.append(f"  [accent]flow ssh {task_ref}[/accent]")

        return lines

    @staticmethod
    def format_post_submit_commands(task: Task) -> list[str]:
        """Return only the recommended commands to run after submission.

        Args:
            task: The submitted task

        Returns:
            List of command lines (no header), using task name when available
        """
        task_ref = task.name or task.task_id
        return [
            f"  [accent]flow status {task_ref}[/accent]",
            f"  [accent]flow logs {task_ref} -f[/accent]",
            f"  [accent]flow ssh {task_ref}[/accent]",
        ]
