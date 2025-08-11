"""Legacy import shim for RemoteExecutionError.

Tests may import `flow.providers.mithril.remote_operations.RemoteExecutionError`.
Forward to mithril implementation to maintain compatibility.
"""

from flow.providers.mithril.remote_operations import RemoteExecutionError  # noqa: F401

__all__ = ["RemoteExecutionError"]
