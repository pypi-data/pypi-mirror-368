"""Quota-aware instance selection for Mithril provider.

Simple, correct quota management following the principle:
"Fail fast with clear errors, suggest alternatives."
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class QuotaInfo:
    """Simple quota information."""

    instance_type: str
    available: int
    total: int

    @property
    def is_available(self) -> bool:
        return self.available > 0


class QuotaChecker:
    """Check quota and suggest alternatives."""

    # Instance type aliases and their actual Mithril names
    INSTANCE_ALIASES = {
        "h100": "8x NVIDIA H100 80GB SXM5",
        "h100-pcie": "8x NVIDIA H100 80GB PCIe",
        "a100": "1x NVIDIA A100 80GB SXM4",
        "8xa100": "8x NVIDIA A100 80GB SXM4",
    }

    @staticmethod
    def check_quota_url() -> str:
        """Return the quota check URL."""
        return "https://app.mithril.ai/instances/quotas"

    @staticmethod
    def format_quota_error(requested: str, suggestion: Optional[str] = None) -> str:
        """Format a clear quota error message."""
        msg = f"No quota available for {requested}"
        if suggestion:
            msg += f". Try: {suggestion}"
        msg += f"\nCheck quota: {QuotaChecker.check_quota_url()}"
        return msg
