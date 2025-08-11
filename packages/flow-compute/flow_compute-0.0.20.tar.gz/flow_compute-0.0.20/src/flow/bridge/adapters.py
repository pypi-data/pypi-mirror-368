"""Registry of available bridge adapters."""

from flow.bridge.base import BridgeAdapter
from flow.bridge.config import ConfigBridge
from flow.bridge.formatter import FormatterBridge
from flow.bridge.http import HTTPBridge
from flow.bridge.mithril_api import MithrilAPIBridge

# Registry of all available adapters
ADAPTERS: dict[str, type[BridgeAdapter]] = {
    "config": ConfigBridge,
    "http": HTTPBridge,
    "mithril": MithrilAPIBridge,
    "formatter": FormatterBridge,
}

__all__ = ["ADAPTERS", "BridgeAdapter"]
