"""Provider setup interface for Flow SDK.

This module defines the contract for provider-specific setup and configuration.
Each provider implements this interface to handle its own initialization flow.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class SetupResult:
    """Result of a setup operation."""

    success: bool
    config: Dict[str, Any]
    message: Optional[str] = None


class ProviderSetup(ABC):
    """Abstract base class for provider-specific setup logic.

    Each provider must implement this interface to handle:
    - Interactive configuration wizard
    - Credential validation
    - Project selection
    - Optional component setup (SSH keys, regions, etc.)
    """

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of this provider."""
        pass

    @abstractmethod
    def run_interactive_setup(self) -> SetupResult:
        """Run interactive setup wizard.

        Returns:
            SetupResult with configuration data
        """
        pass

    @abstractmethod
    def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """Validate provider credentials.

        Args:
            credentials: Provider-specific credentials

        Returns:
            True if credentials are valid
        """
        pass

    @abstractmethod
    def get_required_fields(self) -> List[str]:
        """Get list of required configuration fields.

        Returns:
            List of field names that must be configured
        """
        pass

    @abstractmethod
    def get_optional_fields(self) -> List[str]:
        """Get list of optional configuration fields.

        Returns:
            List of field names that can be configured
        """
        pass

    def setup_with_options(
        self,
        api_key: Optional[str] = None,
        project: Optional[str] = None,
        region: Optional[str] = None,
        **kwargs,
    ) -> SetupResult:
        """Configure with provided options (non-interactive).

        Args:
            api_key: API key or equivalent credential
            project: Project identifier
            region: Default region
            **kwargs: Additional provider-specific options

        Returns:
            SetupResult with configuration data
        """
        config = {}

        # Let subclasses handle their specific options
        if api_key:
            config["api_key"] = api_key
        if project:
            config["project"] = project
        if region:
            config["region"] = region

        config.update(kwargs)

        # Validate what we have
        if self.validate_credentials(config):
            return SetupResult(success=True, config=config)
        else:
            return SetupResult(
                success=False, config=config, message="Invalid credentials or configuration"
            )
