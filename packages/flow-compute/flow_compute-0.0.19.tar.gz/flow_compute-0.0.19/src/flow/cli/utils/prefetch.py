"""Background prefetch and in-memory cache for common CLI workflows.

Design goals:
- Minimal blast radius: lives in CLI utils; no provider changes required
- SOLID/DRY: single module to orchestrate prefetch and shared cache
- Safe defaults: non-blocking, best-effort, short TTLs for freshness

This module prefetches likely-needed data right after the user invokes
the CLI, based on the subcommand. Results are cached in-memory for the
current process and optionally consulted by consumer helpers such as
TaskFetcher to accelerate UX-heavy commands like `flow status`.

Environment variables:
- FLOW_PREFETCH: Set to "0" to disable prefetch entirely
- FLOW_PREFETCH_DEBUG: Set to "1" for debug logs
"""

from __future__ import annotations

import concurrent.futures
import logging
import os
import sys
import threading
import time
from typing import Any, Callable, Dict, Optional


_logger = logging.getLogger(__name__)


class _PrefetchCache:
    """Thread-safe in-memory cache with per-key TTL.

    Values are stored with a timestamp and a TTL to control staleness.
    The cache is process-local and intentionally simple to avoid IO.
    """

    def __init__(self) -> None:
        self._data: Dict[str, tuple[float, float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        now = time.time()
        with self._lock:
            entry = self._data.get(key)
            if not entry:
                return None
            ts, ttl, value = entry
            if now - ts > ttl:
                # Expired
                self._data.pop(key, None)
                return None
            return value

    def set(self, key: str, value: Any, ttl_seconds: float) -> None:
        with self._lock:
            self._data[key] = (time.time(), ttl_seconds, value)

    def age(self, key: str) -> Optional[float]:
        with self._lock:
            entry = self._data.get(key)
            if not entry:
                return None
            ts, ttl, _ = entry
            return time.time() - ts


# Global cache instance
_CACHE = _PrefetchCache()


def get_cached(key: str) -> Optional[Any]:
    """Public accessor for cached prefetch results.

    Keys used by this module:
    - tasks_running: list[Task]
    - tasks_pending: list[Task]
    - tasks_all: list[Task]
    - instance_catalog: list[dict]
    - volumes_list: list[Volume]
    - ssh_keys: list[dict]
    - projects: list[dict]
    - me: dict
    """

    return _CACHE.get(key)


def _maybe_log_debug(message: str) -> None:
    if os.environ.get("FLOW_PREFETCH_DEBUG") == "1":
        _logger.debug(message)


def _should_enable() -> bool:
    # Default enabled; explicitly disable with FLOW_PREFETCH=0
    return os.environ.get("FLOW_PREFETCH", "1") != "0"


def _with_safety(task_name: str, func: Callable[[], Any], ttl_seconds: float, cache_key: str) -> None:
    """Execute func(), swallow errors, and cache result if available."""
    if not _should_enable():
        return
    try:
        result = func()
        if result is not None:
            _CACHE.set(cache_key, result, ttl_seconds)
            _maybe_log_debug(f"Prefetched {task_name} → {cache_key} (ttl={ttl_seconds}s)")
    except Exception as exc:
        # Best-effort: do not impact foreground UX
        _maybe_log_debug(f"Prefetch {task_name} failed: {exc}")


def _build_flow():
    # Local import to avoid import cycles on module load
    from flow.api.client import Flow

    # auto_init=False to avoid accidental interactive prompts in background
    return Flow(auto_init=False)


def _prefetch_tasks(status: Optional[str], limit: int, cache_key: str) -> None:
    from flow.api.models import TaskStatus

    def _task_call():
        flow = _build_flow()
        status_enum = TaskStatus(status) if status else None
        return flow.list_tasks(status=status_enum, limit=limit, force_refresh=False)

    # Fresh enough for a short window; keep tiny TTL
    _with_safety(
        task_name=f"tasks[{status or 'all'}]",
        func=_task_call,
        ttl_seconds=10.0,
        cache_key=cache_key,
    )


def _prefetch_catalog() -> None:
    def _call():
        flow = _build_flow()
        # Warms Flow's internal 5-min cache
        return flow._load_instance_catalog()  # noqa: SLF001 – purposeful warmup

    _with_safety("instance_catalog", _call, ttl_seconds=300.0, cache_key="instance_catalog")


def _prefetch_volumes() -> None:
    def _call():
        flow = _build_flow()
        return flow.list_volumes(limit=200)

    _with_safety("volumes", _call, ttl_seconds=60.0, cache_key="volumes_list")


def _prefetch_ssh_keys() -> None:
    def _call():
        flow = _build_flow()
        return flow.list_ssh_keys()

    _with_safety("ssh_keys", _call, ttl_seconds=300.0, cache_key="ssh_keys")


def _prefetch_projects() -> None:
    def _call():
        flow = _build_flow()
        return flow.list_projects()

    _with_safety("projects", _call, ttl_seconds=300.0, cache_key="projects")


def _prefetch_me() -> None:
    # Reach directly to provider HTTP for a very quick /v2/me
    def _call():
        flow = _build_flow()
        provider = flow.provider  # Ensure provider exists
        if not hasattr(provider, "http"):
            return None
        return provider.http.request(method="GET", url="/v2/me")

    _with_safety("me", _call, ttl_seconds=300.0, cache_key="me")


def prefetch_for_command(argv: Optional[list[str]] = None) -> None:
    """Start background prefetch for a given CLI argv.

    This function is intentionally non-blocking. It returns immediately
    after scheduling background jobs.

    Args:
        argv: Full argv list. Defaults to sys.argv if None.
    """
    if not _should_enable():
        return

    args = argv or sys.argv
    cmd = args[1] if len(args) > 1 and not args[1].startswith("-") else None

    # Nothing to do if no subcommand was provided
    if not cmd:
        return

    # Plan prefetch tasks based on command
    jobs: list[Callable[[], None]] = []

    # Universal small win: auth/profile and active tasks snapshot
    jobs.append(lambda: _prefetch_me())

    # Commands → Prefetch plan
    if cmd in {"status", "logs", "ssh", "cancel"}:
        # Likely to inspect active tasks next
        jobs.append(lambda: _prefetch_tasks("running", limit=100, cache_key="tasks_running"))
        jobs.append(lambda: _prefetch_tasks("pending", limit=100, cache_key="tasks_pending"))
        # Also keep a small general slice for fallbacks
        jobs.append(lambda: _prefetch_tasks(None, limit=100, cache_key="tasks_all"))
    if cmd in {"run", "grab", "dev"}:
        jobs.append(_prefetch_catalog)
        jobs.append(_prefetch_ssh_keys)
    if cmd in {"init", "tutorial", "ssh-keys"}:
        jobs.append(_prefetch_projects)
        jobs.append(_prefetch_ssh_keys)
    if cmd in {"volumes", "mount"}:
        jobs.append(_prefetch_volumes)

    # Opportunistic: if user passed a task id in argv, we could prefetch its logs.
    # Keep this extremely conservative to avoid surprises.
    # (We skip here to remain minimal and surgical.)

    # Execute in a very small thread pool to keep resource usage low
    def _run_background(jobs_to_run: list[Callable[[], None]]) -> None:
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, len(jobs_to_run) or 1)) as ex:
                futures = [ex.submit(job) for job in jobs_to_run]
                # Do not block; arrange callbacks to observe errors only in debug mode
                for f in futures:
                    f.add_done_callback(lambda fut: _maybe_log_debug(
                        f"Prefetch job done, error={fut.exception()}" if fut.exception() else "Prefetch job done"))
        except Exception as exc:
            _maybe_log_debug(f"Prefetch scheduling failed: {exc}")

    # Fire and forget in a single short-lived thread
    t = threading.Thread(target=_run_background, args=(jobs,), daemon=True)
    t.start()

    # Periodic refresh for long-running or UX-heavy commands (status/watch)
    # Keep extremely conservative defaults to avoid API pressure
    try:
        def _start_periodic(cmd_name: Optional[str]) -> None:
            if not cmd_name:
                return
            # Only enable for status; logs/ssh are streaming and don't need frequent updates
            if cmd_name not in {"status"}:
                return

            # Configurable intervals (seconds)
            # Default to low frequency; can be tuned via env vars
            try:
                active_ivl = float(os.environ.get("FLOW_PREFETCH_ACTIVE_INTERVAL", "15.0"))
            except Exception:
                active_ivl = 15.0
            try:
                all_ivl = float(os.environ.get("FLOW_PREFETCH_ALL_INTERVAL", "30.0"))
            except Exception:
                all_ivl = 30.0

            def _loop() -> None:
                next_run_running = time.time()
                next_run_pending = time.time()
                next_run_all = time.time()
                while _should_enable():
                    now = time.time()
                    try:
                        if now >= next_run_running:
                            _prefetch_tasks("running", limit=100, cache_key="tasks_running")
                            next_run_running = now + active_ivl
                        if now >= next_run_pending:
                            _prefetch_tasks("pending", limit=100, cache_key="tasks_pending")
                            next_run_pending = now + active_ivl
                        if now >= next_run_all:
                            _prefetch_tasks(None, limit=100, cache_key="tasks_all")
                            next_run_all = now + all_ivl
                    except Exception as exc:
                        _maybe_log_debug(f"Periodic prefetch error: {exc}")
                    time.sleep(0.5)

            threading.Thread(target=_loop, daemon=True).start()

        _start_periodic(cmd)
    except Exception as exc:
        _maybe_log_debug(f"Failed to start periodic prefetch: {exc}")


# Convenience alias used by consumers
start_prefetch_for_command = prefetch_for_command


