"""SSH key management component for Mithril provider.

This module provides clean separation of concerns for SSH key operations,
including automatic key provisioning and error handling.
"""

import json
import logging
import os
import platform
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

from flow._internal.io.http_interfaces import IHttpClient
from flow.errors import FlowError

from ..api.types import SSHKeyModel as SSHKey

logger = logging.getLogger(__name__)


class SSHKeyError(FlowError):
    """Base error for SSH key operations."""

    pass


class SSHKeyNotFoundError(SSHKeyError):
    """Raised when SSH keys cannot be found or created."""

    pass


class SSHKeyManager:
    """Manages SSH keys with automatic provisioning and caching."""

    def __init__(self, http_client: IHttpClient, project_id: Optional[str] = None):
        """Initialize SSH key manager.

        Args:
            http_client: HTTP client for API requests
            project_id: Optional project ID for scoped operations
        """
        self.http = http_client
        self.project_id = project_id
        self._keys_cache: Optional[List[SSHKey]] = None
        self._key_dir = Path.home() / ".flow" / "keys"

    def ensure_keys(self, requested_keys: Optional[List[str]] = None) -> List[str]:
        """Ensure SSH keys are available for use.

        This method follows a fallback strategy:
        1. Use explicitly provided key IDs if given
        2. Use existing keys from the project
        3. Optionally create a default key if none exist

        Args:
            requested_keys: Optional list of specific SSH key IDs to use

        Returns:
            List of SSH key IDs ready for use

        Raises:
            SSHKeyNotFoundError: If no keys can be obtained
        """
        # Use explicitly provided keys if given
        if requested_keys:
            logger.debug(f"Using {len(requested_keys)} explicitly provided SSH keys")
            return requested_keys

        # Get existing keys
        existing_keys = self.list_keys()
        if existing_keys:
            key_ids = [key.fid for key in existing_keys]
            logger.info(f"Using {len(key_ids)} existing SSH keys from project")
            return key_ids

        # No keys available
        logger.warning("No SSH keys available for the project")

        # Optionally try to create a default key from environment
        if default_key := self._try_create_default_key():
            return [default_key]

        # Return empty list - let the caller decide if this is an error
        return []

    def list_keys(self) -> List[SSHKey]:
        """List all SSH keys for the project.

        Returns:
            List of SSHKey objects
        """
        if self._keys_cache is not None:
            return self._keys_cache

        try:
            params = {}
            if self.project_id:
                params["project"] = self.project_id  # API expects 'project', not 'project_id'

            response = self.http.request(
                method="GET",
                url="/v2/ssh-keys",
                params=params,
            )

            # API returns list directly
            keys_data = response if isinstance(response, list) else []

            self._keys_cache = [
                SSHKey(
                    fid=k["fid"],
                    name=k["name"],
                    public_key=k.get("public_key", ""),
                    created_at=k.get("created_at"),
                )
                for k in keys_data
                if "fid" in k and "name" in k
            ]

            logger.debug(f"Loaded {len(self._keys_cache)} SSH keys from API")
            return self._keys_cache

        except Exception as e:
            logger.error(f"Failed to fetch SSH keys: {e}")
            return []

    def create_key(self, name: str, public_key: str = None) -> str:
        """Create a new SSH key.

        Args:
            name: Key name
            public_key: SSH public key content (optional - if not provided, Mithril generates one)

        Returns:
            ID of the created key

        Raises:
            SSHKeyError: If key creation fails
        """
        payload = {
            "name": name,
        }

        # Only include public_key if provided
        if public_key:
            payload["public_key"] = public_key.strip()

        if self.project_id:
            payload["project"] = self.project_id

        try:
            response = self.http.request(
                method="POST",
                url="/v2/ssh-keys",
                json=payload,
            )

            key_id = response.get("fid")
            if not key_id:
                raise SSHKeyError(f"No key ID returned in response: {response}")

            # Invalidate cache
            self._keys_cache = None

            logger.info(f"Created SSH key '{name}' with ID: {key_id}")
            return key_id

        except Exception as e:
            raise SSHKeyError(f"Failed to create SSH key '{name}': {e}") from e

    def delete_key(self, key_id: str) -> bool:
        """Delete an SSH key.

        Args:
            key_id: SSH key ID to delete

        Returns:
            True if successful, False otherwise

        Raises:
            SSHKeyNotFoundError: If the key doesn't exist
            SSHKeyError: For other deletion failures
        """
        try:
            self.http.request(
                method="DELETE",
                url=f"/v2/ssh-keys/{key_id}",
            )

            # Invalidate cache
            self._keys_cache = None

            logger.info(f"Deleted SSH key: {key_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete SSH key {key_id}: {e}")
            # Preserve the original error for better debugging
            error_msg = str(e)
            if "not found" in error_msg.lower():
                raise SSHKeyNotFoundError(f"SSH key {key_id} not found") from e
            raise SSHKeyError(f"Failed to delete SSH key {key_id}: {error_msg}") from e

    def get_key(self, key_id: str) -> Optional[SSHKey]:
        """Get a specific SSH key by ID.

        Args:
            key_id: SSH key ID

        Returns:
            SSHKey if found, None otherwise
        """
        keys = self.list_keys()
        for key in keys:
            if key.fid == key_id:
                return key
        return None

    def find_keys_by_name(self, name: str) -> List[SSHKey]:
        """Find SSH keys by name.

        Args:
            name: Key name to search for

        Returns:
            List of matching SSH keys (may be empty)
        """
        keys = self.list_keys()
        return [k for k in keys if k.name == name]

    def invalidate_cache(self):
        """Clear the cache, forcing fresh lookups."""
        self._keys_cache = None
        logger.debug("SSH key cache invalidated")

    def ensure_platform_keys(self, key_references: List[str]) -> List[str]:
        """Ensure local SSH keys are uploaded to platform.

        This method handles different key reference types:
        - Platform IDs (sshkey_*): Used directly
        - Key names: Resolved locally and uploaded if needed
        - Paths: Read and uploaded if needed

        Args:
            key_references: List of key references (names, paths, or platform IDs)

        Returns:
            List of platform SSH key IDs
        """
        from flow.core.ssh_resolver import SmartSSHKeyResolver, SSHKeyReference

        resolver = SmartSSHKeyResolver(ssh_key_manager=self)
        platform_keys = []

        for key_ref in key_references:
            key_reference = SSHKeyReference.from_config_value(key_ref)

            # Platform SSH key IDs can be used directly
            if key_reference.type == "platform_id":
                platform_keys.append(key_ref)
                continue

            # For local keys, resolve to file path and upload
            local_key_path = resolver.resolve_ssh_key(key_reference)
            if not local_key_path:
                logger.warning(
                    f"Could not resolve SSH key '{key_ref}'\n"
                    f"  - Not found locally in ~/.ssh/\n"
                    f"  - Not found on platform (check 'flow list-keys')\n"
                    f"  - May have different format (RSA vs ED25519)"
                )
                continue

            # Check if this key already exists on platform
            public_key_path = local_key_path.with_suffix(".pub")
            if not public_key_path.exists():
                logger.warning(
                    f"No public key found at {local_key_path}.pub\n"
                    f"  - Ensure both private and public keys exist\n"
                    f"  - Run 'ssh-keygen -y -f {local_key_path} > {local_key_path}.pub' to regenerate"
                )
                continue

            public_key_content = public_key_path.read_text().strip()

            # Check if key with same content already exists
            existing_platform_key = self._find_existing_key_by_content(public_key_content)
            if existing_platform_key:
                logger.info(
                    f"SSH key '{key_ref}' already exists on platform as {existing_platform_key}"
                )
                platform_keys.append(existing_platform_key)
                continue

            # Upload the key
            try:
                # Use the original reference as the name for clarity
                key_name = key_reference.value
                if key_name.startswith("~/"):
                    key_name = key_name.replace("~/", "home_")
                if "/" in key_name:
                    key_name = Path(key_name).stem

                platform_key_id = self.create_key(key_name, public_key_content)
                logger.info(f"Uploaded SSH key '{key_ref}' to platform as {platform_key_id}")
                platform_keys.append(platform_key_id)

                # Invalidate cache to include new key
                self.invalidate_cache()
            except Exception as e:
                logger.warning(f"Failed to upload SSH key '{key_ref}': {e}")

        return platform_keys

    def _find_existing_key_by_content(self, public_key_content: str) -> Optional[str]:
        """Find platform key with matching public key content.

        Args:
            public_key_content: SSH public key content

        Returns:
            Platform key ID if found, None otherwise
        """
        existing_keys = self.list_keys()

        # Normalize the key content for comparison
        normalized_content = public_key_content.strip()

        for key in existing_keys:
            if hasattr(key, "public_key") and key.public_key:
                if key.public_key.strip() == normalized_content:
                    return key.fid

        return None

    def _try_create_default_key(self) -> Optional[str]:
        """Try to create a default SSH key for Mithril use.

        This method ONLY checks environment variables and auto-generation.
        It does NOT scan or upload user's personal SSH keys from ~/.ssh/.

        Returns:
            Key ID if created, None otherwise
        """
        # Check environment variable for public key content.
        if public_key := os.environ.get("MITHRIL_SSH_PUBLIC_KEY"):
            try:
                logger.info("Creating SSH key from MITHRIL_SSH_PUBLIC_KEY environment variable")
                return self.create_key("flow-env-key", public_key)
            except Exception as e:
                logger.debug(f"Failed to create key from environment: {e}")

        # Check for MITHRIL_SSH_KEY environment variable pointing to a key file.
        if key_file := os.environ.get("MITHRIL_SSH_KEY"):
            try:
                key_path = Path(key_file)
                if key_path.exists():
                    # Check if it's a private key and find the corresponding public key.
                    if not key_file.endswith(".pub"):
                        pub_key_path = key_path.with_suffix(".pub")
                        if pub_key_path.exists():
                            # Verify private key has secure permissions.
                            from flow.utils.security import check_ssh_key_permissions

                            check_ssh_key_permissions(key_path)

                            public_key = pub_key_path.read_text().strip()
                            logger.info(
                                f"Creating SSH key from MITHRIL_SSH_KEY environment variable: {pub_key_path}"
                            )
                            return self.create_key("flow-mithril-key", public_key)
                    else:
                        # File is already a public key.
                        public_key = key_path.read_text().strip()
                        logger.info(
                            f"Creating SSH key from MITHRIL_SSH_KEY environment variable: {key_path}"
                        )
                        return self.create_key("flow-mithril-key", public_key)
            except Exception as e:
                logger.debug(f"Failed to create key from MITHRIL_SSH_KEY: {e}")

        # Check for previously auto-generated keys in cache.
        auto_key = self._get_cached_auto_key()
        if auto_key:
            logger.info(f"Using previously generated Mithril SSH key: {auto_key}")
            return auto_key

        # Generate a new Mithril-specific key.
        logger.info("No SSH keys found, auto-generating new Mithril-specific SSH key")
        return self.auto_generate_key()

    def auto_generate_key(self) -> Optional[str]:
        """Auto-generate an SSH key using the best available method.

        Tries server-side generation first (no local dependencies),
        falls back to local generation if needed.

        Returns:
            Optional[str]: SSH key ID if successful, None otherwise.
        """
        # Try server-side generation first (preferred)
        key_id = self.generate_server_key()
        if key_id:
            return key_id

        # Fall back to local generation if server-side fails
        logger.info("Server-side generation unavailable, trying local generation...")
        return self._generate_ssh_key()

    def generate_server_key(self) -> Optional[str]:
        """Generate SSH key server-side using Mithril API.

        This is simpler than local generation as it doesn't require ssh-keygen.
        Mithril returns both public and private keys which we save locally.

        Returns:
            Optional[str]: SSH key ID if successful, None if generation failed.
        """
        try:
            # Generate unique name with timestamp
            import random

            timestamp = int(time.time())
            random_suffix = random.randint(1000, 9999)
            key_name = f"flow-auto-{timestamp}-{random_suffix}"

            logger.info("Generating SSH key server-side...")

            # Make direct API call to get full response including private key
            # Validate project ID
            if not self.project_id:
                raise ValueError("Project ID is required for SSH key generation")

            request_payload = {
                "name": key_name,
                "project": self.project_id,
                # No public_key - server will generate both keys
            }
            logger.info(f"SSH key generation request: name={key_name}, project={self.project_id}")

            response = self.http.request(method="POST", url="/v2/ssh-keys", json=request_payload)

            logger.debug(f"SSH key generation response: {response}")

            key_id = response.get("fid")
            if not key_id:
                raise Exception(f"No key ID in response: {response}")

            # Save private key locally if returned
            if "private_key" in response:
                logger.info("Saving private key locally...")

                # Ensure key directory exists
                self._key_dir.mkdir(parents=True, exist_ok=True)

                # Save private key
                private_path = self._key_dir / key_name
                private_path.write_text(response["private_key"])
                private_path.chmod(0o600)  # Set proper permissions

                # Save public key if available
                if "public_key" in response:
                    public_path = self._key_dir / f"{key_name}.pub"
                    public_path.write_text(response["public_key"])
                    public_path.chmod(0o644)

                # Store metadata
                self._store_key_metadata(key_id, key_name, private_path)

                logger.info(f"Server-generated SSH key: {key_id}")
                logger.info(f"Private key saved to: {private_path}")
            else:
                logger.warning("No private key in server response")

            return key_id

        except Exception as e:
            logger.error(f"Failed to generate SSH key server-side: {type(e).__name__}: {e}")
            import traceback

            logger.debug(f"Full traceback: {traceback.format_exc()}")
            return None

    def _check_ssh_keygen_available(self) -> bool:
        """Check if ssh-keygen is available on the system.

        Returns:
            bool: True if ssh-keygen is found in PATH, False otherwise.
        """
        if shutil.which("ssh-keygen"):
            return True

        logger.warning(
            "ssh-keygen not found. SSH keys cannot be auto-generated. "
            "Install OpenSSH or manually create keys."
        )
        return False

    def generate_local_key(self) -> Optional[str]:
        """Generate SSH key locally using ssh-keygen.

        Public method for local key generation when server-side isn't available.

        Returns:
            Optional[str]: SSH key ID if successful, None if generation failed.
        """
        return self._generate_ssh_key()

    def _generate_ssh_key(self) -> Optional[str]:
        """Generate SSH key pair locally and register with Mithril.

        Creates an Ed25519 key pair using ssh-keygen, stores it in ~/.flow/keys,
        registers the public key with Mithril API, and tracks metadata locally.

        Returns:
            Optional[str]: SSH key ID if successful, None if generation failed.
        """
        # Check if ssh-keygen is available
        if not self._check_ssh_keygen_available():
            return None

        try:
            # Generate unique name with timestamp and random component
            import random

            timestamp = int(time.time())
            random_suffix = random.randint(1000, 9999)
            key_name = f"flow-auto-{timestamp}-{random_suffix}"

            # Generate key pair locally
            private_path, public_path = self._create_key_pair(key_name)

            # Read public key
            public_key = public_path.read_text().strip()

            # Register with Mithril API
            if not self.project_id:
                raise ValueError("Project ID is required for SSH key registration")

            response = self.http.request(
                method="POST",
                url="/v2/ssh-keys",
                json={"name": key_name, "project": self.project_id, "public_key": public_key},
            )

            # Store metadata
            key_id = response.get("fid")
            if not key_id:
                raise Exception(f"No key ID in response: {response}")
            self._store_key_metadata(key_id, key_name, private_path)

            logger.info(f"Auto-generated SSH key: {key_id}")
            return key_id

        except Exception as e:
            logger.debug(f"Failed to auto-generate SSH key: {e}")
            return None

    def _create_key_pair(self, key_name: str) -> Tuple[Path, Path]:
        """Create SSH key pair using ssh-keygen.

        Args:
            key_name: Base name for the key files (without extension).

        Returns:
            Tuple[Path, Path]: Paths to (private_key, public_key).

        Raises:
            SSHKeyError: If ssh-keygen fails or returns non-zero exit code.
        """
        key_dir = Path.home() / ".flow" / "keys"
        key_dir.mkdir(parents=True, exist_ok=True)

        private_path = key_dir / key_name
        public_path = private_path.with_suffix(".pub")

        # Build ssh-keygen command with secure defaults
        cmd = [
            "ssh-keygen",
            "-t",
            "ed25519",  # Ed25519 for better security and performance
            "-f",
            str(private_path),
            "-N",
            "",  # Empty passphrase for automation
            "-C",
            f"flow-auto@{platform.node()}",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)  # Prevent hanging
        if result.returncode != 0:
            raise SSHKeyError(f"ssh-keygen failed: {result.stderr}")

        # Ensure correct permissions
        self._set_key_permissions(private_path)

        return private_path, public_path

    def _store_key_metadata(self, key_id: str, key_name: str, private_path: Path) -> None:
        """Store metadata about auto-generated SSH key.

        Persists key information to ~/.flow/keys/metadata.json for future reuse.
        Updates existing metadata file if present, preserving other entries.

        Args:
            key_id: Mithril-assigned SSH key ID.
            key_name: Human-readable key name.
            private_path: Path to the private key file.
        """
        key_dir = private_path.parent

        # Store metadata
        metadata = {
            "key_id": key_id,
            "key_name": key_name,
            "private_key_path": str(private_path),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "project": self.project_id,
            "auto_generated": True,
        }

        metadata_path = key_dir / "metadata.json"
        existing = {}
        if metadata_path.exists():
            try:
                existing = json.loads(metadata_path.read_text())
            except Exception:
                pass

        existing[key_id] = metadata
        metadata_path.write_text(json.dumps(existing, indent=2))
        self._set_key_permissions(metadata_path)

    def _get_cached_auto_key(self) -> Optional[str]:
        """Check for previously auto-generated keys.

        Searches metadata.json for auto-generated keys belonging to the current
        project. Returns the most recently created key if multiple exist.

        Returns:
            Optional[str]: SSH key ID of most recent auto-generated key, or None.
        """
        metadata_path = Path.home() / ".flow" / "keys" / "metadata.json"
        if not metadata_path.exists():
            return None

        try:
            metadata = json.loads(metadata_path.read_text())
            # Filter keys by project and auto-generated flag
            project_keys = [
                (k, v)
                for k, v in metadata.items()
                if v.get("project") == self.project_id and v.get("auto_generated")
            ]
            if project_keys:
                # Sort by timestamp descending, return newest
                project_keys.sort(key=lambda x: x[1]["created_at"], reverse=True)
                return project_keys[0][0]
        except Exception:
            pass

        return None

    def _set_key_permissions(self, key_path: Path) -> None:
        """Set secure permissions on private key.

        Sets file permissions to 0600 (read/write for owner only) to meet
        SSH security requirements. Continues silently if permission setting
        fails (e.g., on non-Unix systems).

        Args:
            key_path: Path to the file requiring secure permissions.
        """
        try:
            key_path.chmod(0o600)
        except Exception as e:
            logger.debug(f"Could not set key permissions: {e}")
            # Continue execution - functional key with suboptimal permissions
            # is preferable to complete failure

    def find_matching_local_key(self, api_key_id: str) -> Optional[Path]:
        """Find local private key that matches an API SSH key.

        Searches standard SSH locations and cached metadata to find
        a local private key corresponding to the given API key ID.

        Args:
            api_key_id: Mithril SSH key ID to match

        Returns:
            Path to matching private key if found, None otherwise
        """
        # Get API key details
        api_key = self.get_key(api_key_id)
        if not api_key or not api_key.public_key:
            logger.debug(f"API key {api_key_id} not found or has no public key")
            return None

        # Check metadata cache first for auto-generated keys
        cached_key = self._check_metadata_for_key(api_key_id)
        if cached_key and cached_key.exists():
            logger.debug(f"Found cached key for {api_key_id}: {cached_key}")
            return cached_key

        # Standard SSH key locations to check
        key_paths = []

        # First check MITHRIL_SSH_KEY environment variable
        if env_key := os.environ.get("MITHRIL_SSH_KEY"):
            env_path = Path(env_key).expanduser()
            if not env_path.suffix == ".pub":
                key_paths.append(env_path)

        # Add standard key names
        standard_names = ["id_rsa", "id_ed25519", "id_ecdsa", "id_dsa"]
        for name in standard_names:
            key_paths.append(Path.home() / ".ssh" / name)

        # Also check all other SSH keys in ~/.ssh directory
        ssh_dir = Path.home() / ".ssh"
        if ssh_dir.exists():
            for key_file in ssh_dir.glob("*"):
                # Skip if it's a public key, directory, or already in our list
                if (
                    not key_file.suffix == ".pub"
                    and key_file.is_file()
                    and key_file not in key_paths
                    and key_file.name not in ["known_hosts", "authorized_keys", "config"]
                ):
                    key_paths.append(key_file)

        # Try each potential private key
        for private_key_path in key_paths:
            if not private_key_path.exists():
                continue

            public_key_path = private_key_path.with_suffix(".pub")
            if not public_key_path.exists():
                continue

            try:
                local_public_key = public_key_path.read_text().strip()
                if self._keys_match(local_public_key, api_key.public_key):
                    logger.info(f"Found matching local key for {api_key.name}: {private_key_path}")
                    return private_key_path
            except Exception as e:
                logger.debug(f"Error reading {public_key_path}: {e}")
                continue

        logger.debug(f"No matching local key found for {api_key_id} ({api_key.name})")
        return None

    def _check_metadata_for_key(self, api_key_id: str) -> Optional[Path]:
        """Check metadata cache for auto-generated key.

        Args:
            api_key_id: Mithril SSH key ID

        Returns:
            Path to private key if found in metadata, None otherwise
        """
        metadata_path = Path.home() / ".flow" / "keys" / "metadata.json"
        if not metadata_path.exists():
            return None

        try:
            metadata = json.loads(metadata_path.read_text())
            if api_key_id in metadata:
                key_info = metadata[api_key_id]
                private_path = Path(key_info.get("private_key_path", ""))
                if private_path.exists():
                    return private_path
        except Exception as e:
            logger.debug(f"Error reading metadata: {e}")

        return None

    def _keys_match(self, local_public_key: str, api_public_key: str) -> bool:
        """Compare two SSH public keys for equality.

        Normalizes keys before comparison to handle formatting differences.

        Args:
            local_public_key: Public key content from local file
            api_public_key: Public key content from API

        Returns:
            True if keys match, False otherwise
        """
        # Normalize keys - strip whitespace and comments
        local_normalized = self._normalize_public_key(local_public_key)
        api_normalized = self._normalize_public_key(api_public_key)

        return local_normalized == api_normalized

    def _normalize_public_key(self, public_key: str) -> str:
        """Normalize SSH public key for comparison.

        Extracts the key type and base64 data, ignoring comments.

        Args:
            public_key: Raw public key content

        Returns:
            Normalized key string (type + base64 data)
        """
        try:
            # SSH public keys format: <type> <base64-data> [comment]
            parts = public_key.strip().split()
            if len(parts) >= 2:
                # Return type and key data only
                return f"{parts[0]} {parts[1]}"
            return public_key.strip()
        except Exception:
            return public_key.strip()
