"""Bid building component for the Mithril provider.

Provides a small, testable helper for constructing bid payloads.
"""

import logging
from dataclasses import dataclass
from typing import Any

from flow.api.models import TaskConfig
from flow.errors import FlowError

logger = logging.getLogger(__name__)


class BidValidationError(FlowError):
    """Raised when bid parameters are invalid."""

    pass


@dataclass
class BidSpecification:
    """Complete specification for a bid request."""

    # Required fields
    project_id: str
    region: str
    name: str
    instance_quantity: int
    limit_price: str  # Dollar string format (e.g., "$25.60")

    # Instance targeting - must have auction_id OR instance_type (not both)
    auction_id: str | None = None
    instance_type: str | None = None

    # Launch specification
    ssh_keys: list[str] = None
    startup_script: str = ""
    volumes: list[dict[str, Any]] = None

    def __post_init__(self):
        """Validate the specification after initialization."""
        self._validate()

        # Set defaults
        if self.ssh_keys is None:
            self.ssh_keys = []
        if self.volumes is None:
            self.volumes = []

    def _validate(self):
        """Validate bid specification.

        Raises:
            BidValidationError: If specification is invalid
        """
        # Required fields
        if not self.project_id:
            raise BidValidationError("project_id is required")
        if not self.region:
            raise BidValidationError("region is required")
        if not self.name:
            raise BidValidationError("name is required")
        if self.instance_quantity < 1:
            raise BidValidationError("instance_quantity must be at least 1")

        # Price validation
        if not self.limit_price or not self.limit_price.startswith("$"):
            raise BidValidationError("limit_price must be in dollar format (e.g., '$25.60')")

        # Instance targeting validation
        # For spot bids (with auction_id), instance_type is also required by the API
        if self.auction_id and not self.instance_type:
            raise BidValidationError(
                "When auction_id is provided, instance_type is also required for spot bids"
            )
        if not self.auction_id and not self.instance_type:
            raise BidValidationError(
                "Must specify instance_type (and optionally auction_id for spot instances)"
            )

    def to_api_payload(self) -> dict[str, Any]:
        """Convert to Mithril API payload format.

        Returns:
            Dict ready for API submission
        """
        # Build launch specification
        # Extract volume IDs from volume attachment specs
        volume_ids = [vol["volume_id"] for vol in self.volumes] if self.volumes else []

        launch_spec = {
            "ssh_keys": self.ssh_keys,
            "startup_script": self.startup_script,
            "volumes": volume_ids,  # Mithril API expects list of volume IDs, not attachment specs
        }

        # Build base payload
        payload = {
            "project": self.project_id,
            "region": self.region,
            "name": self.name,
            "instance_quantity": self.instance_quantity,
            "limit_price": self.limit_price,
            "launch_specification": launch_spec,
        }

        # Add instance targeting
        payload["instance_type"] = self.instance_type
        if self.auction_id:
            payload["auction_id"] = self.auction_id

        return payload


class BidBuilder:
    """Builds bid specifications from task configurations."""

    @staticmethod
    def build_specification(
        config: TaskConfig,
        project_id: str,
        region: str,
        auction_id: str | None = None,
        instance_type_id: str | None = None,
        ssh_keys: list[str] | None = None,
        startup_script: str = "",
        volume_attachments: list[dict[str, Any]] | None = None,
    ) -> BidSpecification:
        """Build a bid specification from task config and resolved components.

        Args:
            config: Task configuration
            project_id: Resolved project ID
            region: Target region
            auction_id: Optional auction ID for spot instances
            instance_type_id: Optional instance type ID for on-demand
            ssh_keys: List of SSH key IDs
            startup_script: Complete startup script
            volume_attachments: Volume attachment specifications

        Returns:
            Complete BidSpecification

        Raises:
            BidValidationError: If parameters are invalid
        """
        # Determine limit price based on priority or explicit setting
        if config.max_price_per_hour is not None:
            # Explicit limit price takes precedence
            limit_price = f"${config.max_price_per_hour:.2f}"
        else:
            # Use priority tier with centralized pricing
            tier = config.priority

            # Use config's limit_prices which now comes from centralized pricing module
            # The config object should have limit_prices from MithrilConfig
            pricing_table = getattr(config, "limit_prices", None)
            if pricing_table is None:
                # Fallback to importing directly if config doesn't have it
                from flow._internal import pricing

                pricing_table = pricing.DEFAULT_PRICING

            # Use centralized pricing calculation
            from flow._internal import pricing

            gpu_type, gpu_count = pricing.extract_gpu_info(config.instance_type)

            # Get prices for this GPU type
            gpu_prices = pricing_table.get(gpu_type, pricing_table.get("default", {}))
            per_gpu_price = gpu_prices.get(tier, gpu_prices.get("med", 4.0))

            # Calculate total price: per-GPU price * number of GPUs
            total_price = per_gpu_price * gpu_count
            limit_price = f"${total_price:.2f}"

        # Ensure we have instance targeting
        if not auction_id and not instance_type_id:
            raise BidValidationError("Either auction_id or instance_type_id must be provided")

        return BidSpecification(
            project_id=project_id,
            region=region,
            name=config.name,
            instance_quantity=config.num_instances,
            limit_price=limit_price,
            auction_id=auction_id,
            instance_type=instance_type_id,
            ssh_keys=ssh_keys or [],
            startup_script=startup_script,
            volumes=volume_attachments or [],
        )

    @staticmethod
    def format_volume_attachment(
        volume_id: str, mount_path: str, mode: str = "rw"
    ) -> dict[str, Any]:
        """Format a volume attachment specification.

        Args:
            volume_id: ID of the volume to attach
            mount_path: Path to mount the volume
            mode: Access mode (rw or ro)

        Returns:
            Volume attachment dict
        """
        return {
            "volume_id": volume_id,
            "mount_path": mount_path,
            "mode": mode,
        }
