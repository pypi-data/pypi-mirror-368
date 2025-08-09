"""Mount specification parser for storage mounts.

Handles parsing of mount specifications in various formats:
- source (auto-generates target based on source type)
- target=source (explicit target path)

Auto-mount rules:
- s3:// URLs mount to /data
- volume:// URLs mount to /mnt
- Other paths mount to /mnt/<basename>
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple


class MountParser:
    """Parse and validate mount specifications."""

    # Default mount points for different source types
    AUTO_MOUNT_RULES = {
        "s3://": "/data",
        "volume://": "/mnt",
    }

    def parse_mounts(self, mount_specs: Tuple[str, ...]) -> Optional[Dict[str, str]]:
        """Parse mount specifications into target:source mapping.

        Args:
            mount_specs: Tuple of mount specifications in format:
                - "source" (auto-generates target)
                - "target=source" (explicit target)

        Returns:
            Dictionary mapping target paths to source paths,
            or None if no mounts specified.

        Examples:
            >>> parser = MountParser()
            >>> parser.parse_mounts(("s3://bucket/data",))
            {'/data': 's3://bucket/data'}

            >>> parser.parse_mounts(("/workspace=s3://bucket/data",))
            {'/workspace': 's3://bucket/data'}

            >>> parser.parse_mounts(("volume://vol-123",))
            {'/mnt': 'volume://vol-123'}
        """
        if not mount_specs:
            return None

        mount_dict = {}

        for mount_spec in mount_specs:
            target, source = self._parse_single_mount(mount_spec)

            # Check for duplicate targets
            if target in mount_dict:
                raise ValueError(
                    f"Duplicate mount target '{target}'. "
                    f"Both '{mount_dict[target]}' and '{source}' mount to the same path."
                )

            mount_dict[target] = source

        return mount_dict

    def _parse_single_mount(self, mount_spec: str) -> Tuple[str, str]:
        """Parse a single mount specification.

        Args:
            mount_spec: Mount specification string

        Returns:
            Tuple of (target, source)

        Raises:
            ValueError: If mount specification is invalid
        """
        if not mount_spec:
            raise ValueError("Empty mount specification")

        if "=" in mount_spec:
            # Format: target=source
            parts = mount_spec.split("=", 1)
            if len(parts) != 2 or not parts[0] or not parts[1]:
                raise ValueError(f"Invalid mount specification: '{mount_spec}'")

            target, source = parts

            # Validate target path
            if not target.startswith("/"):
                raise ValueError(f"Mount target must be an absolute path: '{target}'")

            return target, source
        else:
            # Format: source (auto-generate target)
            source = mount_spec
            target = self._generate_target_path(source)
            return target, source

    def _generate_target_path(self, source: str) -> str:
        """Generate target path based on source type.

        Args:
            source: Source path or URL

        Returns:
            Generated target path
        """
        # Check auto-mount rules
        for prefix, target in self.AUTO_MOUNT_RULES.items():
            if source.startswith(prefix):
                return target

        # For local paths, mount under /mnt/<basename>
        try:
            path = Path(source)
            basename = path.name
            if basename:
                return f"/mnt/{basename}"
            else:
                # Handle edge case of root directory
                return "/mnt/root"
        except Exception:
            # If path parsing fails, use a generic mount point
            return "/mnt/data"

    def validate_mounts(self, mounts: Dict[str, str]) -> List[str]:
        """Validate mount configuration.

        Args:
            mounts: Dictionary of target:source mappings

        Returns:
            List of validation warnings (empty if all valid)
        """
        warnings = []

        for target, source in mounts.items():
            # Check for overlapping mount points
            for other_target in mounts:
                if target != other_target and target.startswith(other_target + "/"):
                    warnings.append(f"Mount target '{target}' is inside '{other_target}'")

            # Warn about common system directories
            system_dirs = ["/bin", "/etc", "/proc", "/sys", "/dev", "/tmp"]
            if any(target.startswith(d) for d in system_dirs):
                warnings.append(f"Mount target '{target}' overlaps with system directory")

        return warnings

    def format_mounts_display(self, mounts: Dict[str, str]) -> List[str]:
        """Format mounts for display.

        Args:
            mounts: Dictionary of target:source mappings

        Returns:
            List of formatted mount strings
        """
        if not mounts:
            return []

        return [f"{target} → {source}" for target, source in sorted(mounts.items())]
