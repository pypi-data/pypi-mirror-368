from __future__ import annotations

import json
from datetime import datetime as _dt

import click

from flow.api.client import Flow
from flow.cli.commands.base import BaseCommand, console


class ReservationsCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "reservations"

    @property
    def help(self) -> str:
        return "Manage capacity reservations (create/list/show)"

    def get_command(self) -> click.Command:
        @click.group(name=self.name, help=self.help)
        def grp():
            pass

        @grp.command(name="create", help="Create a new reservation")
        @click.option("--instance-type", "instance_type", required=True)
        @click.option("--region", required=False)
        @click.option("--quantity", type=int, default=1)
        @click.option(
            "--start", "start_time", required=True, help="ISO8601 UTC e.g. 2025-01-31T18:00:00Z"
        )
        @click.option("--duration", "duration_hours", type=int, required=True)
        @click.option("--name", default=None)
        @click.option("--ssh-key", "ssh_keys", multiple=True)
        @click.option("--json", "output_json", is_flag=True, help="Output JSON")
        def create(
            instance_type: str,
            region: str | None,
            quantity: int,
            start_time: str,
            duration_hours: int,
            name: str | None,
            ssh_keys: tuple[str, ...],
            output_json: bool,
        ):
            try:
                start = _dt.fromisoformat(start_time.replace("Z", "+00:00"))
            except Exception as e:
                self.handle_error(f"Invalid --start: {e}")
                return

            flow = Flow()
            # Build a minimal TaskConfig to carry startup script env and num_instances
            from flow.api.models import TaskConfig

            cfg_updates = {
                "name": name or f"reservation-{instance_type}",
                "instance_type": instance_type,
                "num_instances": quantity,
                "ssh_keys": list(ssh_keys or ()),
                "allocation_mode": "reserved",
                "scheduled_start_time": start,
                "reserved_duration_hours": int(duration_hours),
            }
            if region:
                cfg_updates["region"] = region
            config = TaskConfig(**cfg_updates)

            # Use provider reserved path by calling run() with reserved config
            task = flow.run(config)
            rid = (
                task.provider_metadata.get("reservation", {}).get("reservation_id")
                if getattr(task, "provider_metadata", None)
                else None
            )
            if output_json:
                console.print(
                    json.dumps({"reservation_id": rid or task.task_id, "task_id": task.task_id})
                )
            else:
                console.print(f"Created reservation: [accent]{rid or task.task_id}[/accent]")

        @grp.command(name="list", help="List reservations")
        @click.option("--json", "output_json", is_flag=True, help="Output JSON")
        def list_cmd(output_json: bool):
            flow = Flow()
            provider = flow.provider
            try:
                items = provider.list_reservations()
            except Exception as e:
                self.handle_error(e)
                return
            if output_json:
                console.print(json.dumps([getattr(it, "model_dump", lambda: it)() for it in items]))
            else:
                for it in items:
                    console.print(
                        f"- {it.reservation_id} [{it.status.value if hasattr(it.status,'value') else it.status}] {it.instance_type} x{it.quantity} {it.region} start={it.start_time_utc}"
                    )

        @grp.command(name="show", help="Show reservation details")
        @click.argument("reservation_id")
        @click.option("--json", "output_json", is_flag=True, help="Output JSON")
        def show_cmd(reservation_id: str, output_json: bool):
            flow = Flow()
            provider = flow.provider
            try:
                res = provider.get_reservation(reservation_id)
            except Exception as e:
                self.handle_error(e)
                return
            if output_json:
                console.print(json.dumps(getattr(res, "model_dump", lambda: res)()))
            else:
                console.print(f"Reservation: [accent]{res.reservation_id}[/accent]")
                console.print(
                    f"  status={res.status} type={res.instance_type} qty={res.quantity} region={res.region}"
                )
                console.print(f"  start={res.start_time_utc} end={res.end_time_utc}")

        return grp


command = ReservationsCommand()
