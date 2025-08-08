"""Parse GPU specifications from strings."""

import re
from typing import Any, Dict

from flow.errors import ValidationError


class GPUParser:
    """Parses GPU strings like 'a100', 'a100:4', 'cheapest'.

    Simple and user-friendly - users just type what they want.
    """

    # Known GPU types and their canonical names
    GPU_ALIASES = {
        "a100": "a100-80gb",
        "h100": "h100-80gb",
        "a10": "a10-24gb",
        "t4": "t4-16gb",
        "v100": "v100-32gb",
        "l4": "l4-24gb",
    }

    def parse(self, gpu_string: str) -> Dict[str, Any]:
        """Parse GPU string into components.

        Examples:
            >>> parser = GPUParser()
            >>> parser.parse("a100")
            {"gpu_type": "a100-80gb", "count": 1}
            >>> parser.parse("h100:4")
            {"gpu_type": "h100-80gb", "count": 4}
            >>> parser.parse("")
            {}

        Args:
            gpu_string: User input like "a100", "a100:4"

        Returns:
            Dict with parsed components:
            - gpu_type: Canonical GPU name (e.g., "a100-80gb")
            - count: Number of GPUs (1-8)

        Raises:
            ValidationError: If string format invalid or GPU unknown
        """
        if not gpu_string:
            return {}

        # Parse "gpu:count" format
        # Regex: gpu_type (alphanumeric) optionally followed by :count (digits)
        match = re.match(r"^([a-z0-9]+)(?::(\d+))?$", gpu_string.lower())
        if not match:
            raise ValidationError(
                f"Invalid GPU string: {gpu_string}",
                suggestions=[
                    "Use format: 'a100' or 'a100:4'",
                    f"Supported GPUs: {', '.join(self.GPU_ALIASES.keys())}",
                ],
            )

        gpu_type = match.group(1)
        count = int(match.group(2)) if match.group(2) else 1

        # Validate GPU type
        if gpu_type not in self.GPU_ALIASES:
            raise ValidationError(
                f"Unknown GPU type: {gpu_type}",
                suggestions=[
                    f"Supported GPUs: {', '.join(self.GPU_ALIASES.keys())}",
                    "Use 't4' for the most affordable GPU",
                ],
            )

        # Validate count (most cloud providers limit to 8 GPUs per instance)
        if count < 1 or count > 8:
            raise ValidationError(
                f"Invalid GPU count: {count}", suggestions=["GPU count must be between 1 and 8"]
            )

        return {"gpu_type": self.GPU_ALIASES[gpu_type], "count": count}
