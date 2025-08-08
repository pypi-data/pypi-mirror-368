"""Task resolution utilities for Flow CLI.

This module provides intelligent task resolution that accepts either
task IDs or task names, following the principle of least surprise.
When ambiguous, it fails fast with helpful guidance.

Design principles:
- Exact ID match always wins (no ambiguity)
- Name prefix matching for convenience
- Clear error messages for ambiguous cases
- Zero magic, predictable behavior
"""

from typing import List, Optional, Tuple

from flow import Flow
from flow.api.models import Task
from .task_fetcher import TaskFetcher
from .task_index_cache import TaskIndexCache


def resolve_task_identifier(
    flow_client: Flow, identifier: str, require_unique: bool = True
) -> Tuple[Optional[Task], Optional[str]]:
    """Resolve a task identifier to a Task object.

    Resolution order:
    1. Index reference (e.g., :1, :2)
    2. Direct get_task() lookup (for exact task IDs)
    3. Exact task_id match from list
    4. Exact name match
    5. Prefix match on task_id
    6. Prefix match on name

    Args:
        flow_client: Flow API client
        identifier: Task ID, name, or index reference to resolve
        require_unique: If True, fail on ambiguous matches

    Returns:
        Tuple of (Task if found, error message if any)
    """
    # Check for index reference first (e.g., :1, :2) or bare single index (e.g., 1)
    if identifier.startswith(":"):
        cache = TaskIndexCache()
        task_id, error = cache.resolve_index(identifier)
        if error:
            # Provide clearer, multi-line guidance for indices
            error_lines = [
                f"No task found for index reference '{identifier}'.",
                "",
                "Tips:",
                "  • Run 'flow status' to refresh the index cache (now lasts 30 minutes).",
                "  • Use single index like ':1' or bare '1' after 'flow status'.",
                "  • For names or IDs, use the full task name or task ID.",
            ]
            return None, "\n".join(error_lines)
        if task_id:
            # Resolve the cached task ID
            identifier = task_id
    else:
        # Accept bare single-index form for consistency with tips (e.g., "2")
        import re as _re
        if _re.fullmatch(r"\d+", identifier):
            cache = TaskIndexCache()
            # Use the same cache logic as resolve_index but without requiring ':'
            # Build a temporary index reference
            task_id, error = cache.resolve_index(f":{identifier}")
            if error:
                return None, error
            if task_id:
                identifier = task_id

    # Try direct lookup first - this is the 80/20 optimization
    # Most users will provide exact task IDs
    try:
        task = flow_client.get_task(identifier)
        return task, None
    except Exception:
        # Not a valid task ID or doesn't exist - continue with list-based search
        pass

    # Use centralized task fetcher for consistent behavior
    task_fetcher = TaskFetcher(flow_client)
    all_tasks = task_fetcher.fetch_for_resolution()

    # 1. Exact task_id match
    for task in all_tasks:
        if task.task_id == identifier:
            return task, None

    # 2. Exact name match
    name_matches = [t for t in all_tasks if t.name == identifier]
    if len(name_matches) == 1:
        return name_matches[0], None
    elif len(name_matches) > 1:
        return None, _format_ambiguous_error(identifier, name_matches, "name")

    # 3. Prefix match on task_id
    id_prefix_matches = [t for t in all_tasks if t.task_id.startswith(identifier)]
    if len(id_prefix_matches) == 1:
        return id_prefix_matches[0], None
    elif len(id_prefix_matches) > 1 and require_unique:
        return None, _format_ambiguous_error(identifier, id_prefix_matches, "ID prefix")

    # 4. Prefix match on name
    name_prefix_matches = [t for t in all_tasks if t.name and t.name.startswith(identifier)]
    if len(name_prefix_matches) == 1:
        return name_prefix_matches[0], None
    elif len(name_prefix_matches) > 1 and require_unique:
        return None, _format_ambiguous_error(identifier, name_prefix_matches, "name prefix")

    # No matches - provide helpful error message
    # Build multi-line, readable guidance
    lines = [f"No task found matching '{identifier}'.", "", "Suggestions:"]

    # Index-looking input (digits or digits/ranges with optional colon)
    import re
    looks_like_index = bool(re.fullmatch(r":?[0-9,\-\s]+", identifier))
    if looks_like_index:
        lines.extend(
            [
                "  • Run 'flow status' to refresh the index cache (valid for 30 minutes).",
                "  • Then use ':1' or '1' to reference a specific row.",
                "  • Ranges like '1-3,5' are supported for commands that accept multi-select.",
            ]
        )
    else:
        # Likely name or ID
        if identifier.startswith("task-") or len(identifier) > 20:
            lines.extend(
                [
                    "  • Task may still be initializing; try again shortly.",
                    "  • Verify the task ID is correct.",
                ]
            )
        lines.append("  • Use 'flow status' to list tasks, then select by name, ID, or index (:1).")

    return None, "\n".join(lines)


def _format_ambiguous_error(identifier: str, matches: List[Task], match_type: str) -> str:
    """Format an error message for ambiguous matches."""
    lines = [f"Multiple tasks match {match_type} '{identifier}':"]
    for task in matches[:5]:  # Show max 5
        # Only show task ID if it's not a bid ID
        if task.task_id and not task.task_id.startswith("bid_"):
            lines.append(f"  - {task.name or 'unnamed'} ({task.task_id})")
        else:
            lines.append(f"  - {task.name or 'unnamed'}")
    if len(matches) > 5:
        lines.append(f"  ... and {len(matches) - 5} more")
    lines.append("\nUse a more specific identifier or the full task ID")
    return "\n".join(lines)
