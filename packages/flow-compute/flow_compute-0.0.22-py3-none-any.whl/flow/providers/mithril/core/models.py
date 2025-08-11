"""Mithril-specific models.

These models represent Mithril's API responses and concepts.
They are separate from the domain models to maintain clean architecture.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator


class MithrilBid(BaseModel):
    """Mithril bid model - their concept of a 'task'.

    This represents what Mithril calls a 'bid' which maps to our domain concept of a 'task'.
    """

    fid: str = Field(..., description="Mithril ID for the bid")
    name: str = Field(..., description="User-provided name")
    project: str = Field(..., description="Project ID")
    created_by: str = Field(..., description="User ID who created the bid")
    created_at: datetime = Field(..., description="When the bid was created")
    deactivated_at: datetime | None = Field(None, description="When the bid was deactivated")

    # Bid details
    status: str = Field(..., description="Status like 'Pending', 'Allocated', 'Failed'")
    limit_price: str = Field(..., description="Max price in dollar format like '$25.00'")
    instance_quantity: int = Field(..., description="Number of instances requested")
    instance_type: str = Field(..., description="Instance type ID like 'it_XqgKWbhZ5gznAYsG'")
    region: str = Field(..., description="Region like 'us-central1-b'")

    # Runtime
    instances: list[str] = Field(default_factory=list, description="Instance IDs if allocated")
    launch_specification: dict[str, Any] = Field(
        default_factory=dict, description="Contains ssh_keys, startup_script, volumes"
    )

    # Optional fields that might be in responses
    auction_id: str | None = Field(None, description="Auction ID if spot bid")


class MithrilInstance(BaseModel):
    """Mithril instance model.

    Represents a running compute instance in Mithril.
    """

    fid: str = Field(..., description="Instance ID")
    bid_id: str = Field(..., description="Parent bid ID")
    status: str = Field(..., description="Status like 'Provisioning', 'Running', 'Terminating'")

    # Connection details (might need separate API call)
    public_ip: str | None = Field(None, description="Public IP address")
    private_ip: str | None = Field(None, description="Private IP address")
    ssh_host: str | None = Field(None, description="SSH connection string")
    ssh_port: int | None = Field(22, description="SSH port")

    # Metadata
    instance_type: str = Field(..., description="Instance type ID")
    region: str = Field(..., description="Region")
    created_at: datetime = Field(..., description="When instance was created")

    # Optional fields
    terminated_at: datetime | None = Field(None, description="When instance was terminated")


class MithrilAuction(BaseModel):
    """Mithril auction/spot availability model.

    Represents available spot capacity.
    """

    fid: str = Field(..., description="Auction ID like 'auc_rECU5s87CABp37aB'")
    instance_type: str = Field(..., description="Instance type ID")
    region: str = Field(..., description="Region")
    capacity: int = Field(..., description="Available capacity")
    last_instance_price: str = Field(..., description="Last price like '$12.00'")

    # Optional fields from API
    created_at: datetime | None = Field(None, description="When auction was created")
    expires_at: datetime | None = Field(None, description="When auction expires")


class MithrilVolume(BaseModel):
    """Mithril volume model.

    Represents a storage volume.
    """

    fid: str = Field(..., description="Volume ID")
    name: str = Field(..., description="Volume name")
    size_gb: int = Field(..., description="Size in GB")
    region: str = Field(..., description="Region")
    status: str = Field(..., description="Status like 'available', 'attached'")
    created_at: datetime = Field(..., description="When volume was created")

    # Attachment info
    attached_to: list[str] = Field(default_factory=list, description="Instance IDs")
    mount_path: str | None = Field(None, description="Mount path if attached")


class MithrilProject(BaseModel):
    """Mithril project model."""

    fid: str = Field(..., description="Project ID like 'proj_0C7CSvEyFRpE8o8V'")
    name: str = Field(..., description="Project name like 'test'")
    created_at: datetime = Field(..., description="When project was created")

    # Optional fields
    region: str | None = Field(None, description="Default region")
    organization_id: str | None = Field(None, description="Parent organization")


class MithrilSSHKey(BaseModel):
    """Mithril SSH key model."""

    fid: str = Field(..., description="SSH key ID like 'sshkey_UO4YxwT5EoySoGys'")
    name: str = Field(..., description="Key name")
    public_key: str = Field(..., description="SSH public key content")
    created_at: datetime = Field(..., description="When key was created")

    # Optional
    fingerprint: str | None = Field(None, description="Key fingerprint")
    created_by: str | None = Field(None, description="User who created the key")


class Auction(BaseModel):
    """Unified auction model used across provider components.

    This model normalizes differing field names used across older and newer
    implementations so existing code paths remain compatible.

    Supported synonymous fields:
    - auction_id <-> fid
    - instance_type_id <-> instance_type
    - available_gpus <-> capacity
    - price_per_hour (float) <-> last_instance_price (e.g. "$12.00")
    """

    # Identity
    auction_id: str | None = Field(None, description="Auction ID")
    fid: str | None = Field(None, description="Alias for auction_id")

    # Instance type
    instance_type_id: str | None = Field(None, description="Instance type identifier")
    instance_type: str | None = Field(None, description="Alias for instance_type_id")

    # Attributes
    gpu_type: str | None = Field(None, description="GPU type name")
    available_gpus: int | None = Field(None, description="Available GPU count")
    capacity: int | None = Field(None, description="Alias for available_gpus")

    # Pricing
    price_per_hour: float | None = Field(None, ge=0, description="Price in dollars per hour")
    last_instance_price: str | None = Field(None, description="Formatted price like '$12.00'")

    # Region / networking
    region: str | None = Field(None, description="Region identifier")
    internode_interconnect: str | None = Field(None, description="Inter-node network type")
    intranode_interconnect: str | None = Field(None, description="Intra-node network type")

    @model_validator(mode="after")
    def _normalize_synonyms(self) -> "Auction":
        # auction_id <-> fid
        if self.auction_id and not self.fid:
            object.__setattr__(self, "fid", self.auction_id)
        if self.fid and not self.auction_id:
            object.__setattr__(self, "auction_id", self.fid)

        # instance_type_id <-> instance_type
        if self.instance_type_id and not self.instance_type:
            object.__setattr__(self, "instance_type", self.instance_type_id)
        if self.instance_type and not self.instance_type_id:
            object.__setattr__(self, "instance_type_id", self.instance_type)

        # available_gpus <-> capacity
        if self.available_gpus is not None and self.capacity is None:
            object.__setattr__(self, "capacity", int(self.available_gpus))
        if self.capacity is not None and self.available_gpus is None:
            object.__setattr__(self, "available_gpus", int(self.capacity))

        # price_per_hour <-> last_instance_price
        if self.price_per_hour is not None and self.last_instance_price is None:
            # Format as $X.YY
            object.__setattr__(self, "last_instance_price", f"${self.price_per_hour:.2f}")
        if self.last_instance_price is not None and self.price_per_hour is None:
            try:
                # Strip leading '$' and convert to float
                normalized = self.last_instance_price.strip().lstrip("$")
                object.__setattr__(self, "price_per_hour", float(normalized))
            except Exception:
                # Leave as None if unparsable
                pass

        return self
