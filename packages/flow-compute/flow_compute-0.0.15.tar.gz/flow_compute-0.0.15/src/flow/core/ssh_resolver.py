"""Smart SSH Key Resolver for Flow SDK.

Platform-grade SSH key resolution that makes SSH "just work" for 90% of users
while enabling power users to do anything they need.

Design Philosophy:
- Convention over configuration
- Deterministic resolution
- No leaky abstractions
- Simple for 90%, powerful for 10%
"""

import os
import logging
from pathlib import Path
from typing import Optional, List, Tuple, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SSHKeyReference:
    """A reference to an SSH key that can be resolved to a file path."""

    value: str
    type: str  # 'absolute_path', 'name', 'platform_id', 'env_var'

    @classmethod
    def from_config_value(cls, value: str) -> "SSHKeyReference":
        """Create SSH key reference from config value with smart type detection."""
        value = value.strip()

        # Absolute path (starts with / or ~)
        if value.startswith("/") or value.startswith("~"):
            return cls(value, "absolute_path")

        # Platform SSH key ID (starts with sshkey_)
        if value.startswith("sshkey_"):
            return cls(value, "platform_id")

        # Environment variable (starts with $)
        if value.startswith("$"):
            return cls(value[1:], "env_var")

        # Otherwise treat as a name to be resolved
        return cls(value, "name")


