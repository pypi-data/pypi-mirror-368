"""Centralized pricing configuration for Flow SDK.

Single source of truth for GPU pricing defaults.
"""

import re

# Single source of truth for default pricing
# Prices are per-GPU per-hour in USD
DEFAULT_PRICING = {
    "h100": {"low": 4.0, "med": 8.0, "high": 16.0},
    "a100": {"low": 3.0, "med": 6.0, "high": 12.0},
    "a10": {"low": 1.0, "med": 2.0, "high": 4.0},
    "t4": {"low": 0.5, "med": 1.0, "high": 2.0},
    "default": {"low": 2.0, "med": 4.0, "high": 8.0},
}


def extract_gpu_info(instance_type: str) -> tuple[str, int]:
    """Extract GPU type and count from instance type string.

    Args:
        instance_type: Instance type string (e.g., "h100", "8xh100", "a100-80gb")

    Returns:
        Tuple of (gpu_type, gpu_count)

    Examples:
        >>> extract_gpu_info("h100")
        ("h100", 1)
        >>> extract_gpu_info("8xh100")
        ("h100", 8)
        >>> extract_gpu_info("a100-80gb")
        ("a100", 1)
    """
    # Match patterns like "8xh100" or "4xa100"
    match = re.match(r"(\d+)x([a-z0-9]+)", instance_type.lower())
    if match:
        gpu_count = int(match.group(1))
        gpu_type = match.group(2)
    else:
        # Single GPU or special format
        gpu_count = 1
        # Extract base GPU type (e.g., "a100" from "a100-80gb")
        gpu_type = instance_type.lower().split("-")[0].split(".")[0]

        # Handle "gpu.nvidia.h100" format
        if "." in instance_type:
            parts = instance_type.split(".")
            if len(parts) >= 3:
                gpu_type = parts[-1].split("-")[0]

    return gpu_type, gpu_count


def get_pricing_table(config_overrides: dict | None = None) -> dict:
    """Get pricing table with optional config overrides.

    Args:
        config_overrides: Optional dictionary of pricing overrides

    Returns:
        Merged pricing table

    Note:
        Supports partial overrides - you can override just specific
        GPU types or just specific tiers.
    """
    if not config_overrides:
        return DEFAULT_PRICING

    # Deep merge to support partial overrides
    result = {}
    for gpu_type, prices in DEFAULT_PRICING.items():
        result[gpu_type] = prices.copy()

    for gpu_type, prices in config_overrides.items():
        if gpu_type in result:
            result[gpu_type].update(prices)
        else:
            result[gpu_type] = prices

    return result


def calculate_instance_price(
    instance_type: str, priority: str = "med", pricing_table: dict | None = None
) -> float:
    """Calculate total price for instance type and priority tier.

    Args:
        instance_type: Instance type string
        priority: Priority tier ("low", "med", "high")
        pricing_table: Optional custom pricing table

    Returns:
        Total price per hour in USD
    """
    if pricing_table is None:
        pricing_table = DEFAULT_PRICING

    gpu_type, gpu_count = extract_gpu_info(instance_type)

    # Get prices for GPU type, fall back to default
    gpu_prices = pricing_table.get(gpu_type, pricing_table.get("default", {}))

    # Get price for tier, fall back to med
    per_gpu_price = gpu_prices.get(priority, gpu_prices.get("med", 4.0))

    return per_gpu_price * gpu_count
