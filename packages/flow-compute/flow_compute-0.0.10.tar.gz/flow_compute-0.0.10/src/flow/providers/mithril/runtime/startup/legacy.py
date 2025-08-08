"""Mithril-specific startup script generation.

This module provides backward compatibility while using the new
implementation with better separation of concerns.

Key Mithril compatibility features:
- Respects Mithril's 10,000 character limit for startup scripts
- Automatically compresses scripts exceeding the limit
- Creates log symlinks at Mithril-expected locations
"""

from flow.api.models import TaskConfig

from ...core.constants import STARTUP_SCRIPT_MAX_SIZE
from .builder import MithrilStartupScriptBuilder as _NewBuilder


class MithrilStartupScriptBuilder:
    """Builds startup scripts for Mithril instances.

    This class provides backward compatibility while delegating to
    the new implementation with cleaner architecture.
    """

    # Maximum size before we need to compress
    MAX_UNCOMPRESSED_SIZE = STARTUP_SCRIPT_MAX_SIZE

    def __init__(self):
        """Initialize with new builder implementation."""
        self._builder = _NewBuilder()

    def build(self, config: TaskConfig) -> str:
        """Build a startup script from task configuration.

        Args:
            config: Task configuration

        Returns:
            Complete startup script as a string

        Raises:
            ValueError: If configuration validation fails
        """
        script = self._builder.build(config)

        if not script.is_valid:
            raise ValueError(f"Invalid configuration: {', '.join(script.validation_errors)}")

        return script.content
