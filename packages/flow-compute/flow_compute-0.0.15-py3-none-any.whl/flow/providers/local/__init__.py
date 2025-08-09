"""Local testing provider for Flow SDK.

Enables rapid development and testing without cloud infrastructure.
"""

from flow.providers.local.config import LocalInstanceMapping, LocalTestConfig
from flow.providers.local.executor import ContainerTaskExecutor, ProcessTaskExecutor
from flow.providers.local.manifest import LOCAL_MANIFEST
from flow.providers.local.provider import LocalProvider
from flow.providers.local.storage import LocalStorage

# Register with provider registry
from flow.providers.registry import ProviderRegistry

ProviderRegistry.register("local", LocalProvider)

__all__ = [
    "LocalProvider",
    "LocalTestConfig",
    "LocalInstanceMapping",
    "ContainerTaskExecutor",
    "ProcessTaskExecutor",
    "LocalStorage",
    "LOCAL_MANIFEST",
]
