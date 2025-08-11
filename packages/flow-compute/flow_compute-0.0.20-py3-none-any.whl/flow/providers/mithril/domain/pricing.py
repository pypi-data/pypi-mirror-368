"""Pricing-related helpers and services for the Mithril provider.

Centralizes price parsing, current market price queries, and enhanced
validation error construction for insufficient bid prices.
"""

from __future__ import annotations

from flow._internal.io.http_interfaces import IHttpClient
from flow.errors import InsufficientBidPriceError, ValidationAPIError


class PricingService:
    """Service for price parsing and price-aware recommendations.

    Args:
        http: HTTP client bound to the Mithril API base URL.
    """

    def __init__(self, http: IHttpClient) -> None:
        self._http = http

    def parse_price(self, price_str: str | None) -> float:
        """Parse a price string like "$10.00" to a float.

        Returns 0.0 for empty or malformed values.
        """
        if not price_str:
            return 0.0
        clean = price_str.strip().lstrip("$").replace(",", "").strip()
        try:
            return float(clean)
        except (ValueError, TypeError):
            return 0.0

    def get_current_market_price(self, instance_type_id: str, region: str) -> float | None:
        """Fetch current market price for an instance type in a region.

        Returns:
            The current market price or None if unavailable.
        """
        try:
            auctions = self._http.request(
                method="GET",
                url="/v2/spot/availability",
                params={"instance_type": instance_type_id, "region": region},
            )

            if auctions and isinstance(auctions, list):
                # Prefer exact match, otherwise first item
                match = None
                for a in auctions:
                    if a.get("instance_type") == instance_type_id and a.get("region") == region:
                        match = a
                        break
                candidate = match or auctions[0]
                return self.parse_price(candidate.get("last_instance_price", ""))
        except Exception:
            return None
        return None

    def is_price_validation_error(self, error: ValidationAPIError) -> bool:
        """Detect whether a ValidationAPIError is price-related."""
        if not getattr(error, "validation_errors", None):
            return False
        price_keywords = ["price", "bid", "limit_price", "minimum", "insufficient"]
        for item in error.validation_errors:
            msg = str(item.get("msg", "")).lower()
            loc = item.get("loc", [])
            if any("price" in str(f).lower() for f in loc):
                return True
            if any(k in msg for k in price_keywords):
                return True
        return False

    def enhance_price_error(
        self,
        error: ValidationAPIError,
        *,
        instance_type_id: str,
        region: str,
        attempted_price: float | None,
        instance_display_name: str,
    ) -> InsufficientBidPriceError:
        """Augment a price validation error with current pricing and advice."""
        try:
            auctions = self._http.request(
                method="GET",
                url="/v2/spot/availability",
                params={"instance_type": instance_type_id, "region": region},
            )
            if not auctions:
                raise error
            auction = None
            if len(auctions) == 1:
                auction = auctions[0]
            else:
                for a in auctions:
                    if a.get("region") == region and a.get("instance_type") == instance_type_id:
                        auction = a
                        break
            auction = auction or auctions[0]
            current_price = self.parse_price(auction.get("last_instance_price"))
            min_bid_price = self.parse_price(auction.get("min_bid_price"))
            effective = max(v for v in [current_price, min_bid_price] if v is not None)
            recommended = effective * 1.5
            message = (
                f"Bid price ${attempted_price:.2f}/hour is too low for {instance_display_name} "
                f"in {region}. Current spot price is ${effective:.2f}/hour."
            )
            return InsufficientBidPriceError(
                message=message,
                current_price=effective,
                min_bid_price=min_bid_price or None,
                recommended_price=recommended,
                instance_type=instance_display_name,
                region=region,
                response=getattr(error, "response", None),
            )
        except Exception:
            # On failure to enhance, re-raise original
            raise error
