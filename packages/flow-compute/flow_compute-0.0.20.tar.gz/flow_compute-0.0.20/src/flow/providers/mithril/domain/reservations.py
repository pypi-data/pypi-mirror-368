from __future__ import annotations

from datetime import timedelta
from typing import Any

from flow.api.models import Reservation, ReservationSpec, ReservationStatus


class ReservationsService:
    """High-level service for Mithril reservations.

    Translates provider-agnostic ReservationSpec to Mithril API payloads
    and maps responses back to Reservation objects.
    """

    def __init__(self, api_client) -> None:
        self._api = api_client

    @staticmethod
    def _to_api_payload(spec: ReservationSpec) -> dict[str, Any]:
        # Mithril expected fields (align with latest API):
        # name, project, region, instance_type, quantity, start_time, duration_hours,
        # launch_specification: { ssh_keys, startup_script, volumes }
        launch_spec: dict[str, Any] = {
            "ssh_keys": spec.ssh_keys,
            "startup_script": spec.startup_script or "",
            "volumes": spec.volumes,
        }
        return {
            "name": spec.name,
            "project": spec.project_id,
            "region": spec.region,
            "instance_type": spec.instance_type,
            "instance_quantity": spec.quantity,
            "start_time": spec.start_time_utc.isoformat(),
            "duration_hours": spec.duration_hours,
            "launch_specification": launch_spec,
        }

    @staticmethod
    def _status_from_api(raw: str) -> ReservationStatus:
        v = (raw or "").lower()
        if v in {"scheduled", "pending"}:
            return ReservationStatus.SCHEDULED
        if v in {"active", "running", "allocated"}:
            return ReservationStatus.ACTIVE
        if v in {"expired", "completed"}:
            return ReservationStatus.EXPIRED
        return ReservationStatus.FAILED

    def _from_api(self, data: dict[str, Any]) -> Reservation:
        # API may be flat or under 'data'
        d = data.get("data", data) if isinstance(data, dict) else {}
        rid = d.get("fid") or d.get("id") or d.get("reservation_id")
        start_iso = d.get("start_time") or d.get("start_time_utc")
        start = None
        end = None
        if start_iso:
            try:
                # Support 'Z'
                start = start_iso.replace("Z", "+00:00")
                from datetime import datetime

                start = datetime.fromisoformat(start)
            except Exception:
                start = None
        duration_h = d.get("duration_hours")
        if start and isinstance(duration_h, (int, float)):
            end = start + timedelta(hours=float(duration_h))

        return Reservation(
            reservation_id=rid,
            name=d.get("name"),
            status=self._status_from_api(d.get("status", "")),
            instance_type=d.get("instance_type") or d.get("instance_type_id") or "",
            region=d.get("region") or "",
            quantity=d.get("instance_quantity") or d.get("quantity") or 1,
            start_time_utc=start,
            end_time_utc=end,
            price_total_usd=None,
            provider_metadata=d,
        )

    # ------------- Public API -------------
    def create(self, spec: ReservationSpec) -> Reservation:
        payload = self._to_api_payload(spec)
        resp = self._api.create_reservation(payload)
        return self._from_api(resp)

    def list(self, params: dict[str, Any] | None = None) -> list[Reservation]:
        resp = self._api.list_reservations(params or {})
        data = resp.get("data", resp)
        items = data if isinstance(data, list) else []
        return [self._from_api(it) for it in items]

    def get(self, reservation_id: str) -> Reservation:
        resp = self._api.get_reservation(reservation_id)
        return self._from_api(resp)
