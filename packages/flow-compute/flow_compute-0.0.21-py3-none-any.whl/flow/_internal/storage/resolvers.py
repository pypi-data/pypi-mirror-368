"""Storage resolver implementations."""

import os
from typing import Any
from urllib.parse import urlparse

from flow._internal.data.resolver import DataError
from flow.core.paths import S3FS_CACHE_DIR
from flow.api.models import MountSpec


class MithrilVolumeResolver:
    """Resolver for Mithril volume storage.

    Handles volume:// URLs and Mithril-specific volume IDs (vol_*).
    """

    def __init__(self):
        # Cache for name->ID mappings
        self._name_cache: dict[str, str] = {}

    def can_resolve(self, url: str) -> bool:
        """Check if this is a volume URL."""
        parsed = urlparse(url)
        return parsed.scheme == "volume" or url.startswith("vol_")

    def resolve(self, url: str, target: str, context: dict[str, Any]) -> MountSpec:
        """Resolve volume URL to mount spec."""
        provider = context.get("provider")
        if not provider:
            raise DataError("Provider required for volume resolution")

        # Parse the URL
        if url.startswith("vol_"):
            # Direct volume ID
            volume_id = url
        else:
            parsed = urlparse(url)
            volume_ref = parsed.netloc or parsed.path.lstrip("/")

            if not volume_ref:
                raise DataError(
                    "Invalid volume URL: missing volume name/ID",
                    suggestions=["Use volume://name or volume://vol_id"],
                )

            # Check if it's an ID or name
            if self.is_storage_id(volume_ref):
                volume_id = volume_ref
            else:
                volume_id = self._resolve_name(volume_ref, provider)

        return MountSpec(
            source=f"/volumes/{volume_id}",
            target=target,
            mount_type="volume",
            options={"volume_id": volume_id},
        )

    def is_storage_id(self, identifier: str) -> bool:
        """Check if identifier is an Mithril volume ID."""
        return identifier.startswith("vol_")

    def _resolve_name(self, name: str, provider: Any) -> str:
        """Resolve volume name to ID."""
        # Check cache first
        cache_key = f"{provider.__class__.__name__}:{name}"
        if cache_key in self._name_cache:
            return self._name_cache[cache_key]

        # List volumes and find by name
        volumes = provider.list_volumes(limit=1000)
        for vol in volumes:
            vol_name = vol.get("name") if isinstance(vol, dict) else vol.name
            vol_id = vol.get("id") if isinstance(vol, dict) else vol.volume_id

            if vol_name == name:
                self._name_cache[cache_key] = vol_id
                return vol_id

        # Not found - create it with default size
        new_volume = provider.create_volume(size_gb=100, name=name)
        volume_id = new_volume.volume_id if hasattr(new_volume, "volume_id") else new_volume["id"]
        self._name_cache[cache_key] = volume_id
        return volume_id


class LocalPathResolver:
    """Resolver for local filesystem paths."""

    def can_resolve(self, url: str) -> bool:
        """Check if this is a local path."""
        parsed = urlparse(url)
        return not parsed.scheme or parsed.scheme == "file"

    def resolve(self, url: str, target: str, context: dict[str, Any]) -> MountSpec:
        """Resolve local path to bind mount."""
        parsed = urlparse(url)
        path = parsed.path if parsed.scheme else url

        abspath = os.path.abspath(path)
        if not os.path.exists(abspath):
            raise DataError(
                f"Local path does not exist: {abspath}",
                suggestions=["Check the path exists", "Use absolute paths"],
            )

        return MountSpec(
            source=abspath, target=target, mount_type="bind", options={"readonly": True}
        )

    def is_storage_id(self, identifier: str) -> bool:
        """Local paths are never storage IDs."""
        return False


class S3Resolver:
    """Resolver for S3 URLs."""

    def can_resolve(self, url: str) -> bool:
        """Check if this is an S3 URL."""
        parsed = urlparse(url)
        return parsed.scheme == "s3"

    def resolve(self, url: str, target: str, context: dict[str, Any]) -> MountSpec:
        """Resolve S3 URL to s3fs mount."""
        parsed = urlparse(url)

        if not parsed.netloc:
            raise DataError(
                "Invalid S3 URL: missing bucket name", suggestions=["Use s3://bucket/path format"]
            )

        bucket = parsed.netloc
        prefix = parsed.path.lstrip("/")

        # Build S3 URL for s3fs
        s3_url = f"s3://{bucket}"
        if prefix:
            s3_url = f"{s3_url}/{prefix}"

            return MountSpec(
                source=s3_url,
                target=target,
                mount_type="s3fs",
                options={
                    "bucket": bucket,
                    "prefix": prefix,
                    "readonly": True,
                    # S3FS options for performance (centralized cache path)
                    "cache": S3FS_CACHE_DIR,
                    "parallel_count": "16",
                    "multipart_size": "128",
                },
            )

    def is_storage_id(self, identifier: str) -> bool:
        """S3 URLs are never storage IDs."""
        return False
