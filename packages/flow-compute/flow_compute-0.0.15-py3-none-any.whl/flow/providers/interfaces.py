"""Provider initialization and configuration interfaces.

This module defines interfaces specific to provider configuration,
initialization, and setup wizards. These interfaces are separated
from core provider operations as they deal with implementation
details rather than core domain concepts.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Protocol


@dataclass
class ConfigField:
    """Minimal field definition for provider configuration.

    Attributes:
        description: Human-readable field description shown in prompts
        secret: Whether field should be masked (passwords, API keys)
        choices: List of valid options for select fields
        default: Default value if user doesn't provide one
    """

    description: str
    secret: bool = False
    choices: Optional[List[str]] = None
    default: Optional[str] = None


class IProviderInit(Protocol):
    """Provider initialization and configuration interface.

    Defines provider-specific initialization capabilities and enables the CLI
    to gather configuration without hard-coding provider logic. This abstraction
    allows new providers to be added without modifying the CLI commands.
    """

    def get_config_fields(self) -> Dict[str, ConfigField]:
        """Return configuration field definitions for this provider.

        Describes all fields needed to configure the provider, including their
        types, validation rules, and UI hints. Used by configuration wizards
        to build dynamic forms.

        Returns:
            Dict mapping field names to their definitions. Field names should be
            valid Python identifiers. Order is preserved for display purposes.

        Example:
            >>> provider.get_config_fields()
            {
                'api_key': ConfigField(
                    description="API key for authentication",
                    secret=True
                ),
                'project': ConfigField(
                    description="Default project name"
                ),
                'region': ConfigField(
                    description="Deployment region",
                    choices=['us-east-1', 'us-west-2'],
                    default='us-east-1'
                )
            }
        """
        ...

    def validate_config(self, config: Dict[str, str]) -> List[str]:
        """Validate complete configuration set.

        Checks that all required fields are present and valid. Can perform
        cross-field validation and API connectivity checks. Should complete
        within 5 seconds.

        Args:
            config: Field name to value mapping from user input.

        Returns:
            List of error messages. Empty list means valid config. Each error
            should be a complete sentence.

        Example:
            >>> errors = provider.validate_config({
            ...     'api_key': 'invalid',
            ...     'project': ''
            ... })
            >>> errors
            ["API key format is invalid", "Project name is required"]
        """
        ...

    def list_projects(self) -> List[Dict[str, str]]:
        """List available projects for authenticated user.

        Returns projects the current credentials have access to. Used during
        configuration to help users select correct project. May return empty
        list if projects not applicable.

        Returns:
            List of project dictionaries with 'id' and 'name' keys. Additional
            metadata keys allowed but not required.

        Raises:
            AuthenticationError: If credentials are invalid.
            ProviderError: If API request fails.
        """
        ...

    def list_ssh_keys(self, project_id: Optional[str] = None) -> List[Dict[str, str]]:
        """List SSH keys available for use.

        Returns SSH keys that can be added to instances. Used during
        configuration to set default keys. Optionally filtered by project
        for multi-project providers.

        Args:
            project_id: Optional project filter.

        Returns:
            List of SSH key dictionaries with 'id' and 'name' keys. May include
            'fingerprint' or other metadata.

        Raises:
            AuthenticationError: If credentials are invalid.
            ProviderError: If API request fails.
        """
        ...
