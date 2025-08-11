"""Provider resolver for CLI.

Single source of truth for provider information in the CLI. Loads provider
manifests and exposes a small API for querying provider-specific details
without hardcoding provider knowledge.
"""

import importlib
import re
from pathlib import Path
from typing import Any

from flow.errors import ProviderError
from flow.providers.base import ProviderManifest


class ProviderResolver:
    """Single source of truth for provider information in CLI.

    This resolver loads provider manifests and provides a clean API
    for the CLI to query provider-specific information without
    hardcoding provider knowledge.
    """

    _manifest_cache: dict[str, ProviderManifest] = {}

    @classmethod
    def get_manifest(cls, provider_name: str) -> ProviderManifest:
        """Get the complete provider manifest.

        Args:
            provider_name: Name of the provider (e.g., "mithril", "aws")

        Returns:
            ProviderManifest with all provider specifications

        Raises:
            ProviderError: If provider not found or manifest invalid
        """
        if provider_name in cls._manifest_cache:
            return cls._manifest_cache[provider_name]

        try:
            # Import provider module (existence check)
            importlib.import_module(f"flow.providers.{provider_name}")

            # Prefer explicit manifest submodule import to avoid MagicMock hasattr issues
            try:
                manifest_module = importlib.import_module(
                    f"flow.providers.{provider_name}.manifest"
                )
                manifest_name = f"{provider_name.upper()}_MANIFEST"
                manifest = getattr(manifest_module, manifest_name)
            except ImportError:
                # Fall back to constructing from capabilities for legacy providers
                provider_module = importlib.import_module(f"flow.providers.{provider_name}")
                manifest = cls._construct_legacy_manifest(provider_name, provider_module)

            cls._manifest_cache[provider_name] = manifest
            return manifest

        except ImportError as e:
            raise ProviderError(f"Provider '{provider_name}' not found") from e
        except AttributeError as e:
            raise ProviderError(f"Provider '{provider_name}' has invalid manifest") from e

    @classmethod
    def resolve_mount_path(cls, provider_name: str, source: str) -> str:
        """Resolve mount source to target path using provider rules.

        Args:
            provider_name: Name of the provider
            source: Mount source (e.g., "s3://bucket/path")

        Returns:
            Target mount path in container
        """
        manifest = cls.get_manifest(provider_name)

        # Check each pattern in order
        for pattern, target in manifest.cli_config.mount_patterns.items():
            if re.match(pattern, source):
                return target

        # Default fallback via centralized rule
        from flow.core.mount_rules import auto_target_for_source

        return auto_target_for_source(source)

    @classmethod
    def get_connection_command(cls, provider_name: str, task: Any) -> str | None:
        """Get connection command for a task.

        Args:
            provider_name: Name of the provider
            task: Task object with connection details

        Returns:
            Connection command string or None if not supported
        """
        manifest = cls.get_manifest(provider_name)
        method = manifest.cli_config.connection_method

        if method.type == "ssh" and hasattr(task, "ssh_host"):
            return method.command_template.format(
                host=task.ssh_host,
                port=getattr(task, "ssh_port", 22),
                user=getattr(task, "ssh_user", "ubuntu"),
            )
        elif method.type == "web" and hasattr(task, "web_url"):
            return f"Open in browser: {task.web_url}"

        return None

    @classmethod
    def validate_config_value(cls, provider_name: str, key: str, value: str) -> bool:
        """Validate a configuration value against provider rules.

        Args:
            provider_name: Name of the provider
            key: Configuration key (e.g., "api_key")
            value: Value to validate

        Returns:
            True if valid, False otherwise
        """
        manifest = cls.get_manifest(provider_name)

        # Check validation rules
        if key == "api_key" and manifest.validation.api_key_pattern:
            return bool(re.match(manifest.validation.api_key_pattern, value))
        elif key == "region" and manifest.validation.region_pattern:
            return bool(re.match(manifest.validation.region_pattern, value))
        elif key == "project" and manifest.validation.project_name_pattern:
            return bool(re.match(manifest.validation.project_name_pattern, value))

        # Check config field patterns
        for field in manifest.cli_config.config_fields:
            if field.name == key and field.validation_pattern:
                return bool(re.match(field.validation_pattern, value))

        # No validation rules, assume valid
        return True

    @classmethod
    def get_env_vars(cls, provider_name: str) -> dict[str, str]:
        """Get environment variable names for a provider.

        Args:
            provider_name: Name of the provider

        Returns:
            Dictionary mapping config keys to env var names
        """
        manifest = cls.get_manifest(provider_name)
        env_vars = {}

        # Get from env_vars list
        for env_var in manifest.cli_config.env_vars:
            # Map common config keys to env vars
            if "API_KEY" in env_var.name:
                env_vars["api_key"] = env_var.name
            elif "PROJECT" in env_var.name:
                env_vars["project"] = env_var.name
            elif "REGION" in env_var.name:
                env_vars["region"] = env_var.name

        # Also check config fields
        for field in manifest.cli_config.config_fields:
            if field.env_var:
                env_vars[field.name] = field.env_var

        return env_vars

    @classmethod
    def get_default_region(cls, provider_name: str) -> str | None:
        """Get default region for a provider.

        Args:
            provider_name: Name of the provider

        Returns:
            Default region or None
        """
        manifest = cls.get_manifest(provider_name)
        return manifest.cli_config.default_region

    @classmethod
    def _construct_legacy_manifest(
        cls, provider_name: str, provider_module: Any
    ) -> ProviderManifest:
        """Construct a manifest for providers that don't have one yet."""
        # This provides backward compatibility
        # Real implementation would introspect the provider
        raise NotImplementedError(f"Provider '{provider_name}' needs to define a manifest")
