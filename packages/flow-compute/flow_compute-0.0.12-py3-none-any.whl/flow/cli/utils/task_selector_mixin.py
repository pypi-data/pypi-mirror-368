"""Task selector mixin for commands that operate on tasks.

Provides a clean abstraction for commands that need to select tasks,
following SOLID principles and avoiding leaky abstractions.
"""

from typing import Optional, List, Callable, TypeVar
from abc import ABC, abstractmethod

import click

from flow import Flow
from flow.api.models import Task
from flow.errors import AuthenticationError

from .interactive_selector import select_task
from .task_resolver import resolve_task_identifier


T = TypeVar("T")


class TaskFilter:
    """Composable task filters following the Strategy pattern."""

    @staticmethod
    def running_only(tasks: List[Task]) -> List[Task]:
        """Filter for running tasks only."""
        from flow.api.models import TaskStatus

        return [t for t in tasks if t.status == TaskStatus.RUNNING]

    @staticmethod
    def cancellable(tasks: List[Task]) -> List[Task]:
        """Filter for tasks that can be cancelled."""
        from flow.api.models import TaskStatus

        return [t for t in tasks if t.status in [TaskStatus.PENDING, TaskStatus.RUNNING]]

    @staticmethod
    def with_logs(tasks: List[Task]) -> List[Task]:
        """Filter for tasks that have logs available."""
        from flow.api.models import TaskStatus

        # Only running and completed tasks have accessible logs
        # Cancelled tasks have terminated instances with no SSH access
        return [t for t in tasks if t.status in [TaskStatus.RUNNING, TaskStatus.COMPLETED]]

    @staticmethod
    def with_ssh(tasks: List[Task]) -> List[Task]:
        """Filter for tasks with SSH access."""
        return [t for t in tasks if t.status == "RUNNING" and t.ssh_host]


class TaskSelectorMixin(ABC):
    """Mixin for commands that need to select tasks.

    This follows the Template Method pattern, providing a clean way
    for commands to get a task either from arguments or interactive selection.
    """

    @abstractmethod
    def get_task_filter(self) -> Optional[Callable[[List[Task]], List[Task]]]:
        """Return the filter to apply to tasks, or None for all tasks."""
        pass

    @abstractmethod
    def get_selection_title(self) -> str:
        """Return the title for the interactive selector."""
        pass

    @abstractmethod
    def get_no_tasks_message(self) -> str:
        """Return message when no tasks match the filter."""
        pass

    def resolve_task(
        self, task_identifier: Optional[str], client: Flow, allow_multiple: bool = False
    ) -> Optional[Task] | List[Task]:
        """Resolve a task from identifier or interactive selection.

        This method encapsulates the common pattern of:
        1. Using provided identifier if available
        2. Otherwise showing interactive selection
        3. Applying appropriate filters

        Args:
            task_identifier: Optional task ID/name from command args
            client: Flow API client
            allow_multiple: Whether to allow multiple selection

        Returns:
            Selected task(s) or None if cancelled

        Raises:
            SystemExit: If task not found or selection cancelled
        """
        from ..commands.base import console

        # If identifier provided, resolve it directly
        if task_identifier:
            task, error = resolve_task_identifier(client, task_identifier)
            if error:
                console.print(f"[red]✗ Error:[/red] {error}")
                raise SystemExit(1)
            return task

        # Interactive selection
        # Use TaskFetcher to ensure we find all active tasks
        from .task_fetcher import TaskFetcher

        fetcher = TaskFetcher(client)
        all_tasks = fetcher.fetch_for_resolution(limit=1000)

        # Apply filter if specified
        task_filter = self.get_task_filter()
        if task_filter:
            filtered_tasks = task_filter(all_tasks)
        else:
            filtered_tasks = all_tasks

        if not filtered_tasks:
            console.print(f"[yellow]{self.get_no_tasks_message()}[/yellow]")
            raise SystemExit(0)

        # Show selector
        selected = select_task(
            filtered_tasks, title=self.get_selection_title(), allow_multiple=allow_multiple
        )

        if not selected:
            console.print("No task selected")
            raise SystemExit(0)

        return selected


