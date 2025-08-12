"""Provider initialization and configuration interfaces.

This module defines interfaces specific to provider configuration,
initialization, and setup wizards. These interfaces are separated
from core provider operations as they deal with implementation
details rather than core domain concepts.
"""

from dataclasses import dataclass
from typing import Protocol


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
    choices: list[str] | None = None
    default: str | None = None


class IProviderInit(Protocol):
    """Provider initialization and configuration interface.

    Defines provider-specific initialization capabilities and enables the CLI
    to gather configuration without hard-coding provider logic. This abstraction
    allows new providers to be added without modifying the CLI commands.
    """

    def get_config_fields(self) -> dict[str, ConfigField]:
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

    def validate_config(self, config: dict[str, str]) -> list[str]:
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

    def list_projects(self) -> list[dict[str, str]]:
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

    def list_ssh_keys(self, project_id: str | None = None) -> list[dict[str, str]]:
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

    def list_tasks_by_ssh_key(self, key_id: str, limit: int = 100) -> list[dict[str, str]]:
        """List recent tasks launched with a given SSH key.

        Provider-neutral enrichment for CLI to show task history by SSH key
        without reaching into provider internals.

        Args:
            key_id: Platform SSH key identifier (e.g., sshkey_abc123)
            limit: Maximum number of tasks to return (default: 100)

        Returns:
            List of dictionaries with minimal task details:
            - task_id (str)
            - name (str)
            - status (str)
            - instance_type (str)
            - region (str)
            - created_at (ISO8601 str or datetime)

        Note:
            This method is optional. Callers should check for existence via
            hasattr(provider_init, 'list_tasks_by_ssh_key').
        """
        ...
