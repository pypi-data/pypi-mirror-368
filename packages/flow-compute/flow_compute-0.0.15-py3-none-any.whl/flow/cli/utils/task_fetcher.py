"""Centralized task fetching service for Flow CLI.

This module provides efficient task fetching logic that prioritizes active tasks
and handles large task lists gracefully. It solves the common problem where
newer active tasks might not appear in paginated results when fetching from
oldest-first APIs.

Design principles:
- Single source of truth for task fetching logic
- Optimized for common use cases (canceling/viewing active tasks)
- Handles pagination edge cases transparently
- Provides consistent behavior across all CLI commands
"""

from typing import List, Optional, Dict
from flow import Flow
from flow.api.models import Task, TaskStatus


class TaskFetcher:
    """Centralized service for fetching tasks with active task prioritization."""

    def __init__(self, flow_client: Optional[Flow] = None):
        """Initialize with optional Flow client.

        Args:
            flow_client: Optional Flow client instance. Creates one if not provided.
        """
        self.flow_client = flow_client or Flow()

    def fetch_all_tasks(
        self,
        limit: int = 1000,
        prioritize_active: bool = True,
        status_filter: Optional[TaskStatus] = None,
    ) -> List[Task]:
        """Fetch tasks with intelligent prioritization.

        This method handles the common case where active tasks (running/pending)
        might not appear in the default task list due to pagination ordering.
        It explicitly fetches active tasks first, then merges with the general list.

        Args:
            limit: Maximum number of tasks to return
            prioritize_active: Whether to prioritize active tasks in results
            status_filter: Optional status filter for tasks

        Returns:
            List of tasks with active tasks prioritized if requested
        """
        if status_filter:
            # If filtering by specific status, just fetch those
            return self.flow_client.list_tasks(status=status_filter, limit=limit)

        tasks_by_id: Dict[str, Task] = {}

        if prioritize_active:
            # Fetch active tasks first to ensure they're included
            # This handles the case where tasks were created outside the current session
            for status in [TaskStatus.RUNNING, TaskStatus.PENDING]:
                try:
                    active_tasks = self.flow_client.list_tasks(
                        status=status,
                        limit=min(100, limit),  # Cap at 100 per status
                    )
                    for task in active_tasks:
                        tasks_by_id[task.task_id] = task
                except Exception:
                    # Continue if status-specific fetch fails
                    pass

        # Fetch general task list
        remaining_limit = limit - len(tasks_by_id)
        if remaining_limit > 0:
            try:
                general_tasks = self.flow_client.list_tasks(limit=remaining_limit)
                for task in general_tasks:
                    if task.task_id not in tasks_by_id:
                        tasks_by_id[task.task_id] = task
            except Exception:
                # If general fetch fails, at least return active tasks
                pass

        # Return as list, sorted by created_at (newest first)
        all_tasks = list(tasks_by_id.values())

        # Always sort by created_at in descending order (newest first)
        all_tasks.sort(key=lambda t: t.created_at, reverse=True)

        return all_tasks[:limit]

    def fetch_for_display(
        self, show_all: bool = False, status_filter: Optional[str] = None, limit: int = 100
    ) -> List[Task]:
        """Fetch tasks optimized for display commands (status, list).

        Args:
            show_all: Whether to show all tasks or apply time filtering
            status_filter: Optional status string to filter by
            limit: Maximum number of tasks to return

        Returns:
            List of tasks ready for display
        """
        # Convert status string to enum if provided
        status_enum = TaskStatus(status_filter) if status_filter else None

        if not show_all and not status_filter:
            # Default view: Show only running/pending tasks
            # If none exist, fall back to showing all recent tasks

            # First, try to fetch only active (running/pending) tasks
            active_tasks = []
            tasks_by_id = {}

            for status in [TaskStatus.RUNNING, TaskStatus.PENDING]:
                try:
                    status_tasks = self.flow_client.list_tasks(status=status, limit=min(100, limit))
                    for task in status_tasks:
                        if task.task_id not in tasks_by_id:
                            tasks_by_id[task.task_id] = task
                            active_tasks.append(task)
                except Exception:
                    pass

            # If we found active tasks, return only those
            if active_tasks:
                # Sort by created_at (newest first)
                active_tasks.sort(key=lambda t: t.created_at, reverse=True)
                return active_tasks[:limit]

            # No active tasks found - fall back to showing all recent tasks
            # This maintains the previous behavior when no tasks are running/pending
            return self.fetch_all_tasks(limit=limit, prioritize_active=True, status_filter=None)
        else:
            # Specific status filter or --all flag
            return self.fetch_all_tasks(
                limit=limit, prioritize_active=False, status_filter=status_enum
            )

    def fetch_for_resolution(self, limit: int = 1000) -> List[Task]:
        """Fetch tasks optimized for name/ID resolution (cancel, ssh, logs).

        This method prioritizes active tasks since those are most likely
        to be the target of user actions.

        Args:
            limit: Maximum number of tasks to fetch

        Returns:
            List of tasks with active tasks prioritized
        """
        return self.fetch_all_tasks(limit=limit, prioritize_active=True, status_filter=None)
