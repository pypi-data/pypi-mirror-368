"""Script size handling for Mithril startup scripts.

This module provides strategies for handling Mithril's 10KB startup script size limit
through compression, splitting, and external storage.
"""

from .exceptions import ScriptSizeError, ScriptTooLargeError
from .handler import ScriptSizeHandler
from .models import PreparedScript
from .strategies import (
    CompressionStrategy,
    ITransferStrategy,
    InlineStrategy,
    SplitStrategy,
)

__all__ = [
    "ScriptSizeHandler",
    "PreparedScript",
    "ITransferStrategy",
    "InlineStrategy",
    "CompressionStrategy",
    "SplitStrategy",
    "ScriptSizeError",
    "ScriptTooLargeError",
]
