"""Mithril API bridge adapter."""

from typing import Any

from flow.api import Flow
from flow.api.models import TaskConfig
from flow.bridge.base import BridgeAdapter


class MithrilAPIBridge(BridgeAdapter):
    """Bridge adapter for Mithril-specific API operations."""

    def __init__(self):
        """Initialize the Mithril API bridge."""
        self._flow = None

    @property
    def flow(self) -> Flow:
        """Lazy-load the Flow instance."""
        if self._flow is None:
            self._flow = Flow()
        return self._flow

    def get_capabilities(self) -> dict[str, Any]:
        """Return capabilities of the Mithril API adapter."""
        return {
            "description": "Mithril-specific API operations",
            "methods": {
                "list_spot_availability": {
                    "description": "List available spot instances with pricing",
                    "args": {},
                    "returns": "list of auction data",
                },
                "create_bid": {
                    "description": "Create a spot instance bid",
                    "args": {
                        "instance_type": "Instance type (e.g., 'a100', '2xa100')",
                        "region": "Specific region (optional)",
                        "ssh_key_path": "Path to SSH public key (optional)",
                    },
                    "returns": "bid ID",
                },
                "get_bid_status": {
                    "description": "Get bid and instance status",
                    "args": {"bid_id": "Bid ID to check"},
                    "returns": "bid status data",
                },
                "delete_bid": {
                    "description": "Cancel bid and terminate instance",
                    "args": {"bid_id": "Bid ID to delete"},
                    "returns": "bool (success)",
                },
                "list_bids": {
                    "description": "List active bids for project",
                    "args": {},
                    "returns": "list of bid data",
                },
                "ensure_ssh_key": {
                    "description": "Ensure SSH key is registered with project",
                    "args": {"public_key": "SSH public key content"},
                    "returns": "SSH key ID",
                },
            },
        }

    def list_spot_availability(self) -> list[dict[str, Any]]:
        """List available spot instances with pricing.

        Returns:
            List of auction data matching mithril-js format
        """
        # Get provider
        provider = self.flow.provider

        # Get spot availability using internal method
        from flow.providers.mithril.bidding.finder import SpotFinder

        finder = SpotFinder(provider)
        auctions = finder.find_spot_auctions()

        # Convert to mithril-js format
        result = []
        for auction in auctions:
            # Extract GPU count from instance type name
            gpu_count = 1  # Default
            if hasattr(auction, "instance_type_name"):
                name = auction.instance_type_name
                if "2x" in name:
                    gpu_count = 2
                elif "4x" in name:
                    gpu_count = 4
                elif "8x" in name:
                    gpu_count = 8

            result.append(
                {
                    "type": auction.instance_type_name,
                    "region": auction.region,
                    "gpu": gpu_count,
                    "price": f"${auction.last_instance_price:.2f}",
                    "available": auction.capacity,
                    "id": auction.auction_id,  # Include auction ID for create_bid
                }
            )

        return result

    def create_bid(
        self,
        instance_type: str,
        region: str | None = None,
        ssh_key_path: str | None = None,
    ) -> str:
        """Create a spot instance bid.

        Args:
            instance_type: Instance type (e.g., 'a100', '2xa100')
            region: Specific region (optional)
            ssh_key_path: Path to SSH public key (optional)

        Returns:
            Bid ID
        """
        # Create minimal task config for spot bid
        config = TaskConfig(
            name=f"mithril-{instance_type}",
            instance_type=instance_type,
            command=["sleep", "infinity"],  # Keep instance running
            ssh_keys=[],  # Will be populated by Flow
        )

        # Set region if specified
        if region:
            config.region = region

        # Submit task
        task = self.flow.run(config)

        # Return task ID (which is the bid ID in Mithril)
        return task.task_id

    def get_bid_status(self, bid_id: str) -> dict[str, Any]:
        """Get bid and instance status.

        Args:
            bid_id: Bid ID to check

        Returns:
            Bid status data matching mithril-js format
        """
        try:
            # Get task (which represents the bid)
            task = self.flow.get_task(bid_id)

            # Get instances for SSH info
            instances = task.get_instances() if hasattr(task, "get_instances") else []

            # Extract instance info
            instance_data = {}
            if instances:
                inst = instances[0]
                instance_data = {
                    "status": inst.status,
                    "public_ip": getattr(inst, "ssh_host", None),
                }

            return {
                "id": bid_id,
                "type": task.instance_type or "N/A",
                "status": self._map_task_status(task.status),
                "region": task.region or "N/A",
                "ip": instance_data.get("public_ip"),
                "created": task.created_at.isoformat() if task.created_at else None,
                "instance": instance_data,
            }
        except Exception as e:
            # Handle not found
            if "not found" in str(e).lower():
                return {"id": bid_id, "status": "NOT_FOUND"}
            raise

    def delete_bid(self, bid_id: str) -> bool:
        """Cancel bid and terminate instance.

        Args:
            bid_id: Bid ID to delete

        Returns:
            True if deleted, False if not found
        """
        try:
            self.flow.cancel(bid_id)
            return True
        except Exception as e:
            if "not found" in str(e).lower():
                return False
            raise

    def list_bids(self) -> list[dict[str, Any]]:
        """List active bids for project.

        Returns:
            List of bid data matching mithril-js format
        """
        # List recent tasks
        tasks = self.flow.list_tasks(limit=100)

        # Filter to active ones (matching mithril-js logic)
        active_statuses = ["pending", "running"]
        active_tasks = [t for t in tasks if t.status.lower() in active_statuses]

        # Convert to mithril-js format
        result = []
        for task in active_tasks:
            result.append(
                {
                    "id": task.task_id,
                    "type": task.instance_type or "N/A",
                    "status": self._map_task_status(task.status),
                    "region": task.region or "N/A",
                }
            )

        return result

    def ensure_ssh_key(self, public_key: str) -> str:
        """Ensure SSH key is registered with project.

        Args:
            public_key: SSH public key content

        Returns:
            SSH key ID
        """
        # Get provider to access SSH key management
        provider = self.flow.provider

        # Delegate to provider's SSH key manager; scope to current project
        ssh_manager = getattr(provider, "ssh_key_manager", None)
        if ssh_manager is None:
            from flow.providers.mithril.resources.ssh import SSHKeyManager
            ssh_manager = SSHKeyManager(provider._api_client, getattr(provider, "project_id", None))
        else:
            try:
                if getattr(ssh_manager, "project_id", None) is None:
                    ssh_manager.project_id = provider.project_id
            except Exception:
                pass

        # Ensure the key is present; manager should dedupe by fingerprint if supported
        key_id = ssh_manager.ensure_public_key(public_key, name="mithril-key")
        return key_id

    def _map_task_status(self, status: str) -> str:
        """Map Flow task status to mithril-js status.

        Args:
            status: Flow task status

        Returns:
            Mithril-js compatible status
        """
        status_lower = status.lower()

        # Map to mithril expected statuses
        if status_lower == "pending":
            return "PENDING"
        elif status_lower in ["preparing", "running"]:
            return "RUNNING"
        elif status_lower == "completed":
            return "TERMINATED"
        elif status_lower == "failed":
            return "FAILED"
        elif status_lower == "cancelled":
            return "TERMINATED"
        else:
            return status.upper()
