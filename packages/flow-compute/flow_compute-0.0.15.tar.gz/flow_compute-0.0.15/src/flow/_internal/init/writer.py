"""Configuration writer for Flow SDK.

Persists configuration to disk using an AWS-style approach:
- ~/.flow/credentials for secrets (INI format)
- ~/.flow/config.yaml for non-sensitive configuration
"""

import configparser
import os
import tempfile
from pathlib import Path
from typing import Any, Optional

import yaml

from flow.api.models import ValidationResult


class ConfigWriter:
    """Writes Flow configuration securely.

    Features:
    - Provider-specific credentials files (~/.flow/credentials.{provider})
    - Atomic file writes with rollback
    - Proper file permissions (0600)
    - Simple, explicit behavior
    """

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize writer.

        Args:
            config_path: Path to config file (defaults to ~/.flow/config.yaml)
        """
        self.config_path = config_path or Path.home() / ".flow" / "config.yaml"
        self.flow_dir = self.config_path.parent

    def write(self, config: dict[str, Any], validation: ValidationResult) -> None:
        """Write configuration to disk.

        Args:
            config: Configuration dictionary
            validation: Validation result (for future use)

        Raises:
            OSError: If unable to write configuration
        """
        # Extract API key before writing to file
        api_key = config.pop("api_key", None)

        # Transform to new config format if provider is specified
        provider = config.get("provider")
        if provider:
            # New provider-based format
            file_config = {"provider": provider}

            # Move provider-specific settings
            if provider == "mithril":
                mithril_config = {}
                if "project" in config:
                    mithril_config["project"] = config.pop("project")
                if "region" in config:
                    mithril_config["region"] = config.pop("region")
                if "api_url" in config:
                    mithril_config["api_url"] = config.pop("api_url")
                if "default_ssh_key" in config:
                    ssh_key = config.pop("default_ssh_key")
                    # Handle platform auto-generation special case
                    if ssh_key == "_auto_":
                        mithril_config["ssh_keys"] = ["_auto_"]
                    else:
                        mithril_config["ssh_keys"] = [ssh_key]

                if mithril_config:
                    file_config["mithril"] = mithril_config

            # Any remaining fields go at top level (for extensibility)
            file_config.update(config)
        else:
            # Legacy format - write as-is
            file_config = config

        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write config file atomically
        self._write_config_file(file_config)

        # Store API key in provider-specific credentials file
        if api_key and provider:
            self._write_provider_credentials(provider, api_key)

    def read_api_key(self, provider: str = "mithril") -> Optional[str]:
        """Read API key from provider-specific credentials file.

        Args:
            provider: Provider name (defaults to mithril)

        Returns:
            API key if found, None otherwise
        """
        credentials_path = self.flow_dir / f"credentials.{provider}"
        if not credentials_path.exists():
            return None

        try:
            config = configparser.ConfigParser()
            config.read(credentials_path)
            return config.get("default", "api_key", fallback=None)
        except Exception:
            return None

    def _write_provider_credentials(self, provider: str, api_key: str) -> None:
        """Write provider-specific credentials file.

        Args:
            provider: Provider name (e.g., 'mithril', 'local')
            api_key: API key to store

        Raises:
            OSError: If unable to write file
        """
        credentials_path = self.flow_dir / f"credentials.{provider}"

        # Simple INI format
        config = configparser.ConfigParser()
        config.add_section("default")
        config.set("default", "api_key", api_key)

        # Write atomically
        with tempfile.NamedTemporaryFile(mode="w", dir=self.flow_dir, delete=False) as tmp:
            config.write(tmp)
            tmp_path = Path(tmp.name)

        # Set proper permissions
        try:
            tmp_path.chmod(0o600)
        except Exception:
            pass

        # Atomic rename
        try:
            tmp_path.replace(credentials_path)
        except Exception:
            tmp_path.unlink(missing_ok=True)
            raise

    def _write_config_file(self, config: dict[str, Any]) -> None:
        """Write config file atomically with proper permissions.

        Handles both legacy flat format and new provider-based format.

        Args:
            config: Configuration dictionary (without api_key)

        Raises:
            OSError: If unable to write file
        """
        # Write to temporary file first
        with tempfile.NamedTemporaryFile(
            mode="w", dir=self.config_path.parent, delete=False
        ) as tmp:
            yaml.dump(config, tmp, default_flow_style=False, sort_keys=False)
            tmp_path = Path(tmp.name)

        # Set proper permissions (0600 - read/write for owner only)
        try:
            tmp_path.chmod(0o600)
        except Exception:
            # Windows may not support chmod, continue anyway
            pass

        # Atomic rename
        try:
            tmp_path.replace(self.config_path)
        except Exception:
            # Clean up temp file on failure
            tmp_path.unlink(missing_ok=True)
            raise
