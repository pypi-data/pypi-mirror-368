"""Simple region validation utilities."""

from typing import List, Optional, Tuple

from flow.providers.mithril.core.constants import VALID_REGIONS


def validate_region(region: Optional[str]) -> Tuple[bool, Optional[str]]:
    """Validate region and suggest correction for common mistakes.

    Args:
        region: Region string to validate

    Returns:
        (is_valid, suggested_correction)
    """
    if not region:
        return True, None  # Region is optional

    if region in VALID_REGIONS:
        return True, None

    # Check for missing zone suffix (common mistake)
    if region in ["us-central1", "eu-central1"]:
        return False, f"{region}-a"

    return False, None


def list_regions() -> List[str]:
    """Get list of valid regions."""
    return VALID_REGIONS.copy()
