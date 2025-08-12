"""Configuration bridge adapter."""

import os
from pathlib import Path
from typing import Any

from flow._internal.config_loader import ConfigLoader
from flow.bridge.base import BridgeAdapter


class ConfigBridge(BridgeAdapter):
    """Bridge adapter for Flow SDK configuration management."""

    def __init__(self):
        """Initialize the config bridge."""
        self._loader = None

    @property
    def loader(self) -> ConfigLoader:
        """Lazy-load the ConfigLoader instance."""
        if self._loader is None:
            self._loader = ConfigLoader()
        return self._loader

    def get_capabilities(self) -> dict[str, Any]:
        """Return capabilities of the config adapter."""
        return {
            "description": "Flow SDK configuration management",
            "methods": {
                "get_config": {
                    "description": "Get complete configuration",
                    "args": {},
                    "returns": "dict",
                },
                "get_api_key": {
                    "description": "Get API key from config or environment",
                    "args": {},
                    "returns": "str or null",
                },
                "get_project": {
                    "description": "Get project from config or environment",
                    "args": {},
                    "returns": "str or null",
                },
                "get_api_url": {
                    "description": "Get API URL from config or environment",
                    "args": {},
                    "returns": "str",
                },
                "get_region": {
                    "description": "Get default region from config",
                    "args": {},
                    "returns": "str or null",
                },
                "has_flow_config": {
                    "description": "Check if Flow SDK config exists",
                    "args": {},
                    "returns": "bool",
                },
                "get_config_path": {
                    "description": "Get path to Flow config file",
                    "args": {},
                    "returns": "str",
                },
            },
        }

    def get_config(self) -> dict[str, Any]:
        """Get complete configuration.

        Returns:
            Dictionary with all configuration values
        """
        try:
            # Load config
            config = self.loader.load_config()

            # Convert to serializable dict
            return {
                "api_key": config.api_key,
                "project": config.project,
                "api_url": config.api_url,
                "region": config.region,
                "provider": config.provider,
            }
        except Exception as e:
            # Return partial config even if some fields fail
            return {
                "api_key": os.environ.get("MITHRIL_API_KEY"),
                "project": os.environ.get("MITHRIL_PROJECT"),
                "api_url": os.environ.get("MITHRIL_API_URL") or "https://api.mithril.ai/v2",
                "region": os.environ.get("MITHRIL_REGION"),
                "provider": "mithril",
                "error": str(e),
            }

    def get_api_key(self) -> str | None:
        """Get API key from config or environment.

        Returns:
            API key or None if not configured
        """
        # Check environment first (matches mithril-js behavior)
        api_key = os.environ.get("MITHRIL_API_KEY")
        if api_key:
            return api_key

        # Try Flow config
        try:
            config = self.loader.load_config()
            return config.api_key
        except:
            return None

    def get_project(self) -> str | None:
        """Get project from config or environment.

        Returns:
            Project name or None if not configured
        """
        # Check environment first
        project = os.environ.get("MITHRIL_PROJECT")
        if project:
            return project

        # Try Flow config
        try:
            config = self.loader.load_config()
            return config.project
        except:
            return None

    def get_api_url(self) -> str:
        """Get API URL from config or environment.

        Returns:
            API URL (defaults to Mithril production URL)
        """
        # Check environment first
        url = os.environ.get("MITHRIL_API_URL")
        if url:
            return url

        # Try Flow config
        try:
            config = self.loader.load_config()
            if config.api_url:
                return config.api_url
        except:
            pass

        # No legacy fallback; use canonical env var only

        # Default to Mithril production
        return "https://api.mithril.ai/v2"

    def get_region(self) -> str | None:
        """Get default region from config.

        Returns:
            Region or None if not configured
        """
        try:
            config = self.loader.load_config()
            return config.region
        except:
            return None

    def has_flow_config(self) -> bool:
        """Check if Flow SDK config exists.

        Returns:
            True if config file exists
        """
        config_path = Path.home() / ".flow" / "config.yaml"
        return config_path.exists()

    def get_config_path(self) -> str:
        """Get path to Flow config file.

        Returns:
            Absolute path to config file
        """
        return str(Path.home() / ".flow" / "config.yaml")
