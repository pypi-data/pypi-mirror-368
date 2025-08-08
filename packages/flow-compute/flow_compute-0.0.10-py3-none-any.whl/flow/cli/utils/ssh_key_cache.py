"""SSH key resolution cache for instant connections.

Caches SSH key paths for tasks to avoid repeated lookups and filesystem
searches. Follows the same ephemeral caching pattern as task indices.
"""

import json
import time
from pathlib import Path
from typing import Dict, Optional, Tuple


class SSHKeyCache:
    """Manages cached SSH key resolutions.

    Stores mappings from task IDs to resolved SSH key paths, avoiding
    expensive repeated lookups. Cache entries expire after 30 minutes.
    """

    CACHE_TTL_SECONDS = 1800  # 30 minutes

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize cache with optional custom directory.

        Args:
            cache_dir: Directory for cache file (defaults to ~/.flow)
        """
        self.cache_dir = cache_dir or Path.home() / ".flow"
        self.cache_file = self.cache_dir / "ssh_keys.json"

    def save_key_path(self, task_id: str, key_path: str) -> None:
        """Cache a resolved SSH key path.

        Args:
            task_id: Task ID
            key_path: Resolved SSH private key path
        """
        # Create directory if needed
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Load existing cache
        cache_data = self._load_cache() or {"keys": {}}

        # Update with new key
        cache_data["keys"][task_id] = {"path": key_path, "timestamp": time.time()}

        # Clean expired entries
        self._clean_expired(cache_data)

        # Atomic write
        temp_file = self.cache_file.with_suffix(".tmp")
        temp_file.write_text(json.dumps(cache_data, indent=2))
        temp_file.replace(self.cache_file)

    def get_key_path(self, task_id: str) -> Optional[str]:
        """Get cached SSH key path if available.

        Args:
            task_id: Task ID to look up

        Returns:
            SSH key path or None if not cached/expired
        """
        cache_data = self._load_cache()
        if not cache_data:
            return None

        key_info = cache_data.get("keys", {}).get(task_id)
        if not key_info:
            return None

        # Check if expired
        age = time.time() - key_info.get("timestamp", 0)
        if age > self.CACHE_TTL_SECONDS:
            return None

        key_path = key_info.get("path")
        if key_path and Path(key_path).exists():
            return key_path

        return None

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

    def _clean_expired(self, cache_data: Dict) -> None:
        """Remove expired entries from cache data.

        Args:
            cache_data: Cache data to clean (modified in place)
        """
        now = time.time()
        keys_to_remove = []

        for task_id, key_info in cache_data.get("keys", {}).items():
            age = now - key_info.get("timestamp", 0)
            if age > self.CACHE_TTL_SECONDS:
                keys_to_remove.append(task_id)

        for task_id in keys_to_remove:
            cache_data["keys"].pop(task_id, None)

    def clear(self) -> None:
        """Clear the SSH key cache."""
        if self.cache_file.exists():
            self.cache_file.unlink()
