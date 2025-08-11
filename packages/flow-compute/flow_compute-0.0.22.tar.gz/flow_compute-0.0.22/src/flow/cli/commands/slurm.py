from __future__ import annotations

import json
import sys
from typing import Any

import click

from flow.api.client import Flow
from flow.cli.commands.base import BaseCommand, console


class SlurmCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "slurm"

    @property
    def help(self) -> str:
        return "Interact with Slurm on reservations (submit/status/cancel/ssh)"

    def get_command(self) -> click.Command:
        @click.group(name=self.name, help=self.help)
        def grp() -> None:
            pass

        def _get_slurm_meta(reservation_id: str) -> dict[str, Any]:
            flow = Flow()
            provider = flow.provider
            res = provider.get_reservation(reservation_id)
            meta = getattr(res, "provider_metadata", {}) or {}
            slurm = meta.get("slurm") or {}
            if not slurm:
                self.handle_error(
                    "Reservation is not Slurm-enabled. Recreate with --with-slurm or contact support."
                )
                raise click.Abort()
            return slurm

        @grp.command(name="submit", help="Submit a SLURM script to a reservation's Slurm cluster")
        @click.argument("reservation_id")
        @click.argument("script_path")
        @click.option("--env", "env_kv", multiple=True, help="Env KEY=VALUE to pass to job")
        @click.option("--account", default=None)
        @click.option("--partition", default=None)
        @click.option("--array", default=None)
        @click.option("--name", default=None)
        def submit_cmd(
            reservation_id: str,
            script_path: str,
            env_kv: tuple[str, ...],
            account: str | None,
            partition: str | None,
            array: str | None,
            name: str | None,
        ) -> None:
            try:
                slurm = _get_slurm_meta(reservation_id)
            except click.Abort:
                return

            try:
                content = open(script_path, "r", encoding="utf-8").read()
            except Exception as e:  # noqa: BLE001
                self.handle_error(e)
                return

            # Minimal slurmrestd payload with validated env
            env_dict: dict[str, Any] = {}
            if env_kv:
                for kv in env_kv:
                    if "=" not in kv:
                        self.handle_error(f"Invalid --env item '{kv}'. Expected KEY=VALUE format.")
                        return
                    key, value = kv.split("=", 1)
                    env_dict[key] = value
            payload: dict[str, Any] = {
                "script": content,
                "environment": env_dict,
            }
            if account:
                payload["account"] = account
            if partition:
                payload["partition"] = partition
            if array:
                payload["array"] = array
            if name:
                payload["name"] = name

            restd_url = slurm.get("restd_url")
            ca_pem = slurm.get("ca_pem")
            if not restd_url:
                self.handle_error("Slurm REST endpoint is not available for this reservation")
                return

            import tempfile
            import requests
            import os
            verify_param: object = True
            caf = None
            caf_path: str | None = None
            try:
                if ca_pem:
                    caf = tempfile.NamedTemporaryFile("w", delete=False)
                    caf.write(ca_pem)
                    caf.flush()
                    caf_path = caf.name
                    verify_param = caf_path
                api_version = os.getenv("FLOW_SLURM_API_VERSION", "v0.0.40")
                r = requests.post(
                    restd_url.rstrip("/") + f"/slurm/{api_version}/job/submit",
                    json=payload,
                    timeout=30,
                    verify=verify_param,
                )
                if r.status_code >= 300:
                    self.handle_error(f"slurmrestd error: {r.status_code} {r.text}")
                    return
                data = r.json()
            finally:
                try:
                    if caf:
                        caf.close()
                    if caf_path:
                        try:
                            os.unlink(caf_path)
                        except Exception:
                            pass
                except Exception:
                    pass
            console.print(json.dumps(data))

        @grp.command(name="status", help="List jobs for a Slurm-enabled reservation")
        @click.argument("reservation_id")
        @click.option("--user", default=None)
        @click.option("--state", default=None)
        def status_cmd(reservation_id: str, user: str | None, state: str | None) -> None:
            try:
                slurm = _get_slurm_meta(reservation_id)
            except click.Abort:
                return
            restd_url = slurm.get("restd_url")
            ca_pem = slurm.get("ca_pem")
            if not restd_url:
                self.handle_error("Slurm REST endpoint is not available for this reservation")
                return
            import tempfile
            import requests
            import os

            params: dict[str, Any] = {}
            if user:
                params["user_name"] = user
            if state:
                params["job_state"] = state
            verify_param: object = True
            caf = None
            caf_path: str | None = None
            try:
                if ca_pem:
                    caf = tempfile.NamedTemporaryFile("w", delete=False)
                    caf.write(ca_pem)
                    caf.flush()
                    caf_path = caf.name
                    verify_param = caf_path
                api_version = os.getenv("FLOW_SLURM_API_VERSION", "v0.0.40")
                r = requests.get(
                    restd_url.rstrip("/") + f"/slurm/{api_version}/jobs",
                    params=params,
                    timeout=30,
                    verify=verify_param,
                )
                if r.status_code >= 300:
                    self.handle_error(f"slurmrestd error: {r.status_code} {r.text}")
                    return
                data = r.json()
            finally:
                try:
                    if caf:
                        caf.close()
                    if caf_path:
                        try:
                            os.unlink(caf_path)
                        except Exception:
                            pass
                except Exception:
                    pass
            console.print(json.dumps(data))

        @grp.command(name="cancel", help="Cancel a Slurm job")
        @click.argument("reservation_id")
        @click.argument("job_id")
        def cancel_cmd(reservation_id: str, job_id: str) -> None:
            try:
                slurm = _get_slurm_meta(reservation_id)
            except click.Abort:
                return
            restd_url = slurm.get("restd_url")
            ca_pem = slurm.get("ca_pem")
            if not restd_url:
                self.handle_error("Slurm REST endpoint is not available for this reservation")
                return
            import tempfile
            import requests
            import os
            verify_param: object = True
            caf = None
            caf_path: str | None = None
            try:
                if ca_pem:
                    caf = tempfile.NamedTemporaryFile("w", delete=False)
                    caf.write(ca_pem)
                    caf.flush()
                    caf_path = caf.name
                    verify_param = caf_path
                api_version = os.getenv("FLOW_SLURM_API_VERSION", "v0.0.40")
                r = requests.delete(
                    restd_url.rstrip("/") + f"/slurm/{api_version}/job/{job_id}",
                    timeout=30,
                    verify=verify_param,
                )
                if r.status_code >= 300:
                    self.handle_error(f"slurmrestd error: {r.status_code} {r.text}")
                    return
            finally:
                try:
                    if caf:
                        caf.close()
                    if caf_path:
                        try:
                            os.unlink(caf_path)
                        except Exception:
                            pass
                except Exception:
                    pass
            console.print(f"Cancelled job {job_id}")

        @grp.command(name="ssh", help="Print an SSH command to the reservation's login node")
        @click.argument("reservation_id")
        def ssh_cmd(reservation_id: str) -> None:
            try:
                slurm = _get_slurm_meta(reservation_id)
            except click.Abort:
                return
            host = slurm.get("login_host")
            if not host:
                self.handle_error("No login_host available on this reservation")
                return
            console.print(f"ssh {host}")

        return grp


command = SlurmCommand()


