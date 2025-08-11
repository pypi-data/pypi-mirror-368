from __future__ import annotations

import shlex
from typing import Optional

import click

from flow import Flow
from flow.api.models import Task
from flow.cli.commands.base import BaseCommand, console
from flow.cli.utils.task_resolver import resolve_task_identifier


class PortsCommand(BaseCommand):
    """Manage instance port exposure and local tunnels for a task."""

    @property
    def name(self) -> str:
        return "ports"

    @property
    def help(self) -> str:
        return "Open/close/list exposed ports and create local SSH tunnels"

    def get_command(self) -> click.Command:
        from flow.cli.utils.mode import demo_aware_command

        @click.group(name=self.name, help=self.help)
        def ports():
            pass

        @ports.command(name="open")
        @click.argument("task_identifier", required=True)
        @click.option("--port", "port", type=int, required=True, help="Port to open (>=1024)")
        @click.option("--persist/--no-persist", default=True, help="Persist via systemd if available")
        @demo_aware_command()
        def open_cmd(task_identifier: str, port: int, persist: bool):
            """Open a public port on the task instance (Mithril: foundrypf)."""
            if port < 1024 or port > 65535:
                console.print("[red]Error:[/red] Port must be in 1024-65535 range")
                return
            try:
                flow_client = Flow(auto_init=True)
            except Exception as e:
                self.handle_auth_error()
                return

            task, error = resolve_task_identifier(flow_client, task_identifier)
            if error:
                console.print(f"[red]Error:[/red] {error}")
                return

            provider = flow_client.provider
            remote_ops = provider.get_remote_operations() if provider else None
            if not remote_ops:
                console.print("[red]Error:[/red] Provider does not support remote operations")
                return

            cmds: list[str] = []
            # Open via foundrypf
            cmds.append(f"sudo /usr/local/bin/foundrypf {port}")
            if persist:
                cmds.extend(
                    [
                        "sudo bash -lc 'cat > /etc/systemd/system/foundrypf@.service <<\\'EOF\\'\n"
                        "[Unit]\nDescription=Foundry Port Forwarding %i\nAfter=network-online.target\nWants=network-online.target\n\n"
                        "[Service]\nType=simple\nExecStart=/usr/local/bin/foundrypf %i\nRestart=always\nRestartSec=3\n\n"
                        "[Install]\nWantedBy=multi-user.target\nEOF'",
                        "sudo systemctl daemon-reload || true",
                        f"sudo systemctl enable --now foundrypf@{port}.service || true",
                    ]
                )

            try:
                for c in cmds:
                    remote_ops.execute_command(task.task_id, c, timeout=60)
                console.print(f"[green]✓[/green] Opened port {port}")
                if getattr(task, "ssh_host", None):
                    console.print(f"URL: http://{task.ssh_host}:{port}")
                # Next steps
                try:
                    task_ref = task.name or task.task_id
                    self.show_next_actions(
                        [
                            f"Create a local tunnel: [accent]flow ports tunnel {task_ref} --remote {port}[/accent]",
                            f"List open ports: [accent]flow ports list {task_ref}[/accent]",
                            f"Close this port: [accent]flow ports close {task_ref} --port {port}[/accent]",
                        ]
                    )
                except Exception:
                    pass
            except Exception as e:
                self.handle_error(e)
                return

        @ports.command(name="close")
        @click.argument("task_identifier", required=True)
        @click.option("--port", "port", type=int, required=True, help="Port to close")
        @demo_aware_command()
        def close_cmd(task_identifier: str, port: int):
            """Close a previously opened public port."""
            try:
                flow_client = Flow(auto_init=True)
            except Exception:
                self.handle_auth_error()
                return

            task, error = resolve_task_identifier(flow_client, task_identifier)
            if error:
                console.print(f"[red]Error:[/red] {error}")
                return
            provider = flow_client.provider
            remote_ops = provider.get_remote_operations() if provider else None
            if not remote_ops:
                console.print("[red]Error:[/red] Provider does not support remote operations")
                return

            cmds = [
                f"sudo /usr/local/bin/foundrypf -d {port} || true",
                f"sudo systemctl disable --now foundrypf@{port}.service || true",
            ]
            try:
                for c in cmds:
                    remote_ops.execute_command(task.task_id, c, timeout=60)
                console.print(f"[green]✓[/green] Closed port {port}")
                # Next steps
                try:
                    task_ref = task.name or task.task_id
                    self.show_next_actions(
                        [
                            f"List open ports: [accent]flow ports list {task_ref}[/accent]",
                            f"Open a new port: [accent]flow ports open {task_ref} --port 8888[/accent]",
                        ]
                    )
                except Exception:
                    pass
            except Exception as e:
                self.handle_error(e)
                return

        @ports.command(name="list")
        @click.argument("task_identifier", required=True)
        @demo_aware_command()
        def list_cmd(task_identifier: str):
            """List open ports and foundrypf services on the instance."""
            try:
                flow_client = Flow(auto_init=True)
            except Exception:
                self.handle_auth_error()
                return
            task, error = resolve_task_identifier(flow_client, task_identifier)
            if error:
                console.print(f"[red]Error:[/red] {error}")
                return
            provider = flow_client.provider
            remote_ops = provider.get_remote_operations() if provider else None
            if not remote_ops:
                console.print("[red]Error:[/red] Provider does not support remote operations")
                return

            try:
                out_services = remote_ops.execute_command(
                    task.task_id,
                    "systemctl list-units --type=service --no-legend 'foundrypf@*.service' 2>/dev/null || true",
                    timeout=30,
                )
                out_ss = remote_ops.execute_command(
                    task.task_id,
                    "ss -lntp 2>/dev/null | awk 'NR>1 {print $4}' || true",
                    timeout=30,
                )
                services = []
                for line in (out_services or "").splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    services.append(line.split()[0])
                ports = []
                for line in (out_ss or "").splitlines():
                    # Expect address:port
                    if ":" in line:
                        try:
                            ports.append(int(line.rsplit(":", 1)[1]))
                        except Exception:
                            continue
                ports = sorted(set(p for p in ports if 1024 <= p <= 65535))

                console.print("[bold]Open ports (TCP):[/bold] " + (", ".join(map(str, ports)) or "-"))
                if services:
                    console.print("[bold]Services:[/bold]")
                    for s in services:
                        console.print(f"  • {s}")
                if getattr(task, "ssh_host", None) and ports:
                    console.print("[bold]URLs:[/bold]")
                    for p in ports:
                        console.print(f"  • http://{task.ssh_host}:{p}")
                # Next steps
                try:
                    task_ref = task.name or task.task_id
                    example_port = ports[0] if ports else 8888
                    self.show_next_actions(
                        [
                            f"Open a port: [accent]flow ports open {task_ref} --port 8888[/accent]",
                            f"Create a local tunnel: [accent]flow ports tunnel {task_ref} --remote {example_port}[/accent]",
                        ]
                    )
                except Exception:
                    pass
            except Exception as e:
                self.handle_error(e)
                return

        @ports.command(name="tunnel")
        @click.argument("task_identifier", required=True)
        @click.option("--remote", "remote_port", type=int, required=True, help="Remote port")
        @click.option("--local", "local_port", type=int, default=0, show_default=True, help="Local port (0=auto)")
        @click.option("--print-only", is_flag=True, help="Only print SSH command; do not execute")
        @demo_aware_command()
        def tunnel_cmd(task_identifier: str, remote_port: int, local_port: int, print_only: bool):
            """Create a local SSH tunnel to the remote port."""
            if remote_port < 1 or remote_port > 65535:
                console.print("[red]Error:[/red] Invalid --remote port")
                return
            try:
                flow_client = Flow(auto_init=True)
            except Exception:
                self.handle_auth_error()
                return
            task, error = resolve_task_identifier(flow_client, task_identifier)
            if error:
                console.print(f"[red]Error:[/red] {error}")
                return
            if not task.ssh_host or not task.ssh_user:
                console.print("SSH not ready yet; wait for provisioning.")
                return

            # Autopick local port when 0
            if local_port == 0:
                import socket

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(("", 0))
                    s.listen(1)
                    local_port = s.getsockname()[1]

            # Build SSH command safely; explicitly cast and quote username/host
            user_at_host = f"{task.ssh_user}@{task.ssh_host}"
            ssh_cmd = (
                f"ssh -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=60 -o ServerAliveCountMax=2 "
                f"-L {int(local_port)}:localhost:{int(remote_port)} {shlex.quote(user_at_host)}"
            )

            if print_only:
                console.print(ssh_cmd)
                console.print(f"Local URL: http://localhost:{local_port}")
                try:
                    task_ref = task.name or task.task_id
                    self.show_next_actions(
                        [
                            f"Open in browser: [accent]http://localhost:{local_port}[/accent]",
                            f"List open ports: [accent]flow ports list {task_ref}[/accent]",
                        ]
                    )
                except Exception:
                    pass
                return

            import subprocess

            console.print(f"Starting SSH tunnel (local {local_port} → remote {remote_port}). Press Ctrl+C to stop…")
            try:
                subprocess.run(shlex.split(ssh_cmd), check=False)
            except KeyboardInterrupt:
                pass
            # Next steps after tunnel ends
            try:
                task_ref = task.name or task.task_id
                self.show_next_actions(
                    [
                        f"List open ports: [accent]flow ports list {task_ref}[/accent]",
                        f"Open another tunnel: [accent]flow ports tunnel {task_ref} --remote {remote_port}[/accent]",
                    ]
                )
            except Exception:
                pass

        return ports


# Export command instance
command = PortsCommand()


