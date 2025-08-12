"""Shared helpers for task status checks used across CLI commands.

Centralizes common logic for determining whether a task is "active-like"
(eligible for operations that may finalize when the task becomes ready),
so commands don't need to duplicate status string sets.
"""

from __future__ import annotations

from flow.api.models import Task

# Provider-agnostic set of statuses that represent an active/provisioning state
ACTIVE_LIKE_STATUSES: set[str] = {
    "running",
    "active",
    "pending",
    "starting",
    "initializing",
    "allocated",
    "provisioning",
}


def get_status_string(task: Task) -> str:
    """Return lowercase status string for a task in a provider-agnostic way."""
    status = getattr(task, "status", None)
    try:
        return getattr(status, "value", str(status)).lower()
    except Exception:
        return str(status).lower() if status is not None else ""


def is_active_like(task: Task) -> bool:
    """Determine if a task is in an active/provisioning state."""
    return get_status_string(task) in ACTIVE_LIKE_STATUSES
