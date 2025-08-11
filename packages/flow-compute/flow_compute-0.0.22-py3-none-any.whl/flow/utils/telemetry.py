"""Minimal opt-in telemetry for Flow CLI.

Writes JSONL events to ~/.flow/metrics.jsonl when FLOW_TELEMETRY=1.
Never raises; best-effort only.
"""

from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class CommandMetric:
    command: str
    duration: float
    success: bool
    error_type: Optional[str] = None
    timestamp: str | None = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat() + "Z"


class Telemetry:
    def __init__(self) -> None:
        self.enabled = os.environ.get("FLOW_TELEMETRY", "0") == "1"
        self.metrics_file = Path.home() / ".flow" / "metrics.jsonl"
        self._lock = threading.Lock()

    def track_command(self, command: str):
        class CommandTracker:
            def __init__(self, telemetry: "Telemetry", command: str) -> None:
                self.telemetry = telemetry
                self.command = command
                self.start_time: float | None = None

            def __enter__(self) -> "CommandTracker":
                self.start_time = time.time()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[override]
                if not self.telemetry.enabled:
                    return
                try:
                    duration = 0.0
                    if self.start_time is not None:
                        duration = time.time() - self.start_time
                    metric = CommandMetric(
                        command=self.command,
                        duration=duration,
                        success=exc_type is None,
                        error_type=exc_type.__name__ if exc_type else None,
                    )
                    self.telemetry.write_metric(metric)
                except Exception:
                    # Never raise from telemetry
                    pass

        return CommandTracker(self, command)

    def _write_metric(self, metric: CommandMetric) -> None:
        with self._lock:
            try:
                self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.metrics_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(asdict(metric)) + "\n")
            except Exception:
                pass

    # Public API for writing a metric; used by nested trackers to avoid
    # cross-object access to a private method per repo lint policy
    def write_metric(self, metric: CommandMetric) -> None:
        self._write_metric(metric)


