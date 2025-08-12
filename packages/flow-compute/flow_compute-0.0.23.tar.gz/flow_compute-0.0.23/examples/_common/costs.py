from __future__ import annotations

from typing import Any

from flow import Flow


def estimate_price_for_instance(instance_type: str, region: str | None = None) -> float | None:
    """Best-effort price estimate for an instance type using public SDK.

    Returns price_per_hour if discoverable, else None.
    """
    requirements: dict[str, Any] = {"instance_type": instance_type}
    if region:
        requirements["region"] = region

    try:
        with Flow() as client:
            results = client.find_instances(requirements, limit=5)
            if not results:
                return None
            # Prefer exact region match if provided, else cheapest overall
            if region:
                regional = [r for r in results if r.get("region") == region]
                if regional:
                    return regional[0].get("price_per_hour")
            return min(
                (r.get("price_per_hour") for r in results if r.get("price_per_hour") is not None),
                default=None,
            )
    except Exception:
        return None
