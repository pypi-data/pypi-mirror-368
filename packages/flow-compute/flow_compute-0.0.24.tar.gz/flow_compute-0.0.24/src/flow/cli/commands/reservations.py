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
        @click.option("--with-slurm", is_flag=True, help="Provision Slurm controller/workers for this reservation")
        @click.option("--slurm-version", default=None, help="Requested Slurm version (e.g., 25.05.1)")
        @click.option("--json", "output_json", is_flag=True, help="Output JSON")
        def create(
            instance_type: str,
            region: str | None,
            quantity: int,
            start_time: str,
            duration_hours: int,
            name: str | None,
            ssh_keys: tuple[str, ...],
            with_slurm: bool,
            slurm_version: str | None,
            output_json: bool,
        ):
            try:
                start = _dt.fromisoformat(start_time.replace("Z", "+00:00"))
            except Exception as e:
                self.handle_error(f"Invalid --start: {e}")
                return

            flow = Flow()
            # Capability gate: require provider reservations support
            try:
                caps = flow.provider.get_capabilities()
                if not getattr(caps, "supports_reservations", False):
                    console.print("Reservations are not supported by the current provider (demo/mock mode).")
                    try:
                        self.show_next_actions(
                            [
                                "Switch provider: flow init --provider mithril",
                                "Schedule via run: flow run training.yaml --allocation reserved --start <ISO> --duration <h>",
                            ]
                        )
                    except Exception:
                        pass
                    return
            except Exception:
                # If capability lookup fails, proceed and let provider error surface
                pass
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

            # Inject Slurm opt-in hint for startup provisioning
            if with_slurm:
                env = dict(config.env or {})
                env["_FLOW_WITH_SLURM"] = "1"
                if slurm_version:
                    env["_FLOW_SLURM_VERSION"] = slurm_version
                config = config.model_copy(update={"env": env})

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
                # Next steps
                try:
                    ref = rid or task.task_id
                    self.show_next_actions(
                        [
                            "List reservations: [accent]flow reservations list[/accent]",
                            f"Show details: [accent]flow reservations show {ref}[/accent]",
                            "Monitor tasks: [accent]flow status --all[/accent]",
                        ]
                    )
                except Exception:
                    pass

        @grp.command(name="list", help="List reservations")
        @click.option("--json", "output_json", is_flag=True, help="Output JSON")
        @click.option("--slurm-only", is_flag=True, help="Show only Slurm-enabled reservations")
        def list_cmd(output_json: bool, slurm_only: bool):
            flow = Flow()
            provider = flow.provider
            try:
                # Safe path: if provider lacks list_reservations, show a helpful message
                # Use prefetch cache for instant UX if available
                try:
                    from flow.cli.utils.prefetch import get_cached  # type: ignore

                    cached = get_cached("reservations")
                except Exception:
                    cached = None
                if hasattr(provider, "list_reservations"):
                    items = cached or provider.list_reservations()
                else:
                    console.print("Reservations are not supported by the current provider (demo/mock mode).")
                    try:
                        self.show_next_actions(
                            [
                                "Switch provider: flow init --provider mithril",
                                "Schedule a run: flow run training.yaml --allocation reserved --start <ISO> --duration <h>",
                            ]
                        )
                    except Exception:
                        pass
                    return
            except Exception as e:
                self.handle_error(e)
                return
            # Optionally filter to Slurm-enabled
            def _has_slurm(res) -> bool:
                meta = getattr(res, "provider_metadata", {}) or {}
                return bool(meta.get("slurm"))

            if slurm_only:
                items = [it for it in items if _has_slurm(it)]

            if output_json:
                console.print(json.dumps([getattr(it, "model_dump", lambda: it)() for it in items]))
            else:
                for it in items:
                    meta = getattr(it, "provider_metadata", {}) or {}
                    slurm = meta.get("slurm") or {}
                    slurm_tag = " [slurm]" if slurm else ""
                    console.print(
                        f"- {it.reservation_id}{slurm_tag} "
                        f"[{it.status.value if hasattr(it.status,'value') else it.status}] "
                        f"{it.instance_type} x{it.quantity} {it.region} start={it.start_time_utc}"
                    )
                # Next steps
                try:
                    self.show_next_actions(
                        [
                            "Create a reservation: [accent]flow reservations create --instance-type h100 --start 2025-01-01T00:00:00Z --duration 4[/accent]",
                            "Show a reservation: [accent]flow reservations show <reservation-id>[/accent]",
                        ]
                    )
                except Exception:
                    pass

        @grp.command(name="show", help="Show reservation details")
        @click.argument("reservation_id")
        @click.option("--json", "output_json", is_flag=True, help="Output JSON")
        def show_cmd(reservation_id: str, output_json: bool):
            flow = Flow()
            provider = flow.provider
            try:
                if not hasattr(provider, "get_reservation"):
                    console.print("Reservations are not supported by the current provider (demo/mock mode).")
                    return
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
                # Next steps
                try:
                    self.show_next_actions(
                        [
                            "List reservations: [accent]flow reservations list[/accent]",
                            "Monitor capacity: [accent]flow alloc --watch[/accent]",
                        ]
                    )
                except Exception:
                    pass

        return grp


command = ReservationsCommand()
