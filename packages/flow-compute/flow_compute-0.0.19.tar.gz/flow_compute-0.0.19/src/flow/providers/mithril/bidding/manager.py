"""Bid management with support for partial fulfillment.

Bid lifecycle management including:
- Single all-or-nothing bids
- Chunked bids for partial fulfillment
- Custom startup script per chunk
"""

import logging
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from flow.api.models import TaskConfig
from flow._internal.io.http_interfaces import IHttpClient
from flow.errors import FlowError

logger = logging.getLogger(__name__)


class BidSubmissionError(FlowError):
    """Error during bid submission."""

    pass


class BidRequest(BaseModel):
    """Request for submitting a bid."""

    model_config = ConfigDict(frozen=True)

    auction_id: str = Field(..., description="Auction ID to bid on")
    instance_type_id: str = Field(..., description="Instance type identifier")
    quantity: int = Field(..., ge=1, description="Number of instances requested")
    max_price_per_hour: float = Field(..., ge=0, description="Maximum price per hour in dollars")
    task_name: str = Field(..., description="Name for the task")
    ssh_keys: List[str] = Field(..., description="SSH public keys for access")
    startup_script: str = Field(..., description="Startup script to run on instances")
    disk_attachments: List[Dict[str, Any]] = Field(
        default_factory=list, description="Disk attachments"
    )

    # Partial fulfillment options
    allow_partial: bool = Field(False, description="Allow partial fulfillment")
    min_quantity: int = Field(1, ge=1, description="Minimum acceptable quantity")
    chunk_size: Optional[int] = Field(
        None, ge=1, description="Size of chunks for partial fulfillment"
    )


class BidResult(BaseModel):
    """Result of a bid submission."""

    model_config = ConfigDict(frozen=True)

    bid_id: str = Field(..., description="Unique bid identifier")
    quantity_fulfilled: int = Field(..., ge=0, description="Number of instances fulfilled")
    instances: List[str] = Field(default_factory=list, description="Instance IDs")

    @property
    def is_fully_fulfilled(self) -> bool:
        """Check if all requested instances were fulfilled."""
        return len(self.instances) == self.quantity_fulfilled


