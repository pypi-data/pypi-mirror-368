"""Mithril provider initialization and configuration implementation."""

from typing import Dict, List, Optional

from flow.providers.interfaces import ConfigField, IProviderInit
from flow._internal.io.http_interfaces import IHttpClient
from flow.providers.mithril.core.constants import (
    DEFAULT_REGION,
    SUPPORTED_REGIONS,
)


class MithrilInit(IProviderInit):
    """Mithril provider initialization interface implementation.

    Handles configuration gathering and validation for the
    Mithril provider.
    """

    def __init__(self, http_client: IHttpClient):
        """Initialize with HTTP client for API calls.

        Args:
            http_client: Authenticated HTTP client instance
        """
        self.http = http_client

    def get_config_fields(self) -> Dict[str, ConfigField]:
        """Return Mithril configuration field definitions.

        Mithril requires:
        - API key for authentication
        - Project selection
        - Region selection (from available regions)
        - Optional SSH key configuration
        """
        # Get regions from constants to maintain DRY principle
        # In future, could fetch dynamically from /v2/regions endpoint
        region_choices = SUPPORTED_REGIONS

        return {
            "api_key": ConfigField(description="Mithril API key", secret=True),
            "project": ConfigField(description="Project name"),
            "region": ConfigField(
                description="Region", choices=region_choices, default=DEFAULT_REGION
            ),
            "default_ssh_key": ConfigField(description="Default SSH key ID (optional)"),
        }

    def validate_config(self, config: Dict[str, str]) -> List[str]:
        """Validate Mithril configuration.

        Checks:
        - API key format and validity
        - Project name is provided
        - Region is valid (if not using dynamic selection)
        - SSH key format if provided

        Args:
            config: User-provided configuration values

        Returns:
            List of validation error messages
        """
        errors = []

        # Validate API key
        api_key = config.get("api_key", "").strip()
        if not api_key:
            errors.append("API key is required")
        elif not api_key.startswith("mlfoundry_"):
            errors.append("API key should start with 'mlfoundry_'")

        # Validate project
        project = config.get("project", "").strip()
        if not project:
            errors.append("Project is required")

        # Validate region if provided and not in choices
        region = config.get("region", "").strip()
        if region and region not in SUPPORTED_REGIONS:
            errors.append(
                f"Invalid region '{region}'. Valid regions: {', '.join(SUPPORTED_REGIONS[:5])}..."
            )

        # Validate SSH key format if provided
        ssh_key = config.get("default_ssh_key", "").strip()
        if ssh_key and not ssh_key.startswith("sshkey_"):
            errors.append("SSH key ID should start with 'sshkey_'")

        return errors

    def list_projects(self) -> List[Dict[str, str]]:
        """List available projects for the authenticated user.

        Fetches projects dynamically from the API to ensure
        current list based on user permissions.

        Returns:
            List of project dictionaries with id and name

        Raises:
            AuthenticationError: If API key is invalid
            ProviderError: If API request fails
        """
        response = self.http.request("GET", "/v2/projects")
        projects = []

        for project in response:
            # Extract relevant fields, handling potential API response variations
            project_id = project.get("id")
            project_name = project.get("name") or project.get("display_name")

            projects.append(
                {
                    "id": project_id if project_id is not None else "",
                    "name": project_name if project_name is not None else "",
                }
            )

        return projects

    def list_ssh_keys(self, project_id: Optional[str] = None) -> List[Dict[str, str]]:
        """List SSH keys available in the account/project.

        Args:
            project_id: Optional project filter for multi-project setups

        Returns:
            List of SSH key dictionaries with id and name

        Raises:
            AuthenticationError: If API key is invalid
            ProviderError: If API request fails
        """
        params = {}
        if project_id:
            params["project"] = project_id

        response = self.http.request("GET", "/v2/ssh-keys", params=params)
        ssh_keys = []

        for key in response:
            # Handle potential variations in API response structure
            key_id = key.get("id")
            key_name = key.get("name") or key.get("display_name")
            fingerprint = key.get("fingerprint")

            ssh_keys.append(
                {
                    "id": key_id if key_id is not None else "",
                    "name": key_name if key_name is not None else "",
                    # Optional: include fingerprint for user verification
                    "fingerprint": fingerprint if fingerprint is not None else "",
                }
            )

        return ssh_keys
