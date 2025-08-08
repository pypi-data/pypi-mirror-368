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
from ..core.constants import DEFAULT_REGION, VALID_REGIONS
from flow._internal.config_loader import ConfigLoader
from flow._internal.init.writer import ConfigWriter
from flow.api.models import ValidationResult as ApiValidationResult
from flow.cli.utils.shell_completion import CompletionCommand


class MithrilSetupAdapter(ProviderSetupAdapter):
    """Mithril provider setup adapter."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize Mithril setup adapter.

        Args:
            console: Rich console for output (creates one if not provided)
        """
        self.console = console or Console()
        self.api_url = os.environ.get("FLOW_API_URL", "https://api.mithril.ai")
        self.config_path = Path.home() / ".flow" / "config.yaml"
        self._current_context = {}  # Store current wizard context

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
                display_name="API Key",
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
                display_name="Default SSH Key",
            ),
            ConfigField(
                name="region",
                field_type=FieldType.CHOICE,
                required=False,
                choices=VALID_REGIONS,
                default=DEFAULT_REGION,
                help_text="Default region for instances",
                display_name="Default Region",
            ),
        ]

    def validate_field(
        self, field_name: str, value: str, context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Validate a single field value."""
        # Update current context if provided
        if context:
            self._current_context.update(context)

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
        # Store the current context for use in validation
        self._current_context = context

        if field_name == "project":
            return self._get_project_choices(context.get("api_key"))
        elif field_name == "default_ssh_key":
            return self._get_ssh_key_choices(context.get("api_key"), context.get("project"))
        else:
            return []

    def detect_existing_config(self) -> Dict[str, Any]:
        """Detect existing configuration from environment, files, etc."""
        # Use the centralized ConfigLoader for proper precedence and consistency
        loader = ConfigLoader(self.config_path)
        sources = loader.load_all_sources()

        config = {}

        # API Key (env > credentials > config file)
        api_key = sources.api_key
        if api_key and not api_key.startswith("YOUR_"):
            config["api_key"] = api_key

        # Get Mithril-specific configuration
        mithril_config = sources.get_mithril_config()

        # Project
        project = mithril_config.get("project")
        if project and not project.startswith("YOUR_"):
            config["project"] = project

        # Region (always show default)
        region = mithril_config.get("region", DEFAULT_REGION)
        config["region"] = region

        # SSH Keys (handle both list and single key formats)
        ssh_keys = mithril_config.get("ssh_keys")
        if ssh_keys:
            if isinstance(ssh_keys, list):
                # Check for platform auto-generation
                if ssh_keys == ["_auto_"]:
                    config["default_ssh_key"] = "_auto_"
                else:
                    config["default_ssh_key"] = ",".join(ssh_keys)
            else:
                config["default_ssh_key"] = str(ssh_keys)
        else:
            # Default to platform auto-generation for new users
            config["default_ssh_key"] = "_auto_"

        return config

    def save_configuration(self, config: Dict[str, Any]) -> bool:
        """Save the final configuration using centralized ConfigWriter."""
        try:
            # Get existing config and merge
            existing_config = self._load_existing_config()
            final_config = existing_config.copy()
            final_config.update(config)

            # Ensure provider is set
            if "provider" not in final_config:
                final_config["provider"] = "mithril"

            # Use centralized ConfigWriter for consistent, secure saving
            writer = ConfigWriter(self.config_path)
            writer.write(final_config, ApiValidationResult(is_valid=True, projects=[]))

            # Update environment script with provider-specific variables
            self._create_env_script(final_config)

            # Set up shell completion automatically
            try:
                completion_cmd = CompletionCommand()
                shell = completion_cmd._detect_shell()
                if shell:
                    self.console.print(f"\n[dim]Setting up {shell} shell completion...[/dim]")
                    completion_cmd._install_completion(shell, None)
            except Exception:
                # Don't fail the whole setup if completion install fails
                pass

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

            # Check billing status (non-blocking)
            try:
                http_client = HttpClient(
                    base_url=self.api_url,
                    headers={"Authorization": f"Bearer {config.get('api_key')}"},
                )
                billing_status = http_client.request("GET", "/v2/account/billing")
                if not billing_status.get("configured", False):
                    # Store billing status for completion message
                    self._billing_not_configured = True
                    self.console.print(
                        "\n[yellow]Note: Billing not configured yet. Set it up at:[/yellow]"
                    )
                    self.console.print("[cyan]https://app.mithril.ai/settings/billing[/cyan]")
            except:
                # Don't fail setup for billing check
                pass

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
        return "Setup Complete! Your Flow SDK is configured and ready to run GPU workloads."

    # Private helper methods

    def _validate_api_key(self, api_key: str) -> ValidationResult:
        """Validate API key format and with API."""
        # Basic format validation
        if not api_key.startswith("fkey_") or len(api_key) < 20:
            return ValidationResult(
                is_valid=False,
                message="Invalid API key format. Expected: fkey_XXXXXXXXXXXXXXXXXXXXXXXX",
            )

        # API validation
        try:
            client = HttpClient(
                base_url=self.api_url,
                headers={"Authorization": f"Bearer {api_key}"},
            )
            client.request("GET", "/v2/projects")
            masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 10 else "[CONFIGURED]"
            return ValidationResult(is_valid=True, display_value=masked_key)
        except Exception as e:
            return ValidationResult(is_valid=False, message=f"API validation failed: {e}")

    def _validate_project(self, project: str) -> ValidationResult:
        """Validate project name."""
        if not project or len(project.strip()) == 0:
            return ValidationResult(is_valid=False, message="Project name cannot be empty")
        return ValidationResult(is_valid=True, display_value=project)

    def _validate_ssh_key(self, ssh_key: str) -> ValidationResult:
        """Validate SSH key ID or handle generation requests."""
        if not ssh_key or len(ssh_key.strip()) == 0:
            return ValidationResult(is_valid=False, message="SSH key ID cannot be empty")

        # Handle platform auto-generation (recommended)
        if ssh_key == "_auto_":
            self.console.print(
                "\n[green]✓[/green] Platform will auto-generate SSH keys for each instance"
            )
            self.console.print(
                "[dim]This is the recommended secure option - each instance gets unique keys[/dim]\n"
            )
            return ValidationResult(
                is_valid=True,
                display_value="Platform auto-generates (secure)",
                processed_value="_auto_",
            )

        # Handle generation options
        if ssh_key == "GENERATE_SERVER":
            self.console.print("\n[yellow]Generating SSH key on Mithril platform...[/yellow]")
            generated_key_id = self._generate_server_side_key()
            if generated_key_id:
                self.console.print(
                    f"[green]✓[/green] Successfully generated SSH key: {generated_key_id}"
                )
                self.console.print("[dim]Private key saved to ~/.flow/keys/ for SSH access[/dim]\n")
                return ValidationResult(
                    is_valid=True, display_value=generated_key_id, processed_value=generated_key_id
                )
            else:
                return ValidationResult(is_valid=False, message="Failed to generate SSH key")

        elif ssh_key == "GENERATE_LOCAL":
            self.console.print("\n[yellow]Generating SSH key locally...[/yellow]")
            generated_key_id = self._generate_local_key()
            if generated_key_id:
                self.console.print(
                    f"[green]✓[/green] Successfully generated SSH key: {generated_key_id}"
                )
                self.console.print("[dim]Key pair stored in ~/.flow/keys/[/dim]\n")
                return ValidationResult(
                    is_valid=True, display_value=generated_key_id, processed_value=generated_key_id
                )
            else:
                return ValidationResult(
                    is_valid=False, message="Failed to generate SSH key locally"
                )

        # Regular SSH key ID
        if ssh_key.startswith("sshkey_"):
            display_value = f"Platform key ({ssh_key[:14]}...)"
        elif ssh_key == "_auto_":
            display_value = "Platform auto-generates (secure)"
        else:
            display_value = "Configured"
        return ValidationResult(is_valid=True, display_value=display_value)

    def _validate_region(self, region: str) -> ValidationResult:
        """Validate region."""
        valid_regions = VALID_REGIONS
        if region not in valid_regions:
            return ValidationResult(
                is_valid=False, message=f"Invalid region. Choose from: {', '.join(valid_regions)}"
            )
        return ValidationResult(is_valid=True, display_value=region)

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
        """Get available SSH keys from API plus generation options."""
        choices = []

        # Add generation options first - platform auto-generation is recommended
        choices.extend(
            [
                "_auto_|Platform auto-generates per instance (recommended)",
                "GENERATE_SERVER|Generate new SSH key on Mithril platform",
                "GENERATE_LOCAL|Generate new SSH key locally with ssh-keygen",
            ]
        )

        if not api_key or not project:
            return choices

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
                return choices

            # Get existing SSH keys
            ssh_keys = client.request("GET", "/v2/ssh-keys", params={"project": project_id})
            if isinstance(ssh_keys, list):
                for key in ssh_keys:
                    # Format: ID|Name|CreatedAt|Fingerprint for richer display
                    created_at = key.get("created_at", "")
                    # Extract fingerprint from public key if available
                    fingerprint = self._extract_fingerprint(key.get("public_key", ""))
                    choices.append(f"{key['fid']}|{key['name']}|{created_at}|{fingerprint}")

            return choices
        except Exception:
            return choices

    def _generate_server_side_key(self) -> Optional[str]:
        """Generate SSH key server-side."""
        try:
            # Get current config for API access
            config = self.detect_existing_config()
            # Check wizard context first (from get_dynamic_choices), then detected config, then env vars
            api_key = (
                self._current_context.get("api_key")
                or config.get("api_key")
                or os.environ.get("MITHRIL_API_KEY")
            )
            project = (
                self._current_context.get("project")
                or config.get("project")
                or os.environ.get("MITHRIL_PROJECT")
            )

            if not api_key or not project:
                self.console.print("[red]API key and project required for SSH key generation[/red]")
                return None

            # Set up client
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
                self.console.print("[red]Could not resolve project ID[/red]")
                return None

            # Import SSH manager
            from flow.providers.mithril.resources.ssh import SSHKeyManager

            ssh_manager = SSHKeyManager(client, project_id)

            # Generate server-side key
            key_id = ssh_manager.generate_server_key()
            return key_id

        except Exception as e:
            self.console.print(f"[red]Error generating SSH key: {type(e).__name__}: {e}[/red]")
            if hasattr(e, "response"):
                self.console.print(f"[red]API Response: {getattr(e, 'response', 'N/A')}[/red]")
            return None

    def _generate_local_key(self) -> Optional[str]:
        """Generate SSH key locally."""
        try:
            # Get current config for API access
            config = self.detect_existing_config()
            # Check wizard context first (from get_dynamic_choices), then detected config, then env vars
            api_key = (
                self._current_context.get("api_key")
                or config.get("api_key")
                or os.environ.get("MITHRIL_API_KEY")
            )
            project = (
                self._current_context.get("project")
                or config.get("project")
                or os.environ.get("MITHRIL_PROJECT")
            )

            if not api_key or not project:
                self.console.print("[red]API key and project required for SSH key generation[/red]")
                return None

            # Set up client
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
                self.console.print("[red]Could not resolve project ID[/red]")
                return None

            # Import SSH manager
            from flow.providers.mithril.resources.ssh import SSHKeyManager

            ssh_manager = SSHKeyManager(client, project_id)

            # Generate local key
            key_id = ssh_manager.generate_local_key()
            return key_id

        except Exception as e:
            self.console.print(f"[red]Error generating SSH key: {type(e).__name__}: {e}[/red]")
            if hasattr(e, "response"):
                self.console.print(f"[red]API Response: {getattr(e, 'response', 'N/A')}[/red]")
            return None

    def _create_env_script(self, config: Dict[str, Any]):
        """Create shell script with clean provider-specific environment variables.

        Clean, decisive approach: MITHRIL_* variables only.
        No legacy compatibility - users adapt to the right way.
        """
        env_script = self.config_path.parent / "env.sh"

        with open(env_script, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("# Flow SDK Mithril provider environment variables\n")
            f.write("# Source this file: source ~/.flow/env.sh\n\n")

            # Project - provider-specific naming only
            if "project" in config:
                f.write(f'export MITHRIL_DEFAULT_PROJECT="{config["project"]}"\n')

            # Region - provider-specific naming only
            if "region" in config:
                f.write(f'export MITHRIL_DEFAULT_REGION="{config["region"]}"\n')

            # SSH keys - provider-specific naming only
            if "default_ssh_key" in config:
                f.write(f'export MITHRIL_SSH_KEYS="{config["default_ssh_key"]}"\n')

        env_script.chmod(0o600)

    def _extract_fingerprint(self, public_key: str) -> str:
        """Extract fingerprint from SSH public key.

        Args:
            public_key: SSH public key content

        Returns:
            Fingerprint string or empty string if extraction fails
        """
        if not public_key:
            return ""

        try:
            import hashlib
            import base64

            # SSH public keys format: <type> <base64-data> [comment]
            parts = public_key.strip().split()
            if len(parts) >= 2:
                # Decode base64 key data
                key_data = base64.b64decode(parts[1])
                # Calculate SHA256 hash
                sha256 = hashlib.sha256(key_data).digest()
                # Convert to base64 and format
                fingerprint = base64.b64encode(sha256).decode("utf-8").rstrip("=")
                # Return shortened fingerprint for display
                return f"SHA256:{fingerprint[:8]}..."
            return ""
        except Exception:
            return ""

    def _load_existing_config(self) -> Dict[str, Any]:
        """Load existing configuration from file."""
        if not self.config_path.exists():
            return {}

        try:
            import yaml

            with open(self.config_path, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}