class BidManager:
    """Manages bid submission with partial fulfillment support."""

    def __init__(self, http_client: IHttpClient):
        """Initialize bid manager.

        Args:
            http_client: HTTP client for API requests
        """
        self.http = http_client

    def submit_bid(
        self,
        request: BidRequest,
        startup_script_customizer: Optional[Callable[[int, str], str]] = None,
    ) -> List[BidResult]:
        """Submit bid with optional partial fulfillment.

        Args:
            request: Bid request parameters
            startup_script_customizer: Optional function to customize startup script per chunk

        Returns:
            List of bid results (one per chunk if using partial fulfillment)
        """
        if request.allow_partial and request.chunk_size:
            return self._submit_chunked_bids(request, startup_script_customizer)
        else:
            result = self._submit_single_bid(request)
            return [result]

    def _submit_single_bid(self, request: BidRequest) -> BidResult:
        """Submit a single all-or-nothing bid."""
        payload = {
            "auction_id": request.auction_id,
            "instance_type": request.instance_type_id,
            "quantity": request.quantity,
            "max_price": int(request.max_price_per_hour * 100),  # Convert to cents
            "task_name": request.task_name,
            "ssh_keys": request.ssh_keys,
            "startup_script": request.startup_script,
            "disk_attachments": request.disk_attachments,
        }

        try:
            response = self.http.request(
                method="POST",
                url="/bids",
                json=payload,
            )

            bid_id = response.get("bid_id", response.get("fid"))
            instances = response.get("instances", [])

            return BidResult(
                bid_id=bid_id,
                quantity_fulfilled=len(instances),
                instances=[inst.get("fid") for inst in instances],
            )

        except Exception as e:
            raise BidSubmissionError(f"Failed to submit bid: {e}") from e

    def _submit_chunked_bids(
        self,
        request: BidRequest,
        startup_script_customizer: Optional[Callable[[int, str], str]] = None,
    ) -> List[BidResult]:
        """Submit multiple smaller bids for partial fulfillment."""
        if not request.chunk_size or request.chunk_size <= 0:
            raise ValueError("Invalid chunk size for partial fulfillment")

        results = []
        remaining = request.quantity
        chunk_index = 0

        while remaining > 0:
            # Determine chunk size
            chunk_quantity = min(request.chunk_size, remaining)

            # Customize startup script if function provided
            if startup_script_customizer:
                chunk_script = startup_script_customizer(chunk_index, request.startup_script)
            else:
                # Default: add chunk index as environment variable
                chunk_script = f"export CHUNK_INDEX={chunk_index}\n{request.startup_script}"

            # Create chunk request
            chunk_request = BidRequest(
                auction_id=request.auction_id,
                instance_type_id=request.instance_type_id,
                quantity=chunk_quantity,
                max_price_per_hour=request.max_price_per_hour,
                task_name=f"{request.task_name}-chunk-{chunk_index}",
                ssh_keys=request.ssh_keys,
                startup_script=chunk_script,
                disk_attachments=request.disk_attachments,
                allow_partial=False,  # Individual chunks are all-or-nothing
            )

            try:
                result = self._submit_single_bid(chunk_request)
                results.append(result)

                # Update remaining count
                remaining -= result.quantity_fulfilled

                # Stop if we got less than requested (partial fulfillment)
                if result.quantity_fulfilled < chunk_quantity:
                    logger.warning(
                        f"Chunk {chunk_index} only fulfilled {result.quantity_fulfilled} "
                        f"out of {chunk_quantity} requested"
                    )
                    break

            except Exception as e:
                logger.error(f"Failed to submit chunk {chunk_index}: {e}")
                # Stop on error if we have some successful bids
                if results:
                    break
                # Re-raise if this was the first chunk
                raise

            chunk_index += 1

        # Log summary
        total_fulfilled = sum(r.quantity_fulfilled for r in results)
        logger.info(
            f"Partial fulfillment complete: {total_fulfilled}/{request.quantity} instances "
            f"across {len(results)} bids"
        )

        return results

    def cancel_bid(self, bid_id: str) -> bool:
        """Cancel a bid if possible.

        Args:
            bid_id: ID of the bid to cancel

        Returns:
            True if cancelled successfully
        """
        try:
            self.http.request(
                method="DELETE",
                url=f"/v2/spot/bids/{bid_id}",
            )
            return True
        except Exception as e:
            logger.error(f"Failed to cancel bid {bid_id}: {e}")
            return False

    def create_request_from_config(
        self,
        config: TaskConfig,
        auction_id: str,
        instance_type_id: str,
        startup_script: str,
        disk_attachments: List[Dict[str, Any]],
        allow_partial: bool = False,
        chunk_size: Optional[int] = None,
    ) -> BidRequest:
        """Create bid request from task configuration.

        Args:
            config: Task configuration
            auction_id: Auction to bid on
            instance_type_id: Resolved instance type ID
            startup_script: Complete startup script
            disk_attachments: Volume attachments
            allow_partial: Whether to allow partial fulfillment
            chunk_size: Size of chunks for partial fulfillment

        Returns:
            BidRequest object
        """
        return BidRequest(
            auction_id=auction_id,
            instance_type_id=instance_type_id,
            quantity=config.num_instances,
            max_price_per_hour=config.max_price_per_hour or 100.0,  # Default $100/hr for h100x8
            task_name=config.name,
            ssh_keys=config.ssh_keys,
            startup_script=startup_script,
            disk_attachments=disk_attachments,
            allow_partial=allow_partial,
            min_quantity=1,
            chunk_size=chunk_size,
        )
