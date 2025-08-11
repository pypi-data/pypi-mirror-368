"""Instance-related helpers and services for the Mithril provider.

Provides instance fetch and normalization utilities and an orchestration
method to build `Instance` models for a task's bid.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from flow._internal.io.http_interfaces import IHttpClient
from flow.api.models import Instance, InstanceStatus
from flow.errors import ResourceNotFoundError
from flow.providers.mithril.adapters.models import MithrilAdapter
from flow.providers.mithril.core.models import MithrilBid, MithrilInstance


class InstanceService:
    """Service to fetch and adapt instance data for tasks."""

    def __init__(self, http: IHttpClient, get_project_id: Callable[[], str]) -> None:
        self._http = http
        self._get_project_id = get_project_id

    def get_instance(self, instance_id: str) -> dict:
        """Fetch detailed instance information by ID."""
        # Prefer v2/spot/instances; fall back to v2/instances when shape differs
        try:
            response = self._http.request(
                method="GET", url="/v2/spot/instances", params={"id": instance_id}
            )
            instances = response.get("data", []) if isinstance(response, dict) else []
        except Exception:
            instances = []

        if not instances:
            # Fallback
            response = self._http.request(
                method="GET",
                url="/v2/instances",
                params={"fid": instance_id, "project": self._get_project_id()},
            )
            instances = response.get("data", []) if isinstance(response, dict) else []
        if not instances:
            raise ResourceNotFoundError(f"Instance {instance_id} not found")
        return instances[0]

    def list_for_bid(self, bid: dict, task_id: str) -> list[Instance]:
        """Build `Instance` models for all instance IDs in the bid."""
        instances: list[Instance] = []
        instance_ids = bid.get("instances", [])
        for instance_id in instance_ids:
            if isinstance(instance_id, str):
                try:
                    data = self.get_instance(instance_id)
                    instance = MithrilAdapter.mithril_instance_to_instance(
                        MithrilInstance(**data), MithrilBid(**bid)
                    )
                    instances.append(instance)
                except Exception:
                    instances.append(
                        Instance(
                            instance_id=instance_id,
                            task_id=task_id,
                            status=InstanceStatus.PENDING,
                            created_at=datetime.now(),
                        )
                    )
            elif isinstance(instance_id, dict):
                try:
                    instance = MithrilAdapter.mithril_instance_to_instance(
                        MithrilInstance(**instance_id), MithrilBid(**bid)
                    )
                    instances.append(instance)
                except Exception:
                    # Skip malformed instance dicts gracefully
                    continue
        return instances
