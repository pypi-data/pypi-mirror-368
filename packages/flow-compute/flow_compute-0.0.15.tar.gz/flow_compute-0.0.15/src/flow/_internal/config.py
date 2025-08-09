"""Configuration for Flow SDK.

Clean, provider-agnostic configuration system that separates
core SDK configuration from provider-specific settings.
"""

import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Type

from . import pricing


@dataclass
class Config:
    """Provider-agnostic Flow SDK configuration.

    Core configuration that works across all providers. This class provides
    a unified interface for managing authentication and provider settings
    regardless of the underlying compute provider.

    Attributes:
        provider: The compute provider to use (e.g., 'mithril').
        auth_token: Authentication token for API access.
        provider_config: Dictionary of provider-specific settings.
        health_config: Dictionary of health monitoring settings.

    Example:
        >>> # Create config from environment
        >>> config = Config.from_env()

        >>> # Create config manually
        >>> config = Config(
        ...     provider="mithril",
        ...     auth_token="your-api-key",
        ...     provider_config={
        ...         "project": "my-project",
        ...         "region": "us-east-1"
        ...     }
        ... )
    """

    provider: str = "mithril"
    auth_token: Optional[str] = None
    provider_config: Dict[str, Any] = field(default_factory=dict)
    health_config: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_env(cls, require_auth: bool = True) -> "Config":
        """Create config from environment variables and config files.

        Loads configuration from multiple sources in precedence order:
        1. Environment variables (highest priority)
        2. flow.yaml in current directory
        3. ~/.flow/config.yaml (lowest priority)

        Environment variables:
            FLOW_PROVIDER: Provider to use (default: mithril)
            MITHRIL_API_KEY: Authentication token for Mithril provider
            MITHRIL_DEFAULT_PROJECT: Default project for Mithril
            MITHRIL_DEFAULT_REGION: Default region for Mithril
            MITHRIL_SSH_KEYS: Comma-separated SSH key names

        Args:
            require_auth: Whether to require authentication token.
                         Set to False for operations that don't need auth.

        Returns:
            Config: Loaded configuration object.

        Raises:
            ValueError: If authentication is required but not configured.

        Example:
            >>> # Load config requiring authentication
            >>> config = Config.from_env(require_auth=True)

            >>> # Load config for local operations
            >>> config = Config.from_env(require_auth=False)
        """
        from flow._internal.config_loader import ConfigLoader

        # Load from all sources with proper precedence
        loader = ConfigLoader()
        sources = loader.load_all_sources()

        provider = sources.provider
        auth_token = sources.api_key

        # Load provider-specific config
        provider_config = {}
        if provider == "mithril":
            provider_config = sources.get_mithril_config()

        # Load health monitoring config
        health_config = sources.get_health_config()

        # Validate auth if required
        if require_auth and (not auth_token or auth_token.startswith("YOUR_")):
            raise ValueError(
                "Authentication not configured. Please either:\n"
                "1. Set MITHRIL_API_KEY environment variable\n"
                "2. Run 'flow init' to set up authentication\n"
                "3. For tests, ensure FLOW_DISABLE_KEYCHAIN=1 is set"
            )

        return cls(
            provider=provider,
            auth_token=auth_token,
            provider_config=provider_config,
            health_config=health_config,
        )

    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests.

        Returns:
            Dict[str, str]: Headers including authorization and content type.

        Example:
            >>> config = Config(auth_token="abc123")
            >>> headers = config.get_headers()
            >>> headers
            {'Authorization': 'Bearer abc123', 'Content-Type': 'application/json'}
        """
        # Get SDK version for User-Agent
        try:
            from flow import __version__

            version = __version__
        except:
            version = "unknown"

        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
            "User-Agent": f"Flow-SDK/{version}",
            "X-Flow-SDK-Version": version,
            "X-Flow-Client": "flow-cli",
        }


# Provider-specific configuration classes
@dataclass
class MithrilConfig:
    """Mithril  provider-specific configuration.

    Attributes:
        api_url: Base URL for Mithril API endpoints.
        project: Mithril project identifier.
        region: Default region for resource creation.
        ssh_keys: List of SSH key names for instance access.

    Example:
        >>> mithril_config = MithrilConfig(
        ...     project="my-project",
        ...     region="us-east-1",
        ...     ssh_keys=["my-key", "team-key"]
        ... )
    """

    api_url: str = field(
        default_factory=lambda: os.getenv("MITHRIL_API_URL", "https://api.mithril.ai")
    )
    project: Optional[str] = None
    region: Optional[str] = None
    ssh_keys: Optional[list[str]] = None
    enable_workload_resume: bool = True  # Enable automatic workload resumption after preemption

    # Default limit prices by GPU type and priority tier
    # Now sourced from centralized pricing module
    limit_prices: Dict[str, Dict[str, float]] = field(
        default_factory=lambda: pricing.DEFAULT_PRICING
    )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MithrilConfig":
        """Create MithrilConfig from dictionary.

        Args:
            data: Dictionary containing configuration values.
                  Unknown keys are ignored.

        Returns:
            MithrilConfig: Configuration object with values from dictionary.

        Example:
            >>> config_dict = {
            ...     "project": "ml-training",
            ...     "region": "us-west-2",
            ...     "ssh_keys": ["dev-key"],
            ...     "unknown_key": "ignored"
            ... }
            >>> mithril_config = MithrilConfig.from_dict(config_dict)
            >>> mithril_config.project
            'ml-training'
        """
        # Get default api_url from environment if not in data
        default_api_url = os.getenv("MITHRIL_API_URL", "https://api.mithril.ai")

        # Get limit_prices - support custom overrides
        custom_pricing = data.get("limit_prices")
        if custom_pricing:
            # Merge custom pricing with defaults
            limit_prices = pricing.get_pricing_table(custom_pricing)
        else:
            limit_prices = pricing.DEFAULT_PRICING

        return cls(
            api_url=data.get("api_url", default_api_url),
            project=data.get("project"),
            region=data.get("region"),
            ssh_keys=data.get("ssh_keys"),
            enable_workload_resume=data.get("enable_workload_resume", True),
            limit_prices=limit_prices,
        )

    @property
    def api_key(self) -> Optional[str]:
        """Legacy property for compatibility during migration.

        This will be removed once all provider code is updated.
        """
        # Temporary: Auth token retrieval during migration period
        # TODO: Remove once provider code is updated to use main Config
        return os.environ.get("MITHRIL_API_KEY")


# Registry for provider configurations
PROVIDER_CONFIGS: Dict[str, Type] = {
    "mithril": MithrilConfig,
}


def get_provider_config_class(provider: str) -> Type:
    """Get the configuration class for a provider.

    Args:
        provider: Provider name (e.g., 'mithril').

    Returns:
        Type: The configuration class for the specified provider.

    Raises:
        ValueError: If the provider is not recognized.

    Example:
        >>> config_class = get_provider_config_class("mithril")
        >>> config_class.__name__
        'MithrilConfig'
    """
    if provider not in PROVIDER_CONFIGS:
        raise ValueError(
            f"Unknown provider: {provider}. "
            f"Available providers: {', '.join(PROVIDER_CONFIGS.keys())}"
        )
    return PROVIDER_CONFIGS[provider]
