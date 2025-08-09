"""Registry of available bridge adapters."""

from typing import Dict, Type

from .base import BridgeAdapter
from .config import ConfigBridge
from .mithril_api import MithrilAPIBridge
from .formatter import FormatterBridge
from .http import HTTPBridge

# Registry of all available adapters
ADAPTERS: Dict[str, Type[BridgeAdapter]] = {
    "config": ConfigBridge,
    "http": HTTPBridge,
    "mithril": MithrilAPIBridge,
    "formatter": FormatterBridge,
}

__all__ = ["ADAPTERS", "BridgeAdapter"]
