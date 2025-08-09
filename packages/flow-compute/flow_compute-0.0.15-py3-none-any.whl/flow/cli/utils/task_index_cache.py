"""Task index cache for quick task references.

Provides ephemeral index-based task references (e.g., :1, :2) based on
the last displayed task list. Follows the principle of least surprise
with explicit, time-bounded behavior.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from flow.api.models import Task


class TaskIndexCache:
    """Manages ephemeral task index mappings.

    Stores mappings from display indices to task IDs, allowing users
    to reference tasks by position (e.g., :1, :2) from the last status
    display. Indices expire after 30 minutes to prevent stale references.
    """

    CACHE_TTL_SECONDS = 1800  # 30 minutes

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize cache with optional custom directory.

        Args:
            cache_dir: Directory for cache file (defaults to ~/.flow)
        """
        self.cache_dir = cache_dir or Path.home() / ".flow"
        self.cache_file = self.cache_dir / "task_indices.json"

    def save_indices(self, tasks: List[Task]) -> None:
        """Save task indices from a displayed list.

        Args:
            tasks: Ordered list of tasks as displayed
        """
        # Create directory if needed
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # If there are no tasks, clear the cache to avoid stale mappings
        if not tasks:
            self.clear()
            return

        # Build index mapping (1-based for user friendliness)
        indices = {str(i + 1): task.task_id for i, task in enumerate(tasks)}

        # Cache full task details for instant access
        task_details = {}
        for task in tasks:
            task_details[task.task_id] = {
                "task_id": task.task_id,
                "name": task.name,
                "status": task.status.value,
                "instance_type": task.instance_type,
                "ssh_host": task.ssh_host,
                "ssh_port": task.ssh_port,
                "ssh_user": task.ssh_user,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "region": task.region,
                "cost_per_hour": task.cost_per_hour,
            }

        cache_data = {
            "indices": indices,
            "task_details": task_details,
            "timestamp": time.time(),
            "task_count": len(tasks),
        }

        # Atomic write
        temp_file = self.cache_file.with_suffix(".tmp")
        temp_file.write_text(json.dumps(cache_data, indent=2))
        temp_file.replace(self.cache_file)

    def resolve_index(self, index_str: str) -> Tuple[Optional[str], Optional[str]]:
        """Resolve an index reference to a task ID.

        Args:
            index_str: Index string (e.g., ":1", ":2")

        Returns:
            Tuple of (task_id if found, error message if any)
        """
        # Parse index
        if not index_str.startswith(":"):
            return None, None  # Not an index reference

        try:
            index = int(index_str[1:])
        except ValueError:
            return None, f"Invalid index format: {index_str}"

        if index < 1:
            return None, "Index must be positive"

        # Load cache
        cache_data = self._load_cache()
        if not cache_data:
            return None, "No recent task list. Run 'flow status' first"

        # Check if expired
        age = time.time() - cache_data["timestamp"]
        if age > self.CACHE_TTL_SECONDS:
            return None, "Task indices expired. Run 'flow status' to refresh"

        # Look up index
        task_id = cache_data["indices"].get(str(index))
        if not task_id:
            max_index = cache_data["task_count"]
            return None, f"Index {index} out of range (1-{max_index})"

        return task_id, None

    def get_indices_map(self) -> Dict[str, str]:
        """Return the last saved indices mapping if cache is fresh.

        Returns:
            Mapping of display index (str) -> task_id, or empty dict if expired/unavailable.
        """
        cache_data = self._load_cache()
        if not cache_data:
            return {}
        age = time.time() - cache_data.get("timestamp", 0)
        if age > self.CACHE_TTL_SECONDS:
            return {}
        return dict(cache_data.get("indices", {}))

    def _load_cache(self) -> Optional[Dict]:
        """Load cache data if valid.

        Returns:
            Cache data dict or None if not found/invalid
        """
        if not self.cache_file.exists():
            return None

        try:
            return json.loads(self.cache_file.read_text())
        except (json.JSONDecodeError, KeyError):
            # Invalid cache file
            return None

    def get_cached_task(self, task_id: str) -> Optional[Dict]:
        """Get cached task details if available.

        Args:
            task_id: Task ID to look up

        Returns:
            Task details dict or None if not cached/expired
        """
        cache_data = self._load_cache()
        if not cache_data:
            return None

        # Check if expired
        age = time.time() - cache_data["timestamp"]
        if age > self.CACHE_TTL_SECONDS:
            return None

        return cache_data.get("task_details", {}).get(task_id)

    def clear(self) -> None:
        """Clear the index cache."""
        if self.cache_file.exists():
            self.cache_file.unlink()
