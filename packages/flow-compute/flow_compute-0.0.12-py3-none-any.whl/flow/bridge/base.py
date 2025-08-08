"""Base class for bridge adapters."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BridgeAdapter(ABC):
    """Base class for all bridge adapters.

    Bridge adapters provide a JSON-serializable interface to Flow SDK components.
    Each adapter exposes specific functionality through methods that can be called
    via the bridge protocol.
    """

    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Return a dictionary describing the adapter's capabilities.

        This should include:
        - Available methods
        - Method signatures
        - Brief descriptions

        Returns:
            Dictionary describing adapter capabilities
        """
        pass
