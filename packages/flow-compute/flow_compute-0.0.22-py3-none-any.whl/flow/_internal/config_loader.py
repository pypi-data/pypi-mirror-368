"""Unified configuration loader for Flow SDK.

Loads Flow configuration from supported sources with a clear precedence order.
"""

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from flow.errors import ConfigParserError

logger = logging.getLogger(__name__)


@dataclass
class ConfigSources:
    """All configuration data from various sources."""

    env_vars: dict[str, str]
    keychain_api_key: str | None
    config_file: dict[str, Any]

    @property
    def api_key(self) -> str | None:
        """Get API key with proper precedence: env > keychain > file."""
        return (
            self.env_vars.get("MITHRIL_API_KEY")
            or self.keychain_api_key
            or self.config_file.get("api_key")
        )

    @property
    def provider(self) -> str:
        """Get provider with proper precedence and demo-mode override.

        Precedence:
        1) Demo mode (FLOW_DEMO_MODE=1) → provider 'mock' unless FLOW_PROVIDER explicitly set
        2) FLOW_PROVIDER env var
        3) config file 'provider'
        4) default 'mithril'
        """
        # 1) Demo mode may use mock, but do not force provider silently
        demo = self.env_vars.get("FLOW_DEMO_MODE")
        provider_env = self.env_vars.get("FLOW_PROVIDER")
        if demo and str(demo).lower() in ("1", "true", "yes") and provider_env:
            return provider_env

        # 2) Explicit env var wins
        if provider_env:
            return provider_env

        # 3) Config file provider key
        cfg_provider = self.config_file.get("provider") if isinstance(self.config_file, dict) else None
        if cfg_provider:
            return str(cfg_provider)

        # 4) Default
        return "mithril"

    def get_mithril_config(self) -> dict[str, Any]:
        """Get Mithril-specific configuration with proper precedence."""
        config = {}

        # API URL
        config["api_url"] = (
            self.env_vars.get("MITHRIL_API_URL")
            or self.config_file.get("mithril", {}).get("api_url")
            or self.config_file.get("api_url")
            or "https://api.mlfoundry.com"
        )

        # Project
        project = self.env_vars.get("MITHRIL_DEFAULT_PROJECT") or \
            self.config_file.get("mithril", {}).get("project") or \
            self.config_file.get("project")
        if project:
            config["project"] = project

        # Region
        region = self.env_vars.get("MITHRIL_DEFAULT_REGION") or \
            self.config_file.get("mithril", {}).get("region") or \
            self.config_file.get("region")
        if region:
            config["region"] = region

        # SSH Keys
        ssh_keys_env = self.env_vars.get("MITHRIL_SSH_KEYS")
        if ssh_keys_env:
            config["ssh_keys"] = [k.strip() for k in ssh_keys_env.split(",") if k.strip()]
        else:
            # Check config file
            ssh_keys = self.config_file.get("mithril", {}).get("ssh_keys")
            if ssh_keys:
                config["ssh_keys"] = ssh_keys
            else:
                # Legacy single-key field
                legacy_key = self.config_file.get("default_ssh_key") or self.config_file.get("ssh_key")
                if legacy_key:
                    config["ssh_keys"] = [legacy_key]

        # Pricing overrides (from config file only; explicit CLI flags override at runtime)
        try:
            limit_prices = self.config_file.get("mithril", {}).get("limit_prices")
            if isinstance(limit_prices, dict) and limit_prices:
                config["limit_prices"] = limit_prices
        except Exception:
            pass

        return config

    def get_health_config(self) -> dict[str, Any]:
        """Get health monitoring configuration with proper precedence."""
        config = {}

        # Health monitoring enabled
        config["enabled"] = (
            self.env_vars.get("FLOW_HEALTH_MONITORING", "true").lower() == "true"
            if "FLOW_HEALTH_MONITORING" in self.env_vars
            else self.config_file.get("health", {}).get("enabled", True)
        )

        # GPUd configuration
        config["gpud_version"] = self.env_vars.get("FLOW_GPUD_VERSION") or self.config_file.get(
            "health", {}
        ).get("gpud_version", "v0.5.1")

        config["gpud_port"] = int(
            self.env_vars.get("FLOW_GPUD_PORT")
            or self.config_file.get("health", {}).get("gpud_port", 15132)
        )

        config["gpud_bind"] = self.env_vars.get("FLOW_GPUD_BIND") or self.config_file.get(
            "health", {}
        ).get("gpud_bind", "127.0.0.1")

        # Metrics configuration
        config["metrics_endpoint"] = self.env_vars.get(
            "FLOW_METRICS_ENDPOINT"
        ) or self.config_file.get("health", {}).get("metrics_endpoint")

        config["metrics_batch_size"] = int(
            self.env_vars.get("FLOW_METRICS_BATCH_SIZE")
            or self.config_file.get("health", {}).get("metrics_batch_size", 100)
        )

        config["metrics_interval"] = int(
            self.env_vars.get("FLOW_METRICS_INTERVAL")
            or self.config_file.get("health", {}).get("metrics_interval", 60)
        )

        # Storage configuration
        config["retention_days"] = int(
            self.env_vars.get("FLOW_METRICS_RETENTION_DAYS")
            or self.config_file.get("health", {}).get("retention_days", 7)
        )

        config["compress_after_days"] = int(
            self.env_vars.get("FLOW_METRICS_COMPRESS_AFTER_DAYS")
            or self.config_file.get("health", {}).get("compress_after_days", 1)
        )

        return config


