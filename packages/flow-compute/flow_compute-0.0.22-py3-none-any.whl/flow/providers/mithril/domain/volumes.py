"""Volume service for Mithril provider.

Encapsulates volume CRUD and list operations, mapping provider-specific payloads
and responses to domain models via adapters, and centralizing validation.
"""

from __future__ import annotations

from datetime import datetime

from flow.api.models import Volume
from flow.errors import ValidationError
from flow.providers.mithril.adapters.models import MithrilAdapter
from flow.providers.mithril.api.client import MithrilApiClient
from flow.providers.mithril.core.constants import (
    DEFAULT_REGION,
    DISK_INTERFACE_BLOCK,
    DISK_INTERFACE_FILE,
    MAX_VOLUME_SIZE_GB,
)
from flow.providers.mithril.core.models import MithrilVolume


class VolumeService:
    """Service to manage volumes in Mithril."""

    def __init__(self, api: MithrilApiClient, *, default_region: str = DEFAULT_REGION) -> None:
        self._api = api
        self._default_region = default_region

    def create_volume(
        self, *, project_id: str, size_gb: int, name: str | None, interface: str, region: str | None
    ) -> Volume:
        if size_gb > MAX_VOLUME_SIZE_GB:
            raise ValidationError(f"Volume size {size_gb}GB exceeds maximum {MAX_VOLUME_SIZE_GB}GB")

        disk_interface = DISK_INTERFACE_FILE if interface == "file" else DISK_INTERFACE_BLOCK
        payload = {
            "size_gb": size_gb,
            "name": name or self._generate_name(),
            "project": project_id,
            "disk_interface": disk_interface,
            "region": region or self._default_region,
        }

        resp = self._api.create_volume(payload)
        # Normalize fields and adapt to domain
        mv = MithrilVolume(
            fid=resp["fid"],
            name=resp.get("name", payload["name"]),
            size_gb=size_gb,
            region=resp.get("region", payload["region"]),
            status=resp.get("status", "available"),
            created_at=resp.get("created_at", datetime.now().isoformat()),  # type: ignore[arg-type]
            attached_to=resp.get("attached_to", []),
            mount_path=resp.get("mount_path"),
        )
        return MithrilAdapter.mithril_volume_to_volume(mv)

    def delete_volume(self, volume_id: str) -> bool:
        # API deletion is synchronous; timeout handled at HTTP layer in provider
        self._api.delete_volume(volume_id)
        return True

    def list_volumes(
        self, *, project_id: str, region: str | None, limit: int = 100
    ) -> list[Volume]:
        params = {
            "project": project_id,
            "region": region or self._default_region,
            "limit": str(limit),
            "sort_by": "created_at",
            "sort_dir": "desc",
        }
        resp = self._api.list_volumes(params)
        volumes_data = resp if isinstance(resp, list) else resp.get("data", resp.get("volumes", []))

        out: list[Volume] = []
        for v in volumes_data:
            size_gb = v.get("capacity_gb") if "capacity_gb" in v else v.get("size_gb", 0)
            mv = MithrilVolume(
                fid=v.get("fid"),
                name=v.get("name"),
                size_gb=int(size_gb or 0),
                region=v.get("region", self._default_region),
                status=v.get("status", "available"),
                created_at=v.get("created_at", datetime.now().isoformat()),  # type: ignore[arg-type]
                attached_to=v.get("attached_to", []),
                mount_path=v.get("mount_path"),
            )
            out.append(MithrilAdapter.mithril_volume_to_volume(mv))
        return out

    # Optional: raw upload endpoints are provider-specific and not standardized; keep in facade

    def _generate_name(self) -> str:
        import time
        import uuid

        ts = int(time.time() * 1000) % 10_000_000
        rand = uuid.uuid4().hex[:4]
        return f"flow-volume-{ts}-{rand}"
