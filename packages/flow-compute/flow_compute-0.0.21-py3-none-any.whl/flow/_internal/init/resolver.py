"""Configuration resolver for Flow SDK init command."""

from pathlib import Path
from typing import Any

import yaml


class ConfigResolver:
    """Resolves configuration from multiple sources with clear precedence."""

    DEFAULTS = {
        "api_key": None,
        "project": None,
        "region": "us-central1-a",
        "api_url": "https://api.mithril.ai",
    }

    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path or Path.home() / ".flow" / "config.yaml"

    def resolve(self, cli_args: dict[str, Any], env: dict[str, str]) -> dict[str, Any]:
        """Resolve configuration: CLI > Environment > File > Defaults."""
        return {
            **self.DEFAULTS,
            **self._load_file_config(),
            **self._load_env_config(env),
            **{k: v for k, v in cli_args.items() if v is not None},
        }

    def _load_file_config(self) -> dict[str, Any]:
        """Load configuration from file."""
        if not self.config_path.exists():
            return {}

        try:
            with open(self.config_path) as f:
                data = yaml.safe_load(f) or {}
        except (OSError, yaml.YAMLError):
            return {}

        config = {}

        # Direct values
        for key in self.DEFAULTS:
            if key in data:
                config[key] = data[key]

        # Provider-specific values (e.g., mithril.project)
        provider = data.get("provider", "mithril")
        if provider in data and isinstance(data[provider], dict):
            provider_data = data[provider]
            for key in ["project", "region", "api_url"]:
                if key in provider_data:
                    config[key] = provider_data[key]

        return config

    def _load_env_config(self, env: dict[str, str]) -> dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}

        # Provider-specific API key
        if "MITHRIL_API_KEY" in env or "Mithril_API_KEY" in env:
            config["api_key"] = env.get("MITHRIL_API_KEY") or env.get("Mithril_API_KEY")
        if "MITHRIL_PROJECT" in env or "Mithril_PROJECT" in env:
            config["project"] = env.get("MITHRIL_PROJECT") or env.get("Mithril_PROJECT")
        if "MITHRIL_REGION" in env or "Mithril_REGION" in env:
            config["region"] = env.get("MITHRIL_REGION") or env.get("Mithril_REGION")
        if "MITHRIL_API_URL" in env or "Mithril_API_URL" in env:
            config["api_url"] = env.get("MITHRIL_API_URL") or env.get("Mithril_API_URL")

        return config

    def get_missing_required_fields(self, config: dict[str, Any]) -> list[str]:
        """Return required fields that are missing."""
        return [field for field in ["api_key", "project"] if not config.get(field)]