class ConfigLoader:
    """Unified configuration loader with clear precedence and error handling."""

    def __init__(self, config_path: Path | None = None):
        """Initialize the loader.

        Args:
            config_path: Path to config file (defaults to ~/.flow/config.yaml)
        """
        self.config_path = config_path or Path.home() / ".flow" / "config.yaml"

    def load_all_sources(self) -> ConfigSources:
        """Load configuration from all available sources.

        Returns:
            ConfigSources object with all available configuration
        """
        # 1. Environment variables (highest precedence)
        env_vars = dict(os.environ)

        # 2. Credentials file API key
        keychain_api_key = self._load_from_credentials_file()

        # 3. Config file (lowest precedence)
        config_file = self._load_config_file()

        return ConfigSources(
            env_vars=env_vars, keychain_api_key=keychain_api_key, config_file=config_file
        )

    def _load_from_credentials_file(self) -> str | None:
        """Load API key from provider-specific credentials file.

        Returns:
            API key if found, None otherwise
        """
        try:
            # Get provider from environment or config file
            provider = os.environ.get("FLOW_PROVIDER")
            if not provider:
                config = self._load_config_file()
                provider = config.get("provider", "mithril")

            # Check provider-specific credentials file directly
            credentials_path = Path.home() / ".flow" / f"credentials.{provider}"
            if credentials_path.exists():
                import configparser

                cfg = configparser.ConfigParser()
                cfg.read(credentials_path)
                api_key = cfg.get("default", "api_key", fallback=None)
                if api_key:
                    return api_key

        except Exception as e:
            logger.debug(f"Could not load from credentials file: {e}")
            return None

    def _load_config_file(self) -> dict[str, Any]:
        """Load configuration from YAML file.

        Returns:
            Configuration dict, empty dict if file doesn't exist or has errors
        """
        if not self.config_path.exists():
            return {}

        try:
            with open(self.config_path) as f:
                content = yaml.safe_load(f) or {}
                if not isinstance(content, dict):
                    raise ConfigParserError(
                        f"Configuration file must contain a YAML dictionary, got {type(content).__name__}",
                        suggestions=[
                            "Ensure your config file starts with key: value pairs",
                            "Check that you haven't accidentally created a list or string",
                            "Example valid config: api_key: YOUR_KEY",
                        ],
                        error_code="CONFIG_002",
                    )
                return content
        except yaml.YAMLError as e:
            raise ConfigParserError(
                f"Invalid YAML syntax in {self.config_path}: {str(e)}",
                suggestions=[
                    "Check YAML indentation (use spaces, not tabs)",
                    "Ensure all strings with special characters are quoted",
                    "Validate syntax at yamllint.com",
                    "Common issue: unquoted strings containing colons",
                ],
                error_code="CONFIG_001",
            ) from e
        except ConfigParserError:
            raise
        except Exception as e:
            # For unexpected errors, still log and return empty dict for backward compatibility
            logger.warning(f"Unexpected error reading config file {self.config_path}: {e}")
            return {}

    def has_valid_config(self) -> bool:
        """Check if valid configuration exists.

        Returns:
            True if we have an API key from any source
        """
        sources = self.load_all_sources()
        api_key = sources.api_key
        return bool(api_key and not api_key.startswith("YOUR_"))

    def get_config_status(self) -> tuple[bool, str]:
        """Get detailed configuration status.

        Returns:
            Tuple of (is_valid, status_message)
        """
        sources = self.load_all_sources()

        # Check API key
        if sources.env_vars.get("MITHRIL_API_KEY"):
            api_key_source = "environment variable (MITHRIL_API_KEY)"
        elif sources.keychain_api_key:
            api_key_source = "credentials file"
        elif sources.config_file.get("api_key"):
            api_key_source = "config file"
        else:
            return (
                False,
                "No API key found in environment (MITHRIL_API_KEY), credentials file, or config file",
            )

        api_key = sources.api_key
        if not api_key:
            return False, "No API key configured"

        if api_key.startswith("YOUR_"):
            return False, f"API key in {api_key_source} needs to be updated"

        # Check project
        mithril_config = sources.get_mithril_config()
        if not mithril_config.get("project"):
            return False, f"API key found in {api_key_source}, but no project configured"

        return True, f"Valid configuration found (API key from {api_key_source})"
