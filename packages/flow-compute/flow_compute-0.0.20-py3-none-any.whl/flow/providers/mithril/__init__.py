"""Mithril Provider implementation.

The Mithril  provider implements compute and storage
operations using the Mithril API. It supports market-based resource allocation
through auctions.
"""

from flow.providers.mithril.manifest import MITHRIL_MANIFEST
from flow.providers.mithril.provider import MithrilProvider
from flow.providers.registry import ProviderRegistry

# Import from the direct module, not the setup subpackage
try:
    from flow.providers.mithril.setup import MithrilProviderSetup
except ImportError:
    # Fallback if setup module causes issues
    MithrilProviderSetup = None

# Self-register with the provider registry
ProviderRegistry.register("mithril", MithrilProvider)

__all__ = ["MithrilProvider", "MithrilProviderSetup", "MITHRIL_MANIFEST"]
