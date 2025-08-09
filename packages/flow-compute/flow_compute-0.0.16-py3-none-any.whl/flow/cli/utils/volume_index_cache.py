"""Volume index cache for quick volume references.

Provides ephemeral index-based volume references (e.g., :1, :2) based on
the last displayed volume list. Follows the principle of least surprise
with explicit, time-bounded behavior.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from flow.api.models import Volume


class VolumeIndexCache:
    """Manages ephemeral volume index mappings.

    Stores mappings from display indices to volume IDs, allowing users
    to reference volumes by position (e.g., :1, :2) from the last volume
    list display. Indices expire after 5 minutes to prevent stale references.
    """

    CACHE_TTL_SECONDS = 300  # 5 minutes

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize cache with optional custom directory.

        Args:
            cache_dir: Directory for cache file (defaults to ~/.flow)
        """
        self.cache_dir = cache_dir or Path.home() / ".flow"
        self.cache_file = self.cache_dir / "volume_indices.json"

    def save_indices(self, volumes: List[Volume]) -> None:
        """Save volume indices from a displayed list.

        Args:
            volumes: Ordered list of volumes as displayed
        """
        # Create directory if needed
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Build index mapping (1-based for user friendliness)
        indices = {str(i + 1): volume.id for i, volume in enumerate(volumes)}

        # Cache full volume details for instant access
        volume_details = {}
        for volume in volumes:
            volume_details[volume.id] = {
                "id": volume.id,
                "name": volume.name,
                "region": volume.region,
                "size_gb": volume.size_gb,
                "interface": getattr(volume, "interface", "block"),
                "created_at": volume.created_at.isoformat() if volume.created_at else None,
            }

        cache_data = {
            "indices": indices,
            "volume_details": volume_details,
            "timestamp": time.time(),
            "volume_count": len(volumes),
        }

        # Atomic write
        temp_file = self.cache_file.with_suffix(".tmp")
        temp_file.write_text(json.dumps(cache_data, indent=2))
        temp_file.replace(self.cache_file)

    def resolve_index(self, index_str: str) -> Tuple[Optional[str], Optional[str]]:
        """Resolve an index reference to a volume ID.

        Args:
            index_str: Index string (e.g., ":1", ":2")

        Returns:
            Tuple of (volume_id if found, error message if any)
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
            return None, "No recent volume list. Run 'flow volumes list' first"

        # Check if expired
        age = time.time() - cache_data["timestamp"]
        if age > self.CACHE_TTL_SECONDS:
            return None, "Volume indices expired. Run 'flow volumes list' to refresh"

        # Look up index
        volume_id = cache_data["indices"].get(str(index))
        if not volume_id:
            max_index = cache_data["volume_count"]
            return None, f"Index {index} out of range (1-{max_index})"

        return volume_id, None

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

    def get_cached_volume(self, volume_id: str) -> Optional[Dict]:
        """Get cached volume details if available.

        Args:
            volume_id: Volume ID to look up

        Returns:
            Volume details dict or None if not cached/expired
        """
        cache_data = self._load_cache()
        if not cache_data:
            return None

        # Check if expired
        age = time.time() - cache_data["timestamp"]
        if age > self.CACHE_TTL_SECONDS:
            return None

        return cache_data.get("volume_details", {}).get(volume_id)

    def clear(self) -> None:
        """Clear the index cache."""
        if self.cache_file.exists():
            self.cache_file.unlink()
