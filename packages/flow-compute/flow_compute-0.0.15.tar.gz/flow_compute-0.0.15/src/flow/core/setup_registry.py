"""Registry for provider setup implementations.

Manages the mapping between provider names and their setup adapters.
"""

from typing import Dict, Type, Optional
from flow.core.setup_adapters import ProviderSetupAdapter
from flow.core.provider_setup import ProviderSetup


class SetupRegistry:
    """Registry for provider setup implementations."""

    _registry: Dict[str, Type[ProviderSetup]] = {}
    _adapter_registry: Dict[str, Type[ProviderSetupAdapter]] = {}

    @classmethod
    def register(cls, provider_name: str, setup_class: Type[ProviderSetup]):
        """Register a provider setup implementation.

        Args:
            provider_name: Name of the provider
            setup_class: Setup implementation class
        """
        cls._registry[provider_name.lower()] = setup_class

    @classmethod
    def register_adapter(cls, provider_name: str, adapter_class: Type[ProviderSetupAdapter]):
        """Register a provider setup adapter.

        Args:
            provider_name: Name of the provider
            adapter_class: Setup adapter implementation class
        """
        cls._adapter_registry[provider_name.lower()] = adapter_class

    @classmethod
    def get_setup(cls, provider_name: str) -> Optional[ProviderSetup]:
        """Get setup implementation for a provider.

        Args:
            provider_name: Name of the provider

        Returns:
            Setup instance or None if not found
        """
        setup_class = cls._registry.get(provider_name.lower())
        if setup_class:
            return setup_class()
        return None

    @classmethod
    def get_adapter(cls, provider_name: str) -> Optional[ProviderSetupAdapter]:
        """Get setup adapter for a provider.

        Args:
            provider_name: Name of the provider

        Returns:
            Setup adapter instance or None if not found
        """
        adapter_class = cls._adapter_registry.get(provider_name.lower())
        if adapter_class:
            return adapter_class()
        return None

    @classmethod
    def list_providers(cls) -> list[str]:
        """List all registered providers.

        Returns:
            List of provider names
        """
        return list(cls._registry.keys())

    @classmethod
    def list_adapters(cls) -> list[str]:
        """List all providers that have registered setup adapters.

        Returns:
            List of provider names with adapters
        """
        return list(cls._adapter_registry.keys())


# Register providers
def register_providers():
    """Register all available provider setups."""
    # Import here to avoid circular imports
    from flow.providers.mithril.setup import MithrilSetupAdapter

    # Only register the adapter for now (old setup causes circular imports)
    SetupRegistry.register_adapter("mithril", MithrilSetupAdapter)

    # Future providers would be registered here
    # from flow.providers.local.setup import LocalProviderSetup
    # SetupRegistry.register("local", LocalProviderSetup)
