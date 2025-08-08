"""Flow SDK providers.

This package contains provider implementations for different cloud platforms.
Each provider implements the IProvider interface and self-registers with the
provider registry.

Currently supported:
- Mithril

Adding a new provider:
1. Create a new package under providers/ (e.g., providers/aws/)
2. Implement the IProvider interface
3. Register in the package's __init__.py:
   >>> from flow.providers.registry import ProviderRegistry
   >>> ProviderRegistry.register("aws", AWSProvider)

The provider will then be automatically available through the factory.
"""

# Import providers to trigger registration
from . import mithril
from .base import PricingModel, ProviderCapabilities, ProviderInfo
from .factory import create_provider
from .registry import ProviderRegistry

__all__ = [
    "create_provider",
    "ProviderRegistry",
    "ProviderCapabilities",
    "ProviderInfo",
    "PricingModel",
]
