"""Mithril provider setup implementation.

Handles Mithril-specific configuration including API keys, projects, SSH keys, and regions.
"""

import os
import configparser
from typing import Dict, Any, Optional, List
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt, Confirm

from flow.core.provider_setup import ProviderSetup, SetupResult
from flow._internal.io.http import HttpClient
from flow.errors import AuthenticationError
from .core.constants import DEFAULT_REGION, VALID_REGIONS


class MithrilProviderSetup(ProviderSetup):
    """Mithril-specific setup implementation."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize Mithril setup.

        Args:
            console: Rich console for output (creates one if not provided)
        """
        self.console = console or Console()
        self.api_url = os.environ.get("FLOW_API_URL", "https://api.mithril.ai")

    def get_provider_name(self) -> str:
        """Get the name of this provider."""
        return "mithril"

    def get_required_fields(self) -> List[str]:
        """Get required configuration fields."""
        return ["api_key", "project"]

    def get_optional_fields(self) -> List[str]:
        """Get optional configuration fields."""
        return ["region", "default_ssh_key", "api_url"]

    def run_interactive_setup(self) -> SetupResult:
        """Run interactive Mithril setup wizard."""
        config = {}

        self.console.print("\n[bold]Mithril Provider Setup[/bold]")
        self.console.print("─" * 50)

        # Step 1: API Key
        api_key = self._setup_api_key()
        if not api_key:
            return SetupResult(success=False, config={}, message="API key setup cancelled")
        config["api_key"] = api_key

        # Step 2: Project
        project = self._setup_project(api_key)
        if not project:
            return SetupResult(success=False, config=config, message="Project setup cancelled")
        config["project"] = project

        # Step 3: SSH Keys (optional)
        ssh_key = self._setup_ssh_keys(api_key, project)
        if ssh_key:
            config["default_ssh_key"] = ssh_key

        # Step 4: Region (optional)
        region = self._setup_region()
        if region:
            config["region"] = region

        # Save API key to credentials file (Mithril-specific)
        self._save_credentials(api_key)

        return SetupResult(success=True, config=config)

    def setup_with_options(
        self,
        api_key: Optional[str] = None,
        project: Optional[str] = None,
        region: Optional[str] = None,
        **kwargs,
    ) -> SetupResult:
        """Configure with provided options (non-interactive).

        Args:
            api_key: Mithril API key
            project: Project name
            region: Default region
            **kwargs: Additional options (e.g., api_url)

        Returns:
            SetupResult with configuration data
        """
        config = {}

        if api_key:
            config["api_key"] = api_key
        if project:
            config["project"] = project
        if region:
            config["region"] = region
        if "api_url" in kwargs:
            config["api_url"] = kwargs["api_url"]

        # Validate credentials
        if config.get("api_key") and self.validate_credentials(config):
            # Save API key to credentials file
            self._save_credentials(config["api_key"])
            return SetupResult(success=True, config=config)
        else:
            return SetupResult(success=False, config=config, message="Invalid or missing API key")

    def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """Validate Mithril credentials."""
        api_key = credentials.get("api_key", "").strip()
        if not api_key:
            return False

        # Validate format
        # Inline validation to avoid circular import
        if not (api_key.startswith("fkey_") and len(api_key) >= 20):
            return False

        # Validate with API
        try:
            client = HttpClient(
                base_url=self.api_url,
                headers={"Authorization": f"Bearer {api_key}"},
            )
            client.request("GET", "/v2/projects")
            return True
        except Exception:
            return False

    def _setup_api_key(self) -> Optional[str]:
        """Configure API key interactively."""
        self.console.print("\n[bold]Step 1: API Key Configuration[/bold]")
        self.console.print("Get your API key from: https://mithril.ai/account/api-keys")

        api_key = Prompt.ask("\nEnter your Mithril API key").strip()

        # Validate format
        if not api_key.startswith("fkey_") or len(api_key) < 20:
            self.console.print("[red]Invalid API key format[/red]")
            self.console.print("[dim]Expected format: fkey_XXXXXXXXXXXXXXXXXXXXXXXX[/dim]")
            if not Confirm.ask("Continue anyway?", default=False):
                return None

        # Verify with API
        if self.validate_credentials({"api_key": api_key}):
            self.console.print("[green]✓[/green] API key validated successfully")
            return api_key
        else:
            self.console.print("[red]Failed to validate API key[/red]")
            if Confirm.ask("Use this key anyway?", default=False):
                return api_key
            return None

    def _setup_project(self, api_key: str) -> Optional[str]:
        """Configure project selection."""
        self.console.print("\n[bold]Step 2: Project Selection[/bold]")

        # Fetch available projects
        try:
            client = HttpClient(
                base_url=self.api_url,
                headers={"Authorization": f"Bearer {api_key}"},
            )
            projects = client.request("GET", "/v2/projects")

            if not projects:
                self.console.print("[yellow]No projects found.[/yellow]")
                return Prompt.ask("Enter project name manually", default="default")

            # Single project
            if len(projects) == 1:
                project_name = projects[0]["name"]
                self.console.print(f"[green]✓[/green] Using project: {project_name}")
                return project_name

            # Multiple projects
            self.console.print("\nAvailable projects:")
            for i, proj in enumerate(projects, 1):
                self.console.print(f"  {i}. {proj['name']}")

            while True:
                choice = Prompt.ask("\nSelect project number", default="1")
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(projects):
                        return projects[idx]["name"]
                    else:
                        self.console.print("[red]Invalid selection[/red]")
                except ValueError:
                    self.console.print("[red]Please enter a number[/red]")

        except Exception as e:
            self.console.print(f"[yellow]Could not fetch projects: {e}[/yellow]")
            return Prompt.ask("Enter project name manually", default="default")

    def _setup_ssh_keys(self, api_key: str, project: str) -> Optional[str]:
        """Configure SSH keys (optional)."""
        self.console.print("\n[bold]Step 3: SSH Key Configuration (Optional)[/bold]")

        if not Confirm.ask("Configure SSH keys now?", default=True):
            return None

        try:
            # Get HTTP client
            client = HttpClient(
                base_url=self.api_url,
                headers={"Authorization": f"Bearer {api_key}"},
            )

            # Resolve project name to ID (Mithril-specific requirement)
            projects = client.request("GET", "/v2/projects")
            project_id = None
            for proj in projects:
                if proj.get("name") == project:
                    project_id = proj.get("fid")
                    break

            if not project_id:
                self.console.print(f"[yellow]Could not resolve project '{project}'[/yellow]")
                return None

            # First, check for local SSH keys
            from flow.core.ssh_resolver import SmartSSHKeyResolver
            from flow.providers.mithril.resources.ssh import SSHKeyManager

            ssh_key_manager = SSHKeyManager(client, project_id)
            resolver = SmartSSHKeyResolver(ssh_key_manager)

            # Find available local keys
            local_keys = resolver.find_available_keys()

            # Fetch existing platform keys
            platform_keys = client.request("GET", "/v2/ssh-keys", params={"project": project_id})

            # Show options
            self.console.print("\n[bold]SSH Key Options:[/bold]")
            options = []

            # Add local keys that aren't uploaded yet
            for key_name, key_path in local_keys:
                # Check if this key is already on platform
                public_key_path = key_path.with_suffix(".pub")
                if public_key_path.exists():
                    public_key_content = public_key_path.read_text().strip()
                    is_uploaded = any(
                        k.get("public_key", "").strip() == public_key_content for k in platform_keys
                    )
                    if not is_uploaded:
                        options.append(("local", key_name, key_path))
                        self.console.print(f"  {len(options)}. Upload local key: {key_name}")

            # Add existing platform keys
            for key in platform_keys:
                options.append(("platform", key["name"], key["fid"]))
                self.console.print(f"  {len(options)}. Use existing: {key['name']} ({key['fid']})")

            if not options:
                self.console.print(
                    "[yellow]No SSH keys found. Auto-generating a new SSH key...[/yellow]"
                )

                # Auto-generate SSH key using server-side generation
                try:
                    generated_key_id = ssh_key_manager.generate_server_key()

                    if generated_key_id:
                        self.console.print(
                            f"[green]✓[/green] Auto-generated SSH key: {generated_key_id}"
                        )
                        self.console.print("[dim]Key generated on Mithril platform[/dim]")
                        return generated_key_id
                    else:
                        self.console.print("[red]Failed to auto-generate SSH key[/red]")
                        self.console.print("\nTo create an SSH key manually:")
                        self.console.print("  ssh-keygen -t ed25519 -f ~/.ssh/flow_key")
                        return None

                except Exception as e:
                    self.console.print(f"[red]Error generating SSH key: {e}[/red]")
                    self.console.print("\nTo create an SSH key manually:")
                    self.console.print("  ssh-keygen -t ed25519 -f ~/.ssh/flow_key")
                    return None

            # Add generation options with clear descriptions
            self.console.print(
                f"  {len(options) + 1}. Generate new SSH key (server-side, recommended)"
            )
            self.console.print(
                f"  {len(options) + 2}. Generate new SSH key (local, requires ssh-keygen)"
            )

            # Add skip option
            self.console.print(f"  {len(options) + 3}. Skip SSH key configuration")

            choice = Prompt.ask("\nSelect option", default="1")

            try:
                idx = int(choice) - 1
                if idx == len(options):  # Server-side generation
                    self.console.print("[yellow]Generating SSH key on Mithril platform...[/yellow]")
                    try:
                        generated_key_id = ssh_key_manager.generate_server_key()
                        if generated_key_id:
                            self.console.print(
                                f"[green]✓[/green] Generated SSH key: {generated_key_id}"
                            )
                            self.console.print(
                                "[dim]Private key saved locally for SSH access[/dim]"
                            )
                            return generated_key_id
                        else:
                            self.console.print("[red]Failed to generate SSH key[/red]")
                            return None
                    except Exception as e:
                        self.console.print(f"[red]Error generating SSH key: {e}[/red]")
                        return None
                elif idx == len(options) + 1:  # Local generation
                    self.console.print("[yellow]Generating SSH key locally...[/yellow]")
                    try:
                        generated_key_id = ssh_key_manager._generate_ssh_key()
                        if generated_key_id:
                            self.console.print(
                                f"[green]✓[/green] Generated SSH key: {generated_key_id}"
                            )
                            self.console.print("[dim]Key pair stored in ~/.flow/keys/[/dim]")
                            return generated_key_id
                        else:
                            self.console.print("[red]Failed to generate SSH key locally[/red]")
                            self.console.print(
                                "[yellow]Try server-side generation instead (option 1)[/yellow]"
                            )
                            return None
                    except Exception as e:
                        self.console.print(f"[red]Error generating SSH key: {e}[/red]")
                        return None
                elif idx == len(options) + 2:  # Skip option
                    return None

                if 0 <= idx < len(options):
                    option_type, name, value = options[idx]

                    if option_type == "local":
                        # Upload the local key
                        public_key_path = value.with_suffix(".pub")
                        public_key_content = public_key_path.read_text().strip()

                        self.console.print(f"Uploading SSH key '{name}'...")
                        response = client.request(
                            "POST",
                            "/v2/ssh-keys",
                            json={
                                "name": name,
                                "project": project_id,
                                "public_key": public_key_content,
                            },
                        )
                        key_id = response["fid"]
                        self.console.print(f"[green]✓[/green] Uploaded: {name} ({key_id})")
                        return name  # Return the key name for config
                    else:
                        # Use existing platform key
                        self.console.print(f"[green]✓[/green] Selected: {name}")
                        return value  # Return the platform key ID

            except ValueError:
                pass

        except Exception as e:
            self.console.print(f"[yellow]SSH key configuration failed: {e}[/yellow]")

        return None

    def _setup_region(self) -> Optional[str]:
        """Configure default region (optional)."""
        self.console.print("\n[bold]Step 4: Default Region (Optional)[/bold]")

        regions = VALID_REGIONS

        self.console.print("\nAvailable regions:")
        for i, region in enumerate(regions, 1):
            self.console.print(f"  {i}. {region}")

        choice = Prompt.ask("\nSelect region (or Enter to skip)", default="")
        if not choice:
            return None

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(regions):
                return regions[idx]
        except ValueError:
            # Maybe they typed the region name directly
            if choice in regions:
                return choice

        return None

    def _save_credentials(self, api_key: str):
        """Save API key to credentials file.

        Args:
            api_key: The API key to save
        """
        credentials_dir = Path.home() / ".flow"
        credentials_dir.mkdir(exist_ok=True)
        credentials_path = credentials_dir / "credentials"

        # Read existing credentials
        config = configparser.ConfigParser()
        if credentials_path.exists():
            config.read(credentials_path)

        # Update with new API key
        if "default" not in config:
            config.add_section("default")
        config["default"]["api_key"] = api_key

        # Write back
        with open(credentials_path, "w") as f:
            config.write(f)

        # Set appropriate permissions (Unix-like systems)
        try:
            credentials_path.chmod(0o600)
        except Exception:
            pass  # Windows doesn't support chmod