class TaskOperationCommand(TaskSelectorMixin):
    """Base class for commands that operate on tasks.

    Provides a clean abstraction that:
    - Handles authentication errors consistently
    - Manages task selection/resolution
    - Follows the Template Method pattern for execution
    """

    @abstractmethod
    def execute_on_task(self, task: Task, client: Flow, **kwargs) -> None:
        """Execute the command logic on the selected task."""
        pass

    def execute_with_selection(self, task_identifier: Optional[str], **kwargs) -> None:
        """Execute command with task selection.

        This is the main entry point that:
        1. Handles authentication
        2. Resolves/selects the task
        3. Executes the command logic
        """
        from ..commands.base import console
        from .animated_progress import AnimatedEllipsisProgress

        try:
            # Check if command manages its own progress
            if hasattr(self, "manages_own_progress") and self.manages_own_progress:
                # Commands that manage their own progress display
                if task_identifier:
                    # Just resolve the task without animation - command will show its own progress
                    client = Flow(auto_init=True)
                    task = self.resolve_task(task_identifier, client)
                    self.execute_on_task(task, client, **kwargs)
                else:
                    # No identifier - need animation for loading tasks
                    with AnimatedEllipsisProgress(
                        console, "Loading tasks", transient=True, start_immediately=True
                    ) as progress:
                        client = Flow(auto_init=True)
                        # Fetch tasks within animation context to show progress
                        from .task_fetcher import TaskFetcher

                        fetcher = TaskFetcher(client)
                        all_tasks = fetcher.fetch_for_resolution(limit=1000)

                    # Animation stopped, now show interactive selector with already-fetched tasks
                    # We need to resolve task without re-fetching
                    task_filter = self.get_task_filter()
                    if task_filter:
                        filtered_tasks = task_filter(all_tasks)
                    else:
                        filtered_tasks = all_tasks

                    if not filtered_tasks:
                        console.print(f"[yellow]{self.get_no_tasks_message()}[/yellow]")
                        raise SystemExit(0)

                    # Show selector
                    from .interactive_selector import select_task

                    selected = select_task(
                        filtered_tasks, title=self.get_selection_title(), allow_multiple=False
                    )

                    if not selected:
                        console.print("No task selected")
                        raise SystemExit(0)

                    # Execute command logic
                    self.execute_on_task(selected, client, **kwargs)
            elif hasattr(self, "name") and self.name == "logs":
                # For logs command, also use cache for instant display
                display_msg = "Fetching logs"
                if task_identifier:
                    # Quick cache lookup for better UX
                    from .task_index_cache import TaskIndexCache

                    cache = TaskIndexCache()

                    # If it's an index reference, resolve it
                    if task_identifier.startswith(":"):
                        task_id, _ = cache.resolve_index(task_identifier)
                        if task_id:
                            cached_task = cache.get_cached_task(task_id)
                            if cached_task:
                                name = cached_task.get("name", task_id)
                                display_msg = f"Fetching logs from {name} ({task_id[:12]})"
                            else:
                                display_msg = f"Fetching logs from {task_id[:12]}"
                    else:
                        # Direct task ID - check cache
                        cached_task = cache.get_cached_task(task_identifier)
                        if cached_task:
                            name = cached_task.get("name", task_identifier)
                            display_msg = f"Fetching logs from {name} ({task_identifier[:12]})"
                        else:
                            display_msg = f"Fetching logs from {task_identifier}"

                    # Show animation while fetching logs
                    with AnimatedEllipsisProgress(
                        console, display_msg, transient=True, start_immediately=True
                    ):
                        client = Flow(auto_init=True)
                        # Resolve task
                        task = self.resolve_task(task_identifier, client)
                        # Execute command logic
                        self.execute_on_task(task, client, **kwargs)
                else:
                    # No identifier - need to stop animation before interactive selector
                    with AnimatedEllipsisProgress(
                        console,
                        "Loading tasks for log viewing",
                        transient=True,
                        start_immediately=True,
                    ) as progress:
                        client = Flow(auto_init=True)
                        # Fetch tasks within animation context to show progress
                        from .task_fetcher import TaskFetcher

                        fetcher = TaskFetcher(client)
                        all_tasks = fetcher.fetch_for_resolution(limit=1000)

                    # Animation stopped, now show interactive selector with already-fetched tasks
                    # We need to resolve task without re-fetching
                    task_filter = self.get_task_filter()
                    if task_filter:
                        filtered_tasks = task_filter(all_tasks)
                    else:
                        filtered_tasks = all_tasks

                    if not filtered_tasks:
                        console.print(f"[yellow]{self.get_no_tasks_message()}[/yellow]")
                        raise SystemExit(0)

                    # Show selector
                    from .interactive_selector import select_task

                    selected = select_task(
                        filtered_tasks, title=self.get_selection_title(), allow_multiple=False
                    )

                    if not selected:
                        console.print("No task selected")
                        raise SystemExit(0)

                    # Execute command logic
                    self.execute_on_task(selected, client, **kwargs)
            elif hasattr(self, "name") and self.name == "cancel":
                # For cancel command, show immediate feedback
                display_msg = "Looking up tasks to cancel"
                if task_identifier:
                    display_msg = f"Looking up task: {task_identifier}"
                    # Resolve the task with animation, then stop before confirmation
                    with AnimatedEllipsisProgress(
                        console, display_msg, transient=True, start_immediately=True
                    ):
                        client = Flow(auto_init=True)
                        # Resolve task
                        task = self.resolve_task(task_identifier, client)
                    # Animation stopped, now execute (which shows confirmation)
                    self.execute_on_task(task, client, **kwargs)
                else:
                    # No identifier - need to stop animation before interactive selector
                    with AnimatedEllipsisProgress(
                        console, display_msg, transient=True, start_immediately=True
                    ) as progress:
                        client = Flow(auto_init=True)
                        # Fetch tasks within animation context to show progress
                        from .task_fetcher import TaskFetcher

                        fetcher = TaskFetcher(client)
                        all_tasks = fetcher.fetch_for_resolution(limit=1000)

                    # Animation stopped, now show interactive selector with already-fetched tasks
                    # We need to resolve task without re-fetching
                    task_filter = self.get_task_filter()
                    if task_filter:
                        filtered_tasks = task_filter(all_tasks)
                    else:
                        filtered_tasks = all_tasks

                    if not filtered_tasks:
                        console.print(f"[yellow]{self.get_no_tasks_message()}[/yellow]")
                        raise SystemExit(0)

                    # Show selector
                    from .interactive_selector import select_task

                    selected = select_task(
                        filtered_tasks, title=self.get_selection_title(), allow_multiple=False
                    )

                    if not selected:
                        console.print("No task selected")
                        raise SystemExit(0)

                    # Execute command logic
                    self.execute_on_task(selected, client, **kwargs)
            elif hasattr(self, "name") and self.name == "release":
                # For release command, stop animation before showing confirmation
                if task_identifier:
                    display_msg = f"Looking up task: {task_identifier}"
                    with AnimatedEllipsisProgress(
                        console, display_msg, transient=True, start_immediately=True
                    ) as progress:
                        client = Flow(auto_init=True)
                        # Resolve task
                        task = self.resolve_task(task_identifier, client)
                    # Animation stopped, now execute (which may show confirmation)
                    self.execute_on_task(task, client, **kwargs)
                else:
                    # No identifier - need to stop animation before interactive selector
                    with AnimatedEllipsisProgress(
                        console, "Loading grabbed resources", transient=True, start_immediately=True
                    ) as progress:
                        client = Flow(auto_init=True)
                        # Fetch tasks within animation context to show progress
                        from .task_fetcher import TaskFetcher

                        fetcher = TaskFetcher(client)
                        all_tasks = fetcher.fetch_for_resolution(limit=1000)

                    # Animation stopped, now show interactive selector with already-fetched tasks
                    # We need to resolve task without re-fetching
                    task_filter = self.get_task_filter()
                    if task_filter:
                        filtered_tasks = task_filter(all_tasks)
                    else:
                        filtered_tasks = all_tasks

                    if not filtered_tasks:
                        console.print(f"[yellow]{self.get_no_tasks_message()}[/yellow]")
                        raise SystemExit(0)

                    # Show selector
                    from .interactive_selector import select_task

                    selected = select_task(
                        filtered_tasks, title=self.get_selection_title(), allow_multiple=False
                    )

                    if not selected:
                        console.print("No task selected")
                        raise SystemExit(0)

                    # Execute command logic
                    self.execute_on_task(selected, client, **kwargs)
            else:
                # For other commands, use animated progress
                if task_identifier:
                    # If we have a specific identifier, run the animation through the whole process
                    with AnimatedEllipsisProgress(
                        console,
                        f"Looking up task: {task_identifier}",
                        transient=True,
                        start_immediately=True,
                    ):
                        client = Flow(auto_init=True)
                        # Resolve task (from arg or interactive)
                        task = self.resolve_task(task_identifier, client)
                        # Execute command logic
                        self.execute_on_task(task, client, **kwargs)
                else:
                    # No identifier - need to stop animation before interactive selector
                    with AnimatedEllipsisProgress(
                        console, "Loading tasks", transient=True, start_immediately=True
                    ) as progress:
                        client = Flow(auto_init=True)
                        # Fetch tasks within animation context to show progress
                        from .task_fetcher import TaskFetcher

                        fetcher = TaskFetcher(client)
                        all_tasks = fetcher.fetch_for_resolution(limit=1000)

                    # Animation stopped, now show interactive selector with already-fetched tasks
                    # We need to resolve task without re-fetching
                    task_filter = self.get_task_filter()
                    if task_filter:
                        filtered_tasks = task_filter(all_tasks)
                    else:
                        filtered_tasks = all_tasks

                    if not filtered_tasks:
                        console.print(f"[yellow]{self.get_no_tasks_message()}[/yellow]")
                        raise SystemExit(0)

                    # Show selector
                    from .interactive_selector import select_task

                    selected = select_task(
                        filtered_tasks, title=self.get_selection_title(), allow_multiple=False
                    )

                    if not selected:
                        console.print("No task selected")
                        raise SystemExit(0)

                    # Execute command logic
                    self.execute_on_task(selected, client, **kwargs)

        except AuthenticationError:
            console.print("[red]Authentication failed[/red]")
            console.print("\nPlease run [cyan]flow init[/cyan] to configure your credentials")
            raise SystemExit(1)
        except SystemExit:
            raise
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            raise SystemExit(1)
