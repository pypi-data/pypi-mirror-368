"""Self-update command for Flow CLI.

This command allows users to update the Flow SDK to the latest version
or check for available updates without installing them.
"""

import json
import re
import subprocess
import sys
from importlib.metadata import version as get_version
from pathlib import Path
from typing import Optional, Tuple

import click
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markup import escape

from .base import BaseCommand

from ..utils.theme_manager import theme_manager

console = theme_manager.create_console()


class UpdateChecker:
    """Check for and install Flow SDK updates."""

    PYPI_API_URL = "https://pypi.org/pypi/flow-compute/json"
    PACKAGE_NAME = "flow-compute"

    def __init__(self):
        self.current_version = self._get_current_version()
        self.latest_version = None
        self.available_versions = []

    def _get_current_version(self) -> str:
        """Get the currently installed version."""
        try:
            return get_version(self.PACKAGE_NAME)
        except Exception:
            # Fallback to reading from pyproject.toml if in development
            try:
                pyproject_path = (
                    Path(__file__).parent.parent.parent.parent.parent / "pyproject.toml"
                )
                if pyproject_path.exists():
                    with open(pyproject_path) as f:
                        for line in f:
                            if line.startswith("version"):
                                return line.split("=")[1].strip().strip('"')
            except Exception:
                pass
            return "0.0.0"

    def check_for_updates(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """Check if updates are available.

        Returns:
            Tuple of (update_available, latest_version, release_notes_url)
        """
        try:
            response = requests.get(self.PYPI_API_URL, timeout=5)
            response.raise_for_status()
            data = response.json()

            # Get all non-yanked versions for compatibility checking
            non_yanked_versions = []
            for ver, releases in data["releases"].items():
                # Check if any release for this version is not yanked
                # (all releases for a version should have same yanked status)
                if releases and not releases[0].get("yanked", False):
                    non_yanked_versions.append(ver)

            self.available_versions = sorted(
                non_yanked_versions, key=lambda v: _parse_version(v), reverse=True
            )

            # PyPI's info.version might be yanked, so use the latest non-yanked version
            pypi_latest = data["info"]["version"]

            # Check if PyPI's reported latest is yanked
            if pypi_latest in data["releases"]:
                releases = data["releases"][pypi_latest]
                if releases and releases[0].get("yanked", False):
                    # Use the highest non-yanked version instead
                    self.latest_version = (
                        self.available_versions[0] if self.available_versions else pypi_latest
                    )
                else:
                    self.latest_version = pypi_latest
            else:
                # Fallback to highest non-yanked version
                self.latest_version = (
                    self.available_versions[0] if self.available_versions else pypi_latest
                )

            # Compare versions
            current = _parse_version(self.current_version)
            latest = _parse_version(self.latest_version)

            # Get release URL
            release_url = f"https://pypi.org/project/{self.PACKAGE_NAME}/{self.latest_version}/"

            return latest > current, self.latest_version, release_url

        except requests.exceptions.RequestException as e:
            console.print(f"[red]Error checking for updates: {escape(str(e))}[/red]")
            return False, None, None
        except Exception as e:
            console.print(f"[red]Unexpected error: {escape(str(e))}[/red]")
            return False, None, None

    def get_version_info(self, version_str: str) -> dict:
        """Get detailed info about a specific version."""
        try:
            response = requests.get(self.PYPI_API_URL, timeout=5)
            response.raise_for_status()
            data = response.json()

            if version_str in data["releases"]:
                release = data["releases"][version_str]
                if release:
                    # Get the first distribution's info
                    dist = release[0]
                    return {
                        "version": version_str,
                        "upload_time": dist.get("upload_time", "Unknown"),
                        "size": dist.get("size", 0),
                        "python_version": dist.get("requires_python", "Unknown"),
                    }
            return {}
        except Exception:
            return {}

    def detect_environment(self) -> dict:
        """Detect the current Python environment."""
        env_info = {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "executable": sys.executable,
            "is_virtual": False,
            "venv_path": None,
            "installer": None,
            "can_update": True,
            "update_command": None,
        }

        # Check if in virtual environment
        env_info["is_virtual"] = hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        )

        if env_info["is_virtual"]:
            env_info["venv_path"] = sys.prefix

        # Detect installer (pip, uv, pipx, etc.)
        # Check if installed as a uv tool
        if "uv/tools" in sys.executable:
            env_info["installer"] = "uv-tool"
            env_info["update_command"] = f"uv tool install --upgrade {self.PACKAGE_NAME}"
        elif "uv" in sys.executable or Path(sys.executable).parent.name == "uv":
            env_info["installer"] = "uv"
            env_info["update_command"] = f"uv pip install --upgrade {self.PACKAGE_NAME}"
        elif "pipx" in str(Path(sys.executable).parent):
            env_info["installer"] = "pipx"
            env_info["update_command"] = f"pipx upgrade {self.PACKAGE_NAME}"
        else:
            env_info["installer"] = "pip"
            env_info["update_command"] = (
                f"{sys.executable} -m pip install --upgrade {self.PACKAGE_NAME}"
            )

        # Check write permissions
        try:
            import site

            site_packages = site.getsitepackages()[0] if site.getsitepackages() else None
            if site_packages:
                test_file = Path(site_packages) / ".flow_update_test"
                try:
                    test_file.touch()
                    test_file.unlink()
                except (PermissionError, OSError):
                    env_info["can_update"] = False
                    if not env_info["is_virtual"]:
                        env_info["update_command"] = f"sudo {env_info['update_command']}"
        except Exception:
            pass

        return env_info

    def perform_update(self, target_version: Optional[str] = None, force: bool = False) -> bool:
        """Perform the actual update.

        Args:
            target_version: Specific version to install, or None for latest
            force: Force update even if already on latest version

        Returns:
            True if update succeeded
        """
        env_info = self.detect_environment()

        if not env_info["can_update"] and not force:
            console.print("[red]Insufficient permissions to update.[/red]")
            console.print(f"[yellow]Try running: {env_info['update_command']}[/yellow]")
            return False

        # Build update command
        if target_version:
            package_spec = f"{self.PACKAGE_NAME}=={target_version}"
        else:
            package_spec = self.PACKAGE_NAME

        if env_info["installer"] == "uv-tool":
            cmd = ["uv", "tool", "install", "--upgrade", package_spec]
            if force:
                cmd.append("--force")
        elif env_info["installer"] == "uv":
            cmd = ["uv", "pip", "install", "--upgrade", package_spec]
            if force:
                cmd.append("--force-reinstall")
        elif env_info["installer"] == "pipx":
            if target_version:
                cmd = ["pipx", "install", "--force", package_spec]
            else:
                cmd = ["pipx", "upgrade", self.PACKAGE_NAME]
        else:
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade", package_spec]
            if force:
                cmd.append("--force-reinstall")

        console.print(f"[cyan]Running: {' '.join(cmd)}[/cyan]")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode == 0:
                success_color = theme_manager.get_color("success")
                console.print(f"[{success_color}]✓ Update completed successfully![/{success_color}]")
                return True
            else:
                console.print(f"[red]Update failed with exit code {escape(str(result.returncode))}[/red]")
                if result.stderr:
                    console.print(f"[red]Error: {escape(result.stderr)}[/red]")
                return False

        except subprocess.SubprocessError as e:
            console.print(f"[red]Failed to run update command: {escape(str(e))}[/red]")
            return False
        except Exception as e:
            console.print(f"[red]Unexpected error during update: {escape(str(e))}[/red]")
            return False

    def create_backup(self) -> Optional[str]:
        """Create a backup of current version info for rollback.

        Returns:
            Backup identifier or None if backup failed
        """
        backup_info = {
            "version": self.current_version,
            "timestamp": str(Path.cwd()),
            "environment": self.detect_environment(),
        }

        backup_dir = Path.home() / ".flow" / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        backup_file = backup_dir / f"backup_{self.current_version}.json"

        try:
            with open(backup_file, "w") as f:
                json.dump(backup_info, f, indent=2)
            return str(backup_file)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not create backup: {e}[/yellow]")
            return None

    def rollback(self, backup_file: str) -> bool:
        """Rollback to a previous version using backup info.

        Args:
            backup_file: Path to backup file

        Returns:
            True if rollback succeeded
        """
        try:
            with open(backup_file) as f:
                backup_info = json.load(f)

            target_version = backup_info["version"]
            console.print(f"[cyan]Rolling back to version {target_version}...[/cyan]")

            return self.perform_update(target_version=target_version, force=True)

        except Exception as e:
            console.print(f"[red]Rollback failed: {escape(str(e))}[/red]")
            return False


