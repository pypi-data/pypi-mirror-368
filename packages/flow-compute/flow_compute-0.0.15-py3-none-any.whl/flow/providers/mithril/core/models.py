"""Mithril-specific models.

These models represent Mithril's API responses and concepts.
They are separate from the domain models to maintain clean architecture.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MithrilBid(BaseModel):
    """Mithril bid model - their concept of a 'task'.

    This represents what Mithril calls a 'bid' which maps to our domain concept of a 'task'.
    """

    fid: str = Field(..., description="Mithril ID for the bid")
    name: str = Field(..., description="User-provided name")
    project: str = Field(..., description="Project ID")
    created_by: str = Field(..., description="User ID who created the bid")
    created_at: datetime = Field(..., description="When the bid was created")
    deactivated_at: Optional[datetime] = Field(None, description="When the bid was deactivated")

    # Bid details
    status: str = Field(..., description="Status like 'Pending', 'Allocated', 'Failed'")
    limit_price: str = Field(..., description="Max price in dollar format like '$25.00'")
    instance_quantity: int = Field(..., description="Number of instances requested")
    instance_type: str = Field(..., description="Instance type ID like 'it_XqgKWbhZ5gznAYsG'")
    region: str = Field(..., description="Region like 'us-central1-b'")

    # Runtime
    instances: List[str] = Field(default_factory=list, description="Instance IDs if allocated")
    launch_specification: Dict[str, Any] = Field(
        default_factory=dict, description="Contains ssh_keys, startup_script, volumes"
    )

    # Optional fields that might be in responses
    auction_id: Optional[str] = Field(None, description="Auction ID if spot bid")


class MithrilInstance(BaseModel):
    """Mithril instance model.

    Represents a running compute instance in Mithril.
    """

    fid: str = Field(..., description="Instance ID")
    bid_id: str = Field(..., description="Parent bid ID")
    status: str = Field(..., description="Status like 'Provisioning', 'Running', 'Terminating'")

    # Connection details (might need separate API call)
    public_ip: Optional[str] = Field(None, description="Public IP address")
    private_ip: Optional[str] = Field(None, description="Private IP address")
    ssh_host: Optional[str] = Field(None, description="SSH connection string")
    ssh_port: Optional[int] = Field(22, description="SSH port")

    # Metadata
    instance_type: str = Field(..., description="Instance type ID")
    region: str = Field(..., description="Region")
    created_at: datetime = Field(..., description="When instance was created")

    # Optional fields
    terminated_at: Optional[datetime] = Field(None, description="When instance was terminated")


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
    created_at: Optional[datetime] = Field(None, description="When auction was created")
    expires_at: Optional[datetime] = Field(None, description="When auction expires")


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
    attached_to: List[str] = Field(default_factory=list, description="Instance IDs")
    mount_path: Optional[str] = Field(None, description="Mount path if attached")


class MithrilProject(BaseModel):
    """Mithril project model."""

    fid: str = Field(..., description="Project ID like 'proj_0C7CSvEyFRpE8o8V'")
    name: str = Field(..., description="Project name like 'test'")
    created_at: datetime = Field(..., description="When project was created")

    # Optional fields
    region: Optional[str] = Field(None, description="Default region")
    organization_id: Optional[str] = Field(None, description="Parent organization")


class MithrilSSHKey(BaseModel):
    """Mithril SSH key model."""

    fid: str = Field(..., description="SSH key ID like 'sshkey_UO4YxwT5EoySoGys'")
    name: str = Field(..., description="Key name")
    public_key: str = Field(..., description="SSH public key content")
    created_at: datetime = Field(..., description="When key was created")

    # Optional
    fingerprint: Optional[str] = Field(None, description="Key fingerprint")
    created_by: Optional[str] = Field(None, description="User who created the key")


# Temporary compatibility aliases during refactoring
Project = MithrilProject
SSHKey = MithrilSSHKey
Auction = MithrilAuction
Bid = MithrilBid
VolumeResponse = MithrilVolume
InstanceType = None  # This will need to be handled differently
