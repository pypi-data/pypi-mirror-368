"""Configuration for Flow SDK.

Clean, provider-agnostic configuration system that separates
core SDK configuration from provider-specific settings.
"""

import os
from dataclasses import dataclass, field
from typing import Any

from flow._internal import pricing


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
    auth_token: str | None = None
    provider_config: dict[str, Any] = field(default_factory=dict)
    health_config: dict[str, Any] = field(default_factory=dict)

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
        # If an explicit environment API key is provided, prefer mithril provider
        env_api_key = os.getenv("MITHRIL_API_KEY")
        if env_api_key:
            provider = "mithril"

        # Load provider-specific config
        provider_config = {}
        if provider == "mithril":
            provider_config = sources.get_mithril_config()
            # Normalize SSH keys parsing (handle spaces and empty strings)
            ssh_keys = provider_config.get("ssh_keys")
            if isinstance(ssh_keys, str):
                parsed = [k.strip() for k in ssh_keys.split(",") if k.strip()]
                if parsed:
                    provider_config["ssh_keys"] = parsed
                else:
                    provider_config.pop("ssh_keys", None)
            # Explicitly parse from environment if present (takes precedence)
            env_ssh = os.getenv("MITHRIL_SSH_KEYS")
            if env_ssh is not None:
                parsed = [k.strip() for k in env_ssh.split(",") if k.strip()]
                # Even if parsed is empty, tests expect preserving explicit empty list handling earlier.
                # Here, only set when non-empty; otherwise leave as-is to allow prior normalization to apply.
                if parsed:
                    provider_config["ssh_keys"] = parsed
        elif provider == "mock":
            # For demo/mock, surface top-level settings and demo block for UX
            cfg = sources.config_file if isinstance(sources.config_file, dict) else {}
            demo_cfg = cfg.get("demo", {}) if isinstance(cfg.get("demo", {}), dict) else {}
            provider_config = {
                "project": cfg.get("project"),
                "region": cfg.get("region"),
                "default_ssh_key": cfg.get("default_ssh_key"),
                "demo": {
                    "api_key": demo_cfg.get("api_key"),
                },
            }

        # Load health monitoring config
        health_config = sources.get_health_config()

        # In demo/mock mode, skip auth requirement only when explicitly enabled
        if provider == "mock":
            if os.getenv("FLOW_DEMO") or os.getenv("FLOW_TEST_MODE"):
                require_auth = False

        # Validate auth if required
        # When auth is required, accept API key from env, credentials file, or
        # config file as a last resort (but reject placeholder YOUR_* values).
        api_key_candidate = env_api_key or sources.keychain_api_key or sources.config_file.get("api_key")
        if require_auth and (not api_key_candidate or str(api_key_candidate).startswith("YOUR_")):
            # Use a terse, easily detectable message that CLI can intercept and reformat
            raise ValueError(
                "Authentication not configured: run 'flow init' or set MITHRIL_API_KEY"
            )

        return cls(
            provider=provider,
            auth_token=api_key_candidate if require_auth else auth_token,
            provider_config=provider_config,
            health_config=health_config,
        )

    def get_headers(self) -> dict[str, str]:
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

        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
            "User-Agent": f"flow-compute/{version}",
            "X-Flow-Compute-Version": version,
        }
        # Add origin tag (SDK default; CLI overrides via env at process start)
        try:
            from flow.utils.origin import detect_origin as _detect_origin

            headers["X-Flow-Origin"] = _detect_origin()
        except Exception:
            pass
        return headers


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
        default_factory=lambda: os.getenv("MITHRIL_API_URL", "https://api.mlfoundry.com")
    )
    project: str | None = None
    region: str | None = None
    ssh_keys: list[str] | None = None
    enable_workload_resume: bool = True  # Enable automatic workload resumption after preemption

    # Default limit prices by GPU type and priority tier
    # Now sourced from centralized pricing module
    limit_prices: dict[str, dict[str, float]] = field(
        default_factory=lambda: pricing.DEFAULT_PRICING
    )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MithrilConfig":
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
        default_api_url = os.getenv("MITHRIL_API_URL", "https://api.mlfoundry.com")

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
    def api_key(self) -> str | None:
        """Legacy property for compatibility during migration.

        This will be removed once all provider code is updated.
        """
        # Temporary: Auth token retrieval during migration period
        # TODO: Remove once provider code is updated to use main Config
        return os.environ.get("MITHRIL_API_KEY")


# Registry for provider configurations
PROVIDER_CONFIGS: dict[str, type] = {
    "mithril": MithrilConfig,
}


def get_provider_config_class(provider: str) -> type:
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
