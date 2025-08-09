"""Type definitions for Mithril API responses.

Strong typing for all API responses based on the official Mithril spec.
These types ensure compile-time safety and self-documenting code.
"""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProjectModel(BaseModel):
    """Project resource from /v2/projects."""

    fid: str
    name: str
    created_at: datetime


class SSHKeyModel(BaseModel):
    """SSH key resource from /v2/ssh-keys."""

    fid: str
    name: str
    project: Optional[str] = None
    public_key: str
    created_at: datetime


class GPUModel(BaseModel):
    """GPU specifications within an instance type."""

    name: str
    vram_gb: int
    count: int


class InstanceTypeModel(BaseModel):
    """Instance type resource from /v2/instance-types."""

    name: str
    fid: str
    cpu_cores: Optional[int] = Field(None, alias="num_cpus")  # API uses num_cpus
    ram_gb: Optional[int] = Field(None, alias="ram")  # API uses ram
    gpus: Optional[List[GPUModel]] = None
    storage_gb: Optional[int] = Field(None, alias="local_storage_gb")
    network_bandwidth_gbps: Optional[float] = None

    model_config = ConfigDict(populate_by_name=True)  # Allow both field names and aliases


class AuctionModel(BaseModel):
    """Spot auction resource from /v2/spot/availability."""

    fid: str
    instance_type: str
    region: str
    capacity: int
    last_instance_price: str  # Dollar string format: "$25.60"
    min_bid_price: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BidModel(BaseModel):
    """Spot bid resource from /v2/spot/bids."""

    fid: str
    project: str
    region: str
    instance_type: str
    price: str  # Dollar string format
    status: Literal["pending", "running", "completed", "failed", "cancelled"]
    created_at: datetime
    updated_at: datetime
    ssh_keys: List[str]
    startup_script: Optional[str] = None
    volumes: Optional[List[str]] = None


class BidsResponse(BaseModel):
    """Paginated response from GET /v2/spot/bids."""

    data: List[BidModel]
    next_cursor: Optional[str] = None


class VolumeModel(BaseModel):
    """Storage volume resource from /v2/volumes."""

    fid: str
    name: str
    project: str
    region: str
    capacity_gb: int
    interface: Literal["block", "file"]
    status: Literal["available", "attached", "deleting"]
    created_at: datetime
    updated_at: datetime


# Type aliases for API responses
ProjectsResponse = List[ProjectModel]
SSHKeysResponse = List[SSHKeyModel]
InstanceTypesResponse = List[InstanceTypeModel]
SpotAvailabilityResponse = List[AuctionModel]
VolumesResponse = List[VolumeModel]


# Request models
class CreateVolumeRequest(BaseModel):
    """Request to create a volume."""

    name: str
    project: str
    disk_interface: str
    region: str
    size_gb: int


class CreateBidRequest(BaseModel):
    """Request to create a spot bid."""

    project: str
    region: str
    instance_type: str
    price: str  # Dollar string format
    ssh_keys: List[str]
    startup_script: Optional[str] = None
    volumes: Optional[List[str]] = None


class UpdateBidRequest(BaseModel):
    """Request to update a spot bid."""

    price: Optional[str] = None
    status: Optional[Literal["cancelled"]] = None


# Response models
class UserModel(BaseModel):
    """User information from /v2/me."""

    fid: str
    email: str
    name: Optional[str] = None
    created_at: datetime


class CreatedSshKey(BaseModel):
    """Response from creating an SSH key."""

    fid: str
    name: str
    project: str
    public_key: str
    created_at: datetime


class InstanceModel(BaseModel):
    """Instance resource."""

    fid: str
    bid: str
    status: Literal["pending", "running", "stopped", "terminated"]
    public_ip: Optional[str] = None
    private_ip: Optional[str] = None
    created_at: datetime
    terminated_at: Optional[datetime] = None
