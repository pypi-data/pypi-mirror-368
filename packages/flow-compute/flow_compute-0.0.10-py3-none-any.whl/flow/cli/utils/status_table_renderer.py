"""Status table renderer (core).

Unified task table for the Flow CLI with compact columns.
"""
from __future__ import annotations

from typing import List, Optional

from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich.text import Text

from flow.api.models import Task
from .theme_manager import theme_manager
from .time_formatter import TimeFormatter
from .gpu_formatter import GPUFormatter
from .terminal_adapter import TerminalAdapter
from .owner_resolver import OwnerResolver, Me


class StatusTableRenderer:
    """Render tasks per the compact Status Table Spec.

    Columns (core, fixed positions):
      Index | Status | Task | Owner | GPU | Age

    Wide mode appends right-side columns only.
    """

    def __init__(self, console: Optional[Console] = None) -> None:
        self.console = console or theme_manager.create_console()
        self.time_fmt = TimeFormatter()
        self.gpu_fmt = GPUFormatter()
        self.term = TerminalAdapter()

    def render(
        self,
        tasks: List[Task],
        *,
        me: Optional[Me] = None,
        title: Optional[str] = None,
        wide: bool = False,
        return_renderable: bool = False,
    ):
        if not tasks:
            return (
                Panel("No tasks found", border_style=theme_manager.get_color("muted"))
                if return_renderable
                else self.console.print("[dim]No tasks found[/dim]")
            )

        layout = self.term.get_responsive_layout()

        table = Table(
            box=None if not title else None,
            show_header=True,
            header_style=theme_manager.get_color("table.header"),
            border_style=theme_manager.get_color("table.border"),
            padding=(0, 1),
            expand=True,
        )

        # Core columns
        table.add_column("Index", justify="right", width=4, no_wrap=True)
        table.add_column("Status", justify="center", width=10, no_wrap=True)
        table.add_column("Task", justify="left", width=22, no_wrap=True)
        table.add_column("Owner", justify="left", width=10, no_wrap=True)
        table.add_column("GPU", justify="center", width=14, no_wrap=True)
        table.add_column("Age", justify="right", width=8, no_wrap=True)

        # Wide-only appended columns
        if wide:
            table.add_column("IP", justify="left", width=15, no_wrap=True)
            table.add_column("Class", justify="left", width=6, no_wrap=True)
            table.add_column("Created", justify="right", width=10, no_wrap=True)

        for idx, task in enumerate(tasks, start=1):
            status_display = self._format_status(task)
            task_name = self._format_task_name(task)
            owner = self._format_owner(task, me)
            gpu = self._format_gpu(task)
            age = self.time_fmt.format_ultra_compact_age(task.created_at)

            row = [
                str(idx),
                status_display,
                task_name,
                owner,
                gpu,
                age,
            ]

            if wide:
                row.extend(
                    [
                        task.ssh_host or "-",
                        self._format_class(task),
                        self.time_fmt.format_ultra_compact_age(task.created_at),
                    ]
                )

            table.add_row(*row)

        if title:
            from rich.markup import escape

            safe_title = escape(title)
            title_text = Text(safe_title, style=f"bold {theme_manager.get_color('accent')}")
            panel = Panel(
                table,
                title=title_text,
                title_align="center",
                border_style=theme_manager.get_color("table.border"),
                padding=(1, 2),
            )
            return panel if return_renderable else self.console.print(panel)
        return table if return_renderable else self.console.print(table)

    # --- Cell formatters ---

    def _format_status(self, task: Task) -> str:
        from .task_formatter import TaskFormatter

        instance_status = getattr(task, "instance_status", None)
        if instance_status in {"STATUS_STARTING", "STATUS_INITIALIZING"}:
            return TaskFormatter.format_status_with_color("starting")
        if instance_status == "STATUS_SCHEDULED":
            return TaskFormatter.format_status_with_color("pending")
        return TaskFormatter.format_status_with_color(task.status.value)

    def _format_task_name(self, task: Task) -> str:
        name = task.name or "unnamed"
        return self.term.intelligent_truncate(name, 22, "middle")

    def _format_owner(self, task: Task, me: Optional[Me]) -> str:
        try:
            created_by = getattr(task, "created_by", None)
            if me is not None:
                text = OwnerResolver.format_owner(created_by, me)
                if text and text != "-":
                    return text
        except Exception:
            pass
        try:
            user = task.get_user()
            if user and getattr(user, "email", None):
                email = user.email
                if "@" in email:
                    return email.split("@")[0]
        except Exception:
            pass
        user_id = getattr(task, "created_by", None)
        if not user_id:
            return "-"
        return user_id.replace("user_", "")[:8]

    def _format_gpu(self, task: Task) -> str:
        return self.gpu_fmt.format_ultra_compact_width_aware(
            task.instance_type, getattr(task, "num_instances", 1), 14
        )

    def _format_class(self, task: Task) -> str:
        it = (task.instance_type or "").lower()
        try:
            provider_meta = getattr(task, "provider_metadata", {}) or {}
        except Exception:
            provider_meta = {}
        if "sxm" in it:
            return "SXM"
        socket = str(provider_meta.get("socket", "")).lower()
        if "pcie" in it or "pcie" in socket:
            return "PCIe"
        return "-"
