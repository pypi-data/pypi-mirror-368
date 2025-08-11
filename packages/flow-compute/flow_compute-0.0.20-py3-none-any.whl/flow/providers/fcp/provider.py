"""Legacy import shim for Mithril provider.

Historically tests referenced `flow.providers.mithril.provider.MithrilProvider`.
We now provide a thin shim that re-exports the class from the mithril package.
"""

from flow.providers.mithril.provider import MithrilProvider  # noqa: F401

__all__ = ["MithrilProvider"]
