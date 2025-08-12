"""Task assembly service for Mithril provider.

This module encapsulates the logic for constructing Flow ``Task`` objects from
Mithril bid data, including status mapping, instance-type name resolution,
SSH destination parsing, price parsing, and optional enrichment with market
pricing. Extracted from the provider facade for testability and clarity.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from flow._internal.io.http_interfaces import IHttpClient
from flow.api.models import Task, TaskConfig, TaskStatus
from flow.providers.mithril.core.constants import (
    DEFAULT_REGION,
    DEFAULT_SSH_PORT,
    DEFAULT_SSH_USER,
    INSTANCE_TYPE_MAPPINGS,
    STATUS_MAPPINGS,
)
from flow.providers.mithril.domain.instances import InstanceService
from flow.providers.mithril.domain.pricing import PricingService


class TaskService:
    """Builds ``Task`` objects from Mithril bid dictionaries."""

    def __init__(
        self,
        http: IHttpClient,
        pricing: PricingService,
        instances: InstanceService,
        *,
        default_region: str = DEFAULT_REGION,
        default_ssh_user: str = DEFAULT_SSH_USER,
        default_ssh_port: int = DEFAULT_SSH_PORT,
    ) -> None:
        self._http = http
        self._pricing = pricing
        self._instances = instances
        self._default_region = default_region
        self._default_ssh_user = default_ssh_user
        self._default_ssh_port = default_ssh_port

    def build_task(
        self,
        bid_data: dict[str, Any],
        *,
        config: TaskConfig | None = None,
        fetch_instance_details: bool = False,
    ) -> Task:
        task_id = bid_data.get("fid", "")

        # Name resolution
        bid_name = bid_data.get("name", "")
        if bid_name:
            name = bid_name
        elif config and config.name:
            name = config.name
        else:
            name = f"task-{task_id[:8]}" if len(task_id) > 8 else f"task-{task_id}"

        status = self._map_mithril_status_to_enum(bid_data.get("status", "pending"))

        # Timestamps
        # created_at may be datetime or ISO string; handle both
        if bid_data.get("created_at"):
            try:
                if isinstance(bid_data["created_at"], datetime):
                    created_at = bid_data["created_at"]
                else:
                    created_at = datetime.fromisoformat(str(bid_data["created_at"]).replace("Z", "+00:00"))
            except Exception:
                created_at = datetime.now(timezone.utc)
        else:
            created_at = datetime.now(timezone.utc)
        started_at = None
        if bid_data.get("started_at"):
            try:
                started_at = (
                    bid_data["started_at"]
                    if isinstance(bid_data["started_at"], datetime)
                    else datetime.fromisoformat(str(bid_data["started_at"]).replace("Z", "+00:00"))
                )
            except Exception:
                started_at = None
        completed_at = None
        if bid_data.get("completed_at"):
            try:
                completed_at = (
                    bid_data["completed_at"]
                    if isinstance(bid_data["completed_at"], datetime)
                    else datetime.fromisoformat(str(bid_data["completed_at"]).replace("Z", "+00:00"))
                )
            except Exception:
                completed_at = None

        # Instance type
        instance_type_id = bid_data.get("instance_type", "")
        if instance_type_id:
            instance_type = self._get_instance_type_name(instance_type_id)
        elif config and config.instance_type:
            instance_type = config.instance_type
        else:
            instance_type = "unknown"

        # Instances count and region
        num_instances = bid_data.get(
            "instance_quantity",
            bid_data.get("num_instances", config.num_instances if config else 1),
        )
        region = bid_data.get("region", config.region if config else self._default_region)

        # Cost per hour
        cost_per_hour = self._determine_cost_per_hour(
            bid_data, status, instance_type_id, region, fetch_instance_details
        )

        # Total cost
        total_cost = None
        if started_at and (completed_at or status == TaskStatus.RUNNING):
            duration_hours = (
                (completed_at or datetime.now(timezone.utc)) - started_at
            ).total_seconds() / 3600
            try:
                cost_value = float(cost_per_hour.strip("$"))
            except Exception:
                cost_value = 0.0
            try:
                total_cost = f"${duration_hours * cost_value * (num_instances or 1):.2f}"
            except Exception:
                total_cost = None

        # SSH info
        ssh_host = None
        ssh_port = self._default_ssh_port
        ssh_command = None
        instances = bid_data.get("instances", [])
        instance_created_at = None

        if instances and isinstance(instances, list) and instances[0]:
            first = instances[0]
            if isinstance(first, str):
                if fetch_instance_details:
                    inst_data = self._fetch_instance_details(first)
                    if inst_data:
                        instances[0] = inst_data
                        ssh_destination = inst_data.get("ssh_destination")
                        if ssh_destination:
                            ssh_host, ssh_port = self._parse_ssh_destination(ssh_destination)
                        if inst_data.get("created_at"):
                            try:
                                instance_created_at = datetime.fromisoformat(
                                    inst_data["created_at"].replace("Z", "+00:00")
                                )
                            except Exception:
                                instance_created_at = None
            elif isinstance(first, dict):
                ssh_destination = first.get("ssh_destination")
                if ssh_destination:
                    ssh_host, ssh_port = self._parse_ssh_destination(ssh_destination)
                else:
                    public_ip = first.get("public_ip")
                    if public_ip:
                        ssh_host = public_ip
                        ssh_port = self._default_ssh_port

                if first.get("created_at"):
                    try:
                        instance_created_at = datetime.fromisoformat(
                            first["created_at"].replace("Z", "+00:00")
                        )
                    except Exception:
                        instance_created_at = None

            if ssh_host:
                ssh_command = f"ssh -p {ssh_port} {self._default_ssh_user}@{ssh_host}"

        # Provider metadata
        provider_metadata: dict[str, Any] = {
            "provider": "mithril",
            "bid_id": task_id,
            "bid_status": bid_data.get("status", "unknown"),
            "instance_type_id": instance_type_id,
            "limit_price": bid_data.get("limit_price"),
        }

        # Attach origin hint for downstream UX (CLI vs SDK)
        try:
            from flow.utils.origin import detect_origin as _detect_origin

            provider_metadata["origin"] = _detect_origin()
        except Exception:
            pass

        # Price competitiveness for pending bids
        if status == TaskStatus.PENDING and instance_type_id and region and fetch_instance_details:
            try:
                market_price = self._pricing.get_current_market_price(instance_type_id, region)
                if market_price:
                    provider_metadata["market_price"] = market_price
                    bid_val = self._pricing.parse_price(str(bid_data.get("limit_price", "")))
                    if bid_val and market_price:
                        if bid_val < market_price:
                            diff = market_price - bid_val
                            provider_metadata["price_competitiveness"] = "below_market"
                            provider_metadata["price_diff"] = diff
                            provider_metadata["price_message"] = (
                                f"Your bid is ${diff:.2f}/hour below market price"
                            )
                        elif bid_val > market_price * 1.2:
                            diff = bid_val - market_price
                            provider_metadata["price_competitiveness"] = "above_market"
                            provider_metadata["price_diff"] = diff
                            provider_metadata["price_message"] = (
                                f"Your bid is ${diff:.2f}/hour above market price"
                            )
                        else:
                            provider_metadata["price_competitiveness"] = "at_market"
                            provider_metadata["price_message"] = (
                                "Your bid is competitive with market price"
                            )
            except Exception:
                pass

        # Instance-level state
        if instances and isinstance(instances, list) and instances[0]:
            first = instances[0]
            if isinstance(first, dict):
                inst_status = first.get("status", "")
                if inst_status:
                    provider_metadata["instance_status"] = inst_status

        # Console link
        from flow.links import WebLinks
        provider_metadata["web_console_url"] = WebLinks.instances_spot()

        task = Task(
            task_id=task_id,
            name=name,
            status=status,
            config=config,
            created_at=created_at,
            started_at=started_at,
            completed_at=completed_at,
            created_by=bid_data.get("created_by"),
            instance_created_at=instance_created_at,
            instance_type=instance_type,
            num_instances=num_instances,
            region=region,
            cost_per_hour=cost_per_hour,
            total_cost=total_cost,
            ssh_host=ssh_host,
            ssh_port=ssh_port,
            ssh_command=ssh_command,
            instances=[
                inst.get("fid", "") if isinstance(inst, dict) else str(inst)
                for inst in (instances or [])
            ],
            message=bid_data.get("message"),
            provider_metadata=provider_metadata,
        )

        return task

    # ------------------------- helpers -------------------------

    def _fetch_instance_details(self, instance_id: str) -> dict[str, Any] | None:
        try:
            return self._instances.get_instance(instance_id)
        except Exception:
            return None

    def _map_mithril_status_to_enum(self, mithril_status: str) -> TaskStatus:
        if not mithril_status:
            return TaskStatus.PENDING
        normalized = mithril_status.lower().strip()
        mapped = STATUS_MAPPINGS.get(normalized)
        if mapped:
            return TaskStatus[mapped]
        if "alloc" in normalized:
            return TaskStatus.RUNNING
        if "termin" in normalized or "cancel" in normalized:
            return TaskStatus.CANCELLED
        if "fail" in normalized or "error" in normalized:
            return TaskStatus.FAILED
        if "complete" in normalized or "success" in normalized:
            return TaskStatus.COMPLETED
        if "open" in normalized:
            return TaskStatus.PENDING
        return TaskStatus.PENDING

    def _determine_cost_per_hour(
        self,
        bid_data: dict[str, Any],
        status: TaskStatus,
        instance_type_id: str,
        region: str,
        fetch_details: bool,
    ) -> str:
        if (
            status in [TaskStatus.RUNNING, TaskStatus.COMPLETED]
            and instance_type_id
            and region
            and fetch_details
        ):
            try:
                market_price = self._pricing.get_current_market_price(instance_type_id, region)
                if market_price:
                    return f"${market_price:.2f}"
            except Exception:
                pass
        limit_price = bid_data.get("limit_price", "$0")
        return limit_price if isinstance(limit_price, str) else f"${limit_price}"

    def _parse_ssh_destination(self, ssh_destination: str | None) -> tuple[str | None, int]:
        if not ssh_destination:
            return None, self._default_ssh_port
        parts = ssh_destination.split(":")
        host = parts[0]
        port = int(parts[1]) if len(parts) > 1 else self._default_ssh_port
        return host, port

    def _is_more_specific_type(self, type1: str, type2: str) -> bool:
        if "h100" in type1.lower() and "h100" in type2.lower():
            if type1.lower() == "8xh100":
                return True
            if type2.lower() == "8xh100":
                return False
        import re as _re

        m1 = _re.match(r"(\d+)x(.+)", type1.lower())
        m2 = _re.match(r"(\d+)x(.+)", type2.lower())
        if m1 and not m2:
            return True
        if m2 and not m1:
            return False
        if m1 and m2:
            c1, c2 = int(m1.group(1)), int(m2.group(1))
            if c1 != c2:
                return c1 > c2
        return False

    def _get_instance_type_name(self, instance_id: str) -> str:
        reverse: dict[str, str] = {}
        for name, fid in INSTANCE_TYPE_MAPPINGS.items():
            if fid not in reverse or self._is_more_specific_type(name, reverse[fid]):
                reverse[fid] = name
        if instance_id in reverse:
            return reverse[instance_id]

        upper = instance_id.upper()
        gpu_patterns: list[tuple[str, list[str]]] = [
            ("A100", ["A100", "AMPERE"]),
            ("H100", ["H100", "HOPPER"]),
            ("A10", ["A10"]),
            ("V100", ["V100", "VOLTA"]),
            ("T4", ["T4", "TURING"]),
            ("L4", ["L4"]),
            ("A40", ["A40"]),
        ]
        for gpu_name, patterns in gpu_patterns:
            if any(p in upper for p in patterns):
                return f"GPU-{gpu_name}"
        if instance_id.startswith(("it_", "IT_")):
            return "GPU"
        return instance_id
