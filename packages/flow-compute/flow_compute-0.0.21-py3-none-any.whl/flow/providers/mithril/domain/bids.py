"""Bid submission and selection facade.

Unifies region selection, instance type resolution, and bid submission behind a
single service used by the provider facade.
"""

from __future__ import annotations

from typing import Any

from flow.api.models import TaskConfig
from flow.errors import ResourceNotAvailableError
from flow.providers.mithril.api.client import MithrilApiClient
from flow.providers.mithril.bidding.builder import BidBuilder
from flow.providers.mithril.core.models import Auction
from flow.providers.mithril.domain.pricing import PricingService
from flow.providers.mithril.domain.region import RegionSelector


class BidsService:
    def __init__(
        self,
        api: MithrilApiClient,
        region_selector: RegionSelector,
        pricing: PricingService,
        resolve_instance_type: callable,
        get_project_id: callable,
    ) -> None:
        self._api = api
        self._region_selector = region_selector
        self._pricing = pricing
        self._resolve_instance_type = resolve_instance_type
        self._get_project_id = get_project_id

    def select_region_and_instance(
        self, config: TaskConfig, instance_type: str
    ) -> tuple[str, str, Auction | None]:
        # Resolve instance type FID
        instance_type_id = self._resolve_instance_type(instance_type)
        # Check availability across regions
        availability = self._region_selector.check_availability(instance_type_id)
        # Select best region
        selected_region = self._region_selector.select_best_region(availability, config.region)
        if not selected_region:
            regions_checked = sorted(availability.keys())
            raise ResourceNotAvailableError(
                f"No available regions for instance type {instance_type}",
                suggestions=[
                    f"Checked regions: {', '.join(regions_checked)}",
                    "Try a different instance type",
                    "Increase your max price limit",
                    "Check back later for availability",
                ],
            )
        auction = availability.get(selected_region)
        return selected_region, instance_type_id, auction

    def submit_bid(
        self,
        config: TaskConfig,
        *,
        region: str,
        instance_type_id: str,
        project_id: str | None = None,
        ssh_keys: list[str] | None = None,
        startup_script: str | None = None,
        volume_attachments: list[dict[str, Any]] | None = None,
        auction_id: str | None = None,
    ) -> Any:
        bid_spec = BidBuilder.build_specification(
            config=config,
            project_id=project_id or self._get_project_id(),
            region=region,
            auction_id=auction_id,
            instance_type_id=instance_type_id,
            ssh_keys=ssh_keys or [],
            startup_script=startup_script,
            volume_attachments=volume_attachments or [],
        )
        return self._api.create_bid(bid_spec.to_api_payload())
