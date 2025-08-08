"""Mithril provider setup adapter.

Extracts Mithril-specific logic from the wizard to make it provider-agnostic
while maintaining all the beautiful UI and functionality.
"""

import asyncio
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from rich.console import Console

from flow.core.setup_adapters import ProviderSetupAdapter, ConfigField, FieldType, ValidationResult
from flow._internal.io.http import HttpClient
from flow._internal.config_loader import ConfigLoader
from flow.cli.utils.config_validator import ConfigValidator, ValidationStatus
from flow.cli.commands._init_components.config_analyzer import ConfigAnalyzer
from flow._internal.init.writer import ConfigWriter
from flow.api.models import ValidationResult as ApiValidationResult


class MithrilSetupAdapter(ProviderSetupAdapter):
    """Mithril provider setup adapter."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize Mithril setup adapter.

        Args:
            console: Rich console for output (creates one if not provided)
        """
        self.console = console or Console()
        self.validator = ConfigValidator()
        self.api_url = os.environ.get("FLOW_API_URL", "https://api.mithril.ai")
        self.config_path = Path.home() / ".flow" / "config.yaml"
        self.analyzer = ConfigAnalyzer(self.config_path)

    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "mithril"

    def get_configuration_fields(self) -> List[ConfigField]:
        """Get Mithril configuration fields."""
        return [
            ConfigField(
                name="api_key",
                field_type=FieldType.PASSWORD,
                required=True,
                mask_display=True,
                help_url="https://app.mithril.ai/account/apikeys",
                help_text="Get your API key from Mithril",
                default=None,
            ),
            ConfigField(
                name="project",
                field_type=FieldType.CHOICE,
                required=True,
                dynamic_choices=True,
                help_text="Select your Mithril project",
            ),
            ConfigField(
                name="default_ssh_key",
                field_type=FieldType.CHOICE,
                required=False,
                dynamic_choices=True,
                help_url="https://app.mithril.ai/ssh-keys",
                help_text="SSH key for accessing running instances",
            ),
            ConfigField(
                name="region",
                field_type=FieldType.CHOICE,
                required=False,
                choices=[
                    "us-central1-a",
                    "us-central1-c",
                    "us-east1-c",
                    "us-west1-b",
                    "europe-west4-a",
                ],
                default="us-central1-b",
                help_text="Default region for instances",
            ),
        ]

    def validate_field(self, field_name: str, value: str) -> ValidationResult:
        """Validate a single field value."""
        if field_name == "api_key":
            return self._validate_api_key(value)
        elif field_name == "project":
            return self._validate_project(value)
        elif field_name == "default_ssh_key":
            return self._validate_ssh_key(value)
        elif field_name == "region":
            return self._validate_region(value)
        else:
            return ValidationResult(is_valid=False, message=f"Unknown field: {field_name}")

    def get_dynamic_choices(self, field_name: str, context: Dict[str, Any]) -> List[str]:
        """Get dynamic choices for a field."""
        if field_name == "project":
            return self._get_project_choices(context.get("api_key"))
        elif field_name == "default_ssh_key":
            return self._get_ssh_key_choices(context.get("api_key"), context.get("project"))
        else:
            return []

    def detect_existing_config(self) -> Dict[str, Any]:
        """Detect existing configuration from environment, files, etc."""
        sources = ConfigLoader(self.config_path).load_all_sources()
        config = {}

        # API Key
        api_key = sources.api_key
        if api_key and not api_key.startswith("YOUR_"):
            config["api_key"] = api_key

        # Project
        mithril_config = sources.get_mithril_config()
        project = mithril_config.get("project") or sources.config_file.get("project")
        if project and not project.startswith("YOUR_"):
            config["project"] = project

        # SSH Keys
        ssh_keys = mithril_config.get("ssh_keys") or sources.config_file.get("default_ssh_key")
        if ssh_keys:
            config["default_ssh_key"] = (
                ssh_keys if isinstance(ssh_keys, str) else ",".join(ssh_keys)
            )

        # Region
        region = mithril_config.get("region") or sources.config_file.get("region")
        if region:
            config["region"] = region

        return config

    def save_configuration(self, config: Dict[str, Any]) -> bool:
        """Save the final configuration."""
        try:
            # Get existing config and merge
            existing_config = self.analyzer.get_existing_config()
            final_config = existing_config.copy()
            final_config.update(config)

            # Ensure provider is set
            if "provider" not in final_config:
                final_config["provider"] = "mithril"

            # Use ConfigWriter for proper handling
            writer = ConfigWriter(config_path=self.config_path)
            writer.write(final_config, ApiValidationResult(is_valid=True, projects=[]))

            # Save API key to credentials file (Mithril-specific)
            if "api_key" in config:
                self._save_credentials(config["api_key"])

            # Create environment script
            self._create_env_script(final_config)

            return True

        except Exception:
            return False

    def verify_configuration(self, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Verify that the configuration works end-to-end."""
        try:
            # Set environment from config
            if "api_key" in config:
                os.environ["MITHRIL_API_KEY"] = config["api_key"]
            if "project" in config:
                os.environ["MITHRIL_PROJECT"] = config["project"]

            # Test API operation
            from flow import Flow

            client = Flow()
            client.list_tasks(limit=1)

            return True, None

        except Exception as e:
            return False, str(e)

    def get_welcome_message(self) -> Tuple[str, List[str]]:
        """Get Mithril-specific welcome message."""
        return (
            "Welcome to Flow SDK Setup",
            [
                "Get and validate your API key",
                "Select your project",
                "Configure SSH access",
                "Verify everything works",
            ],
        )

    def get_completion_message(self) -> str:
        """Get Mithril-specific completion message."""
        return "🎉 Setup Complete! Your Flow SDK is configured and ready to run GPU workloads."

    # Private helper methods

    def _validate_api_key(self, api_key: str) -> ValidationResult:
        """Validate API key format and with API."""
        # Format validation
        format_result = self.validator.validate_api_key_format(api_key)
        if format_result.status != ValidationStatus.VALID:
            return ValidationResult(is_valid=False, message=format_result.message)

        # API validation
        try:
            result = asyncio.run(self.validator.verify_api_key(api_key))
            if result.status == ValidationStatus.VALID:
                masked_key = (
                    f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 10 else "[CONFIGURED]"
                )
                return ValidationResult(is_valid=True, display_value=masked_key)
            else:
                return ValidationResult(is_valid=False, message=result.message)
        except Exception as e:
            return ValidationResult(is_valid=False, message=f"Validation failed: {e}")

    def _validate_project(self, project: str) -> ValidationResult:
        """Validate project name."""
        result = self.validator.validate_project_name(project)
        if result.status == ValidationStatus.VALID:
            return ValidationResult(is_valid=True, display_value=project)
        else:
            return ValidationResult(is_valid=False, message=result.message)

    def _validate_ssh_key(self, ssh_key: str) -> ValidationResult:
        """Validate SSH key ID."""
        result = self.validator.validate_ssh_key_id(ssh_key)
        if result.status == ValidationStatus.VALID:
            display_value = (
                f"Platform key ({ssh_key[:14]}...)"
                if ssh_key.startswith("sshkey_")
                else "Configured"
            )
            return ValidationResult(is_valid=True, display_value=display_value)
        else:
            return ValidationResult(is_valid=False, message=result.message)

    def _validate_region(self, region: str) -> ValidationResult:
        """Validate region."""
        result = self.validator.validate_region(region)
        if result.status == ValidationStatus.VALID:
            return ValidationResult(is_valid=True, display_value=region)
        else:
            return ValidationResult(is_valid=False, message=result.message)

    def _get_project_choices(self, api_key: Optional[str]) -> List[str]:
        """Get available projects from API."""
        if not api_key:
            return []

        try:
            client = HttpClient(
                base_url=self.api_url,
                headers={"Authorization": f"Bearer {api_key}"},
            )
            projects = client.request("GET", "/v2/projects")
            return [proj["name"] for proj in projects if isinstance(projects, list)]
        except Exception:
            return []

    def _get_ssh_key_choices(self, api_key: Optional[str], project: Optional[str]) -> List[str]:
        """Get available SSH keys from API."""
        if not api_key or not project:
            return []

        try:
            client = HttpClient(
                base_url=self.api_url,
                headers={"Authorization": f"Bearer {api_key}"},
            )

            # Get project ID
            projects = client.request("GET", "/v2/projects")
            project_id = None
            for proj in projects:
                if proj.get("name") == project:
                    project_id = proj.get("fid")
                    break

            if not project_id:
                return []

            # Get SSH keys
            ssh_keys = client.request("GET", "/v2/ssh-keys", params={"project": project_id})
            return [
                f"{key['name']} ({key['fid']})" for key in ssh_keys if isinstance(ssh_keys, list)
            ]
        except Exception:
            return []

    def _save_credentials(self, api_key: str):
        """Save API key to credentials file."""
        import configparser

        credentials_dir = Path.home() / ".flow"
        credentials_dir.mkdir(exist_ok=True)
        credentials_path = credentials_dir / "credentials"

        config = configparser.ConfigParser()
        if credentials_path.exists():
            config.read(credentials_path)

        if "default" not in config:
            config.add_section("default")
        config["default"]["api_key"] = api_key

        with open(credentials_path, "w") as f:
            config.write(f)

        try:
            credentials_path.chmod(0o600)
        except Exception:
            pass  # Windows doesn't support chmod

    def _create_env_script(self, config: Dict[str, Any]):
        """Create shell script with environment variables."""
        env_script = self.config_path.parent / "env.sh"

        with open(env_script, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("# Flow SDK environment variables\n")
            f.write("# Source this file: source ~/.flow/env.sh\n\n")

            if "api_key" in config:
                f.write(f'export MITHRIL_API_KEY="{config["api_key"]}"\n')
            if "project" in config:
                f.write(f'export FLOW_DEFAULT_PROJECT="{config["project"]}"\n')
            if "region" in config:
                f.write(f'export FLOW_DEFAULT_REGION="{config["region"]}"\n')
            if "default_ssh_key" in config:
                f.write(f'export FLOW_SSH_KEYS="{config["default_ssh_key"]}"\n')

        env_script.chmod(0o600)
