"""Shared SSH utilities for Flow SDK.

Common SSH functionality used across setup, resolution, and operations.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class SSHDirectoryScanner:
    """Utility for scanning SSH directories and finding key files."""

    @staticmethod
    def find_public_keys(ssh_dir: Path | None = None) -> list[Path]:
        """Find SSH public keys in a directory.

        Args:
            ssh_dir: Directory to scan (defaults to ~/.ssh)

        Returns:
            List of Path objects for *.pub files
        """
        if ssh_dir is None:
            ssh_dir = Path.home() / ".ssh"

        if not ssh_dir.exists():
            return []

        return list(ssh_dir.glob("*.pub"))

    @staticmethod
    def find_private_keys(ssh_dir: Path | None = None) -> list[Path]:
        """Find SSH private keys in a directory.

        Args:
            ssh_dir: Directory to scan (defaults to ~/.ssh)

        Returns:
            List of Path objects for private key files (non-.pub files)
        """
        if ssh_dir is None:
            ssh_dir = Path.home() / ".ssh"

        if not ssh_dir.exists():
            return []

        # Find files that are not .pub and have corresponding .pub files
        private_keys = []
        for key_file in ssh_dir.iterdir():
            if (
                key_file.is_file()
                and not key_file.name.endswith(".pub")
                and not key_file.name.startswith(".")
                and key_file.name not in ["config", "known_hosts", "authorized_keys"]
            ):
                # Check if corresponding public key exists
                pub_key = key_file.with_suffix(".pub")
                if pub_key.exists():
                    private_keys.append(key_file)

        return private_keys

    @staticmethod
    def find_key_pairs(ssh_dir: Path | None = None) -> list[tuple[Path, Path]]:
        """Find SSH key pairs (private, public) in a directory.

        Args:
            ssh_dir: Directory to scan (defaults to ~/.ssh)

        Returns:
            List of (private_key_path, public_key_path) tuples
        """
        if ssh_dir is None:
            ssh_dir = Path.home() / ".ssh"

        if not ssh_dir.exists():
            return []

        key_pairs = []
        for private_key in SSHDirectoryScanner.find_private_keys(ssh_dir):
            public_key = private_key.with_suffix(".pub")
            if public_key.exists():
                key_pairs.append((private_key, public_key))

        return key_pairs

    @staticmethod
    def find_key_by_name(key_name: str, ssh_dir: Path | None = None) -> Path | None:
        """Find a specific SSH key by name.

        Args:
            key_name: Name of the key file (without extension)
            ssh_dir: Directory to search (defaults to ~/.ssh)

        Returns:
            Path to private key if found, None otherwise
        """
        if ssh_dir is None:
            ssh_dir = Path.home() / ".ssh"

        if not ssh_dir.exists():
            return None

        # Try exact name first
        private_key = ssh_dir / key_name
        if private_key.exists():
            public_key = private_key.with_suffix(".pub")
            if public_key.exists():
                return private_key

        # Try with common suffixes
        for suffix in ["_rsa", "_ed25519", "_ecdsa"]:
            private_key = ssh_dir / f"{key_name}{suffix}"
            if private_key.exists():
                public_key = private_key.with_suffix(".pub")
                if public_key.exists():
                    return private_key

        return None


def get_standard_ssh_locations() -> list[Path]:
    """Get list of standard SSH key locations to check.

    Returns:
        List of Path objects for standard SSH key locations
    """
    ssh_dir = Path.home() / ".ssh"
    return [
        ssh_dir / "id_rsa",
        ssh_dir / "id_ed25519",
        ssh_dir / "id_ecdsa",
        ssh_dir / "flow_key",  # Flow-specific default
    ]
