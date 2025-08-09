"""Mithril auction and bidding subsystem.

This package implements the Mithril bidding system:
- Auction discovery and filtering
- Bid specification building
- Bid lifecycle management
"""

from .builder import BidBuilder, BidSpecification, BidValidationError
from .finder import AuctionCatalogError, AuctionCriteria, AuctionFinder, AuctionMatcher
from .manager import BidManager, BidRequest, BidResult, BidSubmissionError

__all__ = [
    # Builder
    "BidBuilder",
    "BidSpecification",
    "BidValidationError",
    # Finder
    "AuctionFinder",
    "AuctionCriteria",
    "AuctionMatcher",
    "AuctionCatalogError",
    # Manager
    "BidManager",
    "BidRequest",
    "BidResult",
    "BidSubmissionError",
]
