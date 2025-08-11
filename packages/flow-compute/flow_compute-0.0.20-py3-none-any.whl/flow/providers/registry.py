"""Provider registry used for dynamic discovery and registration.

Providers self-register at import time rather than being hardcoded in the core.
This allows downstream integrations to plug in additional providers without
modifying the SDK.
"""

import logging

from flow._internal.config import Config
from flow.core.provider_interfaces import IProvider
from flow.errors import FlowError

logger = logging.getLogger(__name__)


class ProviderNotFoundError(FlowError):
    """Raised when requested provider is not registered."""

    pass


class ProviderRegistry:
    """Central registry for compute providers.

    Providers self-register when imported, allowing dynamic discovery
    and preventing circular dependencies between core and providers.

    Example:
        >>> # In provider module __init__.py:
        >>> from flow.providers.registry import ProviderRegistry
        >>> from .provider import MyProvider
        >>>
        >>> ProviderRegistry.register("my_provider", MyProvider)

        >>> # Later, in application code:
        >>> provider = ProviderRegistry.create("my_provider", config)
    """

    _providers: dict[str, type[IProvider]] = {}
    _initialized: bool = False

    @classmethod
    def register(cls, name: str, provider_class: type[IProvider]) -> None:
        """Register a provider implementation.

        Args:
            name: Provider identifier (e.g., "mithril", "aws", "gcp")
            provider_class: Provider class implementing IProvider

        Raises:
            ValueError: If provider name already registered
        """
        if name in cls._providers:
            # Allow re-registration for hot reloading in development
            logger.warning(f"Provider '{name}' already registered, overwriting")

        cls._providers[name] = provider_class
        logger.debug(f"Registered provider: {name} -> {provider_class.__name__}")

    @classmethod
    def unregister(cls, name: str) -> None:
        """Remove a provider from the registry.

        Args:
            name: Provider identifier to remove
        """
        if name in cls._providers:
            del cls._providers[name]
            logger.debug(f"Unregistered provider: {name}")

    @classmethod
    def get(cls, name: str) -> type[IProvider]:
        """Get a registered provider class.

        Args:
            name: Provider identifier

        Returns:
            Provider class

        Raises:
            ProviderNotFoundError: If provider not registered
        """
        # Auto-discover providers on first access
        if not cls._initialized:
            cls._auto_discover()

        if name not in cls._providers:
            available = list(cls._providers.keys())
            raise ProviderNotFoundError(
                f"Provider '{name}' not found. Available providers: {sorted(available)}"
            )

        return cls._providers[name]

    @classmethod
    def create(cls, name: str, config: Config) -> IProvider:
        """Create a provider instance.

        Args:
            name: Provider identifier
            config: Configuration object

        Returns:
            Initialized provider instance

        Raises:
            ProviderNotFoundError: If provider not registered
        """
        provider_class = cls.get(name)

        # Use from_config factory method if available
        if hasattr(provider_class, "from_config"):
            return provider_class.from_config(config)

        # Fall back to direct instantiation
        return provider_class(config)

    @classmethod
    def list_providers(cls) -> dict[str, type[IProvider]]:
        """Get all registered providers.

        Returns:
            Dictionary mapping provider names to classes
        """
        if not cls._initialized:
            cls._auto_discover()

        return cls._providers.copy()

    @classmethod
    def clear(cls) -> None:
        """Clear all registered providers. Useful for testing."""
        cls._providers.clear()
        cls._initialized = False
        logger.debug("Cleared provider registry")

    @classmethod
    def _auto_discover(cls) -> None:
        """Auto-discover and import provider modules.

        This triggers the import of provider __init__.py files,
        which should register their providers.
        """
        cls._initialized = True

        # Import known providers to trigger registration
        # This list can be extended or made dynamic
        providers_to_discover = ["mithril", "local", "mock"]  # Add more as needed

        for provider_name in providers_to_discover:
            try:
                # Dynamic import triggers __init__.py execution
                __import__(f"flow.providers.{provider_name}")
                logger.debug(f"Auto-discovered provider: {provider_name}")
            except ImportError as e:
                logger.debug(f"Provider '{provider_name}' not available: {e}")
