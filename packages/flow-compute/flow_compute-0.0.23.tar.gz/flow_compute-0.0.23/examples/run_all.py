#!/usr/bin/env python3
"""Run a curated set of examples with preflight checks and summary.

Defaults to local-provider smoke tests. Use --cloud to run minimal cloud tests.

Usage:
  python examples/run_all.py            # local smoke
  python examples/run_all.py --cloud    # minimal cloud run
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

# Ensure we can import examples/_common when running as a script from repo root
THIS_DIR = Path(__file__).parent
sys.path.insert(0, str(THIS_DIR))

from _common import (
    detect_provider,
    ensure_ready,
    error,
    estimate_price_for_instance,
    info,
    success,
    warn,
)

ROOT = Path(__file__).resolve().parents[1]


def run_script(path: Path) -> int:
    info(f"Running: {path.relative_to(ROOT)}")
    proc = subprocess.run([sys.executable, str(path)], cwd=str(ROOT))
    return proc.returncode


def local_smoke() -> list[tuple[str, int]]:
    """Fast local-provider smoke tests."""
    tasks: list[tuple[str, int]] = []

    # 1) LocalProvider smoke (non-interactive)
    script = ROOT / "examples/03_development/local_smoke.py"
    rc = run_script(script)
    tasks.append((str(script.relative_to(ROOT)), rc))

    return tasks


def cloud_minimal() -> list[tuple[str, int]]:
    """Minimal cloud tests to validate setup with low cost."""
    tasks: list[tuple[str, int]] = []

    # 1) Hello GPU (single-GPU)
    hello = ROOT / "examples/01_basics/hello_gpu.py"
    # Print rough estimate for user awareness
    estimate = estimate_price_for_instance("a100")
    if estimate is not None:
        info(f"Estimated price for a100: ${estimate:.2f}/hr (informational)")
    rc = run_script(hello)
    tasks.append((str(hello.relative_to(ROOT)), rc))

    return tasks


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Flow examples suite")
    parser.add_argument(
        "--cloud", action="store_true", help="Run minimal cloud tests instead of local smoke"
    )
    args = parser.parse_args()

    provider = detect_provider()
    info(f"Detected provider: {provider}")
    for w in ensure_ready(provider):
        warn(w)

    if args.cloud:
        runs = cloud_minimal()
    else:
        runs = local_smoke()

    failed = [(name, rc) for name, rc in runs if rc != 0]
    success_count = len(runs) - len(failed)

    print("\n=== Summary ===")
    print(f"Total: {len(runs)} | Passed: {success_count} | Failed: {len(failed)}")
    for name, rc in failed:
        error(f"FAILED: {name} (rc={rc})")
    if not failed:
        success("All selected examples passed")

    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