class UpdateCommand(BaseCommand):
    """Update command implementation."""

    @property
    def name(self) -> str:
        return "update"

    @property
    def help(self) -> str:
        return "Update Flow SDK to the latest version"

    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        @click.option("--check", is_flag=True, help="Check for updates without installing")
        @click.option("--force", is_flag=True, help="Force update even if on latest version")
        @click.option("--version", help="Install specific version")
        @click.option("--rollback", help="Rollback to previous version using backup file")
        @click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompt")
        @click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
        def update(
            check: bool,
            force: bool,
            version: Optional[str],
            rollback: Optional[str],
            yes: bool,
            output_json: bool,
        ):
            """Update Flow SDK to the latest version.

            \b
            Examples:
                flow update              # Update to latest version
                flow update --check      # Check for updates only
                flow update --version 0.0.5  # Install specific version
                flow update --force      # Force reinstall
            """
            checker = UpdateChecker()

            # Handle rollback
            if rollback:
                if output_json:
                    success = checker.rollback(rollback)
                    print(json.dumps({"success": success}))
                else:
                    success = checker.rollback(rollback)
                    if not success:
                        raise click.exceptions.Exit(1)
                return

            # Check for updates
            update_available, latest_version, release_url = checker.check_for_updates()

            if check:
                # Just check, don't update
                if output_json:
                    result = {
                        "current_version": checker.current_version,
                        "latest_version": latest_version,
                        "update_available": update_available,
                        "release_url": release_url,
                    }
                    print(json.dumps(result, indent=2))
                else:
                    self._display_version_info(checker, update_available, latest_version)
                return

            # Perform update
            if version:
                # Install specific version
                target = version
                console.print(f"[cyan]Installing Flow SDK version {target}...[/cyan]")
            elif not update_available and not force:
                if output_json:
                    print(
                        json.dumps(
                            {
                                "current_version": checker.current_version,
                                "latest_version": latest_version,
                                "message": "Already on latest version",
                            }
                        )
                    )
                else:
                    success_color = theme_manager.get_color("success")
                    console.print(
                        f"[{success_color}]✓ You're already on the latest version ({checker.current_version})[/{success_color}]"
                    )
                return
            else:
                target = latest_version

            # Show update info and confirm
            if not yes and not output_json:
                env_info = checker.detect_environment()

                # Display update details
                table = Table(title="Update Details", show_header=False)
                table.add_column("Property", style="cyan")
                table.add_column("Value")

                table.add_row("Current Version", checker.current_version)
                table.add_row("Target Version", target or "latest")
                table.add_row("Python Version", env_info["python_version"])
                table.add_row("Environment", "Virtual" if env_info["is_virtual"] else "System")
                table.add_row("Installer", env_info["installer"] or "pip")

                console.print(table)

                if not click.confirm("\nProceed with update?"):
                    console.print("[yellow]Update cancelled[/yellow]")
                    return

            # Create backup
            backup_file = checker.create_backup()
            if backup_file and not output_json:
                console.print(f"[dim]Backup saved to: {backup_file}[/dim]")

            # Perform update
            success = checker.perform_update(target_version=version, force=force)

            if output_json:
                result = {
                    "success": success,
                    "previous_version": checker.current_version,
                    "target_version": target or latest_version,
                    "backup_file": backup_file,
                }
                print(json.dumps(result, indent=2))
            elif success:
                success_color = theme_manager.get_color("success")
                console.print(f"\n[{success_color}]✓ Update completed successfully![/{success_color}]")
                console.print(
                    f"[cyan]Restart your terminal or run 'flow --version' to verify[/cyan]"
                )
                if backup_file:
                    console.print(f"[dim]To rollback: flow update --rollback {backup_file}[/dim]")
            else:
                console.print("\n[red]✗ Update failed[/red]")
                console.print("[yellow]Try running the update command manually:[/yellow]")
                env_info = checker.detect_environment()
                console.print(f"[cyan]{env_info['update_command']}[/cyan]")
                raise click.exceptions.Exit(1)

        return update

    def _display_version_info(
        self, checker: UpdateChecker, update_available: bool, latest_version: Optional[str]
    ) -> None:
        """Display version information in a nice format."""

        # Create version info panel
        if update_available:
            status = "[yellow]🔄 Update Available[/yellow]"
            message = f"A new version of Flow SDK is available: {latest_version}"
            action = "Run 'flow update' to upgrade"
        else:
            status = "[green]✓ Up to Date[/green]"
            message = f"You're running the latest version: {checker.current_version}"
            action = "No action needed"

        panel_content = f"""{status}

Current: {checker.current_version}
Latest:  {latest_version or "Unknown"}

{message}

{action}"""

        console.print(Panel(panel_content, title="Flow SDK Version Check"))

        # Show recent versions if available
        if checker.available_versions:
            recent = checker.available_versions[:5]
            console.print("\n[bold]Recent Versions:[/bold]")
            for v in recent:
                if v == checker.current_version:
                    console.print(f"  • {v} [green](current)[/green]")
                elif v == latest_version:
                    console.print(f"  • {v} [yellow](latest)[/yellow]")
                else:
                    console.print(f"  • {v}")


