"""Provider factory using the registry pattern.

This replaces the old provider_factory in core, removing the circular
dependency where core imported from providers.
"""

from flow._internal.config import Config
from flow.core.provider_interfaces import IProvider
from flow.providers.registry import ProviderRegistry


def create_provider(config: Config) -> IProvider:
    """Create a provider instance from configuration.

    This is the main entry point for provider creation, used by
    the Flow class and other high-level APIs.

    Args:
        config: SDK configuration with provider settings

    Returns:
        Initialized provider instance

    Raises:
        ProviderNotFoundError: If the requested provider is not available

    Example:
        >>> from flow._internal.config import Config
        >>> from flow.providers.factory import create_provider
        >>>
        >>> config = Config(provider="mithril", ...)
        >>> provider = create_provider(config)
    """
    return ProviderRegistry.create(config.provider, config)
