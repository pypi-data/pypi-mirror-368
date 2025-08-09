"""Base storage abstraction interfaces."""

from typing import Any, Dict, List, Optional, Protocol

from flow.api.models import MountSpec


class IStorageResolver(Protocol):
    """Protocol for storage URL resolvers.

    Each provider can implement its own resolver for handling
    storage URLs in a provider-specific way.
    """

    def can_resolve(self, url: str) -> bool:
        """Check if this resolver can handle the given URL.

        Args:
            url: The storage URL to check

        Returns:
            True if this resolver can handle the URL
        """
        ...

    def resolve(self, url: str, target: str, context: Dict[str, Any]) -> MountSpec:
        """Resolve a storage URL to a mount specification.

        Args:
            url: The storage URL to resolve
            target: The target mount path in the container
            context: Provider-specific context (e.g., provider instance)

        Returns:
            MountSpec for mounting the storage

        Raises:
            DataError: If URL cannot be resolved
        """
        ...

    def is_storage_id(self, identifier: str) -> bool:
        """Check if the identifier is a storage ID (vs a name).

        Args:
            identifier: The identifier to check

        Returns:
            True if this is a storage ID, False if it's a name
        """
        ...


class StorageResolverChain:
    """Chain of storage resolvers for handling different URL types.

    This implements the Chain of Responsibility pattern, allowing
    multiple resolvers to be tried in sequence until one can handle
    the URL.
    """

    def __init__(self, resolvers: Optional[List[IStorageResolver]] = None):
        """Initialize the resolver chain.

        Args:
            resolvers: List of resolvers to use, in order of priority
        """
        self.resolvers = resolvers or []

    def add_resolver(self, resolver: IStorageResolver) -> None:
        """Add a resolver to the chain.

        Args:
            resolver: The resolver to add
        """
        self.resolvers.append(resolver)

    def resolve(self, url: str, target: str, context: Optional[Dict[str, Any]] = None) -> MountSpec:
        """Resolve a URL using the chain of resolvers.

        Args:
            url: The storage URL to resolve
            target: The target mount path
            context: Optional context for resolvers

        Returns:
            MountSpec for the resolved storage

        Raises:
            DataError: If no resolver can handle the URL
        """
        context = context or {}

        for resolver in self.resolvers:
            if resolver.can_resolve(url):
                return resolver.resolve(url, target, context)

        # No resolver found
        from flow._internal.data.resolver import DataError

        raise DataError(
            f"No resolver found for URL: {url}",
            suggestions=[
                "Check the URL format",
                "Ensure the storage type is supported by your provider",
            ],
        )
