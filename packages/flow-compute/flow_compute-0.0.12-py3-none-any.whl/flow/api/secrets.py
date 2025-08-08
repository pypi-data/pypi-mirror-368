"""Secure secrets management for Flow tasks.

This module provides a type-safe interface for managing secrets in Flow tasks,
ensuring sensitive data is never exposed in logs, configurations, or code.
Secrets are injected at runtime through environment variables or secure stores.

Example:
    >>> from flow import FlowApp, Secret
    >>>
    >>> app = FlowApp()
    >>>
    >>> @app.function(
    ...     gpu="a100",
    ...     secrets=[
    ...         Secret.from_name("huggingface"),
    ...         Secret.from_env("OPENAI_API_KEY")
    ...     ]
    ... )
    ... def train_model(config_path: str):
    ...     import os
    ...     # Secrets are available as environment variables
    ...     hf_token = os.environ["HF_TOKEN"]  # from "huggingface" secret
    ...     openai_key = os.environ["OPENAI_API_KEY"]  # from env
    ...     # ... use secrets safely ...
"""

import os
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class Secret(BaseModel):
    """Secure secret reference for runtime injection.

    Secrets provide a safe way to pass sensitive data (API keys, tokens,
    passwords) to tasks without exposing them in code or configurations.
    The actual secret values are stored securely and injected at runtime.

    Security principles:
    - Never log or print secret values
    - Store references only, not actual values
    - Inject at runtime via environment variables
    - Provider handles secure storage/retrieval

    Attributes:
        name: Secret identifier in provider's secret store
        env_vars: Mapping of environment variable names to secret keys
        source: Where the secret comes from ("provider", "env", "file")
    """

    name: str = Field(..., description="Secret identifier")
    env_vars: Dict[str, str] = Field(
        default_factory=dict, description="Environment variable mappings"
    )
    source: str = Field("provider", description="Secret source")

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        """Ensure secret name is valid."""
        if not v or not v.strip():
            raise ValueError("Secret name cannot be empty")
        # Basic validation - alphanumeric, dash, underscore
        if not all(c.isalnum() or c in "-_" for c in v):
            raise ValueError(
                f"Secret name '{v}' contains invalid characters. "
                "Use only letters, numbers, dashes, and underscores."
            )
        return v

    @classmethod
    def from_name(cls, name: str, env_var: Optional[str] = None) -> "Secret":
        """Create secret reference from provider-managed secret.

        Args:
            name: Secret name in provider's secret store (e.g., "wandb-api-key")
            env_var: Environment variable name to use. If None, derives from name
                by converting to uppercase and replacing dashes with underscores.

        Returns:
            Secret configured to load from provider store.

        Example:
            >>> # Provider has secret "huggingface-token"
            >>> secret = Secret.from_name("huggingface-token")
            >>> # Will be available as HF_TOKEN env var
            >>>
            >>> # Custom env var name
            >>> secret = Secret.from_name("api-key", env_var="MY_API_KEY")
        """
        if env_var is None:
            # Default: convert to uppercase, replace dashes
            # "huggingface-token" -> "HUGGINGFACE_TOKEN"
            env_var = name.upper().replace("-", "_")

        return cls(
            name=name,
            env_vars={env_var: "*"},  # "*" means use entire secret value
            source="provider",
        )

    @classmethod
    def from_env(cls, env_var: str, required: bool = True) -> "Secret":
        """Create secret from local environment variable.

        Args:
            env_var: Environment variable name to pass through
            required: Whether to validate the env var exists locally

        Returns:
            Secret configured to pass through local env var.

        Raises:
            ValueError: If required=True and env var not set.

        Example:
            >>> # Pass through local OPENAI_API_KEY
            >>> secret = Secret.from_env("OPENAI_API_KEY")
            >>>
            >>> # Optional env var (won't fail if missing)
            >>> secret = Secret.from_env("OPTIONAL_KEY", required=False)
        """
        if required and env_var not in os.environ:
            raise ValueError(
                f"Environment variable '{env_var}' not set. Either set it or use required=False."
            )

        return cls(
            name=f"env-{env_var.lower()}",
            env_vars={env_var: env_var},  # Pass through as-is
            source="env",
        )

    @classmethod
    def from_dict(cls, env_vars: Dict[str, str], name: Optional[str] = None) -> "Secret":
        """Create secret with multiple environment variables.

        Args:
            env_vars: Dict mapping env var names to secret keys/values
            name: Optional name for the secret group

        Returns:
            Secret with multiple env var mappings.

        Example:
            >>> # Multiple related secrets
            >>> secret = Secret.from_dict({
            ...     "AWS_ACCESS_KEY_ID": "my-access-key",
            ...     "AWS_SECRET_ACCESS_KEY": "my-secret-key",
            ...     "AWS_SESSION_TOKEN": "my-session-token"
            ... }, name="aws-creds")
        """
        if not name:
            name = "custom-secret"

        return cls(name=name, env_vars=env_vars, source="custom")

    def to_env_dict(self) -> Dict[str, str]:
        """Convert to environment variable dict for task config.

        This is used internally by the decorator to inject secrets.
        For provider secrets, values are placeholders that get replaced
        at runtime. For env secrets, values are taken from local env.

        Returns:
            Dict of environment variables to set.
        """
        result = {}

        if self.source == "env":
            # Pass through from local environment
            for env_var, local_var in self.env_vars.items():
                if local_var in os.environ:
                    result[env_var] = os.environ[local_var]
        elif self.source == "provider":
            # Provider will inject these at runtime
            # Use placeholder values for now
            for env_var in self.env_vars:
                result[env_var] = f"__SECRET_{self.name}_{env_var}__"
        else:
            # Custom dict - use as provided
            result.update(self.env_vars)

        return result


class SecretMount(BaseModel):
    """File-based secret mount specification.

    For secrets that need to be mounted as files rather than environment
    variables (e.g., service account JSON files, SSL certificates).

    Note: This is a future enhancement - not yet implemented.
    """

    secret_name: str
    mount_path: str
    file_name: Optional[str] = None
    mode: str = "0600"  # Read-only by owner


def validate_secrets(secrets: List[Secret]) -> None:
    """Validate a list of secrets for conflicts and issues.

    Args:
        secrets: List of secrets to validate

    Raises:
        ValueError: If there are conflicts or invalid configurations
    """
    env_vars = {}

    for secret in secrets:
        for env_var in secret.env_vars:
            if env_var in env_vars:
                raise ValueError(
                    f"Environment variable '{env_var}' is set by multiple secrets: "
                    f"'{env_vars[env_var]}' and '{secret.name}'. "
                    "Each environment variable can only be set by one secret."
                )
            env_vars[env_var] = secret.name