# Export command instance
command = UpdateCommand()


def _parse_version(version_str: Optional[str]):
    """Parse version string into a tuple for safe comparison without packaging.

    Handles semantic versions like '1.2.3', optionally with pre-release/build
    metadata. Non-numeric parts are handled so that stable releases sort after
    pre-releases (e.g., 1.0.0 > 1.0.0rc1).
    """
    if not version_str:
        return (0, 0, 0, 1, ())

    # Extract core numeric parts and pre-release tag
    match = re.match(r"^(\d+)\.(\d+)(?:\.(\d+))?(.*)$", version_str)
    if not match:
        # Fallback: try to parse any digits we see
        digits = [int(x) for x in re.findall(r"\d+", version_str)[:3]]
        while len(digits) < 3:
            digits.append(0)
        # Treat unknown suffix as pre-release to keep it below stable
        return (digits[0], digits[1], digits[2], 0, (version_str,))

    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3) or 0)
    suffix = match.group(4) or ""

    # Stable releases sort after pre-releases: use flag 1 for stable, 0 for pre
    is_stable = 1 if suffix in ("", ".post", "+") else 0

    # Normalize well-known pre-release tags so they sort correctly
    # rc > beta > alpha
    if "rc" in suffix:
        pre_rank = 2
    elif "b" in suffix or "beta" in suffix:
        pre_rank = 1
    elif "a" in suffix or "alpha" in suffix:
        pre_rank = 0
    else:
        pre_rank = -1  # unknown; keep lowest

    # Extract any trailing number in the suffix, e.g., rc1 -> 1
    pre_num_match = re.search(r"(\d+)", suffix)
    pre_num = int(pre_num_match.group(1)) if pre_num_match else 0

    return (major, minor, patch, is_stable, (pre_rank, pre_num))
