"""Lightweight local background agent for Flow CLI.

This daemon maintains warm caches and disk snapshots to make CLI commands
feel instant across invocations. It exposes a tiny JSON-over-UNIX-socket
RPC for basic control and diagnostics.

Focus: minimal dependencies, robust error handling, small footprint.
"""

from __future__ import annotations

import json
import os
import socket
import sys
import threading
import time
from pathlib import Path
from typing import Any

SOCKET_PATH = Path.home() / ".flow" / "flowd.sock"
PID_PATH = Path.home() / ".flow" / "flowd.pid"


def _ensure_runtime_dir() -> None:
    try:
        SOCKET_PATH.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


def _send_json(conn: socket.socket, payload: dict[str, Any]) -> None:
    try:
        data = (json.dumps(payload) + "\n").encode("utf-8")
        conn.sendall(data)
    except Exception:
        pass


def _recv_json(conn: socket.socket) -> dict[str, Any] | None:
    try:
        buf = b""
        # Read until newline (one JSON per connection)
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            buf += chunk
            if b"\n" in chunk:
                break
        if not buf:
            return None
        line = buf.split(b"\n", 1)[0].decode("utf-8", errors="ignore")
        return json.loads(line)
    except Exception:
        return None


def _prefetch_tick(active_only: bool = True) -> None:
    """Perform one refresh tick using CLI prefetch helpers."""
    try:
        from flow.cli.utils.prefetch import (
            _prefetch_catalog,
            _prefetch_projects,
            _prefetch_ssh_keys,
            _prefetch_volumes,
            refresh_active_task_caches,
            refresh_all_tasks_cache,
        )

        # Active tasks are the highest value for responsiveness
        refresh_active_task_caches()
        # Opportunistically refresh others in longer cadence
        if not active_only:
            refresh_all_tasks_cache()
            _prefetch_catalog()
            _prefetch_ssh_keys()
            _prefetch_projects()
            _prefetch_volumes()
    except Exception:
        # Daemon must be silent on transient errors
        pass


class DaemonState:
    def __init__(self) -> None:
        self.start_time = time.time()
        self.last_refresh_active = 0.0
        self.last_refresh_all = 0.0
        self.lock = threading.Lock()
        self.shutdown_flag = False
        self.connections_handled = 0

    def to_dict(self) -> dict[str, Any]:
        with self.lock:
            return {
                "uptime": time.time() - self.start_time,
                "last_refresh_active": self.last_refresh_active,
                "last_refresh_all": self.last_refresh_all,
                "connections_handled": self.connections_handled,
                "pid": os.getpid(),
            }


def _refresh_loop(state: DaemonState) -> None:
    # Active refresh every ~30s, all refresh every ~90s with jitter
    def _jitter(base: float) -> float:
        try:
            import random

            return base * (1.0 + random.uniform(-0.2, 0.2))
        except Exception:
            return base

    next_active = time.time()
    next_all = time.time()
    while not state.shutdown_flag:
        now = time.time()
        try:
            if now >= next_active:
                _prefetch_tick(active_only=True)
                with state.lock:
                    state.last_refresh_active = time.time()
                next_active = now + _jitter(30.0)
            if now >= next_all:
                _prefetch_tick(active_only=False)
                with state.lock:
                    state.last_refresh_all = time.time()
                next_all = now + _jitter(90.0)
        except Exception:
            pass
        time.sleep(0.5)


def _handle_connection(conn: socket.socket, state: DaemonState) -> None:
    try:
        req = _recv_json(conn) or {}
        cmd = req.get("cmd")
        if cmd == "ping":
            _send_json(conn, {"ok": True, "pong": True})
        elif cmd == "status":
            _send_json(conn, {"ok": True, "status": state.to_dict()})
        elif cmd == "refresh":
            which = req.get("which", "active")
            if which == "all":
                _prefetch_tick(active_only=False)
            else:
                _prefetch_tick(active_only=True)
            _send_json(conn, {"ok": True})
        elif cmd == "shutdown":
            state.shutdown_flag = True
            _send_json(conn, {"ok": True})
        elif cmd == "version":
            try:
                from flow._version import get_version

                v = get_version()
            except Exception:
                v = "unknown"
            _send_json(conn, {"ok": True, "version": v})
        else:
            _send_json(conn, {"ok": False, "error": "unknown command"})
    except Exception:
        pass
    finally:
        with state.lock:
            state.connections_handled += 1
        try:
            conn.close()
        except Exception:
            pass


def run_server() -> int:
    _ensure_runtime_dir()
    # Clean up stale socket
    try:
        if SOCKET_PATH.exists():
            SOCKET_PATH.unlink()
    except Exception:
        pass

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(str(SOCKET_PATH))
    os.chmod(str(SOCKET_PATH), 0o600)
    server.listen(16)

    # Write PID file
    try:
        PID_PATH.write_text(str(os.getpid()))
    except Exception:
        pass

    state = DaemonState()
    # Start background refresh loop
    t = threading.Thread(target=_refresh_loop, args=(state,), daemon=True)
    t.start()

    # Idle shutdown after TTL if no connections and no refresh demanded externally
    idle_ttl = float(os.environ.get("FLOW_DAEMON_IDLE_TTL", "1800"))  # 30 minutes default
    last_activity = time.time()

    try:
        while not state.shutdown_flag:
            server.settimeout(1.0)
            try:
                conn, _ = server.accept()
                last_activity = time.time()
            except TimeoutError:
                # Idle shutdown
                if (time.time() - last_activity) > idle_ttl:
                    break
                continue
            except Exception:
                continue

            # Handle request in thread (short, one-shot)
            threading.Thread(target=_handle_connection, args=(conn, state), daemon=True).start()
    finally:
        try:
            server.close()
        except Exception:
            pass
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

    return 0


def main() -> int:
    # Minimal shim to allow -m execution
    return run_server()


if __name__ == "__main__":
    sys.exit(main())
