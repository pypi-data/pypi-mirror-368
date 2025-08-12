"""Registry for frontend adapters."""

from flow._internal.frontends.base import BaseFrontendAdapter


class FrontendRegistry:
    """Registry for frontend adapter implementations."""

    _adapters: dict[str, type[BaseFrontendAdapter]] = {}

    @classmethod
    def register(cls, name: str):
        """Decorator to register a frontend adapter.

        Usage:
            @FrontendRegistry.register("slurm")
            class SlurmFrontendAdapter(BaseFrontendAdapter):
                ...
        """

        def decorator(adapter_class: type[BaseFrontendAdapter]) -> type[BaseFrontendAdapter]:
            cls._adapters[name] = adapter_class
            return adapter_class

        return decorator

    @classmethod
    def get_adapter(cls, name: str) -> BaseFrontendAdapter:
        """Get frontend adapter instance by name.

        Args:
            name: Frontend name (e.g., "slurm", "submitit", "yaml")

        Returns:
            Frontend adapter instance

        Raises:
            ValueError: If frontend name is not registered
        """
        if name not in cls._adapters:
            raise ValueError(
                f"Unknown frontend: {name}. Available frontends: {list(cls._adapters.keys())}"
            )

        adapter_class = cls._adapters[name]
        return adapter_class(name=name)

    @classmethod
    def list_frontends(cls) -> list[str]:
        """List all registered frontend names."""
        return list(cls._adapters.keys())

    @classmethod
    def clear(cls) -> None:
        """Clear all registered frontends (mainly for testing)."""
        cls._adapters.clear()
