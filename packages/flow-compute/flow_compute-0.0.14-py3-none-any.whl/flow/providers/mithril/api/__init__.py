"""Mithril API interaction layer.

This package handles communication with the Mithril API:
- API data types and models
- Error handling and response validation
"""

from .handlers import handle_mithril_errors, validate_response
from .types import (
    AuctionModel,
    GPUModel,
    InstanceTypeModel,
    InstanceTypesResponse,
    ProjectModel,
    SpotAvailabilityResponse,
    SSHKeyModel,
)

__all__ = [
    # Handlers
    "handle_mithril_errors",
    "validate_response",
    # Types
    "ProjectModel",
    "SSHKeyModel",
    "GPUModel",
    "InstanceTypeModel",
    "AuctionModel",
    "SpotAvailabilityResponse",
    "InstanceTypesResponse",
]
