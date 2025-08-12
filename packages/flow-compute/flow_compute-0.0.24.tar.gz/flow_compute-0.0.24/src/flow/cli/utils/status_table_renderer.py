"""Status table renderer (core).

Unified task table for the Flow CLI with compact columns.
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from flow.api.models import Task
from flow.cli.utils.gpu_formatter import GPUFormatter
from flow.cli.utils.owner_resolver import Me, OwnerResolver
from flow.cli.utils.terminal_adapter import TerminalAdapter
from flow.cli.utils.theme_manager import theme_manager
from flow.cli.utils.time_formatter import TimeFormatter


class StatusTableRenderer:
    """Render tasks per the compact Status Table Spec.

    Columns (core, fixed positions):
      Index | Status | Task | GPU | Owner | Age

    Wide mode appends right-side columns only.
    """

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or theme_manager.create_console()
        self.time_fmt = TimeFormatter()
        self.gpu_fmt = GPUFormatter()
        self.term = TerminalAdapter()
        # Centralized column config (DRY) — single source of truth for widths/alignments
        self._col_cfg = {
            "#": {"justify": "right", "width": 3, "no_wrap": True},
            "Status": {
                "justify": "center",
                "width": 10,
                "min_width": 10,
                "no_wrap": True,
                "overflow": "crop",
            },
            "Task": {
                "justify": "left",
                "min_width": 20,
                "max_width": 40,
                "no_wrap": True,
                "overflow": "ellipsis",
            },
            "GPU": {
                "justify": "center",
                "width": 12,
                "min_width": 10,
                "no_wrap": True,
                "overflow": "crop",
            },
            "Owner": {
                "justify": "left",
                "min_width": 6,
                "max_width": 10,
                "no_wrap": True,
                "overflow": "ellipsis",
            },
            # Ensure Age always has room for formats like "11:20" or "8m"
            "Age": {"justify": "right", "width": 5, "min_width": 4, "no_wrap": True},
        }
        # Cache for quick access
        self._gpu_col_width = self._col_cfg["GPU"].get("width", 12)

    def render(
        self,
        tasks: list[Task],
        *,
        me: Me | None = None,
        title: str | None = None,
        wide: bool = False,
        start_index: int = 1,
        return_renderable: bool = False,
    ):
        if not tasks:
            return (
                Panel("No tasks found", border_style=theme_manager.get_color("muted"))
                if return_renderable
                else self.console.print("[dim]No tasks found[/dim]")
            )

        layout = self.term.get_responsive_layout()

        # Allow table to expand to available width to avoid cramped columns
        table = Table(
            box=None if not title else None,
            show_header=True,
            header_style=theme_manager.get_color("table.header"),
            border_style=theme_manager.get_color("table.border"),
            padding=(0, 1),
            expand=False,  # Keep table compact; avoid stretching columns unnaturally
        )

        # Core columns from centralized config
        for name in ["#", "Status", "Task", "GPU", "Owner", "Age"]:
            cfg = self._col_cfg[name]
            table.add_column(
                name,
                justify=cfg.get("justify", "left"),
                width=cfg.get("width"),
                min_width=cfg.get("min_width"),
                max_width=cfg.get("max_width"),
                no_wrap=cfg.get("no_wrap", False),
                overflow=cfg.get("overflow"),
            )

        # Wide-only appended columns
        if wide:
            table.add_column("IP", justify="left", width=15, no_wrap=True)
            table.add_column("Class", justify="left", width=6, no_wrap=True)
            table.add_column("Created", justify="right", width=10, no_wrap=True)
            table.add_column("Start In", justify="right", width=8, no_wrap=True)
            table.add_column("Window", justify="right", width=7, no_wrap=True)

        for idx, task in enumerate(tasks, start=start_index):
            status_display = self._format_status(task)
            # Coerce possible Mock attributes to safe strings
            try:
                name_val = getattr(task, "name", None)
                if name_val is None:
                    name_val = getattr(task, "task_id", "unnamed")
                task_name = str(name_val)
            except Exception:
                task_name = "unnamed"
            gpu = self._format_gpu(task)
            owner = self._format_owner(task, me)
            age = self.time_fmt.format_ultra_compact_age(task.created_at)

            row = [
                str(idx),
                status_display,
                task_name,
                gpu,
                owner,
                age,
            ]

            if wide:
                start_in, window = self._format_reservation_columns(task)
                row.extend(
                    [
                        task.ssh_host or "-",
                        self._format_class(task),
                        self.time_fmt.format_ultra_compact_age(task.created_at),
                        start_in,
                        window,
                    ]
                )

            table.add_row(*row)

        if title:
            from rich.markup import escape

            try:
                safe_title = escape(str(title))
            except Exception:
                safe_title = "Tasks"
            title_text = Text(safe_title, style=f"bold {theme_manager.get_color('accent')}")
            panel = Panel(
                table,
                title=title_text,
                title_align="center",
                border_style=theme_manager.get_color("table.border"),
                padding=(1, 2),
                # Avoid stretching to full terminal width when content is narrow
                expand=False,
            )
            return panel if return_renderable else self.console.print(panel)
        return table if return_renderable else self.console.print(table)

    # --- Cell formatters ---

    def _format_status(self, task: Task) -> str:
        from flow.cli.utils.task_formatter import TaskFormatter

        # Width-aware hybrid: show word when it fits, otherwise compact symbol-only
        STATUS_COL_WIDTH = 10
        layout = self.term.get_responsive_layout()

        display_status = TaskFormatter.get_display_status(task)

        plain_length = 2 + len(display_status)  # symbol + space + word
        compact = layout.get("use_compact_status", False) or plain_length > STATUS_COL_WIDTH
        base = (
            TaskFormatter.format_compact_status(display_status)
            if compact
            else TaskFormatter.format_status_with_color(display_status)
        )

        # Append a tiny reserved badge when space allows
        try:
            meta = getattr(task, "provider_metadata", {}) or {}
            res = meta.get("reservation")
            if res:
                # Only annotate when not extremely tight
                if not compact and (plain_length + 3) <= STATUS_COL_WIDTH:
                    # Use subtle dim 'R' badge to indicate reserved capacity
                    return f"{base} [dim]R[/dim]"
        except Exception:
            pass
        return base

    def _format_task_name(self, task: Task) -> str:
        # Let the table column control width and overflow; avoid pre-truncation
        return task.name or "unnamed"

    def _format_owner(self, task: Task, me: Me | None) -> str:
        try:
            created_by = getattr(task, "created_by", None)
            if me is not None:
                text = OwnerResolver.format_owner(created_by, me)
                # Only accept resolver text if it's not just the compact created_by token
                if text and text != "-":
                    compact = (
                        created_by.replace("user_", "")[:8] if isinstance(created_by, str) else None
                    )
                    if text != compact:
                        return text
                # If unresolved but task originated from this CLI session, use my email-derived label
                try:
                    provider_meta = getattr(task, "provider_metadata", {}) or {}
                    if provider_meta.get("origin") == "flow-cli":
                        if me.email and "@" in me.email:
                            local = me.email.split("@")[0]
                            first = local.split(".")[0].split("_")[0].split("-")[0]
                            if first:
                                return first.lower()
                        if me.username:
                            first = me.username.split()[0].split(".")[0].split("_")[0].split("-")[0]
                            if first:
                                return first.lower()
                except Exception:
                    pass
        except Exception:
            pass
        # Avoid network calls in table rendering; do not fetch user profile here
        user_id = getattr(task, "created_by", None)
        if not user_id:
            return "-"
        # Be robust against mocks or non-string types
        try:
            user_id_str = str(user_id)
        except Exception:
            return "-"
        return user_id_str.replace("user_", "")[:8]

    def _format_gpu(self, task: Task) -> str:
        # Be resilient to Mock objects: coerce num_instances to int>0
        num = getattr(task, "num_instances", 1)
        try:
            num = int(num)
            if num <= 0:
                num = 1
        except Exception:
            num = 1
        # Use the configured GPU column width to drive width-aware formatting
        return self.gpu_fmt.format_ultra_compact_width_aware(
            task.instance_type, num, self._gpu_col_width
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

    def _format_reservation_columns(self, task: Task) -> tuple[str, str]:
        """Return (Start In, Window) for wide mode when task has reservation metadata."""
        try:
            from datetime import datetime, timezone

            meta = getattr(task, "provider_metadata", {}) or {}
            res = meta.get("reservation")
            if not res:
                return "-", "-"
            st = res.get("start_time") or res.get("start_time_utc")
            et = res.get("end_time") or res.get("end_time_utc")
            start_in = "-"
            if st:
                try:
                    s = str(st).replace("Z", "+00:00")
                    dt = datetime.fromisoformat(s)
                    delta_min = max(0, int((dt - datetime.now(timezone.utc)).total_seconds() // 60))
                    start_in = f"{delta_min}m" if delta_min < 120 else f"{delta_min//60}h"
                except Exception:
                    pass
            window = "-"
            if st and et:
                try:
                    s1 = str(st).replace("Z", "+00:00")
                    s2 = str(et).replace("Z", "+00:00")
                    dt1 = datetime.fromisoformat(s1)
                    dt2 = datetime.fromisoformat(s2)
                    hours = int(round((dt2 - dt1).total_seconds() / 3600))
                    window = f"{hours}h"
                except Exception:
                    pass
            return start_in, window
        except Exception:
            return "-", "-"
