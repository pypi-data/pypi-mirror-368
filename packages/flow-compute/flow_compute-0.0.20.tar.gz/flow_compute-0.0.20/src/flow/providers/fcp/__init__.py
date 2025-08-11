"""Compatibility layer for older imports expecting `flow.providers.mithril`.

This module re-exports Mithril provider symbols so legacy tests that import
`flow.providers.mithril.provider` or related utilities continue to work.
"""

from flow.providers.mithril.provider import MithrilProvider  # noqa: F401

# Re-export RemoteExecutionError from the mithril remote operations so tests
# importing from `flow.providers.mithril.remote_operations` work.
from flow.providers.mithril.remote_operations import (  # noqa: F401
    RemoteExecutionError,
)

__all__ = [
    "MithrilProvider",
    "RemoteExecutionError",
]
