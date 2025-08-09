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
import time

try:
    # Optional cache import; fallback to no-op if unavailable
    from .prefetch import get_cached  # type: ignore
except Exception:  # pragma: no cover - optional dependency for CLI path
    def get_cached(_: str):  # type: ignore
        return None
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
        # Fast path: consult prefetch cache when available
        if status_filter:
            cache_key = None
            if status_filter == TaskStatus.RUNNING:
                cache_key = "tasks_running"
            elif status_filter == TaskStatus.PENDING:
                cache_key = "tasks_pending"
            # Use cached slice first if present (still fall back to live if miss)
            if cache_key:
                cached = get_cached(cache_key)
                if cached:
                    try:
                        cached_sorted = sorted(cached, key=lambda t: t.created_at, reverse=True)
                        return cached_sorted[:limit]
                    except Exception:
                        # Fall back if cached objects are not fully typed yet
                        return list(cached)[:limit]
            # If filtering by specific status, just fetch those
            return self.flow_client.list_tasks(status=status_filter, limit=limit)

        tasks_by_id: Dict[str, Task] = {}

        if prioritize_active:
            # Check cached active slices first for instant response
            cached_running = get_cached("tasks_running") or []
            cached_pending = get_cached("tasks_pending") or []

            # If caches are cold, wait briefly for prefetch to populate
            if not cached_running and not cached_pending:
                end = time.time() + 0.15
                while time.time() < end:
                    cached_running = get_cached("tasks_running") or []
                    cached_pending = get_cached("tasks_pending") or []
                    if cached_running or cached_pending:
                        break
                    time.sleep(0.05)
            try:
                cached_running = sorted(cached_running, key=lambda t: t.created_at, reverse=True)
                cached_pending = sorted(cached_pending, key=lambda t: t.created_at, reverse=True)
            except Exception:
                # If cache elements are not fully typed, proceed without sorting
                pass
            for task in list(cached_running)[: min(100, limit)]:
                tasks_by_id[getattr(task, "task_id", getattr(task, "id", ""))] = task
            for task in list(cached_pending)[: min(100, max(0, limit - len(tasks_by_id)))]:
                tasks_by_id[getattr(task, "task_id", getattr(task, "id", ""))] = task

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
                # Consult broader cached slice to avoid an immediate API call
                general_tasks = get_cached("tasks_all") or []
                if not general_tasks:
                    # Give prefetch a brief moment to complete
                    end = time.time() + 0.15
                    while time.time() < end:
                        general_tasks = get_cached("tasks_all") or []
                        if general_tasks:
                            break
                        time.sleep(0.05)
                if not general_tasks:
                    general_tasks = self.flow_client.list_tasks(limit=remaining_limit)
                for task in general_tasks:
                    tid = getattr(task, "task_id", getattr(task, "id", None))
                    if tid and tid not in tasks_by_id:
                        tasks_by_id[tid] = task
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

            # Fast path: consult prefetch cache for running/pending slices
            try:
                cached_running = get_cached("tasks_running") or []
                cached_pending = get_cached("tasks_pending") or []
                # If both caches are empty, wait briefly for prefetch to complete
                if not cached_running and not cached_pending:
                    end = time.time() + 0.15
                    while time.time() < end:
                        cached_running = get_cached("tasks_running") or []
                        cached_pending = get_cached("tasks_pending") or []
                        if cached_running or cached_pending:
                            break
                        time.sleep(0.05)
                # Use cached if any present to avoid immediate network calls
                if cached_running or cached_pending:
                    combined = list(cached_running) + list(cached_pending)
                    # Deduplicate by task_id while preserving order
                    seen: dict[str, Task] = {}
                    for t in combined:
                        tid = getattr(t, "task_id", getattr(t, "id", None))
                        if tid and tid not in seen:
                            seen[tid] = t
                    # Sort newest first if timestamps available; otherwise return as-is
                    try:
                        result = sorted(seen.values(), key=lambda t: t.created_at, reverse=True)
                    except Exception:
                        result = list(seen.values())
                    return result[:limit]
            except Exception:
                # Ignore cache errors and proceed with live fetch
                pass

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
