"""Mithril Provider implementation.

The Mithril  provider implements compute and storage
operations using the Mithril API. It supports market-based resource allocation
through auctions.
"""

from flow.providers.registry import ProviderRegistry

from .manifest import MITHRIL_MANIFEST
from .provider import MithrilProvider

# Import from the direct module, not the setup subpackage
try:
    from .setup import MithrilProviderSetup
except ImportError:
    # Fallback if setup module causes issues
    MithrilProviderSetup = None

# Self-register with the provider registry
ProviderRegistry.register("mithril", MithrilProvider)

__all__ = ["MithrilProvider", "MithrilProviderSetup", "MITHRIL_MANIFEST"]
