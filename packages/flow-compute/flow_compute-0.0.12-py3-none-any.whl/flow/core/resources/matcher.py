"""Match GPU requirements to instance types."""

from typing import Any, Dict, List

from flow.errors import FlowError


class NoMatchingInstanceError(FlowError):
    """No instance matches requirements."""

    pass


class InstanceMatcher:
    """Matches GPU requirements to available instances.

    Single responsibility: matching only. Open for extension with new
    matching strategies. Testable in isolation.

    Performance: O(n) catalog scan, typically <10ms for 1000 instances.
    Algorithm: Finds cheapest exact match, then cheapest larger instance.

    Examples:
        >>> catalog = [{"gpu_type": "a100-80gb", "gpu_count": 4, ...}]
        >>> matcher = InstanceMatcher(catalog)
        >>> matcher.match({"gpu_type": "a100-80gb", "count": 4})
        'a100.80gb.sxm4.4x'
    """

    def __init__(self, catalog: List[Dict[str, Any]]):
        """Initialize with instance catalog.

        Args:
            catalog: List of available instances with properties:
                - instance_type: str
                - gpu_type: str
                - gpu_count: int
                - price_per_hour: float
                - available: bool
        """
        self.catalog = catalog

        # Build indices for fast lookup
        self._by_gpu_type: Dict[str, List[Dict]] = {}
        for instance in catalog:
            gpu_type = instance.get("gpu_type", "").lower()
            if gpu_type not in self._by_gpu_type:
                self._by_gpu_type[gpu_type] = []
            self._by_gpu_type[gpu_type].append(instance)

    def match(self, requirements: Dict[str, Any]) -> str:
        """Find best instance for requirements.

        Args:
            requirements: Parsed GPU requirements

        Returns:
            Instance type string

        Raises:
            NoMatchingInstanceError: If no match found
        """

        # Match by GPU type and count
        gpu_type = requirements.get("gpu_type")
        count = requirements.get("count", 1)

        if not gpu_type:
            raise NoMatchingInstanceError(
                "No GPU type specified",
                suggestions=["Specify a GPU type like gpu='a100' or gpu='h100'"],
            )

        candidates = self._find_candidates(gpu_type, count)
        if not candidates:
            self._raise_no_match_error(gpu_type, count)

        # Return cheapest matching instance
        best = min(candidates, key=lambda x: x["price_per_hour"])
        return best["instance_type"]

    def _find_candidates(self, gpu_type: str, count: int) -> List[Dict[str, Any]]:
        """Find instances matching GPU requirements."""
        candidates = []

        # Exact match preferred
        for instance in self._by_gpu_type.get(gpu_type.lower(), []):
            if instance.get("gpu_count") == count and instance.get("available", False):
                candidates.append(instance)

        # If no exact match, find larger instances
        if not candidates:
            for instance in self._by_gpu_type.get(gpu_type.lower(), []):
                if instance.get("gpu_count") >= count and instance.get("available", False):
                    candidates.append(instance)

        return candidates

    def _raise_no_match_error(self, gpu_type: str, count: int):
        """Raise error with helpful suggestions."""
        # Just tell them what's actually available
        available = []
        for instance in self._by_gpu_type.get(gpu_type.lower(), []):
            if instance.get("available", False):
                available.append(f"{instance['instance_type']} ({instance['gpu_count']} GPUs)")

        suggestions = []
        if available:
            suggestions.append(f"Available {gpu_type}: {', '.join(available)}")
        else:
            suggestions.append(f"No {gpu_type} instances currently available")

        raise NoMatchingInstanceError(
            f"No instances found with {count}x {gpu_type}", suggestions=suggestions
        )
