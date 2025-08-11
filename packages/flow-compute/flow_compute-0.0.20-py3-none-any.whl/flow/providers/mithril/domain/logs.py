"""Log retrieval and streaming via provider remote operations.

Encapsulates the SSH-based log commands and adds a small TTL cache for the
`get_task_logs` fast-path.
"""

from __future__ import annotations

from flow.core.provider_interfaces import IRemoteOperations
from flow.providers.mithril.domain.caches import TtlCache


class LogService:
    """Cache-aware log retrieval and streaming for tasks."""

    def __init__(
        self, remote_ops: IRemoteOperations, *, cache_ttl: float = 5.0, max_entries: int = 100
    ):
        self._remote = remote_ops
        self._cache = TtlCache[tuple[str, int, str], str](
            ttl_seconds=cache_ttl, max_entries=max_entries
        )

    def get_cached(self, task_id: str, tail: int, log_type: str) -> str | None:
        return self._cache.get((task_id, tail, log_type))

    def set_cache(self, task_id: str, tail: int, log_type: str, content: str) -> None:
        self._cache.set((task_id, tail, log_type), content)

    def build_command(self, task_id: str, tail: int, log_type: str) -> str:
        if log_type == "both":
            return (
                "CN=$(docker ps -a --format '{{.Names}}' | head -n1); "
                'if [ -n "$CN" ]; then '
                f"  echo '=== Docker container logs ===' && docker logs \"$CN\" --tail {tail} 2>&1; "
                "else "
                "  echo 'Task logs not available yet. Showing startup logs...' && "
                "  LOG=/var/log/foundry/startup_script.log; "
                '  if [ -s "$LOG" ]; then '
                f'    sudo tail -n {tail} "$LOG"; '
                "  else "
                "    echo 'Startup logs are empty (instance may still be starting).'; "
                f"    echo '  • Wait and re-run: flow logs {task_id}'; "
                f"    echo '  • Test connectivity: flow ssh {task_id}'; "
                "  fi; "
                "fi"
            )
        elif log_type == "stderr":
            return (
                "CN=$(docker ps -a --format '{{.Names}}' | head -n1); "
                'if [ -n "$CN" ]; then '
                f'  docker logs "$CN" --tail {tail} 2>&1 >/dev/null; '
                "else "
                "  echo 'No stderr logs available (no container running).'; "
                f"  echo 'Try stdout or startup logs: flow logs {task_id}'; "
                "fi"
            )
        else:
            return (
                # Prefer explicit container name 'main' when present for predictable tests
                f"if docker ps --format '{{{{.Names}}}}' | grep -q '^main$'; then docker logs main --tail {tail}; "
                "else CN=$(docker ps -a --format '{{.Names}}' | head -n1); "
                'if [ -n "$CN" ]; then '
                f'  docker logs "$CN" --tail {tail}; '
                "else "
                "  echo 'Task logs not available yet. Showing startup logs...' && "
                "  LOG=/var/log/foundry/startup_script.log; "
                '  if [ -s "$LOG" ]; then '
                f'    sudo tail -n {tail} "$LOG"; '
                "  else "
                "    echo 'Startup logs are empty (instance may still be starting).'; "
                f"    echo '  • Wait and re-run: flow logs {task_id}'; "
                f"    echo '  • Test connectivity: flow ssh {task_id}'; "
                "  fi; fi; fi"
            )

    # Public helper to execute a log command via the remote interface without exposing internals
    def execute_via_remote(self, task_id: str, command: str) -> str:
        return self._remote.execute_command(task_id, command)
