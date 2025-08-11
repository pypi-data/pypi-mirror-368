#!/usr/bin/env python3
"""Hyperparameter sweep example with cost-aware defaults.

Fan out multiple training runs with different hyperparameters. Defaults to
small, affordable single-GPU runs and a short TTL. Aggregates metrics from
logs at the end.
"""

from __future__ import annotations

import itertools
import json
from dataclasses import dataclass

from flow import Flow, TaskConfig


@dataclass
class SweepSpec:
    learning_rates: list[float]
    batch_sizes: list[int]
    epochs: int = 2


def build_command(lr: float, batch: int, epochs: int) -> str:
    return f"""
set -e
python - <<'PY'
import json, random, time
lr={lr}
batch={batch}
epochs={epochs}
best=10.0
for e in range(epochs):
    # Fake decreasing loss
    best *= 0.7 + random.random()*0.05
    print(json.dumps({{"epoch": e, "lr": lr, "batch": batch, "loss": best}}))
    time.sleep(0.2)
print(json.dumps({{"final": True, "lr": lr, "batch": batch, "loss": best}}))
PY
"""


def parse_final_loss(logs: str) -> float | None:
    last = None
    for line in logs.splitlines():
        try:
            obj = json.loads(line)
            if obj.get("final"):
                last = float(obj["loss"])  # type: ignore[index]
        except Exception:
            continue
    return last


def main() -> int:
    spec = SweepSpec(
        learning_rates=[1e-4, 5e-4, 1e-3],
        batch_sizes=[16, 32],
        epochs=2,
    )

    configs: list[tuple[str, TaskConfig]] = []
    for lr, batch in itertools.product(spec.learning_rates, spec.batch_sizes):
        name = f"sweep-lr{lr}-bs{batch}"
        cfg = TaskConfig(
            name=name,
            unique_name=True,
            instance_type="a100",
            image="python:3.11-slim",
            command=build_command(lr, batch, spec.epochs),
            max_run_time_hours=0.5,
        )
        configs.append((name, cfg))

    tasks = []
    with Flow() as client:
        for name, cfg in configs:
            t = client.run(cfg)
            tasks.append((name, t))

        print(f"Submitted {len(tasks)} runs. Waiting for completion...")
        for _, t in tasks:
            t.wait()

    results: list[tuple[str, float | None]] = []
    for name, t in tasks:
        logs = t.logs()
        loss = parse_final_loss(logs)
        results.append((name, loss))

    results.sort(key=lambda x: (x[1] is None, x[1] if x[1] is not None else float("inf")))
    print("\n=== Sweep Results (lower is better) ===")
    for name, loss in results:
        print(f"{name}: {loss if loss is not None else 'N/A'}")

    best = next((r for r in results if r[1] is not None), None)
    if best:
        print(f"\nBest: {best[0]} (loss={best[1]:.4f})")
    else:
        print("\nNo successful runs parsed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