class SmartSSHKeyResolver:
    """Smart SSH key resolver with deterministic resolution order.

    Resolution Order:
    1. Explicit absolute paths (power users)
    2. Config-specified names with smart resolution (90% case)
    3. Environment variables (CI/automation)
    4. Platform SSH key IDs (platform integration)
    5. Standard locations (fallback)
    """

    def __init__(self, ssh_key_manager=None):
        """Initialize the resolver.

        Args:
            ssh_key_manager: Optional SSH key manager for platform key resolution
        """
        self.ssh_key_manager = ssh_key_manager

    def resolve_ssh_key(self, key_reference: Union[str, SSHKeyReference]) -> Optional[Path]:
        """Resolve SSH key reference to local private key path.

        Args:
            key_reference: SSH key reference (string or SSHKeyReference)

        Returns:
            Path to private key file if found, None otherwise
        """
        if isinstance(key_reference, str):
            key_ref = SSHKeyReference.from_config_value(key_reference)
        else:
            key_ref = key_reference

        logger.debug(f"Resolving SSH key: {key_ref.value} (type: {key_ref.type})")

        # 1. Explicit absolute paths
        if key_ref.type == "absolute_path":
            return self._resolve_absolute_path(key_ref.value)

        # 2. Config-specified names with smart resolution
        if key_ref.type == "name":
            return self._resolve_name(key_ref.value)

        # 3. Environment variables
        if key_ref.type == "env_var":
            return self._resolve_env_var(key_ref.value)

        # 4. Platform SSH key IDs
        if key_ref.type == "platform_id":
            return self._resolve_platform_id(key_ref.value)

        logger.warning(f"Unknown SSH key reference type: {key_ref.type}")
        return None

    def _resolve_absolute_path(self, path: str) -> Optional[Path]:
        """Resolve explicit absolute path."""
        expanded_path = Path(path).expanduser().resolve()

        if expanded_path.exists():
            logger.debug(f"Found SSH key at explicit path: {expanded_path}")
            return expanded_path

        logger.debug(f"SSH key not found at explicit path: {expanded_path}")
        return None

    def _resolve_name(self, name: str) -> Optional[Path]:
        """Resolve SSH key name using smart conventions.

        Strategy:
        1. Try ~/.ssh/{name} (e.g., flow_key → ~/.ssh/flow_key)
        2. Try ~/.ssh/{name}_rsa (legacy naming)
        3. Try ~/.flow/keys/{name} (Flow-managed keys)
        """
        from flow.core.ssh_utils import SSHDirectoryScanner

        # First try standard SSH directory
        ssh_key = SSHDirectoryScanner.find_key_by_name(name)
        if ssh_key:
            logger.debug(f"Resolved SSH key name '{name}' to: {ssh_key}")
            return ssh_key

        # Then try Flow-managed keys directory
        flow_keys_dir = Path.home() / ".flow" / "keys"
        flow_key = SSHDirectoryScanner.find_key_by_name(name, flow_keys_dir)
        if flow_key:
            logger.debug(f"Resolved SSH key name '{name}' to Flow key: {flow_key}")
            return flow_key

        logger.debug(f"Could not resolve SSH key name: {name}")
        return None

    def _resolve_env_var(self, env_var: str) -> Optional[Path]:
        """Resolve SSH key from environment variable."""
        value = os.environ.get(env_var)
        if not value:
            logger.debug(f"Environment variable {env_var} not set")
            return None

        # Environment variable can contain path or content
        if value.startswith("/") or value.startswith("~"):
            # It's a path
            return self._resolve_absolute_path(value)
        else:
            # It's likely key content - not supported for private keys
            logger.warning(f"Environment variable {env_var} contains key content, not path")
            return None

    def _resolve_platform_id(self, platform_id: str) -> Optional[Path]:
        """Resolve platform SSH key ID to local private key."""
        if not self.ssh_key_manager:
            logger.debug("No SSH key manager available for platform key resolution")
            return None

        try:
            return self.ssh_key_manager.find_matching_local_key(platform_id)
        except Exception as e:
            logger.debug(f"Failed to resolve platform SSH key {platform_id}: {e}")
            return None

    def resolve_multiple_keys(
        self, key_references: List[Union[str, SSHKeyReference]]
    ) -> List[Path]:
        """Resolve multiple SSH key references.

        Args:
            key_references: List of SSH key references

        Returns:
            List of resolved private key paths (excludes None values)
        """
        resolved_keys = []

        for key_ref in key_references:
            resolved_path = self.resolve_ssh_key(key_ref)
            if resolved_path:
                resolved_keys.append(resolved_path)

        return resolved_keys

    def get_resolution_status(self, key_reference: Union[str, SSHKeyReference]) -> Tuple[bool, str]:
        """Get detailed resolution status for debugging.

        Args:
            key_reference: SSH key reference to analyze

        Returns:
            Tuple of (is_resolved, status_message)
        """
        if isinstance(key_reference, str):
            key_ref = SSHKeyReference.from_config_value(key_reference)
        else:
            key_ref = key_reference

        resolved_path = self.resolve_ssh_key(key_ref)

        if resolved_path:
            return True, f"Resolved '{key_ref.value}' ({key_ref.type}) → {resolved_path}"
        else:
            return False, f"Failed to resolve '{key_ref.value}' ({key_ref.type})"

    def find_available_keys(self) -> List[Tuple[str, Path]]:
        """Find all available SSH keys in standard locations.

        Returns:
            List of (key_name, key_path) tuples for available keys
        """
        from flow.core.ssh_utils import SSHDirectoryScanner

        available_keys = []

        # Check standard SSH directory
        ssh_pairs = SSHDirectoryScanner.find_key_pairs()
        for private_key, public_key in ssh_pairs:
            available_keys.append((private_key.name, private_key))

        # Check Flow-managed keys
        flow_keys_dir = Path.home() / ".flow" / "keys"
        flow_pairs = SSHDirectoryScanner.find_key_pairs(flow_keys_dir)
        for private_key, public_key in flow_pairs:
            available_keys.append((f"flow:{private_key.name}", private_key))

        return available_keys


# Convenience functions for common usage patterns


def resolve_ssh_key(
    key_reference: Union[str, SSHKeyReference], ssh_key_manager=None
) -> Optional[Path]:
    """Resolve a single SSH key reference.

    Convenience function for one-off key resolution.
    """
    resolver = SmartSSHKeyResolver(ssh_key_manager)
    return resolver.resolve_ssh_key(key_reference)


def resolve_ssh_keys_from_config(ssh_keys_config: List[str], ssh_key_manager=None) -> List[Path]:
    """Resolve SSH keys from configuration list.

    Args:
        ssh_keys_config: List of SSH key references from config
        ssh_key_manager: Optional SSH key manager for platform keys

    Returns:
        List of resolved private key paths
    """
    resolver = SmartSSHKeyResolver(ssh_key_manager)
    return resolver.resolve_multiple_keys(ssh_keys_config)
