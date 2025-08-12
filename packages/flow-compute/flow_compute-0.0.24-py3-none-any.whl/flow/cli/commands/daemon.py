"""Daemon command - Manage local background agent (flowd).

Provides start/stop/status subcommands for the lightweight daemon that
keeps provider connections warm and maintains disk snapshots for instant CLI UX.
"""

from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

import click

from flow.cli.commands.base import BaseCommand, console

SOCKET_PATH = Path.home() / ".flow" / "flowd.sock"
PID_PATH = Path.home() / ".flow" / "flowd.pid"
TOKEN_PATH = Path.home() / ".flow" / "flowd.token"


def _load_token() -> str | None:
    try:
        if TOKEN_PATH.exists():
            return TOKEN_PATH.read_text().strip()
    except Exception:
        return None
    return None


def _send(cmd: dict, timeout: float = 0.5) -> dict | None:
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect(str(SOCKET_PATH))
        payload = dict(cmd)
        token = _load_token()
        if token:
            payload["token"] = token
        s.sendall((__import__("json").dumps(payload) + "\n").encode("utf-8"))
        buf = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            buf += chunk
            if b"\n" in chunk:
                break
        s.close()
        if not buf:
            return None
        line = buf.split(b"\n", 1)[0].decode("utf-8", errors="ignore")
        return __import__("json").loads(line)
    except Exception:
        return None


class DaemonCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "daemon"

    @property
    def help(self) -> str:
        return "Manage local background agent for snappier CLI UX"

    def get_command(self) -> click.Command:
        @click.group(name=self.name, help=self.help)
        def daemon():
            pass

        @daemon.command("start", help="Start the daemon in the background")
        @click.option("--idle-ttl", type=int, default=1800, help="Idle shutdown after N seconds")
        def start(idle_ttl: int):
            # If already running, say so
            if SOCKET_PATH.exists() and _send({"cmd": "ping"}):
                console.print("[dim]flowd is already running[/dim]")
                return
            # Launch background process
            env = os.environ.copy()
            env["FLOW_DAEMON_IDLE_TTL"] = str(idle_ttl)
            cmd = [sys.executable, "-m", "flow.cli.utils.daemon_server"]
            try:
                # Detach
                subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                console.print(f"[red]Failed to start daemon:[/red] {e}")
                return
            # Wait briefly for socket
            deadline = time.time() + 2.0
            while time.time() < deadline:
                if SOCKET_PATH.exists() and _send({"cmd": "ping"}):
                    console.print("[green]flowd started[/green]")
                    return
                time.sleep(0.05)
            console.print("[yellow]Started, but did not get a response in time[/yellow]")

        @daemon.command("stop", help="Stop the daemon if running")
        def stop():
            # Try graceful shutdown via RPC
            if SOCKET_PATH.exists():
                _send({"cmd": "shutdown"}, timeout=0.2)
                time.sleep(0.2)
            # If PID exists, try kill
            try:
                if PID_PATH.exists():
                    pid = int(PID_PATH.read_text().strip())
                    os.kill(pid, signal.SIGTERM)
            except Exception:
                pass
            # Cleanup
            try:
                if SOCKET_PATH.exists():
                    SOCKET_PATH.unlink()
            except Exception:
                pass
            try:
                if PID_PATH.exists():
                    PID_PATH.unlink()
            except Exception:
                pass
            console.print("[green]flowd stopped[/green]")

        @daemon.command("status", help="Show daemon status")
        def status():
            resp = _send({"cmd": "status"})
            if not resp or not resp.get("ok"):
                console.print("[yellow]flowd is not running[/yellow]")
                return
            status = resp.get("status", {})
            uptime = status.get("uptime", 0.0)
            console.print(
                f"[dim]flowd running[/dim] pid={status.get('pid')} uptime={uptime:.1f}s handled={status.get('connections_handled')}"
            )

        return daemon


command = DaemonCommand()
