"""Status presenter (core default UI).

Coordinates fetching, formatting, table rendering, header summary, tip bar,
and index cache saving for the default status UI.
"""

from __future__ import annotations

from dataclasses import dataclass

from rich.console import Console

from flow import Flow
from flow.api.models import Task
from flow.cli.utils.owner_resolver import OwnerResolver
from flow.cli.utils.status_table_renderer import StatusTableRenderer
from flow.cli.utils.task_fetcher import TaskFetcher
from flow.cli.utils.task_index_cache import TaskIndexCache
from flow.cli.utils.theme_manager import theme_manager
from flow.cli.utils.time_formatter import TimeFormatter


@dataclass
class StatusDisplayOptions:
    show_all: bool = False
    limit: int = 20
    wide: bool = False
    group_by_origin: bool = True


class StatusPresenter:
    def __init__(self, console: Console | None = None, flow_client: Flow | None = None) -> None:
        self.console = console or theme_manager.create_console()
        self.flow = flow_client or Flow()
        self.fetcher = TaskFetcher(self.flow)
        self.time_fmt = TimeFormatter()
        self.table = StatusTableRenderer(self.console)
        self.owner_resolver = OwnerResolver(self.flow)

    def present(self, options: StatusDisplayOptions, tasks: list[Task] | None = None) -> None:
        if tasks is None:
            tasks = self.fetcher.fetch_for_display(
                show_all=options.show_all, status_filter=None, limit=options.limit
            )
        if not tasks:
            self.console.print("[dim]No tasks found[/dim]")
            return

        running = sum(1 for t in tasks if getattr(t.status, "value", str(t.status)) == "running")
        pending = sum(1 for t in tasks if getattr(t.status, "value", str(t.status)) == "pending")

        parts = []
        if running:
            parts.append(f"{running} running")
        if pending:
            parts.append(f"{pending} pending")
        if parts:
            self.console.print("[dim]" + " · ".join(parts) + "[/dim]\n")

        me = self.owner_resolver.get_me()

        # Optional grouping by origin (Flow vs Other) using provider metadata
        if options.group_by_origin:
            flow_tasks: list[Task] = []
            other_tasks: list[Task] = []
            for t in tasks:
                try:
                    meta = getattr(t, "provider_metadata", {}) or {}
                    if meta.get("origin") == "flow-cli":
                        flow_tasks.append(t)
                    else:
                        other_tasks.append(t)
                except Exception:
                    other_tasks.append(t)

            displayed_tasks: list[Task] = []

            if flow_tasks:
                title_flow = "Flow"
                panel_flow = self.table.render(
                    flow_tasks,
                    me=me,
                    title=title_flow,
                    wide=options.wide,
                    start_index=1,
                    return_renderable=True,
                )
                self.console.print(panel_flow)
                displayed_tasks.extend(flow_tasks)

            if other_tasks:
                # Add spacing if both groups present
                if flow_tasks:
                    self.console.print("")
                title_other = "External"
                panel_other = self.table.render(
                    other_tasks,
                    me=me,
                    title=title_other,
                    wide=options.wide,
                    start_index=(len(flow_tasks) + 1),
                    return_renderable=True,
                )
                self.console.print(panel_other)
                displayed_tasks.extend(other_tasks)

            if not flow_tasks and not other_tasks:
                self.console.print("[dim]No tasks found[/dim]")
        else:
            if not options.show_all:
                title = f"Tasks (showing up to {options.limit}, last 24 hours)"
            else:
                title = f"Tasks (showing up to {options.limit})"
            displayed_tasks = list(tasks)
            panel = self.table.render(
                tasks,
                me=me,
                title=title,
                wide=options.wide,
                start_index=1,
                return_renderable=True,
            )
            self.console.print(panel)

        if options.group_by_origin:
            legend = "External = other sources (e.g., provider console)"
            try:
                provider_name = getattr(getattr(self.flow, "config", None), "provider", None) or ""
                if not provider_name:
                    import os as _os

                    provider_name = (_os.environ.get("FLOW_PROVIDER") or "").lower()
                if (provider_name or "").lower() == "mithril":
                    legend = "External = other sources (e.g., Mithril Console)"
            except Exception:
                pass
            self.console.print(f"\n[dim]Legend: Flow = Flow CLI · {legend}[/dim]")
        if not options.show_all:
            self.console.print("[dim]Showing active tasks only. Use --all to see all tasks.[/dim]")
        self.console.print(
            "[dim]Tip: Index shortcuts (:1, 2, 1-3) are valid for 30 minutes after this view.[/dim]"
        )

        # Save indices in the order displayed so shortcuts match UI numbering
        # Be resilient when tasks are mocks (tests) and may not be JSON serializable
        try:
            cache = TaskIndexCache()
            cache.save_indices(displayed_tasks)
        except Exception:
            # Skip caching silently; indices will not be available but display is intact
            pass

        count = min(len(displayed_tasks), options.limit)
        if count >= 7:
            multi_example = ":1-3,5,7"
            range_example = ":1-3"
        elif count >= 5:
            multi_example = ":1-3,5"
            range_example = ":1-3"
        elif count >= 3:
            multi_example = ":1-3"
            range_example = ":1-3"
        elif count == 2:
            multi_example = ":1-2"
            range_example = ":1-2"
        else:
            multi_example = ":1"
            range_example = ":1"

        steps = [
            "\n[bold]Next steps:[/bold]",
            "  • SSH into running task:",
            "    [accent]flow ssh <task-name>[/accent]",
            "    [accent]flow ssh :1[/accent]",
            "  • View logs for a task:",
            "    [accent]flow logs <task-name>[/accent]",
            "    [accent]flow logs :1[/accent]",
            "  • Cancel tasks by index or range:",
            "    [accent]flow cancel :1-3,5[/accent]",
            "  • Submit a new task:",
            "    [accent]flow run task.yaml[/accent]",
        ]
        self.console.print("\n" + "\n".join(steps))
