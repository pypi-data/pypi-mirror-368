"""Centralized links for web, docs, and status URLs.

All downstream code should import from this module instead of hard-coding
URLs. Base hosts are configurable via environment variables and come from
`flow.providers.mithril.core.constants`.
"""

from __future__ import annotations

from typing import Final

from flow.providers.mithril.core.constants import (
    MITHRIL_DOCS_URL,
    MITHRIL_STATUS_URL,
    MITHRIL_WEB_BASE_URL,
)


def _join(base: str, *parts: str) -> str:
    base = (base or "").rstrip("/")
    path = "/".join(p.strip("/") for p in parts if p)
    return f"{base}/{path}" if path else base


class WebLinks:
    """Dashboard/console links under the Mithril web app."""

    @staticmethod
    def root() -> str:
        return MITHRIL_WEB_BASE_URL

    @staticmethod
    def api_keys() -> str:
        return _join(MITHRIL_WEB_BASE_URL, "account", "apikeys")

    @staticmethod
    def ssh_keys() -> str:
        return _join(MITHRIL_WEB_BASE_URL, "account", "ssh-keys")

    @staticmethod
    def billing_settings() -> str:
        return _join(MITHRIL_WEB_BASE_URL, "settings", "billing")

    @staticmethod
    def projects_settings() -> str:
        return _join(MITHRIL_WEB_BASE_URL, "settings", "projects")

    @staticmethod
    def instances() -> str:
        return _join(MITHRIL_WEB_BASE_URL, "instances")

    @staticmethod
    def instances_spot() -> str:
        return _join(MITHRIL_WEB_BASE_URL, "instances", "spot")

    @staticmethod
    def quotas_instances() -> str:
        return _join(MITHRIL_WEB_BASE_URL, "instances", "quotas")

    @staticmethod
    def quotas_storage() -> str:
        return _join(MITHRIL_WEB_BASE_URL, "storage", "quotas")


class DocsLinks:
    """Documentation links."""

    @staticmethod
    def root() -> str:
        return MITHRIL_DOCS_URL

    @staticmethod
    def quickstart() -> str:
        # General quickstart landing page
        return _join(MITHRIL_DOCS_URL, "quickstart")

    @staticmethod
    def compute_quickstart() -> str:
        # Compute + storage focused quickstart page
        return _join(MITHRIL_DOCS_URL, "compute-and-storage", "compute-quickstart")

    @staticmethod
    def startup_scripts() -> str:
        return _join(MITHRIL_DOCS_URL, "compute-and-storage", "startup-scripts")

    @staticmethod
    def regions() -> str:
        return _join(MITHRIL_DOCS_URL, "regions")

    @staticmethod
    def spot_auction_mechanics() -> str:
        return _join(
            MITHRIL_DOCS_URL,
            "compute-and-storage",
            "spot-bids#spot-auction-mechanics",
        )

    @staticmethod
    def compute_api_reference() -> str:
        return _join(MITHRIL_DOCS_URL, "compute-api", "compute-api-reference")

    @staticmethod
    def compute_api_overview() -> str:
        return _join(MITHRIL_DOCS_URL, "compute-api", "api-overview-and-quickstart")


def status_page() -> str:
    """Service status page."""
    return MITHRIL_STATUS_URL


# Back-compat short aliases
web: Final[type[WebLinks]] = WebLinks
docs: Final[type[DocsLinks]] = DocsLinks


