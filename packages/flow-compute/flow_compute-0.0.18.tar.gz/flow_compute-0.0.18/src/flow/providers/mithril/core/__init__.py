"""Core Mithril provider components - models, constants, and errors.

This package contains the foundational elements of the Mithril provider:
- Domain models (MithrilBid, MithrilInstance, MithrilVolume, Auction)
- Constants and configuration values
- Mithril-specific error types
"""

from .constants import (
    DEFAULT_REGION,
    DEFAULT_SSH_PORT,
    DEFAULT_SSH_USER,
    DISK_INTERFACE_BLOCK,
    DISK_INTERFACE_FILE,
    MITHRIL_LOG_DIR,
    MITHRIL_STARTUP_LOG,
    FLOW_LEGACY_LOG_DIR,
    FLOW_LOG_DIR,
    MAX_INSTANCES_PER_TASK,
    MAX_VOLUME_SIZE_GB,
    STARTUP_SCRIPT_MAX_SIZE,
    STATUS_MAPPINGS,
    SUPPORTED_REGIONS,
    USER_CACHE_TTL,
    VALID_DISK_INTERFACES,
    VALID_REGIONS,
    VOLUME_DELETE_TIMEOUT,
    VOLUME_ID_PREFIX,
)
from .errors import (
    MithrilAPIError,
    MithrilAuthenticationError,
    MithrilBidError,
    MithrilError,
    MithrilInstanceError,
    MithrilQuotaExceededError,
    MithrilResourceNotFoundError,
    MithrilTimeoutError,
    MithrilValidationError,
    MithrilVolumeError,
)
from .models import Auction, MithrilBid, MithrilInstance, MithrilVolume

__all__ = [
    # Constants
    "VALID_REGIONS",
    "STARTUP_SCRIPT_MAX_SIZE",
    "DISK_INTERFACE_BLOCK",
    "DISK_INTERFACE_FILE",
    "VALID_DISK_INTERFACES",
    "DEFAULT_REGION",
    "DEFAULT_SSH_PORT",
    "DEFAULT_SSH_USER",
    "MITHRIL_LOG_DIR",
    "MITHRIL_STARTUP_LOG",
    "FLOW_LEGACY_LOG_DIR",
    "FLOW_LOG_DIR",
    "MAX_INSTANCES_PER_TASK",
    "MAX_VOLUME_SIZE_GB",
    "STATUS_MAPPINGS",
    "SUPPORTED_REGIONS",
    "USER_CACHE_TTL",
    "VOLUME_DELETE_TIMEOUT",
    "VOLUME_ID_PREFIX",
    # Errors
    "MithrilError",
    "MithrilAPIError",
    "MithrilAuthenticationError",
    "MithrilResourceNotFoundError",
    "MithrilQuotaExceededError",
    "MithrilValidationError",
    "MithrilTimeoutError",
    "MithrilInstanceError",
    "MithrilBidError",
    "MithrilVolumeError",
    # Models
    "MithrilBid",
    "MithrilInstance",
    "MithrilVolume",
    "Auction",
]
